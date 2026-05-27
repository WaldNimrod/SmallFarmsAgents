<?php
declare(strict_types=1);
require __DIR__ . '/../vendor/autoload.php';

// phpunit.xml env settings propagate via getenv(), but $_ENV is not auto-populated.
// Bridge them so the app's Db / Hmac / Logger pick them up.
foreach (['APP_ENV_FILE','APP_ENV','APP_DEBUG','DB_DSN','DB_NAME','DB_USER','INGEST_HMAC_SECRET','LOG_LEVEL'] as $k) {
    $v = getenv($k);
    if ($v !== false) {
        $_ENV[$k] = $v;
    }
}
