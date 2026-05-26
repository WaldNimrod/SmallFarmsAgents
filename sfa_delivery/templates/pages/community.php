<?php
use SFA\Lib\Template;
$page_title = 'קהילה';
$wa = !empty($contact['whatsapp']) ? ('https://wa.me/' . preg_replace('/\D+/', '', (string)$contact['whatsapp'])) : '#';
ob_start();
?>
<section>
  <h1>קהילה</h1>
  <p>דף קהילה סטטי בלבד בשלב זה. אין טפסים ואין כתיבות למסד נתונים.</p>
  <a href="<?= htmlspecialchars($wa, ENT_QUOTES, 'UTF-8') ?>">הצטרפו ב-WhatsApp</a>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
