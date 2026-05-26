<?php
use SFA\Lib\Template;
$page_title = (string)($variety['name'] ?? 'זן');
ob_start();
?>
<section>
  <h1><?= htmlspecialchars((string)($variety['name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></h1>
  <p>גידול: <a href="/crop-book/<?= htmlspecialchars((string)$crop['slug'], ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$crop['hebrew_name'], ENT_QUOTES, 'UTF-8') ?></a></p>
  <pre><?= htmlspecialchars(json_encode($variety, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT), ENT_QUOTES, 'UTF-8') ?></pre>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
