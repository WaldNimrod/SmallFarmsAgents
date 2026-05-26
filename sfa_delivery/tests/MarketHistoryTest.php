<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

final class MarketHistoryTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec('CREATE TABLE products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE product_prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price_date TEXT, price REAL, source TEXT)');

        $this->pdo->exec("INSERT INTO products (id,slug,hebrew_name,payload_json,last_pushed_at) VALUES (10,'onion-dry','בצל יבש','{}','2026-05-27')");
        $this->pdo->exec("INSERT INTO product_prices (product_id,price_date,price,source) VALUES (10,'2026-05-20',12.1,'market')");
    }

    public function testHistoryApiReturnsRows(): void
    {
        $res = $this->app->handle((new ServerRequestFactory())->createServerRequest('GET', '/api/v1/market/onion-dry/history?days=28'));
        $this->assertSame(200, $res->getStatusCode());
        $rows = json_decode((string)$res->getBody(), true);
        $this->assertNotEmpty($rows);
    }

    public function testHistoryApiReturnsEmptyForUnknownProduct(): void
    {
        $res = $this->app->handle((new ServerRequestFactory())->createServerRequest('GET', '/api/v1/market/missing/history?days=28'));
        $this->assertSame(200, $res->getStatusCode());
        $rows = json_decode((string)$res->getBody(), true);
        $this->assertSame([], $rows);
    }
}
