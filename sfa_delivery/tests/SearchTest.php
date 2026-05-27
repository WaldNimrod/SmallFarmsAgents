<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

final class SearchTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec('CREATE TABLE crops (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, scientific_name TEXT, family_name_he TEXT, category TEXT, season TEXT, dtm_min INTEGER, dtm_max INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');

        $this->pdo->exec("INSERT INTO crops (id,slug,hebrew_name,payload_json,last_pushed_at) VALUES (1,'tomato','עגבנייה','{}','2026-05-27')");
        $this->pdo->exec("INSERT INTO products (id,slug,hebrew_name,payload_json,last_pushed_at) VALUES (1,'pepper','פלפל','{}','2026-05-27')");
    }

    public function testSearchReturnsBothArrays(): void
    {
        $res = $this->app->handle((new ServerRequestFactory())->createServerRequest('GET', '/api/v1/search?q=ע'));
        $this->assertSame(200, $res->getStatusCode());
        $data = json_decode((string)$res->getBody(), true);
        $this->assertIsArray($data['crops']);
        $this->assertIsArray($data['products']);
    }

    public function testSearchEmptyQueryReturnsEmptyCollections(): void
    {
        $res = $this->app->handle((new ServerRequestFactory())->createServerRequest('GET', '/api/v1/search?q='));
        $data = json_decode((string)$res->getBody(), true);
        $this->assertSame([], $data['crops']);
        $this->assertSame([], $data['products']);
    }
}
