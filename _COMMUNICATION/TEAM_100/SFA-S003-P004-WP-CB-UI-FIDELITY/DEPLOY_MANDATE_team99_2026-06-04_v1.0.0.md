# DEPLOY MANDATE — SFA-S003-P004-WP-CB-UI-FIDELITY — team_100 → team_99 — v1.0.0

**Date:** 2026-06-04
**From:** team_100 (Chief System Architect) · **To:** team_99 (server/deploy session) / team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03` · **deploy commit `8ce4fe1`** (current HEAD; FIDELITY blockers + visual quick-wins + 70 crop icons + patch01 WI-8/9) · **scope expanded — see What to deploy**
**Why routed:** this Mac session is deploy-auth-gated (SSH to waldhomeserver blocked by the auto-mode classifier — `reference_prod_deploy_authorization`). Deploy runs from **waldhomeserver** (the uPress-allowlisted FTPS relay), not this Mac.

## Gate state
L-GATE_B **PASS** (team_100, verdict `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/LGATE-B_VERDICT_team100_2026-06-04_v1.0.0.md`). composer 167/167, validate 0 FAIL. Authorized for deploy → external L-GATE_V.

## What to deploy
Deliver the **delivery tier** (`sfa_delivery/`) at branch HEAD `4c9bab2` (delivery-tree identical at `f305bbd`) to uPress (`sfa.nimrod.bio`).

**⚠ BASELINE CORRECTED (per team_99 MSG-HUB-20260604-001, 2026-06-04):** the live site is **already at `6703313`** — team_99 FINAL-deployed **WP-CB-UI-patch01** (WI-1..WI-7, `.cb-paths` grid, `.sh__mark` logo, mobile-overflow) on 2026-06-04, CSS `?v=` `1780515224`→`1780520599`, smoke 4/4 PASS. **The team_50 NO-GO (08f529d baseline) is therefore ALREADY RESOLVED** — do not re-attribute it here.
- `6703313` is an **ancestor of this FIDELITY HEAD** (verified): the live→HEAD `sfa_delivery/` delta is **exactly the FIDELITY changes** (FieldRegistry + 2 controllers + book_crop/book_entry/prov_value/calc_panel + crop-book-deep.css + classb.js + market_product + 2 tests). So this deploy adds **only the FIDELITY delta** on top of the live patch01 state — clean forward deploy, no regression of patch01.
- **SEQUENCING — ✅ RELEASED (team_100, 2026-06-04): DEPLOY IS GO.** Precondition met: **patch01 L-GATE_V R2 PASSED** (team_190/GPT-5.x, 9/9 on live `6703313`) and patch01 is **LOD500_LOCKED** (`_archive/SFA-S003-P004-WP-CB-UI-patch01/ARCHIVE_MANIFEST.md`). team_99 may now deploy this FIDELITY HEAD. This deploy ALSO carries **patch01 WI-8/WI-9** (`/crop-book/table` @375 RTL-overflow fix, `c7b4368`/`e798bc8`) live — clearing the one deferred residual from patch01 R2. After deploy → team_190 FIDELITY L-GATE_V on the new live (must regression-confirm patch01 C1–C9 + WI-5/6/mobile still hold).

## ⚠ Expanded scope since the original GO (deploy commit advanced `4c9bab2`→`8ce4fe1`)
This deploy now ALSO carries the crop-book **visual remediation** team_00 requested:
- **Card grid restored** to the team_35 168px template (was over-densified 120px); **crop detail page centered** (`.cb-crop-detail max-width:1120px` — fixes the full-width stretch); **toggle aligned**.
- **70/70 crops now have watercolor art** (was 14): 14 recovered via slug-map fix + **43 new Devora masters** generated, all knocked out to transparent. → **67 new/changed image files** under `sfa_delivery/public_assets/img/crops/wc-*.png` (~49 MB) **MUST upload** — not just CSS/templates. Confirm the FTPS mirror includes `public_assets/img/crops/`.
- Maps wired in `CropBookViewController.php` (`WC_ART`) + `book_entry.php` (`$wc_art_map`). composer **192/192**, validate 0 FAIL.

## How (canon)
- Runbook: `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`
- Script: `scripts/ftp_deploy_sfa_ui.sh` (FTPS→uPress; `prot_c`, port 21 explicit TLS, IP allowlist — `reference_upress_ftps`).
- **Bump the asset version** so CSS/JS cache-busts (`?v=` advances) — fixes are in `crop-book-v1.css`, `crop-book-deep.css`, `classb.js`, templates.
- **Ensure the image mirror runs** — the 67 new `public_assets/img/crops/wc-*.png` are the visible payload; a CSS-only deploy would ship the layout fix but leave crops on the generic glyph.

## Post-deploy smoke (team_99, then hand to team_190)
On the LIVE site, confirm the served assets advanced and the fixes are live:
1. `/crop-book/lettuce/` — numbers formatted (no `59.043478`, no `.000000`), Hebrew units (`ס״מ/ימ׳/שבועות`, no `cm/days/weeks`), **one** hero (no duplicate "חסה", no green blob).
2. `/market/` — category chips in Hebrew (no `root_vegetables/legumes_fresh/…`).
3. `/crop-book/` — filter labeled **"עונה"** (a `<select>`: קיץ/חורף/אביב/סתיו); `?season=summer` AND `?dtm_max=60` each return a non-empty, correct set; "שאלות מובילות" card reads **3 שאלות** (not 12) and its summer/winter/fast links land on non-empty results.
4. `/crop-book/` — **crop cards show watercolor art, not the generic 🌱** (spot-check e.g. עגבנייה/tomato, תפוח-אדמה/potato, תות/strawberry, חיטה/wheat); cards are the larger 168px size; the list is a centered column, not edge-to-edge.
5. Spot-check served images load 200: `/public_assets/img/crops/wc-strawberry.png`, `wc-potato.png`, `wc-wheat.png` (the 43 new ones).
6. Served CSS contains `.cb-paths{display:grid` (WI-5) and `.sh__mark` sizing (WI-6); served `classb.js` defines `window.fetchHistory`; served `crop-book-v1.css` has `.cards-grid` `minmax(168px` and `.cb-crop-detail` `max-width: 1120px`.
7. Write `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_REPORT_v1.0.0.md` with the deployed SHA (`8ce4fe1`), the new `?v=` value, and confirmation the crop images uploaded (count of wc-*.png served).

## Then
Notify team_100; team_100 routes **team_190 (non-Claude) L-GATE_V** design-vs-Board-A/B on the live site (the launch gate) + team_50 re-audit.
