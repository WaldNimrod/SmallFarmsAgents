<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

final class ProductsController
{
    public function __construct(private PDO $pdo) {}

    public function list(Request $request, Response $response): Response
    {
        $q = $request->getQueryParams();
        $category = $q['category'] ?? null;
        $maxFreshness = isset($q['max_freshness_days']) ? (int)$q['max_freshness_days'] : null;

        $sql = 'SELECT id, slug, hebrew_name, category, unit, last_price,
                       last_price_date, freshness_days
                FROM products WHERE 1=1';
        $params = [];
        if ($category !== null)     { $sql .= ' AND category = ?';        $params[] = $category; }
        if ($maxFreshness !== null) { $sql .= ' AND freshness_days <= ?'; $params[] = $maxFreshness; }
        $sql .= ' ORDER BY category, hebrew_name';

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll();

        return self::json($response, ['count' => count($rows), 'items' => $rows]);
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');

        $stmt = $this->pdo->prepare(
            'SELECT id, slug, hebrew_name, category, unit, last_price,
                    last_price_date, freshness_days, last_pushed_at, payload_json
             FROM products WHERE slug = ?'
        );
        $stmt->execute([$slug]);
        $product = $stmt->fetch();
        if ($product === false) {
            return self::error($response, 404, 'product not found');
        }

        if (!empty($product['payload_json'])) {
            $payload = json_decode($product['payload_json'], true);
            unset($product['payload_json']);
            $product = array_merge($product, $payload ?? []);
        }

        // Fetch price history (last 30 days)
        $priceStmt = $this->pdo->prepare(
            'SELECT price_date, price, source FROM product_prices
             WHERE product_id = ? AND price_date >= (CURRENT_DATE - INTERVAL 30 DAY)
             ORDER BY price_date'
        );
        $priceStmt->execute([$product['id']]);
        $product['price_history_30d'] = $priceStmt->fetchAll();

        return self::json($response, $product);
    }

    private static function json(Response $r, array $p, int $s = 200): Response
    {
        $r->getBody()->write(json_encode($p, JSON_UNESCAPED_UNICODE));
        return $r->withStatus($s)->withHeader('Content-Type', 'application/json; charset=utf-8');
    }

    private static function error(Response $r, int $s, string $m): Response
    {
        return self::json($r, ['error' => true, 'message' => $m], $s);
    }
}
