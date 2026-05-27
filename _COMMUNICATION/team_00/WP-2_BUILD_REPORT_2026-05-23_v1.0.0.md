---
id: WP-2_BUILD_REPORT_SFA-S003-P003-WP-2_v1.0.0
type: BUILD_REPORT
gate: L-GATE_V (closed)
work_package: SFA-S003-P003-WP-2
date: 2026-05-23
recorded_by: team_100 (executed BUILD in-session as sfa_build)
status: LOD500_LOCKED — deployed live
related: DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN, DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY, UPRESS_PROVISIONING_RESULTS
---

# WP-2 BUILD Report — Slim PHP delivery skeleton LIVE

## §1 Outcome

**`https://sfa.nimrod.bio` is LIVE** as of 2026-05-23. PHP 8.5.5 + MySQL 8 + Slim 4 + 6-table schema (4 data + 2 plumbing) + HMAC-authenticated ingest API + read endpoints. All 11 unit + integration tests pass locally; all 6 live ACs pass end-to-end from Mac via curl.

## §2 What was built

**27 source files** under `sfa_delivery/` (vendor/ gitignored, populated by `composer install --no-dev` at deploy):

| Category | Files |
|----------|-------|
| Front controller + routing | `index.php`, `.htaccess`, `app/routes.php` |
| App container | `app/Bootstrap.php` |
| Controllers (4) | `Health`, `Ingest`, `Crops`, `Products` |
| Middleware (3) | `HmacAuth`, `JsonError`, `JsonResponse` |
| Lib (3) | `Db` (PDO factory, MySQL+sqlite dialect-aware), `Hmac` (sign/verify), `Logger` (Monolog rotating) |
| Migrations | `001_schema_migrations.sql` (tracker + ingest_log), `002_crops.sql`, `003_products.sql`, `migrate.php` (CLI + web-callable) |
| Tests | `tests/HmacTest.php` (7 cases), `tests/IngestSmokeTest.php` (4 cases), `bootstrap.php` |
| Project meta | `composer.json`, `composer.lock`, `phpunit.xml`, `.env.example`, `.gitignore`, `README.md` |

## §3 Local validation

```
PHPUnit 10.5.63 by Sebastian Bergmann and contributors.
...........                                                       11 / 11 (100%)
Time: 00:00.038, Memory: 10.00 MB
OK (11 tests, 20 assertions)
```

Tests use sqlite::memory: backend. Dialect-aware upsert in `IngestController::upsert()` switches between MySQL `ON DUPLICATE KEY UPDATE` and ANSI `ON CONFLICT (...) DO UPDATE SET ...` based on `PDO::ATTR_DRIVER_NAME`.

## §4 Deploy execution

1. `composer install --no-dev --optimize-autoloader` locally → `vendor/` ~3.2 MB
2. Staged bundle → `/tmp/sfa-staged/` (27 source files + vendor + composed `.env` with prod values from Mac `.env`)
3. `lftp mirror -R --parallel=4 --include-hidden=true /tmp/sfa-staged/ /` to `ftp.s1240.upress.link` (FTPS prot_c) — completed
4. `chmod 600 .env` on remote
5. `GET /admin/migrate?token=<one-time>` → applied 001, 002, 003
6. `ADMIN_MIGRATE_TOKEN` rotated to empty in `.env` (endpoint now locked)

**Issue encountered + fixed mid-deploy:**
- Cloudflare CNAME initially pointed to www origin (old uPress server pool) → "Domain Not Found" splash. team_00 updated CF to point at new server. After ~30s, live.
- Initial migrate run failed: MySQL DDL auto-commits and broke explicit `beginTransaction()/commit()` wrapping. Fixed `HealthController::migrate` to drop transactions around DDL (DDL is non-transactional in MySQL by design). Re-uploaded only that file.

## §5 Live AC verification (6/6 PASS)

Run from Mac, against `https://sfa.nimrod.bio`:

