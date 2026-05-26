<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use SFA\Lib\Modules;
use Slim\Psr7\Factory\ServerRequestFactory;

final class ModulesTest extends TestCase
{
    public function testByTierOpenHasModules(): void
    {
        $open = Modules::byTier('open');
        $this->assertNotEmpty($open);
    }

    public function testModulesApiListsEightModules(): void
    {
        $app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($app);
        $res = $app->handle((new ServerRequestFactory())->createServerRequest('GET', '/api/v1/modules'));
        $this->assertSame(200, $res->getStatusCode());
        $data = json_decode((string)$res->getBody(), true);
        $this->assertCount(8, $data['modules']);
    }
}
