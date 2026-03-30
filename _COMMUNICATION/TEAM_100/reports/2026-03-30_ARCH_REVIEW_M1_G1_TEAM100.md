# Architecture Review — M1 Implementation & G1 Gate Decision
**Date:** 2026-03-30  
**From:** Team 100 (Architecture)  
**Re:** Team 20 M1 completion + delta report  
**Gate:** G1

---

## Decision: CONDITIONAL PASS

G1 may open **after** the two blocking issues below are resolved.
Non-blocking findings are accepted or acknowledged without holding the gate.

---

## Blocking Issues (must resolve before G1 is formally open)

### B1 — Python Version: 3.9.6 Used, 3.11+ Required (HIGH)

Team 20's report states the validation environment was Python 3.9.6.
The spec (`ARCHITECTURE_DECISIONS_HE.md`, `coding-standards.mdc`) locks Python 3.11+.

**Required action (Team 20):** Re-run full test suite on Python 3.11+,
confirm 7/7 PASS, and update the environment note in the report.

> Rationale: Python 3.11 introduces performance improvements, `tomllib`,
> and `ExceptionGroup` that feature teams will use from M2. Running M1
> validation on 3.9 gives false confidence.

### B2 — Docker PostgreSQL: Temporary Container Used, Direct Install Required (MEDIUM)

The spec requires PostgreSQL installed directly on the local machine (no Docker).
Docker is acceptable for CI pipelines but NOT as the primary development environment.

**Required action (Team 20):** Confirm or set up local direct PostgreSQL install.
Re-run `alembic upgrade head` and `db.check` against direct install.
Document the local `DATABASE_URL` in `.env.example` (not `.env`).

---

## Accepted Deviations (confirmed correct, mandate will be updated)

### A1 — `env.py`: `parents[2]` is correct, mandate had a typo

The mandate snippet used `parents[3]`. Team 20's correction to `parents[2]`
is the right path for `organic_market_agent/db/env.py` → project root.
**Mandate `MANDATE_M1_INFRASTRUCTURE.md` updated** to reflect `parents[2]`.

### A2 — `run_migrations_online`: URL injection retained

Injecting `sqlalchemy.url` into the section dict before `engine_from_config`
is the correct and robust pattern. Accepted.

### A3 — `db/__init__.py`: Lazy `__getattr__` pattern

Elegant solution — prevents `DATABASE_URL` requirement at model-import time.
Accepted. This is the canonical pattern going forward.

### A4 — `models/__init__.py` includes `ProductVariant` and `WeeklySnapshot`

The mandate's `__init__.py` example was incomplete. Team 20's version is
correct and complete (includes `ProductVariant`, `WeeklySnapshot`,
`ObservationFlag`). **Mandate updated.**

### A5 — `psycopg2-binary` instead of `sqlalchemy[postgresql]`

**Official policy decision:** Use `psycopg2-binary` directly.
`sqlalchemy[postgresql]` pulls psycopg2 source on macOS without pg_config.
`requirements.txt` should keep `psycopg2-binary>=2.9` and plain `sqlalchemy>=2.0`.
Remove the `[postgresql]` extra. **Mandate updated.**

---

## Non-Blocking Findings

### N1 — `sessionmaker(bind=engine)` — LOW

```python
# current (works, but old style)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)

# SQLAlchemy 2.x preferred
SessionFactory = sessionmaker(engine, expire_on_commit=False)
```

Not blocking. Team 10 should use the 2.x style in any new session factories.
Team 20 can address in a follow-up commit.

### N2 — `get_session()` return type annotation — LOW

```python
# current
@contextmanager
def get_session() -> Session:

# correct for contextmanager
from typing import Generator
@contextmanager
def get_session() -> Generator[Session, None, None]:
```

Not blocking. Address in follow-up commit.

### N3 — `downgrade()` in seed migrations uses `DELETE FROM` — ACCEPTABLE

`002_seed_units.py` `downgrade()` uses `DELETE FROM unit_conversions` and
`DELETE FROM measurement_units`. This is destructive if run on a DB with
real data. Acceptable for local development seeds — document the risk.
For production migrations, seed downgrades should be no-ops.

---

## Mandate Updates Applied (Team 100 action)

The following corrections have been made to `MANDATE_M1_INFRASTRUCTURE.md`:
- `parents[3]` → `parents[2]` in `env.py` snippet
- `models/__init__.py` updated to include `ProductVariant`, `WeeklySnapshot`
- `requirements.txt` policy clarified: `psycopg2-binary`, no `[postgresql]` extra

---

## Next Steps

1. **Team 20:** Resolve B1 (Python 3.11+) and B2 (direct PostgreSQL), re-submit
2. **Team 50:** Once B1+B2 resolved — proceed with formal G1 QA sign-off
3. **Team 10:** May begin M2 planning/reading. Do NOT write M2 code until G1 is formally open.
4. **Team 100:** Will publish M2 mandate after G1 sign-off.
