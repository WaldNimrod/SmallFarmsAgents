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
 * Integration smoke test for /api/v1/ingest end-to-end:
 * - boots the Slim app with sqlite in-memory DB
 * - applies migrations (SQLite-adapted minimal schema)
 * - posts HMAC-signed payload
 * - asserts row inserted, idempotency works, bad HMAC returns 401
 */
final class IngestSmokeTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);

        // Container PDO is sqlite::memory: (from phpunit.xml DB_DSN)
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        // Apply SQLite-flavored DDL (subset matching ingest needs)
        $this->pdo->exec("
            CREATE TABLE schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT);
            CREATE TABLE ingest_log (
              idempotency_key TEXT PRIMARY KEY,
              table_name TEXT NOT NULL,
              applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
              row_count INTEGER NOT NULL,
              status TEXT NOT NULL
            );
            CREATE TABLE crops (
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
        ");
    }

    public function testIngestAcceptsValidPayload(): void
    {
        $payload = [
            'schema_version' => 1,
            'table' => 'crops',
            'operation' => 'upsert',
            'idempotency_key' => 'crops_test_001',
            'rows' => [[
                'id' => 1, 'slug' => 'tomato', 'hebrew_name' => 'עגבנייה',
                'category' => 'vegetable', 'season' => 'spring',
                'dtm_min' => 60, 'dtm_max' => 90,
                'last_pushed_at' => '2026-05-23 12:00:00',
                'payload_json' => ['schema_version' => 1, 'description_md' => 'test'],
            ]],
        ];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $resp->getStatusCode(), (string)$resp->getBody());
        $body = json_decode((string)$resp->getBody(), true);
        $this->assertSame(1, $body['accepted']);
        $this->assertSame(0, $body['rejected']);

        $row = $this->pdo->query('SELECT slug, hebrew_name FROM crops WHERE id = 1')->fetch();
        $this->assertSame('tomato', $row['slug']);
        $this->assertSame('עגבנייה', $row['hebrew_name']);
    }

    public function testIngestRejectsBadHmac(): void
    {
        $payload = ['schema_version' => 1, 'table' => 'crops', 'operation' => 'upsert',
            'idempotency_key' => 'x', 'rows' => []];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: false);
        $this->assertSame(401, $resp->getStatusCode());
    }

    public function testIngestRejectsUnknownTable(): void
    {
        $payload = ['schema_version' => 1, 'table' => 'unknown', 'operation' => 'upsert',
            'idempotency_key' => 'x2', 'rows' => []];
        $resp = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(400, $resp->getStatusCode());
    }

    public function testIdempotencyReplay(): void
    {
        $payload = [
            'schema_version' => 1, 'table' => 'crops', 'operation' => 'upsert',
            'idempotency_key' => 'crops_test_replay',
            'rows' => [[
                'id' => 2, 'slug' => 'cucumber', 'hebrew_name' => 'מלפפון',
                'last_pushed_at' => '2026-05-23 12:00:00',
                'payload_json' => ['schema_version' => 1],
            ]],
        ];
        $first = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $first->getStatusCode());
        $firstBody = json_decode((string)$first->getBody(), true);
        $this->assertSame(1, $firstBody['accepted']);

        // Replay
        $second = $this->post('/api/v1/ingest', $payload, withValidSig: true);
        $this->assertSame(200, $second->getStatusCode());
        $secondBody = json_decode((string)$second->getBody(), true);
        $this->assertTrue($secondBody['duplicate'] ?? false);
    }

    private function post(string $path, array $payload, bool $withValidSig): \Psr\Http\Message\ResponseInterface
    {
        $body = json_encode($payload, JSON_UNESCAPED_UNICODE);
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
