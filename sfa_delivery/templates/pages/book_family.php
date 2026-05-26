<?php
use SFA\Lib\Template;
$page_title = 'משפחות גידול';
ob_start();
?>
<section>
  <h1>משפחות גידול</h1>
  <ul>
    <?php foreach (($families ?? []) as $family): ?>
      <li><?= htmlspecialchars((string)$family['family_name_he'], ENT_QUOTES, 'UTF-8') ?> (<?= (int)$family['total'] ?>)</li>
    <?php endforeach; ?>
  </ul>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
