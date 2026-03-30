# MyFarmAgents — Development Roadmap
**Version:** 1.3  
**Date:** 2026-03-30  
**Author:** Team 100 (Architecture)  
**Active Milestone:** M3 — Normalizer Engine (Phase B: G3 QA in progress)

> PRIMARY REFERENCE for all development decisions.
> Read this file at the start of every session.

---

## Team Map

| Team | Name | Role |
|------|------|------|
| **Team 100** | Architecture | Owns spec and decisions. No code. |
| **Team 50** | QA | Validates every deliverable against spec. Signs off on gates. |
| **Team 20** | Infrastructure | Env, DB, Alembic, models, seed data, utils. |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, aggregator, admin UI. |

---

## Milestone Flow

```
M1 ──► M2 ──► M3 ──► M4 ──► M5 ──► M6 ──► M7
DB    Collect  Norm   Agg   Admin  Auto  Go-Live
Tm20   Tm10   Tm10   Tm10   Tm10  Tm10  Tm10+20
  ↑QA   ↑QA   ↑QA   ↑QA   ↑QA   ↑QA    ↑QA
  G1    G2    G3    G4    G5    G6     G7
```

### Each milestone has three phases:

```
Phase A — Implementation  (executing team: Team 20 or Team 10)
    └─ Delivers code + unit tests
Phase B — QA Validation   (Team 50)
    └─ Runs integration/data quality/regression/E2E tests
    └─ Files QA report + PASS/FAIL/CONDITIONAL
Gate Gₙ opens            (Team 50 sign-off, Team 100 for G5, Nimrod for G7)
```

**No team advances to the next milestone until the gate is formally open.**

---

## Test Type Definitions

| Type | Who Writes | Who Runs | When |
|------|-----------|----------|------|
| **Unit** | Implementing team (10/20) | Both teams + Team 50 | Every milestone, in Phase A |
| **Integration** | Team 50 | Team 50 | Phase B — components with real DB, no mocks |
| **Data Quality** | Team 50 | Team 50 | Phase B (G2+) — DB table content correctness |
| **Regression** | Team 50 | Team 50 | Phase B (G3+) — prior layer data still intact |
| **End-to-End** | Team 50 | Team 50 | Phase B (G4+) — full pipeline run |
| **Functional/UI** | Team 50 | Team 50 | Phase B (G5) — browser-based UI flows |
| **Operational** | Team 50 | Team 50 | Phase B (G6) — cron, email, resilience |

---

## M1 — Local Foundation
**Team:** Team 20 (Infrastructure)
**Mandate:** `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md`
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md`
**Status:** ✅ COMPLETE — G1 open (Conditional Pass: seed patch P1–P3 required before G3)

### Phase A — Implementation (Team 20)
- Python project skeleton (`organic_market_agent/` package, all submodules)
- `requirements.txt` complete
- PostgreSQL 15 via Docker (`docker-compose up -d` — see `docker-compose.yml` at repo root)
- Alembic migrations: 5 revisions (001 schema, 002–005 seed data)
- All 23 tables + 2 views
- SQLAlchemy 2.x models for all tables
- Seed data: 11 units, 4 conversions, 29 products, 20 sources, initial aliases
- `organic_market_agent/utils/`: logging, config, checksum
- `organic_market_agent/db/`: session factory, engine, Alembic env
- CLI: `python -m organic_market_agent.db.check`
- `tests/test_db_health.py`

**Unit tests required (Phase A):**
- `pytest tests/test_db_health.py` → 7 tests: tables, row counts, aliases, units, no floats, TIMESTAMPTZ, CLI

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | Run `pytest tests/test_db_health.py` — all must PASS |
| Integration | Verify migration round-trip on clean DB (downgrade base → upgrade head) |
| Schema | SQL queries: all 23 tables exist, all required indexes, all CHECK constraints |
| Data Quality | Row counts: exactly 11 units, 29 products, ≥20 sources, aliases present |
| Type Safety | No `FLOAT` columns; all `*_at` columns are `TIMESTAMPTZ`; price columns `NUMERIC(12,4)` |
| Environment | Python 3.11+; PostgreSQL 15 via Docker (`docker ps` shows postgres container) |

**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md`

