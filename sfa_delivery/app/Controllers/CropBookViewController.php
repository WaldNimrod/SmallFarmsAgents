<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class CropBookViewController
{
    /**
     * Icon slug mapping (sprite id without 'icon-' prefix).
     * Used by book_crop hero + market_link art. Defaults to 'leaf' for unknown.
     */
    private const ICON_MAP = [
        'tomato'     => 'tomato',
        'lettuce'    => 'lettuce',
        'cucumber'   => 'cucumber',
        'pepper'     => 'pepper',
        'eggplant'   => 'eggplant',
        'carrot'     => 'carrot',
        'onion'      => 'onion',
        'zucchini'   => 'zucchini',
        'basil'      => 'leaf',
        'strawberry' => 'tomato',
    ];

    public function __construct(private PDO $pdo)
    {
    }

    public function entry(Request $request, Response $response): Response
    {
        // AC-U3-07: query crop list for the landing crop-card grid.
        $stmt = $this->pdo->query(
            'SELECT slug, hebrew_name, scientific_name, category, dtm_min, dtm_max, payload_json FROM crops ORDER BY hebrew_name'
        );
        $rows = $stmt ? $stmt->fetchAll() : [];

        $crops = [];
        foreach ($rows as $row) {
            $slug    = (string)($row['slug'] ?? '');
            $payload = json_decode((string)($row['payload_json'] ?? '{}'), true);
            $payload = is_array($payload) ? $payload : [];

            $dtm = isset($row['dtm_max']) && $row['dtm_max'] !== null
                ? (int)$row['dtm_max']
                : (isset($row['dtm_min']) && $row['dtm_min'] !== null ? (int)$row['dtm_min'] : null);

            $crops[] = [
                'slug'          => $slug,
                'name_he'       => (string)($row['hebrew_name'] ?? ''),
                'en_name'       => (string)($payload['name_en'] ?? ($row['scientific_name'] ?? '')),
                'icon_slug'     => self::ICON_MAP[$slug] ?? 'leaf',
                'icon_svg'      => '<svg viewBox="0 0 24 24"><use href="#icon-' . htmlspecialchars(self::ICON_MAP[$slug] ?? 'leaf', ENT_QUOTES, 'UTF-8') . '"></use></svg>',
                'icon_url'      => (string)($payload['icon_url'] ?? ''),
                'family_tag_he' => (string)($payload['family_tag_he'] ?? ''),
                'category'      => (string)($row['category'] ?? ''),
                'dtm_days'      => $dtm,
            ];
        }

        return $this->html($response, Template::render('pages/book_entry', ['crops' => $crops]));
    }

    public function questions(Request $request, Response $response): Response
    {
        // Template (book_questions.php) expects q_he/sub_he/href shape.
        $questions = [
            ['slug' => 'summer',      'q_he' => 'מה מתאים לקיץ?',     'sub_he' => 'גידולי קיץ פוריים',     'href' => '/crop-book/table?category=summer'],
            ['slug' => 'winter',      'q_he' => 'מה זורעים לחורף?',   'sub_he' => 'גידולי חורף קלים',     'href' => '/crop-book/table?category=winter'],
            ['slug' => 'fast',        'q_he' => 'מה גדל מהר?',        'sub_he' => 'DTM קצר',              'href' => '/crop-book/table?category=fast'],
            ['slug' => 'beginner',    'q_he' => 'מה מתאים למתחילים?', 'sub_he' => 'התחלה רכה',            'href' => '/crop-book/table?category=beginner'],
            ['slug' => 'small-space', 'q_he' => 'מה מתאים לשטח קטן?',  'sub_he' => 'כדים, מרפסות, מ״ר',    'href' => '/crop-book/table?category=small-space'],
        ];
        return $this->html($response, Template::render('pages/book_questions', ['questions' => $questions]));
    }

    public function family(Request $request, Response $response): Response
    {
        $rows = $this->pdo->query('SELECT COALESCE(family_name_he, "לא ידוע") AS family_name_he, COUNT(*) AS total FROM crops GROUP BY family_name_he ORDER BY total DESC, family_name_he')->fetchAll();

        $families = [];
        foreach ($rows as $r) {
            $name = (string)($r['family_name_he'] ?? '');
            $families[] = [
                'slug'       => self::slugify($name) ?: 'family',
                'name_he'    => $name,
                'name_lat'   => '',
                'crop_count' => (int)($r['total'] ?? 0),
                'total'      => (int)($r['total'] ?? 0), // back-compat alias
            ];
        }

        return $this->html($response, Template::render('pages/book_family', ['families' => $families]));
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
        $rows = $stmt->fetchAll();

        // Map legacy keys → canonical template keys (name_he/family_he/dtm_days/...).
        $crops = [];
        foreach ($rows as $row) {
            $slug = (string)($row['slug'] ?? '');
            $dtm  = isset($row['dtm_max']) ? (int)$row['dtm_max'] : (isset($row['dtm_min']) ? (int)$row['dtm_min'] : null);
            $crops[] = array_merge($row, [
                'name_he'         => (string)($row['hebrew_name'] ?? ''),
                'family_he'       => (string)($row['family_name_he'] ?? ''),
                'dtm_days'        => $dtm,
                'yield_kg_per_m2' => null,
                'best_season'     => (string)($row['season'] ?? '—'),
                'source_count'    => null,
                'icon_slug'       => self::ICON_MAP[$slug] ?? 'leaf',
            ]);
        }

        return $this->html($response, Template::render('pages/book_table', [
            'crops'    => $crops,
            'category' => $category,
        ]));
    }

    public function search(Request $request, Response $response): Response
    {
        $q = trim((string)($request->getQueryParams()['q'] ?? ''));
        $items = [];
        if ($q !== '') {
            $stmt = $this->pdo->prepare('SELECT slug, hebrew_name, scientific_name, family_name_he, category, dtm_min, dtm_max FROM crops WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 30');
            $stmt->execute(['%' . $q . '%']);
            foreach ($stmt->fetchAll() as $row) {
                $items[] = [
                    'slug'          => (string)($row['slug'] ?? ''),
                    'name_he'       => (string)($row['hebrew_name'] ?? ''),
                    'en_name'       => (string)($row['scientific_name'] ?? ''),
                    'family_tag_he' => (string)($row['family_name_he'] ?? ''),
                    'dtm_days'      => isset($row['dtm_max']) ? (int)$row['dtm_max'] : null,
                    'icon_svg'      => '',
                ];
            }
        }

        return $this->html($response, Template::render('pages/book_search', [
            'query'   => $q,
            'q'       => $q,      // back-compat alias
            'results' => $items,
            'items'   => $items,  // back-compat alias
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
            $variety['vslug']   = self::varietySlug($variety);
            $variety['slug']    = $variety['vslug']; // back-compat
            $variety['name_he'] = (string)($variety['name_he'] ?? ($variety['name'] ?? ''));
            unset($variety['payload_json']);

            // Ensure agronomy is always an array.
            if (!isset($variety['agronomy']) || !is_array($variety['agronomy'])) {
                $variety['agronomy'] = [];
            }

            // Alias days_to_maturity → dtm_days (payload key mismatch fix).
            $variety['dtm_days'] = $variety['dtm_days']
                ?? ($variety['agronomy']['days_to_maturity'] ?? null);
        }
        unset($variety);

        // Identify the default variety and build per-variety agro_delta maps.
        $defaultVariety = null;
        foreach ($varieties as $v) {
            if (!empty($v['is_default'])) {
                $defaultVariety = $v;
                break;
            }
        }
        // Fall back to the first variety if none is explicitly marked default.
        if ($defaultVariety === null && !empty($varieties)) {
            $defaultVariety = $varieties[0];
        }

        // Backfill the default variety's agronomy from the other varieties
        // (team_00 ruling 2026-05-29): the default MUST carry a value wherever any
        // variety has one — "the default becomes the datum we have". For each field
        // the default lacks, use the median of the sibling varieties that report it.
        // Render-time only: the uPress MySQL stays a faithful mirror of Postgres
        // (these computed baselines are presentation, never pushed back).
        if ($defaultVariety !== null) {
            $fieldValues = []; // field => list of numeric values across all varieties
            foreach ($varieties as $v) {
                foreach (($v['agronomy'] ?? []) as $f => $val) {
                    if ($val !== null && $val !== '') {
                        $fieldValues[$f][] = (float)$val;
                    }
                }
            }
            $median = static function (array $a) {
                sort($a);
                $n = count($a);
                if ($n === 0) {
                    return null;
                }
                $mid = intdiv($n, 2);
                return $n % 2 ? $a[$mid] : ($a[$mid - 1] + $a[$mid]) / 2.0;
            };
            $defaultSlug = $defaultVariety['vslug'];
            foreach ($varieties as &$variety) {
                if ($variety['vslug'] !== $defaultSlug) {
                    continue;
                }
                foreach ($fieldValues as $f => $vals) {
                    $cur = $variety['agronomy'][$f] ?? null;
                    if ($cur === null || $cur === '') {
                        $variety['agronomy'][$f] = $median($vals); // computed baseline
                    }
                }
                if (($variety['dtm_days'] ?? null) === null
                    && isset($variety['agronomy']['days_to_maturity'])) {
                    $variety['dtm_days'] = $variety['agronomy']['days_to_maturity'];
                }
                $defaultVariety = $variety; // refresh baseline used by the delta loop
                break;
            }
            unset($variety);
        }

        foreach ($varieties as &$variety) {
            $isDefault = ($defaultVariety !== null && $variety['vslug'] === $defaultVariety['vslug']);
            $agro_delta = [];
            if (!$isDefault && $defaultVariety !== null) {
                $agronomy        = $variety['agronomy'];
                $defaultAgronomy = $defaultVariety['agronomy'] ?? [];
                foreach ($agronomy as $field => $value) {
                    $defaultValue      = $defaultAgronomy[$field] ?? null;
                    $agro_delta[$field] = ($defaultValue !== null && $value !== $defaultValue);
                }
            } else {
                // Default variety itself: all-false deltas.
                foreach (($variety['agronomy'] ?? []) as $field => $_) {
                    $agro_delta[$field] = false;
                }
            }
            $variety['agro_delta'] = $agro_delta;
        }
        unset($variety);

        // Canonical shape for book_crop.php
        $crop['name_he']       = (string)($crop['name_he']  ?? ($crop['hebrew_name']    ?? ''));
        $crop['name_lat']      = (string)($crop['name_lat'] ?? ($crop['scientific_name'] ?? ''));
        $crop['en_name']       = (string)($crop['en_name']  ?? '');
        $crop['icon_slug']     = (string)($crop['icon_slug'] ?? (self::ICON_MAP[$slug] ?? 'leaf'));
        $crop['description_he'] = (string)($crop['description_he'] ?? '');
        $crop['family_tag_he'] = (string)($crop['family_tag_he'] ?? ($crop['family_name_he'] ?? ''));
        $crop['dtm_days']      = $crop['dtm_days'] ?? ($crop['dtm_max'] ?? ($crop['dtm_min'] ?? null));
        $crop['varieties']     = $varieties;

        // family object — template uses $crop['family']['slug'] / ['name_he']
        if (!isset($crop['family']) || !is_array($crop['family'])) {
            $famName = (string)($crop['family_name_he'] ?? '');
            if ($famName !== '') {
                $crop['family'] = ['slug' => self::slugify($famName) ?: 'family', 'name_he' => $famName];
            }
        }

        // Best-effort market_link: only attach when a matching product exists.
        $marketStmt = $this->pdo->prepare('SELECT slug, hebrew_name, last_price FROM products WHERE slug = ? LIMIT 1');
        $marketStmt->execute([$slug]);
        $marketRow = $marketStmt->fetch();
        if ($marketRow) {
            $crop['market_link'] = [
                'slug'          => (string)($marketRow['slug'] ?? $slug),
                'price_current' => (float)($marketRow['last_price'] ?? 0.0),
                'source_count'  => 0, // aggregate not joined here; template tolerates 0.
            ];
        }

        // knowledge_notes — preserve as-is from payload (template filters
        // is_internal_farm_use_only). Default to empty array when missing.
        if (!isset($crop['knowledge_notes']) || !is_array($crop['knowledge_notes'])) {
            $crop['knowledge_notes'] = [];
        }

        return $this->html($response, Template::render('pages/book_crop', [
            'crop' => $crop,
            'varieties' => $varieties, // legacy top-level for any template that reads it
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
        $crop['name_he']  = (string)($crop['hebrew_name'] ?? '');
        $crop['name_lat'] = (string)($crop['scientific_name'] ?? '');

        $varStmt = $this->pdo->prepare('SELECT id, name, payload_json FROM crop_varieties WHERE crop_id = ? ORDER BY name');
        $varStmt->execute([$crop['id']]);
        $variety = null;
        foreach ($varStmt->fetchAll() as $row) {
            if (self::varietySlug($row) === $vslug) {
                $payload = json_decode((string)($row['payload_json'] ?? '{}'), true);
                $variety = array_merge($row, is_array($payload) ? $payload : []);
                unset($variety['payload_json']);
                $variety['vslug']   = $vslug;
                $variety['name_he'] = (string)($variety['name_he'] ?? ($variety['name'] ?? ''));
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

    /**
     * Build a deterministic URL slug for a variety row.
     * Fix for F-BUILD-04: Hebrew variety names previously slugged to a
     * shared fallback 'variety' (slugify strips non-ASCII), causing all
     * varieties of a crop to collide on the same URL. Now we use the
     * numeric id as the unique deterministic component.
     * Pattern: variety-{id}  (e.g., variety-401, variety-415)
     */
    private static function varietySlug(array $variety): string
    {
        $id = (int)($variety['id'] ?? 0);
        if ($id <= 0) {
            // Shouldn't happen — id is PK in crop_varieties — but keep a
            // legacy fallback to the old ASCII-only slugifier just in case.
            return self::slugify((string)($variety['name'] ?? ''));
        }
        return 'variety-' . $id;
    }
}
