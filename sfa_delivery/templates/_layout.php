<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = $page_title ?? 'Small Farms Agents';
?><!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= $h($page_title) ?> · Small Farms Agents</title>
<link rel="stylesheet" href="/public_assets/css/site.css?v=1">
<meta name="description" content="ספר גידולים וחישובי מחירים לחקלאים בישראל">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">חקלאות קטנה</a>
    <nav class="nav">
      <a href="/crop-book/" class="<?= ($active ?? '') === 'crop_book' ? 'is-active' : '' ?>">ספר גידולים</a>
      <a href="/market/"    class="<?= ($active ?? '') === 'market'    ? 'is-active' : '' ?>">מחירון</a>
    </nav>
  </div>
</header>

<main class="site-main">
  <div class="wrap">
    <?= $content ?? '' ?>
  </div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <small>נתוני מקור: סוכני סריקה של mezoo. עודכן: <?= $h(date('Y-m-d H:i')) ?> (UTC).</small>
  </div>
</footer>
</body>
</html>
