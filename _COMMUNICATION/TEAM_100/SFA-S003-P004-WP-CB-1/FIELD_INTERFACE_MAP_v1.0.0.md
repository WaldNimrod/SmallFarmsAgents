# FIELD_INTERFACE_MAP — SFA-S003-P004-WP-CB-1 — team_100 — v1.0.0

**Date:** 2026-05-31
**Author:** team_100
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1 UI slice)
**Type:** ARCHITECTURE_CONTRACT (binding input to the UI build)

> Binds every **design field key** (team_35 LOD300 `FIELD_INFO`/`CALC`/`MANDATORY`) to the **migrated
> data model** (post WP-CB-MIG). This is the authority the UI consumes: it resolves what to read, from
> which layer, under which storage key, and which Hebrew label to render. **No raw DB key is ever shown
> to a user** — `field_label()` resolves `field_name → (Hebrew label, explainer)`; the DB key appears only
> in the dev tooltip and in this doc.

---

## 0. The naming-drift problem this contract solves

Three layers name the same concept differently, verified deterministically (`python3` introspection of the
live modules, 2026-05-31):

- **Design** (`cropbook-v1.js` `FIELD_INFO`/`MANDATORY`/`CALC`) uses **JMF/old** names:
  `in_row_spacing_cm`, `avg_yield_per_bed_m`, `documented_price`, `seeds_per_gram`, `days_in_nursery`,
  `succession_interval`, `frost_tolerance`, `nutrient_removal_N`, `planting_season`.
- **`field_policy.py`** (the reconciler's field table — the reconciler keys each `crop_field_enrichment`
  row by its `FIELD_POLICY` key) still uses **old** names for 4 fields
  (`avg_yield_per_bed_m`, `documented_price`, `in_row_spacing_cm`, `planting_season`) and **new** names for
  the rest (`seeds_per_g`, `days_in_nursery`, `succession_interval_weeks`, `nutrient_removal_n_kg_per_ha`).
- **`calculator_meta.py`** uses **canonical/new** names and ships `FIELD_ALIASES` (old→new) to bridge.
- **Canon** (`WP-CB-0` §7) is the new-name authority; categorical/list fields live in `crop_attribute`.

**Consequence:** `crop_field_enrichment.field_name` rows are keyed by the **`field_policy` name** (old for the
4 drifted fields). The UI must not hard-code either spelling. **F-CB1-UI-01** (below) tracks the
`field_policy`↔canon drift as a backend corrective; the UI is made correct **regardless** via the resolver in §1.

## 1. Canonical resolver (the UI's binding rule)

The delivery tier MUST resolve field access through one **bidirectional alias map** (mirror of
`calculator_meta.FIELD_ALIASES`), so a lookup succeeds whether a row is stored old- or new-keyed:

```
CANON = {                       # concept → canonical name
  in_row_spacing_cm:  spacing_in_row_cm
  avg_yield_per_bed_m: yield_per_bed_m
  documented_price:   price_documented
  seeds_per_gram:     seeds_per_g
  frost_tolerance:    frost_tolerance_class
  days_in_nursery_cell: days_in_nursery
  succession_interval: succession_interval_weeks
  nutrient_removal_N: nutrient_removal_n_kg_per_ha
}
# resolve(name): canonical = CANON.get(name, name)
# read(crop, name): try enrichment[canonical] → enrichment[name] → any alias-sibling → MISSING
```

Read order for a concept: **canonical key → original key → alias siblings**. First hit wins. This makes the
UI immune to the §0 drift and to whether the live migration renamed rows or not (verified at QA, AC-13).

## 2. Field map — design key → data model

Layer legend: **EN** = `crop_field_enrichment.value_best` (T1 numeric, carries `confidence_score`,
`winning_source_class` → drives `prov_value`); **AT** = `crop_attribute` (`value_canonical` T2 / `value_list`
T3); **ID** = identity column on `crops`/`crop_varieties`; **AS** = `assumptions.py` (never crop data, never
affects complete/partial); **DERIVE** = computed on read.