### Gate G1 — Acceptance Criteria
- [ ] `python -m organic_market_agent.db.check` → PASS (all 23 tables)
- [ ] `alembic upgrade head` succeeds on a clean DB
- [ ] `alembic downgrade base` + `alembic upgrade head` round-trip succeeds
- [ ] All 29 products, 20 sources, 11 units present in DB
- [ ] All price columns `NUMERIC(12,4)` — no `FLOAT` anywhere
- [ ] All `*_at` columns are `TIMESTAMPTZ`
- [ ] Python 3.11+ confirmed
- [ ] PostgreSQL 15 Docker container confirmed running (`docker ps | grep postgres`)
- [ ] `pytest tests/test_db_health.py` — all PASS
- [ ] Team 50 written sign-off

---

## M2 — Collection Layer
**Team:** Team 10 (Feature Dev)
**Dependency:** Gate G1 must be open
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md`
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md`
**Status:** ✅ COMPLETE — G2 open (Conditional: seed patch P1–P3 required before G3)

### Phase A — Implementation (Team 10)
- `CollectorEngine` + `BaseCollector` (retry, timeout, checksum dedup)
- `EasyFarmCollector`, `StandaloneHTMLCollector`, `GovtBenchmarkCollector`
- `ParserEngine` dispatcher
- `EasyFarmCatalogParser`, `SimpleProductGridParser`, `OfficialWholesaleParser`
- `IngestionRunner` CLI: `python -m organic_market_agent.scheduler.run_ingestion`
- Raw assets stored on filesystem; metadata in `raw_assets`
- `raw_extracted_items` populated

**Unit tests required (Phase A):**
- `tests/test_collectors.py` — 8+ tests (no live HTTP — all mocked)
- `tests/test_parsers.py` — 8+ tests (in-memory only)

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | Run `pytest tests/test_collectors.py tests/test_parsers.py` — all PASS |
| Integration | Live collection run: `run_ingestion --run-type manual` against ≥3 real sources |
| Data Quality | `raw_extracted_items` ≥50 rows; no NULL in `raw_product_name` AND `raw_payload_json` simultaneously |
| Dedup | Run ingestion twice for same sources; second run produces zero new `raw_assets` rows |
| Error Handling | Simulate unreachable source; verify retry count, `status='failed'`, `log_entries` row created |
| Isolation | No `normalized_observations` rows created (normalizer not yet active) |
| File System | Raw asset files exist on disk at `RAW_FILES_ROOT/{source_code}/{date}/` |

**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md`

### Gate G2 — Acceptance Criteria
- [ ] `pytest tests/test_collectors.py tests/test_parsers.py` — all PASS
- [ ] ≥3 sources collected successfully (live run)
- [ ] `raw_extracted_items` ≥50 rows
- [ ] Raw asset files present on filesystem
- [ ] Dedup verified: re-run → zero new `raw_assets`
- [ ] Failed source → retry count in `source_fetch_runs`, `log_entries` row present
- [ ] `normalized_observations` table still empty
- [ ] Team 50 written sign-off

---

## M3 — Normalizer Engine
**Team:** Team 10
**Dependency:** Gate G2 open ✅
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md`
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G3.md`
**Status:** 🟡 PHASE B — G3 QA open (Team 50 active)

### Phase A — Implementation (Team 10)
- `NormalizerEngine` — 7 stages (alias → organic flag → unit resolve → price normalize → quantity → basket → confidence)
- `alias_resolver.py`, `unit_resolver.py`, `price_resolver.py`, `confidence.py`
- All rules and aliases loaded from DB (never hardcoded)
- `normalized_observations` populated from `raw_extracted_items`
- Basic alias CRUD admin endpoint

**Unit tests required (Phase A):**
- `tests/test_normalizer.py` — 10+ tests
  - Each stage tested in isolation
  - DB-driven alias test: insert alias → verify resolution
  - Basket product test: basket items get `normalized_price_value=NULL`
  - Confidence score range test

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/test_normalizer.py` — all PASS |
| Integration | Full normalizer run on M2 data; verify `normalized_observations` populated |
| Data Quality | All `confidence_score` in [0.0, 1.0]; no NULLs in mandatory fields; `flag_status` valid values only |
| DB-Driven Test | Change an alias in DB, re-run normalizer, verify the observation's product_id changes |
| Basket Policy | All basket products: `is_basket_product=true`, `normalized_price_value IS NULL` |
| Regression | M2 tables (`raw_assets`, `raw_extracted_items`) unchanged after M3 run |
| No Float | `price_amount` and `normalized_price_value` are `NUMERIC` — verify no Python `float` assignment |

