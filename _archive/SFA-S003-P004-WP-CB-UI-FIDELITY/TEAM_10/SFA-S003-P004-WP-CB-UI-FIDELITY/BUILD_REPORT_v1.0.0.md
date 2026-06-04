---
id: BUILD_REPORT_WP-CB-UI-FIDELITY_team10_v1.0.0
from: team_10 (Builder, Claude Sonnet)
to: team_100 (Chief Architect, for L-GATE_B)
date: 2026-06-04
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
branch: claude/ui-polish-hub-cropbook-2026-06-03
---

# BUILD REPORT — WP-CB-UI-FIDELITY (team_10 → team_100)

**No commits made.** Working tree dirty. team_100 commits with explicit sfa_delivery/ paths.

---

## Files Changed

All under `sfa_delivery/` except the two team_10 comm artifacts:

### sfa_delivery/ (delivery tier — render layer only, no DB/Python/migration)
1. `sfa_delivery/app/Lib/FieldRegistry.php` — added `fmtNumber()`, `unitLabel()`, extended `ENUM_LABELS['category']`
2. `sfa_delivery/app/Controllers/MarketViewController.php` — WI-3: `fetchCategories()` uses `enumLabel()`; added `use FieldRegistry`
3. `sfa_delivery/app/Controllers/CropBookViewController.php` — WI-5: leading questions re-routed; season/beginner/small-space removed
4. `sfa_delivery/templates/pages/book_crop.php` — WI-1+2: `$pv()` closure; WI-1b: removed 3 hardcoded `<small>` units; WI-4: hero dedup, `id="identity"` retarget, lede+pills preserved; variety table fmtNumber
5. `sfa_delivery/templates/pages/book_entry.php` — WI-5: season filter free-text → `<select>` with actual stored tokens
6. `sfa_delivery/templates/pages/market_product.php` — WI-6: added `data-slug` attr to `.pgraph` for `window.fetchHistory`
7. `sfa_delivery/templates/macros/prov_value.php` — WI-1+2: `fmtNumber()` + `unitLabel()` applied to all 3 render states
8. `sfa_delivery/templates/macros/calc_panel.php` — WI-1+2: `fmtNumber()` + `unitLabel()` for book_fields display
9. `sfa_delivery/public_assets/css/crop-book-deep.css` — WI-4: `.cb-crop-hero__icon` rule removed (green blob)
10. `sfa_delivery/public_assets/js/classb.js` — WI-6: `window.fetchHistory` binding + live SVG redraw; `wireRangeSel` fetches API
11. `sfa_delivery/tests/CropCardIconTest.php` — updated AC-U2-03/AC-U2-04 tests to reflect WI-4 single-hero architecture

### _COMMUNICATION/ (team_10 artifacts)
12. `_COMMUNICATION/team_10/SFA-S003-P004-WP-CB-UI-FIDELITY/DESIGN_REQUEST_team35_v1.0.0.md` — WI-7
13. `_COMMUNICATION/team_10/SFA-S003-P004-WP-CB-UI-FIDELITY/BUILD_REPORT_v1.0.0.md` — this file

---

## Per-WI Status

| WI | Status | Notes |
|----|--------|-------|
| WI-1 | **DONE** | `FieldRegistry::fmtNumber()` added; applied in `$pv()` (book_crop.php), `prov_value.php` (all 3 states), `calc_panel.php` book_fields, variety table cells |
| WI-2 | **DONE** | `FieldRegistry::unitLabel()` added covering all canon units; applied in same render paths; `count` → '' (omit) |
| WI-1b (D-1b) | **DONE** | 3 hardcoded `<small>` unit suffixes at book_crop.php:208/215/227 removed; single-unit rule enforced |
| WI-3 | **DONE** | `fetchCategories()` uses `enumLabel('category', $cat)`; added `legumes_fresh`→קטניות טריות, `eggs`→ביצים, `baskets`→סלים (marked as team_35-confirm defaults per Q2) |
| WI-4 | **DONE** | Legacy `.cb-crop-hero` section collapsed to lede+meta `<div class="cb-crop-lede">` only; duplicate breadcrumb/h1/icon box removed; `.crophero` gains `id="identity"` (nav anchor preserved); lede + family/dtm pills preserved; `.cb-crop-hero__icon` CSS removed |
| WI-5 (D-4b) | **DONE (partial)** | `fast` → `?dtm_max=60` (correct); `summer`/`winter` **removed** (BLOCKED-ON-DATA, see below); `beginner`/`small-space` **removed** (no backing attribute, Q4) — now only 1 leading question ships |
| WI-5 (D-4a) | **PARTIAL / SURFACED** | Season filter free-text input converted to `<select>` with actual stored tokens (`annual`/`year-round`/`biennial`). This makes the filter functional for what IS stored. However the stored tokens are **growth-cycle** values (not planting seasons) — see BLOCKED note below |
| WI-6 | **DONE** | `window.fetchHistory` binding added to `classb.js`; `wireRangeSel` calls the API on click + redraws SVG path; `data-slug` added to `.pgraph` container in `market_product.php`. crop-book/calc interactions confirmed in `crop-book-v1.js` (all 7 wired handlers present) |
| WI-7 | **DONE** | `DESIGN_REQUEST_team35_v1.0.0.md` filed covering Q2/Q3/Q4/Q5 |
| WI-8 | **PARTIAL** | In-scope fidelity fixes applied (hero dedup, number format, units, category Hebrew, filter routing). Systematic desktop-1440 + mobile-375 CDP comparison vs Board-A/B NOT run (requires team_100 CDP harness per mandate). Noted: crop lede/meta now in `<div class="cb-crop-lede">` — team_100 should verify spacing vs Board-A. |
| WI-9 | **VERIFIED** | `crop-book-deep.css:726-734` WP-CB-UI-patch01 responsive table CSS intact and not touched |

