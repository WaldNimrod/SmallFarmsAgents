<?php
declare(strict_types=1);

namespace SFA\Lib;

/**
 * CommunityFeed — global hook for community feed items (COMPONENTS.md §9).
 *
 * Returns feed_item-shaped rows (kind/author_he/region_he/date_he/text_he/
 * tag_he/upvotes) for any route to render via macros/feed_item.php.
 *
 * Source of truth: data/community_feed.json (team_00 maintained). If the file
 * is missing or unparseable, falls back to a small curated set so the sidebar
 * never renders empty. No community write surface exists yet (LV-S-1).
 */
final class CommunityFeed
{
    private const KINDS = ['suggest', 'correction', 'data'];

    private static ?array $cache = null;

    /** @return list<array<string,mixed>> */
    public static function recent(int $limit = 3): array
    {
        if (self::$cache === null) {
            self::$cache = self::load();
        }
        if ($limit < 0) {
            $limit = 0;
        }
        return array_slice(self::$cache, 0, $limit);
    }

    /** @return list<array<string,mixed>> */
    private static function load(): array
    {
        $path = __DIR__ . '/../../data/community_feed.json';
        if (is_file($path) && is_readable($path)) {
            $raw = file_get_contents($path);
            if ($raw !== false) {
                $decoded = json_decode($raw, true);
                if (is_array($decoded)) {
                    $items = array_values(array_filter(
                        array_map([self::class, 'normalize'], $decoded),
                        static fn(?array $i): bool => $i !== null
                    ));
                    if ($items !== []) {
                        return $items;
                    }
                }
            }
        }
        return self::fallback();
    }

    /** @param mixed $item @return array<string,mixed>|null */
    private static function normalize($item): ?array
    {
        if (!is_array($item)) {
            return null;
        }
        $kind = (string)($item['kind'] ?? 'data');
        if (!in_array($kind, self::KINDS, true)) {
            $kind = 'data';
        }
        return [
            'kind'      => $kind,
            'author_he' => (string)($item['author_he'] ?? ''),
            'region_he' => (string)($item['region_he'] ?? ''),
            'date_he'   => (string)($item['date_he']   ?? ''),
            'text_he'   => (string)($item['text_he']   ?? ''),
            'tag_he'    => (string)($item['tag_he']    ?? ''),
            'upvotes'   => (int)($item['upvotes'] ?? 0),
        ];
    }

    /** @return list<array<string,mixed>> */
    private static function fallback(): array
    {
        return [
            [
                'kind' => 'data', 'author_he' => 'דנה', 'region_he' => 'עמק יזרעאל',
                'date_he' => '3 ימים', 'text_he' => 'הוספתי זמני נביטה לעגבניות שרי מהעונה האחרונה בבית רשת.',
                'tag_he' => 'עגבניות', 'upvotes' => 7,
            ],
            [
                'kind' => 'correction', 'author_he' => 'יוסי', 'region_he' => 'גליל מערבי',
                'date_he' => 'שבוע', 'text_he' => 'מרווח השתילה לכרוב היה גבוה מדי — תיקנתי ל-45 ס״מ.',
                'tag_he' => 'כרוב', 'upvotes' => 4,
            ],
            [
                'kind' => 'suggest', 'author_he' => 'מירי', 'region_he' => 'השרון',
                'date_he' => 'שבועיים', 'text_he' => 'אפשר להוסיף טבלת ליווי גידולים? יעזור לתכנון ערוגות.',
                'tag_he' => 'תכנון', 'upvotes' => 11,
            ],
        ];
    }
}
