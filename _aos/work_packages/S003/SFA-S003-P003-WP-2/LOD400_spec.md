# LOD400 — SFA-S003-P003-WP-2 — Slim PHP skeleton + DB schema + ingest API

**Date:** 2026-05-23
**Status:** LOD400_DRAFT — awaiting team_00 approval before BUILD.
**Builder:** sfa_build (Sonnet)
**Validator:** external (Cursor/Codex) — Iron Rule #1
**Effort:** NORMAL (~2-3 days)
**Branch:** new branch off `claude/gallant-elbakyan-727a60` once BUILD starts.

---

## §1 Goal (one paragraph)

Stand up a minimal, durable PHP application at `sfa.nimrod.bio` root that (a) serves HTTP routes via Slim 4 + PDO, (b) holds a MySQL schema mirror of the canonical Postgres tables on waldhomeserver, (c) accepts authenticated delta pushes from the waldhomeserver publisher via `POST /api/v1/ingest` (HMAC-SHA256), and (d) exposes read JSON endpoints `GET /api/v1/crops` and `GET /api/v1/products`. **No user-facing HTML in this WP** — that is WP-3.

This WP is the *load-bearing skeleton* of the new delivery tier. All subsequent WPs (3 routes, 4 publisher, 5 cutover) build on it. Therefore correctness > features.

## §2 Site layout (binding)

Per WP-1 closure §4.1 — no WordPress on this site. Slim app lives at site root, no `/app/` subdir.

```
/  (site root, served by uPress nginx → PHP-FPM)
├── index.php                         ← front controller (Slim bootstrap, ~30 lines)
├── .htaccess                         ← rewrites all non-file requests to index.php
├── composer.json                     ← Slim 4 + Monolog + PHP-DI + phpdotenv
├── composer.lock                     ← committed for reproducibility
├── vendor/                           ← uploaded as part of bundle (composer install --no-dev locally, ship)
├── .env                              ← created MANUALLY on first deploy (chmod 600), see §6
├── .env.example                      ← shipped in bundle
├── app/
│   ├── bootstrap.php                 ← container, env loading, error handler
│   ├── routes.php                    ← route definitions
│   ├── Controllers/
│   │   ├── HealthController.php
│   │   ├── IngestController.php
│   │   ├── CropsController.php
│   │   └── ProductsController.php
│   ├── Middleware/
│   │   ├── HmacAuthMiddleware.php
│   │   └── JsonResponseMiddleware.php
│   └── Lib/
│       ├── Db.php                    ← PDO factory
│       ├── Hmac.php                  ← sign/verify helpers
│       └── Logger.php                ← Monolog factory
├── migrations/
│   ├── 001_schema_migrations.sql     ← tracking table
│   ├── 002_crops.sql                 ← crops + varieties (mirror subset of Postgres)
│   ├── 003_products.sql              ← products + prices + sources
│   └── migrate.php                   ← CLI runner (php migrations/migrate.php)
├── tests/
│   ├── HmacTest.php                  ← unit
│   ├── IngestSmokeTest.php           ← integration (against test MySQL)
│   └── bootstrap.php
├── public_assets/                    ← (empty in WP-2; populated in WP-3)
├── logs/                             ← Monolog rotating file (chmod 770)
└── README.md                         ← deploy procedure + ops notes
```

**Removed during BUILD:** the uPress default `index.php` (327 KB landing page) — overwritten by our front-controller `index.php`.

## §3 `composer.json` (binding deps)

```json
{
  "name": "smallfarms/sfa-delivery",
  "description": "SFA dedicated delivery tier (sfa.nimrod.bio) — Slim 4 + MySQL",
  "type": "project",
  "license": "proprietary",
  "require": {
    "php": ">=8.1",
    "ext-pdo_mysql": "*",
    "ext-openssl": "*",
    "ext-json": "*",
    "slim/slim": "^4.13",
    "slim/psr7": "^1.6",
    "php-di/php-di": "^7.0",
    "vlucas/phpdotenv": "^5.6",
    "monolog/monolog": "^3.5"
  },
  "require-dev": {
    "phpunit/phpunit": "^10.5"
  },
  "autoload": {
    "psr-4": {
      "SFA\\": "app/"
    }
  },
  "autoload-dev": {
    "psr-4": {
      "SFA\\Tests\\": "tests/"
    }
  },
  "scripts": {
    "migrate": "php migrations/migrate.php",
    "test": "phpunit"
  }
}
```

