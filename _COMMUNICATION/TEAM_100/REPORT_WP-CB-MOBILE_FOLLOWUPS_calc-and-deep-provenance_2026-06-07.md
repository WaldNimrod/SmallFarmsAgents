# REPORT — WP-CB-MOBILE carried-forward follow-ups (detailed scope) — team_100

**Date:** 2026-06-07 · **Author:** team_100 · **Purpose:** detailed, code-grounded scope for the two follow-ups carried out of WP-CB-MOBILE (now closed), to seed future WPs. All findings verified against the codebase + the live site `https://sfa.nimrod.bio`.

---

# ITEM 1 — Calculator completion (6/14 live → wire the rest)

## 1.1 Current state (verified)
The v4 "define the question" builder (`sfa_delivery/templates/pages/calc_dash.php`) exposes **14 goals** (6 primary buttons + 8 in a dropdown). Only **6 have client-side math**; the other 8 show a "מחשבון זה בפיתוח" notice on compute (`calc_dash.php:221-225`, triggered when `runEngine()` returns `{ok:false}` for an empty/`soon` kind, `crop-book-v1.js:626`).

**Crucially: all 14 calculators are already fully implemented in Python** (`organic_market_agent/crop_book/calculators.py`) — server-side math exists for 13 of them; only `water` (צריכת מים) has **no implementation anywhere**. The client (`crop-book-v1.js` `CALC` registry, L31-129) implements only 6. **So the gap is mostly a Python→JS port, not new math.**

### The full 14-goal map
| Goal (Hebrew) | calc# | JS `CALC` | State | Python impl | Type |
|---|---|---|---|---|---|
| זרעים לקנות | 1 `seed` | ✅ | **LIVE** | yes | qty |
| יבול צפוי | 8 `yield` | ✅ | **LIVE** | yes | qty |
| הכנסה צפויה | 9 `revenue` | ✅ | **LIVE** | yes | qty |
| צפיפות שתילה | 10 `pop` | ✅ | **LIVE** | yes | qty |
| כמות דישון | 12 `fert` | ✅ | **LIVE** | yes | qty |
| ערוגות ליעד | 7 `beds` | ✅ | **LIVE** | yes | qty |
| כמות שתילים | 2 `transplants` | ✗ | STUB | **yes** | qty (trivial) |
| רווח גולמי | 13 `profit` | ✗ | STUB | **yes** | qty (multi-crop) |
| עלות זרעים | 14 `seed_cost` | ✗ | STUB | **yes** | qty (new inputs) |
| תאריך זריעה | 4 `sow_date` | ✗ | STUB | **yes** | **DATE** |
| ימי משתלה | 3 `nursery` | ✗ | STUB | **yes** | **DATE** |
| רצף גידולים | 6 `succession` | ✗ | STUB | **yes** | **DATE** |
| חלון קרה | 11 `frost` | ✗ | STUB | **yes** | **DATE** |
| צריכת מים | 0 `water` | ✗ | STUB | **NONE** | undefined |