### Gate G3 — Acceptance Criteria
- [ ] `pytest tests/test_normalizer.py` — all PASS
- [ ] `normalized_observations` ≥40 valid rows
- [ ] All confidence scores in [0.0, 1.0]
- [ ] Basket products: `is_basket_product=true`, `normalized_price_value IS NULL`
- [ ] Alias change in DB → normalization changes on re-run
- [ ] M2 data tables unmodified (regression)
- [ ] Team 50 written sign-off

---

## M4 — Aggregation + Local Viewer
**Team:** Team 10
**Dependency:** Gate G3 must be open
**Mandate:** To be issued after G3 opens
**QA Mandate:** To be issued after G3 opens

### Phase A — Implementation (Team 10)
- `AggregatorEngine`: `daily_aggregates`, `weekly_snapshots`
- `QAEngine`: outlier detection, missing source alerts, duplicate detection
- `PublishEngine` (local only — no FTPS):
  - `public_report.json` to local directory
  - `public_report.html` via Jinja2
  - `manifest.json` with `staleness_level`
- Local viewer: `http.server` on `localhost:8080`

**Unit tests required (Phase A):**
- `tests/test_aggregator.py` — 8+ tests
  - Publish threshold: 2 obs from 2 distinct sources → `meets_publish_threshold=true`
  - Below threshold: 1 source → `meets_publish_threshold=false`
  - Outlier detection: price >3σ from mean → flagged
  - `weekly_snapshots` built from `daily_aggregates`
