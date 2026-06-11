<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\CropArt;
use SFA\Lib\FieldRegistry;
use SFA\Lib\Template;

final class MarketViewController
{
    /**
     * Hebrew month names for updated_he formatting.
     * Key = month number (1-12), value = Hebrew month name.
     */
    private const HE_MONTHS = [
        1 => 'ינואר', 2 => 'פברואר', 3 => 'מרץ', 4 => 'אפריל',
        5 => 'מאי', 6 => 'יוני', 7 => 'יולי', 8 => 'אוגוסט',
        9 => 'ספטמבר', 10 => 'אוקטובר', 11 => 'נובמבר', 12 => 'דצמבר',
    ];

    /**
     * Icon slug mapping for known product categories / slugs.
     * Falls back to 'leaf' for unknown products (renders icon-leaf sprite).
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

    public function index(Request $request, Response $response): Response
    {
        $stmt = $this->pdo->query('SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days FROM products ORDER BY hebrew_name');
        $rows = $stmt->fetchAll();

        // Compute per-product aggregates (min/median/max/source_count/observation_count)
        // from product_prices in a single query to avoid N+1.
        $aggregates = $this->fetchAggregatesAll();

        // WP-CB-UI-REDESIGN (WI-5): per-product 28-point price series → sparkline +
        // trend% (the mockup's drill-down graph). One query, merged into aggregates.
        foreach ($this->fetchSeriesAll() as $pid => $s) {
            $aggregates[$pid] = array_merge($aggregates[$pid] ?? [], $s);
        }

        $products = [];
        foreach ($rows as $row) {
            $products[] = $this->mapProductRow($row, $aggregates[(int)$row['id']] ?? null);
        }

        return $this->html($response, Template::render('pages/market_list', [
            'products'   => $products,
            'categories' => $this->fetchCategories(),
        ]));
    }

    public function detail(Request $request, Response $response, array $args): Response
    {
        $slug = (string)($args['slug'] ?? '');
        $stmt = $this->pdo->prepare('SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days, payload_json FROM products WHERE slug = ? LIMIT 1');
        $stmt->execute([$slug]);
        $row = $stmt->fetch();

        if (!$row) {
            return $this->html($response, Template::render('error', ['code' => 404, 'message' => 'מוצר לא נמצא']), 404);
        }

        $history = $this->fetchHistory((int)$row['id'], 28);
        $agg     = $this->aggregateFromHistory($history);

        $product = $this->mapProductRow($row, $agg);

        // Resolve crop slug: look up crops whose payload_json.oma_product_id matches
        // this product's code or slug so the cross-link goes to the right /crop-book/{slug}.
        $product['book_slug']     = $this->resolveCropSlug($row);
        $product['book_label_he'] = (string)($row['hebrew_name'] ?? '');

        // Expose 28-day history under both shape conventions for template defensiveness.
        $product['history'] = $this->mapHistoryRows($history);

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

    /**
     * Resolve the correct crop slug for a product row (AC-U4-07 cross-link fix).
     *
     * Strategy (in order):
     *   1. Look up crops whose payload_json.oma_product_id equals this product's
     *      payload_json.code (the canonical OMA product code).
     *   2. Fall back to matching crops.slug = product.slug (same-slug assumption
     *      that was used before — still valid when slugs were aligned).
     *   3. If neither matches, return '' so the template omits the cross-link
     *      rather than emitting a 404 URL.
     *
     * @param array<string,mixed> $productRow Raw DB row including payload_json.
     */
    private function resolveCropSlug(array $productRow): string
    {
        // Extract the OMA product code from the product's payload_json.
        $payload = json_decode((string)($productRow['payload_json'] ?? '{}'), true);
        $code    = is_array($payload) ? (string)($payload['code'] ?? '') : '';
        $prodSlug = (string)($productRow['slug'] ?? '');

        // 1. Match via oma_product_id in crops.payload_json.
        if ($code !== '') {
            try {
                $driver = (string)$this->pdo->getAttribute(\PDO::ATTR_DRIVER_NAME);
                // MySQL supports JSON_EXTRACT; SQLite uses json_extract (same syntax).
                $stmt = $this->pdo->prepare(
                    "SELECT slug FROM crops WHERE JSON_EXTRACT(payload_json, '$.oma_product_id') = ? LIMIT 1"
                );
                $stmt->execute([$code]);
                $row = $stmt->fetch();
                if ($row && (string)($row['slug'] ?? '') !== '') {
                    return (string)$row['slug'];
                }
            } catch (\Throwable $e) {
                // json_extract may not be available in all SQLite builds; fall through.
            }
        }

        // 2. Direct slug match (e.g., product slug 'tomato' aligns with crop slug 'tomato').
        if ($prodSlug !== '') {
            try {
                $stmt = $this->pdo->prepare('SELECT slug FROM crops WHERE slug = ? LIMIT 1');
                $stmt->execute([$prodSlug]);
                $row = $stmt->fetch();
                if ($row && (string)($row['slug'] ?? '') !== '') {
                    return (string)$row['slug'];
                }
            } catch (\Throwable $e) {
                // Ignore — crop table may be missing in test fixture.
            }
        }

        // 3. Match by Hebrew name (product canonical_name_he ↔ crops.hebrew_name) —
        // the only reliable linkage today (crops.oma_product_id is unpopulated).
        $hebrewName = (string)($productRow['hebrew_name'] ?? '');
        if ($hebrewName !== '') {
            try {
                $stmt = $this->pdo->prepare('SELECT slug FROM crops WHERE hebrew_name = ? LIMIT 1');
                $stmt->execute([$hebrewName]);
                $row = $stmt->fetch();
                if ($row && (string)($row['slug'] ?? '') !== '') {
                    return (string)$row['slug'];
                }
            } catch (\Throwable $e) {
                // Ignore — crop table may be missing in test fixture.
            }
        }

        // 4. No match — suppress cross-link to avoid 404.
        return '';
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

    /**
     * Map a DB row (legacy keys: hebrew_name/last_price/...) onto the canonical
     * template shape (name_he/price_current/...). Preserves legacy keys for
     * backward-compatibility with any code that still reads them.
     *
     * @param array<string,mixed>      $row Raw DB row (must include id, slug, hebrew_name, last_price, last_price_date).
     * @param array<string,mixed>|null $agg Aggregate row {min, median, max, source_count, observation_count} or null.
     * @return array<string,mixed> Merged product array with both legacy + canonical keys.
     */
    private function mapProductRow(array $row, ?array $agg): array
    {
        $slug         = (string)($row['slug'] ?? '');
        $hebrewName   = (string)($row['hebrew_name'] ?? '');
        $lastPrice    = isset($row['last_price']) && $row['last_price'] !== null ? (float)$row['last_price'] : null;
        $category     = (string)($row['category'] ?? '');

        $iconSlug = self::ICON_MAP[$slug] ?? self::ICON_MAP[$category] ?? 'leaf';

        $priceMin    = $agg !== null && isset($agg['min'])    ? (float)$agg['min']    : ($lastPrice ?? 0.0);
        $priceMax    = $agg !== null && isset($agg['max'])    ? (float)$agg['max']    : ($lastPrice ?? 0.0);
        $priceMedian = $agg !== null && isset($agg['median']) ? (float)$agg['median'] : ($lastPrice ?? 0.0);
        $sourceCount = $agg !== null ? (int)($agg['source_count']      ?? 0) : 0;
        $obsCount    = $agg !== null ? (int)($agg['observation_count'] ?? 0) : 0;

        $product = $row;
        // Canonical (template-side) keys
        $product['name_he']           = $hebrewName;
        $product['en_name']           = (string)($row['en_name'] ?? '');
        $product['unit_he']           = (string)($row['unit'] ?? '');
        $product['glyph_letter']      = $hebrewName !== '' ? mb_substr($hebrewName, 0, 1, 'UTF-8') : '';
        $product['price_current']     = $lastPrice ?? 0.0;
        $product['currency']          = '₪';
        $product['price_median']      = $priceMedian;
        $product['price_min']         = $priceMin;
        $product['price_max']         = $priceMax;
        $product['source_count']      = $sourceCount;
        $product['observation_count'] = $obsCount;
        $product['icon_slug']         = $iconSlug;
        // WP-CB-UI-MOCKUP-FIDELITY: watercolor thumbnail (same art as the crop
        // book) — '' when unmapped so the .pc__art line-glyph icon is the fallback.
        $product['wc_art']            = CropArt::file($slug) ?? '';
        $product['book_slug']         = $this->resolveCropSlug($row); // resolved crop slug ('' when none — no 404)
        $product['book_label_he']     = $hebrewName;
        $product['updated_he']        = $this->formatHebrewDate((string)($row['last_price_date'] ?? ''));
        // WI-5: 28-day sparkline + week-over-week trend (empty/flat when no history).
        $product['spark']             = $agg['spark']     ?? [];
        $product['trend_pct']         = $agg['trend_pct'] ?? 0.0;
        $product['trend_dir']         = (string)($agg['trend_dir'] ?? 'flat');

        return $product;
    }

    /**
     * Normalize history rows to expose both `date_he`/`source_count` and the legacy
     * `price_date`/`source` shape for template iteration.
     *
     * @param array<int,array<string,mixed>> $history
     * @return array<int,array<string,mixed>>
     */
    private function mapHistoryRows(array $history): array
    {
        $out = [];
        foreach ($history as $hr) {
            $out[] = array_merge($hr, [
                'date_he' => $this->formatHebrewDate((string)($hr['price_date'] ?? '')),
                'price'   => (float)($hr['price'] ?? 0),
            ]);
        }
        return $out;
    }

    /**
     * Compute aggregates for ALL products in a single query.
     *
     * @return array<int,array{min:float,max:float,median:float,source_count:int,observation_count:int}>
     */
    private function fetchAggregatesAll(): array
    {
        $out = [];
        try {
            $stmt = $this->pdo->query(
                'SELECT product_id, MIN(price) AS pmin, MAX(price) AS pmax,
                        COUNT(*) AS obs_count, COUNT(DISTINCT source) AS src_count
                 FROM product_prices
                 GROUP BY product_id'
            );
            if ($stmt === false) {
                return [];
            }
            foreach ($stmt->fetchAll() as $r) {
                $pid = (int)($r['product_id'] ?? 0);
                if ($pid <= 0) continue;
                // Median requires a second pass (cheap for typical product sizes)
                $median = $this->fetchMedian($pid);
                $out[$pid] = [
                    'min'               => (float)($r['pmin'] ?? 0),
                    'max'               => (float)($r['pmax'] ?? 0),
                    'median'            => $median,
                    'source_count'      => (int)($r['src_count'] ?? 0),
                    'observation_count' => (int)($r['obs_count'] ?? 0),
                ];
            }
        } catch (\Throwable $e) {
            // Aggregation is best-effort — template fallbacks handle missing keys.
            return [];
        }
        return $out;
    }

    /**
     * WP-CB-UI-REDESIGN (WI-5): per-product recent price series → normalized
     * sparkline heights (35–95%) + week-over-week trend%. One query for all
     * products; tolerates an absent product_prices table (returns empty).
     *
     * @return array<int,array{spark:int[],trend_pct:float,trend_dir:string}>
     */
    private function fetchSeriesAll(): array
    {
        $out = [];
        try {
            $stmt = $this->pdo->query(
                'SELECT product_id, price FROM product_prices ORDER BY product_id, price_date'
            );
            if ($stmt === false) {
                return [];
            }
            $byPid = [];
            foreach ($stmt->fetchAll() as $r) {
                $byPid[(int)($r['product_id'] ?? 0)][] = (float)($r['price'] ?? 0);
            }
            foreach ($byPid as $pid => $prices) {
                $series = array_slice($prices, -28); // last 28 points
                $n = count($series);
                if ($n < 2) {
                    $out[$pid] = ['spark' => array_map(static fn () => 60, $series), 'trend_pct' => 0.0, 'trend_dir' => 'flat'];
                    continue;
                }
                $min = min($series);
                $max = max($series);
                $span = ($max - $min) > 1e-9 ? ($max - $min) : 1.0;
                $spark = array_map(static fn ($p) => (int)round(35 + 60 * (($p - $min) / $span)), $series);
                $first = $series[0];
                $last  = $series[$n - 1];
                $trend = $first > 0 ? round((($last - $first) / $first) * 100, 0) : 0.0;
                $out[$pid] = [
                    'spark'     => $spark,
                    'trend_pct' => (float)$trend,
                    'trend_dir' => $trend > 0.5 ? 'up' : ($trend < -0.5 ? 'down' : 'flat'),
                ];
            }
        } catch (\Throwable) {
            return [];
        }
        return $out;
    }

    /**
     * Median of all prices for a product. Returns 0.0 when no rows exist.
     */
    private function fetchMedian(int $productId): float
    {
        $stmt = $this->pdo->prepare('SELECT price FROM product_prices WHERE product_id = ? ORDER BY price');
        $stmt->execute([$productId]);
        $prices = array_map('floatval', array_column($stmt->fetchAll(), 'price'));
        $n = count($prices);
        if ($n === 0) return 0.0;
        if ($n % 2 === 1) return $prices[(int)floor($n / 2)];
        return ($prices[$n / 2 - 1] + $prices[$n / 2]) / 2.0;
    }

    /**
     * Aggregate a freshly-fetched history array (for the detail view).
     *
     * @param array<int,array<string,mixed>> $history
     * @return array{min:float,max:float,median:float,source_count:int,observation_count:int}|null
     */
    private function aggregateFromHistory(array $history): ?array
    {
        if (empty($history)) return null;
        $prices  = array_map(static fn($r) => (float)($r['price'] ?? 0), $history);
        $sources = array_filter(array_map(static fn($r) => (string)($r['source'] ?? ''), $history), 'strlen');
        sort($prices);
        $n = count($prices);
        $median = $n === 0 ? 0.0
            : ($n % 2 === 1 ? $prices[(int)floor($n / 2)] : ($prices[$n / 2 - 1] + $prices[$n / 2]) / 2.0);
        return [
            'min'               => $prices[0] ?? 0.0,
            'max'               => $prices[$n - 1] ?? 0.0,
            'median'            => $median,
            'source_count'      => count(array_unique($sources)),
            'observation_count' => $n,
        ];
    }

    /**
     * Fetch distinct product categories for the facet chips on /market/.
     *
     * @return array<int,array{slug:string,name_he:string}>
     */
    private function fetchCategories(): array
    {
        try {
            $stmt = $this->pdo->query(
                "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category"
            );
            if ($stmt === false) return [];
            $out = [];
            foreach ($stmt->fetchAll() as $r) {
                $cat = (string)($r['category'] ?? '');
                if ($cat === '') continue;
                // WI-3 / D-3: map category slug → Hebrew via FieldRegistry::enumLabel
                $out[] = ['slug' => $cat, 'name_he' => FieldRegistry::enumLabel('category', $cat)];
            }
            return $out;
        } catch (\Throwable $e) {
            return [];
        }
    }

    /**
     * Format an ISO date (YYYY-MM-DD) to a short Hebrew label, e.g. "26 במאי".
     * Returns the input unchanged if parsing fails.
     */
    private function formatHebrewDate(string $iso): string
    {
        if ($iso === '') return '';
        $ts = strtotime($iso);
        if ($ts === false) return $iso;
        $day   = (int)date('j', $ts);
        $month = (int)date('n', $ts);
        $name  = self::HE_MONTHS[$month] ?? '';
        return $name !== '' ? sprintf('%d ב%s', $day, $name) : $iso;
    }
}
