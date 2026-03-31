# Testing

## Framework

- **pytest** under [`../../tests/`](../../tests/)
- PostgreSQL required for many integration tests; connection from `DATABASE_URL` (see `tests/conftest.py`)

## Run

```bash
cd /path/to/SmallFarmsAgents
python3 -m pytest
python3 -m pytest tests/test_normalizer.py -q
```

## Layout (indicative)

| File / area | Focus |
|-------------|--------|
| `test_normalizer.py` | Normalizer stages and engine |
| `test_publisher_local.py` | Publish engine and rolling window |
| `test_admin_routes.py` | Flask admin HTTP surface |
| `test_scope_skip.py` | Approved scope-skip rules |
| `test_aggregator.py`, `test_price_rules.py` | Aggregation and price rules |

## CI / local DB

If PostgreSQL is unavailable, some tests **skip** rather than fail.
