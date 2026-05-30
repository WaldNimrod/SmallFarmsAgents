# CALCULATOR CATALOG — SFA-S003-P004-WP-CB-1 — team_100 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1 — calculator-driven)
**Type:** CALCULATOR_CATALOG
**Status:** APPROVED by team_00 (in-session, 2026-05-30) — LOCKED scope for the mandatory-field schema
**Deliverable:** 1 of 6 (Crop Book spec program)

---

## 1. Purpose & scope rule

This catalog is the **scope-defining artifact** for Crop Book v1. The locked rule (team_00):

> **A field is MANDATORY iff (a) JMF already carries it, OR (b) a calculator in this catalog needs it.**

The calculators turn the existing agronomic data store from a *reference* into a *planning tool*. Every operand a calculator reads is either:
- a reconciled **book value** — `crop_field_enrichment.value_best` for `(variety, field_name)` (the ONE winning value from the multi-source services layer), or
- an **`AssumptionField`** — a sensible default the user can override inline (see §3), or
- a direct **user input** (area, target date, target quantity, price).

**14 calculators, approved 2026-05-30.** (Soil/liming calculator considered and explicitly NOT included this WP.)

---

## 2. The 14 calculators

Audience: **G** = home gardener (Cards UX) · **F** = small farmer (Table UX) · **B** = both.
Legend: `book field` = reconciled value_best · *AssumptionField* · **[input]** = user-typed.

| # | Calculator | Aud. | Book fields | AssumptionFields | User inputs | Formula |
|---|-----------|------|-------------|------------------|-------------|---------|
| 1 | **Seed quantity to buy** | B | `rows_per_bed`, `in_row_spacing_cm`, `seeds_per_gram` | *germination_rate=90%*, *oversow=1.1* | **bed-length m**, **seeds/hole** | plants = (len·100 / spacing)·rows·seeds_per_hole; seeds = plants / germ_rate · oversow; **grams = seeds / seeds_per_gram** |
| 2 | **Transplants / seedlings needed** | B | `rows_per_bed`, `in_row_spacing_cm` | — | **bed-length m** (or area) | plants = (len·100 / spacing)·rows |
| 3 | **Nursery trays + sow date** | F | `days_in_nursery` | *tray_cells (by `nursery_tray_type`)*, *oversow=1.1* | from #2: plants; **field-set date** | trays = ceil(plants·oversow / tray_cells); tray-sow = field-set − days_in_nursery |
| 4 | **Sowing date (back-calc from harvest)** | B | `days_to_maturity`, `days_in_nursery`, `planting_method` | — | **target harvest date** | transplant: sow = harvest − DTM − nursery; direct: sow = harvest − DTM |
| 5 | **Harvest date + window (forward)** | B | `days_to_maturity`, `harvest_window_max_days`, `planting_method`, `days_in_nursery` | — | **sow date** | start = sow (+ nursery if transplant) + DTM; end = start + harvest_window_max_days |
| 6 | **Succession schedule** | F | `succession_interval_weeks`, `planting_season` | — | **first sow date**, **# successions** (or season end) | dates = [start + n·interval_weeks]; clamp to planting_season / frost window (#11) |
| 7 | **Beds / bed-meters for a target yield** | F | `avg_yield_per_bed_m` | *std_bed_length_m=30* | **target kg** | bed_m = target_kg / yield_per_m; beds = bed_m / std_bed_length_m |
| 8 | **Expected yield from an area** | B | `avg_yield_per_bed_m` | — | **bed-length m** | yield_kg = yield_per_m · len_m  *(= team_35 `CalcField` reference example)* |
| 9 | **Expected revenue** | F | `avg_yield_per_bed_m`, `documented_price`, `documented_price_unit`, conversion group | — | **area / bed-length m** | revenue = yield_kg · price; unit-convert bunch/head → kg via `crop_unit_conversions` |
| 10 | **Plant population / spacing layout** | B | `rows_per_bed`, `in_row_spacing_cm` | *bed_width=80 cm* | — | plants_per_m2 = (rows / bed_width_m)·(100 / spacing_cm); render visual grid |
| 11 | **Frost / planting window** | B | `frost_tolerance_class`, `days_to_maturity`, `planting_season` | *hardiness_offset(class)* | **last frost date**, **first frost date** | earliest_plant = last_frost − hardiness_offset(class); latest_plant = first_frost − DTM |
| 12 | **Fertilizer / compost rate** | F | `nutrient_removal_n_kg_ha`, `nutrient_removal_p_kg_ha`, `nutrient_removal_k_kg_ha` | *compost_N_pct=1.5%*, *application_efficiency=0.5* | **bed area** (or bed-length m) | area_ha = area / 10 000; N_kg = removal_n_kg_ha · area_ha; compost_kg = N_kg / (compost_N_pct · efficiency); P, K shown alongside (informational) |
| 13 | **Crop profit comparison** | F | `avg_yield_per_bed_m`, `documented_price(+unit)` across crops | — | **bed-meters available** (optional) | per crop: revenue/m = yield_per_m · price; if #14 set, margin/m = revenue/m − seed_cost/m; rank descending |
| 14 | **Seed / input cost** | F | from #1: grams needed | — | **seed price /g** (or **pack price** + **g/pack**) | cost = grams · seed_price (or packs · pack_price); feeds margin into #13 |

---

## 3. The `AssumptionField` pattern (team_00 directive, 2026-05-30)

Several operands above are not per-crop book data but **planning assumptions**. team_00 directed these be a **first-class UI component** — never a silent constant:

