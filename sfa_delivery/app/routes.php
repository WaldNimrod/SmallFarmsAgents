<?php
declare(strict_types=1);

use SFA\Controllers\HealthController;
use SFA\Controllers\HomeController;
use SFA\Controllers\IngestController;
use SFA\Controllers\CropsController;
use SFA\Controllers\CropBookViewController;
use SFA\Controllers\ProductsController;
use SFA\Controllers\MarketViewController;
use SFA\Middleware\HmacAuthMiddleware;
use Slim\App;
use Slim\Routing\RouteCollectorProxy;

return function (App $app): void {
    // Landing (HTML)
    $app->get('/', [HomeController::class, 'index']);

    // User-facing HTML (WP-3)
    $app->get('/crop-book[/]', [CropBookViewController::class, 'index']);
    $app->get('/crop-book/{slug}[/]', [CropBookViewController::class, 'detail']);
    $app->get('/market[/]', [MarketViewController::class, 'index']);
    $app->get('/market/{slug}[/]', [MarketViewController::class, 'detail']);

    // API v1 (WP-2)
    $app->group('/api/v1', function (RouteCollectorProxy $g): void {
        $g->get('/health', [HealthController::class, 'health']);

        $g->get('/crops', [CropsController::class, 'list']);
        $g->get('/crops/{slug}', [CropsController::class, 'detail']);

        $g->get('/products', [ProductsController::class, 'list']);
        $g->get('/products/{slug}', [ProductsController::class, 'detail']);

        $g->post('/ingest', [IngestController::class, 'receive'])
          ->add(HmacAuthMiddleware::class);
    });

    // First-deploy migration runner (token-gated; locked once token blank)
    $app->get('/admin/migrate', [HealthController::class, 'migrate']);
};
