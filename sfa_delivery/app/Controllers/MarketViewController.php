<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class MarketViewController
{
    public function __construct(private PDO $pdo)
    {
    }

    public function index(Request $request, Response $response): Response
    {
        $stmt = $this->pdo->query('SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days FROM products ORDER BY hebrew_name');
        $products = $stmt->fetchAll();
        return $this->html($response, Template::render('pages/market_list', ['products' => $products]));
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $stmt = $this->pdo->prepare('SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days, payload_json FROM products WHERE slug = ? LIMIT 1');
        $stmt->execute([$slug]);
        $product = $stmt->fetch();

        if (!$product) {
            return $this->html($response, Template::render('error', ['code' => 404, 'message' => 'מוצר לא נמצא']), 404);
        }

        $history = $this->fetchHistory((int)$product['id'], 28);

        return $this->html($response, Template::render('pages/market_product', [
            'product' => $product,
            'history' => $history,
        ]));
    }

    public function productHistoryApi(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $days = max(1, min(365, (int)($request->getQueryParams()['days'] ?? 28)));

        $stmt = $this->pdo->prepare('SELECT id FROM products WHERE slug = ? LIMIT 1');
        $stmt->execute([$slug]);
        $product = $stmt->fetch();
        if (!$product) {
            $response->getBody()->write(json_encode([], JSON_UNESCAPED_UNICODE));
            return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
        }

        $history = $this->fetchHistory((int)$product['id'], $days);
        $response->getBody()->write(json_encode($history, JSON_UNESCAPED_UNICODE));
        return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
    }

    private function fetchHistory(int $productId, int $days): array
    {
        $driver = (string)$this->pdo->getAttribute(PDO::ATTR_DRIVER_NAME);
        $sql = $driver === 'sqlite'
            ? 'SELECT price_date, price, source FROM product_prices WHERE product_id = ? ORDER BY price_date DESC LIMIT ?'
            : 'SELECT price_date, price, source FROM product_prices WHERE product_id = ? AND price_date >= (CURRENT_DATE - INTERVAL ? DAY) ORDER BY price_date DESC';

        $stmt = $this->pdo->prepare($sql);
        if ($driver === 'sqlite') {
            $stmt->bindValue(1, $productId, PDO::PARAM_INT);
            $stmt->bindValue(2, $days, PDO::PARAM_INT);
            $stmt->execute();
        } else {
            $stmt->execute([$productId, $days]);
        }

        return $stmt->fetchAll();
    }

    private function html(Response $response, string $body, int $status = 200): Response
    {
        $response->getBody()->write($body);
        return $response->withStatus($status)->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
