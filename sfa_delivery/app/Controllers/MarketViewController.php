<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class MarketViewController
{
    public function __construct(private PDO $pdo) {}

    public function index(Request $request, Response $response): Response
    {
        $q = $request->getQueryParams();
        $category = $q['category'] ?? null;

        $sql = 'SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days
                FROM products WHERE 1=1';
        $params = [];
        if ($category !== null && $category !== '') { $sql .= ' AND category = ?'; $params[] = $category; }
        $sql .= ' ORDER BY category, hebrew_name';
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        $products = $stmt->fetchAll();

        $cats = $this->pdo->query(
            'SELECT category, COUNT(*) c FROM products WHERE category IS NOT NULL GROUP BY category ORDER BY category'
        )->fetchAll();

        $html = Template::render('market/list', [
            'products' => $products,
            'categories' => $cats,
            'current_category' => $category,
            'total' => count($products),
        ]);
        return self::html($response, $html);
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $stmt = $this->pdo->prepare(
            'SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date,
                    freshness_days, last_pushed_at, payload_json
             FROM products WHERE slug = ?'
        );
        $stmt->execute([$slug]);
        $product = $stmt->fetch();
        if (!$product) {
            $html = Template::render('error', ['code' => 404, 'message' => 'מוצר לא נמצא']);
            return self::html($response, $html, 404);
        }
        $payload = !empty($product['payload_json']) ? (json_decode($product['payload_json'], true) ?: []) : [];
        $product = array_merge($product, $payload);
        unset($product['payload_json']);

        $priceStmt = $this->pdo->prepare(
            'SELECT price_date, price, source FROM product_prices
             WHERE product_id = ? AND price_date >= (CURRENT_DATE - INTERVAL 30 DAY)
             ORDER BY price_date DESC LIMIT 30'
        );
        $priceStmt->execute([$product['id']]);
        $history = $priceStmt->fetchAll();

        $html = Template::render('market/detail', [
            'product' => $product, 'history' => $history,
        ]);
        return self::html($response, $html);
    }

    private static function html(Response $r, string $body, int $status = 200): Response
    {
        $r->getBody()->write($body);
        return $r->withStatus($status)->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
