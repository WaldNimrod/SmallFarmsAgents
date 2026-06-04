---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-FIDELITY_v2.0.0
title: team_99 — WP-CB-UI-FIDELITY SECOND deploy SUCCESS — 67 crop watercolors live, all 5 smoke PASS
status: SUCCESS
date: 2026-06-04
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (FIDELITY L-GATE_V non-Claude), team_50 (re-audit), team_00 (Principal)
parent_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_MANDATE_team99_2026-06-04_v1.0.0.md  # routes "SECOND deploy @ acca9b2"
prior_report: ./DEPLOY_REPORT_v1.0.0.md  # FIRST deploy @ 4c9bab2 (10 code files, no images)
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
branch: claude/ui-polish-hub-cropbook-2026-06-03
deployed_sha: acca9b2  # last sfa_delivery-touching commit
branch_tip_at_deploy: 2255f89  # ops/route doc commit on top; identical sfa_delivery
css_version_pre: 1780532267
css_version_post: 1780576560
payload_summary: "67 wc-*.png watercolors + CSS + templates + classb.js + controllers — 80 files total"
prior_finding_status: RESOLVED — v1 §4.1 prov__srcval raw 6-decimal fix verified (0 hits at depth=drill)
---

# WP-CB-UI-FIDELITY SECOND deploy — Report

## 1. Verdict

**SUCCESS.** All 5 mandate §5 smoke checks PASS. The IMAGE-COUNT GATE was met (67 `wc-*.png` transferred in the lftp run — not the failure-mode of "~10 files only"). The v1 §4.1 `prov__srcval` finding is now RESOLVED in v2 (`/crop-book/lettuce/?depth=drill` returns 0 raw 6-decimals).

## 2. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `2255f89` (after `git reset --hard origin/...`). Last sfa_delivery-touching commit = `acca9b2` (deployed SHA per mandate intent + per the file-set in the mirror).
- **Pre-flight gates — all PASS:**
  - 72 `wc-*.png` files in worktree ✅
  - 3 sample files present (strawberry 870 KB, potato 828 KB, wheat 902 KB) ✅
  - 85 `=> 'wc-` mappings in `CropBookViewController.php` (= 28+14+43 per mandate) ✅
  - `minmax(168px` rule at `crop-book-v1.css:34` ✅
  - `max-width: 1120px` rule at `crop-book-v1.css:564` ✅
- **lftp stats:** **80 transferred · 36 in-place replacements · 3 mkdirs · exit 0 · no `Fatal`/`530`/`max-retries`.**
  - **67 wc-*.png watercolors transferred ✅** (the critical image-payload gate)
  - Plus 13 code/CSS files (controllers, macros, templates, classb.js, css)
- **Deploy log on host:** `/tmp/sfa_fidelity_deploy2.log`.

## 3. Smoke evidence — per mandate §5 (a–e)

### §5a — Crop image served at 200

```
$ curl -sI https://sfa.nimrod.bio/public_assets/img/crops/wc-strawberry.png
HTTP/2 200
content-type: image/png
```
✅

### §5b — `/crop-book/` HTML references wc-* images (not generic glyph)

```
img/crops/wc-* references in HTML:   71
distinct wc-*.png filenames:         69
First 10 distinct: wc-anise-hyssop / artichokes / arugula / basil / bay /
                   beans-default-pole-climbing / beet / blackberry /
                   broccoli / cabbage / …
```
✅

### §5c — Served `crop-book-v1.css` has BOTH restored values + `?v=` advanced

```
URL on /crop-book/:  crop-book-v1.css?v=1780576560      (was 1780532267 → advanced ✓)
minmax(168px hits:   1
max-width: 1120px:   1
```
✅ Both `.cards-grid` columns rule (line 34) and `.cb-crop-detail` page-centering (line 564) are served live.

### §5d — `/crop-book/lettuce/?depth=drill` raw 59.043478 = 0

```
59.043478 hits:                   0   (v1 finding RESOLVED)
prov__srcval class hits:          1   (the class is still in the DOM, but no longer renders the raw 6-decimal)
other 6-decimal raw numbers:      0
```
✅

### §5e — Regressions intact

```
single hero on /crop-book/lettuce (<h1>חסה</h1>):   1  (no duplicate)         ✅
Hebrew units on lettuce (ס״מ/ימ׳/שבועות sum):       23                          ✅
Hebrew market chip sample (דלועיים):                1  (chips are Hebrew)     ✅
all served ?v= values found on /crop-book/:        ?v=1780576560 (single, advanced past 1780532267)  ✅
```

## 4. Payload manifest (file categories transferred)

| Category | Count |
|---|---|
| `public_assets/img/crops/wc-*.png` (new watercolors) | **67** |
| Other sfa_delivery code/CSS/JS/templates | 13 |
| **Total transferred** | **80** |
| Removed (in-place replacements) | 36 |
| Directories created | 3 |

The 67 watercolors map to the 85 `=> 'wc-…'` entries in
`CropBookViewController.php` (some files are shared across the
28+14+43 = 85 crop/family/variety entries; 67 distinct files cover them).

## 5. What was touched / not touched

- ✅ Server checkout: branch reset to `2255f89` (sfa_delivery == `acca9b2`).
- ✅ `sfa_delivery/` mirrored to uPress (80 transferred / 36 replaced / 3 mkdirs).
- ✅ This `DEPLOY_REPORT_v2.0.0.md` written (new version — v1 retained for FIRST-deploy audit trail).
- ✅ `MSG-HUB-20260604-004` to team_100.
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations/data, no deploy-script change, no Cloudflare touch, no `.env` change.
- ❌ No L-GATE_V verdict self-issued.

## 6. Handoff

→ **team_190 (non-Claude)**: FIDELITY L-GATE_V design-vs-Board-A/B on live `acca9b2` is now executable (the visual round — wc watercolors render on `/crop-book/`, crop detail layout centered at 1120px, grid uses minmax(168px) responsive columns). team_100 will route.
→ **team_100**: please route 190 (the launch gate) + team_50 re-audit. v1 §4.1 finding (`prov__srcval`) is RESOLVED in v2.
→ **team_50**: stand by for re-audit routing from team_100.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-04
