<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Log\LoggerInterface;
use Throwable;

/**
 * POST /api/v1/ingest — receives delta pushes from waldhomeserver publisher.
 * HMAC-authenticated upstream (HmacAuthMiddleware).
 *
 * Payload shape (JSON):
 * {
 *   "schema_version": 1,
 *   "table": "crops" | "crop_varieties" | "products" | "product_prices",
 *   "operation": "upsert" | "delete",
 *   "idempotency_key": "crops_2026-05-23_001",
 *   "rows": [ {...}, {...} ]
 * }
 */
final class IngestController
{
    /** Whitelisted target tables + their column allowlist. */
    private const TABLE_COLUMNS = [
        'crops' => [
            'id', 'slug', 'hebrew_name', 'scientific_name',
            'family_id', 'family_name_he', 'category', 'season',
            'dtm_min', 'dtm_max', 'last_pushed_at', 'payload_json',
        ],
        'crop_varieties' => [
            'id', 'crop_id', 'name', 'payload_json',
        ],
        'products' => [
            'id', 'slug', 'hebrew_name', 'category', 'unit',
            'last_price', 'last_price_date', 'freshness_days',
            'last_pushed_at', 'payload_json',
        ],
        'product_prices' => [
            'product_id', 'price_date', 'price', 'source',
        ],
        'crop_field_enrichment' => [
            'crop_id', 'field_name', 'value_best', 'unit',
            'field_state', 'winning_source_class', 'confidence_score', 'last_pushed_at',
        ],
        'crop_attribute' => [
            'crop_id', 'attribute_key', 'value_canonical', 'value_list',
            'field_state', 'last_pushed_at',
        ],
        'crop_content' => [
            'crop_id', 'content_type', 'text_md', 'winning_source_class',
            'confidence_score', 'field_state', 'last_pushed_at',
        ],
        'crop_content_source' => [
            'crop_id', 'content_type', 'source_label', 'source_class',
            'raw_text_md', 'source_url', 'display_order', 'last_pushed_at',
        ],
    ];

    public function __construct(
        private PDO $pdo,
        private LoggerInterface $log,
    ) {}

    public function receive(Request $request, Response $response): Response
    {
        $payload = $request->getParsedBody();
        if (!is_array($payload)) {
            return self::error($response, 400, 'body must be JSON object');
        }

        // Validate envelope
        $required = ['schema_version', 'table', 'operation', 'idempotency_key', 'rows'];
        foreach ($required as $k) {
            if (!array_key_exists($k, $payload)) {
                return self::error($response, 400, "missing field: {$k}");
            }
        }
        $schemaVersion = (int)$payload['schema_version'];
        $table = (string)$payload['table'];
        $operation = (string)$payload['operation'];
        $idempotencyKey = (string)$payload['idempotency_key'];
        $rows = $payload['rows'];

        if ($schemaVersion !== 1) {
            return self::error($response, 400, "unsupported schema_version: {$schemaVersion}");
        }
        if (!isset(self::TABLE_COLUMNS[$table])) {
            return self::error($response, 400, "unknown table: {$table}");
        }
        if (!in_array($operation, ['upsert', 'delete'], true)) {
            return self::error($response, 400, "unknown operation: {$operation}");
        }
        if (!is_array($rows)) {
            return self::error($response, 400, 'rows must be array');
        }

        // Idempotency check
        $stmt = $this->pdo->prepare('SELECT row_count FROM ingest_log WHERE idempotency_key = ?');
        $stmt->execute([$idempotencyKey]);
        $existing = $stmt->fetchColumn();
        if ($existing !== false) {
            return self::json($response, [
                'duplicate' => true,
                'idempotency_key' => $idempotencyKey,
                'previously_accepted' => (int)$existing,
            ]);
        }

        // Apply
        $accepted = 0;
        $errors = [];
        $this->pdo->beginTransaction();
        try {
            foreach ($rows as $i => $row) {
                if (!is_array($row)) {
                    $errors[] = ['index' => $i, 'error' => 'row must be object'];
                    continue;
                }
                try {
                    if ($operation === 'upsert') {
                        $this->upsert($table, $row);
                    } else {
                        $this->delete($table, $row);
                    }
                    $accepted++;
                } catch (Throwable $e) {
                    $errors[] = ['index' => $i, 'error' => $e->getMessage()];
                }
            }

            // Record idempotency
            $status = empty($errors) ? 'ok' : (($accepted > 0) ? 'partial' : 'fail');
            $logStmt = $this->pdo->prepare(
                'INSERT INTO ingest_log (idempotency_key, table_name, row_count, status) VALUES (?, ?, ?, ?)'
            );
            $logStmt->execute([$idempotencyKey, $table, $accepted, $status]);

            // Opportunistic retention pruning (>30d ingest_log rows).
            // ~1% of requests, indexed by applied_at — cheap and self-healing.
            if (random_int(1, 100) === 1) {
                try {
                    $this->pdo->exec("DELETE FROM ingest_log WHERE applied_at < NOW() - INTERVAL 30 DAY");
                } catch (Throwable $e) {
                    $this->log->warning('ingest_log prune failed', ['err' => $e->getMessage()]);
                }
            }

            $this->pdo->commit();
        } catch (Throwable $e) {
            $this->pdo->rollBack();
            $this->log->error('ingest transaction failed', ['err' => $e->getMessage()]);
            return self::error($response, 500, 'ingest transaction failed');
        }

        $this->log->info('ingest accepted', [
            'table' => $table, 'key' => $idempotencyKey,
            'accepted' => $accepted, 'rejected' => count($errors),
        ]);

        return self::json($response, [
            'accepted' => $accepted,
            'rejected' => count($errors),
            'errors' => $errors,
            'idempotency_key' => $idempotencyKey,
        ]);
    }

