<?php
use SFA\Lib\Template;

$h = [Template::class, 'h'];
$page_title       = $page_title       ?? 'Small Farms Agents';
$page_sub         = $page_sub         ?? 'חקלאות קטנה';
$page_description = $page_description ?? 'Small Farms Agents — אינדקס פתוח של גידולים ומחירי שוק קהילתי';
$active           = $active           ?? '';
$stats            = $stats            ?? [];
$status           = $status           ?? 'fresh';
$foot_text        = $foot_text        ?? ('עודכן ' . date('H:i'));
$body_html        = $content          ?? ($body_html ?? '');
$canonical_path   = $canonical_path   ?? ($_SERVER['REQUEST_URI'] ?? '/');
// Strip query string from canonical
$canonical_path = strtok($canonical_path, '?');
$og_image_url   = $og_image_url ?? 'https://sfa.nimrod.bio/public_assets/img/og-default.webp';

// Asset version: max(filemtime) across ALL CSS + the JS bundle.
// Previous version used only desktop-extras.css mtime, which left stale
// cache when other CSS files were updated (Cloudflare keeps serving old
// hub.css if its ?v= query didn't change). Now any file in the asset
// chain bumps the buster.
if (!isset($asset_ver)) {
    $_css_dir = __DIR__ . '/../public_assets/css';
    $_js_file = __DIR__ . '/../public_assets/js/sfa.js';
    $_mtimes  = [];
    foreach (['tokens', 'gj', 'hub', 'community', 'crop-book-deep', 'crop-book-v1', 'desktop-extras', 'classb'] as $_n) {
        $_mt = @filemtime($_css_dir . '/' . $_n . '.css');
        if ($_mt) { $_mtimes[] = $_mt; }
    }
    $_mt = @filemtime($_js_file);
    if ($_mt) { $_mtimes[] = $_mt; }
    $_mt = @filemtime(__DIR__ . '/../public_assets/js/crop-book-v1.js');
    if ($_mt) { $_mtimes[] = $_mt; }
    $_mt = @filemtime(__DIR__ . '/../public_assets/js/classb.js');
    if ($_mt) { $_mtimes[] = $_mt; }
    $asset_ver = $_mtimes ? max($_mtimes) : 'build';
}

// Class B routes: /, /market/*, /search, /community, /about, /account
// (not /crop-book/* and not /calc/* which are Class A only)
$_path = $canonical_path ?? '/';
$_is_classb = (
    $_path === '/' ||
    str_starts_with($_path, '/market') ||
    $_path === '/search' ||
    $_path === '/community' ||
    $_path === '/about' ||
    str_starts_with($_path, '/account')
);
?><!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= $h($page_title) ?> · SFA</title>
<meta name="description" content="<?= $h($page_description) ?>">

<meta property="og:title" content="<?= $h($page_title) ?>">
<meta property="og:description" content="<?= $h($page_description) ?>">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Small Farms Agents">
<meta property="og:locale" content="he_IL">
<meta property="og:image" content="<?= $h($og_image_url) ?>">
<link rel="canonical" href="https://sfa.nimrod.bio<?= $h($canonical_path) ?>">
<link rel="icon" type="image/png" sizes="32x32" href="/public_assets/img/favicon-32.png?v=<?= $h($asset_ver) ?>">
<link rel="apple-touch-icon" sizes="180x180" href="/public_assets/img/apple-touch-icon.png?v=<?= $h($asset_ver) ?>">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;600;700;800&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="/public_assets/css/tokens.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/gj.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/hub.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/community.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/crop-book-deep.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/crop-book-v1.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/desktop-extras.css?v=<?= $h($asset_ver) ?>">
<?php if ($_is_classb): ?>
<link rel="stylesheet" href="/public_assets/css/classb.css?v=<?= $h($asset_ver) ?>">
<?php endif; ?>

