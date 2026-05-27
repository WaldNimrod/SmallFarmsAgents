<?php
/**
 * book_table.php — Route /crop-book/table (CB3 / D3)
 *
 * Mandate §3 (route 8): `.gj-shell` (mobile) + `.dt-shell` `.dt-table` (desktop).
 * `<th scope="col">` per column. `data-sort` attribute on each <th> drives sfa.js Behavior 3.
 *
 * COMPONENTS.md class names (LOD400 v1.0.3 §0.5):
 *   Mobile compact list: `.cb-table` / `.cb-table__head` / `.cb-table__row` / `.cb-table__name`
 *                        / `.cb-table__fam` / `.cb-table__num`  (crop-book-deep.css L140–172)
 *   Desktop data grid: `.dt-table` (desktop.css)
 *
 * Both renderings share the same source `$crops` array and the same `data-sort` keys so
 * client-side sort in sfa.js works on whichever DOM the viewport surfaces.
 *
 * Variables expected from controller:
 *   $crops array — each item: [
 *     'slug', 'name_he', 'family_he', 'dtm_days' (int|null), 'yield_kg_per_m2' (float|null),
 *     'best_season' (str), 'source_count' (int|null)
 *   ]
 *   $category string (optional) — filter label
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$page_title = 'טבלת גידולים';
$page_sub   = 'ספר גידולים · כל הגידולים';
$active     = 'crop-book';
$back_url   = '/crop-book/';

$crops    = $crops    ?? [];
$category = $category ?? '';

$fmt_dtm = function ($v): string {
    if ($v === null || $v === '' || (int)$v === -32768) return '—';
    return (string)(int)$v;
};
$fmt_yield = function ($v): string {
    if ($v === null || $v === '') return '—';
    return number_format((float)$v, 1);
};

ob_start();
?>
<section class="cb-table-page">
  <h2 class="cb-section-h">טבלת גידולים מלאה</h2>

  <?php if ($category !== ''): ?>
    <p class="cb-qhint">פילטר: <?= $h($category) ?></p>
  <?php endif; ?>

  <?php if (empty($crops)): ?>
    <p class="cb-qhint">טבלת הגידולים תיטען לאחר ייבוא נתוני העונה.</p>
  <?php else: ?>

    <!-- Mobile compact list (.cb-table) -->
    <div class="cb-table">
      <div class="cb-table__head" role="row">
        <span role="columnheader" data-sort="name_he">שם</span>
        <span role="columnheader" data-sort="family_he">משפחה</span>
        <span role="columnheader" data-sort="dtm_days">DTM</span>
        <span role="columnheader" data-sort="yield_kg_per_m2">יבול</span>
      </div>
      <?php foreach ($crops as $crop): ?>
        <a class="cb-table__row"
           href="/crop-book/<?= $h((string)($crop['slug'] ?? '')) ?>"
           data-name_he="<?= $h((string)($crop['name_he'] ?? '')) ?>"
           data-family_he="<?= $h((string)($crop['family_he'] ?? '')) ?>"
           data-dtm_days="<?= $h($fmt_dtm($crop['dtm_days'] ?? null)) ?>"
           data-yield_kg_per_m2="<?= $h($fmt_yield($crop['yield_kg_per_m2'] ?? null)) ?>">
          <span class="cb-table__name"><?= $h((string)($crop['name_he'] ?? '')) ?></span>
          <span class="cb-table__fam"><?= $h((string)($crop['family_he'] ?? '')) ?></span>
          <span class="cb-table__num"><?= $h($fmt_dtm($crop['dtm_days'] ?? null)) ?></span>
          <span class="cb-table__num cb-table__num--accent"><?= $h($fmt_yield($crop['yield_kg_per_m2'] ?? null)) ?></span>
        </a>
      <?php endforeach; ?>
    </div>

    <!-- Desktop data grid (.dt-table) -->
    <table class="dt-table">
      <thead>
        <tr>
          <th scope="col" data-sort="name_he">שם</th>
          <th scope="col" data-sort="family_he">משפחה</th>
          <th scope="col" data-sort="dtm_days">DTM (ימים)</th>
          <th scope="col" data-sort="yield_kg_per_m2">יבול (ק״ג/מ״ר)</th>
          <th scope="col" data-sort="best_season">עונה מיטבית</th>
          <th scope="col" data-sort="source_count">מקורות</th>
          <th scope="col"><span class="visually-hidden">פעולות</span></th>
        </tr>
      </thead>
      <tbody>
        <?php foreach ($crops as $crop): ?>
          <tr>
            <td><?= $h((string)($crop['name_he'] ?? '')) ?></td>
            <td><?= $h((string)($crop['family_he'] ?? '')) ?></td>
            <td class="cb-table__num"><?= $h($fmt_dtm($crop['dtm_days'] ?? null)) ?></td>
            <td class="cb-table__num"><?= $h($fmt_yield($crop['yield_kg_per_m2'] ?? null)) ?></td>
            <td><?= $h((string)($crop['best_season'] ?? '—')) ?></td>
            <td class="cb-table__num"><?= isset($crop['source_count']) ? (int)$crop['source_count'] : '—' ?></td>
            <td><a href="/crop-book/<?= $h((string)($crop['slug'] ?? '')) ?>">פרטים</a></td>
          </tr>
        <?php endforeach; ?>
      </tbody>
    </table>

  <?php endif; ?>

  <?php
  $context          = 'book.table';
  $context_label_he = 'ספר · טבלת גידולים';
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
