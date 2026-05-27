<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

final class CropsController
{
    public function __construct(private PDO $pdo) {}

    public function list(Request $request, Response $response): Response
    {
        $q = $request->getQueryParams();
        $category = $q['category'] ?? null;
        $season = $q['season'] ?? null;
        $dtmMax = isset($q['dtm_max']) ? (int)$q['dtm_max'] : null;

        $sql = 'SELECT id, slug, hebrew_name, scientific_name, family_id, family_name_he,
                       category, season, dtm_min, dtm_max
                FROM crops WHERE 1=1';
        $params = [];
        if ($category !== null) { $sql .= ' AND category = ?'; $params[] = $category; }
        if ($season !== null)   { $sql .= ' AND season = ?';   $params[] = $season; }
        if ($dtmMax !== null)   { $sql .= ' AND dtm_max <= ?'; $params[] = $dtmMax; }
        $sql .= ' ORDER BY hebrew_name';

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll();

        return self::json($response, ['count' => count($rows), 'items' => $rows]);
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
        if ($crop === false) {
            return self::error($response, 404, 'crop not found');
        }

        // Merge payload_json into top-level
        if (!empty($crop['payload_json'])) {
            $payload = json_decode($crop['payload_json'], true);
            unset($crop['payload_json']);
            $crop = array_merge($crop, $payload ?? []);
        }

        // Fetch varieties
        $varStmt = $this->pdo->prepare(
            'SELECT id, name, payload_json FROM crop_varieties WHERE crop_id = ? ORDER BY name'
        );
        $varStmt->execute([$crop['id']]);
        $varieties = $varStmt->fetchAll();
        foreach ($varieties as &$v) {
            if (!empty($v['payload_json'])) {
                $p = json_decode($v['payload_json'], true);
                unset($v['payload_json']);
                if (is_array($p)) {
                    $v = array_merge($v, $p);
                }
            }
        }
        unset($v);
        $crop['varieties'] = $varieties;

        return self::json($response, $crop);
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
