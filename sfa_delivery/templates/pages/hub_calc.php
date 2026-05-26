<?php
use SFA\Lib\Template;
$page_title = 'מחשבון לחקלאי';
$wa = !empty($contact['whatsapp']) ? ('https://wa.me/' . preg_replace('/\D+/', '', (string)$contact['whatsapp'])) : '#';
ob_start();
?>
<section>
  <h1>מחשבון לחקלאי</h1>
  <p>בטא · בפיתוח</p>
  <p>עמוד זה נמצא בפיתוח מתקדם וייפתח בהמשך.</p>
  <a href="<?= htmlspecialchars($wa, ENT_QUOTES, 'UTF-8') ?>">WhatsApp</a>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
