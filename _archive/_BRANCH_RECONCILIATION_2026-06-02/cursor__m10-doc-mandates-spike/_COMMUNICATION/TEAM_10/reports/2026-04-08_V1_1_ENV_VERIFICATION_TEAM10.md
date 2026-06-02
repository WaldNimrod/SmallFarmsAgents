# Environment verification — v1.1.0 (Team 10)

**Date:** 2026-04-08  
**Mandate:** MANDATE-20260408-V1-1-LOD400-EXEC  
**Reference:** Team 20 `_COMMUNICATION/TEAM_20/reports/2026-03-30_V1_1_LOD400_INFRA_COMPLETE_TEAM100.md`

## Alembic script chain (offline)

```text
alembic heads → 073 (head)
```

## Database connectivity (this session)

| Check | Result |
|-------|--------|
| `DATABASE_URL` from `.env` (localhost:55435) | **Connection refused** — no listener |
| `docker compose up -d` (`oma-postgres`, port **5433**) | Container **started** |
| `DATABASE_URL=postgresql://oma:oma@127.0.0.1:5433/organic_market_agent alembic current` | **FATAL: no pg_hba.conf entry** for host route |

## Pytest (without live DB)

| Command | Result |
|---------|--------|
| `pytest tests/test_basket_tier_resolver.py -q` | **16 passed** |
| `pytest tests/ -m "not upress" -q` | **Fails** on any test requiring DB (admin routes, `test_db_health`, etc.) when `DATABASE_URL` unreachable |

## Operator checklist (Nimrod / workstation)

Per Team 20 infra report:

```bash
alembic upgrade head
alembic current   # expect 073
python3 -m pytest tests/ -q --ignore=tests/test_upress_validation.py --ignore=tests/test_ftps_upload.py
python3 -m organic_market_agent.db.check
```

**Team 10 does not claim env-073 PASS** until the above succeeds on an operator machine with a DB at **071** or earlier, upgraded through **073**.
