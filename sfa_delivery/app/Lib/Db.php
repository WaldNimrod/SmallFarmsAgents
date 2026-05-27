<?php
declare(strict_types=1);

namespace SFA\Lib;

use PDO;
use RuntimeException;

final class Db
{
    public static function create(): PDO
    {
        $host = $_ENV['DB_HOST'] ?? 'localhost';
        $port = (int)($_ENV['DB_PORT'] ?? 3306);
        $name = $_ENV['DB_NAME'] ?? '';
        $user = $_ENV['DB_USER'] ?? '';
        $pass = $_ENV['DB_PASS'] ?? '';

        // sqlite fallback for tests (set DB_DSN=sqlite::memory: in test env)
        if (!empty($_ENV['DB_DSN'])) {
            return new PDO($_ENV['DB_DSN'], null, null, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ]);
        }

        if ($name === '' || $user === '') {
            throw new RuntimeException('DB_NAME and DB_USER must be set in .env');
        }

        $dsn = "mysql:host={$host};port={$port};dbname={$name};charset=utf8mb4";
        return new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
        ]);
    }
}
