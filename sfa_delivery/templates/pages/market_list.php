<?php
/**
 * market_list.php — Route /market/
 *
 * Per MANDATE_WP-UI-RE-BUILD §3 (route 12) + LOD400 v1.0.3 §0.5 + COMPONENTS.md §5 + §10.
 *
 * Variables expected from controller (MarketViewController::index):
 *   $products   — array<array{slug,hebrew_name,category,unit,last_price,last_price_date,freshness_days,...}>
 *   $categories — (optional) array<array{slug,name_he}> — facet chips. May be absent.
 *   $current_category — (optional) string — active facet slug.
 *
 * BEM contract (LOD400 §0.5 → COMPONENTS.md names verbatim):
 *   .mk-disclaimer (via market_disclaimer.php macro)
 *   .mk-chips, .mk-chip, .is-active
 *   .mk-list, .mk-grid, .mk-empty
 *   .pcard etc. (via price_card.php macro)
 *   .contrib-strip (via contrib_strip.php macro)
 *
 * Note: MANDATE §3 cited `.gj-row` for the per-product layout. Per LOD400 §0.5,
 * COMPONENTS.md is SSoT and §5 defines `.pcard`. We emit `.pcard` via macro.
 */
use SFA\Lib\Template;

$page_title = 'מחירון';
$page_sub   = 'מחירי שוק קהילתיים';
$active     = 'market';

$products         = $products         ?? [];
$categories       = $categories       ?? [];
$current_category = $current_category ?? '';

ob_start();
?>
<?php /* Disclaimer at top — MANDATORY on every market view (COMPONENTS.md §10) */ ?>
<?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>

<?php /* Optional category facet chips */ ?>
<?php if (!empty($categories)): ?>
  <div class="mk-chips" role="group" aria-label="סינון לפי קטגוריה">
    <a class="mk-chip<?= empty($current_category) ? ' is-active' : '' ?>" href="/market/">הכל</a>
    <?php foreach ($categories as $cat):
      $cat_slug = (string)($cat['slug'] ?? $cat['category'] ?? '');
      $cat_name = (string)($cat['name_he'] ?? $cat['category'] ?? '');
      $is_active = ($current_category === $cat_slug);
    ?>
      <a class="mk-chip<?= $is_active ? ' is-active' : '' ?>" href="/market/?category=<?= urlencode($cat_slug) ?>"><?= htmlspecialchars($cat_name, ENT_QUOTES, 'UTF-8') ?></a>
    <?php endforeach; ?>
  </div>
<?php endif; ?>

<?php /* Product list — pcard grid (COMPONENTS.md §5) */ ?>
<section class="mk-list">
  <?php if (empty($products)): ?>
    <p class="mk-empty">אין נתונים זמינים כרגע.</p>
  <?php else: ?>
    <div class="mk-grid">
      <?php foreach ($products as $row):
        // Map controller row (hebrew_name/last_price/...) to price_card contract
        // (name_he/price_current/...). Defensive defaults handle missing fields.
        $name_he = (string)($row['name_he'] ?? $row['hebrew_name'] ?? '');
        $product = [
          'slug'              => (string)($row['slug']              ?? ''),
          'name_he'           => $name_he,
          'en_name'           => (string)($row['en_name']           ?? ''),
          'unit_he'           => (string)($row['unit_he']           ?? $row['unit'] ?? ''),
          'glyph_letter'      => (string)($row['glyph_letter']      ?? mb_substr($name_he, 0, 1, 'UTF-8')),
          'price_current'     => (float) ($row['price_current']     ?? $row['last_price'] ?? 0.0),
          'currency'          => (string)($row['currency']          ?? '₪'),
          'price_median'      => (float) ($row['price_median']      ?? $row['last_price'] ?? 0.0),
          'price_min'         => (float) ($row['price_min']         ?? $row['last_price'] ?? 0.0),
          'price_max'         => (float) ($row['price_max']         ?? $row['last_price'] ?? 0.0),
          'source_count'      => (int)   ($row['source_count']      ?? 0),
          'observation_count' => (int)   ($row['observation_count'] ?? 0),
        ];
        include __DIR__ . '/../macros/price_card.php';
      endforeach; ?>
    </div>
  <?php endif; ?>
</section>

<?php /* Contrib strip at bottom (COMPONENTS.md §8) */
$context          = 'market.list';
$context_label_he = 'מחירון';
include __DIR__ . '/../macros/contrib_strip.php';
?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
