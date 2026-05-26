<?php
use SFA\Lib\Template;
$page_title = (string)($crop['hebrew_name'] ?? 'גידול');
ob_start();
?>
<section>
  <h1><?= htmlspecialchars((string)($crop['hebrew_name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></h1>
  <p><?= htmlspecialchars((string)($crop['scientific_name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></p>
  <h2>זנים</h2>
  <ul>
    <?php foreach (($varieties ?? []) as $variety): ?>
      <li>
        <a href="/crop-book/<?= htmlspecialchars((string)$crop['slug'], ENT_QUOTES, 'UTF-8') ?>/variety/<?= htmlspecialchars((string)($variety['slug'] ?? ''), ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$variety['name'], ENT_QUOTES, 'UTF-8') ?></a>
      </li>
    <?php endforeach; ?>
  </ul>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
