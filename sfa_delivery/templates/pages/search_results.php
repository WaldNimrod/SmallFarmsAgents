<?php
/**
 * search_results.php — Global search results page (route: /search?q=...)
 *
 * Mandate §3 contract: emits .gj-shell (mobile/desktop) + .gj-search (search bar
 *   inside the page head) + .gj-search__input + .gj-search__submit. The form
 *   present here is the explicitly-allowed GET search form — distinct from
 *   community.php LV-S-1 binding.
 *
 *   Also emits .search-page + .search-page__head + .search-page__meta +
 *   .search-page__empty + .search-section + .search-section__h +
 *   .search-section__grid, plus .gj-cropcard (via macros/crop_card.php) and
 *   .pcard (via macros/price_card.php).
 *
 * Architecture note: _layout.php includes both shell/mobile.php and
 *   shell/desktop.php. The page emits body content only.
 *
 * Variables consumed (provided by controller):
 *   $query           string  — the user's search query (raw string)
 *   $crop_results    array   — list of crop entries (slug, name_he, en_name,
 *                              family_tag_he, dtm_days, icon_svg) — see
 *                              macros/crop_card.php
 *   $product_results array   — list of product entries (slug, name_he, en_name,
 *                              unit_he, glyph_letter, price_current, currency,
 *                              price_median, price_min, price_max,
 *                              source_count, observation_count) — see
 *                              macros/price_card.php
 *
 * Shell variables set:
 *   $page_title = 'חיפוש'
 *   $active     = 'home'
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$query           = (string)($query ?? ($q ?? ''));
$crop_results    = is_array($crop_results    ?? null) ? $crop_results    : [];
$product_results = is_array($product_results ?? null) ? $product_results : [];

$total = count($crop_results) + count($product_results);

$page_title = 'חיפוש';
$active     = 'home';

ob_start();
?>
<section class="search-page">
  <header class="search-page__head">
    <form class="gj-search" action="/search" method="get" role="search">
      <input type="search" name="q" value="<?= $h($query) ?>" placeholder="חיפוש חופשי…" autofocus class="gj-search__input"/>
      <button type="submit" class="gj-search__submit" aria-label="חיפוש">⌕</button>
    </form>
    <?php if ($query !== ''): ?>
      <p class="search-page__meta">תוצאות עבור: <strong><?= $h($query) ?></strong> — <?= (int)$total ?> תוצאות</p>
    <?php endif; ?>
  </header>

  <?php if ($query === ''): ?>
    <p class="search-page__empty">הזינו מילת חיפוש כדי להתחיל.</p>
  <?php elseif (empty($crop_results) && empty($product_results)): ?>
    <p class="search-page__empty">לא נמצאו תוצאות עבור "<?= $h($query) ?>".</p>
  <?php else: ?>
    <?php if (!empty($crop_results)): ?>
      <section class="search-section">
        <h2 class="search-section__h">בספר הגידולים (<?= count($crop_results) ?>)</h2>
        <div class="search-section__grid">
          <?php foreach ($crop_results as $crop): include __DIR__ . '/../macros/crop_card.php'; endforeach; ?>
        </div>
      </section>
    <?php endif; ?>
    <?php if (!empty($product_results)): ?>
      <section class="search-section">
        <h2 class="search-section__h">במחירון (<?= count($product_results) ?>)</h2>
        <div class="search-section__grid">
          <?php foreach ($product_results as $product): include __DIR__ . '/../macros/price_card.php'; endforeach; ?>
        </div>
      </section>
    <?php endif; ?>
  <?php endif; ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
