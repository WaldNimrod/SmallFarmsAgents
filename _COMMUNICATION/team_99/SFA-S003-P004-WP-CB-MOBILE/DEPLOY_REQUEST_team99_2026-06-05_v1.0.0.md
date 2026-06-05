# DEPLOY REQUEST — WP-CB-MOBILE (single batch) — team_100 → team_99 — v1.0.0

**Date:** 2026-06-05 · **From:** team_100 · **To:** team_99 (server-side deploy) · **Authorize:** team_00
**WP:** SFA-S003-P004-WP-CB-MOBILE · **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` @ **`9cd077b`** (PUSHED to origin)

## What to deploy
The full WP-CB-MOBILE v4 mobile remediation + the held IL_general quick-win, as **one batch** (team_00: "hold for mobile batch"). All UI code is on the shared branch, **pushed to origin** at HEAD **`9cd077b`** — `git fetch` then deploy that commit. Commits in this batch (on top of the last live deploy `7fb3cf7`):
- `bac5b69`, `9f60f56` — calendar region-map / IL_general leak fix
- `bf473fb` — plan + design package
- `0024059` (stage 1), `05d7610` (stage 2), `7f4c105` (stage 3) — the mobile build
- `9cd077b` — restore 13-topic canon parity (regression caught by the pre-push pytest gate + fixed)

## Deploy path (per canon)
UI code → uPress via FTPS. Runbook: `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md` (`scripts/ftp_deploy_sfa_ui.sh`). The deploy host = **waldhomeserver** (FTPS relay; its egress IP is uPress-allowlisted — the Mac's is not). This is why team_100/this Mac cannot push directly (auth-gated; see memory `reference_prod_deploy_authorization`).

## New/changed files to ship (under `sfa_delivery/`)
- **NEW:** `public_assets/css/mobile-fixes.css` (the override layer — must be served + linked; `_layout.php` already links it after `classb.css`).
- **NEW:** `templates/macros/crop_topics.php`.
- **MODIFIED:** `templates/_layout.php`, `public_assets/js/crop-book-v1.js`, `app/Controllers/CropBookViewController.php`, `templates/macros/{crop_calendar,market_disclaimer,audience_switch}.php`, `templates/pages/{book_entry,book_crop,hub_home,hub_tiers,market_list,calc_dash}.php`.
  → Ensure `mobile-fixes.css` is included in the FTPS mirror set (it's a new file in `public_assets/css/` — the deploy script should pick it up; verify it lands).

## Pre-deploy state (team_100 verified)
- PHP suite **215/215** (real-vendor, main-tree run). `validate_aos` **0 FAIL**. No desktop regression beyond the two team_00-ratified changes (D1 market table-default, D2 type floor).

## Post-deploy
1. Bump the asset version (`?v=…`) so the new CSS/JS bust cache (the css-dir mtime glob in `_layout.php` should handle it — confirm the live `?v=` changed).
2. Report the deployed commit + live `?v=` back to team_100.
3. **Then** team_50 runs the @375 visual QA (mandate: `_COMMUNICATION/team_50/SFA-S003-P004-WP-CB-MOBILE/QA_MANDATE_team50_375_2026-06-05_v1.0.0.md`).

⚠ Production deploy needs team_00 authorization. Dev/staging TLS quirks are by-design; a cert error on the production domain IS a defect.
