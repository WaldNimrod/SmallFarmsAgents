<?php
declare(strict_types=1);

use SFA\Controllers\AssumptionsController;
use SFA\Controllers\CropBookViewController;
use SFA\Controllers\CropsController;
use SFA\Controllers\HealthController;
use SFA\Controllers\HubController;
use SFA\Controllers\IngestController;
use SFA\Controllers\MarketViewController;
use SFA\Controllers\ModulesController;
use SFA\Controllers\ProductsController;
use SFA\Controllers\SearchController;
use SFA\Middleware\HmacAuthMiddleware;
use Slim\App;
use Slim\Routing\RouteCollectorProxy;

return function (App $app): void {
    $app->get('/', [HubController::class, 'home']);
    $app->get('/about[/]', [HubController::class, 'tiers']);
    $app->get('/search[/]', [HubController::class, 'search']);
    $app->get('/calc[/]', [HubController::class, 'calc']);
    // WP-CB-1-patch01: calculator-plan export (csv | pdf-print)
    $app->get('/calc/export.{fmt:csv|pdf}', [HubController::class, 'calcExport']);

    $app->get('/crop-book[/]', [CropBookViewController::class, 'entry']);
    $app->get('/crop-book/questions[/]', [CropBookViewController::class, 'questions']);
    $app->get('/crop-book/family[/]', [CropBookViewController::class, 'family']);
    $app->get('/crop-book/table[/]', [CropBookViewController::class, 'tableView']);
    $app->get('/crop-book/search[/]', [CropBookViewController::class, 'search']);
    $app->get('/crop-book/cover-crops[/]', [CropBookViewController::class, 'coverCrops']);
    // AC-U4-07: /crop-book/family/{slug} links in book_family.php point to a family-detail
    // page that does not exist yet — redirect to the family list to avoid 404.
    $app->get('/crop-book/family/{slug}[/]', function ($req, $res) {
        return $res->withHeader('Location', '/crop-book/family/')->withStatus(302);
    });
    $app->get('/crop-book/{slug}[/]', [CropBookViewController::class, 'detail']);
    $app->get('/crop-book/{slug}/variety/{vslug}[/]', [CropBookViewController::class, 'variety']);

    $app->get('/market[/]', [MarketViewController::class, 'index']);
    $app->get('/market/{slug}[/]', [MarketViewController::class, 'detail']);

    $app->get('/community[/]', [HubController::class, 'community']);

    // AC-U4-07: redirect planned/future modules so they don't 404.
    // /clients/ is linked from the home page module grid (tier=paid, status=planned).
    $app->get('/clients[/]', function ($req, $res) {
        return $res->withHeader('Location', '/')->withStatus(302);
    });

    $app->group('/api/v1', function (RouteCollectorProxy $g): void {
        $g->get('/health', [HealthController::class, 'health']);
        $g->get('/modules', [ModulesController::class, 'list']);
        $g->get('/search', [SearchController::class, 'globalSearch']);
        $g->get('/crops', [CropsController::class, 'list']);
        $g->get('/crops/{slug}', [CropsController::class, 'detail']);
        $g->get('/products', [ProductsController::class, 'list']);
        $g->get('/products/{slug}', [ProductsController::class, 'detail']);
        $g->get('/market/{slug}/history', [MarketViewController::class, 'productHistoryApi']);
        $g->post('/ingest', [IngestController::class, 'receive'])->add(HmacAuthMiddleware::class);
        // WP-CB-1 endpoints
        $g->get('/assumptions', [AssumptionsController::class, 'list']);
        $g->post('/contribute', [AssumptionsController::class, 'contribute']);
    });

    $app->get('/admin/migrate', [HealthController::class, 'migrate']);
};
