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
            'tiers' => Modules::all()['tiers'] ?? [],
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
        $html = Template::render('pages/calc_dash', [
            'contact' => Modules::all()['contact'] ?? [],
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
        $fmt = strtolower((string)($args['fmt'] ?? 'csv'));
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
        return self::html($response, $html);
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
