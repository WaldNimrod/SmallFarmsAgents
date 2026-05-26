<?php
use SFA\Lib\Template;

$h = [Template::class, 'h'];
$page_title = $page_title ?? 'Small Farms Agents';
$asset_ver = $asset_ver ?? 'build';
?><!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= $h($page_title) ?> · SFA</title>
<meta name="description" content="Small Farms Agents UI shell">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&family=Frank+Ruhl+Libre:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/public_assets/css/tokens.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/gj.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/hub.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/community.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/crop-book-deep.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/desktop.css?v=<?= $h($asset_ver) ?>">
<link rel="stylesheet" href="/public_assets/css/desktop-extras.css?v=<?= $h($asset_ver) ?>">
<script defer src="/public_assets/js/sfa.js?v=<?= $h($asset_ver) ?>"></script>
</head>
<body>
<?php include __DIR__ . '/shell/mobile.php'; ?>
<?php include __DIR__ . '/shell/desktop.php'; ?>
</body>
</html>
