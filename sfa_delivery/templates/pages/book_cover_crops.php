<?php
/**
 * book_cover_crops.php — Route /crop-book/cover-crops (AC-U4-02)
 *
 * Renders the global cover-crop reference list from the cover_crops table.
 * Tolerates an empty list (table not yet populated by sub-agent A).
 *
 * Variables expected from CropBookViewController::coverCrops():
 *   $cover_crops  array  — list of {name_he, name_en, category, sow_window,
 *                          total_days_garden, survives_winter, notes}
 */
use SFA\Lib\Template;

$page_title = 'גידולי כיסוי';
$page_sub   = 'ספר גידולים · כיסוי';
$active     = 'crop-book';
$back_url   = '/crop-book/';

$cover_crops = is_array($cover_crops ?? null) ? $cover_crops : [];

// Group by category for cleaner display.
$by_category = [];
foreach ($cover_crops as $cc) {
    $cat = (string)($cc['category'] ?? 'כללי');
    $by_category[$cat][] = $cc;
}

ob_start();
?>
<section class="cb-cover-header">
  <h2 class="cb-section-h">גידולי כיסוי — מדריך עזר</h2>
  <p class="cb-cover-intro">גידולי כיסוי משפרים את מבנה הקרקע, מפחיתים עשבייה ומקבעים חנקן.
  הרשימה הבאה מבוססת על ניסיון שדה ומקורות אגרונומיים.</p>
</section>

<?php if (empty($cover_crops)): ?>
<section class="cb-cover-empty">
  <p class="cb-empty-state">הנתונים בטעינה — הרשימה תופיע כאן בקרוב.</p>
</section>
<?php else: ?>
  <?php foreach ($by_category as $cat => $items): ?>
  <section class="cb-cover-group">
    <h3 class="cb-cover-group__title"><?= htmlspecialchars($cat, ENT_QUOTES, 'UTF-8') ?></h3>
    <div class="cb-cover-table-wrap">
      <table class="cb-cover-table">
        <thead>
          <tr>
            <th scope="col">שם עברי</th>
            <th scope="col">שם אנגלי</th>
            <th scope="col">חלון זריעה</th>
            <th scope="col">ימים לגינה</th>
            <th scope="col">שורד חורף</th>
            <th scope="col">הערות</th>
          </tr>
        </thead>
        <tbody>
          <?php foreach ($items as $cc):
            $name_he          = (string)($cc['name_he']           ?? '');
            $name_en          = (string)($cc['name_en']           ?? '');
            $sow_window       = (string)($cc['sow_window']        ?? '—');
            $total_days       = $cc['total_days_garden'] !== null ? (int)$cc['total_days_garden'] : null;
            $survives_winter  = !empty($cc['survives_winter']);
            $notes            = (string)($cc['notes']             ?? '');
          ?>
          <tr>
            <td class="cb-cover-table__name-he"><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></td>
            <td class="cb-cover-table__name-en"><?= htmlspecialchars($name_en, ENT_QUOTES, 'UTF-8') ?></td>
            <td><?= htmlspecialchars($sow_window, ENT_QUOTES, 'UTF-8') ?></td>
            <td class="cb-cover-table__days"><?= $total_days !== null ? $total_days : '—' ?></td>
            <td class="cb-cover-table__winter"><?= $survives_winter ? '✓' : '—' ?></td>
            <td class="cb-cover-table__notes"><?= htmlspecialchars($notes, ENT_QUOTES, 'UTF-8') ?></td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  </section>
  <?php endforeach; ?>
<?php endif; ?>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
