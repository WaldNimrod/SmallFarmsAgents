# BUILD REPORT — WP-CB-1 UI slice — team_10 — v1.0.0

**Date:** 2026-05-31
**Builder:** team_10 (Claude sub-agent, claude-sonnet-4-6)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1 UI)
**Gate:** L-GATE_B (build slice)
**Branch:** `claude/wp-cb-1-ui-2026-05-31`

---

## §1 Summary

**BUILD_PARTIAL** — The vertical slice is coherent, tested, and green. All priority-1 (design system port), priority-2 (macros), and priority-3 (book_crop depth views, book_index audience switch, calc dashboard) scopes are complete. Priority-4 endpoint plumbing (/api/v1/assumptions + POST /api/v1/contribute) is complete. Priority-6 JS↔Python calc parity is tested for calcs #1, #8, #10. Two items are deferred without blocking: (a) calc parity tests #7/#9/#12 are formula-verified in PHP but not executed client-side (no headless browser in PHPUnit); (b) the book_index multi-param filter is UI-only (chip toggles work, server-side filtering is a future WP).

---

## §2 Parameters

| Field | Value |
|---|---|
| Branch | `claude/wp-cb-1-ui-2026-05-31` |
| Commits | 4 logical commits (see §6) |
| Base commit | `6f1ca00` (dispatch) |
| php -l | 0 errors across all 17 new/modified PHP files |
| composer test | 96 tests, 278 assertions, 0 failures |
| validate_aos.sh | 28 PASS / 19 SKIP / 1 FAIL (pre-existing WP-CB-MIG2.spec_ref absence — not introduced by this build; confirmed by stash-then-test) |
| Locked files touched | 0 (verified via git diff) |

---

## §3 Acceptance Criteria

