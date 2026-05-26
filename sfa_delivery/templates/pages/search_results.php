<?php
use SFA\Lib\Template;
$page_title = 'חיפוש';
ob_start();
?>
<section>
  <h1>חיפוש</h1>
  <form method="get" action="/search/">
    <input type="text" name="q" value="<?= htmlspecialchars((string)($q ?? ''), ENT_QUOTES, 'UTF-8') ?>">
    <button type="submit">חיפוש</button>
  </form>
  <?php if (!empty($q)): ?>
    <p>תוצאות עבור: <?= htmlspecialchars((string)$q, ENT_QUOTES, 'UTF-8') ?></p>
  <?php else: ?>
    <p>0 results</p>
  <?php endif; ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
