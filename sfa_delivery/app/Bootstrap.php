<?php
declare(strict_types=1);

namespace SFA;

use DI\Container;
use Slim\App;
use Slim\Factory\AppFactory;

final class Bootstrap
{
    public static function createApp(): App
    {
        // Load .env (production) or .env.test (phpunit)
        $envDir = dirname(__DIR__);
        $envFile = getenv('APP_ENV_FILE') ?: '.env';
        if (file_exists($envDir . '/' . $envFile)) {
            $dotenv = \Dotenv\Dotenv::createImmutable($envDir, $envFile);
            $dotenv->safeLoad();
        }

        $container = new Container();

        // PDO singleton
        $container->set(\PDO::class, function () {
            return Lib\Db::create();
        });

        // Logger singleton
        $container->set(\Psr\Log\LoggerInterface::class, function () {
            return Lib\Logger::create();
        });

        AppFactory::setContainer($container);
        $app = AppFactory::create();

        // Body parser middleware (for JSON POSTs)
        $app->addBodyParsingMiddleware();

        // Routing middleware
        $app->addRoutingMiddleware();

        // Error middleware — JSON responses, no HTML stack traces in prod
        $debug = ($_ENV['APP_DEBUG'] ?? 'false') === 'true';
        $errorMiddleware = $app->addErrorMiddleware($debug, true, true);
        $errorMiddleware->setDefaultErrorHandler(new Middleware\JsonErrorHandler(
            $app->getCallableResolver(),
            $app->getResponseFactory(),
            $container->get(\Psr\Log\LoggerInterface::class)
        ));

        return $app;
    }
}