**`AssumptionField` = { default value · inline user override · a clear, attractive explainer (when/why/how to change it) · a "read more →" link to a full nimrod.bio blog post }.**

| AssumptionField | Default | Used by | Explainer theme | nimrod.bio post |
|-----------------|---------|---------|-----------------|-----------------|
| `germination_rate` | **90%** | #1 | How & why seeds lose viability with age; how to test; when to raise oversow | REQUIRED (seed aging) |
| `bed_width` | **80 cm** | #10 | Why we translate JM Fortier's 30″ to **80 cm**, not 75 — our standardization rationale | REQUIRED (bed geometry) |
| `oversow` | 1.1 (×) | #1, #3 | Why sow ~10% extra; thinning vs gaps | optional |
| `tray_cells` | by `nursery_tray_type` (e.g. 128) | #3 | Tray sizing; cells vs plug size | optional |
| `std_bed_length_m` | 30 m | #7 | Standard bed length basis | optional |
| `hardiness_offset(class)` | table §4 | #11 | Frost tolerance classes → safe-plant offsets | optional |
| `compost_N_pct` | 1.5% | #12 | Typical N content of compost; reading a compost analysis | optional |
| `application_efficiency` | 0.5 | #12 | First-year N availability from compost | optional |

**Rules:**
- An AssumptionField **never disables** a calculator — it always has a default.
- germination_rate (90%) and bed_width (80 cm) **must ship with a published explainer + nimrod.bio link** at launch; the others may launch with explainer text and a link added later.
- Defaults live in an **AssumptionField config registry** (see Mandatory Field Schema), not hard-coded in calculator logic.

---

## 4. `hardiness_offset` table (calc #11) — initial defaults

Maps `frost_tolerance_class` (existing enriched field) → days you may plant before/after frost. Tunable AssumptionField; initial proposal:

| frost_tolerance_class | earliest plant (days vs last frost) | notes |
|-----------------------|-------------------------------------|-------|
| `very_hardy` / `hardy` | last_frost − 28 | tolerates hard frost |
| `semi_hardy` | last_frost − 14 | light frost OK |
| `tender` | last_frost + 0 | plant at/after last frost |
| `very_tender` / `warm` | last_frost + 14 | needs warm soil |
| (null / unknown) | last_frost + 0 | conservative default; flag as assumption |

---

## 5. Companion / rotation (NOT a calculator)

team_00 decision: a **family-based rotation hint**, informational only, derived from existing `crop_families` — *"don't follow the same botanical family in this bed for N seasons"* (N is an AssumptionField, default 3). No companion-matrix schema field this WP; a richer companion model is deferred to Planner/Tasks (WP-CB-2/CB-3).

---

## 6. Field → calculator dependency map (drives the mandatory schema)

| Field (book) | Status today | Calculators needing it |
|--------------|--------------|------------------------|
| `days_to_maturity` | enriched ✓ | 4, 5, 11 |
| `harvest_window_max_days` | enriched ✓ | 5 |
| `in_row_spacing_cm` | enriched ✓ | 1, 2, 10 |
| `rows_per_bed` | enriched ✓ | 1, 2, 10 |
| `avg_yield_per_bed_m` | enriched ✓ | 7, 8, 9, 13 |
| `documented_price` (+unit) | enriched ✓ | 9, 13 |
| `planting_season` | enriched ✓ | 6, 11 |
| `planting_method` | enriched ✓ | 4, 5 |
| `frost_tolerance_class` | enriched ✓ | 11 |
| `seeds_per_gram` | enriched ✓ (sparse) | 1 |
| `nutrient_removal_n/p/k_kg_ha` | enriched ✓ | 12 |
| `family` (`crop_families`) | present ✓ | rotation hint |
| **`days_in_nursery`** | source_values only (`days_in_nursery_cell`), **NOT enriched** | 3, 4, 5 → **WIRE** |
| **`succession_interval_weeks`** | column, **NOT enriched** | 6 → **WIRE** |

**Net new agronomic enrichment work = 2 fields** (`days_in_nursery`, `succession_interval_weeks`). All other operands are already enriched, AssumptionFields, or user inputs. `germination_rate` is an AssumptionField (90%), **not** a schema field.

---

## 7. Disabled-state contract (partial crops)

For a shown crop, a calculator is rendered **disabled** iff any required **book field** has no `value_best` (or `confidence_score < τ`, see Gap-Fill Plan). The disabled state shows: which field is missing, that the calculator will enable when the data exists, and a **"request info"** CTA. AssumptionFields and user inputs never cause a disabled state.

---

## 8. Output contracts (forward to future modules)

Each calculator is specified as a **pure function** with typed outputs so future modules consume them without re-deriving:
- #4/#5/#6 → date sequences → **Planner (CB-2)** + **Tasks (CB-3)** timing anchors.
- #7/#10 → bed-meters / plant population → **Planner (CB-2)** bed-map.
- #9/#13/#14 → revenue / margin → **Sales/POS (CB-4)**.
- #1/#3 → seed & tray quantities → **Tasks (CB-3)** procurement.

Module boundary (locked): **Crop Book owns agronomic knowledge and the calculators only.** Planner/Tasks/POS/Tend are downstream consumers of these typed outputs.

---

*Approved by team_00 in-session 2026-05-30. This catalog is the locked input to the Mandatory Field Schema (Deliverable 2), the LOD400 (Deliverable 4), and the team_35 activation (Deliverable 5).*
