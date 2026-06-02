<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use SFA\Lib\Hmac;
use Slim\Psr7\Factory\ServerRequestFactory;
use Slim\Psr7\Factory\StreamFactory;

/**
 * WP-CB-DATA WI-5 — Delivery-tier ingest tests for crop_field_enrichment + crop_attribute.
 *
 * AC-02: TABLE_COLUMNS includes both new tables; unknown-table still 400.
 * AC-08: same-key re-push → duplicate=true; fresh-data upsert stable row count.
 *
 * Uses sqlite in-memory (from phpunit.xml DB_DSN).
 * The .sql files are MySQL; the sqlite DDL below mirrors only what the PHP
 * ingest path needs (whitelist validation + ON CONFLICT composite-PK upsert).
 */
final class IngestEnrichmentMirrorTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);

        $this->pdo = $this->app->getContainer()->get(PDO::class);

        // Minimal SQLite schema: ingest_log + crops (FK parent) +
        // crop_field_enrichment + crop_attribute (composite PK).
        $this->pdo->exec("
            CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT);
            CREATE TABLE IF NOT EXISTS ingest_log (
              idempotency_key TEXT PRIMARY KEY,
              table_name TEXT NOT NULL,
              applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
              row_count INTEGER NOT NULL,
              status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS crops (
              id INTEGER PRIMARY KEY,
              slug TEXT UNIQUE NOT NULL,
              hebrew_name TEXT NOT NULL,
              scientific_name TEXT,
              family_id INTEGER,
              family_name_he TEXT,
              category TEXT,
              season TEXT,
              dtm_min INTEGER,
              dtm_max INTEGER,
              last_pushed_at TEXT NOT NULL,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS crop_field_enrichment (
              crop_id INTEGER NOT NULL,
              field_name TEXT NOT NULL,
              value_best REAL,
              unit TEXT,
              field_state TEXT NOT NULL DEFAULT 'UNVALIDATED',
              winning_source_class TEXT,
              confidence_score REAL,
              last_pushed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (crop_id, field_name)
            );
            CREATE TABLE IF NOT EXISTS crop_attribute (
              crop_id INTEGER NOT NULL,
              attribute_key TEXT NOT NULL,
              value_canonical TEXT,
              value_list TEXT,
              field_state TEXT,
              last_pushed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (crop_id, attribute_key)
            );
        ");

        // Seed a crop row (FK parent for enrichment/attribute).
        $this->pdo->exec("
            INSERT OR IGNORE INTO crops
              (id, slug, hebrew_name, last_pushed_at, payload_json)
            VALUES (1, 'tomato', 'עגבנייה', '2026-06-03 00:00:00', '{\"schema_version\":1}')
        ");
    }

    // -----------------------------------------------------------------------
    // AC-02: TABLE_COLUMNS whitelist
    // -----------------------------------------------------------------------

    public function testCropFieldEnrichmentTableIsAccepted(): void
    {
        $payload = [
            'schema_version'  => 1,
            'table'           => 'crop_field_enrichment',
            'operation'       => 'upsert',
            'idempotency_key' => 'cfe_test_001',
            'rows'            => [[
                'crop_id'              => 1,
                'field_name'           => 'days_to_maturity',
                'value_best'           => 75.0,
                'unit'                 => 'days',
                'field_state'          => 'VALIDATED',
                'winning_source_class' => 'EX',
                'confidence_score'     => 0.90,
                'last_pushed_at'       => '2026-06-03 00:00:00',
            ]],
        ];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $resp->getStatusCode(), (string)$resp->getBody());
        $body = json_decode((string)$resp->getBody(), true);
        $this->assertSame(1, $body['accepted']);
        $this->assertSame(0, $body['rejected']);

        $row = $this->pdo->query(
            "SELECT field_name, value_best, unit, field_state FROM crop_field_enrichment WHERE crop_id = 1"
        )->fetch(PDO::FETCH_ASSOC);
        $this->assertSame('days_to_maturity', $row['field_name']);
        $this->assertEqualsWithDelta(75.0, (float)$row['value_best'], 0.001);
        $this->assertSame('days', $row['unit']);
        $this->assertSame('VALIDATED', $row['field_state']);
    }

    public function testCropAttributeTableIsAccepted(): void
    {
        $payload = [
            'schema_version'  => 1,
            'table'           => 'crop_attribute',
            'operation'       => 'upsert',
            'idempotency_key' => 'ca_test_001',
            'rows'            => [[
                'crop_id'         => 1,
                'attribute_key'   => 'planting_method',
                'value_canonical' => 'direct_seed',
                'value_list'      => null,
                'field_state'     => 'VALIDATED',
                'last_pushed_at'  => '2026-06-03 00:00:00',
            ]],
        ];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $resp->getStatusCode(), (string)$resp->getBody());
        $body = json_decode((string)$resp->getBody(), true);
        $this->assertSame(1, $body['accepted']);

        $row = $this->pdo->query(
            "SELECT attribute_key, value_canonical, field_state FROM crop_attribute WHERE crop_id = 1"
        )->fetch(PDO::FETCH_ASSOC);
        $this->assertSame('planting_method', $row['attribute_key']);
        $this->assertSame('direct_seed', $row['value_canonical']);
        $this->assertSame('VALIDATED', $row['field_state']);
    }

    public function testUnknownTableStillReturns400(): void
    {
        $payload = [
            'schema_version'  => 1,
            'table'           => 'bogus_table_xyz',
            'operation'       => 'upsert',
            'idempotency_key' => 'bogus_001',
            'rows'            => [],
        ];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(400, $resp->getStatusCode());
        $body = json_decode((string)$resp->getBody(), true);
        $this->assertTrue($body['error']);
    }

    // -----------------------------------------------------------------------
    // AC-08: idempotency — same-key re-push returns duplicate=true
    // -----------------------------------------------------------------------

    public function testCropFieldEnrichmentIdempotencyReplay(): void
    {
        $payload = [
            'schema_version'  => 1,
            'table'           => 'crop_field_enrichment',
            'operation'       => 'upsert',
            'idempotency_key' => 'cfe_replay_001',
            'rows'            => [[
                'crop_id'        => 1,
                'field_name'     => 'rows_per_bed',
                'value_best'     => 4.0,
                'unit'           => 'count',
                'field_state'    => 'VALIDATED',
                'last_pushed_at' => '2026-06-03 00:00:00',
            ]],
        ];

        $first = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $first->getStatusCode());
        $firstBody = json_decode((string)$first->getBody(), true);
        $this->assertSame(1, $firstBody['accepted']);

        // Replay with same idempotency key.
        $second = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $second->getStatusCode());
        $secondBody = json_decode((string)$second->getBody(), true);
        $this->assertTrue($secondBody['duplicate'] ?? false, 'expected duplicate=true on replay');
    }

    public function testCropAttributeIdempotencyReplay(): void
    {
        $payload = [
            'schema_version'  => 1,
            'table'           => 'crop_attribute',
            'operation'       => 'upsert',
            'idempotency_key' => 'ca_replay_001',
            'rows'            => [[
                'crop_id'         => 1,
                'attribute_key'   => 'harvest_unit',
                'value_canonical' => 'kg',
                'field_state'     => 'VALIDATED',
                'last_pushed_at'  => '2026-06-03 00:00:00',
            ]],
        ];

        $first = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $first->getStatusCode());
        $firstBody = json_decode((string)$first->getBody(), true);
        $this->assertSame(1, $firstBody['accepted']);

        $second = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $second->getStatusCode());
        $secondBody = json_decode((string)$second->getBody(), true);
        $this->assertTrue($secondBody['duplicate'] ?? false, 'expected duplicate=true on replay');
    }

    // -----------------------------------------------------------------------
    // AC-08: upsert stability — re-push with same key does not double-count rows
    // -----------------------------------------------------------------------

    public function testCropFieldEnrichmentUpsertStableRowCount(): void
    {
        // Push with key A, then push same (crop_id, field_name) with new key B.
        $rowData = [
            'crop_id'        => 1,
            'field_name'     => 'spacing_in_row_cm',
            'value_best'     => 20.0,
            'unit'           => 'cm',
            'field_state'    => 'UNVALIDATED',
            'last_pushed_at' => '2026-06-03 00:00:00',
        ];

        $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_field_enrichment',
            'operation' => 'upsert', 'idempotency_key' => 'cfe_stable_A',
            'rows' => [$rowData],
        ], withValidSig: true);

        // Same (crop_id, field_name) with updated value_best and new key.
        $rowData['value_best'] = 25.0;
        $rowData['field_state'] = 'VALIDATED';
        $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_field_enrichment',
            'operation' => 'upsert', 'idempotency_key' => 'cfe_stable_B',
            'rows' => [$rowData],
        ], withValidSig: true);

        // Only one row per (crop_id, field_name) — upsert, not double-insert.
        $count = $this->pdo->query(
            "SELECT COUNT(*) FROM crop_field_enrichment WHERE crop_id = 1 AND field_name = 'spacing_in_row_cm'"
        )->fetchColumn();
        $this->assertSame('1', (string)$count);

        // Row has the updated value.
        $row = $this->pdo->query(
            "SELECT value_best, field_state FROM crop_field_enrichment
             WHERE crop_id = 1 AND field_name = 'spacing_in_row_cm'"
        )->fetch(PDO::FETCH_ASSOC);
        $this->assertEqualsWithDelta(25.0, (float)$row['value_best'], 0.001);
        $this->assertSame('VALIDATED', $row['field_state']);
    }

    // -----------------------------------------------------------------------
    // Helper
    // -----------------------------------------------------------------------

    private function post(string $path, array $payload, bool $withValidSig): \Psr\Http\Message\ResponseInterface
    {
        $body   = json_encode($payload, JSON_UNESCAPED_UNICODE);
        $secret = $_ENV['INGEST_HMAC_SECRET'];

        $req = (new ServerRequestFactory())
            ->createServerRequest('POST', $path)
            ->withHeader('Content-Type', 'application/json')
            ->withHeader('X-SFA-Auth', $withValidSig
                ? Hmac::sign($body, $secret)
                : 'sha256=' . str_repeat('0', 64))
            ->withBody((new StreamFactory())->createStream($body));

        return $this->app->handle($req);
    }
}
