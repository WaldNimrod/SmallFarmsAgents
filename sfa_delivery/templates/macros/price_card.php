<?php
/**
 * price_card.php — COMPONENTS.md §5
 *
 * Required vars (passed in via include scope):
 *   $product — array with keys:
 *     slug, name_he, en_name, unit_he, glyph_letter,
 *     price_current, currency, price_median, price_min, price_max,
 *     source_count, observation_count
 *   $price_range_min, $price_range_max — (optional) global range for .fill scaling
 *     If absent, .fill is computed against the product's own min/max (100% fill).
 *
 * BEM contract: .pcard, .pcard__head, .pcard__glyph, .pcard__name, .pcard__unit,
 *   .pcard__price, .big, .cur, .med, .pcard__range, .fill, .pcard__range-text,
 *   .pcard__meta, .sources, .pcard__bookcta
 */
$product = $product ?? [];
$slug              = (string)($product['slug']              ?? '');
$book_slug         = (string)($product['book_slug']         ?? '');
$name_he           = (string)($product['name_he']           ?? '');
$en_name           = (string)($product['en_name']           ?? '');
$unit_he           = (string)($product['unit_he']           ?? '');
$glyph_letter      = (string)($product['glyph_letter']      ?? '');
$price_current     = (float)($product['price_current']     ?? 0.0);
$currency          = (string)($product['currency']          ?? '₪');
$price_median      = (float)($product['price_median']      ?? 0.0);
$price_min         = (float)($product['price_min']         ?? 0.0);
$price_max         = (float)($product['price_max']         ?? 0.0);
$source_count      = (int)  ($product['source_count']      ?? 0);
$observation_count = (int)  ($product['observation_count'] ?? 0);

// Compute fill bar position. If global range provided, scale this product's
// [min, max] window inside it; otherwise the card's own range fills the bar.
$global_min = isset($price_range_min) ? (float)$price_range_min : $price_min;
$global_max = isset($price_range_max) ? (float)$price_range_max : $price_max;
$global_span = max($global_max - $global_min, 0.0001);
$fill_inset_end = max(0.0, min(100.0, (($global_max - $price_max) / $global_span) * 100.0));
$fill_size      = max(0.0, min(100.0, (($price_max - $price_min) / $global_span) * 100.0));
?>
<div class="pcard">
  <div class="pcard__head">
    <div class="pcard__glyph"><?= htmlspecialchars($glyph_letter, ENT_QUOTES, 'UTF-8') ?></div>
    <div>
      <div class="pcard__name"><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></div>
      <div class="pcard__unit"><?= htmlspecialchars($unit_he, ENT_QUOTES, 'UTF-8') ?> · <?= htmlspecialchars($en_name, ENT_QUOTES, 'UTF-8') ?></div>
    </div>
  </div>
  <div class="pcard__price">
    <span class="big"><?= number_format($price_current, 2) ?></span>
    <span class="cur"><?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?></span>
    <span class="med">חציון <?= number_format($price_median, 2) ?></span>
  </div>
  <div class="pcard__range">
    <div class="fill" style="inset-inline-end: <?= number_format($fill_inset_end, 2, '.', '') ?>%; inline-size: <?= number_format($fill_size, 2, '.', '') ?>%"></div>
  </div>
  <div class="pcard__range-text">
    <span><?= number_format($price_min, 2) ?></span>
    <span><?= number_format($price_max, 2) ?> <?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?></span>
  </div>
  <div class="pcard__meta">
    <span><span class="sources"><span></span><span></span><span></span></span> <?= (int)$source_count ?></span>
    <span><?= (int)$observation_count ?> תצפיות</span>
    <?php if ($book_slug !== ''): ?><a href="/crop-book/<?= htmlspecialchars($book_slug, ENT_QUOTES, 'UTF-8') ?>" class="pcard__bookcta">↗ ספר</a><?php endif; ?>
  </div>
</div>
