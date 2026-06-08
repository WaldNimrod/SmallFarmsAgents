<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

final class RouteSmokeTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec('CREATE TABLE crops (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, scientific_name TEXT, family_name_he TEXT, category TEXT, season TEXT, dtm_min INTEGER, dtm_max INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE crop_varieties (id INTEGER PRIMARY KEY, crop_id INTEGER, name TEXT, payload_json TEXT)');
        // cover_crops table — AC-U4-02; controller tolerates its absence, but smoke test creates it.
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS cover_crops (id INTEGER PRIMARY KEY, name_he TEXT, name_en TEXT, category TEXT, sow_window TEXT, total_days_garden INTEGER, survives_winter INTEGER, notes TEXT)');
        $this->pdo->exec('CREATE TABLE products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE product_prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price_date TEXT, price REAL, source TEXT)');
        $this->pdo->exec('CREATE TABLE ingest_log (idempotency_key TEXT PRIMARY KEY, table_name TEXT, applied_at TEXT, row_count INTEGER, status TEXT)');
        $this->pdo->exec('CREATE TABLE schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT)');

        $this->pdo->exec("INSERT INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (1,'anise-hyssop','אניס','Agastache','שפתניים','vegetables','spring',60,80,'{}','2026-05-27'),
            (2,'tomato','עגבנייה','Solanum','סולניים','vegetables','summer',70,95,'{}','2026-05-27')");
        $this->pdo->exec("INSERT INTO crop_varieties (id,crop_id,name,payload_json) VALUES (11,1,'Blue Fortune','{\"notes\":\"aromatic\"}')");
        $this->pdo->exec("INSERT INTO products (id,slug,hebrew_name,category,unit,last_price,last_price_date,freshness_days,payload_json,last_pushed_at) VALUES
            (10,'onion-dry','בצל יבש','vegetable','kg',12.5,'2026-05-26',2,'{}','2026-05-27')");
        $this->pdo->exec("INSERT INTO product_prices (product_id,price_date,price,source) VALUES (10,'2026-05-25',11.9,'farm')");
    }

    /** @dataProvider routes */
    public function testHtmlRoutesReturnSuccess(string $path): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', $path);
        $res = $this->app->handle($req);
        $this->assertSame(200, $res->getStatusCode(), $path . ' => ' . (string)$res->getBody());
        $this->assertStringContainsString('text/html', (string)$res->getHeaderLine('Content-Type'));
    }

    public function routes(): array
    {
        return [
            ['/'],
            ['/about/'],
            ['/search/'],
            ['/calc/'],
            ['/crop-book/'],
            ['/crop-book/questions/'],
            ['/crop-book/family/'],
            ['/crop-book/table/'],
            ['/crop-book/search/?q=עגב'],
            ['/crop-book/anise-hyssop/'],
            ['/crop-book/anise-hyssop/variety/variety-11/'],
            ['/crop-book/cover-crops/'],
            ['/market/'],
            ['/market/onion-dry/'],
            ['/community/'],
            ['/assumptions/'],
        ];
    }
}
