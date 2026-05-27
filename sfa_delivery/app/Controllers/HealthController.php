<?php
declare(strict_types=1);

namespace SFA\Controllers;

use PDO;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Throwable;

final class HealthController
{
    public function __construct(private PDO $pdo) {}

    public function root(Request $request, Response $response): Response
    {
        return self::json($response, [
            'service' => 'sfa.nimrod.bio',
            'message' => 'Small Farms Agents — delivery tier',
            'endpoints' => [
                '/api/v1/health',
                '/api/v1/crops',
                '/api/v1/products',
            ],
        ]);
    }

    public function health(Request $request, Response $response): Response
    {
        $dbStatus = 'ok';
        $dbDetail = null;
        try {
            $this->pdo->query('SELECT 1');
        } catch (Throwable $e) {
            $dbStatus = 'fail';
            $dbDetail = $e->getMessage();
        }

        $payload = [
            'status' => $dbStatus === 'ok' ? 'ok' : 'degraded',
            'php_version' => PHP_VERSION,
            'db' => $dbStatus,
            'ts' => gmdate('c'),
        ];
        if ($dbDetail !== null && ($_ENV['APP_DEBUG'] ?? 'false') === 'true') {
            $payload['db_detail'] = $dbDetail;
        }
        return self::json($response, $payload, $dbStatus === 'ok' ? 200 : 500);
    }

    public function migrate(Request $request, Response $response): Response
    {
        $token = $request->getQueryParams()['token'] ?? '';
        $expected = $_ENV['ADMIN_MIGRATE_TOKEN'] ?? '';
        if ($expected === '' || !hash_equals($expected, $token)) {
            return self::json($response, ['error' => 'unauthorized'], 401);
        }

        // Run migrate.php inline
        ob_start();
        $result = ['applied' => [], 'already' => [], 'errors' => []];
        try {
            $files = glob(dirname(__DIR__, 2) . '/migrations/[0-9][0-9][0-9]_*.sql');
            sort($files);

            // Ensure tracking table
            $this->pdo->exec(file_get_contents(dirname(__DIR__, 2) . '/migrations/001_schema_migrations.sql'));

            $applied = $this->pdo->query('SELECT version FROM schema_migrations')
                ->fetchAll(PDO::FETCH_COLUMN);

            // NOTE: MySQL DDL (CREATE TABLE) is non-transactional and causes
            // implicit COMMIT. We don't wrap in transactions here.
            foreach ($files as $file) {
                $version = basename($file, '.sql');
                if (in_array($version, $applied, true)) {
                    $result['already'][] = $version;
                    continue;
                }
                try {
                    $sql = file_get_contents($file);
                    $this->pdo->exec($sql);
                    $stmt = $this->pdo->prepare('INSERT INTO schema_migrations (version) VALUES (?)');
                    $stmt->execute([$version]);
                    $result['applied'][] = $version;
                } catch (Throwable $e) {
                    $result['errors'][] = ['version' => $version, 'error' => $e->getMessage()];
                    break;
                }
            }
        } catch (Throwable $e) {
            $result['errors'][] = ['stage' => 'bootstrap', 'error' => $e->getMessage()];
        }
        ob_end_clean();

        return self::json($response, $result, empty($result['errors']) ? 200 : 500);
    }

    private static function json(Response $response, array $payload, int $status = 200): Response
    {
        $response->getBody()->write(json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
        return $response
            ->withStatus($status)
            ->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