    private function upsert(string $table, array $row): void
    {
        $allowed = self::TABLE_COLUMNS[$table];
        $filtered = array_intersect_key($row, array_flip($allowed));
        if (empty($filtered)) {
            throw new \InvalidArgumentException('no recognized columns in row');
        }
        // Encode any nested arrays/objects as JSON strings
        foreach ($filtered as $col => $val) {
            if (is_array($val) || is_object($val)) {
                $filtered[$col] = json_encode($val, JSON_UNESCAPED_UNICODE);
            }
        }
        $cols = array_keys($filtered);
        $placeholders = array_map(fn($c) => ":{$c}", $cols);
        $driver = $this->pdo->getAttribute(\PDO::ATTR_DRIVER_NAME);

        if ($driver === 'mysql') {
            $updates = array_map(fn($c) => "{$c} = VALUES({$c})", $cols);
            $sql = sprintf(
                'INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s',
                $table, implode(', ', $cols), implode(', ', $placeholders), implode(', ', $updates),
            );
        } else {
            // sqlite / postgres ANSI-style upsert (used by tests)
            $updates = array_map(fn($c) => "{$c} = excluded.{$c}", $cols);
            $conflictKey = match ($table) {
                'product_prices'        => 'product_id, price_date, source',
                'crop_field_enrichment' => 'crop_id, field_name',
                'crop_attribute'        => 'crop_id, attribute_key',
                'crop_content'          => 'crop_id, content_type',
                'crop_content_source'   => 'crop_id, content_type, source_label',
                default                 => 'id',
            };
            $sql = sprintf(
                'INSERT INTO %s (%s) VALUES (%s) ON CONFLICT (%s) DO UPDATE SET %s',
                $table, implode(', ', $cols), implode(', ', $placeholders),
                $conflictKey, implode(', ', $updates),
            );
        }

        $stmt = $this->pdo->prepare($sql);
        foreach ($filtered as $col => $val) {
            $stmt->bindValue(":{$col}", $val);
        }
        $stmt->execute();
    }

    private function delete(string $table, array $row): void
    {
        if (!isset($row['id'])) {
            throw new \InvalidArgumentException('delete row must include id');
        }
        $stmt = $this->pdo->prepare("DELETE FROM {$table} WHERE id = ?");
        $stmt->execute([$row['id']]);
    }

    private static function json(Response $r, array $p, int $s = 200): Response
    {
        $r->getBody()->write(json_encode($p, JSON_UNESCAPED_UNICODE));
        return $r->withStatus($s)->withHeader('Content-Type', 'application/json; charset=utf-8');
    }

    private static function error(Response $r, int $status, string $msg): Response
    {
        return self::json($r, ['error' => true, 'message' => $msg], $status);
    }
}
