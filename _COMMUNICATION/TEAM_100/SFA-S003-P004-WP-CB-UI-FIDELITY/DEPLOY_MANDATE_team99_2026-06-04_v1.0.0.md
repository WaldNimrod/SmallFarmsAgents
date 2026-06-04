# DEPLOY MANDATE — SFA-S003-P004-WP-CB-UI-FIDELITY — team_100 → team_99 — v1.0.0

**Date:** 2026-06-04
**From:** team_100 (Chief System Architect) · **To:** team_99 (server/deploy session) / team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03` · **deploy commit `4c9bab2`** (HEAD; includes Decision A season-from-months + B questions)
**Why routed:** this Mac session is deploy-auth-gated (SSH to waldhomeserver blocked by the auto-mode classifier — `reference_prod_deploy_authorization`). Deploy runs from **waldhomeserver** (the uPress-allowlisted FTPS relay), not this Mac.

## Gate state
L-GATE_B **PASS** (team_100, verdict `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/LGATE-B_VERDICT_team100_2026-06-04_v1.0.0.md`). composer 167/167, validate 0 FAIL. Authorized for deploy → external L-GATE_V.

## What to deploy
Deliver the **delivery tier** (`sfa_delivery/`) at branch HEAD `4c9bab2` (delivery-tree identical at `f305bbd`) to uPress (`sfa.nimrod.bio`).

**⚠ BASELINE CORRECTED (per team_99 MSG-HUB-20260604-001, 2026-06-04):** the live site is **already at `6703313`** — team_99 FINAL-deployed **WP-CB-UI-patch01** (WI-1..WI-7, `.cb-paths` grid, `.sh__mark` logo, mobile-overflow) on 2026-06-04, CSS `?v=` `1780515224`→`1780520599`, smoke 4/4 PASS. **The team_50 NO-GO (08f529d baseline) is therefore ALREADY RESOLVED** — do not re-attribute it here.
- `6703313` is an **ancestor of this FIDELITY HEAD** (verified): the live→HEAD `sfa_delivery/` delta is **exactly the FIDELITY changes** (FieldRegistry + 2 controllers + book_crop/book_entry/prov_value/calc_panel + crop-book-deep.css + classb.js + market_product + 2 tests). So this deploy adds **only the FIDELITY delta** on top of the live patch01 state — clean forward deploy, no regression of patch01.
- **SEQUENCING (team_00/team_190 decision):** patch01's own **L-GATE_V R2 is pending on the currently-live `6703313`** (team_99 pre-staged the mandate). Deploying FIDELITY moves live past `6703313`. RECOMMENDED: let team_190 close **patch01 L-GATE_V R2 on `6703313` first**, THEN deploy this FIDELITY HEAD, THEN FIDELITY L-GATE_V on the new live (which must regression-confirm patch01 WI-5/6/mobile still hold — FIDELITY is stacked on top and WI-9 re-verifies mobile). Alternative (faster): deploy FIDELITY now and have team_190 issue both verdicts from one live pass on `f305bbd` (its tree ⊇ patch01). team_00 picks.

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