- `tests/test_publisher_local.py` — 6+ tests
  - `public_report.json` schema validation
  - `manifest.json` staleness calculation: 0d=current, 3d=warning, 8d=irrelevant
  - Below community threshold: publish aborted

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/test_aggregator.py tests/test_publisher_local.py` — all PASS |
| End-to-End | Full pipeline run: ingest → normalize → aggregate → publish to local dir |
| Data Quality | `daily_aggregates`: verify `min ≤ median ≤ max`; `sample_size = distinct_sources` count |
| Publish Threshold | Products with <2 observations or <2 distinct sources: `meets_publish_threshold=false` |
| JSON Schema | `public_report.json` passes schema validation (all required fields present, correct types) |
| Staleness | Manually set `last_published_at` to -4d; verify `manifest.json` shows `staleness_level=warning` |
| Local Viewer | `localhost:8080` loads, renders prices, shows correct units |
| Regression | M2 + M3 tables unchanged after M4 run |

### Gate G4 — Acceptance Criteria
- [ ] `pytest tests/test_aggregator.py tests/test_publisher_local.py` — all PASS
- [ ] `daily_aggregates` populated after full pipeline run
- [ ] `meets_publish_threshold=true` for ≥5 products
- [ ] `public_report.json` passes schema validation
- [ ] `localhost:8080` renders data correctly
- [ ] `manifest.json` includes correct `staleness_level`
- [ ] Products below threshold excluded from published output
- [ ] M2 + M3 tables unmodified (regression)
- [ ] Team 50 written sign-off

---

## M5 — Admin UI
**Team:** Team 10
**Dependency:** Gate G4 must be open
**Mandate:** To be issued after G4 opens
**QA Mandate:** To be issued after G4 opens

### Phase A — Implementation (Team 10)
- Flask app factory + local password authentication
- Blueprints: dashboard, sources, runs, observations, qa_flags, publish, normalizer
- All admin screens per `INTERFACE_MOCKUPS_HE.md`
- Normalizer management: full CRUD for aliases, rules, merges, flags
- Manual ingestion run trigger from UI

**Unit tests required (Phase A):**
- `tests/test_admin_routes.py` — 10+ tests (Flask test client, no browser)
  - Each blueprint returns HTTP 200
  - CRUD: create alias → verify in DB; update → verify; delete → verify
  - Auth: unauthenticated request → redirect to login
  - Manual run trigger → `ingestion_runs` row created

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/test_admin_routes.py` — all PASS |
| Functional/UI | Manual walkthrough of all 7 screens; verify data matches DB |
| CRUD | Create/edit/delete alias in UI → verify DB; run normalizer → verify change reflected |
| Auth | Unauthenticated access → redirect; wrong password → reject |
| Audit | Every admin write action creates `audit_log` row with correct actor + entity |
| Run Trigger | Manual run trigger from UI → `ingestion_runs` row created, status shown in UI |
| Regression | Full pipeline run from UI still produces correct `daily_aggregates` |

### Gate G5 — Acceptance Criteria
- [ ] `pytest tests/test_admin_routes.py` — all PASS
- [ ] All 7 blueprints functional and accessible
- [ ] Full CRUD for aliases/rules/merges/flags via UI
- [ ] Alias change in UI → normalization reflects on next run
- [ ] Manual run trigger → run executes, UI updates
- [ ] Every admin write → `audit_log` entry
- [ ] Auth: unauthenticated → redirect to login
- [ ] **Team 100 architectural review + approval** (required)
- [ ] Team 50 written sign-off

---

## M6 — Automation + Resilience
**Teams:** Team 10 (code) + Team 20 (cron setup)
**Dependency:** Gate G5 must be open
**Mandate:** To be issued after G5 opens
**QA Mandate:** To be issued after G5 opens

### Phase A — Implementation (Team 10 + Team 20)
- cron job: `0 6 * * * python -m organic_market_agent.scheduler.runner`
- Email alerting (SMTP): ingestion failure, partial run, stale data (3d + 8d)
- Full retry logic + error recovery
- `log_entries` auto-cleanup (90 days)

**Unit tests required (Phase A):**
- `tests/test_alerting.py` — 6+ tests (mock SMTP)
  - Ingestion failure → alert email constructed correctly
  - Stale data 3d → `staleness_level=warning` email triggered
  - Stale data 8d → `staleness_level=irrelevant` email triggered
  - Successful run → no alert sent
- `tests/test_scheduler.py` — 4+ tests
  - Runner handles partial failure gracefully (some sources succeed, some fail)
  - `ingestion_runs.status='partial'` on mixed results

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/test_alerting.py tests/test_scheduler.py` — all PASS |
| Operational | cron entry visible in `crontab -l`; runs automatically at 06:00 |
| Resilience | Simulate 1 failed source: partial run completes, alert sent, other sources unaffected |
| Alert | Mock SMTP or real test inbox: verify failure email delivered with correct content |
| Staleness Alert | Set `last_published_at = now() - interval '3 days'`; verify warning email sent |
| 7-Day Stability | Observe 7 consecutive automatic runs without manual intervention |
| Cleanup | After 90-day-old synthetic `log_entries` inserted: verify cleanup removes them |

### Gate G6 — Acceptance Criteria
- [ ] `pytest tests/test_alerting.py tests/test_scheduler.py` — all PASS
- [ ] cron job configured and running (verified via `crontab -l`)
- [ ] 7 consecutive automatic runs without intervention
- [ ] Alert sent on ingestion failure (evidence: email received)
- [ ] Staleness warning at 3 days; irrelevant at 8 days
- [ ] ≥2 retries before `status=failed`
- [ ] `log_entries` cleanup runs correctly
- [ ] Team 50 full integration sign-off

---

## M7 — Public Publishing / Go-Live
**Teams:** Team 10 + Team 20
**Dependency:** Gate G6 must be open + **Nimrod explicit approval**
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md`
**QA Mandate:** To be issued after G6 opens + Nimrod approval

