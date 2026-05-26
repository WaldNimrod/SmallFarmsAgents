<?php
declare(strict_types=1);

namespace SFA\Lib;

final class Modules
{
    private static ?array $cache = null;

    public static function all(): array
    {
        if (self::$cache !== null) {
            return self::$cache;
        }

        $data = require __DIR__ . '/../../modules.php';
        self::$cache = is_array($data) ? $data : [];
        return self::$cache;
    }

    public static function byTier(string $tier): array
    {
        return array_values(array_filter(self::all()['modules'] ?? [], static fn(array $m): bool => ($m['tier'] ?? '') === $tier));
    }

    public static function byId(string $id): ?array
    {
        foreach (self::all()['modules'] ?? [] as $module) {
            if (($module['id'] ?? '') === $id) {
                return $module;
            }
        }
        return null;
    }
}
