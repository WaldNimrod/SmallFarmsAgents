<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Modules;
use SFA\Lib\Template;

final class HubController
{
    /**
     * Hub DB handle is optional — when null the search page degrades to an empty
     * result set (modules/tier pages still render without DB access).
     */
    // R3 F-190-R3-01 fix: PDO required (was `?PDO $pdo = null` which made PHP-DI
    // skip injection, leaving search() with null PDO and empty result sets even
    // though /api/v1/search worked). Matches ProductsController/CropsController/
    // SearchController pattern. Bootstrap registers \PDO::class singleton.
    public function __construct(private PDO $pdo)
    {
    }

    public function home(Request $request, Response $response): Response
    {
        $html = Template::render('pages/hub_home', [
            'modules' => Modules::all()['modules'] ?? [],
            'tiers'   => Modules::all()['tiers']   ?? [],
            'contact' => Modules::all()['contact']  ?? [],
        ]);
        return self::html($response, $html);
    }

    public function tiers(Request $request, Response $response): Response
    {
        $html = Template::render('pages/hub_tiers', [
            'tiers' => Modules::all()['tiers'] ?? [],
        ]);
        return self::html($response, $html);
    }

    /**
     * Global search (route /search?q=...).
     * Passes both $query (canonical) and $q (back-compat) for B6's defensive shim.
     */
    public function search(Request $request, Response $response): Response
    {
        $q = trim((string)($request->getQueryParams()['q'] ?? ''));

        $cropResults    = [];
        $productResults = [];

        if ($q !== '' && $this->pdo !== null) {
            $like = '%' . $q . '%';

            try {
                $cs = $this->pdo->prepare(
                    'SELECT slug, hebrew_name, scientific_name, family_name_he
                     FROM crops WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 20'
                );
                $cs->execute([$like]);
                foreach ($cs->fetchAll() as $row) {
                    $cropResults[] = [
                        'slug'          => (string)($row['slug'] ?? ''),
                        'name_he'       => (string)($row['hebrew_name'] ?? ''),
                        'en_name'       => (string)($row['scientific_name'] ?? ''),
                        'family_tag_he' => (string)($row['family_name_he'] ?? ''),
                        'dtm_days'      => null,
                        'icon_svg'      => '',
                    ];
                }

                $ps = $this->pdo->prepare(
                    'SELECT slug, hebrew_name, unit, last_price
                     FROM products WHERE hebrew_name LIKE ? ORDER BY hebrew_name LIMIT 20'
                );
                $ps->execute([$like]);
                foreach ($ps->fetchAll() as $row) {
                    $name_he = (string)($row['hebrew_name'] ?? '');
                    $price   = (float)($row['last_price'] ?? 0);
                    $productResults[] = [
                        'slug'              => (string)($row['slug'] ?? ''),
                        'name_he'           => $name_he,
                        'en_name'           => '',
                        'unit_he'           => (string)($row['unit'] ?? ''),
                        'glyph_letter'      => $name_he !== '' ? mb_substr($name_he, 0, 1, 'UTF-8') : '',
                        'price_current'     => $price,
                        'currency'          => '₪',
                        'price_median'      => $price,
                        'price_min'         => $price,
                        'price_max'         => $price,
                        'source_count'      => 0,
                        'observation_count' => 0,
                    ];
                }
            } catch (\Throwable $e) {
                // Degrade gracefully — template handles empty result arrays.
            }
        }

        $html = Template::render('pages/search_results', [
            'query'           => $q,
            'q'               => $q, // back-compat alias for B6's defensive shim
            'crop_results'    => $cropResults,
            'product_results' => $productResults,
        ]);
        return self::html($response, $html);
    }