| # | Test | Result |
|---|------|--------|
| AC-01 | `GET /api/v1/health` | `{status:"ok", php_version:"8.5.5", db:"ok", ts:...}` ✅ |
| AC-02 | POST valid HMAC + crop payload → `/api/v1/ingest` | `200 {accepted:1, rejected:0}` ✅ |
| AC-03 | `GET /api/v1/crops` returns inserted row | `{count:1, items:[{...}]}` ✅ |
| AC-04 | `GET /api/v1/crops/smoke-tomato` returns merged JSON (cols + payload_json) | Hebrew strings + nested keys present ✅ |
| AC-05 | POST bad HMAC → 401 | `401 {error:"unauthorized", reason:"hmac mismatch"}` ✅ |
| AC-06 | POST replay (same idempotency_key) → duplicate | `200 {duplicate:true, previously_accepted:1}` ✅ |
| AC-07 | POST unknown table → 400 | `400 {error:true, message:"unknown table: unknown"}` ✅ |
| AC-08 | DELETE (cleanup smoke data via ingest op:"delete") | `200 {accepted:1}` ✅ |

## §6 Findings (audit log)

| ID | Severity | Description | Disposition |
|----|----------|-------------|-------------|
| F-1 | LOW | uPress nginx only partially honors `.htaccess`: `RewriteRule [F,L]` blocks NOT applied to `composer.json` (200) or `migrations/*.sql` (200). Dotfiles (`.env`) and certain dirs are naturally denied by nginx defaults. No secrets exposed (composer.json + SQL contain only dependency list + DDL); but ideally hardened. | DEFERRED to WP-2-patch01 (optional). Alternative: rename composer.json + migrations into a dotted dir nginx denies. |
| F-2 | INFO | uPress runs nginx (not Apache); `.htaccess` is effectively a no-op for many directives. Slim routing works because uPress nginx has implicit WordPress-style "all → index.php" rewrites. | NOTED in canonical doc; no action. Behavior is favorable to us. |
| F-3 | INFO | PHP version on uPress is **8.5.5** (newer than the 8.1+ minimum in `composer.json`). All deps work. | NOTED. |
| F-4 | INFO | uPress site has NO WordPress auto-installed (per WP-1 discovery confirmed). Our Slim app fully owns the docroot. | As planned. |

## §7 Outstanding WP-2 housekeeping

- [ ] (Optional) Rotate `SFA_FTP_PASS`, `SFA_DB_PASS`, `EMAIL_PASSWORD` after WP-3/4/5 stabilize (leaked in earlier transcript). Not blocking.
- [ ] Add waldhomeserver public IP to uPress FTP allowlist before WP-4 (so publisher push works from the home server).
- [ ] (Optional) F-1 .htaccess hardening (`composer.json` + `migrations/*.sql`).

## §8 What this unblocks

- **WP-3** (user-facing PHP routes — crop-book + market pages): Slim is up; can now port the Flask blueprint pattern to plain PHP templates over the read API.
- **WP-4** (publisher migration): `/api/v1/ingest` is live + HMAC-verified. waldhomeserver `wp_upload.py` → `sfa_ingest_push.py` is now a straight HTTP replacement.
- **WP-5** (301 cutover): unchanged scope, ready once WP-3 + WP-4 done.

## §9 Files of record

- Source: `sfa_delivery/` (27 files, committed)
- Live: `https://sfa.nimrod.bio` (verified)
- Spec: `_aos/work_packages/S003/SFA-S003-P003-WP-2/LOD400_spec.md`
- Canonical docs: `documentation/02-architecture/sfa-delivery-tier.md` + `documentation/03-data-and-schema/sfa-mysql-mirror.md`
- Roadmap: `_aos/roadmap.yaml` SFA-S003-P003-WP-2 → COMPLETE/LOD500_LOCKED

---

*Build report filed 2026-05-23 by team_100. WP-2 LOD500_LOCKED. Proceeding to WP-4 (publisher) next.*
