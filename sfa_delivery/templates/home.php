<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = 'בית';
$active = 'home';
ob_start();
?>

<section class="hero">
  <h1>שני כלים לחקלאים קטנים</h1>
  <p class="lead">
    <strong>ספר גידולים</strong> — מאגר ידע חופשי על גידולים, זנים, אורכי מחזורים, אופן גידול ומקורות תיעוד.<br>
    <strong>מחירון</strong> — מעקב יומי אחר מחירי תוצרת חקלאית ממקורות שיווק שונים.
  </p>
  <div class="hero-cta">
    <a class="btn btn-primary" href="/crop-book/">לספר הגידולים</a>
    <a class="btn" href="/market/">למחירון</a>
  </div>
</section>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