    public function calc(Request $request, Response $response): Response
    {
        // WP-CB-1: serve the new calculator dashboard; hub_calc.php is legacy backup.
        // V03 fix: pass crop list so [data-k="crop_slug"] <select> can be populated.
        $cropList = [];
        try {
            $stmt = $this->pdo->query(
                'SELECT slug, hebrew_name FROM crops ORDER BY hebrew_name'
            );
            if ($stmt) {
                foreach ($stmt->fetchAll() as $row) {
                    $cropList[] = [
                        'slug'    => (string)($row['slug']        ?? ''),
                        'name_he' => (string)($row['hebrew_name'] ?? ''),
                    ];
                }
            }
        } catch (\Throwable) {
            $cropList = []; // DB unavailable — select renders empty, calc still works manually
        }

        // V03 fix: also pass per-crop NUMERIC book values (fields used by SFA_CALC) so that crop
        // selection auto-populates the calculators. WP-CB-CALC: widened the whitelist to add the
        // DATE numeric fields the date engine (Phase B) consumes — days_to_maturity, days_in_nursery
        // (a.k.a. days_in_nursery_cell), harvest_window_max_days. (succession_interval_weeks is NOT
        // delivered — it is derived client-side as round(harvest_window_max_days/7).)
        $cropBookValues = [];
        if (!empty($cropList)) {
            try {
                $slugs       = array_column($cropList, 'slug');
                $inMarks     = implode(',', array_fill(0, count($slugs), '?'));
                $enStmt      = $this->pdo->prepare(
                    "SELECT c.slug, e.field_name, e.value_best
                     FROM crops c
                     JOIN crop_field_enrichment e ON e.crop_id = c.id
                     WHERE c.slug IN ($inMarks)
                       AND e.field_name IN (
                           'spacing_in_row_cm','in_row_spacing_cm',
                           'rows_per_bed',
                           'seeds_per_g','seeds_per_gram',
                           'yield_per_bed_m','avg_yield_per_bed_m',
                           'price_documented','documented_price',
                           'nutrient_removal_n_kg_per_ha','nutrient_removal_N',
                           'nutrient_removal_p_kg_per_ha',
                           'nutrient_removal_k_kg_per_ha',
                           'days_to_maturity',
                           'days_in_nursery','days_in_nursery_cell',
                           'harvest_window_max_days'
                       )"
                );
                $enStmt->execute($slugs);
                foreach ($enStmt->fetchAll() as $row) {
                    $cropBookValues[(string)$row['slug']][(string)$row['field_name']] = $row['value_best'];
                }
            } catch (\Throwable) {
                // crop_field_enrichment may not exist on MySQL mirror yet — degrade gracefully.
                // JS will fall back to manual-input mode (same as current behaviour).
            }
        }

        // WP-CB-CALC: CATEGORICAL book values (planting_method, frost_tolerance_class) live in
        // crop_attribute and are TEXT — they cannot ride the numeric SFA_CROP_BOOK map (the JS
        // flatten drops non-numerics). Deliver them via a separate text channel SFA_CROP_BOOK_TXT.
        // The date engine reads planting_method (direct/transplant/both branch) + frost class.
        $cropBookText = [];
        if (!empty($cropList)) {
            try {
                $slugs   = array_column($cropList, 'slug');
                $inMarks = implode(',', array_fill(0, count($slugs), '?'));
                $atStmt  = $this->pdo->prepare(
                    "SELECT c.slug, a.attribute_key, a.value_canonical
                     FROM crops c
                     JOIN crop_attribute a ON a.crop_id = c.id
                     WHERE c.slug IN ($inMarks)
                       AND a.attribute_key IN ('planting_method','frost_tolerance_class')"
                );
                $atStmt->execute($slugs);
                foreach ($atStmt->fetchAll() as $row) {
                    $val = (string)($row['value_canonical'] ?? '');
                    if ($val !== '') {
                        $cropBookText[(string)$row['slug']][(string)$row['attribute_key']] = $val;
                    }
                }
            } catch (\Throwable) {
                // crop_attribute may not exist on the mirror yet — degrade gracefully (date calcs
                // default to direct-seed; frost shows the honest no-data state).
            }
        }

        $html = Template::render('pages/calc_dash', [
            'contact'         => Modules::all()['contact'] ?? [],
            'crop_list'       => $cropList,
            'crop_book_values'=> $cropBookValues,
            'crop_book_text'  => $cropBookText,
        ]);
        return self::html($response, $html);
    }

    /**
     * WP-CB-1-patch01: calculator-plan export (CSV + print-friendly HTML for PDF).
     * Plan state is ephemeral client-side; the dashboard JS appends it as query
     * params (crop, beds, target_date, and any rows[label]=value pairs). With no
     * params the export still returns a valid (header-only) document.
     */
    public function calcExport(Request $request, Response $response, array $args): Response
    {
        // /calc/export.csv → fmt=csv (route arg); /calc/print → no fmt arg → pdf print view.
        $fmt = strtolower((string)($args['fmt'] ?? 'pdf'));
        $qp  = $request->getQueryParams();
        $crop   = trim((string)($qp['crop']        ?? ''));
        $beds   = trim((string)($qp['beds']        ?? ''));
        $target = trim((string)($qp['target_date'] ?? ''));
        // rows: arbitrary label=>value summary lines (e.g. ?rows[seeds]=12g&rows[yield]=105kg)
        $rows = [];
        if (isset($qp['rows']) && is_array($qp['rows'])) {
            foreach ($qp['rows'] as $label => $val) {
                $rows[(string)$label] = (string)$val;
            }
        }
        $context = array_filter([
            'גידול'      => $crop,
            'מס׳ ערוגות' => $beds,
            'תאריך יעד'  => $target,
        ], static fn ($v) => $v !== '');

        if ($fmt === 'csv') {
            $out = "\xEF\xBB\xBF"; // UTF-8 BOM so Excel reads Hebrew
            $esc = static fn (string $s): string => '"' . str_replace('"', '""', $s) . '"';
            $out .= $esc('שדה') . ',' . $esc('ערך') . "\r\n";
            foreach ($context as $k => $v) { $out .= $esc((string)$k) . ',' . $esc((string)$v) . "\r\n"; }
            foreach ($rows as $k => $v)    { $out .= $esc((string)$k) . ',' . $esc((string)$v) . "\r\n"; }
            $response->getBody()->write($out);
            return $response
                ->withHeader('Content-Type', 'text/csv; charset=utf-8')
                ->withHeader('Content-Disposition', 'attachment; filename="sfa-calc-plan.csv"')
                ->withStatus(200);
        }

        // PDF path → print-friendly HTML (the browser's "Save as PDF" produces the PDF;
        // no server-side PDF engine dependency on the shared LAMP host).
        $html = Template::render('pages/calc_export_print', [
            'context' => $context,
            'rows'    => $rows,
        ]);
        // no-store so the edge never caches this HTML (prevents a repeat of the
        // V01 stale-404 once /calc/print is reachable through Cloudflare).
        return self::html($response->withHeader('Cache-Control', 'no-store'), $html);
    }

    public function community(Request $request, Response $response): Response
    {
        $html = Template::render('pages/community', [
            'contact' => Modules::all()['contact'] ?? [],
        ]);
        return self::html($response, $html);
    }

    private static function html(Response $response, string $body): Response
    {
        $response->getBody()->write($body);
        return $response->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