| # | Design key | Hebrew label | Canonical name | Layer | Storage key (read) | Notes |
|---|-----------|--------------|----------------|-------|--------------------|-------|
| 1 | `days_to_maturity` | ימים להבשלה | `days_to_maturity` | EN | `days_to_maturity` | calc #4/#5/#11 |
| 2 | `harvest_window` | חלון קטיף | `harvest_window_max_days` (+`_min_days`) | EN | `harvest_window_max_days` | calc #5; design shows the max |
| 3 | `in_row_spacing_cm` | מרווח בשורה | `spacing_in_row_cm` | EN | `spacing_in_row_cm`→`in_row_spacing_cm` ⚠ | drift; resolver bridges. calc #1/#2/#10 |
| 4 | `rows_per_bed` | שורות בערוגה | `rows_per_bed` | EN | `rows_per_bed` | calc #1/#2/#10 |
| 5 | `seeds_per_gram` | זרעים לגרם | `seeds_per_g` | EN | `seeds_per_g` | calc #1 |
| 6 | `avg_yield_per_bed_m` | יבול ממוצע למ׳ | `yield_per_bed_m` | EN | `yield_per_bed_m`→`avg_yield_per_bed_m` ⚠ | drift; resolver bridges. calc #7/#8/#9/#13 |
| 7 | `documented_price` | מחיר מתועד | `price_documented` | EN | `price_documented`→`documented_price` ⚠ | drift; resolver bridges. calc #9/#13. Q7: per-bed-m in table; documented unit in calc/full |
| 8 | `planting_season` | עונת שתילה | `sowing_months` (+`transplant_months`) | AT (T3 list) | `crop_attribute.value_list` ⚠ | TYPE CHANGE: scalar→int[] (1–12). Render as month chips, not a string |
| 9 | `planting_method` | שיטת שתילה | `planting_method` | AT (T2) | `crop_attribute.value_canonical` | enum direct_seed/transplant/… calc #4/#5 gate |
| 10 | `frost_tolerance` | עמידות לקרה | `frost_tolerance_class` | AT (T2) | `crop_attribute.value_canonical` | enum hardy/half_hardy/tender/very_tender; calc #11 (→hardiness_offset) |
| 11 | `days_in_nursery` | ימים במשתלה | `days_in_nursery` | EN (+ID col) | `days_in_nursery` | calc #3 reads `days_in_nursery_cell`→aliases to `days_in_nursery`. Q8: single field |
| 12 | `succession_interval` | מרווח רצף | `succession_interval_weeks` | EN | `succession_interval_weeks` | calc #6 |
| 13 | `nutrient_removal_N` | צריכת חנקן (N) | `nutrient_removal_n_kg_per_ha` | EN | `nutrient_removal_n_kg_per_ha` | calc #12 |
| 14 | `family` | משפחה בוטנית | `family_id` → `crop_families` | ID (FK) | `crops.family_id` | rotation hint only; NOT enrichment, NO prov cue |
| 15 | `needs_summer_shade` | הצללה בקיץ | `needs_summer_shade` | AT (proposed) | — until WP-CB-MIG2 | ratified (3 levels 30/40/50 + none); "מוצע" until migration |
| 16 | `irrigation_type` | סוג השקיה | `irrigation_type` (+`drip_lines_per_bed`) | AT (proposed) | — until WP-CB-MIG2 | "מוצע" placeholder |
| — | `seeder_model` | דגם מזרעה | `seeder`(+gears/plate) | ID | `crop_varieties.seeder*` | identity columns already exist; surface in ציוד topic |
| — | `root_depth_class` | עומק שורשים | `root_depth_class` | AT (proposed) | — until WP-CB-MIG2 | "מוצע" placeholder |
| — | `sale_unit` | יחידת מכירה | `harvest_unit_default` (+`unit_size` proposed) | ID/AT | `crop_varieties.harvest_unit_default` | exists as identity; `unit_size` proposed (Q7 normalization) |

