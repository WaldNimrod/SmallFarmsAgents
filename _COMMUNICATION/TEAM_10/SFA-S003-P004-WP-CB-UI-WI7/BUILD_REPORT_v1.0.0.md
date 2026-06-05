# BUILD REPORT — WP-CB-UI-WI7 render-layer fixes
**Artifact:** `BUILD_REPORT_v1.0.0.md`
**Team:** team_10 (Builder, Sonnet)
**Branch:** `claude/ui-polish-hub-cropbook-2026-06-03`
**Date:** 2026-06-04
**Scope:** `sfa_delivery/` only — render-layer; no DB/data mutation; no `_aos/` edits.

---

## Summary

| Item | ID | Status | Files Changed |
|------|----|--------|---------------|
| 1 | F-REA-001 (P0): basket units | DONE | `market_list.php`, `market_product.php` |
| 2 | F-REA-002: search watercolor | DONE | `CropBookViewController.php` |
| 3 | F-REA-003 / WI-7 Q5: English menu eyebrows | DONE (partial — see notes) | `hub_home.php` |
| 4 | WI-7 Q3: kg_per_ha ÷10 + dunam label | DONE | `FieldRegistry.php` |
| 5 | INFO: legacy tableView redirects | DONE | `CropBookViewController.php` |
| 6 | F-REA-005/006: calc pixel polish | DEFERRED (per mandate) | — |

---

## Item 1 — F-REA-001 (MAJOR/P0): basket units

**Root cause addressed:** `basket_large`/`basket_medium`/`basket_small` fell through to the default arm, which prepended `ל` + the raw English token.

**Fix:**
- `sfa_delivery/templates/pages/market_list.php` — `sfa_unit_label()`: added `'basket_large', 'basket_medium', 'basket_small' => 'לסל'` arm.
- `sfa_delivery/templates/pages/market_product.php` (~L49) — inline `match(...)`: same three arms added.
- **Hardened default** in both: `preg_match('/^[a-z][a-z_]*$/', $norm) ? 'ליחידה' : ('ל' . $unit)` — any unmapped raw English snake_case now returns `'ליחידה'` instead of leaking.
- Existing `kg`/`unit`/`bunch` arms and Hebrew passthrough unchanged.

**Tests added (ClassBRouteTest.php):**
- `testSfaUnitLabelBasketLarge` — asserts basket_large/medium/small → `לסל`
- `testSfaUnitLabelHardenedDefault` — asserts English snake_case → `ליחידה`; Hebrew passthrough preserved; `kg` → `לק״ג`
- `testMarketListBasketProductNoEnglishUnit` — integration: market list with basket_large product must contain `לסל`, not `לbasket_large`

---

## Item 2 — F-REA-002 (MINOR): search results watercolor

**Fix:** `CropBookViewController::search()` now resolves the watercolor PNG per slug using `self::WC_ART` (same map used by `entry()` / `detail()`). Sets `icon_url = '/public_assets/img/crops/wc-<slug>.png'` when present; empty string otherwise. `crop_card.php` macro already renders `<img class="crop-card__art">` when `icon_url` is set and falls back to glyph when empty — no template change needed.

**Tests added (ClassBRouteTest.php):**
- `testSearchResultWatercolorPresentForKnownCrop` — `tomato` query renders `crop-card__art` + `wc-tomato.png`
- `testSearchResultFallsBackToGlyphForUnknownCrop` — unknown slug renders `gj-cropcard` (glyph), no `crop-card__art`

---

## Item 3 — F-REA-003 / WI-7 Q5: English eyebrows

**hub_home.php — DONE:**
- Removed `<small><?= $h(strtoupper($m_id)) ?></small>` from `modtile__title` in the dynamic open-tools loop (L120).
- Also removed the hardcoded `<small>FIELD-LOG</small>` from the static Field-Log teaser tile.
- The Hebrew `$m_name` already labels each tile; no information lost.
- Audience-card eyebrows (`GARDENER`/`FARMER`/`PLANNER`) are untouched per Q5=B decision.

**hub_tiers.php (`/about`) — LEFT UNCHANGED (noted):**
The `/about` page tier cards carry `<span class="tier-row__badge-en en"><?= strtoupper($tier_key) ?></span>` (OPEN/BETA/COMING/PAID/CUSTOM). This is an educational tier-system page that deliberately explains the tier identifiers to users. The `en` CSS class signals intentional bilingual display. The mandate flags this as "risky/ambiguous if not sure." Leaving it unchanged is the safe choice; team_35 or team_100 should decide the final disposition.

