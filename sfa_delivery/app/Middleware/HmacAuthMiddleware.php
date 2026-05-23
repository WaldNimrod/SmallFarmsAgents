<?php
declare(strict_types=1);

namespace SFA\Middleware;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface as Handler;
use SFA\Lib\Hmac;
use Slim\Psr7\Response;

final class HmacAuthMiddleware implements MiddlewareInterface
{
    public function process(Request $request, Handler $handler): ResponseInterface
    {
        $secret = $_ENV['INGEST_HMAC_SECRET'] ?? '';
        $headerValue = $request->getHeaderLine('X-SFA-Auth');

        // Read body BEFORE the handler does (Slim BodyParser may consume it)
        $body = (string)$request->getBody();
        $request->getBody()->rewind();

        $err = Hmac::verify($headerValue, $body, $secret);
        if ($err !== null) {
            return self::unauthorized($err);
        }
        return $handler->handle($request);
    }

    private static function unauthorized(string $reason): ResponseInterface
    {
        $r = new Response(401);
        $r->getBody()->write(json_encode(
            ['error' => 'unauthorized', 'reason' => $reason],
            JSON_UNESCAPED_UNICODE
        ));
        return $r->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
