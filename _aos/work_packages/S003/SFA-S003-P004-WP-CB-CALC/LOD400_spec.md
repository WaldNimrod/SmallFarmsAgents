---
id: SFA-S003-P004-WP-CB-CALC-LOD400
wp: SFA-S003-P004-WP-CB-CALC — calculator completion (6/14 → 15 goals)
gate: L-GATE_D (design) → ready for L-GATE_BUILD on team_00 go + team_35 mockups
status: SPEC (decision-complete; presentation layer pending team_35 mockups)
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50 (visual/QA) + team_190 (constitutional, cross-engine)
depends_on:
  - SFA-S003-P004-WP-CB-MOBILE (closed)
  - SFA-S003-P004-WP-CB-CALC-MANDATE-MOCKUPS (team_35 — presentation layer)
  - SFA-S003-P004-WP-CB-CROPDATA-DATES (Phase B-later only)
refs:
  - _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
  - _COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md
  - organic_market_agent/crop_book/calculators.py
  - organic_market_agent/crop_book/assumptions.py
---

# LOD400 — WP-CB-CALC

> Engine/data/logic is implementation-ready here. The **visual + interaction layer is owned by team_35** (mandate `MANDATE_CALC_MOCKUPS_2026-06-07.md`); this spec defines the **UI contract** (§7) the mockups must satisfy and will be merged with the returned mockups before build.

