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
    public function __construct(private ?PDO $pdo = null)
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
        $html = Template::render('pages/hub_calc', [
            'contact' => Modules::all()['contact'] ?? [],
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
