<?php
declare(strict_types=1);

namespace SFA\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Template;

final class HomeController
{
    public function index(Request $request, Response $response): Response
    {
        $body = Template::render('home', []);
        $response->getBody()->write($body);
        return $response->withHeader('Content-Type', 'text/html; charset=utf-8');
    }
}