**PHP minimum 8.1** — uPress shared hosting currently defaults to 8.x. If WP-1 follow-up reveals lower, BUILD pauses and team_100 negotiates with uPress to enable a newer PHP pool (control panel option, no support ticket needed).

## §4 `.htaccess` (root)

```apache
# sfa.nimrod.bio — Slim front-controller routing
RewriteEngine On

# Force HTTPS (Cloudflare also does this, defense-in-depth)
RewriteCond %{HTTP:X-Forwarded-Proto} =http [OR]
RewriteCond %{HTTPS} off
RewriteRule .* https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]

# Block direct access to sensitive files
RewriteRule ^\.env - [F,L]
RewriteRule ^composer\.(json|lock)$ - [F,L]
RewriteRule ^migrations/ - [F,L]
RewriteRule ^app/ - [F,L]
RewriteRule ^tests/ - [F,L]
RewriteRule ^vendor/ - [F,L]
RewriteRule ^logs/ - [F,L]

# Serve real files (CSS/JS/images in public_assets/) directly
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule .* - [L]

# Everything else → Slim front controller
RewriteRule .* index.php [L]
```

## §5 `index.php` (front controller — full file)

```php
<?php
declare(strict_types=1);

require __DIR__ . '/vendor/autoload.php';
require __DIR__ . '/app/bootstrap.php';

$app = SFA\Bootstrap::createApp();
(require __DIR__ . '/app/routes.php')($app);
$app->run();
```

## §6 `.env` on uPress (created manually on first deploy)

Stored at site root, **chmod 600**, blocked from web access by `.htaccess` §4.

```env
APP_ENV=production
APP_DEBUG=false

# MySQL (uPress internal)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sfanms2u_SFAUserUiDB
DB_USER=sfanms2u_DbAdmin
DB_PASS=<<from uPress panel; mirror of SFA_DB_PASS on Mac .env>>

# HMAC shared secret (MUST match SFA_INGEST_HMAC_SECRET on waldhomeserver .env)
INGEST_HMAC_SECRET=<<from openssl rand -base64 32, generated WP-1>>

# Logging
LOG_LEVEL=info
```

Deploy procedure: developer composes `.env` locally with values from password manager (or copies `SFA_DB_PASS`/`SFA_INGEST_HMAC_SECRET` from Mac `.env`), uploads via `lftp put .env`, then runs `chmod 600 .env` via the same lftp session.

## §7 Migrations (binding schema)

### `migrations/001_schema_migrations.sql`

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version VARCHAR(64) PRIMARY KEY,
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### `migrations/002_crops.sql`

