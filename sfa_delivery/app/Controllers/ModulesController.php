<?php
declare(strict_types=1);

namespace SFA\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use SFA\Lib\Modules;

final class ModulesController
{
    public function list(Request $request, Response $response): Response
    {
        $payload = Modules::all();
        $response->getBody()->write(json_encode($payload, JSON_UNESCAPED_UNICODE));
        return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
