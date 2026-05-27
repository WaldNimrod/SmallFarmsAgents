<?php
/**
 * variety_row.php — COMPONENTS.md §7
 *
 * .cb-var is a BLOCK element (not <tr>). Sentinel: dtm_days === -32768
 * means "no DTM data, presence only" (per WP-B1/B3 convention) — render "—".
 *
 * Required vars (passed in via include scope):
 *   $variety — array with keys:
 *     vslug, name_he, breeding_type (F1/heirloom/OP), is_default (bool),
 *     dtm_days, yield_kg_per_m2, color_he, shape_he, taste_stars (1-5),
 *     resistance_he
 *   $crop_slug — parent crop slug (for the href)
 *
 * BEM contract: .cb-var, .cb-var--default, .cb-var__head, .cb-var__star,
 *   .cb-var__grid, .pill, .pill--code
 */
$variety = $variety ?? [];
$crop_slug = (string)($crop_slug ?? '');

$vslug           = (string)($variety['vslug']           ?? '');
$name_he         = (string)($variety['name_he']         ?? '');
$breeding_type   = (string)($variety['breeding_type']   ?? '');
$is_default      = !empty($variety['is_default']);
$dtm_days        = $variety['dtm_days'] ?? null;
$yield_kg_per_m2 = $variety['yield_kg_per_m2'] ?? null;
$color_he        = $variety['color_he']      ?? null;
$shape_he        = $variety['shape_he']      ?? null;
$taste_stars     = $variety['taste_stars']   ?? null;
$resistance_he   = $variety['resistance_he'] ?? null;

$dtm_display = ($dtm_days === null || $dtm_days === '' || (int)$dtm_days === -32768)
    ? '—'
    : (string)(int)$dtm_days;
?>
<a class="cb-var<?= $is_default ? ' cb-var--default' : '' ?>" href="/crop-book/<?= htmlspecialchars($crop_slug, ENT_QUOTES, 'UTF-8') ?>/variety/<?= htmlspecialchars($vslug, ENT_QUOTES, 'UTF-8') ?>/">
  <div class="cb-var__head">
    <?php if ($is_default): ?><span class="cb-var__star" title="זן ברירת מחדל">★</span><?php endif; ?>
    <h4><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></h4>
    <?php if (!empty($breeding_type)): ?>
      <span class="pill pill--code"><?= htmlspecialchars($breeding_type, ENT_QUOTES, 'UTF-8') ?></span>
    <?php endif; ?>
  </div>
  <div class="cb-var__grid">
    <span><small>DTM</small><?= htmlspecialchars($dtm_display, ENT_QUOTES, 'UTF-8') ?></span>
    <span><small>יבול</small><?= !empty($yield_kg_per_m2) ? htmlspecialchars(number_format((float)$yield_kg_per_m2, 1) . ' ק״ג/מ״ר', ENT_QUOTES, 'UTF-8') : '—' ?></span>
    <span><small>צבע</small><?= htmlspecialchars((string)($color_he ?? '—'), ENT_QUOTES, 'UTF-8') ?></span>
    <span><small>צורה</small><?= htmlspecialchars((string)($shape_he ?? '—'), ENT_QUOTES, 'UTF-8') ?></span>
    <span><small>טעם</small><?= !empty($taste_stars) ? str_repeat('★', max(0, min(5, (int)$taste_stars))) : '—' ?></span>
    <span><small>עמידות</small><?= htmlspecialchars((string)($resistance_he ?? '—'), ENT_QUOTES, 'UTF-8') ?></span>
  </div>
</a>
