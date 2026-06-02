# C3 — Blueberries pack research (CQ-P05) — Team 10 → Team 100

**Date:** 2026-04-08  
**From:** Team 10  
**To:** Team 100 (Architecture) — triggers **D1** Pantry ADR per `SPEC-20260408-PHASE-A-LOD400` §D1  
**Mandate:** MANDATE-20260408-V1-1-LOD400-EXEC Task 3–4

## Confirmation

**No code change was made in C3** (research-only task).

## C3 research table (PRD086)

Live population requires post–Phase B SQL on `raw_extracted_items` for active blueberry lines (spec §C3). **Not populated** in this session (no DB).

| source_code | source_name | raw_product_name | raw_unit | price | pack_description | grams_if_known | price_per_100g_calc |
|-------------|-------------|------------------|----------|-------|------------------|----------------|---------------------|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

**Operator SQL (bind when DB available):** see `SPEC-20260408-PHASE-A-LOD400` §C3 for the exact `SELECT` joining `products` / `sources` / `normalized_observations` (or raw) for **PRD086**.

## PRD087–PRD100 pack-size patterns (Pantry ADR input)

No additional pack-size patterns identified without live product titles. Team 10 will append rows here or in a dated addendum after Phase B ingestion.

## Next step

Team 100 may author `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md` when satisfied with completed C3 evidence; until then, completion report will state **D1 pending Team 100 authorship**.
