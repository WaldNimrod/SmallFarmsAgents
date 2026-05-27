<?php
declare(strict_types=1);

namespace SFA\Middleware;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface as Handler;

/**
 * Ensures every response has Content-Type: application/json; charset=utf-8
 * unless one is already set.
 */
final class JsonResponseMiddleware implements MiddlewareInterface
{
    public function process(Request $request, Handler $handler): ResponseInterface
    {
        $response = $handler->handle($request);
        if (!$response->hasHeader('Content-Type')) {
            $response = $response->withHeader('Content-Type', 'application/json; charset=utf-8');
        }
        return $response;
    }
}
