# Catalog scan — technical run report

**Date:** 2026-04-05 (UTC)  
**Team:** Team 10  
**Reference plan:** Catalog mapping scan, remediation, full run, and verification (Cursor plan, not edited).

## Artifacts produced

| Artifact | Path |
|----------|------|
| Metrics (before) | `data/catalog_scan_metrics_before.json` |
| Metrics (post-publish checkpoint) | `data/catalog_scan_metrics_final.json` |
| Baseline snapshot (before) | `data/catalog_scan_baseline_before.json` |
| Baseline snapshot (after) | `data/catalog_scan_baseline_after.json` |
| Exceptions register | `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_EXCEPTIONS_REGISTER_TEAM10.md` |
| Metrics helper script | `scripts/catalog_scan_collect_metrics.py` |
| DB migration (aliases) | `organic_market_agent/db/versions/071_alias_baby_mix_sprouts_blend.py` |

## Alembic

- **Head:** `071`
- **071:** Global aliases `מיקס בייבי` → PRD008; `נבטים , תערובת` → PRD033

## Pipeline commands executed

1. `catalog_renormalize` — re-queued 2 unresolvable rows; normalizer resolved 2; publish OK (**76** products in `public_report.json` at that checkpoint).
2. `run_ingestion --run-type manual --normalize` — **started** full fetch; **stopped** mid-run (long duration / agent limit). New raw rows were created for many sources.
3. `run_normalizer` — resolved **837**, unresolvable **95**, scope_skipped **1569**.
4. `run_aggregator --date 2026-04-05` — created **124**, updated **3** groups.
5. `run_publisher` — **77** products in rolling window.

## Baseline JSON comparison (`normalizer_baseline_snapshot_v1`)

| Field | Before | After | Delta |
|-------|--------|-------|-------|
| normalized (raw_extracted_items) | 2392 | 3231 | +839 |
| unresolvable | 2 | 95 | +93 |
| ignored | 3089 | 4658 | +1569 |
| distinct_unresolved_raw_names | 2 | 92 | +90 |

## Publish output

- **Products in `public_report.json`:** 77 (final)
- **Spot-check `normalized_unit`:** PRD067 → אריזת 12 ביצים; PRD071 / PRD086 → חבילה / אריזה; PRD072 still יחידה on published row set (historical observations).

## Backup

- `pg_dump` was **not** available in the execution environment; backup step **skipped**. Use `scripts/backup_postgres.sh` on a workstation with `libpq` before destructive maintenance.

## Hebrew executive summary

See [`2026-04-05_CATALOG_SCAN_EXEC_SUMMARY_HE_NIMROD.md`](2026-04-05_CATALOG_SCAN_EXEC_SUMMARY_HE_NIMROD.md).
