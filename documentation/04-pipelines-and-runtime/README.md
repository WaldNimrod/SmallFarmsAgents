# Pipelines and runtime

## Standard batch flow

1. **Create `ingestion_run`** (manual admin, cron runner, or CLI).
2. **`run_pipeline(ingestion_run_id)`** (`scheduler/pipeline.py`):
   - Collect + parse per source → `raw_extracted_items` (`extracted`)
   - Optional: `NormalizerEngine` → `normalized` / `unresolvable` / `ignored` (scope skip)
   - `AggregatorEngine` for a UTC calendar day
   - Optional: `PublishEngine` (rolling 7d window)

## Normalizer order

Stages run in order (see `normalizer/engine.py`):

1. **scope_skip** — `catalog_scope_skip_rules` → `ignored` if matched  
2. alias → organic → price_parse → unit → quantity → price_norm → basket  

Counts returned include **`scope_skipped`** when rules apply.

## Maintenance (no new fetch)

| Operation | Entry | Effect |
|-----------|--------|--------|
| Re-queue unresolvable only | Admin “catalog renormalize” or `catalog_renormalize` CLI | `unresolvable` → `extracted`, then normalize → aggregate → publish |
| Full refresh (community) | Admin “full refresh” or `full_data_refresh` CLI | Deletes `normalized_observations` for community rows in `normalized`/`unresolvable`, resets to `extracted`, then full normalize → aggregate → publish. **Does not** reset approved `ignored` rows. |

## Scheduler

- Cron entrypoint: `python -m organic_market_agent.scheduler.runner`
- Uses `scheduler_config` row for time window and enabled flag

## Related docs

- [`../06-scripts-and-cli/`](../06-scripts-and-cli/) — exact commands
- [`../08-troubleshooting/`](../08-troubleshooting/) — failures and alerts
