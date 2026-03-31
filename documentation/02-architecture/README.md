# Architecture

## Layering

| Layer | Responsibility | Primary package paths |
|-------|------------------|------------------------|
| Collect | Fetch raw HTTP assets | `scheduler/run_ingestion.py`, `collectors/` (per source type) |
| Parse | Raw asset → `raw_extracted_items` | `parsers/` |
| Normalize | 8-stage pipeline → `normalized_observations` | `normalizer/` |
| Aggregate | Daily / weekly rollups + price rules | `aggregator/` |
| Publish | Rolling window public index + manifest | `publisher/` |
| Admin | Local monitoring, CRUD, triggers | `admin/` (Flask, Hebrew RTL) |
| Scheduler | Cron-based automation + alerts | `scheduler/` |
| Maintenance | Re-normalize, full refresh, pruning | `maintenance/` |

## Normalizer pipeline (8 stages)

Stages run in order (see `normalizer/engine.py`):

1. **scope_skip** — `catalog_scope_skip_rules` match → `ignored` (301 active rules)
2. **alias_resolver** — exact → global → substring match against `product_aliases` (232 active)
3. **organic_flag** — detect organic markers
4. **price_parser** — extract numeric price from raw text
5. **unit_resolver** — resolve measurement units from rules + product defaults
6. **quantity_parser** — extract quantity values
7. **price_normalizer** — normalize to canonical unit price
8. **basket_handler** — basket/CSA product handling
9. **confidence** — compute confidence score [0.0, 1.0]

**Blocking stages:** `alias_resolver` and `price_parser` — if these fail, the item becomes `unresolvable`. After all stages, if `product_id`, `price_amount`, or `display_unit_id` is NULL, the item is also `unresolvable`.

## Key design choices

- **Normalizer rules and aliases are data-driven** (PostgreSQL); change without redeploy where possible.
- **Scope-skip runs first** to filter non-food/out-of-scope items before alias matching.
- **WordPress reads static files only** — no live DB connection from the public site.
- **Pipeline alerts** use stable message prefixes (`[OPS:…]`, `[PIPELINE:…]`, `[SIMULATION:test]`, etc.) — see `utils/pipeline_alert_tags.py` and `08-troubleshooting/`.
- **Price dispersion rules** suppress publish when 2-source spread >100% or 3+-source outlier >2σ.

## Notable modules

| Module | Purpose |
|--------|---------|
| `scheduler/pipeline.py` | Full run after an `ingestion_run` is created (supports `source_code`, `skip_normalize`, `skip_publish`) |
| `scheduler/runner.py` | Cron-style daily trigger (self-gates on `scheduler_config`) |
| `scheduler/run_ingestion.py` | Per-source collect + parse with retry logic |
| `maintenance/catalog_renormalize.py` | Re-queue `unresolvable` → normalize → aggregate → publish |
| `maintenance/full_data_refresh.py` | Community full refresh (does NOT reset approved `ignored` rows) |
| `maintenance/prune_raw_pipeline.py` | Prune old pipeline data |
| `publisher/rolling_aggregate.py` | 7-day UTC rolling index for publish |
| `publisher/engine.py` | Build public_report JSON/HTML + manifest |
| `aggregator/price_rules.py` | Price dispersion rules (2-source spread, multi-source σ) |
| `aggregator/qa_engine.py` | QA checks: outliers, missing sources, duplicates |
| `utils/data_quality_snapshot.py` | Single source of truth for pipeline counts (admin dashboard, publish, manifest) |

## Package structure

```
organic_market_agent/
├── __main__.py          # CLI entry point
├── admin/               # Flask admin UI (25 templates, 16 route files)
│   ├── routes/          # Blueprint route modules
│   ├── templates/admin/ # Jinja2 templates (Hebrew RTL)
│   └── static/          # JS (sortable_tables.js)
├── aggregator/          # Daily/weekly rollups + QA + price rules
├── collectors/          # HTTP fetch per source type
├── db/                  # Session, engine, Alembic env, health check
│   └── versions/        # 29 Alembic migrations
├── maintenance/         # Catalog renormalize, full refresh, prune
├── models/              # SQLAlchemy ORM models (14 modules)
├── normalizer/          # 8-stage pipeline + engine
├── parsers/             # Raw asset → extracted items
├── publisher/           # Publish engine + HTML template
├── scheduler/           # Pipeline orchestration + cron runner
└── utils/               # Config, logging, checksum, alerts, data quality
```

## Further reading

- Pipelines detail: [`../04-pipelines-and-runtime/`](../04-pipelines-and-runtime/)
- Schema: [`../03-data-and-schema/`](../03-data-and-schema/)
- Admin UI: [`../05-admin-and-operations/`](../05-admin-and-operations/)
