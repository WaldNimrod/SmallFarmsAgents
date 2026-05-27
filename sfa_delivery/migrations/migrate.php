<?php
declare(strict_types=1);

/**
 * CLI migration runner — applies all pending numbered SQL files in /migrations.
 * Idempotent. Tracks state in `schema_migrations` table.
 *
 * Usage: php migrations/migrate.php
 *
 * Also invokable via the web (token-gated) by HealthController::migrate
 * during first deploy when shell is unavailable.
 */

require __DIR__ . '/../vendor/autoload.php';
\Dotenv\Dotenv::createImmutable(__DIR__ . '/..')->safeLoad();

$pdo = SFA\Lib\Db::create();

// Ensure tracking table first
$bootstrap = file_get_contents(__DIR__ . '/001_schema_migrations.sql');
$pdo->exec($bootstrap);

$files = glob(__DIR__ . '/[0-9][0-9][0-9]_*.sql');
sort($files);

$applied = $pdo->query('SELECT version FROM schema_migrations')
    ->fetchAll(PDO::FETCH_COLUMN);

$appliedCount = 0;
foreach ($files as $file) {
    $version = basename($file, '.sql');
    if (in_array($version, $applied, true)) {
        fwrite(STDOUT, "[skip] {$version} (already applied)\n");
        continue;
    }
    fwrite(STDOUT, "[apply] {$version} ... ");
    $pdo->beginTransaction();
    try {
        $sql = file_get_contents($file);
        $pdo->exec($sql);
        $stmt = $pdo->prepare('INSERT INTO schema_migrations (version) VALUES (?)');
        $stmt->execute([$version]);
        $pdo->commit();
        fwrite(STDOUT, "OK\n");
        $appliedCount++;
    } catch (Throwable $e) {
        $pdo->rollBack();
        fwrite(STDERR, "FAIL\n  " . $e->getMessage() . "\n");
        exit(1);
    }
}
fwrite(STDOUT, "Done. Applied {$appliedCount} migration(s).\n");
