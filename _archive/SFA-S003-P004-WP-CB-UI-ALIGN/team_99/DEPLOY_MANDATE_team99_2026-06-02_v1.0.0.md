# DEPLOY MANDATE — SFA-S003-P004-WP-CB-UI-ALIGN (Class A) — team_100 → team_99 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_99 (deploy/ops) · **Routed by:** team_00
**Branch:** `claude/wp-cb-ui-align-2026-06-02` · **Gate cleared:** L-GATE_S PASS_WITH_FINDINGS (Cursor) → LOD400 LOCKED
**Target:** `sfa.nimrod.bio` (uPress) · **Method:** FTPS mirror per `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`

## 0. Why deploy now
Build (f22138d) + QA fixes (f85691e) + team_50 internal visual QA are on-branch and L-GATE_S has locked the
LOD400. The live per-page L-GATE_V round needs the branch deployed (the PHP tier renders data-driven pages only
with the uPress MySQL — no local DB). Deploy is the prerequisite for L-GATE_V.

## 1. Host constraint (MANDATORY)
**Run the deploy from `waldhomeserver`, NOT the Mac.** The Mac's Bezeq IP is not uPress-allowlisted and blocks
outbound port 21; `waldhomeserver`'s egress IP is the allowlisted FTPS relay. Use the `AOS_server` path /
ssh to waldhomeserver, ensure the branch is checked out there, then run the deploy.

## 2. Command (per runbook)
```bash
# on waldhomeserver, repo root, branch claude/wp-cb-ui-align-2026-06-02
bash scripts/ftp_deploy_sfa_ui.sh
```
The script: loads `.env` FTPS creds → `composer install --no-dev --optimize-autoloader` in `sfa_delivery/` →
verifies `vendor/` present → `lftp mirror -R --delete` to `SFA_FTP_ROOT`. (vendor/ is gitignored — Option B,
team_00 2026-05-28; do not re-mirror from main.)

## 3. Post-deploy smoke (UPDATED for this WP — the legacy sidebar is GONE)
The runbook's old step 3 ("desktop sidebar קהילה accordion / community feed") is **obsolete** — WP-CB-UI-ALIGN
replaced `.gj-shell`/`.dt-shell` with the single `.sh` top-nav shell. New smoke:
1. `curl -sI https://sfa.nimrod.bio/ | head -1` → `200`.
2. `curl -sL https://sfa.nimrod.bio/calc/ | grep -c crop-book-v1.js` → ≥1 (the /calc JS-load fix).
3. `curl -sI https://sfa.nimrod.bio/calc/export.csv | head -1` → `200` (export route; PDF likewise no 404).
4. Load `/` , `/crop-book/`, a crop page, `/calc/`, `/market/` → each renders inside the `.sh` top-nav shell
   (logo + ספר גידולים/מחשבון/מחירון + החשבון שלי); **no** legacy `.gj-shell`/`.dt-shell`/`.sfa-nav` chrome.
5. **Cache-bust:** confirm the `?v=` asset query advanced (Cloudflare edge) — the served `tokens.css` must show
   `--gj-paper:#f8fbf8` and zero `#f5f3ec`. If the edge serves stale CSS, purge Cloudflare for the CSS paths.

## 4. On success
Reply to team_100 (`_COMMUNICATION/team_100/`, MSG per ADR043) with the deployed commit SHA + smoke results.
This unblocks team_190 L-GATE_V (live per-page visual round) — mandate already staged at
`_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-ALIGN/VALIDATION_MANDATE_team190_L-GATE_V_2026-06-02_v1.0.0.md`.

## 5. Rollback
The mirror is idempotent with `--delete`; re-deploy the previous known-good commit's `sfa_delivery/` tree to
revert. Capture the current live commit SHA before deploying so rollback target is known.
