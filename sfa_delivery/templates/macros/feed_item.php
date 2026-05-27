<?php
/**
 * feed_item.php — COMPONENTS.md §9
 *
 * Required vars (passed in via include scope):
 *   $kind       — one of: suggest | correction | data
 *   $author_he  — author display name
 *   $region_he  — region label
 *   $date_he    — relative date (e.g., "3 ימים")
 *   $text_he    — body text
 *   $tag_he     — tag/category label
 *   $upvotes    — (optional) int
 *
 * BEM contract: .feed-item, .feed-item__kind, .feed-item__kind--{color},
 *   .feed-item__body, .feed-item__head, .feed-item__date, .feed-item__text,
 *   .feed-item__meta, .feed-item__tag, .feed-item__upvotes, .pill, .pill--muted
 */
$kind      = (string)($kind      ?? 'data');
$author_he = (string)($author_he ?? '');
$region_he = (string)($region_he ?? '');
$date_he   = (string)($date_he   ?? '');
$text_he   = (string)($text_he   ?? '');
$tag_he    = (string)($tag_he    ?? '');
$upvotes   = isset($upvotes) ? (int)$upvotes : 0;

$kind_map = [
    'suggest'    => ['color' => 'sun',    'glyph' => '💡', 'label' => 'הצעה'],
    'correction' => ['color' => 'tomato', 'glyph' => '◐',  'label' => 'תיקון'],
    'data'       => ['color' => 'leaf',   'glyph' => '✎',  'label' => 'תרומה'],
];
$entry = $kind_map[$kind] ?? $kind_map['data'];
$color = $entry['color'];
$glyph = $entry['glyph'];
$kind_label_he = $entry['label'];
?>
<article class="feed-item">
  <div class="feed-item__kind feed-item__kind--<?= htmlspecialchars($color, ENT_QUOTES, 'UTF-8') ?>">
    <span><?= htmlspecialchars($glyph, ENT_QUOTES, 'UTF-8') ?></span>
    <small><?= htmlspecialchars($kind_label_he, ENT_QUOTES, 'UTF-8') ?></small>
  </div>
  <div class="feed-item__body">
    <div class="feed-item__head">
      <strong><?= htmlspecialchars($author_he, ENT_QUOTES, 'UTF-8') ?> · <?= htmlspecialchars($region_he, ENT_QUOTES, 'UTF-8') ?></strong>
      <span class="feed-item__date"><?= htmlspecialchars($date_he, ENT_QUOTES, 'UTF-8') ?></span>
    </div>
    <p class="feed-item__text"><?= htmlspecialchars($text_he, ENT_QUOTES, 'UTF-8') ?></p>
    <div class="feed-item__meta">
      <span class="pill pill--muted feed-item__tag"><?= htmlspecialchars($tag_he, ENT_QUOTES, 'UTF-8') ?></span>
      <?php if ($upvotes > 0): ?>
        <span class="feed-item__upvotes">▲ <?= (int)$upvotes ?></span>
      <?php endif; ?>
    </div>
  </div>
</article>
