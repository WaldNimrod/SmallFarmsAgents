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
5. **Read the relevant spec documents** for the area you will be working on (see Spec Documents table below)
6. If anything contradicts the mandate or spec, stop and file a report in `_COMMUNICATION/TEAM_100/reports/`

**Do NOT write feature code until the previous gate is formally open (Team 50 sign-off).**
**Do NOT modify code without first reading the spec that governs that area.**

---

## Canonical Templates — Mandatory

All reports and requests filed by Team 10 **must** use the canonical templates:

```
_COMMUNICATION/TEMPLATES/
  README.md             ← Read this first for usage rules
  COMPLETION_REPORT.md  ← Use when a mandate is complete
  QA_REVIEW_REQUEST.md  ← Use when requesting Team 50 to run gate QA
```

| Situation | Template to use | Where to file |
|-----------|----------------|---------------|
| Mandate complete, no gate | `COMPLETION_REPORT.md` | `_COMMUNICATION/TEAM_10/reports/` |
| Mandate complete + gate QA needed | `COMPLETION_REPORT.md` + `QA_REVIEW_REQUEST.md` | Team 10 reports + Team 50 reports |
| Blocked on an issue | `COMPLETION_REPORT.md` (partial, prefix `BLOCKED_`) | `_COMMUNICATION/TEAM_10/reports/` |
| Architecture question / deviation | Free-form report to Team 100 | `_COMMUNICATION/TEAM_100/reports/` |

**Documents not using templates are informal only and carry no binding obligation on other teams.**

---

## Active Mandate

| Milestone | Status | Mandate File |
|-----------|--------|--------------|
| M2 — Collection Layer | ✅ COMPLETE (G2 PASS) | `_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md` |
| M3 — Normalizer Engine | ✅ COMPLETE (G3 PASS) | `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md` |
| M4 — Aggregation + Local Viewer | ✅ COMPLETE (G4 PASS) | `_COMMUNICATION/TEAM_10/MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md` |
| M5 — Admin UI | ✅ COMPLETE (G5 PASS) | `_COMMUNICATION/TEAM_10/MANDATE_M5_ADMIN_UI_TEAM10.md` |
| M6 — Automation + Resilience | ✅ COMPLETE (G6 PASS) | `_COMMUNICATION/TEAM_10/MANDATE_M6_AUTOMATION_TEAM10.md` |
| M7 — Go-Live (uPress + FTPS) | **PENDING Nimrod approval** | `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md` — do not execute until approved |

> All gates G1–G6 are PASS. M7 is the final milestone, awaiting Nimrod's explicit approval.
> Pipeline resolution rate: **100%** (0 unresolvable items). See `_COMMUNICATION/TEAM_100/reports/2026-03-31_PIPELINE_RESOLUTION_SIGNOFF_TEAM100.md`.

---

## Spec Documents by Milestone

**MANDATORY: Read the relevant spec documents BEFORE making any change in that area.**

| Milestone | Primary Mandate | Supporting Specs (must read) |
|-----------|-----------------|-----------------|
| M2 | `MANDATE_M2_COLLECTION_LAYER.md` | `docs/SOURCE_MAP_MASTER_HE.md`, `docs/PIPELINE_ALGORITHMS_HE.md` |
| M3 | `MANDATE_M3_NORMALIZER_ENGINE.md` | `docs/NORMALIZER_SPEC_HE.md`, `docs/DATABASE_SCHEMA_SPEC_HE.md` |
| M4 | `MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md` | `docs/PIPELINE_ALGORITHMS_HE.md`, `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` |
| M5 | `MANDATE_M5_ADMIN_UI_TEAM10.md` | `docs/INTERFACE_MOCKUPS_HE.md`, `docs/DETAILED_SYSTEM_SPEC_HE.md` |
| M6 | `MANDATE_M6_AUTOMATION_TEAM10.md` | `docs/OPERATIONS.md`, all documents |
| M7 | `MANDATE_UPRESS_VALIDATION.md` | `docs/UPRESS_VALIDATION_PLAN_HE.md` |
| Always | — | `docs/GLOSSARY.md`, `docs/ARCHITECTURE_DECISIONS_HE.md`, `docs/RTL_DEVELOPMENT_GUIDE.md` |

