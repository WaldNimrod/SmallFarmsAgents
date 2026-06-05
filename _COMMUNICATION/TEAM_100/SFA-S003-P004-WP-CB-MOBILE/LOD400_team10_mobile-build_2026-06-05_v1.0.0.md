# LOD400 — WP-CB-MOBILE build spec (team_100 → team_10) — v1.0.0

**WP:** SFA-S003-P004-WP-CB-MOBILE · **From:** team_100 (Chief Architect) · **To:** team_10 (Build) · **Date:** 2026-06-05
**Design SSoT (team_35 v4):** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-MOBILE/design_handoff_mobile_ui/`
 — `MOBILE_DESIGN_v4.0.0.md` + `README.md` + `design_files/` (8 surface prototypes @375 + `mobile-fixes.css` + 3 base sheets + assets).
**Visual QA:** team_50 @375 (CDP). **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` (SHARED — see §Git discipline).
**Live:** https://sfa.nimrod.bio (uPress, Hebrew/RTL).

---

## 0 · team_100 decisions (RATIFIED — build to these)

1. **Scope = FULL v4 in one WP** (team_00, 2026-06-05). Build *all* of the team_35 v4 package in this WP — including the **calculator rebuild (FIX 6)** and the **3-depth crop IA (Simple/Full/Deep)**. Nothing carved out. (This supersedes the prior "calculator design later" deferral specifically for this consolidated mobile pass.)
2. **D1 RATIFIED — Market default view = TABLE** (desktop + mobile). Server/initial render sets market scope to `table`; the cards⇄table toggle still works and **persists** the user's choice. This is an intentional desktop-reaching change.
3. **D2 RATIFIED — Type-minimum floor** (desktop + mobile). Apply the targeted selector floor in `mobile-fixes.css` → `TYPE MINIMUMS` globally (outside the media query): mono micro ≥ 11px, body-ish ≥ 12px, `.fg dt` 13 / `.fg dd` 14.
   → Both D1 and D2 are **client-requested and team_00-ratified**; they are the *only* sanctioned desktop diffs. **Everything else must be mobile-only (`@media (max-width:480px)`) and must not regress desktop.**

## 1 · Architect verification (assumptions confirmed against the codebase)

| Design assumption | Verified | Note for the build |
|---|---|---|
| Module icons `module-{crop-book,market,calc}.png` | ✅ exist in `sfa_delivery/public_assets/img/modules/` | Use these for hub launchers. **Do NOT** use `heroes/*.webp`. |
| Crop watercolours `wc-<slug>.png` (~70) | ✅ in `public_assets/img/crops/` | Controller maps unknowns → `leaf` fallback (`CropBookViewController.php`). |
| `CropPlantingCalendar` (mig 049) | ✅ `organic_market_agent/db/versions/049_crop_planting_calendar.py` + `crop_book/planting_calendar.py` | Drives calendar + in-season badge. |
| `AssumptionField` editor | ✅ already exists: `sfa_delivery/templates/macros/assumption_field.php` + `crop_book/assumptions.py` | Wire entry points; **do not** build a new editor. |
| CSS load order | ✅ `sfa_delivery/templates/_layout.php` lines 73–81 | `asset_ver` globs the css dir (lines 19–35) → adding `mobile-fixes.css` to the dir + link auto-busts cache. |
| Calc registry `calculators.py` | ✅ `organic_market_agent/crop_book/calculators.py` (+ `calculator_meta.py`) | Map the 14 goal options → `CALC[kind]`. |
| **`baskets`/`סלים` chip** | ⚠️ **PRODUCT category, not crop category** | `baskets` lives in **`products.category`** (market). The **crop** `category` CHECK ([models.py:71](../../../organic_market_agent/crop_book/models.py)) is `vegetables/herbs/baby/legumes/fruits/fruit_trees/grains/cover_crops` — **no `baskets`**. The 11 market chips bind to `products.category`; **do not** conflate with crop category. |

## 2 · Calendar map reconciliation (ALREADY DONE by team_100 — do not redo, extend)

