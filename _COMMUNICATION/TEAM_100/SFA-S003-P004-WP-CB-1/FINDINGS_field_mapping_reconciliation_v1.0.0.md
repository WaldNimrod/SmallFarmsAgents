# FINDINGS — Calculator Field-Mapping Reconciliation — SFA-S003-P004-WP-CB-1 — team_100 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1)
**Type:** FINDINGS (requires a follow-up reconciliation slice before the UI build)
**Severity:** MAJOR (4 of 14 calculators would be disabled for all crops as currently mapped)

---

## 1. What happened

The Calculator Catalog / Mandatory Field Schema / LOD400 field names were derived from **spec text** (WP-B1 spec + the model inventory), not verified against the **live enriched vocabulary** in `crop_field_enrichment`. A live check against the Mac `oma-postgres` (head 057) found several calculator-required fields that are **named differently** or **not present in `crop_field_enrichment`**.

## 2. Live evidence (Mac oma-postgres, `crop_field_enrichment` row counts)

| Calculator field (as specced) | Enriched rows | Verdict |
|-------------------------------|---------------|---------|
| `days_to_maturity` | 347 | ✅ OK |
| `harvest_window_max_days` | 274 | ✅ OK |
| `harvest_window_min_days` | **0** | only `max` exists — no calc uses `min` in its formula, so OK (drop from "mandatory") |
| `in_row_spacing_cm` | 291 | ✅ OK |
| `rows_per_bed` | 308 | ✅ OK |
| `avg_yield_per_bed_m` | 106 | ✅ OK (exists; `yield_per_m2_kg` (132) is a separate per-m² field — do not confuse) |
| `documented_price` | 116 | ✅ OK |
| `seeds_per_gram` | 261 | ✅ OK |
| `nutrient_removal_n/p/k_kg_ha` | 210/178/187 | ✅ OK |
| `succession_interval_weeks` | 140 | ✅ OK |
| **`days_in_nursery_cell`** | **0** | ❌ WRONG NAME — real field is **`days_in_gh_total`** (253 rows) |
| **`planting_method`** | **0** | ❌ not in `crop_field_enrichment` (categorical — likely a `crop_varieties` column) |
| **`planting_season`** | **0** | ❌ not in `crop_field_enrichment` (categorical) |
| **`frost_tolerance_class`** | **0** | ❌ not in `crop_field_enrichment` (categorical — WP-C4 source_values, never enriched) |

## 3. Impact on the 14 calculators

| Calc | Depends on a problem field | Effect as-mapped | After fix |
|------|----------------------------|------------------|-----------|
| #3 nursery trays | `days_in_nursery_cell` | disabled (0 rows) | **works** via `days_in_gh_total` (253) |
| #4 sow-date | `days_in_nursery_cell`, `planting_method` | disabled | works once method read-path fixed |
| #5 harvest-window | `days_in_nursery_cell`, `planting_method` | disabled | works once method read-path fixed |
| #6 succession | `planting_season` | season-clamp degraded | works (interval=140 ok; season optional) |
| #11 frost-window | `planting_season`, `frost_tolerance_class` | disabled | needs frost-class read-path |
| #1,#2,#7,#8,#9,#10,#12,#13,#14 | — | ✅ all required fields enriched | ✅ unaffected |

The calculator **math is correct** (unit-tested, 92/92). The defect is the **mapping + read path**: which field name / which table feeds each calculator.

## 4. Root cause: not everything is in `crop_field_enrichment`

The LOD400 assumed every calculator input is a reconciled `value_best`. Reality: **categorical** fields (`planting_method`, `planting_season`, `frost_tolerance_class`) are **not reconciled numerics** — they live as `crop_varieties` columns or unenriched `source_values`. The read path must cover both:
- **Numeric reconciled fields** → `crop_field_enrichment.value_best` (as designed).
- **Categorical fields** → either (a) the `crop_varieties` column directly, or (b) a `hard_winner` enrichment we add for them, or (c) a small categorical-resolution helper.

## 5. Recommended fix (a bounded reconciliation slice — before the UI build)

1. **Rename** the nursery field everywhere: `days_in_nursery_cell` → **`days_in_gh_total`** (field_policy entry, ingest whitelist, `calculator_meta` required fields for #3/#4/#5, `CalcUnavailable` messages). Already-enriched (253 rows) → calc #3 works immediately.
2. **Decide the categorical read path** (team_00 / team_100): for `planting_method`, `planting_season`, `frost_tolerance_class` — read from `crop_varieties` columns (simplest, data already there) **or** add `hard_winner` enrichment for them. Recommendation: **read the column directly** (categorical, single-source, no reconciliation needed) and treat "column NULL" as MISSING in the field_state logic.
3. **Drop** `harvest_window_min_days` from the mandatory set (no calculator formula uses it).
4. Update `calculator_meta` required-field map + the spec artifacts (Catalog §6, Schema §2, LOD400 §3/§5) to the verified vocabulary; re-run the disabled-state tests.
5. Re-generate the coverage snapshot (Gap-Fill §4) against the corrected field set to get the true COMPLETE/PARTIAL split.

## 6. Status

- The committed backend slice (`fd7dfba`) is **math-correct and tested**; this reconciliation is a **follow-up correction**, not a rebuild.
- Tracked for the next backend step (before/with the UI slice). No deploy depends on it yet.
- The 9 calculators with all-enriched inputs (#1,#2,#7,#8,#9,#10,#12,#13,#14) are already correct.

---

*Discovered during the server-DB assessment (live DB cross-check). Recommend a short reconciliation dispatch to team_10 after team_00 rules on the categorical read path (§5.2).*
