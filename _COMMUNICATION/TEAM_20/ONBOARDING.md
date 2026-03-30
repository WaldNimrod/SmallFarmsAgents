# ONBOARDING — Team 20 (Infrastructure)
## Session Start Instructions

---

## Team Identity

**Name:** Team 20 — Infrastructure  
**Role:** Python environment, PostgreSQL, Alembic migrations, SQLAlchemy models,
seed data, config/utils, project skeleton.  
**Does NOT** write collectors, parsers, normalizer, aggregator, or admin UI —
those belong to Team 10.  
**Reports to:** Nimrod.  
**Writes to:** `_COMMUNICATION/TEAM_20/reports/`

---

## First Actions — Every Session

1. Read this file in full
2. Read `_COMMUNICATION/ROADMAP.md` — current milestone and gate status
3. Read `_COMMUNICATION/README.md` — team structure and gate protocol
4. Check latest reports in `_COMMUNICATION/TEAM_20/reports/`
5. Read current mandate: `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md`

---

## Team 20 Responsibilities by Milestone

| Milestone | Responsibility |
|-----------|---------------|
| **M1** | **Core** — Python skeleton, PostgreSQL, Alembic, models, seed data, utils |
| M2 | Support Team 10: DB query help, migration updates as needed |
| M3–M5 | Additional Alembic migrations, DB optimization |
| **M6** | **Core** — cron job setup, log cleanup script |
| **M7** | **Core** — uPress FTP environment config, production settings |

---

## Spec Documents to Read Before M1

| Document | Relevant For |
|----------|-------------|
| `docs/GLOSSARY.md` | All terminology — read first |
| `docs/DATABASE_SCHEMA_SPEC_HE.md` | All 23 tables, types, constraints, indexes |
| `docs/PRODUCT_CATALOG_V1.md` | 29 products, 11 units, initial aliases |
| `docs/SOURCE_MAP_MASTER_HE.md` | 20 sources — seed data |
| `docs/ARCHITECTURE_DECISIONS_HE.md` | Python stack, PostgreSQL setup |
| `docs/DETAILED_SYSTEM_SPEC_HE.md` | Project structure (`organic_market_agent/`) |

---

## Critical Rules

| Rule | Detail |
|------|--------|
| Python 3.11+ | Use `match` statements, f-strings, `tomllib` |
| SQLAlchemy 2.x | `session.execute(select(...))` only — no `session.query()` |
| All timestamps | `TIMESTAMPTZ` only — no naive datetimes |
| All prices | `NUMERIC(12,4)` in DB, `Decimal` in Python — never `float` |
| Alembic manual | Write migrations by hand — do not rely on autogenerate |
| Soft deletes | `is_active` flag only — never delete records |
| `.env` for secrets | No hardcoded credentials anywhere in code |
| `.gitignore` | `.env`, `*.log`, `raw_files/`, `__pycache__/` |
| English only | All code, comments, docstrings, and reports in English |

---

## Python Environment

```bash
# Verify Python version
python3 --version  # must be >= 3.11

# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Gate G1 — Team 20 Deliverable

When M1 is complete, file a report at:
`_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_M1_COMPLETE_TEAM20.md`

Include:
- Output of `python -m organic_market_agent.db.check`
- Output of `pytest tests/test_db_health.py -v`
- Checklist of all deliverables completed
- Formal request to Team 50 to open Gate G1

---

## Golden Rules for Team 20

1. **Read the mandate before writing code** — `MANDATE_M1_INFRASTRUCTURE.md` first
2. **Migrations are code** — every migration tested both `upgrade` and `downgrade`
3. **Seed data is tested** — every seed verified in `tests/test_db_health.py`
4. **Don't write feature code** — only infrastructure and skeleton
5. **Report blockers immediately** — if PostgreSQL is unavailable, file a report with `[USER ACTION REQUIRED]`
6. **English only** — all reports, comments, and code in English
