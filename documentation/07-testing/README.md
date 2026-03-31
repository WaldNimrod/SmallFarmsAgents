# Testing

## Framework

- **pytest** under [`../../tests/`](../../tests/)
- PostgreSQL required for many integration tests; connection from `DATABASE_URL` (see `tests/conftest.py`)

## Run

```bash
cd /path/to/SmallFarmsAgents
python3 -m pytest tests/ -q               # full suite
python3 -m pytest tests/test_normalizer.py -q  # single module
python3 -m pytest tests/ -v               # verbose output
```

## Current status

**127 passed, 2 skipped** (as of 2026-03-31)

Skips:
- `test_qa001_outlier_high_price` — requires ≥11 active sources (waiver: G4/G5)
- Environment-dependent DB skip in some configurations

## Test files

| File | Focus | Count |
|------|-------|-------|
| `conftest.py` | Fixtures, DB session setup | — |
| `test_normalizer.py` | Normalizer stages and engine (in-memory + DB integration) | ~18 |
| `test_scope_skip.py` | Scope-skip rule matching | ~4 |
| `test_collectors.py` | Collector engine (mocked HTTP) | ~8 |
| `test_parsers.py` | Parser engine (in-memory) | ~8 |
| `test_aggregator.py` | Aggregation engine + QA engine + price rules | ~11 |
| `test_price_rules.py` | Price dispersion rules (2-source spread, multi-source σ) | ~6 |
| `test_publisher_local.py` | Publish engine and rolling window | ~6 |
| `test_admin_routes.py` | Flask admin HTTP surface (login, CRUD, routes) | ~11 |
| `test_admin_summary_counts.py` | Dashboard summary count queries | ~3 |
| `test_catalog_renormalize.py` | Catalog re-normalize maintenance flow | ~3 |
| `test_db_health.py` | DB health check (tables, types, constraints) | ~7 |
| `test_pipeline_failure_alert.py` | Pipeline failure alert generation | ~3 |
| `test_runner.py` | Cron runner (self-gating, time match, alert on outcome) | ~7 |
| `test_scheduler_routes.py` | Scheduler UI routes (toggle, cleanup, alert mark-read) | ~4 |

## CI / local DB

If PostgreSQL is unavailable, some tests **skip** rather than fail (using `OperationalError` catch in fixtures).
