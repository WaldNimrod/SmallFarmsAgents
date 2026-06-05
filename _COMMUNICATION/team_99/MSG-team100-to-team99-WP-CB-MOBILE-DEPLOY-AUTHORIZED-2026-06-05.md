# MSG — team_100 → team_99 — DEPLOY AUTHORIZED: WP-CB-MOBILE (single batch)

**Date:** 2026-06-05
**From:** team_100 (Chief Architect)
**To:** team_99 (server-side deploy)
**Re:** SFA-S003-P004-WP-CB-MOBILE · **DEPLOY AUTHORIZED by team_00** (Nimrod, 2026-06-05)
**Transport:** file-fallback (v2 API unreachable from the Mac: `100.125.98.56:8090` HTTP 000000 — ADR043 §4)

## Authorization
team_00 has **authorized the production deploy** of WP-CB-MOBILE as a **single batch**. Proceed.

## Exact instructions

1. **Fetch + checkout the build.**
   ```
   git fetch origin
   git checkout claude/ui-polish-hub-cropbook-2026-06-03
   git rev-parse --short HEAD     # expect 6202192 (or later)
   ```
   - **Deployable delivery-tier bytes are finalized at `9cd077b`.** Origin HEAD `6202192` is docs/roadmap-only on top (no `sfa_delivery/` change) — deploying current HEAD is byte-identical for the site. Deploy current HEAD of the branch.

2. **Deploy path — FTPS → uPress** (per `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`):
   ```
   scripts/ftp_deploy_sfa_ui.sh
   ```
   - Deploy host = **waldhomeserver** (its egress IP is uPress-allowlisted; the Mac's is not — that is why team_100 cannot push to uPress and you do).
   - Mirror the `sfa_delivery/` delivery tier to uPress (`sfa.nimrod.bio`).

3. **⚠ NEW FILES that MUST land** (verify they are in the mirror set — a new file in `public_assets/css/` and a new macro):
   - `sfa_delivery/public_assets/css/mobile-fixes.css`  ← the override layer; the page links it after `classb.css`. If this file does not deploy, the entire mobile fix is inert.
   - `sfa_delivery/templates/macros/crop_topics.php`
   - Plus all modified: `_layout.php`, `crop-book-v1.js`, `CropBookViewController.php`, macros `crop_calendar.php`/`market_disclaimer.php`/`audience_switch.php`, pages `book_entry.php`/`book_crop.php`/`hub_home.php`/`hub_tiers.php`/`market_list.php`/`calc_dash.php`.

4. **Cache-bust.** Confirm the live asset version (`?v=…`) changed (the css-dir mtime glob in `_layout.php` drives it). Verify `mobile-fixes.css` is served with the new `?v=` (not 404).

5. **Report back to team_100:** the deployed commit SHA + the new live `?v=` value.

## Pre-deploy state (team_100 verified)
- PHP delivery suite **215/215**; Python canon parity restored (`9cd077b`); `validate_aos` **0 FAIL**.
- No desktop regression beyond the two team_00-ratified changes: **D1** market table-default, **D2** type-minimum floor.

## After your deploy
team_50 runs the **@375 visual QA** (CDP) → mandate: `_COMMUNICATION/team_50/SFA-S003-P004-WP-CB-MOBILE/QA_MANDATE_team50_375_2026-06-05_v1.0.0.md`. On GO, team_100 records LOD500.

Full deploy spec: `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-MOBILE/DEPLOY_REQUEST_team99_2026-06-05_v1.0.0.md`

> Production TLS must be valid — a cert error on `sfa.nimrod.bio` (production) IS a defect (dev/staging cert quirks are by-design; not applicable here).
