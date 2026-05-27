<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

final class SearchController
{
    public function __construct(private PDO $pdo)
    {
    }

    public function globalSearch(Request $request, Response $response): Response
    {
        $q = trim((string)($request->getQueryParams()['q'] ?? ''));
        if ($q === '') {
            return $this->json($response, ['query' => '', 'crops' => [], 'products' => []]);
        }

        $like = '%' . $q . '%';

        $cropStmt = $this->pdo->prepare('SELECT slug, hebrew_name, category FROM crops WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 20');
        $cropStmt->execute([$like]);

        $productStmt = $this->pdo->prepare('SELECT slug, hebrew_name, category, unit FROM products WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 20');
        $productStmt->execute([$like]);

        return $this->json($response, [
            'query' => $q,
            'crops' => $cropStmt->fetchAll(),
            'products' => $productStmt->fetchAll(),
        ]);
    }

    private function json(Response $response, array $data): Response
    {
        $response->getBody()->write(json_encode($data, JSON_UNESCAPED_UNICODE));
        return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