```sql
CREATE TABLE IF NOT EXISTS crops (
  id BIGINT PRIMARY KEY,
  slug VARCHAR(80) NOT NULL UNIQUE,
  hebrew_name VARCHAR(200) NOT NULL,
  scientific_name VARCHAR(200),
  family_id BIGINT,
  category VARCHAR(40),
  season VARCHAR(40),
  dtm_min INT,
  dtm_max INT,
  description_md TEXT,
  source_attribution TEXT,
  last_pushed_at DATETIME,
  payload_json JSON,
  INDEX idx_crops_category (category),
  INDEX idx_crops_season (season)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crop_varieties (
  id BIGINT PRIMARY KEY,
  crop_id BIGINT NOT NULL,
  name VARCHAR(200) NOT NULL,
  payload_json JSON,
  FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
  INDEX idx_varieties_crop (crop_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Rationale for `payload_json`**: Postgres-side schema (6 tables, deeply normalized) is the canonical source of truth. On the MySQL mirror we keep top-level queryable fields as columns + a `payload_json` blob with the rest. This lets WP-3 read endpoints serve everything without WP-2 needing to mirror every column. When publisher (WP-4) pushes a crop, the JSON contains the full row dict.

### `migrations/003_products.sql`

```sql
CREATE TABLE IF NOT EXISTS products (
  id BIGINT PRIMARY KEY,
  slug VARCHAR(80) NOT NULL UNIQUE,
  hebrew_name VARCHAR(200) NOT NULL,
  category VARCHAR(40),
  unit VARCHAR(20),
  last_price NUMERIC(10,2),
  last_price_date DATE,
  freshness_days INT,
  last_pushed_at DATETIME,
  payload_json JSON,
  INDEX idx_products_category (category),
  INDEX idx_products_freshness (freshness_days)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS product_prices (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_id BIGINT NOT NULL,
  price_date DATE NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  source VARCHAR(120),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  UNIQUE KEY uq_product_date_source (product_id, price_date, source),
  INDEX idx_prices_date (price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### `migrations/migrate.php` (CLI runner — full file)

```php
<?php
declare(strict_types=1);
require __DIR__ . '/../vendor/autoload.php';
Dotenv\Dotenv::createImmutable(__DIR__ . '/..')->load();

$pdo = new PDO(
  "mysql:host={$_ENV['DB_HOST']};port={$_ENV['DB_PORT']};dbname={$_ENV['DB_NAME']};charset=utf8mb4",
  $_ENV['DB_USER'], $_ENV['DB_PASS'],
  [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

// Ensure tracking table
$pdo->exec(file_get_contents(__DIR__ . '/001_schema_migrations.sql'));

// Find pending
$files = glob(__DIR__ . '/[0-9][0-9][0-9]_*.sql');
sort($files);
$applied = $pdo->query('SELECT version FROM schema_migrations')->fetchAll(PDO::FETCH_COLUMN);

foreach ($files as $file) {
  $version = basename($file, '.sql');
  if (in_array($version, $applied, true)) continue;
  echo "Applying $version ... ";
  $pdo->beginTransaction();
  try {
    $pdo->exec(file_get_contents($file));
    $pdo->prepare('INSERT INTO schema_migrations (version) VALUES (?)')->execute([$version]);
    $pdo->commit();
    echo "OK\n";
  } catch (Throwable $e) {
    $pdo->rollBack();
    echo "FAIL: " . $e->getMessage() . "\n";
    exit(1);
  }
}
echo "All migrations applied.\n";
```

**Invocation on uPress**: no shell access for us, but uPress provides a "PHP Cron Jobs" panel. We schedule a **one-shot cron** to run `php /home/.../htdocs/migrations/migrate.php` once, then delete the cron entry. Alternatively (faster): expose a web endpoint `GET /admin/migrate?token=<one-time>` that runs the same logic — token rotated immediately after. **First deploy uses the web endpoint** (documented in README §3).

## §8 Routes (`app/routes.php`)

```php
<?php
declare(strict_types=1);
use Slim\Routing\RouteCollectorProxy;

return function (Slim\App $app): void {
    $app->get('/', [SFA\Controllers\HealthController::class, 'root']);

    $app->group('/api/v1', function (RouteCollectorProxy $g) {
        $g->get('/health', [SFA\Controllers\HealthController::class, 'health']);
        $g->get('/crops', [SFA\Controllers\CropsController::class, 'list']);
        $g->get('/crops/{slug}', [SFA\Controllers\CropsController::class, 'detail']);
        $g->get('/products', [SFA\Controllers\ProductsController::class, 'list']);
        $g->get('/products/{slug}', [SFA\Controllers\ProductsController::class, 'detail']);

        $g->post('/ingest', [SFA\Controllers\IngestController::class, 'receive'])
          ->add(SFA\Middleware\HmacAuthMiddleware::class);
    });

    // Migration admin (token-gated, removed after first run — see README)
    $app->get('/admin/migrate', [SFA\Controllers\HealthController::class, 'migrate']);
};
```

## §9 HMAC middleware (`app/Middleware/HmacAuthMiddleware.php` — full file)

```php
<?php
declare(strict_types=1);
namespace SFA\Middleware;

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface as Handler;
use Slim\Psr7\Response;

final class HmacAuthMiddleware implements MiddlewareInterface {
    public function process(Request $request, Handler $handler): ResponseInterface {
        $secret = $_ENV['INGEST_HMAC_SECRET'] ?? '';
        if ($secret === '') {
            return $this->unauthorized('server not configured');
        }
        $header = $request->getHeaderLine('X-SFA-Auth');
        if (!str_starts_with($header, 'sha256=')) {
            return $this->unauthorized('missing/malformed X-SFA-Auth');
        }
        $given = substr($header, 7);
        $body = (string) $request->getBody();
        $request->getBody()->rewind();
        $expected = hash_hmac('sha256', $body, $secret);
        if (!hash_equals($expected, $given)) {
            return $this->unauthorized('hmac mismatch');
        }
        return $handler->handle($request);
    }
    private function unauthorized(string $reason): ResponseInterface {
        $r = new Response(401);
        $r->getBody()->write(json_encode(['error' => 'unauthorized', 'reason' => $reason]));
        return $r->withHeader('Content-Type', 'application/json; charset=utf-8');
    }
}
```

## §10 Ingest controller (sketch)

```php
<?php
namespace SFA\Controllers;
// ... receive(Request, Response):
//   - decode JSON body: {table: 'crops'|'crop_varieties'|'products'|'product_prices',
//                         operation: 'upsert'|'delete',
//                         rows: [...],
//                         idempotency_key: 'YYYY-MM-DD_seq',
//                         schema_version: 1}
//   - validate table whitelist + schema_version
//   - look up idempotency_key in `ingest_log` table (added in migration 004 if needed); if seen, return 200 + {duplicate: true}
//   - per row: build upsert SQL (INSERT ... ON DUPLICATE KEY UPDATE) using payload_json
//   - record idempotency_key after success
//   - return 200 + {accepted: N, rejected: M, errors: [...]}
//   - on parse/validation error: 400; on DB error: 500 (caller retries with backoff)
```

**Idempotency**: WP-4 publisher generates `idempotency_key = "{table}_{YYYY-MM-DD}_{sequence}"`. WP-2 stores them with a 30-day TTL (cleaned by a separate cron, deferred to WP-4 since publisher owns delta semantics).

## §11 Deploy procedure (binding)

Documented in `README.md` shipped in the bundle. Summary:

**Build step (Mac, one-time per release):**
```bash
cd /path/to/sfa-app-repo  # to be created at /Users/nimrod/Documents/sfa-delivery, separate from this AOS repo
composer install --no-dev --optimize-autoloader
tar czf sfa-bundle.tgz \
  --exclude='.git*' --exclude='tests' --exclude='.env' --exclude='logs/*' \
  index.php .htaccess composer.json composer.lock vendor app migrations public_assets README.md
```

**Deploy step (Mac, via FTPS verified in WP-1):**
```bash
set -a; source /Users/nimrod/Documents/SmallFarmsAgents/.env; set +a
lftp -u "$SFA_FTP_USER","$SFA_FTP_PASS" \
     -e "set ftp:ssl-force true; set ftp:ssl-protect-data true; set ssl:verify-certificate no;
         cd /;
         rm -f index.php;            # remove uPress default landing
         mirror -R --delete --parallel=4 ./extracted-bundle/ ./;
         bye" \
     "ftp://$SFA_FTP_HOST"
```

(Bundle extracted locally first — uPress doesn't give us shell to untar.)

**First-deploy bootstrap (~3 min):**
1. SCP `.env` to site root (or compose via lftp): `lftp ... -e "put .env"` then `chmod 600 .env`
2. Browse to `https://sfa.nimrod.bio/admin/migrate?token=<from .env, ADMIN_MIGRATE_TOKEN>` → returns `{"applied":["001_schema_migrations","002_crops","003_products"],"already":[]}`
3. Remove `/admin/migrate` route from `app/routes.php`, redeploy (or rotate token to disable)
4. Verify: `curl https://sfa.nimrod.bio/api/v1/health` → `{"status":"ok","php":"8.x.y","db":"ok","ts":"..."}`

## §12 Acceptance Criteria (15)

| # | AC | How to verify |
|---|----|----|
| AC-01 | `composer install --no-dev` succeeds locally with PHP 8.1+ | local `composer install`, exit 0 |
| AC-02 | `.htaccess` blocks `/.env`, `/composer.json`, `/migrations/*`, `/app/*` (403) | `curl -I https://sfa.nimrod.bio/.env` returns 403 |
| AC-03 | `.htaccess` rewrites `/api/v1/health` to `index.php` (200) | `curl https://sfa.nimrod.bio/api/v1/health` returns `{"status":"ok",...}` |
| AC-04 | `php migrations/migrate.php` applies 3 migrations idempotently | run once: applies 3; run again: applies 0 |
| AC-05 | Migration log: `SELECT * FROM schema_migrations` returns 3 rows in order | MySQL query via phpMyAdmin |
| AC-06 | `POST /api/v1/ingest` with valid HMAC + valid payload returns 200 + `{accepted:N}` | curl from waldhomeserver with test payload |
| AC-07 | `POST /api/v1/ingest` with missing/bad HMAC returns 401 | curl without header, with bad sig |
| AC-08 | `POST /api/v1/ingest` with valid HMAC but unknown table returns 400 | curl with `table:"unknown"` |
| AC-09 | `POST /api/v1/ingest` idempotency: same key twice returns `{duplicate:true}` on 2nd | curl same payload twice |
| AC-10 | `GET /api/v1/crops` returns `[]` (empty before ingest), JSON `Content-Type: application/json; charset=utf-8` | curl + header inspect |
| AC-11 | After test ingest: `GET /api/v1/crops` returns the inserted rows | curl + assert count |
| AC-12 | `GET /api/v1/crops/non-existent-slug` returns 404 + JSON error | curl |
| AC-13 | phpunit unit tests pass: HmacTest (sign/verify/mismatch/replay) | `composer test` exit 0 |
| AC-14 | phpunit integration: IngestSmokeTest applies migrations to ephemeral SQLite, posts payload, asserts rows | `composer test` exit 0 |
| AC-15 | Error path: trigger DB error (e.g., wrong DB_PASS in .env), `/api/v1/health` returns 500 + JSON error (not HTML stack trace) | flip env, curl, restore |

## §13 Out of scope (deferred)

- User-facing HTML routes (crop-book grid, market index) → **WP-3**
- Publisher migration from `wp_upload.py` → `sfa_ingest_push.py` → **WP-4**
- Old `www.nimrod.bio/smallfarmsagent/` 301 redirect + mu-plugin removal → **WP-5**
- WP-A two-tier reconciler (Postgres canonical → MySQL mirror diff detection) → P002 WP-A architecture
- Auth/login (JWT) → S004
- Admin UI for data inspection → S004

## §14 Risks + mitigations

| Risk | Mitigation |
|------|------------|
| PHP version on uPress < 8.1 | Detect in `/api/v1/health`; if too low, change PHP pool in uPress panel (control panel, no support ticket) |
| mod_rewrite disabled | `.htaccess` rewrite test in AC-03; if fail, request enablement via uPress panel (standard option) |
| Composer not runnable on uPress (no shell) | We `composer install` LOCALLY and ship `vendor/` in bundle. uPress never runs composer. |
| `.env` accidentally readable via web | `.htaccess` `RewriteRule ^\.env - [F,L]`; verified by AC-02 |
| HMAC secret leak | Stored only in `.env` (chmod 600 both sides); never logged; never in URL |
| Replay attack on `/api/v1/ingest` | Idempotency key per delta; replays return 200 + `duplicate:true` (no double-apply) |
| Schema drift Postgres↔MySQL | `payload_json` blob carries everything; WP-A reconciler (P002) does periodic diff audit |
| MySQL connection limit on shared host | Use short-lived PDO connections per request (Slim default); monitor in WP-3 load test |
| File upload via FTPS slow/fragmented | `lftp mirror --parallel=4 --delete`; bundle target ~5-10 MB total (vendor/ dominates) |

## §15 Test plan (binding)

- **Unit (`tests/HmacTest.php`)**: 6 cases — happy path, wrong secret, malformed header, missing header, empty body, replay (handled at controller layer not middleware, so middleware doesn't dedupe — separate IngestIdempotencyTest)
- **Integration (`tests/IngestSmokeTest.php`)**: spins up ephemeral SQLite (PDO sqlite), runs migrations adapted for SQLite (provided in `tests/fixtures/migrations_sqlite/`), posts 3 sample payloads (1 crop, 1 variety, 1 product), asserts counts + idempotency
- **Manual on uPress (post-deploy)**: AC-03/05/06/07/09/15 all curl-based against live `sfa.nimrod.bio`
- **No browser tests in this WP** — WP-3 owns frontend testing

## §16 Definition of Done (LOD500_LOCKED criteria)

1. All 15 ACs pass
2. `composer test` exit 0
3. `https://sfa.nimrod.bio/api/v1/health` returns `{"status":"ok",...}` continuously for ≥1 hour
4. WP-1 follow-ups resolved: waldhomeserver IP added to FTP allowlist (so WP-4 can use same path); PHP version + mod_rewrite confirmed via AC-03/AC-11
5. README.md committed with deploy procedure verified end-to-end (one full reload cycle: edit → bundle → ftps → curl test)
6. Branch merged to `main` of this AOS spoke (the PHP app itself lives in a separate repo — see §11 build step note)
7. team_190 (external, Cursor/Codex) L-GATE_V verdict PASS or PASS_WITH_FINDINGS

## §17 Unblocks

- **WP-3** — once read endpoints exist + schema is populated by manual test ingests
- **WP-4** — once `/api/v1/ingest` is verified live; publisher refactor is straightforward HTTP replacement
- **WP-5** — once WP-3 + WP-4 are in production, the 301 + mu-plugin cleanup becomes trivial

## §18 Open questions — STATUS

### Q1. Repo layout — ✅ DECIDED 2026-05-23
**team_00 chose: Nested in SmallFarmsAgents (`sfa_delivery/` subdir).** Rationale: branch hygiene + single `.env.example`. BUILD will create `sfa_delivery/` at repo root with composer.json, app/, migrations/, etc. as specified in §2 (layout paths remain relative to that subdir).

### Q2. First-deploy migration method — ✅ DECIDED 2026-05-23
**team_00 chose: Web endpoint token-gated.** `GET /admin/migrate?token=<one-time>` runs `migrate.php` server-side, returns JSON result. Token removed/rotated post-run as specified in §11 first-deploy bootstrap.

### Q3. Schema strategy (mirror granularity) — ✅ DECIDED 2026-05-23
**team_00 chose: Option B (Hybrid — minimal top-level columns + `payload_json` blob).** Decision record + canonical schema spec:
- Decision: `_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md`
- Architecture SSoT: `documentation/02-architecture/sfa-delivery-tier.md`
- Schema SSoT (binding DDL + JSON payload contracts + evolution rules): `documentation/03-data-and-schema/sfa-mysql-mirror.md`

The schema in §7 of this LOD400 is consistent with the canonical doc. **In case of conflict, the canonical docs in `documentation/` are authoritative.** All three open questions are now resolved; BUILD is UNBLOCKED.

---

*LOD400 authored 2026-05-23 by team_100. Awaiting team_00 approval. BUILD will be assigned to sfa_build (Sonnet) under separate session once approved.*
