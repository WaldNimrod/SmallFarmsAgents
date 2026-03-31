# Pipelines and runtime

## Standard batch flow

1. **Create `ingestion_run`** (manual admin trigger, cron runner, or CLI).
2. **`run_pipeline(ingestion_run_id)`** (`scheduler/pipeline.py`):
   - Collect + parse per source → `raw_extracted_items` (`extracted`)
   - Optional: `NormalizerEngine` → `normalized` / `unresolvable` / `ignored` (scope skip)
   - `AggregatorEngine` for a UTC calendar day
   - Optional: `PublishEngine` (rolling 7d window)

Supports focused runs: optional `source_code` (single source), `skip_normalize`, `skip_publish` parameters.

## Normalizer pipeline (8+1 stages)

Stages run in order (see `normalizer/engine.py`):

1. **scope_skip** — `catalog_scope_skip_rules` match → `ignored` (301 active rules in 4 categories: grocery, dry_grocery, donation, cleaning)
2. **alias_resolver** — exact match (source-specific) → exact match (global) → substring match (longest first) against `product_aliases`
3. **organic_flag** — detect organic markers in product name
4. **price_parser** — extract numeric price from raw text (**blocking**: failure → `unresolvable`)
5. **unit_resolver** — resolve measurement units from rules + built-in map + product defaults
6. **quantity_parser** — extract quantity values
7. **price_normalizer** — normalize to canonical unit price
8. **basket_handler** — basket/CSA product special handling
9. **confidence** — compute confidence score [0.0, 1.0]

**Blocking stages:** `alias_resolver` and `price_parser`. After all stages, if `product_id`, `price_amount`, or `display_unit_id` is NULL → `unresolvable`.

Counts returned: `resolved`, `unresolvable`, `scope_skipped`, `skipped`.

## Aggregation and price rules

- `AggregatorEngine` computes `daily_aggregates` and `weekly_snapshots` per product/scope/channel.
- **Publish threshold:** ≥2 observations from ≥2 distinct sources.
- **Price dispersion rules** (see `aggregator/price_rules.py`):
  - 2-source spread >100% → suppress + `[AGG_PRICE_RULE:two_source_price_spread_gt_100pct]` alert
  - 3+-source outlier >2σ → suppress + `[AGG_PRICE_RULE:multi_source_outlier_gt_2sigma]` alert
- Dedup: second run on same date updates existing row (upsert on `uq_daily_aggregate`); duplicate alerts suppressed if `meets_publish_threshold` was already `false`.

## Maintenance (no new fetch)

| Operation | Entry | Effect |
|-----------|--------|--------|
| Re-queue unresolvable only | Admin "catalog renormalize" or `catalog_renormalize` CLI | `unresolvable` → `extracted`, then normalize → aggregate → publish |
| Full refresh (community) | Admin "full refresh" or `full_data_refresh` CLI | Deletes `normalized_observations` for community rows in `normalized`/`unresolvable`, resets to `extracted`, then full normalize → aggregate → publish. **Does not** reset approved `ignored` rows. |
| Prune old data | `prune_raw_pipeline` CLI | Deletes old `source_fetch_runs` + cascade older than configured days |
| Log cleanup | Admin `/scheduler` cleanup trigger | SQL-based cleanup of old runs with row-count feedback |

## Scheduler

- Cron entrypoint: `python -m organic_market_agent.scheduler.runner`
- Uses `scheduler_config` row for time window, enabled flag, retry attempts
- Self-gating: runs every minute via cron, only executes if `is_enabled=true` AND current time matches `run_hour:run_minute` (±1 min)
- Overlap guard: skips if another run is already in progress
- Writes `PipelineAlert` on completion (info/warning/error based on outcome)

## Data flow summary

```
Sources (20) ──► Collectors ──► Parsers ──► raw_extracted_items (508 rows)
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                              scope_skip      alias+normalize    (stuck)
                              → ignored        → normalized      → unresolvable
                              (334 rows)       (174 rows)        (0 rows)
                                                    │
                                                    ▼
                                        normalized_observations (174)
                                                    │
                                                    ▼
                                        daily_aggregates (87)
                                        weekly_snapshots (64)
                                                    │
                                                    ▼
                                        PublishEngine → manifest.json
                                                       public_report-{ts}.json/html
```

## Related docs

- [`../06-scripts-and-cli/`](../06-scripts-and-cli/) — exact commands
- [`../08-troubleshooting/`](../08-troubleshooting/) — failures and alerts
- [`../02-architecture/`](../02-architecture/) — module details
