# ONBOARDING — Team 10 (Feature Dev)
## Session Start Instructions

---

## Team Identity

**Name:** Team 10 — Feature Development  
**Role:** Implement all OrganicMarketAgent features — collectors, parsers,
normalizer, aggregator, publisher, admin UI.  
**Reports to:** Nimrod (project lead). Architectural questions → Team 100.  
**Writes to:** `_COMMUNICATION/TEAM_10/reports/`  
**Reads from:** `_COMMUNICATION/TEAM_10/` mandates, `_COMMUNICATION/ROADMAP.md`,
`docs/GLOSSARY.md`

---

## First Actions — Every Session

1. Read this file in full
2. Read `_COMMUNICATION/ROADMAP.md` — confirm active milestone and gate status
3. Check if the gate before your milestone is signed off: `_COMMUNICATION/TEAM_50/reports/`
4. Read the mandate for the active milestone (see table below) before writing any code
5. If anything contradicts the mandate, stop and file a report in `_COMMUNICATION/TEAM_100/reports/`

**Do NOT write feature code until the previous gate is formally open (Team 50 sign-off).**

---

## Active Mandate

| Milestone | Status | Mandate File |
|-----------|--------|--------------|
| M2 — Collection Layer | **PENDING G1 open** | `_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md` |
| M3 — Normalizer Engine | Locked until G2 | To be issued after G2 |
| M4 — Aggregation + Local Viewer | Locked until G3 | To be issued after G3 |
| M5 — Admin UI | Locked until G4 | To be issued after G4 |
| M6 — Automation + Resilience | Locked until G5 | To be issued after G5 |
| M7 — Go-Live (uPress + FTPS) | **DEFERRED** | `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md` — do not execute until G6 is open |

> Team 10 begins M2 only after Gate G1 is signed off by Team 50.
> Read `_COMMUNICATION/TEAM_50/reports/` to check for the G1 sign-off report.

---

## Spec Documents by Milestone

| Milestone | Primary Mandate | Supporting Specs |
|-----------|-----------------|-----------------|
| M2 | `MANDATE_M2_COLLECTION_LAYER.md` | `docs/SOURCE_MAP_MASTER_HE.md`, `docs/PIPELINE_ALGORITHMS_HE.md` |
| M3 | *(to be issued)* | `docs/NORMALIZER_SPEC_HE.md`, `docs/DATABASE_SCHEMA_SPEC_HE.md` |
| M4 | *(to be issued)* | `docs/PIPELINE_ALGORITHMS_HE.md`, `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` |
| M5 | *(to be issued)* | `docs/INTERFACE_MOCKUPS_HE.md`, `docs/DETAILED_SYSTEM_SPEC_HE.md` |
| M6 | *(to be issued)* | All documents |
| M7 | `MANDATE_UPRESS_VALIDATION.md` | `docs/UPRESS_VALIDATION_PLAN_HE.md` |
| Always | — | `docs/GLOSSARY.md`, `docs/ARCHITECTURE_DECISIONS_HE.md` |

> The Hebrew spec docs in `docs/` are legacy reference material.
> The mandate file is always the authoritative implementation guide.
> If a mandate and a spec doc conflict, the mandate wins. Flag to Team 100.

---

## Tech Stack (locked)

```
Python 3.11+       — required, no exceptions
Flask 3.x          — Admin UI only (127.0.0.1:5000, M5+)
PostgreSQL 15+     — Direct install (no Docker)
SQLAlchemy 2.x     — ORM, select() style only (no legacy session.query())
Alembic            — Migrations (Team 20 owns; do not modify migration files)
httpx              — HTTP client (synchronous in M2; async if needed in M6+)
BeautifulSoup4     — HTML parsing
cron               — Daily schedule 06:00 (M6+)
ftplib/ftputil     — FTPS upload (M7 only)
```

---

## Project Structure

