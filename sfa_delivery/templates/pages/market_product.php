<?php
/**
 * market_product.php — Route /market/{slug}
 *
 * Per MANDATE_WP-UI-RE-BUILD §3 (route 13) + LOD400 v1.0.3 §0.5 + COMPONENTS.md §10.
 *
 * Variables expected from controller (MarketViewController::detail):
 *   $product — array{slug,hebrew_name,category,unit,last_price,last_price_date,freshness_days,payload_json,...}
 *   $history — array<array{price_date,price,source}> — 28-day window.
 *
 * BEM contract (mandate §3 — `gj-pricebig` family; LOD400 §0.5 — `mk-disclaimer`,
 * `contrib-strip`, `gj-crosslink`):
 *   .mk-disclaimer       (via market_disclaimer.php macro)
 *   .gj-pricebig, .gj-pricebig__head, .gj-pricebig__glyph,
 *   .gj-pricebig__name, .gj-pricebig__en,
 *   .gj-pricebig__price, .gj-pricebig__big, .gj-pricebig__cur, .gj-pricebig__unit,
 *   .gj-pricebig__lbl, .gj-pricebig__meta
 *   .gj-pricehist, .gj-pricehist__h, .gj-pricehist__table
 *   .gj-crosslink, .gj-crosslink--soil  (via crosslink.php macro, market-to-book)
 *   .contrib-strip       (via contrib_strip.php macro)
 */
use SFA\Lib\Template;

$product = $product ?? [];
$history = $history ?? [];

// Normalize product fields (defensive — controller currently passes
// hebrew_name/last_price; future shape uses name_he/price_current/etc.)
$slug         = (string)($product['slug']        ?? '');
$name_he      = (string)($product['name_he']     ?? $product['hebrew_name'] ?? '');
$en_name      = (string)($product['en_name']     ?? '');
$icon_slug    = (string)($product['icon_slug']   ?? 'leaf');
$unit_he      = (string)($product['unit_he']     ?? $product['unit'] ?? 'ק״ג');
$currency     = (string)($product['currency']    ?? '₪');
$price_current= (float) ($product['price_current']?? $product['last_price'] ?? 0.0);
$price_median = (float) ($product['price_median'] ?? $price_current);
$price_min    = (float) ($product['price_min']    ?? $price_current);
$price_max    = (float) ($product['price_max']    ?? $price_current);
$source_count = (int)   ($product['source_count']      ?? 0);
$obs_count    = (int)   ($product['observation_count'] ?? 0);
$updated_he   = (string)($product['updated_he']   ?? $product['last_price_date'] ?? '');
$book_slug    = (string)($product['book_slug']    ?? $slug);
$book_label_he= (string)($product['book_label_he']?? $name_he);

// Allow history either via $product['history'] (mandate example) or top-level $history (controller).
$hist_rows = !empty($product['history']) ? $product['history'] : $history;

$page_title = $name_he !== '' ? $name_he : 'מוצר';
$page_sub   = 'מחירון · ' . ($name_he !== '' ? $name_he : '');
$active     = 'market';

ob_start();
?>
<?php /* Disclaimer at top — MANDATORY on every market view (COMPONENTS.md §10) */ ?>
<?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>

<section class="gj-pricebig">
  <div class="gj-pricebig__head">
    <span class="gj-pricebig__glyph"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icon-<?= htmlspecialchars($icon_slug, ENT_QUOTES, 'UTF-8') ?>"/></svg></span>
    <div>
      <h1 class="gj-pricebig__name"><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></h1>
      <p class="gj-pricebig__en"><?= htmlspecialchars($en_name, ENT_QUOTES, 'UTF-8') ?></p>
    </div>
  </div>
  <div class="gj-pricebig__price">
    <span class="gj-pricebig__big"><?= number_format($price_current, 2) ?></span>
    <span class="gj-pricebig__cur"><?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?></span>
    <span class="gj-pricebig__unit"><?= htmlspecialchars($unit_he, ENT_QUOTES, 'UTF-8') ?></span>
  </div>
  <div class="gj-pricebig__lbl">חציון <?= number_format($price_median, 2) ?> · טווח <?= number_format($price_min, 2) ?>–<?= number_format($price_max, 2) ?></div>
  <div class="gj-pricebig__meta">
    <span><?= (int)$source_count ?> מקורות</span>
    <span><?= (int)$obs_count ?> תצפיות</span>
    <span>עודכן <?= htmlspecialchars($updated_he, ENT_QUOTES, 'UTF-8') ?></span>
  </div>
</section>

<?php /* History table — 28-day window */ ?>
<?php if (!empty($hist_rows)): ?>
  <section class="gj-pricehist">
    <h2 class="gj-pricehist__h">היסטוריה — 28 ימים אחרונים</h2>
    <table class="gj-pricehist__table">
      <thead>
        <tr>
          <th scope="col" data-sort="date">תאריך</th>
          <th scope="col" data-sort="price">מחיר</th>
          <th scope="col" data-sort="sources">מקורות</th>
        </tr>
      </thead>
      <tbody>
        <?php foreach ($hist_rows as $hr):
          $date_he      = (string)($hr['date_he']      ?? $hr['price_date'] ?? '');
          $price_val    = (float) ($hr['price']        ?? 0.0);
          $row_source_n = isset($hr['source_count']) ? (int)$hr['source_count'] : null;
          $row_source_s = isset($hr['source']) ? (string)$hr['source'] : '';
        ?>
          <tr>
            <td><?= htmlspecialchars($date_he, ENT_QUOTES, 'UTF-8') ?></td>
            <td><?= number_format($price_val, 2) ?> <?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?></td>
            <td><?= $row_source_n !== null ? (int)$row_source_n : htmlspecialchars($row_source_s, ENT_QUOTES, 'UTF-8') ?></td>
          </tr>
        <?php endforeach; ?>
      </tbody>
    </table>
  </section>
<?php endif; ?>

<?php /* Cross-link to crop book (COMPONENTS.md §4 — market-to-book direction) */ ?>
<?php if ($book_slug !== ''):
  $href       = '/crop-book/' . $book_slug;
  $art_html   = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#icon-' . htmlspecialchars($icon_slug, ENT_QUOTES, 'UTF-8') . '"/></svg>';
  $big_text   = $book_label_he;
  $small_unit = '';
  $sub_text   = 'ספר גידולים — זנים, DTM, יבול';
  $direction  = 'market-to-book';
  include __DIR__ . '/../macros/crosslink.php';
endif; ?>

<?php /* Contrib strip at bottom (COMPONENTS.md §8) */
$context          = 'market.' . $slug;
$context_label_he = 'מחירון · ' . $name_he;
include __DIR__ . '/../macros/contrib_strip.php';
?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
