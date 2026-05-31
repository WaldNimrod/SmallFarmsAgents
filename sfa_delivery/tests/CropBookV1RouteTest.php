<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

/**
 * CropBookV1RouteTest — WP-CB-1 route smoke tests.
 *
 * Tests:
 *   - GET /api/v1/assumptions returns JSON with germination_rate + bed_width
 *   - POST /api/v1/contribute with kind=request-info returns 200
 *   - GET /crop-book/ with ?view=cards returns 200
 *   - GET /crop-book/ with ?view=table returns 200
 *   - GET /crop-book/{slug}/?depth=simple returns 200
 *   - GET /crop-book/{slug}/?depth=full returns 200
 *   - GET /crop-book/{slug}/?depth=drill returns 200
 *   - GET /calc/ returns 200 (dashboard)
 *
 * @see DISPATCH §7
 */
final class CropBookV1RouteTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crops (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, scientific_name TEXT, family_name_he TEXT, category TEXT, season TEXT, dtm_min INTEGER, dtm_max INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crop_varieties (id INTEGER PRIMARY KEY, crop_id INTEGER, name TEXT, payload_json TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS product_prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price_date TEXT, price REAL, source TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS ingest_log (idempotency_key TEXT PRIMARY KEY, table_name TEXT, applied_at TEXT, row_count INTEGER, status TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS cover_crops (id INTEGER PRIMARY KEY, name_he TEXT, name_en TEXT, category TEXT, sow_window TEXT, total_days_garden INTEGER, survives_winter INTEGER, notes TEXT)');

        $this->pdo->exec("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (1,'lettuce','חסה','Lactuca sativa','חסתיים','vegetables','winter',45,60,'{}','2026-05-31'),
            (2,'radish','צנונית','Raphanus sativus','מצליבים','vegetables','spring',25,35,'{}','2026-05-31')");

        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id,crop_id,name,payload_json) VALUES (101,1,'Batavian','{}')");
    }

    private function get(string $path): \Psr\Http\Message\ResponseInterface
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', $path);
        return $this->app->handle($req);
    }

    private function post(string $path, array $data): \Psr\Http\Message\ResponseInterface
    {
        $req = (new ServerRequestFactory())
            ->createServerRequest('POST', $path)
            ->withHeader('Content-Type', 'application/json')
            ->withParsedBody($data);
        return $this->app->handle($req);
    }

    // ── assumptions endpoint ──────────────────────────────────────

    public function testAssumptionsEndpointReturns200(): void
    {
        $res = $this->get('/api/v1/assumptions');
        $this->assertSame(200, $res->getStatusCode(), '/api/v1/assumptions must return 200');
    }

    public function testAssumptionsEndpointReturnsJson(): void
    {
        $res  = $this->get('/api/v1/assumptions');
        $body = json_decode((string)$res->getBody(), true);
        $this->assertIsArray($body);
        $this->assertArrayHasKey('germination_rate', $body, 'germination_rate must be in registry');
        $this->assertArrayHasKey('bed_width', $body,       'bed_width must be in registry');
    }

    public function testAssumptionsHasPostUrlForLaunchBlockers(): void
    {
        $res  = $this->get('/api/v1/assumptions');
        $body = json_decode((string)$res->getBody(), true);
        // Launch-blocking: germination_rate + bed_width MUST have post_url
        $this->assertNotNull($body['germination_rate']['post_url'],
            'germination_rate must have post_url (launch-blocking)');
        $this->assertNotNull($body['bed_width']['post_url'],
            'bed_width must have post_url (launch-blocking)');
    }

    // ── contribute endpoint ───────────────────────────────────────

    public function testContributeReturns200ForRequestInfo(): void
    {
        $res = $this->post('/api/v1/contribute', [
            'kind'       => 'request-info',
            'field_name' => 'seeds_per_g',
            'crop_slug'  => 'lettuce',
        ]);
        $this->assertSame(200, $res->getStatusCode());
        $body = json_decode((string)$res->getBody(), true);
        $this->assertTrue($body['ok'] ?? false);
    }

    public function testContributeReturns400ForUnknownKind(): void
    {
        $res = $this->post('/api/v1/contribute', [
            'kind' => 'unknown-kind',
        ]);
        $this->assertSame(400, $res->getStatusCode());
    }

    // ── crop-book index routes ────────────────────────────────────

    public function testBookIndexCardsView(): void
    {
        $res = $this->get('/crop-book/?view=cards');
        $this->assertSame(200, $res->getStatusCode(), 'Crop-book cards view must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('aud__opt', $html, 'Must include audience switch');
    }

    public function testBookIndexTableView(): void
    {
        $res = $this->get('/crop-book/?view=table');
        $this->assertSame(200, $res->getStatusCode(), 'Crop-book table view must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('ptable', $html, 'Table view must include .ptable');
    }

    // ── crop page depths ──────────────────────────────────────────

    public function testBookCropSimpleDepth(): void
    {
        $res  = $this->get('/crop-book/lettuce/?depth=simple');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('depths', $html, 'Must include depth tabs');
        $this->assertStringContainsString('headvals', $html, 'Simple depth must include headline values');
    }

    public function testBookCropFullDepth(): void
    {
        $res  = $this->get('/crop-book/lettuce/?depth=full');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('topic', $html, 'Full depth must include topic sections');
    }

    public function testBookCropDrillDepth(): void
    {
        $res  = $this->get('/crop-book/lettuce/?depth=drill');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('vtable', $html, 'Drill depth must include variety table');
    }

    public function testBookCropDefaultDepth(): void
    {
        // No depth param — should default to simple
        $res  = $this->get('/crop-book/lettuce/');
        $this->assertSame(200, $res->getStatusCode());
    }

    // ── calculator dashboard ──────────────────────────────────────

    public function testCalcDashReturns200(): void
    {
        $res  = $this->get('/calc/');
        $this->assertSame(200, $res->getStatusCode(), '/calc/ must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('calc-page', $html, 'Calc dashboard must include .calc-page');
        $this->assertStringContainsString('calc-dash', $html, 'Calc dashboard must include .calc-dash');
    }
}
