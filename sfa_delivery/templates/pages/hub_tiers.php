<?php
use SFA\Lib\Template;
$page_title = 'איך זה עובד';
ob_start();
?>
<section>
  <h1>איך זה עובד</h1>
  <ul>
    <?php foreach (($tiers ?? []) as $tier): ?>
      <li><?= htmlspecialchars((string)($tier['label_he'] ?? ''), ENT_QUOTES, 'UTF-8') ?> — <?= htmlspecialchars((string)($tier['description_he'] ?? ''), ENT_QUOTES, 'UTF-8') ?></li>
    <?php endforeach; ?>
  </ul>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
