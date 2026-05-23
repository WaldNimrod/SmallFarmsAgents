# sfa_delivery — sfa.nimrod.bio Slim PHP app

**Canonical docs:**
- Architecture: `../documentation/02-architecture/sfa-delivery-tier.md`
- Schema: `../documentation/03-data-and-schema/sfa-mysql-mirror.md`
- WP spec: `../_aos/work_packages/S003/SFA-S003-P003-WP-2/LOD400_spec.md`

## Layout

```
sfa_delivery/
├── index.php              front controller (Slim bootstrap)
├── .htaccess              rewrites + path blocks
├── composer.json          Slim 4 + Monolog + phpdotenv + PHP-DI
├── .env.example           env template (real .env created on uPress)
├── app/
│   ├── bootstrap.php      app factory, container, error handler
│   ├── routes.php         /api/v1/* routes
│   ├── Controllers/       Health, Ingest, Crops, Products
│   ├── Middleware/        HmacAuth, JsonError, JsonResponse
│   └── Lib/               Db (PDO), Hmac, Logger (Monolog)
├── migrations/
│   ├── 001_schema_migrations.sql   plumbing tracker + ingest_log
│   ├── 002_crops.sql               crops + crop_varieties
│   ├── 003_products.sql            products + product_prices
│   └── migrate.php                 CLI runner (also web-invocable via /admin/migrate)
├── tests/
│   ├── HmacTest.php                unit (7 cases)
│   └── IngestSmokeTest.php         integration (sqlite-backed)
├── phpunit.xml
├── public_assets/                  static CSS/JS (populated in WP-3)
└── logs/                           Monolog rotating file
```

## Local dev

```bash
composer install
composer test           # phpunit (uses sqlite::memory:)
php -S localhost:8080   # ad-hoc dev server (index.php as router via .htaccess emulation: php -S localhost:8080 -t .)
```

## Deploy to uPress (`sfa.nimrod.bio`)

```bash
# 1. Production install (no dev deps)
composer install --no-dev --optimize-autoloader

# 2. Bundle (excludes test/dev files)
tar czf /tmp/sfa-bundle.tgz \
  --exclude='./.git' --exclude='./tests' --exclude='./phpunit.xml' \
  --exclude='./.env' --exclude='./logs/*' --exclude='./.env.*' \
  index.php .htaccess composer.json composer.lock vendor app migrations public_assets README.md

# 3. Extract locally to staging dir, then FTPS mirror to site root
mkdir -p /tmp/sfa-staged && tar xzf /tmp/sfa-bundle.tgz -C /tmp/sfa-staged

# 4. Deploy (uses creds from /Users/nimrod/Documents/SmallFarmsAgents/.env)
set -a; source /Users/nimrod/Documents/SmallFarmsAgents/.env; set +a
lftp -u "$SFA_FTP_USER","$SFA_FTP_PASS" \
     -e "set ftp:ssl-force true; set ftp:ssl-protect-data true; set ssl:verify-certificate no;
         rm -f index.php;
         mirror -R --delete --parallel=4 /tmp/sfa-staged/ /;
         bye" \
     "ftp://$SFA_FTP_HOST"
```

## First-deploy bootstrap

```bash
# 1. Compose .env locally with these values:
#    APP_ENV=production
#    DB_HOST=localhost
#    DB_PORT=3306
#    DB_NAME=<from /Users/nimrod/Documents/SmallFarmsAgents/.env SFA_DB_NAME>
#    DB_USER=<...SFA_DB_USER>
#    DB_PASS=<...SFA_DB_PASS>
#    INGEST_HMAC_SECRET=<...SFA_INGEST_HMAC_SECRET>
#    ADMIN_MIGRATE_TOKEN=$(openssl rand -hex 16)
#    LOG_LEVEL=info

# 2. Upload .env via FTPS to site root, then chmod 600 it
lftp -u "$SFA_FTP_USER","$SFA_FTP_PASS" -e "set ftp:ssl-force true; set ftp:ssl-protect-data true;
                                              put /tmp/sfa-staged/.env;
                                              chmod 600 .env;
                                              bye" "ftp://$SFA_FTP_HOST"

# 3. Run migrations via web endpoint (one-time)
curl "https://sfa.nimrod.bio/admin/migrate?token=<your ADMIN_MIGRATE_TOKEN>"
#   → {"applied":["001_schema_migrations","002_crops","003_products"],"already":[],"errors":[]}

# 4. Remove the migration token (edit .env, set ADMIN_MIGRATE_TOKEN= empty), re-upload, chmod 600

# 5. Verify health
curl https://sfa.nimrod.bio/api/v1/health
#   → {"status":"ok","php_version":"8.x.y","db":"ok","ts":"..."}
```

## Curl ingest sanity (from waldhomeserver or Mac, after deploy)

```bash
SECRET="<from .env>"
BODY='{"schema_version":1,"table":"crops","operation":"upsert","idempotency_key":"manual_smoke_001","rows":[{"id":999,"slug":"smoke-test","hebrew_name":"בדיקה","last_pushed_at":"2026-05-23 00:00:00","payload_json":{"schema_version":1}}]}'
SIG="sha256=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -r | cut -d' ' -f1)"
curl -i -X POST https://sfa.nimrod.bio/api/v1/ingest \
     -H "Content-Type: application/json" \
     -H "X-SFA-Auth: $SIG" \
     -d "$BODY"
# → 200 {"accepted":1,...}
curl https://sfa.nimrod.bio/api/v1/crops
# → {"count":1,"items":[{...}]}
```
