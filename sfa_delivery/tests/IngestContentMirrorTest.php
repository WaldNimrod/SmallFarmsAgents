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
 * WP-CB-CONTENT — Delivery-tier ingest tests for crop_content + crop_content_source.
 *
 * Mirrors IngestEnrichmentMirrorTest: TABLE_COLUMNS whitelist, composite-PK upsert,
 * idempotency replay, column-allowlist filtering. SQLite in-memory (phpunit DB_DSN).
 */
final class IngestContentMirrorTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec("
            CREATE TABLE IF NOT EXISTS ingest_log (
              idempotency_key TEXT PRIMARY KEY,
              table_name TEXT NOT NULL,
              applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
              row_count INTEGER NOT NULL,
              status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS crops (
              id INTEGER PRIMARY KEY, slug TEXT UNIQUE NOT NULL, hebrew_name TEXT NOT NULL,
              last_pushed_at TEXT NOT NULL, payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS crop_content (
              crop_id INTEGER NOT NULL,
              content_type TEXT NOT NULL,
              text_md TEXT,
              winning_source_class TEXT,
              confidence_score REAL,
              field_state TEXT,
              last_pushed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (crop_id, content_type)
            );
            CREATE TABLE IF NOT EXISTS crop_content_source (
              crop_id INTEGER NOT NULL,
              content_type TEXT NOT NULL,
              source_label TEXT NOT NULL,
              source_class TEXT NOT NULL,
              raw_text_md TEXT NOT NULL,
              source_url TEXT,
              display_order INTEGER NOT NULL DEFAULT 0,
              last_pushed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (crop_id, content_type, source_label)
            );
        ");
        $this->pdo->exec("
            INSERT OR IGNORE INTO crops (id, slug, hebrew_name, last_pushed_at, payload_json)
            VALUES (1, 'lettuce', 'חסה', '2026-06-09 00:00:00', '{\"schema_version\":1}')
        ");
    }

    public function testCropContentAcceptedAndStored(): void
    {
        $resp = $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_content', 'operation' => 'upsert',
            'idempotency_key' => 'cc_001',
            'rows' => [[
                'crop_id' => 1, 'content_type' => 'story', 'text_md' => 'סיפור החסה',
                'winning_source_class' => 'NI', 'confidence_score' => 1.0,
                'field_state' => 'VALIDATED', 'last_pushed_at' => '2026-06-09 00:00:00',
                'bogus_col' => 'DROP ME',
            ]],
        ], withValidSig: true);
        $this->assertSame(200, $resp->getStatusCode(), (string)$resp->getBody());
        $body = json_decode((string)$resp->getBody(), true);
        $this->assertSame(1, $body['accepted']);

        $row = $this->pdo->query(
            "SELECT content_type, text_md, winning_source_class, field_state FROM crop_content WHERE crop_id = 1"
        )->fetch(PDO::FETCH_ASSOC);
        $this->assertSame('story', $row['content_type']);
        $this->assertSame('סיפור החסה', $row['text_md']);
        $this->assertSame('NI', $row['winning_source_class']);
        $this->assertSame('VALIDATED', $row['field_state']);
        // bogus_col silently dropped by the allowlist (no column to write to)
        $cols = $this->pdo->query("PRAGMA table_info(crop_content)")->fetchAll(PDO::FETCH_COLUMN, 1);
        $this->assertNotContains('bogus_col', $cols);
    }

    public function testCropContentSourceAcceptedAndStored(): void
    {
        $resp = $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_content_source', 'operation' => 'upsert',
            'idempotency_key' => 'ccs_001',
            'rows' => [
                ['crop_id' => 1, 'content_type' => 'story', 'source_label' => 'NI:groworganic',
                 'source_class' => 'NI', 'raw_text_md' => 'גרסה ישראלית', 'source_url' => 'https://x',
                 'display_order' => 1, 'last_pushed_at' => '2026-06-09 00:00:00'],
                ['crop_id' => 1, 'content_type' => 'story', 'source_label' => 'JMF',
                 'source_class' => 'PR', 'raw_text_md' => 'גרסת JMF', 'source_url' => null,
                 'display_order' => 2, 'last_pushed_at' => '2026-06-09 00:00:00'],
            ],
        ], withValidSig: true);
        $this->assertSame(200, $resp->getStatusCode(), (string)$resp->getBody());
        $this->assertSame(2, json_decode((string)$resp->getBody(), true)['accepted']);

        $rows = $this->pdo->query(
            "SELECT source_label, source_class, display_order FROM crop_content_source
             WHERE crop_id = 1 AND content_type = 'story' ORDER BY display_order"
        )->fetchAll(PDO::FETCH_ASSOC);
        $this->assertCount(2, $rows);
        $this->assertSame('NI:groworganic', $rows[0]['source_label']);
        $this->assertSame('JMF', $rows[1]['source_label']);
    }

    public function testCompositeKeyUpsertStable(): void
    {
        $row = ['crop_id' => 1, 'content_type' => 'care_watering', 'source_label' => 'JMF',
                'source_class' => 'PR', 'raw_text_md' => 'v1', 'display_order' => 2,
                'last_pushed_at' => '2026-06-09 00:00:00'];
        $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_content_source', 'operation' => 'upsert',
            'idempotency_key' => 'ccs_stable_A', 'rows' => [$row],
        ], withValidSig: true);
        // Same composite key, new idempotency key, updated body → upsert, not duplicate row.
        $row['raw_text_md'] = 'v2';
        $this->post('/api/v1/ingest', [
            'schema_version' => 1, 'table' => 'crop_content_source', 'operation' => 'upsert',
            'idempotency_key' => 'ccs_stable_B', 'rows' => [$row],
        ], withValidSig: true);

        $count = $this->pdo->query(
            "SELECT COUNT(*) FROM crop_content_source
             WHERE crop_id = 1 AND content_type = 'care_watering' AND source_label = 'JMF'"
        )->fetchColumn();
        $this->assertSame('1', (string)$count);
        $body = $this->pdo->query(
            "SELECT raw_text_md FROM crop_content_source
             WHERE crop_id = 1 AND content_type = 'care_watering' AND source_label = 'JMF'"
        )->fetchColumn();
        $this->assertSame('v2', $body);
    }

    public function testIdempotencyReplay(): void
    {
        $payload = [
            'schema_version' => 1, 'table' => 'crop_content', 'operation' => 'upsert',
            'idempotency_key' => 'cc_replay_001',
            'rows' => [[
                'crop_id' => 1, 'content_type' => 'care_pests', 'text_md' => 'מזיקים',
                'field_state' => 'VALIDATED', 'last_pushed_at' => '2026-06-09 00:00:00',
            ]],
        ];
        $first = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(1, json_decode((string)$first->getBody(), true)['accepted']);
        $second = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertTrue(json_decode((string)$second->getBody(), true)['duplicate'] ?? false);
    }

    private function post(string $path, array $payload, bool $withValidSig): \Psr\Http\Message\ResponseInterface
    {
        $body   = json_encode($payload, JSON_UNESCAPED_UNICODE);
        $secret = $_ENV['INGEST_HMAC_SECRET'];
        $req = (new ServerRequestFactory())
            ->createServerRequest('POST', $path)
            ->withHeader('Content-Type', 'application/json')
            ->withHeader('X-SFA-Auth', $withValidSig ? Hmac::sign($body, $secret) : 'sha256=' . str_repeat('0', 64))
            ->withBody((new StreamFactory())->createStream($body));
        return $this->app->handle($req);
    }
}
