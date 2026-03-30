# Team 20 → Team 100 — M1 Mandate Update (Architect Delta) & Implementation Status

**Date:** 2026-03-30  
**From:** Team 20 (Infrastructure)  
**To:** Team 100 (Architecture)  
**Subject:** Alignment with revised English M1 mandate (`MANDATE_M1_INFRASTRUCTURE.md`) after in-flight architectural rename to **OrganicMarketAgent**

---

## Summary

Team 20 reviewed the updated M1 mandate (package rename `smallfarms` → `organic_market_agent`, PyPI name `organic-market-agent`, logging namespace, CLI entrypoint, `tests/upress_validation/`, and test naming). The codebase was **refactored to match** the new mandate. PostgreSQL schema, seeds, and Gate G1 tests remain **PASS** after verification on a clean PostgreSQL 15 instance.

---

## Mandate changes vs prior implementation (delta)

| Area | Previous (pre-update) | Per revised mandate | Team 20 action |
|------|------------------------|---------------------|----------------|
| Python package | `smallfarms/` | `organic_market_agent/` | Renamed directory; all imports updated. |
| Distribution name | `smallfarms` | `organic-market-agent` | `pyproject.toml` `[project]` updated; `setuptools.packages.find` → `organic_market_agent*`. |
| Build backend | `setuptools.build_meta` | `setuptools.backends.legacy:build` | Switched to mandate value. |
| Project description | (none) | Mandated `description` | Added. |
| Logger namespace | `smallfarms.*` | `organic_market_agent.*` | Updated in `logging_setup.py`. |
| Default `RAW_FILES_ROOT` | `/tmp/smallfarms_raw` | `/tmp/organic_market_agent_raw` | Updated in `config.py`. |
| DB health CLI | `python -m smallfarms.db.check` | `python -m organic_market_agent.db.check` | Docstrings + banner text aligned; output format aligned with mandate (OK / MISSING / RESULT). |
| Alembic `script_location` | `smallfarms/db` | `organic_market_agent/db` | `alembic.ini` updated. |
| Tests layout | `tests/` only | `tests/upress_validation/` required | Added `tests/upress_validation/__init__.py`. |
| Gate tests | `test_all_products_have_active_unit`, broader timestamptz filter | `test_all_products_have_valid_unit`, `test_all_timestamp_columns_are_timestamptz` with `%_at` only | Renamed and aligned SQL with mandate. |
| `requirements.txt` | Custom note, plain `sqlalchemy` | Mandate-style sections; mandate lists `sqlalchemy[postgresql]` | Kept explicit `psycopg2-binary` **plus** plain `sqlalchemy` to avoid source build of `psycopg2` on hosts without `pg_config` (see note below). |

---

## Intentional deviations from mandate text (recommendation for Team 100)

1. **`organic_market_agent/db/env.py` — `.env` path**  
   Mandate snippet uses `Path(__file__).resolve().parents[3] / ".env"`. For a file at `…/organic_market_agent/db/env.py`, the project root is **`parents[2]`**, not `parents[3]`. Team 20 **keeps `parents[2]`** so `.env` loads correctly.

2. **`run_migrations_online` — SQLAlchemy URL**  
   Mandate shows `engine_from_config` without injecting `sqlalchemy.url` into the section dict. Alembic often receives an empty `[alembic]` section for DB URL. Team 20 **retains** the line that sets `section["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")` so online migrations work reliably.

3. **`organic_market_agent/db/__init__.py` — lazy exports**  
   Mandate shows eager `from …session import get_session, engine`. That forces `DATABASE_URL` at import of `organic_market_agent.db`. Team 20 **retains lazy `__getattr__`** for `engine` and `get_session` so `import organic_market_agent.models` (and Alembic model loading) work without a DB URL in environments that only need metadata.

4. **`sqlalchemy[postgresql]` vs `psycopg2-binary`**  
   The `[postgresql]` extra typically pulls **psycopg2 (source)**. On macOS/Xcode Python without PostgreSQL dev headers, installs fail. Team 20 documents this in `requirements.txt` and keeps **`psycopg2-binary`** alongside `sqlalchemy`. If Team 100 wants strict parity with the mandate line, we can switch once all developer machines/CI use a documented driver strategy.

5. **`models/__init__.py` in mandate**  
   The mandate’s import list omits **`ProductVariant`** and **`WeeklySnapshot`** even though the schema and migration plan include those tables. Team 20 **keeps** those models registered in `models/__init__.py` so `Base.metadata` and Alembic remain complete. Suggest updating the mandate snippet for consistency.

---

## Verification (post-refactor)

Executed on a disposable PostgreSQL 15 container:

- `alembic upgrade head` — OK (revisions `001`–`005`).
- `python -m organic_market_agent.db.check` — **PASS**.
- `pytest tests/test_db_health.py -v` — **7 passed**.

Sample health check banner:

```
OrganicMarketAgent — DB Health Check
==================================================
  OK  measurement_units
  …
RESULT: PASS
```

---

## Request to Team 100

1. Confirm acceptance of the **package rename** as the canonical Python import path for M1 onward.  
2. Amend the mandate’s **`env.py` `parents[3]`** snippet to **`parents[2]`** (or equivalent path logic) to avoid copy-paste failures.  
3. Decide official policy on **`sqlalchemy[postgresql]`** vs **`psycopg2-binary`** for local/CI installs.  
4. Refresh **`models/__init__.py`** in the mandate to include **ProductVariant** and **WeeklySnapshot** (and **ObservationFlag** if omitted elsewhere).

Team 50 QA against `docs/DATABASE_SCHEMA_SPEC_HE.md` and Gate G1 remains the next formal step per roadmap.

---

## Artifacts touched (high level)

- Renamed: `smallfarms/` → `organic_market_agent/`
- Updated: `alembic.ini`, `pyproject.toml`, `requirements.txt`, `organic_market_agent/**/*.py`, `tests/test_db_health.py`
- Added: `tests/upress_validation/__init__.py`

Canonical specs under `docs/` still use historical names such as `smallfarms_local` and `smallfarms_app` for the database — unchanged (DB naming was not part of the Python package rename).