## 3. AssumptionFields (never crop data; never affect complete/partial)

Served by `GET /api/v1/assumptions` from `assumptions.py`. Scalars (6):
`germination_rate` 0.90 (post_url ✓), `bed_width` 0.80 (post_url ✓), `oversow` 1.10, `std_bed_length_m` 30,
`compost_N_pct` 0.015, `application_efficiency` 0.50, `rotation_gap_seasons` 3. Tables (2): `tray_cells`
(`TRAY_CELLS`, default 128), `hardiness_offset` (by `frost_tolerance_class`). Launch-blocking copy: only
`germination_rate` + `bed_width` must carry a `post_url` (both do). The `.af` component renders default +
inline override + explainer + read-more link; teal `--cb-assume` accent.

## 4. Provenance / complete-partial rule (τ = 0.40, v1)

The backend stamps per-field `field_state ∈ {VALIDATED, UNVALIDATED, MISSING}` (ingest payload, AC-09) using
**τ = 0.40** (VALIDATED iff EX/NI override OR `confidence_score ≥ 0.40`). The UI does **no threshold math** —
it renders the stamped state via `prov_value`:
- **VALIDATED** → plain `value unit` (`--cb-validated`).
- **UNVALIDATED** → `value *` + tooltip (`--cb-unvalidated`); the `*` propagates to any calc output using it.
- **MISSING** → `—` + `◐ בקשו נתון` request-info CTA (`--cb-missing`); a calc with a MISSING **required** field
  renders `.cv.is-disabled` (only MISSING disables — not UNVALIDATED, not assumptions, not user input).

Crop **complete** iff `all(prov_value == VALIDATED)` over the MANDATORY set; else **partial** (state dot on card/hero).
Design Q4 (τ=0.50) is the recorded fast-follow — when adopted it changes only the backend stamp, not UI code.

## 5. Calculator binding (`calculator_meta.py` is the SSoT for enabled/disabled)

The UI reads `CALCULATOR_META[id] = {audience G|F|B, required_book_fields[], assumption_keys[], user_inputs[]}`
and `calc_enabled(id, field_state)`. The 6 **interactive** calcs (#1,#7,#8,#9,#10,#12) recompute client-side via
`cropbook-v1.js CALC[kind]` — these MUST stay in parity with Python (AC-11). The rest server-render only.
Operand names in `CALC` are old-style; resolve through §1 before reading enrichment.

## 6. Findings (logged for follow-up — not fixed in this UI slice)

- **F-CB1-UI-01 (MAJOR, backend, deferred):** `field_policy.py` keys `avg_yield_per_bed_m`, `documented_price`,
  `in_row_spacing_cm`, `planting_season` are **old** names while Canon/`calculator_meta` are new — the reconciler
  therefore writes those `crop_field_enrichment` rows under old keys. `field_policy.py` is part of the LOCKED
  backend slice; do **not** edit it in the UI slice. Route the canon-alignment to **WP-CB-MIG2** (or a backend
  corrective). UI is made drift-immune via the §1 resolver; **verify actual stored keys against the live MySQL
  mirror at QA (AC-13)** and record the observed `field_name` set.
- **F-CB1-UI-02 (INFO):** `planting_season` is a **type change** (scalar → `sowing_months` int[] in
  `crop_attribute.value_list`). The UI must render month chips and must not treat it as an enrichment scalar.
- **F-CB1-UI-03 (INFO):** 4 design fields have no live storage yet (`needs_summer_shade`, `irrigation_type`,
  `root_depth_class`, `unit_size`) → render as "מוצע/proposed"; they light up after WP-CB-MIG2.

*Authored by team_100 (Chief Architect) · 2026-05-31 · binding input to the WP-CB-1 UI build dispatch.*