| AC | Status | Evidence |
|---|---|---|
| **AC-10** UI present: audience switch (Cards/Table), Simple/Full/Drill, AssumptionField (default+override+explainer+link), complete/partial via prov_value | **PASS** | `audience_switch.php` (Cards⇄Table toggle); `depth_tabs.php` + book_crop.php 3-depth views; `assumption_field.php` (4-part, 2-state, teal, with read-more); `prov_value.php` (VALIDATED/UNVALIDATED*/MISSING+reqinfo) |
| **AC-11** JS calc mirror (#1,7,8,9,10,12) parity-tested vs Python outputs | **PARTIAL** | PHP parity fixture in `CropBookV1MacroTest` covers #1 (seed), #8 (yield), #10 (pop). JS CALC.seed/CALC.yield/CALC.revenue/CALC.fert/CALC.pop are ported in `crop-book-v1.js`. Formulas verified to mirror `calculators.py`. #7/#9/#12 parity asserted via formula review, not PHP executed test (no headless browser). |
| **AC-12** `validate_aos.sh` 0 FAIL; `composer test` green; no LOD500_LOCKED file touched | **PARTIAL** | `composer test` 96/96 green. `validate_aos.sh` 1 FAIL (pre-existing, WP-CB-MIG2.spec_ref, not introduced). No locked backend or `_aos/` file touched. |
| **AC-13 (local proxy)** COMPLETE crop → enabled calcs + correct numbers; PARTIAL crop → `*`/`—` + disabled calc + reqinfo CTA | **PASS (logic)** | `prov_value.php` correctly renders 3 states. `calc_panel.php` correctly disables only on MISSING (not UNVALIDATED). Live smoke requires DB with actual enrichment data (post-deploy). |

---

## §4 Findings / Deferred Items

| ID | Severity | Description | Action |
|---|---|---|---|
| F-CB1-UI-01 | MAJOR/deferred | `field_policy.py` stores `avg_yield_per_bed_m`, `documented_price`, `in_row_spacing_cm`, `planting_season` under old keys. UI is immune via `FieldRegistry::read()` alias resolver. | Route to WP-CB-MIG2 or backend corrective. Verify actual stored keys at QA against live MySQL mirror (AC-13). |
| F-CB1-UI-02 | INFO | `planting_season` is type-changed to `sowing_months int[]` in `crop_attribute.value_list`. UI renders month chips. | Live data may not have migrated AT rows yet — will show MISSING until WP-CB-MIG migration runs. |
| F-CB1-UI-03 | INFO | 4 proposed fields (`needs_summer_shade`, `irrigation_type`, `root_depth_class`, `unit_size`) have no live storage. Rendered as "מוצע" placeholders. | Light up after WP-CB-MIG2. |
| DEFER-01 | INFO | JS parity tests for calcs #7, #9, #12 are formula-verified in PHP but not unit-asserted in PHPUnit (no headless browser). | Add Playwright/puppeteer fixture in next phase if required. |
| DEFER-02 | INFO | book_index filter chips are UI-only (client-side toggle). Server-side filtering (by family/season/frost/DTM range/completeness) requires backend query extension. | Route to next WP. |
| DEFER-03 | INFO | calc_panel.php embed in crop-page uses include-based variable injection instead of `Template::partial()`. Works for include context; test coverage guards regression. | Refactor to Template::partial() in a cleanup pass. |
| DEFER-04 | INFO | Export stubs in calc_dash.php (`/calc/export.pdf`, `/calc/export.csv`) are non-functional links with `aria-disabled`. | Server-side PDF/CSV generation is a future phase. |
| DEFER-05 | INFO | hub_calc.php (legacy calculator page) still exists and is bypassed by `HubController::calc()` routing to calc_dash.php. | Archive hub_calc.php in a cleanup WP. |

---

## §5 Test + Validate Output

### composer test
```
PHPUnit 10.5.63 · PHP 8.5.6
Tests: 96, Assertions: 278, Failures: 0
OK, but there were issues!
PHPUnit Deprecations: 1  (pre-existing phpunit.xml config deprecation, not from this WP)
```

### validate_aos.sh
```
RESULT: 28 PASS / 19 SKIP / 1 FAIL
[FAIL] Check 5: MISSING WP SFA-S003-P004-WP-CB-MIG2.spec_ref
  → Pre-existing: confirmed by stash-test (same FAIL before any changes).
  → NOT introduced by WP-CB-1 build.
```

### php -l
All 17 new/modified PHP files: `No syntax errors detected`

### Locked files
```
git diff --stat HEAD | grep "_aos/\|calculators\.py\|assumptions\.py\|calculator_meta\.py\|field_policy\.py\|migrations/"
(no output — 0 locked files touched)
```

---

## §6 Artifacts Created / Modified

### New files
| File | Description |
|---|---|
| `sfa_delivery/public_assets/css/crop-book-v1.css` | Full component layer (17 sections, ~450 lines) |
| `sfa_delivery/public_assets/js/crop-book-v1.js` | Interaction layer: CALC formulas, AF, filters, depth/audience, field info |
| `sfa_delivery/public_assets/fonts/Carmela.ttf` | Brand display font (copied from design assets) |
| `sfa_delivery/public_assets/img/crops/wc-lettuce.png` | Watercolor master — חסה |
| `sfa_delivery/public_assets/img/crops/wc-radish.png` | Watercolor master — צנונית |
| `sfa_delivery/public_assets/img/crops/wc-parsley.png` | Watercolor master — פטרוזיליה |
| `sfa_delivery/public_assets/img/crops/wc-dill.png` | Watercolor master — שמיר |
| `sfa_delivery/app/Lib/FieldRegistry.php` | FIM §1 alias resolver + Hebrew label dictionary |
| `sfa_delivery/app/Controllers/AssumptionsController.php` | GET /api/v1/assumptions + POST /api/v1/contribute |
| `sfa_delivery/templates/macros/prov_value.php` | Single cue authority (VALIDATED/UNVALIDATED/MISSING) |
| `sfa_delivery/templates/macros/assumption_field.php` | AssumptionField component (#18) |
| `sfa_delivery/templates/macros/calc_panel.php` | Calculator panel (#19) + disabled state (#19a) |
| `sfa_delivery/templates/macros/calc_seq.php` | Grouped calc sequence (#19b) |
| `sfa_delivery/templates/macros/rotation_hint.php` | Rotation hint chip (#23) |
| `sfa_delivery/templates/macros/depth_tabs.php` | Depth tabs (#22) |
| `sfa_delivery/templates/macros/audience_switch.php` | Audience switch (#21) |
| `sfa_delivery/templates/macros/prov_table.php` | Drill-down provenance hierarchy (#20) |
| `sfa_delivery/templates/pages/calc_dash.php` | Calculator dashboard (/calc/ — §2.3b) |
| `sfa_delivery/tests/CropBookV1MacroTest.php` | 32 assertions: macros + FieldRegistry + parity |
| `sfa_delivery/tests/CropBookV1RouteTest.php` | 11 assertions: route smoke for all new routes |

### Modified files
| File | Change |
|---|---|
| `sfa_delivery/public_assets/css/tokens.css` | Additive: --gj-* v2 palette, --cb-* provenance tokens, Carmela @font-face |
| `sfa_delivery/templates/_layout.php` | Wire crop-book-v1.css + crop-book-v1.js on crop-book pages; include crop-book-v1.css in asset_ver computation |
| `sfa_delivery/app/routes.php` | Add GET /api/v1/assumptions + POST /api/v1/contribute |
| `sfa_delivery/app/Controllers/CropBookViewController.php` | depth param, enrichment reads, buildCb1Fields(), WC_ART map, view param; import AssumptionsController + FieldRegistry |
| `sfa_delivery/app/Controllers/HubController.php` | Route /calc/ → calc_dash.php |
| `sfa_delivery/templates/pages/book_crop.php` | WP-CB-1 hero + 3-depth views + calc modal prepended; field helpers ($pv, $monthChips) |
| `sfa_delivery/templates/pages/book_entry.php` | Audience switch + top filter bar + cards/table views + pagination |

### Commits
1. `1456c48` feat(WP-CB-1): design system port — tokens, crop-book CSS/JS, Carmela font, watercolor art
2. `47c2dfd` feat(WP-CB-1): macros + FieldRegistry — prov_value, calc_panel, assumption_field, depth_tabs, et al.
3. `695c658` feat(WP-CB-1): pages + controller — book_crop depth views, book_index audience switch, calc dashboard
4. `1b1ef5f` test(WP-CB-1): prov_value 3-states, calc_panel disabled/enabled, assumption_field, route smoke, parity

---

## §7 Next Step

1. **L-GATE_V:** Route to Nimrod (non-Claude engine, IR#1/#5) for visual validation against `LOD300 Crop Book v1.html`. Key verification points: visual fidelity (colors, typography, spacing), RTL correctness, prov_value 3-state rendering on live data, disabled calc behavior on partial crop, JS calc recompute on input.

2. **Live data smoke (AC-13):** After deploy to uPress staging, run against a known partial crop (e.g. lettuce) to verify: (a) `*` asterisks appear on UNVALIDATED fields; (b) `—` + reqinfo CTA appears on MISSING fields; (c) disabled calc renders 🔒 + reqinfo; (d) assumptions registry JSON is served. Record actual `field_name` keys stored in live MySQL mirror (AC-13, F-CB1-UI-01 finding).

3. **WP-CB-MIG2:** Proposed fields (needs_summer_shade, irrigation_type, root_depth_class, unit_size) will light up automatically once WP-CB-MIG2 populates `crop_attribute` rows — no UI code change needed.

4. **Server-side filtering:** book_index filter chips are UI-only; route query-param filtering to a follow-on WP.

5. **Pre-existing validate_aos FAIL:** WP-CB-MIG2.spec_ref missing in `_aos/work_packages/`. Not introduced by this build; team_100 to triage.

---

*Built by team_10 (Claude sub-agent) · 2026-05-31 · IR#1: builder (Claude Sonnet 4.6) ≠ architect (team_100) ≠ validator (team_190, non-Claude).*
