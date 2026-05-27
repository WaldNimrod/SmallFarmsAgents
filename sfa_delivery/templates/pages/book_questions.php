<?php
/**
 * book_questions.php — Route /crop-book/questions (CB1)
 *
 * Mandate §3 (route 6): `.gj-shell` + question cards.
 * COMPONENTS.md / crop-book-deep.css L57–96: `.cb-qgrid` + `.cb-qcard` BEM (LOD400 §0.5 wins).
 *
 * Variables expected from controller:
 *   $questions array — each item: ['slug','q_he','sub_he','count_he','href']
 *                      controller may also provide ['num'] for display ordinal
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$page_title = 'שאלות מובילות';
$page_sub   = 'ספר גידולים';
$active     = 'crop-book';
$back_url   = '/crop-book/';

$questions = $questions ?? [];

ob_start();
?>
<section class="cb-questions">
  <h2 class="cb-section-h">שאלות מובילות מהשטח</h2>

  <?php if (empty($questions)): ?>
    <p class="cb-qhint">שאלות יעלו לאחר ייבוא נתוני העונה.</p>
  <?php else: ?>
    <div class="cb-qgrid">
      <?php foreach ($questions as $i => $q): ?>
        <a class="cb-qcard" href="<?= $h((string)($q['href'] ?? '#')) ?>">
          <span class="cb-qcard__num"><?= (int)($q['num'] ?? ($i + 1)) ?></span>
          <h3 class="cb-qcard__q"><?= $h((string)($q['q_he'] ?? '')) ?></h3>
          <?php if (!empty($q['sub_he'])): ?>
            <p class="cb-qcard__sub"><?= $h((string)$q['sub_he']) ?></p>
          <?php endif; ?>
          <?php if (!empty($q['count_he'])): ?>
            <span class="cb-qcard__count"><?= $h((string)$q['count_he']) ?><small>תשובות</small></span>
          <?php endif; ?>
        </a>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>

  <?php
  $context          = 'book.questions';
  $context_label_he = 'ספר · שאלות מובילות';
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
