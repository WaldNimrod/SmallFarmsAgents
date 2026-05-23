<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class CropBookViewController
{
    public function __construct(private PDO $pdo) {}

    public function index(Request $request, Response $response): Response
    {
        $q = $request->getQueryParams();
        $category = $q['category'] ?? null;
        $season = $q['season'] ?? null;

        $sql = 'SELECT id, slug, hebrew_name, scientific_name, family_name_he,
                       category, season, dtm_min, dtm_max
                FROM crops WHERE 1=1';
        $params = [];
        if ($category !== null && $category !== '') { $sql .= ' AND category = ?'; $params[] = $category; }
        if ($season !== null && $season !== '')     { $sql .= ' AND season = ?';   $params[] = $season; }
        $sql .= ' ORDER BY hebrew_name';
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        $crops = $stmt->fetchAll();

        // Category facets
        $cats = $this->pdo->query(
            'SELECT category, COUNT(*) c FROM crops WHERE category IS NOT NULL GROUP BY category ORDER BY category'
        )->fetchAll();

        $html = Template::render('crop_book/list', [
            'crops' => $crops,
            'categories' => $cats,
            'current_category' => $category,
            'total' => count($crops),
        ]);
        return self::html($response, $html);
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $stmt = $this->pdo->prepare(
            'SELECT id, slug, hebrew_name, scientific_name, family_id, family_name_he,
                    category, season, dtm_min, dtm_max, last_pushed_at, payload_json
             FROM crops WHERE slug = ?'
        );
        $stmt->execute([$slug]);
        $crop = $stmt->fetch();
        if (!$crop) {
            $html = Template::render('error', ['code' => 404, 'message' => 'גידול לא נמצא']);
            return self::html($response, $html, 404);
        }

        $payload = !empty($crop['payload_json']) ? (json_decode($crop['payload_json'], true) ?: []) : [];
        $crop = array_merge($crop, $payload);
        unset($crop['payload_json']);

        $varStmt = $this->pdo->prepare(
            'SELECT id, name, payload_json FROM crop_varieties WHERE crop_id = ? ORDER BY name'
        );
        $varStmt->execute([$crop['id']]);
        $varieties = $varStmt->fetchAll();
        foreach ($varieties as &$v) {
            if (!empty($v['payload_json'])) {
                $p = json_decode($v['payload_json'], true);
                if (is_array($p)) { $v = array_merge($v, $p); }
                unset($v['payload_json']);
            }
        }
        unset($v);

        $html = Template::render('crop_book/detail', [
            'crop' => $crop, 'varieties' => $varieties,
        ]);
        return self::html($response, $html);
    }

    private static function html(Response $r, string $body, int $status = 200): Response
    {
        $r->getBody()->write($body);
        return $r->withStatus($status)->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
