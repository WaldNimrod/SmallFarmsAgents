---
id: COVERAGE_SNAPSHOT_SFA-S003-P002-WP-C6_v1.0.0
from: team_100 (Chief Architect)
date: 2026-05-28
type: evidence
wp: SFA-S003-P002-WP-C6
source: oma-postgres (organic_market_agent) @ alembic 056, post-WP-C5
---

# WP-C6 sparse-crop coverage snapshot (grounding for LOD400)

Live query of `crop_field_enrichment` (distinct `field_name` per crop) after
WP-C5 closure. "Sparse" = ≤2 enriched fields (WP-C6 LOD200 definition).

## Coverage distribution (all crops)
| enriched_fields | n_crops |
|---|---|
| 0 | 1 |
| 1 | 9 |
| 2 | 9 |
| 3 | 3 |
| 4 | 2 |
| 5 | 2 |
| 6 | 1 |
| 8 | 4 |
| 9–20 | 21 |

**Sparse set = 19 crops** (1×0, 9×1, 9×2). Matches the LOD200 "~20" estimate.

## The 19 sparse crops (target: ≥6 enriched fields each)
| crop_id | name_he | name_en | category | current ef |
|---|---|---|---|---|
| 57 | ג'ינג'ר | Ginger | vegetables | 0 |
| 5 | דפנה | Bay | fruit_trees | 1 |
| 1 | אזוב מצוי | Anise Hyssop | herbs | 1 |
| 28 | לימון בלם | Lemon Balm | herbs | 1 |
| 34 | נענע | Mint | herbs | 1 |
| 43 | מרווה | Sage | herbs | 1 |
| 47 | טרגון | Tarragon | herbs | 1 |
| 48 | טימין | Thyme | herbs | 1 |
| 13 | פנס סיני | Chinese Lantern | vegetables | 1 |
| 16 | גרגר נחלים | Cress | vegetables | 1 |
| 37 | תפוז | Oranges | fruit_trees | 2 |
| 22 | היביסקוס | Hibiscus | herbs | 2 |
| 29 | לימון ורבנה | Lemon Verbena | herbs | 2 |
| 32 | לובסטייה | Lovage | herbs | 2 |
| 50 | כורכום | Turmeric | herbs | 2 |
| 23 | ארטישוק ירושלמי | Jerusalem Artichoke | vegetables | 2 |
| 24 | ג'יקמה | Jicama | vegetables | 2 |
| 31 | עלי בייבי | Salad Mix | vegetables | 2 |
| 38 | פאק צ'וי | Pac Choi | vegetables | 2 |

By category: herbs ×10, vegetables ×7, fruit_trees ×2.

## Canonical enriched-field vocabulary (29 fields; top by coverage)
`days_to_maturity`, `harvest_window_max_days`, `rows_per_bed`,
`days_in_gh_total`, `soil_ph_target`, `soil_ph_liming_threshold`,
`seeds_per_gram`, `in_row_spacing_cm`, `germination_temp_c_min/opt/max`,
`storage_temp_c_min/max`, `storage_rh_pct_min/max`,
`nutrient_removal_n/p/k_kg_ha` (+ k2o/p2o5/ca/mg), `yield_per_m2_kg`,
`succession_interval_weeks`, `plants_per_m2`, `storage_life_days`,
`days_to_first_potting`, `avg_yield_per_bed_m`, `documented_price`.

A WR research pack supplying any **6+** of these per crop clears the target.

## Reproduce
```sql
WITH cov AS (
  SELECT c.id, c.name_he, c.category,
         COUNT(DISTINCT cfe.field_name) AS ef
  FROM crops c
  LEFT JOIN crop_varieties v ON v.crop_id = c.id
  LEFT JOIN crop_field_enrichment cfe ON cfe.variety_id = v.id
  GROUP BY c.id, c.name_he, c.category)
SELECT * FROM cov WHERE ef <= 2 ORDER BY category, ef;
```
