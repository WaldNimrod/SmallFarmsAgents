<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Controllers\AssumptionsController;
use SFA\Lib\FieldRegistry;
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
        // WP-CB-1-patch01: server-side filtering. Column-backed filters run in SQL;
        // payload-backed filters (planting_method, frost) run as a PHP post-filter
        // because the MySQL mirror stores them in payload_json, not as columns.
        $qp        = $request->getQueryParams();
        $q         = trim((string)($qp['q']      ?? ''));   // free-text (hebrew_name / scientific_name)
        $family    = trim((string)($qp['family'] ?? ''));   // family_name_he exact
        $season    = trim((string)($qp['season'] ?? ''));   // season LIKE
        $dtmMax    = (string)($qp['dtm_max'] ?? '') !== '' ? (int)$qp['dtm_max'] : null; // DTM ≤ N
        $sow       = trim((string)($qp['sow']    ?? ''));   // planting_method (payload)
        $frost     = trim((string)($qp['frost']  ?? ''));   // frost_tolerance_class (payload)

        $sql    = 'SELECT slug, hebrew_name, scientific_name, family_name_he, category, season, dtm_min, dtm_max, payload_json FROM crops';
        $where  = [];
        $params = [];
        if ($q !== '')      { $where[] = '(hebrew_name LIKE ? OR scientific_name LIKE ?)'; $params[] = "%$q%"; $params[] = "%$q%"; }
        if ($family !== '') { $where[] = 'family_name_he = ?'; $params[] = $family; }
        if ($season !== '') { $where[] = 'season LIKE ?';      $params[] = "%$season%"; }
        if ($dtmMax !== null) { $where[] = '(dtm_max IS NULL OR dtm_max <= ?)'; $params[] = $dtmMax; }
        if ($where) { $sql .= ' WHERE ' . implode(' AND ', $where); }
        $sql .= ' ORDER BY hebrew_name';

        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll() ?: [];

        $crops = [];
        foreach ($rows as $row) {
            $slug    = (string)($row['slug'] ?? '');
            $payload = json_decode((string)($row['payload_json'] ?? '{}'), true);
            $payload = is_array($payload) ? $payload : [];

            // Payload-backed filters (post-fetch): planting_method + frost_tolerance_class.
            if ($sow !== '') {
                $pm = (string)($payload['planting_method'] ?? ($payload['agronomy']['planting_method'] ?? ''));
                if ($pm !== $sow) { continue; }
            }
            if ($frost !== '') {
                $ft = (string)($payload['frost_tolerance_class'] ?? ($payload['agronomy']['frost_tolerance_class'] ?? ''));
                if ($ft !== $frost) { continue; }
            }

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

        // WP-CB-1: pass view param (cards|table) and total count
        $view = trim((string)($qp['view'] ?? 'cards'));
        if (!in_array($view, ['cards', 'table'], true)) $view = 'cards';

        // Distinct family list for the filter dropdown (column-backed, cheap).
        $famRows = $this->pdo->query("SELECT DISTINCT family_name_he FROM crops WHERE family_name_he IS NOT NULL AND family_name_he <> '' ORDER BY family_name_he");
        $families = $famRows ? array_column($famRows->fetchAll(), 'family_name_he') : [];

        return $this->html($response, Template::render('pages/book_entry', [
            'crops'    => $crops,
            'view'     => $view,
            'total'    => count($crops),
            'families' => $families,
            'filters'  => [
                'q'      => $q,
                'family' => $family,
                'season' => $season,
                'dtm_max'=> $dtmMax,
                'sow'    => $sow,
                'frost'  => $frost,
            ],
        ]));
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
    /** WP-CB-1-patch01: watercolor art mapping (crop slug -> wc-*.png). Only slugs with a real served PNG; others fall back to the icon sprite. */
    private const WC_ART = [
        'basil' => 'wc-basil.png',
        'beet' => 'wc-beet.png',
        'broccoli' => 'wc-broccoli.png',
        'bush-bean' => 'wc-bush-bean.png',
        'cabbage' => 'wc-cabbage.png',
        'carrot' => 'wc-carrot.png',
        'chard' => 'wc-chard.png',
        'cucumber' => 'wc-cucumber.png',
        'dill' => 'wc-dill.png',
        'eggplant' => 'wc-eggplant.png',
        'fennel' => 'wc-fennel.png',
        'garlic' => 'wc-garlic.png',
        'ginger' => 'wc-ginger.png',
        'kale' => 'wc-kale.png',
        'leek' => 'wc-leek.png',
        'lettuce' => 'wc-lettuce.png',
        'melon' => 'wc-melon.png',
        'onion' => 'wc-onion.png',
        'parsley' => 'wc-parsley.png',
        'pea' => 'wc-pea.png',
        'pepper' => 'wc-pepper.png',
        'pole-bean' => 'wc-pole-bean.png',
        'radish' => 'wc-radish.png',
        'scallion' => 'wc-scallion.png',
        'spinach' => 'wc-spinach.png',
        'tomato' => 'wc-tomato.png',
        'turmeric' => 'wc-turmeric.png',
        'zucchini' => 'wc-zucchini.png',
    ];

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
                    $defaultValue = $defaultAgronomy[$field] ?? null;
                    // Numeric compare (cast both): avoids spurious int-vs-float
                    // deltas, e.g. 45 (int) !== 45.0 (computed median) in strict PHP.
                    $agro_delta[$field] = ($defaultValue !== null
                        && abs((float)$value - (float)$defaultValue) > 1e-9);
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

        // ── WP-UI-patch04: map payload sections (§3.4) ──────────────────
        // Each section is already merged into $crop from payload_json above.
        // Ensure canonical keys exist as arrays so template can test with !empty().

        // (a) identity — scalar fields from crops table + family sub-object
        if (!isset($crop['identity']) || !is_array($crop['identity'])) {
            $identityFamily = [];
            if (!empty($crop['family']) && is_array($crop['family'])) {
                $identityFamily = [
                    'name_he'       => (string)($crop['family']['name_he'] ?? ''),
                    'scientific_name' => (string)($crop['name_lat'] ?? ''),
                ];
            }
            $crop['identity'] = array_filter([
                'category'             => (string)($crop['category']             ?? ''),
                'growth_cycle'         => (string)($crop['growth_cycle']         ?? ''),
                'harvest_unit_default' => (string)($crop['harvest_unit_default'] ?? ''),
                'first_fruit_year'     => $crop['first_fruit_year'] ?? null,
                'description'          => (string)($crop['description_he']       ?? ($crop['description'] ?? '')),
                'dtm_min'              => $crop['dtm_min'] ?? null,
                'dtm_max'              => $crop['dtm_max'] ?? null,
                'family'               => $identityFamily ?: null,
            ], static fn ($v) => $v !== null && $v !== '' && $v !== []);
        }

        // (b) calendar — already an array or empty; normalise.
        if (!isset($crop['calendar']) || !is_array($crop['calendar'])) {
            $crop['calendar'] = [];
        }

        // (c) agronomy — crop-level rollup; already merged or empty.
        if (!isset($crop['agronomy']) || !is_array($crop['agronomy'])) {
            $crop['agronomy'] = [];
        }

        // (d) harvest — list; already merged or empty.
        if (!isset($crop['harvest']) || !is_array($crop['harvest'])) {
            $crop['harvest'] = [];
        }

        // (e) storage — object; already merged or empty.
        if (!isset($crop['storage']) || !is_array($crop['storage'])) {
            $crop['storage'] = [];
        }

        // (f) companions — list; already merged or empty.
        if (!isset($crop['companions']) || !is_array($crop['companions'])) {
            $crop['companions'] = [];
        }

        // (g) notes — public-only list.  payload key is 'notes'.
        // knowledge_notes (legacy) is handled by template's own filter loop.
        if (!isset($crop['notes']) || !is_array($crop['notes'])) {
            $crop['notes'] = [];
        }
        // Hard-gate: strip any inadvertent internal note that somehow made it in.
        $crop['notes'] = array_values(array_filter(
            $crop['notes'],
            static fn ($n) => is_array($n) && empty($n['is_internal_farm_use_only'])
        ));

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

        // ── WP-CB-1: depth param + enrichment + assumptions ──────────
        $depth = trim((string)($request->getQueryParams()['depth'] ?? 'simple'));
        if (!in_array($depth, ['simple', 'full', 'drill'], true)) {
            $depth = 'simple';
        }

        // Read crop_field_enrichment rows (if table exists — tolerates absence).
        $enrichment = [];
        try {
            $enStmt = $this->pdo->prepare(
                'SELECT field_name, value_best, unit, field_state, winning_source_class, confidence_score
                 FROM crop_field_enrichment WHERE crop_id = ?'
            );
            $enStmt->execute([$crop['id']]);
            foreach ($enStmt->fetchAll() as $row) {
                $enrichment[(string)$row['field_name']] = $row;
            }
        } catch (\Throwable) {
            $enrichment = []; // table not yet migrated
        }

        // Read crop_attribute rows (if table exists).
        $attributes = [];
        try {
            $atStmt = $this->pdo->prepare(
                'SELECT attribute_key, value_canonical, value_list
                 FROM crop_attribute WHERE crop_id = ?'
            );
            $atStmt->execute([$crop['id']]);
            foreach ($atStmt->fetchAll() as $row) {
                $attributes[(string)$row['attribute_key']] = $row;
            }
        } catch (\Throwable) {
            $attributes = [];
        }

        // F-UI-01: the MySQL mirror has no crop_field_enrichment / crop_attribute tables;
        // the ingest instead delivers per-field value + field_state inside the DEFAULT
        // variety payload (agronomy{} + field_state{}). Pass it as a fallback so prov
        // cues + calculators light up from the payload the ingest already ships.
        $defaultPayload = is_array($defaultVariety ?? null) ? $defaultVariety : [];
        $cb1_fields = self::buildCb1Fields($enrichment, $attributes, $crop, $defaultPayload);

        // Determine crop state: COMPLETE iff all MANDATORY fields are VALIDATED.
        $mandatory_fields = [
            'days_to_maturity', 'harvest_window_max_days', 'spacing_in_row_cm', 'rows_per_bed',
            'seeds_per_g', 'yield_per_bed_m', 'price_documented', 'sowing_months',
            'planting_method', 'frost_tolerance_class', 'days_in_nursery',
            'succession_interval_weeks', 'nutrient_removal_n_kg_per_ha',
        ];
        $is_complete = true;
        foreach ($mandatory_fields as $mf) {
            $state = strtoupper((string)($cb1_fields[$mf]['field_state'] ?? 'MISSING'));
            if ($state !== 'VALIDATED') { $is_complete = false; break; }
        }

        // Watercolor art for this crop
        $wc_art = self::WC_ART[$slug] ?? null;

        // Family for rotation hint
        $family_name_he = (string)($crop['family_tag_he'] ?? ($crop['family_name_he'] ?? ''));

        return $this->html($response, Template::render('pages/book_crop', [
            'crop'             => $crop,
            'varieties'        => $varieties,
            // WP-CB-1 additions
            'depth'            => $depth,
            'cb1_fields'       => $cb1_fields,
            'attributes'       => $attributes,
            'enrichment'       => $enrichment,
            'is_complete'      => $is_complete,
            'wc_art'           => $wc_art,
            'family_name_he'   => $family_name_he,
            'assumptions'      => AssumptionsController::getAssumptions(),
        ]));
    }

    public function coverCrops(Request $request, Response $response): Response
    {
        // Query the cover_crops table populated by sub-agent A.
        // Tolerate the table not yet existing (returns empty list gracefully).
        $rows = [];
        try {
            $stmt = $this->pdo->query(
                'SELECT name_he, name_en, category, sow_window, total_days_garden,
                        survives_winter, notes
                 FROM cover_crops ORDER BY category, name_he'
            );
            if ($stmt) {
                $rows = $stmt->fetchAll();
            }
        } catch (\Throwable $e) {
            // Table may not exist yet — render empty-state without fatal.
            $rows = [];
        }

        $cover_crops = [];
        foreach ($rows as $row) {
            $cover_crops[] = [
                'name_he'           => (string)($row['name_he'] ?? ''),
                'name_en'           => (string)($row['name_en'] ?? ''),
                'category'          => (string)($row['category'] ?? ''),
                'sow_window'        => (string)($row['sow_window'] ?? ''),
                'total_days_garden' => $row['total_days_garden'] !== null ? (int)$row['total_days_garden'] : null,
                'survives_winter'   => !empty($row['survives_winter']),
                'notes'             => (string)($row['notes'] ?? ''),
            ];
        }

        return $this->html($response, Template::render('pages/book_cover_crops', [
            'cover_crops' => $cover_crops,
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

    /**
     * Build the unified CB1 field array, resolving all names through FIM §1.
     * Returns [canonical_name => {value_best, unit, field_state, winning_source_class, confidence_score, field_name}]
     *
     * @param array<string,array<string,mixed>> $enrichment  crop_field_enrichment rows
     * @param array<string,array<string,mixed>> $attributes  crop_attribute rows
     * @param array<string,mixed>               $crop        crop row (for identity columns)
     * @return array<string,array<string,mixed>>
     */
    private static function buildCb1Fields(array $enrichment, array $attributes, array $crop, array $variety = []): array
    {
        $out = [];

        // F-UI-01 fallback: per-field value + state from the default variety payload
        // (the ingest ships these even when the enrichment tables are absent in the mirror).
        $vAgro  = is_array($variety['agronomy'] ?? null)    ? $variety['agronomy']    : [];
        $vState = is_array($variety['field_state'] ?? null) ? $variety['field_state'] : [];

        // EN fields — read via FieldRegistry::read (canonical → old → alias siblings)
        $en_fields = [
            'days_to_maturity', 'harvest_window_max_days', 'spacing_in_row_cm',
            'rows_per_bed', 'seeds_per_g', 'yield_per_bed_m', 'price_documented',
            'days_in_nursery', 'succession_interval_weeks', 'nutrient_removal_n_kg_per_ha',
            'harvest_window_min_days',
        ];
        foreach ($en_fields as $field) {
            // Try canonical key first, then aliases
            $row = null;
            $canonical = FieldRegistry::resolve($field);
            if (isset($enrichment[$canonical])) {
                $row = $enrichment[$canonical];
            } else {
                // Try alias siblings
                $val = FieldRegistry::read($enrichment, $field);
                if ($val !== null) {
                    // Find which stored key matched
                    foreach ($enrichment as $k => $r) {
                        if ((string)($r['value_best'] ?? '') === (string)$val) {
                            $row = $r; break;
                        }
                    }
                }
            }
            if ($row === null) {
                // Fallback to the default-variety payload (F-UI-01).
                $pv = FieldRegistry::read($vAgro, $field);
                if ($pv !== null) {
                    // field_state keyed by canonical or alias in the payload.
                    $st = (string)($vState[$canonical] ?? $vState[$field] ?? '');
                    $out[$canonical] = [
                        'value_best'           => $pv,
                        'unit'                 => '',
                        'field_state'          => $st !== '' ? strtoupper($st) : 'UNKNOWN',
                        'winning_source_class' => '',
                        'confidence_score'     => null,
                        'field_name'           => $canonical,
                    ];
                    continue;
                }
                $out[$canonical] = [
                    'value_best' => null, 'unit' => '', 'field_state' => 'MISSING',
                    'winning_source_class' => '', 'confidence_score' => null, 'field_name' => $canonical,
                ];
            } else {
                $out[$canonical] = array_merge($row, ['field_name' => $canonical]);
            }
        }

        // AT fields — from crop_attribute
        $at_map = [
            'sowing_months'         => 'value_list',
            'transplant_months'     => 'value_list',
            'planting_method'       => 'value_canonical',
            'frost_tolerance_class' => 'value_canonical',
        ];
        foreach ($at_map as $atKey => $col) {
            $row = $attributes[$atKey] ?? null;
            if ($row === null) {
                // F-UI-01 fallback: categorical value from the variety payload (agronomy or field_state).
                $pv = FieldRegistry::read($vAgro, $atKey);
                if ($pv !== null && $pv !== '' && $pv !== []) {
                    $st = (string)($vState[$atKey] ?? '');
                    $out[$atKey] = [
                        'value_best'           => $pv,
                        'unit'                 => '',
                        'field_state'          => $st !== '' ? strtoupper($st) : 'UNKNOWN',
                        'winning_source_class' => '',
                        'confidence_score'     => null,
                        'field_name'           => $atKey,
                    ];
                    continue;
                }
                $out[$atKey] = ['value_best' => null, 'field_state' => 'MISSING', 'field_name' => $atKey, 'unit' => ''];
            } else {
                $val = $col === 'value_list'
                    ? json_decode((string)($row[$col] ?? '[]'), true)
                    : (string)($row[$col] ?? '');
                $out[$atKey] = [
                    'value_best'          => $val,
                    'unit'                => '',
                    'field_state'         => ($val !== null && $val !== '' && $val !== []) ? 'VALIDATED' : 'MISSING',
                    'winning_source_class' => 'NI',
                    'confidence_score'    => 1.0,
                    'field_name'          => $atKey,
                ];
            }
        }

        // Proposed fields — always MISSING until WP-CB-MIG2
        foreach (['needs_summer_shade', 'irrigation_type', 'root_depth_class', 'unit_size'] as $proposed) {
            $out[$proposed] = ['value_best' => null, 'field_state' => 'PROPOSED', 'field_name' => $proposed, 'unit' => ''];
        }

        // Identity fields from crops row
        if (!empty($crop['dtm_days'])) {
            $dtm = (int)$crop['dtm_days'];
            if (!isset($out['days_to_maturity']) || ($out['days_to_maturity']['value_best'] ?? null) === null) {
                $out['days_to_maturity'] = [
                    'value_best' => $dtm, 'unit' => 'ימים', 'field_state' => 'UNVALIDATED',
                    'winning_source_class' => 'PR', 'confidence_score' => 0.3, 'field_name' => 'days_to_maturity',
                ];
            }
        }

        return $out;
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
