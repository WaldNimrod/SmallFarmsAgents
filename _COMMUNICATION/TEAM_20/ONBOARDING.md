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
5. Read current active mandate in `_COMMUNICATION/TEAM_20/`
6. **Read the relevant spec documents** for the area you will be working on (see Spec Documents table below)

**Do NOT modify schema, models, or migrations without first reading `docs/DATABASE_SCHEMA_SPEC_HE.md`.**

---

## Canonical Templates — Mandatory

All reports and requests filed by Team 20 **must** use the canonical templates:

```
_COMMUNICATION/TEMPLATES/
  README.md             ← Read this first for usage rules
  COMPLETION_REPORT.md  ← Use when a mandate is complete
  QA_REVIEW_REQUEST.md  ← Use when requesting Team 50 to run gate QA
```

| Situation | Template to use | Where to file |
|-----------|----------------|---------------|
| Mandate complete, no gate | `COMPLETION_REPORT.md` | `_COMMUNICATION/TEAM_20/reports/` |
| Mandate complete + gate QA needed | `COMPLETION_REPORT.md` + `QA_REVIEW_REQUEST.md` | Team 20 reports + Team 50 reports |
| Blocked on an issue | `COMPLETION_REPORT.md` (partial, prefix `BLOCKED_`) | `_COMMUNICATION/TEAM_20/reports/` |
| Architecture question / deviation | Free-form report to Team 100 | `_COMMUNICATION/TEAM_100/reports/` |

**Documents not using templates are informal only and carry no binding obligation on other teams.**

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

## Spec Documents to Read Before Working

**MANDATORY: Read the relevant spec document BEFORE making any change in that area.**

| Document | Relevant For | When to Read |
|----------|-------------|-------------|
| `docs/GLOSSARY.md` | All terminology | Always — READ FIRST every session |
| `documentation/README.md` | English documentation hub — structured by topic | Always |
| `docs/DATABASE_SCHEMA_SPEC_HE.md` | 29 tables, types, constraints, indexes (legacy Hebrew) | Before ANY migration or model change |
| `docs/PRODUCT_CATALOG_V1.md` | 67 products, 11 units, aliases (original 29 + expansions) | Before changing seed data |
| `docs/SOURCE_MAP_MASTER_HE.md` | 20 sources — seed data | Before changing source data |
| `docs/ARCHITECTURE_DECISIONS_HE.md` | Python stack, PostgreSQL setup | Before any structural change |
| `docs/DETAILED_SYSTEM_SPEC_HE.md` | Project structure (`organic_market_agent/`) | Before adding new modules |

**By area (for ad-hoc changes):**

| If you're changing... | Read first |
|-----------------------|-----------|
| Tables, columns, constraints | `docs/DATABASE_SCHEMA_SPEC_HE.md` |
| Products, units, aliases (seed data) | `docs/PRODUCT_CATALOG_V1.md` |
| Source configurations | `docs/SOURCE_MAP_MASTER_HE.md` |
| Package structure | `docs/DETAILED_SYSTEM_SPEC_HE.md` |
| Environment, Docker, config | `docs/ARCHITECTURE_DECISIONS_HE.md` |

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

## Python & Database Environment

> **PostgreSQL runs via Docker only** (Homebrew removed 2026-03-30).
> See `docker-compose.yml` at repo root.

```bash
# Start PostgreSQL container (fresh install)
docker-compose up -d

# OR verify existing oma-g2-ev container is running (current dev DB):
docker ps | grep postgres

# Verify Python version
python3 --version  # must be >= 3.11

# Create and activate venv
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Copy and configure .env
cp .env.example .env
# Edit .env — set DATABASE_URL to your Docker container's port

# Verify DB connection
python -m organic_market_agent.db.check
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
2. **Read the spec before changing schema** — `docs/DATABASE_SCHEMA_SPEC_HE.md` for every migration
3. **Migrations are code** — every migration tested both `upgrade` and `downgrade`
4. **Seed data is tested** — every seed verified in `tests/test_db_health.py`
5. **Don't write feature code** — only infrastructure and skeleton
6. **Report blockers immediately** — if PostgreSQL is unavailable, file a report with `[USER ACTION REQUIRED]`
7. **English only** — all reports, comments, and code in English
8. **Log every code change in `CHANGELOG.md`** — under the `[Unreleased]` section, before the session ends
9. **Spec before schema** — understand the design intent from spec docs, not just the current implementation
