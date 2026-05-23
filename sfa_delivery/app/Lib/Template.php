<?php
declare(strict_types=1);

namespace SFA\Lib;

/**
 * Minimal PHP template renderer. No build step. No deps.
 * Templates live in /templates and use plain PHP with $vars in scope.
 *
 * Usage:
 *   $html = Template::render('crop_book/list', ['crops' => $rows]);
 */
final class Template
{
    private const ROOT = __DIR__ . '/../../templates';

    public static function render(string $name, array $vars = []): string
    {
        $file = self::ROOT . '/' . $name . '.php';
        if (!is_file($file)) {
            throw new \RuntimeException("template not found: {$name}");
        }
        extract($vars, EXTR_SKIP);
        ob_start();
        include $file;
        return (string)ob_get_clean();
    }

    /** HTML-escape helper for use inside templates. */
    public static function h(mixed $v): string
    {
        return htmlspecialchars((string)($v ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
