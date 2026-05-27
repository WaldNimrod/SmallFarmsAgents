<?php
declare(strict_types=1);

namespace SFA\Middleware;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Handlers\ErrorHandler;
use Throwable;

/**
 * Returns JSON error responses (no HTML stack traces).
 */
final class JsonErrorHandler extends ErrorHandler
{
    protected function respond(): ResponseInterface
    {
        $exception = $this->exception;
        $statusCode = $this->statusCode;

        $payload = [
            'error' => true,
            'status' => $statusCode,
            'message' => $statusCode >= 500
                ? 'internal server error'
                : ($exception instanceof Throwable ? $exception->getMessage() : 'error'),
        ];

        if ($this->displayErrorDetails && $exception instanceof Throwable) {
            $payload['detail'] = $exception->getMessage();
            $payload['file'] = $exception->getFile();
            $payload['line'] = $exception->getLine();
        }

        $response = $this->responseFactory->createResponse($statusCode);
        $response->getBody()->write(json_encode($payload, JSON_UNESCAPED_UNICODE));
        return $response->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
