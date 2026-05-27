<?php
/**
 * book_search.php — Route /crop-book/search (CB4)
 *
 * Mandate §3 (route 9): `.gj-shell` + `.gj-search` (form) plus result list.
 * COMPONENTS.md: results are `.gj-cropcard` (via crop_card macro). Form classes
 * `.cb-search-form` / `.cb-search-input` per crop-book-deep.css L175–251 (LOD400 §0.5).
 *
 * Variables expected from controller:
 *   $query    string — current ?q= value
 *   $results  array  — each item conforms to crop_card macro contract:
 *                      ['slug','name_he','en_name','family_tag_he','dtm_days','icon_svg']
 *                      (controller may set icon_svg using /public_assets/img/icons.svg sprite)
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$page_title = 'חיפוש בספר';
$page_sub   = 'שם · משפחה · עברית · אנגלית';
$active     = 'crop-book';
$back_url   = '/crop-book/';

$query   = (string)($query   ?? ($q ?? ''));
$results = $results ?? ($items ?? []);

ob_start();
?>
<section class="cb-search">
  <h2 class="cb-section-h">חיפוש בספר הגידולים</h2>

  <form class="cb-search-form gj-search" action="/crop-book/search" method="get" role="search">
    <fieldset>
      <legend>חיפוש חופשי</legend>
      <input
        type="search"
        name="q"
        class="cb-search-input"
        placeholder="חפש שם גידול, משפחה, או זן…"
        value="<?= $h($query) ?>"
        autocomplete="off">
    </fieldset>
    <div class="cb-search-submit">
      <button type="submit">חפש <strong>↵</strong></button>
    </div>
  </form>

  <?php if ($query === ''): ?>
    <p class="cb-search-tip">הקלידו טקסט בעברית או באנגלית כדי לחפש בספר הגידולים.</p>
  <?php elseif (empty($results)): ?>
    <p class="cb-search-tip">לא נמצאו תוצאות עבור «<?= $h($query) ?>».</p>
  <?php else: ?>
    <p class="cb-search-tip"><?= (int)count($results) ?> תוצאות עבור «<?= $h($query) ?>»</p>
    <div class="cb-search-results">
      <?php foreach ($results as $crop): ?>
        <?php include __DIR__ . '/../macros/crop_card.php'; ?>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>

  <?php
  $context          = 'book.search';
  $context_label_he = 'ספר · חיפוש';
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