## 1. Scope
**In:** bring the calculator from 6 live goals to **15** by porting the Python calculators to JS, adding a JS date engine, reworking the result layer to typed results, and widening the server delivery. **Reuse** the existing `CALC` registry + `recompute()` (no math duplication). **Out:** `water` (#0 — `WP-CB-WATER`); the categorical data-enrichment + guided tool (`WP-CB-CROPDATA-DATES`); account-scoped session (per-device stays).

### Phasing (by data dependency — see LOD_DESIGN §0.5)
- **Phase A** (no prereqs): `transplants`(#2), `seed_cost`(#14), `compare`(#13) → 6→9.
- **Phase B-now** (existing data): `harvest_window`(#5, new 15th goal), `succession`(#6, derived), `sow_date`(#4, direct-seed) → 9→12.
- **Phase B-later** (after `WP-CB-CROPDATA-DATES`): `nursery`(#3), `frost`(#11), transplant-accurate `sow_date` → 12→15.

## 2. Phase A — non-date ports
Each adds a `CALC.<kind>(g, book)` mirroring the Python function; flip the goal's `kind` + `soon:false` in `$CALC_GOALS`; extend the CALC↔Python parity fixture (AC-11, `crop-book-v1.js:28`).

- **`transplants` (#2)** — `round((bed_len*100/spacing)*rows)` (Py `transplants_needed`). Book fields `spacing`,`rows` already delivered. Result: scalar `שתילים`. Trivial.
- **`seed_cost` (#14)** — `seed_input_cost`: `grams*price_per_g` OR `ceil(grams/grams_per_pack)*pack_price`. Needs **new builder inputs** (price/gram OR pack price+grams/pack) + **chain `grams`** from the `seed`(#1) result. Result: scalar `₪` (+ packs).
- **`compare` (#13)** — **quantity-first** (team_00). **Scope = SELECTED-CROP BASKET** (team_00 decision 2026-06-07; NOT "all crops"): step 2 becomes a multi-select basket (user picks 2–6 candidate crops); rank only the basket by `avg_yield_per_bed_m` (primary). Secondary line: `₪/מ׳` = yield × `price_documented` (price-list, illustrative). **No "profit"/"margin".** Rename label "השוואת גידולים"; `rlabel`=השוואה, primary unit `ק״ג/מ׳`. Result: **ranked_list** (§6). Uses only whitelisted fields. Basket crops missing yield are excluded (not zeroed). **UI: awaiting team_35 #13 basket mockup iteration** (the all-crops mockup is superseded).

## 3. Phase B-now — date engine on existing data
### 3.1 B0 foundations (shared by all date calcs)
1. **JS date module** — date-only arithmetic on `YYYY-MM-DD` strings (NO `Date` timezone math; avoids DST off-by-one). Mirror Py exactly:
   - `sowing_date_from_harvest`: `target_harvest − days_to_maturity` (direct); transplant also `− days_in_nursery`.
   - `harvest_window_from_sowing`: `harvest_start = sow + nursery_days + days_to_maturity`; `harvest_end = harvest_start + harvest_window_max_days`.
   - `succession_schedule`: from `first_sow`, step `interval_days = succession_interval_weeks*7`, until count/season-end.
   - `nursery_trays_and_sow_date`, `frost_planting_window` (B-later).
2. **Assumptions exposure** — add `TRAY_CELLS` + `HARDINESS_OFFSET` (+ `rotation_gap_seasons`) to `window.SFA_ASSUMPTIONS` (today only the 7 scalars).
3. **`runEngine()` rework** — return a **typed result** `{type, ...}` where `type ∈ {scalar, scalar_grid, date, date_range, date_list, ranked_list}`; for date goals read `state.anchor` + the date input + date book-fields **directly from `window.SFA_CROP_BOOK[slug]`** (not the numeric `[data-book]` chips, which `parseFloat`-filter — `crop-book-v1.js:635`).
4. **Server delivery** (§5).

### 3.2 The three B-now goals
- **`harvest_window` (#5)** — **NEW 15th goal**: add `$CALC_GOALS` entry + dropdown slot. anchor=`sow`. Uses `days_to_maturity`(66/70)+`harvest_window_max_days`(68/70). Result: **date_range**. Best coverage — ship first.
- **`succession` (#6)** — interval is **DERIVED** `round(harvest_window_max_days/7)` (team_00 decision; NOT a delivered field — עידן's empirical cadence is operational, corr 0.10 with biology). anchor=`sow`. New input: number of cycles OR season-end date. Result: **date_list**. Coverage 68/70.
- **`sow_date` (#4)** — anchor=`target` → `target_date − days_to_maturity` (66/70). **Default to direct-seed** when `planting_method` unknown (transplant accuracy in B-later). Result: **date**.

## 4. Phase B-later — gated on WP-CB-CROPDATA-DATES
Needs `planting_method` + `frost_tolerance_class` (+ `days_in_nursery` for revealed transplants), filled by the guided-entry tool.
- **`sow_date` transplant path** — also `− days_in_nursery` when `planting_method ∈ {transplant, both}`.
- **`nursery` (#3)** — `nursery_trays_and_sow_date`: trays `= ceil(plants*oversow/tray_cells)`, tray-sow `= field_set_date − days_in_nursery`. Needs `plants` (chain from #2) + a `field_set_date` input. Result: **scalar_grid**-like (trays + date).
- **`frost` (#11)** — `frost_planting_window`: earliest `= last_frost − HARDINESS_OFFSET[class]`; latest `= first_frost − days_to_maturity`. **Region picker** supplies last/first frost (Israel region table — static asset, assemble once). Result: **date_range**.

## 5. Server plumbing (NEW — beyond the report; blocking for §3/§4)
`HubController::calc()` builds `window.SFA_CROP_BOOK` from a hard-coded **numeric** whitelist (`HubController.php:147-156`). Required changes:
1. **Add numeric date fields** to the whitelist: `days_to_maturity`, `days_in_nursery`/`days_in_nursery_cell`, `harvest_window_max_days`. (NOT `succession_interval_weeks` — derived client-side.)
2. **Add a `crop_attribute` query** for the categoricals `planting_method`, `frost_tolerance_class` (the calc controller does not query `crop_attribute` today; `CropBookViewController::detail` shows the pattern at L681-683).
3. **Non-numeric channel** — emit categoricals in a text sub-map (e.g. `window.SFA_CROP_BOOK_TXT[slug]`) so they survive the JS `parseFloat`/`isFinite` filter (`crop-book-v1.js:635`).
4. **Route test** asserting `planting_method`/`frost_class` + the date numerics reach the rendered payload for a RICH-seeded crop.

## 6. Result-layer rework (typed results) — MOCKUPS DELIVERED & INTEGRATED (team_35, 2026-06-07)
team_35 returned the mockups (`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/MOCKUP_RETURN_team35_2026-06-07_v1.0.0.md`); the visual spec is locked. Source: `_COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/{calc,cropdata_entry}.html` + `mock.css` (LOCKED tokens).

Refactor `showResult`/`renderBreakdown`/`pushSession` (`crop-book-v1.js:719-760`) from scalar-only to **render-by-`type`**, using the mockup's DOM/classes verbatim:

| `type` | Goals | Mockup container | Session-row string |
|---|---|---|---|
| `scalar` | 1,8,2,10,12,7 | `.r-scalar > .big/.lbl` (+ `.breakdown`) | `כמות שתילים · עגבנייה → ~97 שתילים` |
| `scalar` + ₪ secondary | 9, 14 | `.r-scalar > .second` (₪ smaller, "לפי מדד השוק / להמחשה") | as scalar |
| `date` | 4 | `.r-date > .d/.anchor` | `תאריך זריעה · עגבנייה → 16/06/2026` |
| `date_range` | 5, 11 | `.r-range > .ends/.bar/.fill` | `חלון קרה · עגבנייה → 15/03–15/11` |
| `date_list` | 6 | `.r-list > .item(.n/.dt/.meta)` | `רצף · עגבנייה → 5 זריעות מ-16/06` |
| `ranked_list` | 13 | `.r-rank > table` (ק״ג/מ׳ primary, ₪/מ׳ `.v` secondary, `tr.top`) | `השוואה · 8 גידולים → עגבנייה #1` |
| `scalar+date` | 3 | `.r-scalar > .big` (trays) + `.second` (tray-sow date) | trays + date |
| `nodata` | any goal w/o data for the crop; 0 (water) | `.r-nodata > .ic/b` + "עזרו להשלים" | — (not pushed) |

`pushSession` must generalize beyond the scalar assumption to emit the per-shape string above.

## 7. UI contract — SATISFIED by the delivered mockups
- **Goal grid:** all 15 with **honest availability badges** — `.st.live` (זמין) / `.st.soon` (בקרוב, phases A/B-now/B-later) / `.st.dev` (— מודל נפרד = water). (`calc.html` goal registry `G[]`.)
- **ASK 4 steps** + goal-specific `.extra` panels (`#ex-target`,`#ex-seedcost`,`#ex-succession`,`#ex-region`) shown per goal; **anchor step LIVE** — greys/relabels for non-date goals (`anchorhint`, `datefld` opacity); **frost region picker** appears only for #11.
- **compare (#13)** flips the crop step to a **selected-crop basket** (multi-select, 2–6 crops) — team_00 decision; the "all crops" mockup is superseded, team_35 iterating.
- **RESULT:** typed shape (§6) + session (per-device) + export (PDF/CSV) + assumptions link (`assumptions.html`).
- **Honest no-data** is first-class (badge + `.r-nodata` card) — never a 0/guess.
- **Reuse `mock.css` tokens verbatim** (mirrors LOCKED `tokens.css`); calculator must match the redesigned shell.
- **Relabels to apply (mockup flag #6):** `calc_dash.php` — #13 "רווח גולמי"→"השוואת גידולים"; header "14 מחשבונים"→"15 מטרות"; add the `harvest`(#5) goal entry.

## 8. Acceptance criteria
1. Each shipped goal returns a real result; no "בפיתוח" for goals declared live in that phase; honest no-data state otherwise.
2. **Parity:** each new JS calc matches its Python function on the shared fixture (extend AC-11).
3. Date math is date-only and matches Python `timedelta` exactly (test direct-seed AND transplant branches).
4. Server delivery: route test (RICH payload — NOT empty; WP-CB-MOBILE 500 lesson) asserts the new numeric + categorical fields reach the client.
5. Session accumulates typed results; export includes a sensible representation for ranges/lists.
6. **PHP suite green (217/217)** + a route test per touched server path. `validate_aos` 0 FAIL.
7. Presentation matches the approved team_35 mockups (team_50 visual QA).

## 9. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Date parity Py↔JS (DST/off-by-one) | Date-only string math; shared fixture; both branches tested. |
| Scalar-only render breaks on date/range/list | Typed-result refactor (§6) before B-now; route+JS tests. |
| Categoricals silently dropped | Non-numeric channel (§5.3); assert in route test. |
| #13 mislabels revenue as profit | Quantity primary; ₪ secondary; no "profit" wording. |
| `$notes`-style include-scope clobber | Namespace new template locals; RICH route fixtures; live smoke post-deploy. |
| UI overlap with redesign | Engine/UI split; build presentation only from approved mockups; rebase on main; coordinate via Nimrod before merge. |

## 10. Build sequencing
team_00 go → **Phase A** (+B-now once mockups for the 5 result shapes return) → guided tool (`WP-CB-CROPDATA-DATES`) → **B-later**. Isolated branch `claude/cb-followups-2026-06-07`, team_100 commits (IR#4), team_50 + team_190 validate (IR#1/#5). Build does not start until team_35 mockups land (presentation layer) + team_00 go.
