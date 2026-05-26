<?php
use SFA\Lib\Template;
$page_title = 'חיפוש בספר הגידולים';
ob_start();
?>
<section>
  <h1>חיפוש בספר הגידולים</h1>
  <form method="get" action="/crop-book/search/">
    <input type="text" name="q" value="<?= htmlspecialchars((string)($q ?? ''), ENT_QUOTES, 'UTF-8') ?>">
    <button type="submit">חיפוש</button>
  </form>
  <ul>
    <?php foreach (($items ?? []) as $item): ?>
      <li><a href="/crop-book/<?= htmlspecialchars((string)$item['slug'], ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$item['hebrew_name'], ENT_QUOTES, 'UTF-8') ?></a></li>
    <?php endforeach; ?>
  </ul>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