**Tests added (ClassBRouteTest.php):**
- `testHubHomeTileNoEnglishModuleId` — asserts no `modtile__title`...`<small>[A-Z-]+</small>` in hub home output

---

## Item 4 — WI-7 Q3: kg_per_ha ÷10 + ק״ג/דונם

**Fix (`sfa_delivery/app/Lib/FieldRegistry.php`):**
- `fmtNumber()`: when `strtolower($unit) === 'kg_per_ha'`, divide `$f` by 10 before formatting. Positioned before the discrete-units branch so `days`/`count` logic is unaffected.
- `unitLabel()`: `'kg_per_ha' => 'ק״ג/דונם'` (was `'ק״ג/הקטר'`; removed the Q3 comment).
- `LABELS['nutrient_removal_n_kg_per_ha'][1]`: explainer text changed from `'ק״ג להקטר'` → `'ק״ג לדונם'`.

**Tests added (CropBookV1MacroTest.php):**
- `testFmtNumberKgPerHaDividedByTen` — `fmtNumber(80,'kg_per_ha') === '8'`, `fmtNumber(67,'kg_per_ha') === '6.7'`, `fmtNumber(100,'kg_per_ha') === '10'`
- `testFmtNumberOtherUnitsNotAffected` — days/count/cm/kg_per_bed_m/empty all return `'80'` (no ÷10)
- `testUnitLabelKgPerHaIsDunam` — `unitLabel('kg_per_ha') === 'ק״ג/דונם'`

---

## Item 5 — INFO: legacy /crop-book/table route redirects

**Fix (`CropBookViewController::tableView()`):** Added `$legacyRedirects` static map at top of method:

```
'summer'      → /crop-book/?season=summer   (301)
'winter'      → /crop-book/?season=winter   (301)
'fast'        → /crop-book/?dtm_max=60      (301)
'beginner'    → /crop-book/                 (301)
'small-space' → /crop-book/                 (301)
```

Real botanical `category` values pass through to the existing SQL filter unchanged.

**Tests added (ClassBRouteTest.php):**
- `testTableViewLegacySummerRedirects` — 301 → `/crop-book/?season=summer`
- `testTableViewLegacyFastRedirects` — 301 → `/crop-book/?dtm_max=60`
- `testTableViewLegacyBeginnerRedirects` — 301 → `/crop-book/`
- `testTableViewRealCategoryNotRedirected` — `?category=vegetables` still returns 200

---

## Item 6 — DEFERRED

Calculator pixel-polish (F-REA-005/006) — needs design detail from team_35. Not attempted per mandate.

---

## Composer / PHP lint results

```
php -l: 0 errors on all 7 edited files
  - templates/pages/market_list.php     OK
  - templates/pages/market_product.php  OK
  - app/Controllers/CropBookViewController.php OK
  - app/Lib/FieldRegistry.php           OK
  - templates/pages/hub_home.php        OK
  - tests/CropBookV1MacroTest.php       OK
  - tests/ClassBRouteTest.php           OK

composer test: 205/205 PASS (up from 192 baseline — 13 new tests added)
  Assertions: 564
  PHPUnit deprecation: 1 (pre-existing, not introduced by this build)
```

---

## Files changed

| File | Change type |
|------|-------------|
| `sfa_delivery/templates/pages/market_list.php` | Added basket arms + hardened default in `sfa_unit_label()` |
| `sfa_delivery/templates/pages/market_product.php` | Added basket arms + hardened default in inline `match()` |
| `sfa_delivery/app/Controllers/CropBookViewController.php` | `search()`: added `icon_url` via WC_ART; `tableView()`: legacy redirects |
| `sfa_delivery/app/Lib/FieldRegistry.php` | `fmtNumber()` ÷10 for kg_per_ha; `unitLabel()` dunam label; LABELS explainer |
| `sfa_delivery/templates/pages/hub_home.php` | Removed English `<small>` module-id from all modtile titles |
| `sfa_delivery/tests/CropBookV1MacroTest.php` | 3 new tests: fmtNumber kg_per_ha ÷10 + other units safe + unitLabel dunam |
| `sfa_delivery/tests/ClassBRouteTest.php` | 10 new tests: basket units, hardened default, market list integration, search watercolor, hub tile eyebrow, 4 legacy redirects |

---

**Handback to team_100.** No git operations performed.