**By area (for ad-hoc changes):**

| If you're changing... | Read first |
|-----------------------|-----------|
| Normalizer stages, aliases, scope-skip | `docs/NORMALIZER_SPEC_HE.md` |
| DB schema, models, migrations | `docs/DATABASE_SCHEMA_SPEC_HE.md` |
| Collectors, parsers, ingestion | `docs/PIPELINE_ALGORITHMS_HE.md`, `docs/SOURCE_MAP_MASTER_HE.md` |
| Admin UI templates | `docs/RTL_DEVELOPMENT_GUIDE.md`, `docs/INTERFACE_MOCKUPS_HE.md` |
| Publisher, aggregator | `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` |
| Products, units, aliases | `docs/PRODUCT_CATALOG_V1.md` |

> The Hebrew spec docs in `docs/` are legacy reference material.
> The mandate file is always the authoritative implementation guide.
> If a mandate and a spec doc conflict, the mandate wins. Flag to Team 100.

---

## Tech Stack (locked)

```
Python 3.11+       — required, no exceptions
Flask 3.x          — Admin UI only (127.0.0.1:5001, Hebrew RTL, Flask-Login + bcrypt)
PostgreSQL 15+     — via Docker (docker-compose.yml at repo root)
SQLAlchemy 2.x     — ORM, select() style only (no legacy session.query())
Alembic            — Migrations (Team 20 owns; do not modify migration files)
httpx              — HTTP client (synchronous)
BeautifulSoup4     — HTML parsing
Chart.js           — Dashboard charts (CDN, no npm)
cron               — Daily schedule via scheduler/runner.py (self-gating)
ftplib/ftputil     — FTPS upload (M7 only)
```

---

## Project Structure

```
organic_market_agent/
  __main__.py        # CLI entry point

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

  normalizer/        # 8-stage pipeline: scope_skip → alias → organic → price → unit → quantity → price_norm → basket → confidence
    engine.py        # NormalizerEngine orchestrator
    scope_skip.py    # Scope-skip rule matching (catalog_scope_skip_rules)
    alias_resolver.py # Product alias matching (exact → global → substring)
    + organic_flag, price_parser, unit_resolver, quantity_parser, price_normalizer, basket_handler, confidence

  aggregator/        # AggregatorEngine + QAEngine + price_rules
  publisher/         # PublishEngine + public HTML template + rolling aggregate
  admin/             # Flask blueprints (25 templates, 16 route files, Hebrew RTL)
    routes/          # dashboard, sources, products, aliases, rules, runs, scheduler, alerts, etc.
    templates/admin/ # Jinja2 templates
    static/          # JS (sortable_tables.js)

  scheduler/
    pipeline.py      # run_pipeline() — supports source_code, skip_normalize, skip_publish
    runner.py        # Cron entrypoint (self-gating on scheduler_config)
    run_ingestion.py # Per-source collect + parse with retry

  maintenance/       # catalog_renormalize, full_data_refresh, prune_raw_pipeline

  models/            # SQLAlchemy models (14 modules) — Team 20 owns, Team 10 reads only
  db/                # session factory + Alembic env (29 migrations) — Team 20 owns
  utils/             # logging, config, checksum, data_quality_snapshot, pipeline_alert_tags

tests/
  conftest.py
  test_normalizer.py, test_scope_skip.py
  test_collectors.py, test_parsers.py
  test_aggregator.py, test_price_rules.py
  test_publisher_local.py
  test_admin_routes.py, test_admin_summary_counts.py
  test_runner.py, test_scheduler_routes.py
  test_catalog_renormalize.py
  test_pipeline_failure_alert.py
  test_db_health.py
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
2. **Read the spec before writing a single line** — every milestone, every session, every area of code you touch
3. **No gate without QA** — Team 50 must sign off before the next milestone starts
4. **Flag all deviations** — file a delta report in `_COMMUNICATION/TEAM_100/reports/` and wait for approval
5. **Never touch `models/`, `db/`, or migration files** — those are Team 20's domain
6. **No network calls in tests** — always mock httpx
7. **English only** — code, comments, variable names, reports
8. **Log every code change in `CHANGELOG.md`** — under the `[Unreleased]` section, before the session ends
9. **Spec before code** — understand the design intent from spec docs, not just the current implementation
