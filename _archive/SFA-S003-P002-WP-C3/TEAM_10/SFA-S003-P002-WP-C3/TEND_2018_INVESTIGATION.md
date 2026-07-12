# Tend 2018 Investigation — WP-C3

**Date:** 2026-05-27
**Source files:** `data/external_sources/tend_multi_year/Tend_2018_*.csv`

## Files found

| File | Lines | Data rows | Notes |
|------|-------|-----------|-------|
| Tend_2018_TASKS.csv | ~62 | 61 | Task records |
| Tend_2018_GREENHOUSE_PLAN.csv | ~82 | 81 | Seedling schedules |
| Tend_2018_HARVESTS.csv | 1 | **0** | Header only — no harvest data |

## Decision: INGEST (CROP_PLAN + GREENHOUSE_PLAN; skip HARVEST STATS)

### Rationale

1. **HARVESTS file contains zero data rows** — only the CSV header is present.
   Running `parse_harvests_aggregate` on an empty CSV returns `([], 0)`. No
   harvest stats rows will be written for 2018.

2. **TASKS + GREENHOUSE_PLAN schemas match 2019+ format** — the existing
   `import_tend_overlay()` function processes these files identically via the
   same `TEND_CROP_MAP` lookup. No structural change was needed.

3. **`import_tend_overlay(session, dir, year=2018, dry_run=False)` called as-is**
   in `_run_c3_ingestion()`. The existing HARVESTS guard
   (`if harvests_df is not None and not harvests_df.empty`) prevents writing
   harvest stats when the file is empty.

## Ingestion results (live run 2026-05-27)

```
TendOverlaySummary(
  year=2018,
  task_template_rows_upserted=37,
  source_value_rows_upserted=33,
  harvest_stat_rows_upserted=0,
  harvests_aggregated=0,
  crop_map_misses=['Celeriac', 'Beans:', 'Mustard', 'Mizuna', 'Cauliflower', ...]
)
```

- **33 source_value rows** written to `crop_variety_source_values` with `source='Tend_2018'`
- **37 task_template rows** written to `crop_task_templates`
- **0 harvest stats** (as expected — HARVESTS file empty)
- Crop map misses (Celeriac, Cauliflower, Mizuna, etc.) are expected — these
  varieties are not in the `TEND_CROP_MAP` or not in the DB

## AC-C3-07 status: PASS
