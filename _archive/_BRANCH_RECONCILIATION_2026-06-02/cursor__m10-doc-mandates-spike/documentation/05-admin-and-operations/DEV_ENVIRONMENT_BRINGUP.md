# Development environment bring-up (canonical)

This checklist aligns with **AOS Standard 11.2** and [`documentation/08-troubleshooting/DOCKER_SHARED_WORKSTATION.md`](../../08-troubleshooting/DOCKER_SHARED_WORKSTATION.md).

## Prerequisites

- **Docker Desktop** (or Docker Engine) running.
- **Python 3.11+** and project venv: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- **No port conflicts** on the SmallFarmsAgents canonical ports:

| Service | Host port |
|---------|-----------|
| PostgreSQL | **5433** |
| Admin (Flask) | **5001** |
| Public viewer | **8081** |

If another project holds a port, stop that container or reassign it per the AOS registry (see Docker workstation doc).

## 1. Environment file

```bash
cp .env.example .env
# Edit .env — ensure DATABASE_URL matches:
# postgresql://oma:oma@127.0.0.1:5433/organic_market_agent
```

## 2. PostgreSQL (Docker)

```bash
./scripts/docker_postgres.sh start
./scripts/docker_postgres.sh wait
```

Verify: `docker ps` shows `oma-postgres` with `0.0.0.0:5433->5432/tcp`.

## 3. Migrations and DB health

```bash
export DATABASE_URL='postgresql://oma:oma@127.0.0.1:5433/organic_market_agent'
python -m alembic upgrade head   # required on empty DB — creates all tables
python -m organic_market_agent.db.check
```

Expect: `RESULT: PASS` after migrations. A **brand-new** Docker volume has no rows — `db.check` may still fail minimum row counts until seed/migrations that populate catalog data; run Team 20 baseline steps if documented for your milestone.

**Note:** `scripts/verify_dev_stack.sh` runs `alembic upgrade head` automatically before `db.check`.

## 4. Admin UI (local only)

```bash
./scripts/admin_server.sh start
# → http://127.0.0.1:5001/
```

Default login is seeded in migration 015 (`admin@local` / `admin` — see admin docs).

## 5. Public static viewer

Requires published output under `output/public/` (run publisher at least once if empty):

```bash
./scripts/viewer_server.sh start
# → http://127.0.0.1:8081/public_report.html
```

## 6. Automated verification

From repo root:

```bash
./scripts/verify_dev_stack.sh
```

Optional: start Admin + Viewer if down, then probe HTTP (use with care — starts background processes):

```bash
./scripts/verify_dev_stack.sh --start-ui
```

## Troubleshooting

- **5433 in use:** `lsof -nP -iTCP:5433 -sTCP:LISTEN` — resolve conflicting container (often another stack on the same port).
- **Container `oma-postgres` running but no host port:** recreate with `./scripts/docker_postgres.sh down` then `start` (data persists in the named volume unless removed).
- **`db.check` fails on empty DB:** apply migrations; if still failing, compare with Team 20 seed expectations.
- **`alembic upgrade head` fails part-way (e.g. FK violation in a later revision):** the DB may be left in a **non-head** state or partially applied depending on transaction boundaries. Do **not** assume a clean retry without Team 20 guidance — options: fix forward migration data prerequisites, restore from a **certified dump/snapshot** that already matches `alembic` head, or reset the Docker volume (destructive) and retry on a clean DB after any migration fixes land.

## What “all interfaces up” means

| Layer | Meaning |
|-------|---------|
| **TCP 5433** | Host can reach Postgres (`oma-postgres` publishes `5433→5432`). |
| **Schema + data** | `alembic upgrade head` completes; `db.check` **PASS** (or documented waiver for empty-catalog experiments). |
| **5001 / 8081** | Admin and viewer scripts running; HTTP returns 200/302 (not connection refused). |

`./scripts/verify_dev_stack.sh` automates the checks above; it cannot fix migration logic failures — those are code/DB issues.
