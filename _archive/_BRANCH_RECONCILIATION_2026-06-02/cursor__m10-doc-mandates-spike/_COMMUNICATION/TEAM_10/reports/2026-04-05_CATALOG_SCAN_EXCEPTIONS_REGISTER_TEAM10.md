# Catalog scan — exceptions register

**Date:** 2026-04-05  
**Task:** Catalog mapping scan, remediation, full run, and verification (plan execution)  
**Team:** Team 10 (implementation evidence)

## Summary

| raw_name / pattern | source | issue type | severity | status | proposed / actual fix |
|--------------------|--------|------------|----------|--------|------------------------|
| `מיקס בייבי` | SRC061 | alias | medium | **fixed** | Global alias → PRD008 (confidence 0.9), migration `071_alias_baby_mix_sprouts_blend.py` |
| `נבטים , תערובת` | SRC061 | alias | medium | **fixed** | Global alias → PRD033 (0.95), migration `071` |
| PRD072 passion fruit: `unit` on historical observations | multiple | unit semantics | low | **open** | Default product unit is `kg` (069); 10 rows still `unit` — review per source raw_unit_text; add `normalizer_rules` `unit_map` where needed |
| Pantry SKUs PRD087–PRD100: pack weight comparison | SRC036 / retail | normalization | medium | **open** | Epic: net weight from title → `unit_conversions` or `product_variants` |
| Gadi CSA baskets: line-count → basket tier | TBD | catalog / parser | medium | **open** | Architecture: deterministic ranges → PRD025/026/027; parser/template work |
| `pg_dump` not on PATH in CI/agent environment | n/a | ops | low | **open** | Install `libpq` / use `scripts/backup_postgres.sh` on operator workstation before `full_data_refresh` |
| New unresolvable backlog after partial `run_ingestion` + `run_normalizer` | SRC021 (61), SRC022, SRC028, … | alias | **high** | **open** | Batch aliases from `/unresolved` export; prioritize SRC021 EasyFarm strings |
| Ingestion run interrupted (agent timeout) | all sources | ops | medium | **open** | Re-run `run_ingestion --normalize` to completion on operator machine; then `run_aggregator` + `run_publisher` |

## Phase 1 metrics snapshot (before)

See repository `data/catalog_scan_metrics_before.json` and `data/catalog_scan_baseline_before.json`.

## Verification notes (Phase 4)

- Admin: `/runs`, `/products`, `/unresolved`, `/diagnostics`, pipeline alerts.
- Viewer: `scripts/viewer_server.sh` → `public_report.html`; confirm priority SKUs show expected `normalized_unit` labels post-publish.
