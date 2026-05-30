# MANDATORY FIELD SCHEMA — SFA-S003-P004-WP-CB-1 — team_100 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1)
**Type:** MANDATORY_FIELD_SCHEMA
**Status:** Derived from CALCULATOR_CATALOG_v1.0.0 (team_00 approved). Locked input to LOD400.
**Deliverable:** 2 of 6

---

## 1. Definition of "mandatory"

Mandatory set = **(every field JMF carries)** ∪ **(every book field a calculator reads)**.
A crop with all mandatory fields filled-and-validated above the confidence threshold τ is a **COMPLETE book**; otherwise **PARTIAL** (see Gap-Fill Plan, Deliverable 3).

`AssumptionField` operands (germination_rate, bed_width, oversow, …) and direct user inputs are **NOT** mandatory crop fields — they are planning assumptions with defaults (see Catalog §3), and they never affect a crop's complete/partial status.

---

## 2. Mandatory field register

| Field (DB `field_name`) | Unit | Source layer | Enriched today? | Action |
|--------------------------|------|--------------|-----------------|--------|
| `days_to_maturity` | days | source_values → enrichment | ✅ | none |
| `harvest_window_min_days` | days | source_values → enrichment | ✅ | none |
| `harvest_window_max_days` | days | source_values → enrichment | ✅ | none |
| `in_row_spacing_cm` | cm | source_values → enrichment | ✅ | none |
| `rows_per_bed` | rows | source_values → enrichment | ✅ | none |
| `avg_yield_per_bed_m` | kg/m | source_values → enrichment | ✅ | none |
| `documented_price` (+ `documented_price_unit`) | ILS | source_values → enrichment | ✅ | none |
| `planting_season` | text | source_values → enrichment | ✅ | none |
| `planting_method` | enum | source_values → enrichment | ✅ | none |
| `frost_tolerance_class` | enum | source_values → enrichment | ✅ | none |
| `seeds_per_gram` | 1/g | source_values → enrichment | ✅ (sparse) | gap-fill (data, not schema) |
| `nutrient_removal_n_kg_ha` | kg/ha | source_values → enrichment | ✅ | none |
| `nutrient_removal_p_kg_ha` | kg/ha | source_values → enrichment | ✅ | none |
| `nutrient_removal_k_kg_ha` | kg/ha | source_values → enrichment | ✅ | none |
| `family` (`crop_families.name_he` / `scientific_name`) | — | relational | ✅ | none |
| **`days_in_nursery_cell`** | days | source_values **only** | ❌ not enriched | **WIRE (§3.1)** |
| **`succession_interval_weeks`** | weeks | column **only** | ❌ not enriched | **WIRE (§3.2)** |

**Net schema work: 2 enrichment wirings.** No new agronomic columns. Calculators #12/#13/#14 add zero schema (nutrient_removal already enriched; profit & seed-cost use existing yield/price + user inputs).

---

## 3. Schema additions

### 3.1 Wire `days_in_nursery_cell` into enrichment

Data already lands in `crop_variety_source_values` with `field_name="days_in_nursery_cell"` (JMF Nursery & Transplant chart; midpoint of min/max, range in `note`) — but no `FieldPolicy`, so `enrichment_runner` produces no `value_best`.

**Add to `organic_market_agent/crop_book/field_policy.py` `FIELD_POLICY`:**
```python
"days_in_nursery_cell": FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP"),
    blend_strategy="weighted_mean",
    outlier=OutlierConfig(z_threshold=3.5),
),
```
- Calculators #3/#4/#5 read `value_best` for `field_name="days_in_nursery_cell"`.
- No migration: the source_values rows + enrichment table already exist; `run_enrichment` will populate `crop_field_enrichment` for this field on next run.
- **Ingest:** add `"days_in_nursery_cell"` to the agronomy whitelist in `organic_market_agent/publisher/sfa_ingest_push.py` (`_fetch_crop_varieties`, the field whitelist ~L313–330) so `payload_json.agronomy` carries it to the delivery tier.
- **Naming:** the calculator catalog calls this `days_in_nursery`; the DB/enrichment key stays `days_in_nursery_cell` (no rename — avoids touching LOD500_LOCKED importer code). The UI label is Hebrew; the field key is an internal contract.

### 3.2 Wire `succession_interval_weeks` into enrichment

Currently a `crop_varieties` column, not a reconciled field (no source_values rows, no policy). To make it a book value the UI/calculator #6 can read via `value_best`:

1. **Importer:** ensure at least one importer path writes `crop_variety_source_values` rows with `field_name="succession_interval_weeks"`, `value_numeric=<weeks>`, `unit="weeks"`, with the appropriate `source` + `trust_tier`. Candidate sources, in order: JMF succession column (if present in the JMF workbook), else team_00 EX / NI, else WR fallback (Gap-Fill Plan).
2. **Add to `FIELD_POLICY`:**
```python
"succession_interval_weeks": FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP"),
    blend_strategy="hard_winner",
),
```
3. **Ingest:** add `"succession_interval_weeks"` to the agronomy whitelist.
- No migration if we treat it purely through source_values → enrichment (the existing column may remain as a legacy direct field; the calculator reads `value_best`, the reconciled source of truth).

### 3.3 AssumptionField config registry

The planning assumptions (Catalog §3) need a single declarative home — default + explainer + post URL — readable by both the Python calculator layer and the UI:

```python
# organic_market_agent/crop_book/assumptions.py  (NEW)
from dataclasses import dataclass

@dataclass(frozen=True)
class Assumption:
    key: str
    default: float | dict        # scalar, or table (e.g. hardiness_offset)
    unit: str
    explainer_he: str            # short inline explainer (Hebrew)
    post_url: str | None         # "read more" nimrod.bio link (None until published)

ASSUMPTIONS: dict[str, Assumption] = {
    "germination_rate":        Assumption("germination_rate", 0.90, "fraction", "...", "https://nimrod.bio/..."),
    "bed_width":               Assumption("bed_width", 0.80, "m", "...", "https://nimrod.bio/..."),
    "oversow":                 Assumption("oversow", 1.10, "x", "...", None),
    "std_bed_length_m":        Assumption("std_bed_length_m", 30.0, "m", "...", None),
    "compost_N_pct":           Assumption("compost_N_pct", 0.015, "fraction", "...", None),
    "application_efficiency":  Assumption("application_efficiency", 0.50, "fraction", "...", None),
    "rotation_gap_seasons":    Assumption("rotation_gap_seasons", 3, "seasons", "...", None),
    # tray_cells & hardiness_offset are tables — see §3.4 / Catalog §4
}
```
- This is **config/seed data, not per-crop columns** → no migration.
- The UI `AssumptionField` component reads `default`, `explainer_he`, `post_url` from this registry (mirrored into the ingest payload or a static config the PHP tier reads).
- **germination_rate (90%)** and **bed_width (80 cm)** MUST have a non-null `post_url` at launch (content dependency on team_00).

### 3.4 Lookup tables (config, not columns)

- `tray_cells`: map `nursery_tray_type` (text, in source_values) → cells/tray (e.g. `"128"→128`, `"200"→200`, `"72"→72`). Seed from observed `nursery_tray_type` values; default 128 when unknown.
- `hardiness_offset`: `frost_tolerance_class` → offset days (Catalog §4).

---

## 4. Migration footprint

| Change | Migration needed? |
|--------|-------------------|
| `days_in_nursery_cell` enrichment wiring | **No** (policy + ingest whitelist only) |
| `succession_interval_weeks` enrichment wiring | **No** (policy + importer source_values rows + ingest whitelist) |
| AssumptionField registry + lookup tables | **No** (new Python config module + seed data) |

**Estimated Alembic migrations: 0–1** (none strictly required; a migration is only added if WP-CB-1 elects to persist AssumptionField overrides per-user, which is out of scope for v1). Head is currently ~057; any addition is purely additive.

**This is a major simplification vs. the original draft** (which assumed a new `germination_rate` column + migration). team_00's "AssumptionField default 90%" decision removed it.

---

## 5. Confidence / validation state (feeds Gap-Fill Plan)

The services layer already emits, per `(variety, field_name)` in `crop_field_enrichment`: `value_best`, `confidence_score`, `winning_source_class`, `source_count`. The UI derives:
- **validated value** → `winning_source_class ∈ {EX, NI}` (hard override) **or** `confidence_score ≥ τ`.
- **unvalidated value (asterisk)** → present but `confidence_score < τ` or `winning_source_class ∈ {WR, WB, UC}`.
- **missing** → no `crop_field_enrichment` row for that field.

τ and the complete/partial state machine are defined in the Gap-Fill Plan.

---

*Locked input to the LOD400 (Deliverable 4). No governance edit; no build this session.*