<script defer src="/public_assets/js/sfa.js?v=<?= $h($asset_ver) ?>"></script>
<?php if (isset($active) && in_array($active, ['crop-book', 'calc'], true)): ?>
<script defer src="/public_assets/js/crop-book-v1.js?v=<?= $h($asset_ver) ?>"></script>
<?php endif; ?>
<?php if ($_is_classb): ?>
<script defer src="/public_assets/js/crop-book-v1.js?v=<?= $h($asset_ver) ?>"></script>
<script defer src="/public_assets/js/classb.js?v=<?= $h($asset_ver) ?>"></script>
<?php endif; ?>
</head>
<body class="sfa-app">
<?php /* Inline the SVG sprite once per page. Chrome (and others) do not resolve
       <use href="external.svg#id"> reliably without CORS headers from the asset
       host — the sprite ends up with empty bboxes despite a 200 fetch. Inlining
       via readfile preserves a single sprite definition and lets every <use
       href="#icon-X"> in macros/templates resolve synchronously. */
@readfile(__DIR__ . '/../public_assets/img/icons.svg');
?>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="sfa-logo" viewBox="0 0 48 48">
  <rect x="1.5" y="1.5" width="45" height="45" rx="12" fill="#3a4d22"/>
  <g fill="#9bb172"><rect x="12" y="34" width="6" height="4" rx="1.2"/><rect x="21" y="34" width="6" height="4" rx="1.2"/><rect x="30" y="34" width="6" height="4" rx="1.2"/></g>
  <path d="M24 33 V18.5" stroke="#f6f1e3" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M24 24.5 C 19 24.5 15 21.5 14 16.5 C 20 16.5 24 19.5 24 24.5 Z" fill="#f6f1e3"/>
  <path d="M24 21.5 C 29 21.5 33 18.5 34 13.5 C 28 13.5 24 16.5 24 21.5 Z" fill="#cfe0b0"/>
  <circle cx="24" cy="15.5" r="2.4" fill="#d39a32"/>
</symbol></svg>
<div class="sh">
  <div class="sh__bar">
    <a class="sh__mark" href="/" aria-label="SFA — דף הבית"><svg><use href="#sfa-logo"/></svg></a>
    <div class="sh__name">SFA<small><?= $h($page_sub) ?></small></div>
    <nav class="sh__nav">
      <a class="<?= $active==='crop-book' ? 'is-active' : '' ?>" href="/crop-book/"><span class="g">▤</span>ספר גידולים</a>
      <a class="is-calc <?= $active==='calc' ? 'is-active' : '' ?>" href="/calc/"><span class="g">∑</span>מחשבון</a>
      <a class="is-market <?= $active==='market' ? 'is-active' : '' ?>" href="/market/"><span class="g">₪</span>מחירון</a>
    </nav>
    <span class="sh__nav__sp"></span>
    <?php /* Class B: inline search (≥760px); collapses to icon below that */ ?>
    <form class="sh__search" action="/search" method="get" role="search" aria-label="חיפוש">
      <span class="ic">⌕</span>
      <input type="search" name="q" placeholder="חיפוש גידולים ומחירים…" aria-label="שדה חיפוש">
    </form>
    <a class="sh__icon" href="/search" title="חיפוש" aria-label="חיפוש">⌕</a>
    <a class="sh__acct <?= $active==='account' ? 'is-active' : '' ?>" href="/account" aria-label="חשבון"><span class="av">◔</span>חשבון</a>
  </div>
  <div class="sh__body"><?= $body_html ?></div>
  <nav class="sh__nav--mobile" aria-label="ניווט ראשי">
    <a class="<?= $active==='crop-book' ? 'is-active' : '' ?>" href="/crop-book/"><span class="g">▤</span>ספר</a>
    <a class="is-calc <?= $active==='calc' ? 'is-active' : '' ?>" href="/calc/"><span class="g">∑</span>מחשבון</a>
    <a class="is-market <?= $active==='market' ? 'is-active' : '' ?>" href="/market/"><span class="g">₪</span>מחירון</a>
    <a class="<?= $active==='account' ? 'is-active' : '' ?>" href="/account"><span class="g">◔</span>חשבון</a>
  </nav>
  <footer class="sh__foot">
    <span class="dot"></span>
    <a href="/">SFA</a> · קוד פתוח · קהילתי ·
    <a href="/about">על הכלים</a> ·
    <a href="/community">קהילה</a>
  </footer>
</div>
</body>
</html>
