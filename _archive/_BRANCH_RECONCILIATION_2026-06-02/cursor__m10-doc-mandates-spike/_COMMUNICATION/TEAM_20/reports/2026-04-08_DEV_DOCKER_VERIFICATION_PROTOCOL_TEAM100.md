# Dev PostgreSQL (Docker) + verification evidence — Team 20 → Team 100

**Date:** 2026-04-08  
**Purpose:** Lock canonical local DB ports, standardize on repo Docker Compose, and define **repeatable verification** with log artifacts for QA / Team 100.

## Canonical development database

| Item | Value |
|------|--------|
| Orchestration | `docker-compose.yml` service `postgres` |
| Container name | `oma-postgres` |
| **Host port (fixed)** | **5433** (maps to 5432 in container) |
| Database | `organic_market_agent` |
| User / password | `oma` / `oma` |
| `DATABASE_URL` | `postgresql://oma:oma@127.0.0.1:5433/organic_market_agent` |

**Scripts**

- `scripts/docker_postgres.sh` — `start`, `stop`, `down`, `restart`, `status`, `wait`  
- On **port already allocated**, the script prints diagnostics (`docker ps`, `lsof` hints).

**`.env`**

- `.env.example` now defaults to the Docker URL above.  
- If an older `.env` still points at `localhost:55435` / `organic`, either start that legacy server or **align** `DATABASE_URL` with the table above after `docker_postgres.sh start`.

## Verification bundle (evidence artifact)

```bash
cd /path/to/SmallFarmsAgents
./scripts/docker_postgres.sh start
./scripts/verify_dev_db_team100.sh
```

Produces a **timestamped log** under `artifacts/` (path echoed at run start). The bundle includes:

1. `alembic current` (before / after)  
2. `alembic upgrade head`  
3. `pytest tests/` (excluding `test_upress_validation`, `test_ftps_upload`)  
4. `python -m organic_market_agent.db.check`  
5. SQL smoke: count `sources` where `code = 'SRC_WA'`; `pg_get_constraintdef` for `chk_rei_extraction_status`

**Attach the log file** to Team 50 / Team 100 gate evidence.

## Scope note (empty vs existing DB)

Validating **072 / 073** assumes a database already migrated through **071+** (typical dev). A brand-new volume and `alembic upgrade head` from revision `001` may fail on **older** revisions that assume specific seed `sources.id` values; that is **outside** the v1.1 LOD400 072/073 delivery and should be tracked separately if fresh-install parity is required.

## Related report

- `_COMMUNICATION/TEAM_20/reports/2026-03-30_V1_1_LOD400_INFRA_COMPLETE_TEAM100.md` — migration content and ORM alignment.

---

*Team 20 (Infrastructure)*
