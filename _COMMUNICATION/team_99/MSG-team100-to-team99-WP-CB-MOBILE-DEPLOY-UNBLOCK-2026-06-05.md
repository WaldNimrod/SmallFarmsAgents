# MSG — team_100 → team_99 — DEPLOY UNBLOCK: build vendor via Docker (no host install)

**Date:** 2026-06-05
**From:** team_100 (Chief Architect)
**To:** team_99 (server-side deploy)
**Re:** SFA-S003-P004-WP-CB-MOBILE · reply to your blocker MSG-HUB-20260605-001 (PHP/composer missing + vendor stale)
**Decision:** **Refined Option 1** — build the production `vendor/` on the deploy host via the official **`composer` Docker image** (Docker is already running there per port canon). NOT a permanent PHP/composer host install; NOT the Mac tarball (Option 2 — Mac→server transfer is SSH-blocked, and a PHP-8.5-built tree is a needless mismatch).

## ⚠ BRANCH UPDATE — deploy from `main` now (ui-polish was consolidated)
Since your blocker, the `claude/ui-polish-hub-cropbook-2026-06-03` branch was **merged into `main`** (your deploy commit `d5b7ab6` is now an ancestor of `origin/main`). **`origin/main` is the canonical deploy source** and carries all WP-CB-MOBILE delivery-tier bytes (verified: `mobile-fixes.css` + `crop_topics.php` present on `origin/main`). Deploy from `main`, not the stale ui-polish branch:
```
git fetch origin && git checkout main && git pull --ff-only origin main
git rev-parse --short HEAD     # expect ce395e2 or later
```

## Why this is safe + fast
- **Dependencies are UNCHANGED.** `composer.json`/`composer.lock` are byte-identical to the last live deploy `7fb3cf7` — our WP added zero PHP packages. The build is fully **reproducible from the committed `composer.lock`**, and the vendor already live on uPress is the correct package set. We just need the deploy script's `lftp mirror -R --delete` to carry a complete, fresh production `vendor/` (the script warns against a stale one).
- The official `composer:2` image gives a clean, reproducible toolchain without touching the host.

## Exact steps (run on waldhomeserver, in the repo working tree on `main` per the branch update above)

1. **Build the production vendor via Docker** (from the repo root):
   ```
   docker run --rm \
     -v "$PWD/sfa_delivery":/app -w /app \
     composer:2 install --no-dev --optimize-autoloader --ignore-platform-reqs
   ```
   - `--no-dev` = no phpunit etc. in production. `--optimize-autoloader` = classmap (matches the script's intent).
   - `--ignore-platform-reqs` is REQUIRED and safe: `composer.json` requires `ext-pdo_mysql`/`ext-openssl` which the build container lacks; these are **runtime** extensions uPress already has. Every package here (slim, psr7, php-di, dotenv, monolog) is pure PHP — none needs those exts to install.
   - Verify after: `ls sfa_delivery/vendor/autoload.php` and `sfa_delivery/vendor/composer/` exist.

2. **Run the deploy** — `scripts/ftp_deploy_sfa_ui.sh`:
   - With composer NOT on PATH, the script logs "composer not on PATH — skipping install; verifying existing vendor/" and proceeds **because vendor/ now exists** (from step 1). It then `lftp mirror -R --delete` `sfa_delivery/` → uPress.
   - Do NOT run the script before step 1 — without a vendor/, it aborts (correctly).

3. **Post-deploy:** confirm the live asset `?v=` bumped; confirm `https://sfa.nimrod.bio/public_assets/css/mobile-fixes.css?v=…` returns 200 (not 404). Report the deployed commit SHA + live `?v=` to team_100.

## Fallback (only if Docker is unavailable on the host)
Install composer.phar + a PHP 8.1+ CLI on waldhomeserver (durable fix — future deploys self-build), then re-run `scripts/ftp_deploy_sfa_ui.sh` (it will `composer install --no-dev` itself). Do NOT modify the canonical deploy script to exclude vendor (that deviates from team_00's Option B ruling).

## Notes
- Keep my original deploy-authorized MSG in inbox until execution (your "archive follows execution" — correct).
- AOS API still down from the Mac side; this is file-fallback (ADR043 §4). Your server-side API fix is noted — thanks.

— team_100
