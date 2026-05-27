<?php
/**
 * tier_badge.php — COMPONENTS.md §2
 *
 * Required vars (passed in via include scope):
 *   $tier   — one of: open | beta | coming | paid | custom
 *   $size   — (optional) 'sm' (default) | 'lg'
 *
 * BEM contract: .tier, .tier--lg, .tier--{leaf|sun|paper|soil|tomato}, .tier__glyph
 */
$tier = isset($tier) ? (string)$tier : 'open';
$size = isset($size) ? (string)$size : 'sm';

$tier_map = [
    'open'   => ['color' => 'leaf',   'glyph' => '●',  'label' => 'כלים לקהילה'],
    'beta'   => ['color' => 'sun',    'glyph' => 'β',  'label' => 'בטא · ניסיוני'],
    'coming' => ['color' => 'paper',  'glyph' => '⏳', 'label' => 'בקרוב'],
    'paid'   => ['color' => 'soil',   'glyph' => '★',  'label' => 'כלים מתקדמים'],
    'custom' => ['color' => 'tomato', 'glyph' => '✎',  'label' => 'בדיוק לחווה שלך'],
];
$entry = $tier_map[$tier] ?? $tier_map['open'];
$color = $entry['color'];
$glyph = $entry['glyph'];
$label = $entry['label'];
?>
<span class="tier <?= $size === 'lg' ? 'tier--lg ' : '' ?>tier--<?= htmlspecialchars($color, ENT_QUOTES, 'UTF-8') ?>">
  <span class="tier__glyph"><?= htmlspecialchars($glyph, ENT_QUOTES, 'UTF-8') ?></span><?= htmlspecialchars($label, ENT_QUOTES, 'UTF-8') ?>
</span>
