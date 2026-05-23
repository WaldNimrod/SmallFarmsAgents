<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = "שגיאה " . ($code ?? 500);
ob_start();
?>
<section class="error">
  <h1>שגיאה <?= (int)($code ?? 500) ?></h1>
  <p class="lead"><?= $h($message ?? 'אירעה שגיאה') ?></p>
  <p><a class="btn" href="/">חזרה לדף הבית</a></p>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
