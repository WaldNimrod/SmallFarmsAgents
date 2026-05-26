<?php
declare(strict_types=1);

namespace SFA\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Modules;
use SFA\Lib\Template;

final class HubController
{
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

    public function search(Request $request, Response $response): Response
    {
        $q = trim((string)($request->getQueryParams()['q'] ?? ''));
        $html = Template::render('pages/search_results', ['q' => $q]);
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
