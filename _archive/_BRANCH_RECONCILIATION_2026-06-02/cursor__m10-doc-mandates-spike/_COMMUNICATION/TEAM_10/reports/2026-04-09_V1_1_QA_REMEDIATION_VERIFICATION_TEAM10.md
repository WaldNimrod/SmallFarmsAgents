# G-V1.1 QA remediation — verification log (Team 10)

**Date:** 2026-04-09  
**Related:** Gate QA-RPT-20260405-G-V1.1; [`CHANGELOG.md`](../../../CHANGELOG.md) Team 10 entry 2026-04-09

## Automated tests (this workspace)

| Command | Result | Notes |
|---------|--------|--------|
| `pytest tests/ -m "not upress" -q` | **125 passed**, 75 skipped, 12 deselected | PostgreSQL not running locally — `test_db_health` module skipped; integration tests using `db_session` / `require_postgres` skipped as expected |
| `pytest tests/test_basket_tier_resolver.py -v` | **16 passed** | T11 unit coverage unchanged |

Interpreter during run: system `.venv` reported **Python 3.9.6**. Project policy is **3.11+** — recreate the venv with `python3.11` and align with repo [`.python-version`](../../../.python-version).

## Certified QA preconditions (Team 50 re-run)

When PostgreSQL is up, migration **073** applied, and `DATABASE_URL` points at the instance:

1. `python -m organic_market_agent db.check` — expect success  
2. `alembic current` — expect head **073**  
3. `pytest tests/ -m "not upress"` — expect **no skips** for `test_db_health` (unless policy allows partial); `test_t14` runs with live DB  
4. Full mandate T01–T16 per [`QA_MANDATE_G_V1_1.md`](../../TEAM_50/QA_MANDATE_G_V1_1.md)

Team 50: use [`_COMMUNICATION/TEAM_50/reports/2026-04-09_V1_1_QA_REREVIEW_REQUEST_TEAM10.md`](../TEAM_50/reports/2026-04-09_V1_1_QA_REREVIEW_REQUEST_TEAM10.md) when preconditions are met.
