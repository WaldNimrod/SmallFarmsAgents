# Architecture

## Layering

| Layer | Responsibility | Primary package paths |
|-------|------------------|------------------------|
| Collect | Fetch raw HTTP assets | `scheduler/run_ingestion.py`, collectors (per source) |
| Parse | Raw asset → `raw_extracted_items` | `parsers/` |
| Normalize | Map to products, units, prices → `normalized_observations` | `normalizer/` |
| Aggregate | Daily / weekly rollups | `aggregator/` |
| Publish | Rolling window public index + manifest | `publisher/` |
| Admin | Local monitoring & writes | `admin/` |

## Key design choices

- **Normalizer rules and aliases are data-driven** (PostgreSQL); change without redeploy where possible.
- **WordPress reads static files only** — no live DB connection from the public site.
- **Pipeline alerts** use stable message prefixes (`[OPS:…]`, `[PIPELINE:…]`, `[SIMULATION:test]`, etc.) — see `utils/pipeline_alert_tags.py` and `08-troubleshooting/`.

## Notable modules

- `scheduler/pipeline.py` — full run after an `ingestion_run` is created
- `scheduler/runner.py` — cron-style daily trigger
- `maintenance/catalog_renormalize.py` — re-queue `unresolvable` → normalize → aggregate → publish
- `maintenance/full_data_refresh.py` — destructive refresh for community rows (delete NO, reset, re-run)
- `publisher/rolling_aggregate.py` — 7-day UTC rolling index for publish

## Further reading

- Pipelines detail: [`../04-pipelines-and-runtime/`](../04-pipelines-and-runtime/)
- Schema: [`../03-data-and-schema/`](../03-data-and-schema/)
