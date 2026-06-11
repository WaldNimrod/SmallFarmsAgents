---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-WI7_v1.0.0
title: team_99 — WP-CB-UI-WI7 (THIRD deploy) SUCCESS — F-REA-001 basket unit + Q3 dunam + search wc + tile mono-badge + legacy 301 all live
status: SUCCESS
date: 2026-06-04
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_50 (re-audit), team_190 (L-GATE_V if routed), team_00 (Principal)
parent_mandate_thread:
  - earlier FIDELITY v1 deploy (4c9bab2) — DEPLOY_REPORT_v1.0.0
  - FIDELITY v2 deploy (acca9b2) — DEPLOY_REPORT_v2.0.0
  - THIS WI7 deploy (7fb3cf7) — consolidated QA-reaudit + WI-7 fixes
wp: SFA-S003-P004-WP-CB-UI-WI7
branch: claude/ui-polish-hub-cropbook-2026-06-03
deployed_sha: 7fb3cf7  # last sfa_delivery-touching commit (the WI7 fix)
branch_tip_at_deploy: 755330f  # S004-WP002 plan commit on top (docs-only)
last_live_sha_pre_deploy: acca9b2
sfa_delivery_content_delta_files: 7  # 5 PHP + 2 tests; lftp re-mirrored 82 files due to git-reset-mtime touch
---

# WP-CB-UI-WI7 — Deploy Report (THIRD round on top of FIDELITY v2)

## 1. Verdict

**SUCCESS.** All 5 mandate smoke checks PASS. F-REA-001 (P0 basket unit), Q3 dunam, F-REA-002 (search watercolor), F-REA-003 (hub eyebrows), and the legacy `/crop-book/table?category=…` → 301 redirect are all live.

## 2. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `755330f` (`git reset --hard origin/...`).
  - `755330f` = `plan(S004-WP002): external CI triangulation` — docs-only, no sfa_delivery delta.
  - `7fb3cf7` = `build(WI7): consolidated QA-reaudit + WI-7 fixes (F-REA-001 P0 + MINORs + Q3/Q5)` — the actual code commit deployed.
- **Content delta** (`acca9b2..HEAD` in `sfa_delivery/`):
  ```
  app/Controllers/CropBookViewController.php
  app/Lib/FieldRegistry.php
  templates/pages/hub_home.php
  templates/pages/market_list.php
  templates/pages/market_product.php
  tests/ClassBRouteTest.php             (not deployed — tests/ excluded by script)
  tests/CropBookV1MacroTest.php          (same)
  ```
  Net delta in deployable surface: **5 PHP files** as the mandate specified.
- **lftp stats:** **82 transferred · 82 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.** The mirror re-uploaded most of `sfa_delivery/` because `git reset --hard` refreshed working-tree mtimes; **content** delta is the 5 PHP files. No regression: file bytes are identical to origin's HEAD for the unchanged files.
- **Deploy log on host:** `/tmp/sfa_wi7_deploy.log`.

## 3. Smoke evidence — per mandate §3 (a–e)

### §3a — F-REA-001 basket unit fixed — **PASS**

```
/market/                  basket_large hits:  0        ✅ (raw token gone from visible text)
/market/                  לסל hits:           9        ✅ (per-basket Hebrew unit shown 9×)
                          context: <div class="pcard__unit">לסל</div>
                                   <span class="per">לסל</span>
/market/basket_large      basket_large hits:  1
                          context: <link rel="canonical" href="https://…/market/basket_large">
                          status: 404 (slug isn't a real product — basket_large is a UNIT type)
                          → 0 hits in visible UNIT text; the 1 hit is in <link rel=canonical> of a 404 page
```
✅ The MAJOR finding both QA engines cared about is resolved on the live `/market/` list page.

### §3b — Q3 dunam — **PASS**

```
/crop-book/lettuce/?depth=full   ק״ג/דונם hits:  1
context: <span class="pv-validated">6.73<small> ק״ג/דונם</small></span>
```
✅ Value rendered with ÷10 conversion (`6.73`) and the Hebrew "kg/dunam" unit suffix.

### §3c — F-REA-002 search watercolor — **PASS**

```
GET /crop-book/search?q=עגבנייה (tomato in Hebrew)
img/crops/wc- hits in results:    1
matched file:  img/crops/wc-tomato.png
```
✅ Search results now render the watercolor crop image (not the generic glyph fallback).

### §3d — F-REA-003 hub tile mono-badges removed — **PASS**

```
GET /
pattern modtile__title<small>UPPERCASE matches:  0
all 8 visible hub tile titles (Hebrew only):
  ספר גידולים · מחירון · מחשבון לחקלאי · יומן השדה
  תכנון עונה · ניהול לקוחות · מעקב יבול ומלאי · חיבור Tend / חשבונית-ירוקה
```

Compare to the patch01 round (deployed earlier today) where I saw
`<div class="modtile__title">יומן השדה<small>FIELD-LOG</small>` — the
English `<small>FIELD-LOG</small>` mono-badge is now gone. ✅

### §3e — Legacy redirect `/crop-book/table?category=…` → 301 — **PASS**

```
GET /crop-book/table?category=summer
HTTP/2 301
location: /crop-book/?season=summer
server: cloudflare
```
✅ Legacy URL → new `?season=` filter URL.

## 4. What was touched / not touched

- ✅ Server checkout: branch reset to `755330f` (sfa_delivery content == `7fb3cf7`).
- ✅ `sfa_delivery/` mirrored (82 transferred / 82 replaced — content delta = 5 PHP files; rest are mtime-refreshes from git reset).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` written under the new `SFA-S003-P004-WP-CB-UI-WI7/` folder.
- ✅ `MSG-HUB-20260604-005` to team_100.
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations/data, no deploy-script change, no Cloudflare touch (no purge issued — Pragma:no-cache in probes was sufficient), no `.env` change.
- ❌ No L-GATE_V verdict self-issued.

## 5. Notes

- **CSS not changed in WI7**: per mandate "No CSS change → `?v=` may not advance; the changes are server-rendered PHP." Confirmed — the assets `?v=1780576560` from FIDELITY v2 remain. Mandate-anticipated.
- **Cloudflare HTML cache**: did not require purge in this round — the live probes with `Pragma: no-cache` headers (and `?cb=$(date +%s)` cache-busters) returned current HTML reflecting the new code. If team_50 hits stale HTML during re-audit, a CF purge of HTML routes may help.
- **Stack-trace tests** (`tests/ClassBRouteTest.php`, `tests/CropBookV1MacroTest.php`): excluded from deploy by `scripts/ftp_deploy_sfa_ui.sh` `--exclude '^tests/'` rule. Test deltas verified during team_100's L-GATE_B (composer 167/167 reported); not in scope for FTPS.

## 6. Handoff

→ **team_100**: WI7 closure-set complete on live. Please route **team_50 re-audit** on live `7fb3cf7` (the MAJOR F-REA-001 finding both engines cared about is now resolved; the four other items also live). Optionally route **team_190 L-GATE_V** if team_100 considers this iteration in scope of the active gate cycle.
→ **team_50**: stand by for re-audit routing.
→ **team_190**: stand by for L-GATE_V routing if team_100 sees fit.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-04