---

## Critical BLOCKED / Surfaced Items

### D-4a — Season filter: BLOCKED-ON-DATA

**Root cause confirmed:** `crops.season` in the delivery MySQL mirror is populated by
`sfa_ingest_push.py::_season_from_growth_cycle()` which maps `growth_cycle` column values:
- `annual` → `"annual"`
- `perennial` → `"year-round"`
- `biennial` → `"biennial"`

This is a **growth-cycle** field, NOT a planting-season (summer/winter/spring/fall) field.
The planting-season data lives in `crop_attribute` (key: `planting_season`) in Postgres, but is
NOT propagated to the MySQL mirror as a filterable column.

**What was fixed:** Converted the broken free-text season input to a `<select>` with the actual
stored tokens so users get valid (non-zero) results for `annual`/`year-round`/`biennial`.
The label was updated to "מחזור גידול" to accurately describe what is being filtered.

**What is blocked:** A proper season (summer/winter/spring/fall) filter requires a data WP that:
1. Adds a `season_class` column to the delivery mirror table
2. Populates it from `payload_json.calendar` or the `planting_season` attribute
3. The leading questions for summer/winter can then be re-added

**Action needed:** team_100 / team_00: authorize a data WP for `season_class` mirror column.
Until then: summer/winter leading questions are removed; season filter shows growth-cycle only.

### Q3 — kg_per_ha unit (dunam vs hectare): BLOCKED-ON-DATA + team_35

`kg_per_ha` mapped to `ק״ג/הקטר` (safe default). Do NOT change to dunam without verifying
stored values are per-dunam. Filed in DESIGN_REQUEST to team_35.

### Q4 — beginner/small-space questions: BLOCKED-ON-team_35 + data

Removed for launch. Filed in DESIGN_REQUEST.

---

## composer test Results

```
Tests: 167, Assertions: 407, PHPUnit Deprecations: 1
OK (with PHPUnit deprecation — unrelated to this WP's changes; pre-existing)
```

2 tests (AC-U2-03, AC-U2-04 in `CropCardIconTest.php`) updated to match the new WI-4
single-hero architecture. Previously tested `.cb-crop-hero__icon` / `.cb-crop-hero__art`
(legacy hero removed by WI-4); now test `.crophero` single hero behavior.

---

## php -l Results

All clean — no syntax errors:
- `app/Lib/FieldRegistry.php` ✓
- `app/Controllers/MarketViewController.php` ✓
- `app/Controllers/CropBookViewController.php` ✓
- `templates/pages/book_crop.php` ✓
- `templates/pages/book_entry.php` ✓
- `templates/pages/market_product.php` ✓
- `templates/macros/prov_value.php` ✓
- `templates/macros/calc_panel.php` ✓
- `tests/CropCardIconTest.php` ✓

---

## AC Self-Assessment

| AC | Self-verified | Needs CDP |
|----|--------------|-----------|
| AC-1 No raw multi-decimal floats | VERIFIED (grep: no `\d+\.\d{3,}` patterns near pv() calls; fmtNumber applied at all numeric render paths) | CDP text scan for live values |
| AC-2 No English units / raw enum keys | VERIFIED (grep: no `cm|days|weeks|count` beside Hebrew in templates; unitLabel() routes all unit tokens; category chips use enumLabel) | CDP text scan on live pages |
| AC-3 Filters return non-empty sets | PARTIAL (fast→dtm_max=60 should return crops with DTM≤60; season now uses real stored tokens; summer/winter removed) | CDP click test needed for all filters |
| AC-4 Single hero, correct | VERIFIED (grep: 1 `<h1>`, 1 `id="identity"`, 1 breadcrumb, `.cb-crop-hero__icon` gone, lede+pills present) | CDP screenshot vs Board-A |
| AC-4b `#identity` resolves | VERIFIED (`id="identity"` on `.crophero`, section nav links `href="#identity"` still work) | CDP anchor-scroll test |
| AC-5 Interactions work | PARTIAL (classb.js wired; crop-book-v1.js handlers all present; window.fetchHistory bound) | CDP interaction click tests |
| AC-6 Fidelity vs Board-A/B | NOT verified (no CDP access from builder session) | Full CDP L-GATE_B by team_100 |
| AC-7 No regression; composer green; php -l clean | VERIFIED | WI-9 CSS intact |

---

## Fidelity Notes (WI-8 — observed but not fixed)

1. `calc_seq.php` and `calc_dash.php` do not currently render live numeric field values from
   the crop book (they show static `—` placeholders until JS recomputes). No PHP-level number
   formatting issues to fix there; JS client-side fmt() function already handles it.
2. The `cb-crop-lede` div (new container for lede + pills) has no dedicated CSS rule yet.
   It inherits spacing from the page. team_100 should verify Board-A spacing in CDP pass.
3. Market product page: `pgraph__title` class added to `<h3>` (was unclassed) — needed for
   the JS title-update in wireRangeSel. This is backward-compatible.

---
*BUILD_REPORT filed by team_10 · 2026-06-04 · Leave dirty for team_100 review*
