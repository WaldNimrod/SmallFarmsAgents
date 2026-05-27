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

// Asset version: file mtime of the LAST-loaded CSS in the chain. Cheap, deploy-tied, CF-cache-bust friendly.
$asset_ver = $asset_ver ?? @filemtime(__DIR__ . '/../public_assets/css/desktop-extras.css') ?: 'build';
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

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;600;700;800&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="/public_assets/css/tokens.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/gj.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/hub.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/community.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/crop-book-deep.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/desktop.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/desktop-extras.css?v=<?= $h($asset_ver) ?>">

<script defer src="/public_assets/js/sfa.js?v=<?= $h($asset_ver) ?>"></script>
</head>
<body class="sfa-app">
<?php include __DIR__ . '/shell/mobile.php'; ?>
<?php include __DIR__ . '/shell/desktop.php'; ?>
</body>
</html>
