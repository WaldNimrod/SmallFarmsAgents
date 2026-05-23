<?php
declare(strict_types=1);

use SFA\Controllers\HealthController;
use SFA\Controllers\IngestController;
use SFA\Controllers\CropsController;
use SFA\Controllers\ProductsController;
use SFA\Middleware\HmacAuthMiddleware;
use Slim\App;
use Slim\Routing\RouteCollectorProxy;

return function (App $app): void {
    // Landing
    $app->get('/', [HealthController::class, 'root']);

    // API v1
    $app->group('/api/v1', function (RouteCollectorProxy $g): void {
        $g->get('/health', [HealthController::class, 'health']);

        $g->get('/crops', [CropsController::class, 'list']);
        $g->get('/crops/{slug}', [CropsController::class, 'detail']);

        $g->get('/products', [ProductsController::class, 'list']);
        $g->get('/products/{slug}', [ProductsController::class, 'detail']);

        $g->post('/ingest', [IngestController::class, 'receive'])
          ->add(HmacAuthMiddleware::class);
    });

    // First-deploy migration runner (token-gated; remove after first run)
    $app->get('/admin/migrate', [HealthController::class, 'migrate']);
};
