<?php
/**
 * book_entry.php — Route /crop-book/ (CB0)
 *
 * Mandate §3 (route 5): `.gj-shell` + 4 `mod-card`s (entry-path cards).
 * Per LOD400 v1.0.3 §0.5: COMPONENTS.md class names verbatim.
 * Uses `.cb-paths` wrapper (crop-book-deep.css L13) for layout per spec.
 *
 * WP-UI-patch03 (AC-U3-07): when controller passes $crops, renders a crop-card
 * grid using the existing crop_card.php macro below the nav cards.
 *
 * Variables expected from controller (all optional, defaults render):
 *   $crop_total      int   — total crop count (defaults to 66)
 *   $family_total    int   — total family count (defaults to 8)
 *   $variety_total   int   — total variety count (defaults to 242)
 *   $question_total  int   — total question count (defaults to 12)
 *   $crops           array — normalized crop list (each: slug, name_he, en_name,
 *                            icon_svg, icon_url, family_tag_he, dtm_days, category)
 */
use SFA\Lib\Template;

$page_title = 'ספר גידולים';
$page_sub   = 'מאגר ידע פתוח';
$active     = 'crop-book';

$crop_total     = (int)($crop_total     ?? 66);
$family_total   = (int)($family_total   ?? 8);
$variety_total  = (int)($variety_total  ?? 242);
$question_total = (int)($question_total ?? 12);

$paths = [
  [
    'slug'       => 'questions',
    'name_he'    => 'שאלות מובילות',
    'tier'       => 'open',
    'tier_color' => 'sun',
    'sub_he'     => 'מה מתחילים לזרוע השבוע?',
    'stat_he'    => $question_total . ' שאלות',
    'href'       => '/crop-book/questions',
    'icon_id'    => 'icon-leaf',
  ],
  [
    'slug'       => 'family',
    'name_he'    => 'משפחות בוטניות',
    'tier'       => 'open',
    'tier_color' => 'leaf',
    'sub_he'     => 'מה גדל ליד מה? איך מסובבים?',
    'stat_he'    => $family_total . ' משפחות',
    'href'       => '/crop-book/family',
    'icon_id'    => 'icon-seedling',
  ],
  [
    'slug'       => 'table',
    'name_he'    => 'טבלה מלאה',
    'tier'       => 'open',
    'tier_color' => 'soil',
    'sub_he'     => 'כל הגידולים — סינון, מיון, השוואה',
    'stat_he'    => $crop_total . ' גידולים',
    'href'       => '/crop-book/table',
    'icon_id'    => 'icon-tomato',
  ],
  [
    'slug'       => 'search',
    'name_he'    => 'חיפוש חופשי',
    'tier'       => 'open',
    'tier_color' => 'tomato',
    'sub_he'     => 'שם · משפחה · עברית · אנגלית',
    'stat_he'    => $variety_total . ' זנים',
    'href'       => '/crop-book/search',
    'icon_id'    => 'icon-cucumber',
  ],
];

$crops = is_array($crops ?? null) ? $crops : [];

ob_start();
?>
<section class="cb-entry">
  <h2 class="cb-section-h">איך תרצו להיכנס?</h2>
  <div class="cb-paths">
    <?php foreach ($paths as $module): ?>
      <?php include __DIR__ . '/../macros/module_card.php'; ?>
    <?php endforeach; ?>
  </div>
</section>
<?php if (!empty($crops)): ?>
<section class="cb-entry-crops">
  <h2 class="cb-section-h">כל הגידולים</h2>
  <div class="gj-cropgrid">
    <?php foreach ($crops as $crop): ?>
      <?php include __DIR__ . '/../macros/crop_card.php'; ?>
    <?php endforeach; ?>
  </div>
</section>
<?php endif; ?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
