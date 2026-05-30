---
id: SFA-S003-P004-WP-CB-1-LOD400
wp: SFA-S003-P004-WP-CB-1 — Crop Book v1 (calculator-driven planning tool)
gate: L-GATE_S (LOD400 — implementation spec)
status: DRAFT — sections 1–9 + 11–13 complete; §10 (team_35 mockups) PENDING team_35 LOD300
author: team_100 (Claude Code, Chief Architect)
date: 2026-05-30
version: v0.9.0
changelog: >
  v0.9.0 — Initial LOD400 draft. Calculator pure-function contracts (14), schema
  wirings (days_in_nursery_cell + succession_interval_weeks enrichment),
  AssumptionField component + registry, complete/partial state machine, future-module
  API contracts. §10 UI mockups intentionally PENDING — embeds team_35 LOD300 on delivery.
  NOT yet submitted to L-GATE_S; locks to v1.0.0 once §10 mockups are embedded.
catalog_ref: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md
schema_ref: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/MANDATORY_FIELD_SCHEMA_v1.0.0.md
gapfill_ref: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/GAP_FILL_PLAN_v1.0.0.md
builder: team_10 (Claude Sonnet) → QA team_50 (Haiku) → L-GATE_V team_190 (non-Claude, IR#1)
---

# LOD400 — SFA-S003-P004-WP-CB-1: Crop Book v1 (Calculator-Driven)

**Read before writing a single line of code:**
1. `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md` — the 14 calculators (SSoT for scope)
2. `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/MANDATORY_FIELD_SCHEMA_v1.0.0.md` — field register + schema wirings
3. `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/GAP_FILL_PLAN_v1.0.0.md` — complete/partial state machine + τ
4. `organic_market_agent/crop_book/field_policy.py` — FIELD_POLICY dict (to extend)
5. `organic_market_agent/crop_book/importer/enrichment_runner.py` + `reconciler.py` — services layer (READ-ONLY here)
6. `organic_market_agent/crop_book/enrichment_models.py` — `CropFieldEnrichment` (value_best source)
7. `organic_market_agent/publisher/sfa_ingest_push.py` — `_fetch_crop_varieties`/`_fetch_crops` agronomy whitelist (to extend)
8. `documentation/02-architecture/sfa-delivery-tier.md` — hosting canon (uPress serves; never the home server)

---

## 1. Goal

Turn the LIVE read-only Crop Book (`sfa.nimrod.bio/crop-book/`) into a **planning tool**: a tested library of **14 calculators** that consume reconciled book values (`crop_field_enrichment.value_best`) plus user-adjustable **AssumptionFields**, surfaced in a two-audience UI (Cards/Table) with per-crop Simple/Full/Drill-down views and an honest **complete/partial** state. Calculators are **repo-owned pure functions**, unit-tested in isolation, independent of the UI.

**Non-goals (future WPs):** Planner bed-map (CB-2), Tasks (CB-3), Sales/POS (CB-4), Tend write-back (CB-5). This WP only *exposes typed outputs* those will consume (§12).

---

## 2. Architecture & module layout

```
organic_market_agent/crop_book/
├── field_policy.py            ← MODIFY: + days_in_nursery_cell, + succession_interval_weeks
├── assumptions.py             ← NEW: Assumption dataclass + ASSUMPTIONS registry (Schema §3.3)
├── calculators.py             ← NEW: 14 pure functions + result dataclasses + CalcInput/CalcResult
├── calculator_meta.py         ← NEW: per-calc metadata (id, audience, required book fields, assumptions)
└── importer/
    └── (no engine change — reconciler/enrichment_runner are LOD500_LOCKED; we only add policy keys)

organic_market_agent/publisher/
└── sfa_ingest_push.py         ← MODIFY: agronomy whitelist += days_in_nursery_cell, succession_interval_weeks;
                                          embed assumptions registry + per-crop field_state into payload

delivery tier (Slim4/PHP, uPress) — deployed via waldhomeserver FTPS relay:
├── templates/crop_book/       ← MODIFY: calculator panel, AssumptionField component, audience switch,
│                                         Simple/Full/Drill-down, complete/partial rendering
└── (PHP calc mirror OPTIONAL) ← see §9.3 — default is server-render from Python outputs in payload

tests/crop_book/
├── test_calculators.py        ← NEW: ≥ 2 cases per calculator (happy + edge), ≥ 30 tests
├── test_assumptions.py        ← NEW: registry defaults, germination/bed_width have post_url
├── test_calculator_meta.py    ← NEW: required-field maps match catalog
└── test_field_policy.py       ← EXTEND: new keys present, get_field_policy returns them
```

**Files that MUST NOT change** (LOD500_LOCKED): `reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`, migrations 001–057, `models.py` (no new columns this WP), `constants.py` (read-only).

---

## 3. Schema wirings (from Mandatory Field Schema §3)

### 3.1 `field_policy.py` additions (exact)
```python
"days_in_nursery_cell": FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP"),
    blend_strategy="weighted_mean",
    outlier=OutlierConfig(z_threshold=3.5),
),
"succession_interval_weeks": FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP"),
    blend_strategy="hard_winner",
),
```
After this, `python -m organic_market_agent.crop_book.importer.seed --enrich` (existing entrypoint) populates `crop_field_enrichment` for both fields from existing source_values rows. **No migration.**

### 3.2 `succession_interval_weeks` source rows
If no importer currently writes `source_values` for `succession_interval_weeks`, add a source path (JMF column if present, else EX/NI/WR per Gap-Fill Plan). AC-04 verifies ≥1 source_values row exists for the shown set before enrichment.

### 3.3 Ingest whitelist
In `sfa_ingest_push.py`, extend the agronomy field whitelist with `"days_in_nursery_cell"` and `"succession_interval_weeks"`, and add a per-field `field_state` (VALIDATED/UNVALIDATED/MISSING per Gap-Fill §2) so the delivery tier renders asterisks without re-deriving.

---

## 4. AssumptionField (Schema §3.3) — `assumptions.py`

Implement the `Assumption` dataclass + `ASSUMPTIONS` registry exactly as in Mandatory Field Schema §3.3. Hard requirements:
- `germination_rate` (0.90) and `bed_width` (0.80) MUST have a non-null `post_url` (content from team_00).
- `tray_cells` lookup (by `nursery_tray_type`) and `hardiness_offset` (by `frost_tolerance_class`, Catalog §4) live here as tables.
- A helper `get_assumption(key, override=None)` returns `override if override is not None else ASSUMPTIONS[key].default`.

---

## 5. Calculator contracts (`calculators.py`) — the precision core

All calculators are **pure functions**: no DB, no I/O, no globals. Inputs are explicit; book values are passed in by the caller (resolved from `value_best`). Each returns a frozen result dataclass. Units are explicit in field names. All raise `CalcUnavailable(field_name)` if a **required book value is None** (→ caller renders the disabled state).

Shared types:
```python
@dataclass(frozen=True)
class CalcUnavailable(Exception):
    missing_field: str

@dataclass(frozen=True)
class SeedQtyResult:
    plants: int
    seeds: int
    grams: float
```

### Definitions (signature · formula · edge cases)

**1. seed_quantity_to_buy**
`(*, rows_per_bed:int, in_row_spacing_cm:float, seeds_per_gram:float, bed_length_m:float, seeds_per_hole:int=1, germination_rate:float=0.90, oversow:float=1.10) -> SeedQtyResult`
- plants = round((bed_length_m*100 / in_row_spacing_cm) * rows_per_bed * seeds_per_hole)
- seeds = ceil(plants / germination_rate * oversow)
- grams = seeds / seeds_per_gram
- Edge: germination_rate ∈ (0,1]; spacing>0; if `seeds_per_gram` None → CalcUnavailable("seeds_per_gram"); grams rounded to 2 dp.

**2. transplants_needed**
`(*, rows_per_bed:int, in_row_spacing_cm:float, bed_length_m:float) -> int`
- return round((bed_length_m*100 / in_row_spacing_cm) * rows_per_bed)

**3. nursery_trays_and_sow_date**
`(*, plants:int, days_in_nursery:int, field_set_date:date, tray_cells:int=128, oversow:float=1.10) -> {trays:int, tray_sow_date:date}`
- trays = ceil(plants*oversow / tray_cells); tray_sow_date = field_set_date − days_in_nursery days
- Edge: days_in_nursery None → CalcUnavailable("days_in_nursery_cell").

**4. sowing_date_from_harvest**
`(*, target_harvest:date, days_to_maturity:int, planting_method:str, days_in_nursery:int|None) -> {sow_date:date, field_set_date:date|None}`
- transplant*: sow = target_harvest − DTM − days_in_nursery; field_set = sow + days_in_nursery
- direct: sow = target_harvest − DTM; field_set = None
- Edge: DTM None → CalcUnavailable("days_to_maturity"); transplant with days_in_nursery None → CalcUnavailable("days_in_nursery_cell"). `planting_method` startswith "transplant"/"greenhouse" ⇒ transplant.

**5. harvest_window_from_sowing**
`(*, sow_date:date, days_to_maturity:int, harvest_window_max_days:int, planting_method:str, days_in_nursery:int|None) -> {harvest_start:date, harvest_end:date}`
- start = sow + (days_in_nursery if transplant else 0) + DTM; end = start + harvest_window_max_days
- Edge: window None → CalcUnavailable("harvest_window_max_days").

**6. succession_schedule**
`(*, first_sow:date, succession_interval_weeks:int, num_successions:int|None, season_end:date|None, planting_season:str|None) -> list[date]`
- dates = [first_sow + n*interval_weeks*7 for n in range(k)] where k = num_successions, else successions until > season_end.
- Edge: interval None → CalcUnavailable("succession_interval_weeks"); must give num_successions OR season_end (else ValueError); clamp to planting_season window if provided.

**7. beds_for_target_yield**
`(*, target_kg:float, avg_yield_per_bed_m:float, std_bed_length_m:float=30.0) -> {bed_meters:float, beds:float}`
- bed_meters = target_kg / avg_yield_per_bed_m; beds = bed_meters / std_bed_length_m
- Edge: yield None or 0 → CalcUnavailable("avg_yield_per_bed_m").

**8. expected_yield**
`(*, avg_yield_per_bed_m:float, bed_length_m:float) -> float`  → yield_kg = avg_yield_per_bed_m * bed_length_m

**9. expected_revenue**
`(*, avg_yield_per_bed_m:float, bed_length_m:float, documented_price:float, documented_price_unit:str, kg_per_unit:float|None=None) -> {yield_kg:float, revenue:float}`
- yield_kg = avg_yield_per_bed_m * bed_length_m
- if unit is per-kg: revenue = yield_kg * price; else convert via kg_per_unit (from `crop_unit_conversions`): units = yield_kg / kg_per_unit; revenue = units * price
- Edge: price None → CalcUnavailable("documented_price"); non-kg unit without kg_per_unit → CalcUnavailable("conversion").

**10. plant_population**
`(*, rows_per_bed:int, in_row_spacing_cm:float, bed_width_m:float=0.80) -> {plants_per_m2:float, grid:tuple[int,int]}`
- plants_per_m2 = (rows_per_bed / bed_width_m) * (100 / in_row_spacing_cm); grid = (rows_per_bed, round(100/in_row_spacing_cm)) for the visual layout.

**11. frost_planting_window**
`(*, last_frost:date, first_frost:date, frost_tolerance_class:str|None, days_to_maturity:int, hardiness_offset_days:int|None=None) -> {earliest_plant:date, latest_plant:date}`
- offset = hardiness_offset_days if given else hardiness_offset(frost_tolerance_class) (Catalog §4; null class → 0, conservative)
- earliest_plant = last_frost − offset; latest_plant = first_frost − DTM
- Edge: DTM None → CalcUnavailable("days_to_maturity").

**12. fertilizer_compost_rate**
`(*, nutrient_removal_n_kg_ha:float, nutrient_removal_p_kg_ha:float|None, nutrient_removal_k_kg_ha:float|None, area_m2:float, compost_N_pct:float=0.015, application_efficiency:float=0.50) -> {n_kg:float, p_kg:float|None, k_kg:float|None, compost_kg:float}`
- area_ha = area_m2 / 10_000; n_kg = removal_n * area_ha; compost_kg = n_kg / (compost_N_pct * application_efficiency); p_kg/k_kg = removal_* * area_ha (informational)
- Edge: removal_n None → CalcUnavailable("nutrient_removal_n_kg_ha"); compost_N_pct*eff > 0.

**13. crop_profit_comparison**
`(crops:list[CropEconomics], *, bed_meters:float|None=None) -> list[CropRank]` where `CropEconomics(crop_id, name_he, avg_yield_per_bed_m, documented_price, documented_price_unit, kg_per_unit, seed_cost_per_m=None)`
- per crop: revenue_per_m = yield_per_m * price_per_kg (convert unit); margin_per_m = revenue_per_m − (seed_cost_per_m or 0); sort by margin_per_m desc; if bed_meters given, also total = margin_per_m*bed_meters.
- Edge: crops with missing yield/price are excluded and returned in a separate `skipped` list (not silently dropped).

**14. seed_input_cost**
`(*, grams_needed:float, seed_price_per_g:float|None=None, pack_price:float|None=None, grams_per_pack:float|None=None) -> {packs:int|None, cost:float}`
- if seed_price_per_g: cost = grams_needed * seed_price_per_g
- elif pack_price and grams_per_pack: packs = ceil(grams_needed/grams_per_pack); cost = packs*pack_price
- else ValueError (need one pricing mode).

`calculator_meta.py` maps each calc id → {audience, required_book_fields, assumption_keys, user_inputs} so the UI/ingest can decide enabled/disabled per crop (must match Catalog §6 — AC-08).

---

## 6. Complete/partial integration (Gap-Fill §2)

- A calculator is **enabled** for a crop iff every `required_book_field` (per `calculator_meta`) has `field_state == VALIDATED` or `UNVALIDATED` (i.e., a `value_best` exists). **Disabled** iff any required field is `MISSING`.
- UNVALIDATED required fields → calculator runs but its result card shows the asterisk/"based on web-sourced data" note.
- τ = 0.40 (config; finalize with team_00 post-snapshot). Field-state computed once in `sfa_ingest_push.py` and carried in payload; the UI does not re-derive.

---

## 7. UI contract (delivery tier)

- **Two audiences, switchable:** Cards (gardener, default for `/crop-book/`) and Table (farmer). Small diff: same data, different density; Table exposes calculators #6/#7/#9/#12/#13 inline per row; Cards surface #1/#2/#4/#5/#8/#10/#11 per crop.
- **Per-crop views:** Simple (headline values + 3–4 key calcs), Full (all fields + all enabled calcs), Drill-down (per-variety, source provenance, confidence).
- **AssumptionField component:** renders default, inline override input, explainer (Hebrew), and "read more →" nimrod.bio link from `ASSUMPTIONS`. Override is client-side, recomputes the calc; never mutates DB.
- **Read ONE winning value:** every displayed agronomic number is `value_best`; provenance (sources, confidence) lives behind the Drill-down. UI never re-resolves the hierarchy.
- **Family rotation hint:** informational chip from `crop_families` (Catalog §5).
- **Honesty:** asterisks on UNVALIDATED, "—" + "request info" on MISSING, disabled calcs explain the missing field.

---

## 8. Hosting / deploy (canon — no drift)

Delivery tier is **uPress** (`sfa.nimrod.bio`, Slim4/PHP/MySQL). Backend Postgres on **waldhomeserver** (never serves users). Deploy = data push (Mac/server → `POST /api/v1/ingest`, HMAC) + UI mirror (waldhomeserver FTPS relay → uPress, `scripts/ftp_deploy_sfa_ui.sh`). See `documentation/02-architecture/sfa-delivery-tier.md`. **Never deploy the site to the home server.** Deploy is a gated step (team_00 go-ahead), not part of build.

---

## 9. Build sequence (junior-dev executable)

1. `field_policy.py` += 2 keys (§3.1); `test_field_policy.py` extended → green.
2. Ensure `succession_interval_weeks` source_values rows exist (§3.2); run `seed --enrich`; verify both fields produce `crop_field_enrichment` rows.
3. `assumptions.py` registry + tables + `get_assumption` (§4); `test_assumptions.py`.
4. `calculators.py` — 14 pure functions + dataclasses + `CalcUnavailable` (§5); `test_calculators.py` ≥2 cases each.
5. `calculator_meta.py` mapping (§5 end); `test_calculator_meta.py` cross-checks Catalog §6.
6. `sfa_ingest_push.py` — whitelist += 2 fields, embed `field_state` + `ASSUMPTIONS` into payload (§3.3/§6).
7. Delivery-tier templates — calculator panel, AssumptionField, audience switch, Simple/Full/Drill, complete/partial (§7) — **embeds team_35 §10 mockups**.
8. `validate_aos.sh` 0 FAIL; full `composer test` + `pytest tests/crop_book/` green.
9. Generate `COVERAGE_SNAPSHOT_CB1` (Gap-Fill §4); WR fallback + Nimrod fill-list to reach COMPLETE on launch set.
10. Gated deploy (data push + UI mirror) on team_00 go-ahead → live smoke.

### 9.3 Calc execution location
Default: **Python computes once, server-renders** results into the payload/templates (single source of truth, fully unit-tested). Client-side AssumptionField overrides recompute via a thin JS mirror **only** for the interactive calculators (#1,#7,#8,#9,#10,#12) — the JS mirror must be covered by parity tests against the Python outputs (AC-11). Date calculators (#3,#4,#5,#6,#11) and #13/#14 may be server-render-only for v1.

---

## 10. UI MOCKUPS — ⏳ PENDING team_35 (LOD300)

> **PLACEHOLDER.** This section embeds the **approved team_35 LOD300 mockups**: Cards + Table, Simple/Full/Drill-down, the calculator panel, the `AssumptionField` component (germination 90% / bed-width 80 cm with explainer + nimrod.bio link), and the complete/partial states (asterisks, "request info", disabled-calc explainer). team_35 is activated via `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/ACTIVATION_PROMPT_v1.0.0.md` (Deliverable 5) with the approved Calculator Catalog attached. **LOD400 locks to v1.0.0 and goes to L-GATE_S only once these mockups are embedded and approved by team_00.**

---

## 11. Acceptance criteria (precision gate)

| AC | Criterion |
|----|-----------|
| AC-01 | `field_policy.py` has `days_in_nursery_cell` + `succession_interval_weeks`; `get_field_policy` returns them; `test_field_policy` green. |
| AC-02 | `seed --enrich` produces `crop_field_enrichment` rows for both new fields on the shown set (≥1 each where source data exists). |
| AC-03 | `assumptions.py` ASSUMPTIONS has all 8 keys; `germination_rate` + `bed_width` have non-null `post_url`; `get_assumption` honors override. |
| AC-04 | `succession_interval_weeks` has ≥1 `source_values` row for the shown set before enrichment. |
| AC-05 | `calculators.py` implements all 14 with the exact §5 signatures; each raises `CalcUnavailable(<field>)` on a None required book value. |
| AC-06 | `test_calculators.py` ≥30 tests (≥2/calc, incl. one edge each); all green; numeric results match §5 formulas. |
| AC-07 | `calculator_meta` required-field map equals Catalog §6 (test asserts equality). |
| AC-08 | A calculator is disabled iff a required book field is MISSING; enabled (flagged) when UNVALIDATED — verified by unit test over a synthetic field_state map. |
| AC-09 | `sfa_ingest_push` payload carries the 2 new agronomy fields + per-field `field_state` + `ASSUMPTIONS`; existing keys preserved. |
| AC-10 | UI: audience switch (Cards/Table), Simple/Full/Drill-down, AssumptionField (default+override+explainer+link), complete/partial rendering — all present (embeds §10). |
| AC-11 | Interactive JS calc mirror (#1,#7,#8,#9,#10,#12) parity-tested against Python outputs. |
| AC-12 | `validate_aos.sh` 0 FAIL; `pytest tests/crop_book/` + `composer test` green; no change to LOD500_LOCKED files (§2). |
| AC-13 | Live smoke (post gated deploy): a COMPLETE crop shows enabled calculators with correct numbers; a PARTIAL crop shows asterisks + disabled calc + "request info"; served from uPress (not home server). |

---

## 12. Forward API contracts (module boundary)

Calculator outputs are the stable contract to future modules. Do not let CB-2/3/4/5 re-derive:
- `sowing_date_from_harvest`, `harvest_window_from_sowing`, `succession_schedule` → **Planner (CB-2)** / **Tasks (CB-3)** date anchors.
- `beds_for_target_yield`, `plant_population` → **Planner (CB-2)** bed-map.
- `expected_revenue`, `crop_profit_comparison`, `seed_input_cost` → **Sales/POS (CB-4)**.
- `crop_field_enrichment` + source provenance → **Tend (CB-5)** OP-class write-back loop.

Crop Book v1 owns **agronomic knowledge + calculators only**. These four modules are FUTURE; their LOD100 placeholders are registered (Deliverable 6).

---

## 13. Risks

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | `succession_interval_weeks` has no real source → calc #6 disabled for most crops | Acceptable PARTIAL; WR/EX fill per Gap-Fill; calc gracefully disabled |
| R-02 | JS calc mirror drifts from Python | AC-11 parity tests; limit JS to 6 interactive calcs |
| R-03 | AssumptionField post_url content (nimrod.bio) not ready at launch | germination/bed-width posts are a team_00 content dependency; block launch on those 2 only |
| R-04 | τ=0.40 mislabels too many crops PARTIAL | Finalize τ with team_00 after first coverage snapshot |
| R-05 | Deploy drift to home server | Hosting canon §8; deploy script + smoke assert uPress origin |

---

*Author team_100. Builder team_10 (Sonnet) → QA team_50 (Haiku) → L-GATE_V team_190 (non-Claude, IR#1). This draft is NOT yet at L-GATE_S — it locks to v1.0.0 when §10 mockups are embedded.*