(There is also a 15th Python calc, `harvest_window_from_sowing` #5, implemented but not surfaced as a goal — a DATE calc.)

## 1.2 The two real sub-gaps
**(a) Non-date stubs — pure Python→JS port (cheap):**
- **`transplants` (#2):** `round((bed_len·100/spacing)·rows)`. Book fields already in the engine — nearly free.
- **`profit` (#13):** rank crops by gross margin/m — needs a loop over `window.SFA_CROP_BOOK` (multi-crop), modest.
- **`seed_cost` (#14):** `grams·price_per_g` or `⌈grams/pack⌉·pack_price` — needs new seed-price input fields in the builder.

**(b) Date stubs — need a JS date engine + the dead time-anchor (the real lift):**
- The builder already renders a **time-anchor** step (תאריך יעד / תאריך זריעה / עכשיו, `calc_dash.php:182-194`), but it is **captured-but-unused**: `state.anchor` only drives input visibility (`crop-book-v1.js:594-598`); `runEngine()` (L624-662) reads only area/beds/seedlings/target_kg and **never reads `target_date`/`sow_date`/`state.anchor`**. The only consumer of `target_date` is the legacy single-result export path (L502-503). So the date scaffolding exists but no calc consumes it.
- Date calcs: `sow_date`(#4), `nursery`(#3), `succession`(#6), `frost`(#11) (+ `harvest_window`#5). To make them live: **(i)** build a JS date engine (Date arithmetic mirroring the Python `timedelta`); **(ii)** make `runEngine()` consume `state.anchor` + the date inputs; **(iii)** plumb date-relevant book fields (`days_to_maturity`, `planting_method`, `days_in_nursery`, frost-tolerance class) through `QB_BOOK_ALIAS` (L531-540) + the engine `[data-book]` chips (today only spacing/rows/seeds/yield/price/n/p/k); **(iv)** add the `HARDINESS_OFFSET` + `TRAY_CELLS` lookup tables to the JS assumptions; **(v)** date-aware result + session rendering (`runEngine`/`showResult` currently assume a numeric `[data-result]`).

**(c) `water` (#0):** no model anywhere — needs a product decision (define an ET/crop-coefficient water model, or drop the goal). Not a port.

## 1.3 Supporting state (verified)
- **AssumptionField** (`assumptions.py` `ASSUMPTIONS`): 7 scalar keys (germination 0.90, bed_width 0.80, oversow 1.10, std_bed_length_m 30, compost_N_pct 0.015, application_efficiency 0.50, rotation_gap_seasons 3) + 2 lookup tables (`TRAY_CELLS` 128, `HARDINESS_OFFSET`). The calc-result editor (`calc_dash.php:245-260`) surfaces **6** of them; `rotation_gap_seasons` + `tray_cells` are defined but not surfaced. JS binds via `wireAssumptions` → `window.SFA_ASSUMPTIONS`.
- **Session:** `sessionStorage` key `sfa_calc_session_v1`, capped at 30 entries (`crop-book-v1.js:542,711-717`); **per-device only** (no account scope — v1 decision). Export-all serializes the session to `rows[]` and hits `/calc/print` (PDF) + `/calc/export.csv` (`HubController::calcExport`).

## 1.4 Proposed WP — `SFA-S003-P004-WP-CB-CALC` (phased)
- **Phase A (S, ~1 day):** port the 3 non-date stubs — `transplants` (trivial), `profit`, `seed_cost` (+ its inputs). 6→9 live calculators, no new engine.
- **Phase B (M, ~2-4 days):** JS **date engine** + consume the existing time-anchor + plumb date book-fields + lookup tables + date-aware rendering → `sow_date`, `nursery`, `succession`, `frost` (+ optionally surface `harvest_window`). 9→13 live.
- **Phase C (decision):** `water` — define a water model or remove the goal. Don't ship a stub indefinitely.
- **Acceptance:** each goal returns a real result (no "בפיתוח"); date calcs honor the anchor; session accumulates + export-all includes them; PHP suite green + a route test per new calc (seed real book fields, assert numeric/date result — *not* an empty-payload fixture, per the WP-CB-MOBILE 500 lesson).
- **Risks:** date arithmetic parity Python↔JS (timezones/DST — use date-only math); result/session rendering assumes numeric (refactor for dates); `seed_cost`/`profit` need new inputs/data wiring.
- **Open decisions (team_00):** (1) `water` calculator definition vs drop; (2) account-scoped session persistence (currently per-device) — relevant only once accounts exist; (3) surface `harvest_window` (#5) as a 15th goal?

---

# ITEM 2 — Deep-view provenance (source pills) — REASSESSED

## 2.1 Corrected finding (verified on live)
My earlier "honest gap: Deep source pills omitted because the mirror lacks provenance" was **overstated**. Live check (`/crop-book/lettuce/?depth=deep`, 2026-06-07): **32 `srcpill` + 8 `srcline` rows render** — provenance pills **work in production** wherever enrichment data exists. Ranges (`.rng`) + variety table also render. **The architecture is wired end-to-end and functioning.**

## 2.2 How it actually works
- **Pills** need ≥1 field in `$cb1_fields` with a non-empty `winning_source_class`; `buildSourceClasses()` (`CropBookViewController.php:1010-1031`) maps `EXPERT→EX / NI,PROFESSIONAL→PR / WEB,NET→WR`, dedups, ranks `EX>PR>WR`, and `crop_topics.php:91-98` renders the row.
- **Path A (works):** the mirror **does** have `crop_field_enrichment` (migration `004…sql`, incl. `winning_source_class`) + `crop_attribute` (`005…sql`); the publisher pushes them (`sfa_ingest_push.py:638-708`, `--table all`); the controller reads them (`detail()` L665-691) → real pills (lettuce proves it).
- **Path B (fallback, strips provenance):** when a field has no enrichment row, `buildCb1Fields` falls back to the variety payload and **hard-codes `winning_source_class => ''`** (`CropBookViewController.php:879,887,912`) → no pill for that field.

## 2.3 The actual (smaller) gap
1. **Data coverage** — crops/fields **without `crop_field_enrichment` rows** show no pills (they hit path B). This is a **data-completeness** matter (enrich more crops in the PG SSoT + push), *not* a pipeline defect. Lettuce is well-enriched (32 pills); sparser crops will show fewer/none.
2. **Stale/misleading comment** — `CropBookViewController.php:693-696` claims "the MySQL mirror has no crop_field_enrichment / crop_attribute tables." This is **false** (migrations 004/005 exist; pills render live). Should be corrected to avoid future confusion.
3. **Fallback robustness (optional)** — path B could also surface provenance if the per-variety payload carried a `source_class{}` map (producer `sfa_ingest_push.py:467-501` already has `winning_source_class` in `enrichment_meta` L411-415 but only emits `field_state`). Adding it + reading it in the 3 fallback branches would give pills even where the dedicated enrichment table is sparse.

## 2.4 Ranges — confirmed robust
Ranges (`.rng`) render iff ≥2 varieties carry distinct numeric values for a field (`crop_topics.php:41,46`; `buildVarietyRanges` `CropBookViewController.php:974-998`, numeric-only). The backing per-variety `agronomy{}` numerics are reliably in the mirror (`crop_varieties.payload_json`). No gap.

## 2.5 Proposed disposition — `SFA-S003-P004-WP-CB-DEEP-PROVENANCE` (small / mostly data)
- **(S, hours) Verify + close the doc gap:** confirm `SELECT COUNT(*) FROM crop_field_enrichment` on the live mirror; fix the stale comment L693-696. Likely no code change needed for crops that are enriched.
- **(Data, ongoing) Coverage:** enrich more crops in the PG SSoT (the team that owns crop-book enrichment) + push `--table crop_field_enrichment,crop_attribute`. This is the real lever for "more pills."
- **(S, optional ~1 day) Fallback robustness:** add `source_class{}` to the variety payload + read it in the 3 fallback branches (namespace the local var — per the `$notes`-clobber lesson). Gives pills without a dedicated enrichment row.
- **Risks:** low — additive payload key + idempotent push (tested by `IngestEnrichmentMirrorTest`). The low-trust classes `OP/MK/WB/UC` are intentionally not mapped to a pill (no-leak); confirm that's desired.

---

## Recommendation
- **Item 1** is a genuine feature WP worth doing (the calculator is a core pillar and 8/14 goals dead-end on "בפיתוח"). Recommend **Phase A first** (cheap, 6→9 live), then Phase B (date engine) as the substantive piece; resolve `water` (C) with team_00.
- **Item 2** is much smaller than first thought — provenance works; it's a **data-coverage + doc-cleanup** task, not a pipeline rebuild. Recommend the (S) verify/doc-fix now and treat richer pills as crop-enrichment data work.

Neither is a launch blocker. Suggest registering both as REGISTER-tier WPs for team_00 prioritization (not auto-added to the roadmap pending your call).
