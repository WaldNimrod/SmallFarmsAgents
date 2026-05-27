<?php
declare(strict_types=1);

namespace SFA\Lib;

use Monolog\Handler\RotatingFileHandler;
use Monolog\Handler\StreamHandler;
use Monolog\Level;
use Monolog\Logger as MonologLogger;
use Psr\Log\LoggerInterface;

final class Logger
{
    public static function create(): LoggerInterface
    {
        $log = new MonologLogger('sfa');

        $level = match (strtolower($_ENV['LOG_LEVEL'] ?? 'info')) {
            'debug' => Level::Debug,
            'warning' => Level::Warning,
            'error' => Level::Error,
            default => Level::Info,
        };

        $logsDir = dirname(__DIR__, 2) . '/logs';
        if (!is_dir($logsDir)) {
            @mkdir($logsDir, 0770, true);
        }
        if (is_writable($logsDir)) {
            $log->pushHandler(new RotatingFileHandler($logsDir . '/sfa.log', 7, $level));
        } else {
            // Fallback to error_log if filesystem not writable
            $log->pushHandler(new StreamHandler('php://stderr', $level));
        }
        return $log;
    }
}
