<?php
use SFA\Lib\Template;
$page_title = 'כלים גדולים לחוות קטנות';
ob_start();
?>
<section>
  <h1>כלים גדולים לחוות קטנות</h1>
  <?php foreach (['open','beta','coming','paid','custom'] as $tierKey): ?>
    <h2><?= htmlspecialchars((string)($tiers[$tierKey]['label_he'] ?? $tierKey), ENT_QUOTES, 'UTF-8') ?></h2>
    <div class="modules-grid">
      <?php foreach (($modules ?? []) as $module): ?>
        <?php if (($module['tier'] ?? '') === $tierKey): ?>
          <?php include __DIR__ . '/../macros/module_card.php'; ?>
        <?php endif; ?>
      <?php endforeach; ?>
    </div>
  <?php endforeach; ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