### Phase A — Implementation (Team 10 + Team 20)
- uPress validation (Tests U01–U12 from mandate)
- `PublishEngine`: FTPS upload + atomic manifest update
- `manifest_last_good.json` fallback
- WordPress rendering integration
- Stale data banners (3d warning, 8d irrelevant)

**Unit tests required (Phase A):**
- `tests/upress_validation/` — U01–U12 as defined in MANDATE_UPRESS_VALIDATION.md

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/upress_validation/` — all PASS |
| Integration | FTPS connection to uPress server: authenticate, upload test file, verify accessible |
| End-to-End | Full automated pipeline: ingest → normalize → aggregate → publish → verify public URL |
| Fallback | Simulate failed upload; verify `manifest_last_good.json` serves stale data |
| WordPress | Verify WordPress page renders data from FTPS-uploaded JSON |
| Stale Banners | Set dates -4d and -9d; verify correct banners displayed on public page |
| Operational | Automated publish runs 3 consecutive days without intervention |

### Gate G7 — Acceptance Criteria
- [ ] `pytest tests/upress_validation/` — all PASS (U01–U12)
- [ ] FTPS upload verified end-to-end (test file accessible publicly)
- [ ] Full automated publish pipeline runs successfully
- [ ] `manifest_last_good.json` fallback verified
- [ ] WordPress displays live data
- [ ] Stale banners display at correct thresholds (3d / 8d)
- [ ] 3 consecutive automated publish runs without manual action
- [ ] **Nimrod manual approval → LIVE**

---

## Gate Passage Policy

1. Executing team files a completion report in their `reports/` folder
2. **Team 50** reviews against the QA Mandate and the gate criteria above
3. Team 50 files a QA report in `_COMMUNICATION/TEAM_50/reports/` with decision: **PASS / FAIL / CONDITIONAL PASS**
4. No gate opens without Team 50 written sign-off
5. **G5 additionally requires Team 100 architectural review**
6. **G7 additionally requires Nimrod explicit approval**
7. A CONDITIONAL PASS means the next phase can begin on the listed conditions; Team 50 confirms closure

---

## QA Mandate Files

| Gate | QA Mandate |
|------|-----------|
| G1 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` |
| G2 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` |
| G3 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G3.md` |
| G4–G7 | To be issued when the preceding gate opens |

---

## Reference Documents

| Document | Location |
|----------|---------|
| Canonical Glossary | `docs/GLOSSARY.md` |
| Database Schema (23 tables) | `docs/DATABASE_SCHEMA_SPEC_HE.md` |
| Pipeline Algorithms | `docs/PIPELINE_ALGORITHMS_HE.md` |
| Normalizer Spec | `docs/NORMALIZER_SPEC_HE.md` |
| Product Catalog (29 products) | `docs/PRODUCT_CATALOG_V1.md` |
| Source Map (20 sources) | `docs/SOURCE_MAP_MASTER_HE.md` |
| Architecture Decisions | `docs/ARCHITECTURE_DECISIONS_HE.md` |
| uPress Validation Plan | `docs/UPRESS_VALIDATION_PLAN_HE.md` |

> All `_HE.md` spec documents are legacy Hebrew.
> English mandates are the authoritative implementation and QA guides.