```
organic_market_agent/
  collectors/
    base.py          # BaseCollector ABC + FetchResult
    engine.py        # CollectorEngine (dispatches by platform_family/fetch_mode)
    easyfarm.py      # EasyFarmCollector
    html_page.py     # StandaloneHTMLCollector
    govt_benchmark.py

  parsers/
    base.py          # BaseParser ABC + RawItem dataclass
    engine.py        # ParserEngine (dispatches by normalizer_type)
    easyfarm_catalog.py
    simple_product_grid.py
    official_wholesale.py

  normalizer/        # NormalizerEngine (M3)
  aggregator/        # AggregatorEngine + QAEngine (M4)
  publisher/         # PublishEngine, local + FTPS (M4/M7)
  admin/             # Flask blueprints (M5)
  scheduler/
    run_ingestion.py # CLI: python -m organic_market_agent.scheduler.run_ingestion

  models/            # SQLAlchemy models — Team 20 owns, Team 10 reads only
  db/                # session factory + Alembic env — Team 20 owns
  utils/             # logging, config, checksum, exceptions — Team 20 owns
  tests/
    test_collectors.py
    test_parsers.py
    test_normalizer.py   # (M3)
    test_aggregator.py   # (M4)
    ...
```

---

## Critical Coding Rules

| Rule | Detail |
|------|--------|
| No `float` for money | Use `Decimal` in Python; `NUMERIC(12,4)` in DB |
| No hardcoded product names | All products loaded from DB — never in code |
| No hardcoded URLs | All URLs from `source_fetch_profiles.entry_url` in DB |
| No `session.query()` | SQLAlchemy 2.x: `session.execute(select(...))` |
| All timestamps timezone-aware | `datetime.now(timezone.utc)` — never naive datetime |
| Log to `log_entries` table | All errors persisted, not only printed |
| Admin actions to `audit_log` | Every admin write must produce an audit row |
| Normalizer from DB only | Rules, aliases, profiles loaded from DB — not from code |
| No region filter | Removed from V1 — do not implement |
| English only | All code, comments, docstrings, variable names, reports |
| No live HTTP in tests | Always mock httpx — no real network calls in `pytest` |
| Collector failures non-fatal | One source failure must not abort the full run |

---

## Milestone Execution Order

```
G1 open (Team 20 complete + Team 50 sign-off)
    ↓
M2: CollectorEngine + ParserEngine
    → 3 collectors, 3 parsers, raw_assets + raw_extracted_items populated
    ↓ G2 open (Team 50 sign-off)
M3: NormalizerEngine — 7 stages, DB-driven aliases + rules
    → normalized_observations populated
    ↓ G3 open
M4: AggregatorEngine + QAEngine + local viewer (localhost:8080)
    → daily_aggregates, weekly_snapshots, public_report.json + .html
    ↓ G4 open
M5: Flask admin UI — dashboard, sources, runs, normalizer CRUD
    ↓ G5 open (Team 100 architecture review required)
M6: cron scheduler + email alerting + staleness checks
    ↓ G6 open
M7: uPress FTPS publish + WordPress integration (DEFERRED)
    ↓ G7 open (Nimrod approval required)
```

---

## Report Template

```markdown
# Team 10 — [Milestone / Topic]
**Date:** YYYY-MM-DD
**Milestone:** M[N] / Gate G[N]
**Status:** COMPLETE | IN PROGRESS | BLOCKED

## Environment
- Python version: X.X.X
- PostgreSQL version: X.X (direct install)

## What Was Done

## Deliverables
(files created, key classes/functions)

## Test Results
(paste pytest -v output)

## DB Counts After Run
(table: row counts for relevant tables)

## Deviations from Mandate
(any deviation requires Team 100 approval before G[N] can open)

## Blockers / [USER ACTION REQUIRED]
(tag [USER ACTION REQUIRED] if Nimrod must act)

## Gate G[N] Request
Requesting Team 50 to review and sign off on Gate G[N].
Reference: _COMMUNICATION/TEAM_10/MANDATE_M[N]_*.md
```

---

## Golden Rules

1. **The mandate is the source of truth** — if this onboarding and the mandate conflict, the mandate wins
2. **Read the spec before writing a single line** — every milestone, every session
3. **No gate without QA** — Team 50 must sign off before the next milestone starts
4. **Flag all deviations** — file a delta report in `_COMMUNICATION/TEAM_100/reports/` and wait for approval
5. **Never touch `models/`, `db/`, or migration files** — those are Team 20's domain
6. **No network calls in tests** — always mock httpx
7. **English only** — code, comments, variable names, reports