The `IL_general` raw-token leak (defect #2) is fixed at the server/render layer in **`sfa_delivery/templates/macros/crop_calendar.php`** (commits `bac5b69`, `9f60f56`): a `$REGION_LABELS` map renders `IL_general→כל הארץ · IL_north→צפון · IL_center→מרכז · IL_south→דרום · MED_general→אגן הים התיכון`; unknown codes are suppressed (never leaked raw). Tests in `CropCalendarMacroTest.php` lock it (suite 207/207).
**team_10:** when you rebuild the calendar as the `.pcal` grid (FIX 2b), **reuse / extend this same server-side label map** and add the **activity** map (`seed→זריעה · transplant→שתילה · both→both`) and **season** map (`spring/summer/fall/winter/all→אביב/קיץ/סתיו/חורף/כל השנה`). No raw key may appear in visible text anywhere.

---

## 3 · Build approach (from team_35 README §"CSS layer model" + "Implementation order")

The package is engineered as a **portable override layer**. The bulk lands as **(a) ship `mobile-fixes.css` last + (b) add a handful of DOM hooks** in the PHP templates — *not* a rewrite. The HTML files in `design_files/` are **references**, not paste-in production code: recreate inside the existing `sfa_delivery` templates reusing the real class names (`.ccard`, `.pcal`, `.topic`, `.mkt-table`, `.modtile`, `.qb-*`, `.sh__*`).

**RTL discipline (mandatory):** the app is `dir="rtl"`. Use **logical properties** (`inset-inline-*`, `margin-inline-*`, `padding-inline`) — never hard left/right. The only forced LTR is numbers/units (prices, Latin names, month digits) via `dir="ltr"` + `unicode-bidi: isolate`.

### Step 0 · Wire the override layer
- Copy `design_files/mobile-fixes.css` → `sfa_delivery/public_assets/css/mobile-fixes.css`.
- Add `<link rel="stylesheet" href="/public_assets/css/mobile-fixes.css?v=…">` in `_layout.php` **after** `classb.css` (line ~81) so it loads **last**. (Cache-bust is automatic via the css-dir mtime glob.)
- Copy any missing assets the prototypes reference (module icons already present; confirm `assets/` parity).

### Per-surface work (each: template hooks + which CSS section drives it)

| # | Surface | Template(s) | New DOM hooks team_10 adds | CSS section |
|---|---|---|---|---|
| 1 | **Hub / home** | `templates/pages/` hub page | `.modtile--row` launchers w/ real `module-*.png`; `.is-soon` icon-only coming tiles; `.cta` foot | `FIX 5 · HUB` |
| 2 | **Crop entry cards** (defect #4) | crop-book list page + card partial | row `.ccard` (small thumb 66/88px, **no wash**); body order `.ccard__now`→`.ccard__name`→`.ccard__en`→`.cparams`; `.ccard__state` dot; `.ccard--feat` first card; `.seasonchips` (default "עכשיו בעונה"); `.cta--data` foot | `FIX 1 · CROP CARD`, `IN-SEASON` |
| 3 | **Crop page** (defects #1,#2) | `templates/pages/book_crop.php` + `macros/crop_calendar.php` | `.sh__depths` header segmented control (Simple/Full/Deep); stacked `.crophero` (kill overlap); `.pcal` grid (reuse §2 label maps) + `.pcal__legend`/`.pcal__note`; depth content rules (see §4) | `FIX 2a/2b/2c · CROP` |
| 4 | **Market** (defect #3) | `templates/pages/` market + `macros/market_disclaimer.php` | `<details class="mkt-disc">` collapsible disclaimer (closed default); 11 real `.mchips` (incl. `baskets`/`סלים` ← `products.category`); `.aud[data-aud-switch]` view toggle **default=table** (D1); `.mkt-table` 3-col; **`.t-price` stacked LTR number / Hebrew unit** | `FIX 3 · MARKET` |
| 5 | **Calculator** (FIX 6 — full rebuild) | calc page + wire `calculators.py`/`assumptions.py` | ASK: `.qb-goal--grid` 6 buttons + `.qb-more` select (14 → `CALC[kind]`), `.qb-basis` (area/beds/seedlings), time anchor, `.qb__echo`; RESULT: `.qb-session` accumulation, `.qb-answer`+`.qb-break`, **`.qb-assum` → existing AssumptionField editor**, **export = whole session** | `FIX 6 · CALC`, `CALCULATOR builder` |
| 6 | **About** (defect #5) | about page | `.about-intro` + `.about-points` content-first; tiers as secondary expansion (`.about-tiers-h` + two `.tier-group`s: פעיל עכשיו 2 / בקרוב 3) w/ status dots; `.cta` foot | `FIX 4 · ABOUT` |
| 7 | **CTA system** (all surfaces) | shared partial | `.cta--data` (loud, primary), `.cta--suggest` (**inline FORM, never WhatsApp**), `.cta--wa` (**WhatsApp = custom/paid only**) | `CTA SYSTEM` |
| 8 | **Density + type floor** (global) | — | (CSS only) verify desktop holds | `DENSITY`, `TYPE MINIMUMS` (D2) |

## 4 · Crop-page depth rules (the new IA — build carefully)

One route, three view states (`cropDepth: simple|full|deep`); prototype ships them as 3 files (`surface-crop{,-full,-deep}.html`).
- **Simple** (genuinely minimal): essentials `.ess` strip (spacing · DTM · water · method) → calendar → **one key value per topic** (`.keylist`). **No full stat block.**
- **Full**: `.tsum` overview **+ all 17 fields** in collapsible `.topic`/`.fieldgrid` (single-column on mobile).
- **Deep**: same topic structure as Full, but each `.fg dd` opens a `.rng` (range across varieties) + **EX/PR/WR `.srcpill`** row + `.vtable` variety table. Source trust rank: EX>PR>WR.

## 5 · State to implement
`cropDepth` · `marketView` (persist; default `table`) · `marketCategory` (11) · `marketDisclaimerOpen` (default false) · `calcState` (ask|result) + `calcGoal`/`calcBasis`/`calcAnchor`/`calcInputs` · `calcSession` (ordered list → drives session + export-all) · `assumptions` (via AssumptionField) · `seasonFilter` (cards, current-month in-season).

## 6 · Acceptance (team_50 @375 — from MOBILE_DESIGN §8)
No clipping; tight margins · hub real `module-*.png` + icon-only coming + CTA · cards small thumb (no wash) + in-season badge + CTA · depths (Simple minimal / Full all-fields+overview / Deep +ranges/varieties/sources) · market disclaimer collapses, 11 chips incl. סלים, **price reads correct RTL**, table default + cards toggle · calc 6+dropdown(14) + session accumulates + export-all + assumptions editable · about content-first/tiers-below · CTAs (suggest=form, WhatsApp=custom-only) · type floor honored (desktop too). **Desktop must not regress except D1+D2.**

## 7 · Open items routed to data owners / team_00 (non-blocking for build start)
1. Calculator **session persistence scope** — per-device vs account (team_00). Default to per-device/session for v1 unless told otherwise.
2. `goal → CALC[kind]` + `basis → operand` mapping — confirm with `calculators.py` owner.
3. AssumptionField entry points — calc result (primary) + crop-page calculators + anywhere an assumption feeds a number.
4. Calendar `peak`-month source rule; region-overlay selector (reserved).

## 8 · Git discipline (shared branch)
- Build **git-isolated**; **team_100 integrates/commits** (per handoff + memory `feedback_subagent_git_isolation`). Do NOT let the build session move branch refs or commit on the shared branch.
- The `ui-polish` branch is shared with a parallel S004 session + an _aos auto-syncer. Commit defensively (explicit paths), verify ancestry after every dispatch.
- Hold deploy: the IL_general quick-win (`bac5b69`/`9f60f56`) and this whole build ship together in **one team_99 deploy** (team_00 chose "hold for mobile batch").

---
— team_100 · WP-CB-MOBILE LOD400 v1.0.0 · extends team_35 v4 design · 2026-06-05
