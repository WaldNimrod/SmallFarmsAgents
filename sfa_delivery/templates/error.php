<?php
use SFA\Lib\Template;
$page_title = 'שגיאה';
ob_start();
?>
<section>
  <h1><?= htmlspecialchars((string)($code ?? 500), ENT_QUOTES, 'UTF-8') ?></h1>
  <p><?= htmlspecialchars((string)($message ?? 'אירעה שגיאה'), ENT_QUOTES, 'UTF-8') ?></p>
  <a href="/">חזרה לדף הבית</a>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
