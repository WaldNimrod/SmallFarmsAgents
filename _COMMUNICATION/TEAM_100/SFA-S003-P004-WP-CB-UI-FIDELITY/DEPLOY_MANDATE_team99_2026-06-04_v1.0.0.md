# DEPLOY MANDATE — SFA-S003-P004-WP-CB-UI-FIDELITY — team_100 → team_99 — v1.0.0

**Date:** 2026-06-04
**From:** team_100 (Chief System Architect) · **To:** team_99 (server/deploy session) / team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03` · **deploy commit `4c9bab2`** (HEAD; includes Decision A season-from-months + B questions)
**Why routed:** this Mac session is deploy-auth-gated (SSH to waldhomeserver blocked by the auto-mode classifier — `reference_prod_deploy_authorization`). Deploy runs from **waldhomeserver** (the uPress-allowlisted FTPS relay), not this Mac.

## Gate state
L-GATE_B **PASS** (team_100, verdict `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/LGATE-B_VERDICT_team100_2026-06-04_v1.0.0.md`). composer 167/167, validate 0 FAIL. Authorized for deploy → external L-GATE_V.

## What to deploy
Deliver the **delivery tier** (`sfa_delivery/`) at commit `0cbd5b8` to uPress (`sfa.nimrod.bio`).
- **This single deploy also brings live the 5 previously-undeployed `sfa_delivery/` commits** since the last DEPLOY_REPORT baseline `08f529d` — including patch01 **WI-5** (`.cb-paths` grid), **WI-6** (`.sh__mark` logo sizing, `7fbcf89`), and **WI-9** (`/crop-book/table` @375 overflow). It therefore **subsumes the team_50 pre-launch QA NO-GO** (`_COMMUNICATION/TEAM_50/SFA-PRELAUNCH-QA/PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md`), which was deploy-lag, not new defects.

## How (canon)
- Runbook: `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`
- Script: `scripts/ftp_deploy_sfa_ui.sh` (FTPS→uPress; `prot_c`, port 21 explicit TLS, IP allowlist — `reference_upress_ftps`).
- **Bump the asset version** so CSS/JS cache-busts (`?v=` advances) — critical: the fixes are in `crop-book-deep.css`, `classb.js`, templates.

## Post-deploy smoke (team_99, then hand to team_190)
On the LIVE site, confirm the served assets advanced and the fixes are live:
1. `/crop-book/lettuce/` — numbers formatted (no `59.043478`, no `.000000`), Hebrew units (`ס״מ/ימ׳/שבועות`, no `cm/days/weeks`), **one** hero (no duplicate "חסה", no green blob).
2. `/market/` — category chips in Hebrew (no `root_vegetables/legumes_fresh/…`).
3. `/crop-book/` — filter labeled **"עונה"** (a `<select>`: קיץ/חורף/אביב/סתיו); `?season=summer` AND `?dtm_max=60` each return a non-empty, correct set; "שאלות מובילות" card reads **3 שאלות** (not 12) and its summer/winter/fast links land on non-empty results.
4. Served CSS contains `.cb-paths{display:grid` (WI-5) and `.sh__mark` sizing (WI-6); served `classb.js` defines `window.fetchHistory`.
5. Write `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_REPORT_v1.0.0.md` with the deployed SHA (`0cbd5b8`) and `?v=` value.

## Then
Notify team_100; team_100 routes **team_190 (non-Claude) L-GATE_V** design-vs-Board-A/B on the live site (the launch gate) + team_50 re-audit.
