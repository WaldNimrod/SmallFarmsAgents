<?php
use SFA\Lib\Template;
$page_title = 'שאלות לגידול';
ob_start();
?>
<section>
  <h1>שאלות לגידול</h1>
  <?php foreach (($questions ?? []) as $question): ?>
    <article>
      <h3><?= htmlspecialchars((string)$question['title'], ENT_QUOTES, 'UTF-8') ?></h3>
      <a href="/crop-book/table/?category=<?= htmlspecialchars((string)$question['category'], ENT_QUOTES, 'UTF-8') ?>">מעבר לטבלה</a>
    </article>
  <?php endforeach; ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
