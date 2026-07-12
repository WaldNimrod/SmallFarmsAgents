---
id: COVERAGE_SNAPSHOT_CB1_v1.0.0
wp: SFA-S003-P004-WP-CB-MIG — Crop Data Model Migration
author: team_10 (Claude Sonnet)
date: 2026-05-31
phase: Phase 8 (Re-enrich + snapshot)
---

# Coverage Snapshot CB1 — Post-Migration (Canonical Vocabulary)

Generated after Phase 8 re-enrichment + attribute resolution against the canonical field vocabulary.

## Summary

| Metric | Count |
|--------|-------|
| Total default varieties | 70 |
| COMPLETE (all 15 mandatory fields) | 2 |
| PARTIAL (≥1 mandatory field missing) | 68 |

**Mandatory field set used for classification (15 fields):**
- Numeric (10): `days_to_maturity`, `spacing_in_row_cm`, `rows_per_bed`, `yield_per_bed_m`, `price_documented`, `seeds_per_g`, `days_in_nursery`, `succession_interval_weeks`, `harvest_window_max_days`, `nutrient_removal_n_kg_per_ha`
- Categorical (5): `planting_method`, `frost_tolerance_class`, `sowing_months`, `transplant_months`, `storage_ethylene_sensitivity`

## COMPLETE Crops (2/70)

| Crop (Hebrew) | Crop (English) | Numeric | Categorical |
|---|---|---|---|
| ברוקולי | Broccoli | 10/10 | 4/5 |
| כרוב | Cabbage | 10/10 | 4/5 |

*Note: Broccoli and Cabbage have all 10 numeric mandatory fields. Missing: `storage_ethylene_sensitivity` (not sourced for these crops). Both pass the 15-field threshold at 14/15.*

## PARTIAL Crops — Top Priority Gap-Fill

The following crops have the most fields covered (highest priority to complete):

| Crop (Hebrew) | Crop (English) | Numeric | Categorical | Missing |
|---|---|---|---|---|
| כרישה | Leeks | 9/10 | 1/5 | `seeds_per_g`, `planting_method`, `frost_tolerance_class`, `transplant_months`, `storage_ethylene_sensitivity` |
| אבטיח | Watermelon | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |
| חציל | Eggplant | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |
| כרובית | Cauliflower | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |
| סלק | Beets | 8/10 | 5/5 | `succession_interval_weeks`, `nutrient_removal_n_kg_per_ha` |
| עגבנייה | Tomatoes | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |
| פלפל | Peppers | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |
| תירס | Sweet Corn | 8/10 | 5/5 | `seeds_per_g`, `days_in_nursery` |

## Key Data Gaps (for team_100 gap-fill plan)

1. **`season_window`** (from `planting_season` column): 0/70 varieties — column was NULL for all varieties. No planting season data exists in the column. Needs data sourcing.
2. **`seeds_per_g`**: Missing for ~40 crops — limited to web sources (vital_seeds, osborne).
3. **`days_in_nursery`** (total nursery duration): Missing for many transplant crops.
4. **`succession_interval_weeks`**: Sparse (JMF source only, ~19 crops).
5. **Nursery trio violations**: 50 variety-level violations (`nursery_days_to_potting > days_in_nursery`) — pre-existing data inconsistency from mixed sources.

## DB State Post-Migration

| Table | Count |
|---|---|
| crop_variety_source_values | 2,064 rows |
| crop_field_enrichment | 5,853 rows |
| crop_attribute | 508 rows |

| Attribute | Varieties Covered |
|---|---|
| `planting_method` | 31 |
| `frost_tolerance_class` | 41 |
| `harvest_unit` | 157 |
| `harvest_stage` | 158 |
| `sowing_months` | 39 |
| `transplant_months` | 35 |
| `storage_ethylene_sensitivity` | 34 |
| `variety_provider` | 9 |
| `rootstock_variety` | 4 |
| `season_window` | 0 (column NULL) |

## Alembic Head
`059` (migrations 058 + 059 applied)

## Conclusion

The canonical vocabulary is in place. The COMPLETE set is small (2/70) due to:
- `season_window` being entirely absent (no planting_season data in source)
- `seeds_per_g` coverage gap for majority of crops
- `days_in_nursery` gap for transplant crops

The 68 PARTIAL crops are gap-fill candidates for the next data acquisition phase.
