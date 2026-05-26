<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class CropBookViewController
{
    public function __construct(private PDO $pdo)
    {
    }

    public function entry(Request $request, Response $response): Response
    {
        return $this->html($response, Template::render('pages/book_entry'));
    }

    public function questions(Request $request, Response $response): Response
    {
        $questions = [
            ['title' => 'מה מתאים לקיץ?', 'category' => 'summer'],
            ['title' => 'מה זורעים לחורף?', 'category' => 'winter'],
            ['title' => 'מה גדל מהר?', 'category' => 'fast'],
            ['title' => 'מה מתאים למתחילים?', 'category' => 'beginner'],
            ['title' => 'מה מתאים לשטח קטן?', 'category' => 'small-space'],
        ];
        return $this->html($response, Template::render('pages/book_questions', ['questions' => $questions]));
    }

    public function family(Request $request, Response $response): Response
    {
        $rows = $this->pdo->query('SELECT COALESCE(family_name_he, "לא ידוע") AS family_name_he, COUNT(*) AS total FROM crops GROUP BY family_name_he ORDER BY total DESC, family_name_he')->fetchAll();
        return $this->html($response, Template::render('pages/book_family', ['families' => $rows]));
    }

    public function tableView(Request $request, Response $response): Response
    {
        $category = trim((string)($request->getQueryParams()['category'] ?? ''));
        $sql = 'SELECT id, slug, hebrew_name, scientific_name, family_name_he, category, season, dtm_min, dtm_max FROM crops';
        $params = [];
        if ($category !== '') {
            $sql .= ' WHERE category = ?';
            $params[] = $category;
        }
        $sql .= ' ORDER BY hebrew_name';

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);

        return $this->html($response, Template::render('pages/book_table', [
            'crops' => $stmt->fetchAll(),
            'category' => $category,
        ]));
    }

    public function search(Request $request, Response $response): Response
    {
        $q = trim((string)($request->getQueryParams()['q'] ?? ''));
        $items = [];
        if ($q !== '') {
            $stmt = $this->pdo->prepare('SELECT slug, hebrew_name, scientific_name, category FROM crops WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 30');
            $stmt->execute(['%' . $q . '%']);
            $items = $stmt->fetchAll();
        }

        return $this->html($response, Template::render('pages/book_search', [
            'q' => $q,
            'items' => $items,
        ]));
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');

        $stmt = $this->pdo->prepare('SELECT id, slug, hebrew_name, scientific_name, family_name_he, category, season, dtm_min, dtm_max, payload_json FROM crops WHERE slug = ? LIMIT 1');
        $stmt->execute([$slug]);
        $crop = $stmt->fetch();
        if (!$crop) {
            return $this->html($response, Template::render('error', ['code' => 404, 'message' => 'גידול לא נמצא']), 404);
        }

        $payload = json_decode((string)($crop['payload_json'] ?? '{}'), true);
        if (is_array($payload)) {
            $crop = array_merge($crop, $payload);
        }
        unset($crop['payload_json']);

        $varStmt = $this->pdo->prepare('SELECT id, name, payload_json FROM crop_varieties WHERE crop_id = ? ORDER BY name');
        $varStmt->execute([$crop['id']]);
        $varieties = $varStmt->fetchAll();

        foreach ($varieties as &$variety) {
            $vPayload = json_decode((string)($variety['payload_json'] ?? '{}'), true);
            if (is_array($vPayload)) {
                $variety = array_merge($variety, $vPayload);
            }
            $variety['slug'] = self::slugify((string)$variety['name']);
            unset($variety['payload_json']);
        }

        return $this->html($response, Template::render('pages/book_crop', [
            'crop' => $crop,
            'varieties' => $varieties,
        ]));
    }

    public function variety(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $vslug = (string)($args['vslug'] ?? '');

        $stmt = $this->pdo->prepare('SELECT id, slug, hebrew_name, scientific_name FROM crops WHERE slug = ? LIMIT 1');
        $stmt->execute([$slug]);
        $crop = $stmt->fetch();
        if (!$crop) {
            return $this->html($response, Template::render('error', ['code' => 404, 'message' => 'גידול לא נמצא']), 404);
        }

        $varStmt = $this->pdo->prepare('SELECT id, name, payload_json FROM crop_varieties WHERE crop_id = ? ORDER BY name');
        $varStmt->execute([$crop['id']]);
        $variety = null;
        foreach ($varStmt->fetchAll() as $row) {
            if (self::slugify((string)$row['name']) === $vslug) {
                $payload = json_decode((string)($row['payload_json'] ?? '{}'), true);
                $variety = array_merge($row, is_array($payload) ? $payload : []);
                unset($variety['payload_json']);
                break;
            }
        }

        if (!$variety) {
            return $this->html($response, Template::render('error', ['code' => 404, 'message' => 'זן לא נמצא']), 404);
        }

        return $this->html($response, Template::render('pages/book_variety', [
            'crop' => $crop,
            'variety' => $variety,
        ]));
    }

    private function html(Response $response, string $body, int $status = 200): Response
    {
        $response->getBody()->write($body);
        return $response->withStatus($status)->withHeader('Content-Type', 'text/html; charset=utf-8');
    }

    private static function slugify(string $name): string
    {
        $slug = strtolower(trim($name));
        $slug = preg_replace('/[^a-z0-9\s-]/', '', $slug) ?? '';
        $slug = preg_replace('/\s+/', '-', $slug) ?? '';
        return trim($slug, '-') ?: 'variety';
    }
}
