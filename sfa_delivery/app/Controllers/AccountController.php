<?php
declare(strict_types=1);

namespace SFA\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

/**
 * AccountController — /account route (Class B v2)
 *
 * WP-CB-UI-CLASSB §2.8: UI shell only + "בקרוב" labels, no auth backend.
 * Renders account_landing.php with the logged-out shell (login card +
 * open-core empty state) and the static profile shell.
 * LOD400 §9.2: account = visual-only, no functional submit, no auth backend.
 */
final class AccountController
{
    public function index(Request $request, Response $response): Response
    {
        $html = Template::render('pages/account_landing', []);
        $response->getBody()->write($html);
        return $response->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
