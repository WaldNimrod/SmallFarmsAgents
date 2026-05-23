<?php
declare(strict_types=1);

// Front controller for sfa.nimrod.bio
// SFA-S003-P003-WP-2 — Slim 4 + PDO + MySQL

require __DIR__ . '/vendor/autoload.php';

$app = SFA\Bootstrap::createApp();
(require __DIR__ . '/app/routes.php')($app);
$app->run();
