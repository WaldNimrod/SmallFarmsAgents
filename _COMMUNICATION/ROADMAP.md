# MyFarmAgents — Development Roadmap
**Version:** 3.0  
**Date:** 2026-04-02  
**Author:** Team 100 (Architecture)  
**Active Milestone:** M9 — Site Optimization and Maintenance (COMPLETE)

> PRIMARY REFERENCE for all development decisions.
> Read this file at the start of every session.

---

## Team Map

| Team | Name | Role |
|------|------|------|
| **Team 100** | Architecture | Owns spec and decisions. No code. |
| **Team 80** | Product & Strategy | Research, product dev, copy, marketing. OpenAI online. |
| **Team 50** | QA | Validates every deliverable against spec. Signs off on gates. |
| **Team 20** | Infrastructure | Env, DB, Alembic, models, seed data, utils. |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, aggregator, admin UI. |

---

## Milestone Flow

```
M1 ──► M2 ──► M3 ──► M4 ──► M5 ──► M6 ──► M7 ──► M8 ──► M9 ──► M10
DB    Collect  Norm   Agg   Admin  Auto  Live   UX   Content  Spec
Tm20   Tm10   Tm10   Tm10   Tm10  Tm10  Tm100 Tm10  Tm80    Tm100
  ↑QA   ↑QA   ↑QA   ↑QA   ↑QA   ↑QA   ↑QA  ↑QA   ↑Nimrod  (plan)
  G1    G2    G3    G4    G5    G6    G7   G8    G9     —
```

### Each milestone has three phases:

```
Phase A — Implementation  (executing team: Team 20 or Team 10)
    └─ Delivers code + unit tests
    └─ Logs ALL changes in CHANGELOG.md under [Unreleased]
Phase B — QA Validation   (Team 50)
    └─ Runs integration/data quality/regression/E2E tests
    └─ Verifies CHANGELOG.md is complete for the milestone
    └─ Files QA report + PASS/FAIL/CONDITIONAL
Gate Gₙ opens            (Team 50 sign-off, Team 100 for G5, Nimrod for G7)
Phase C — Documentation   (Team 100 + implementing team)
    └─ Move [Unreleased] entries in CHANGELOG.md to versioned section
    └─ Bump version in relevant docs
    └─ Update documentation/ hub to reflect changes
```

**No team advances to the next milestone until the gate is formally open.**
**Documentation update (Phase C) must be completed before next milestone starts.**

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
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G3_v2.md` (v2 — cohort-scoped)
**Status:** ✅ COMPLETE — G3 PASS (binding doc: `QA_MANDATE_G3_RERUN.md`; forward: `QA_MANDATE_G3_v2.md`)

**Data Quality Outputs (issued at G3 closure):**
- `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` — phased lifecycle spec
- `_COMMUNICATION/TEAM_100/reports/2026-03-30_ARCH_DECISION_G3_DATA_QUALITY_TEAM100.md` — gate decision record

**Pending mandates (M3→M4 boundary, required before G4 QA):**
- Team 20: `MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md` — add `source_tier` + `is_quarantined`
- Team 10: `MANDATE_NORMALIZER_FILTER_AND_METRICS_TEAM10.md` — skip quarantined rows + `--metrics` flag

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
- [x] `pytest tests/test_normalizer.py` — all PASS (46/46)
- [x] `normalized_observations` > 0 (7 rows from valid price-grid sources after guard fix)
- [x] All confidence scores in [0.0, 1.0]
- [x] Basket products: `is_basket_product=true`, `normalized_price_value IS NULL`
- [x] Alias change in DB → normalization changes on re-run
- [x] M2 data tables unmodified (regression)
- [x] `unresolvable_reason` column is TEXT (migration 008)
- [x] Team 50 written sign-off (binding: `QA_MANDATE_G3_RERUN.md`)

> **Note:** `≥ 40` threshold retired. Replaced by cohort-scoped `resolved ≥ 10` in `QA_MANDATE_G3_v2.md`.
> The 1,634 unresolvable rows are pre-guard M2 extractions from discovery sources — not a normalizer
> defect. These rows will be quarantined by migration 009 (M3→M4 boundary mandate).

---

## M4 — Aggregation + Local Viewer + Admin Dashboard
**Team:** Team 10 (+ Team 20 for migration 014)
**Dependency:** Gate G3 ✅ PASS + all M3→M4 boundary work ✅ COMPLETE
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md` ✅ ISSUED
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md` ✅ ISSUED
**Schema Mandate:** `_COMMUNICATION/TEAM_20/MANDATE_M4_SCHEMA_TEAM20.md` ✅ ISSUED
**Status:** ✅ COMPLETE — G4 PASS (sign-off: `ARCH-20260331-G4-PASS`)

**M3→M4 Boundary Work (all ✅ COMPLETE as of 2026-03-30):**
- Migration 010: EasyFarm selector fix, SRC007 deactivated, noise sources off
- Migration 011: 6 core-vegetable aliases added (גזר, מלפפון, חציל, חסה, פלפל אדום, רוקט)
- Migration 012: SRC003 (.box_card) selector fixed, 3 basket aliases added
- Migration 013: `source_tier` on `sources`, `is_quarantined` on `raw_extracted_items` — all 20 sources classified, ~1,646 noise rows quarantined
- `NormalizerEngine`: skips `is_quarantined=true` rows
- `run_normalizer --metrics`: forward-metrics summary implemented
- Parser engine: source tier warning log added
- Pipeline result: **22 distinct products, 3 reliable sources, 0 unprocessed items** per full run

**M4 Entry Criteria (all ✅ MET):**
1. ✅ Migration 013 applied: `source_tier` + `is_quarantined` columns exist
2. ✅ Normalizer engine skips quarantined rows
3. ✅ `run_normalizer --metrics` implemented and working
4. ✅ Cohort run: resolved ≥ 10 AND distinct_products ≥ 3 confirmed

### Phase A — Implementation (Team 10)
- `AggregatorEngine`: `daily_aggregates`, `weekly_snapshots`
- `QAEngine`: outlier detection, missing source alerts, duplicate detection
- `PublishEngine` (local only — no FTPS):
  - `public_report.json` to local directory
  - `public_report.html` via Jinja2
  - `manifest.json` with `staleness_level`
- Local viewer: `http.server` on `localhost:8080`
- **Admin Monitoring Dashboard** (new M4 deliverable):
  - Flask app at `organic_market_agent/admin/`
  - Read-only: source status, product coverage, alias gap view (`/unresolved`)
  - CLI: `python -m organic_market_agent run_admin`
  - Spec: see `MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md` Task 5

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
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M5_ADMIN_UI_TEAM10.md` ✅ ISSUED
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G5.md` ✅ ISSUED
**Schema Mandate:** `_COMMUNICATION/TEAM_20/MANDATE_M5_SCHEMA_TEAM20.md` ✅ ISSUED
**Status:** ✅ COMPLETE — G5 PASS (sign-off: `ARCH-20260331-G5-PASS-M5-COMPLETE`)

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
**Teams:** Team 10 (code) + Team 20 (cron + migration)
**Dependency:** Gate G5 ✅ PASS
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M6_AUTOMATION_TEAM10.md` ✅ ISSUED
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G6.md` ✅ ISSUED
**Schema Mandate:** `_COMMUNICATION/TEAM_20/MANDATE_M6_SCHEMA_TEAM20.md` ✅ ISSUED
**Status:** ✅ COMPLETE — G6 PASS (sign-off: `ARCH-20260331-G6-PASS-M6-COMPLETE`)

### Phase A — Implementation (Team 10 + Team 20)

**Team 20 (migration 016):**
- `scheduler_config` table — single-row settings (is_enabled, run_hour, run_minute, retry_attempts, cleanup_enabled, cleanup_after_days)
- `pipeline_alerts` table — in-app alerts (level, message, is_read, ingestion_run_id FK)
- Seed: one row in `scheduler_config` with defaults (enabled, 06:00, retry=2, cleanup=90d)

**Team 10 (features):**
- `scheduler/runner.py` — cron entrypoint: reads `scheduler_config`, self-gates on is_enabled + hour/minute, calls `run_pipeline()`, writes alert on failure/partial
- `run_pipeline()` extended: optional `source_code`, `skip_normalize`, `skip_publish` parameters for focused runs
- `/runs/trigger` form extended with source_code, skip_normalize, skip_publish options; polling for live status
- New blueprint `/scheduler` — schedule enable/disable/edit, cleanup trigger with row-count feedback
- New blueprint `/alerts` — mark-read endpoint
- Dashboard charts (Chart.js CDN): 14-day resolution rate line chart + source success/fail stacked bar
- Alert badge in nav + unread alerts panel on dashboard
- Log cleanup: deletes `source_fetch_runs` (+ cascade) older than `cleanup_after_days`
- Cron line: `* * * * * cd /path/to/repo && python -m organic_market_agent.scheduler.runner`
  (runs every minute; runner self-gates on configured hour/minute)

**Unit tests required (Phase A):**
- `tests/test_runner.py` — 4+ tests: gates on is_enabled=false, gates on wrong hour, executes at correct hour, partial run writes warning alert
- `tests/test_scheduler_routes.py` — 4+ tests: GET /scheduler 200, POST toggle, POST cleanup (mock), alert mark-read
- `tests/test_admin_routes.py` extended: focused trigger with source_code parameter

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/` — 0 failures |
| Scheduler UI | GET /scheduler 200; toggle enable/disable; edit hour/minute saves to DB |
| Focused trigger | POST /runs/trigger with source_code → only that source in run |
| Alert badge | Partial/failed run → unread alert appears in dashboard nav |
| Dashboard charts | Two Chart.js canvases render with real data |
| Cleanup | POST /scheduler/run-cleanup returns row-count flash; DB rows removed |
| Retry | retry_attempts=2 config verified in DB; runner respects setting |
| Regression | All G5 baselines (sources=20, products=29, aliases≥97) still met |

### Gate G6 — Acceptance Criteria
- [ ] `pytest tests/` — 0 failures
- [ ] `/scheduler` page: enable/disable + time edit functional, changes persist to DB
- [ ] Manual cleanup trigger returns row-count confirmation
- [ ] Dashboard shows 2 Chart.js graphs with real data
- [ ] Alert badge appears on dashboard after a partial/failed run
- [ ] Focused trigger (`source_code`) creates run scoped to that source only
- [ ] Retry logic: `retry_attempts` column confirmed in `scheduler_config`; runner reads it
- [ ] Cron line installed and visible in `crontab -l`
- [ ] All G5 regression baselines met
- [ ] Team 50 written sign-off
- [ ] **Team 100 architectural review + approval** (required)

---

## M7 — Public Publishing / Go-Live
**Teams:** Team 100 (implementation), Team 10 + Team 20 (review)
**Dependency:** Gate G6 must be open + **Nimrod explicit approval**
**Nimrod Approval:** ✅ **Approved 2026-03-31** — immediate execution authorized
**Transport:** FTPS (FTP over TLS) on port 21 via `ftplib.FTP_TLS` with `ReusedSessionFTP_TLS` subclass
**Work Plan:** `_COMMUNICATION/TEAM_100/reports/2026-03-31_M7_WORK_PLAN_FOR_APPROVAL_TEAM100.md` (v2.1 — binding)
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md`
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G7.md` ✅ ISSUED

### Phase A — Implementation (Team 100) — COMPLETE
- ✅ Config: uPress FTPS properties in `Config` class, `upress_configured()` helper
- ✅ Alert tags: `TAG_FTPS_UPLOAD_SUCCESS`, `TAG_FTPS_UPLOAD_FAILURE`, `TAG_FTPS_UPLOAD_PARTIAL`
- ✅ Migration 030: `upload_enabled` boolean on `scheduler_config`
- ✅ FTPS upload module: `ftps_upload.py` with `ReusedSessionFTP_TLS`, `upload_artifacts()`, retry logic
- ✅ Body fragment template: `public_report_body.html` (scoped CSS, no `<html>` wrapper)
- ✅ PublishEngine: versioned filenames, fixed-name copies, manifest v2 schema, `manifest_last_good.json`
- ✅ Pipeline wiring: FTPS upload phase after publish, checks `upload_enabled`
- ✅ Runner: reads `upload_enabled` from `SchedulerConfig`
- ✅ CLI: `--upload` flag on `run_publisher`, standalone `run_upload` command
- ✅ WordPress helper: `scripts/wp_shortcode_install.py` (shortcode + page creation)
- ✅ Unit tests: `test_ftps_upload.py` (8 tests), `test_publisher_local.py` (11 tests), `test_pipeline_upload.py` (2 tests)
- ✅ Live server tests: `test_upress_validation.py` (U01–U12, marked `@pytest.mark.upress`)

### Phase B — QA Validation (Team 50)

| Test Type | Scope |
|-----------|-------|
| Unit | `pytest tests/ -m "not upress"` — all PASS |
| FTPS Unit | `pytest tests/test_ftps_upload.py` — 8 tests PASS |
| Publisher | `pytest tests/test_publisher_local.py` — 11 tests PASS |
| Pipeline | `pytest tests/test_pipeline_upload.py` — 2 tests PASS |
| Integration | U01–U12 live server tests: `pytest -m upress tests/test_upress_validation.py` |
| End-to-End | Publish → upload → verify public URL → WordPress page renders |
| Fallback | Verify `manifest_last_good.json` serves stale data |
| Stale Banners | Verify correct banners at 3d warning and 8d irrelevant thresholds |

### Gate G7 — Acceptance Criteria
- [ ] All local pytest suites pass (0 failures)
- [ ] U01–U12 live server tests pass
- [ ] WordPress shortcode installed, page at `/SmallFarmsAgent` renders report
- [ ] End-to-end publish → upload → public access verified
- [ ] `manifest_last_good.json` fallback verified
- [ ] Stale banners display at correct thresholds (3d / 8d)
- [ ] **Nimrod manual approval → LIVE**

---

## M8 — UX Polish + Policy Formalization
**Teams:** Team 10 (template), Team 80 (SEO guidance)
**Dependency:** M7 Go-Live complete
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M8_UX_POLISH_TEAM10.md`
**Spec:** `_COMMUNICATION/TEAM_100/reports/2026-04-02_M8_M10_DETAILED_SPEC_TEAM100.md`
**Status:** ACTIVE

### Phase A — Implementation

**Team 10 (template changes):**
- Item 1: Tooltip layer — custom JS tooltips on table headers (6 terms)
- Item 2: Community CTA banner — below table, WhatsApp link with pre-filled message
- Item 3: Visual hierarchy — CSS adjustments to emphasize average price
- Item 5: Privacy paragraph — add to transparency block in template

**Team 80 (guidance — no code):**
- Item 4: SEO — provide meta title, description, OG tag recommendations for WordPress admin

**Team 100 (spec):**
- Privacy Policy spec: `docs/PRIVACY_POLICY.md` ✅ CREATED

### Gate G8 — Acceptance Criteria
- [ ] All 6 tooltips functional on desktop (hover) and mobile (tap)
- [ ] CTA banner renders between table and transparency block
- [ ] WhatsApp link opens with pre-filled Hebrew message
- [ ] Average price is clearly the visual anchor in each row
- [ ] Privacy paragraph appears in transparency block
- [ ] SEO meta data updated in WordPress admin
- [ ] All existing tests still pass (no regression)
- [ ] Nimrod visual sign-off on public page
- [ ] Team 50 written sign-off

---

## M9 — Site Optimization and Maintenance
**Teams:** Team 10 (implementation), Team 100 (spec)
**Dependency:** Gate G8 must be open
**Status:** COMPLETE — Implementation done, pending Nimrod WP Admin actions

### Phase A — Implementation (Team 10)
- 7-phase optimization plan executed:
  - Phase 1: Security hardening (Yoast removal, readme.html, security headers)
  - Phase 2: Plugin cleanup (9 plugins disabled: Yoast, CF7 comments, OptinMonster, TrustPulse, GSheetConnector, CRED, Layouts, Access, Regenerate Thumbnails)
  - Phase 3: Facebook SDK removal from header.php + IE conditional cleanup
  - Phase 4: Toolset audit and optimization (CRED, Layouts, Access disabled)
  - Phase 5: WPForms conditional loading, admin asset dequeuing
  - Phase 6: File system cleanup (14 legacy dirs, 16 WC images, 27 old reports, 4 unused themes)
  - Phase 7: SEO preparation (documented WP Admin actions for Nimrod)
- Report rotation added to FTPS upload pipeline
- Dead WooCommerce code removed from functions.php
- **Phase 8 (Nimrod-initiated):** SEO, caching, and forms finalization:
  - SEO migrated from AIOSEO to Yoast SEO (included in uPress Pro plan). AIOSEO disabled.
  - Caching switched from WP Rocket to ezCache (uPress native). WP Rocket removed by Nimrod.
  - WPForms removed. Replaced with zero-plugin `[sfagent_contact_form]` shortcode in functions.php.
  - New plugins added by Nimrod: validator-pizza, wpconsent-cookies-banner-privacy-suite
  - functions.php cleaned: removed all WPForms dequeue code, added contact form handler
  - style.css cleaned: removed WPForms CSS remnants
- Results: 20→10 active plugins, 29→11 scripts, 12→4 stylesheets, 0 console errors

### Completion Report
`_COMMUNICATION/TEAM_10/reports/2026-04-02_M9_SITE_OPTIMIZATION_COMPLETE_TEAM10.md`

---

## M9-Content — Content + Community Engagement (formerly M9)
**Teams:** Team 80 (blog post), Team 10 (integration), Nimrod (approval)
**Dependency:** M9 optimization complete
**Mandate:** `_COMMUNICATION/TEAM_80/MANDATE_M9_BLOG_POST_TEAM80.md`
**Status:** PLANNED

### Phase A — Implementation

**Team 80 (content):**
- Item 6: Blog post draft in Hebrew — "Why My Farm Wasn't Profitable"
  - Requires Nimrod briefing: talking points, tone, boundaries
  - 800–1200 words, structured per Team 80 outline
  - Nimrod approval required before publication

**Team 10 (integration):**
- Item 7: WhatsApp data submission protocol
  - Document intake process in `documentation/05-admin-and-operations/`
  - Add blog post link to vision block on public page
  - Process at least one test submission end-to-end

### Gate G9 — Acceptance Criteria
- [ ] Blog post published on nimrod.bio
- [ ] Blog post linked from SmallFarmsAgent page
- [ ] Content approved by Nimrod
- [ ] WhatsApp intake protocol documented
- [ ] At least one test data submission processed
- [ ] Nimrod sign-off

---

## M10 — Advanced Interaction (Specification Only)
**Teams:** Team 100 (architecture), Team 80 (product input)
**Dependency:** Gate G9
**Status:** PLANNED — produces documents only, no code

### Deliverables (spec documents)
- Item 8: WordPress Farmer Roles — architecture decision document
- Item 9: FarmCostAgent — concept brief for new agent under MyFarmAgents
- Item 10: In-Page Submission Form — technical spec (depends on Item 8)

### Gate — None
M10 is a planning milestone. Its outputs feed future milestones (M11+).

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
| G3 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G3_v2.md` (v2 — active) |
| G4 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md` ✅ ISSUED |
| G5 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G5.md` ✅ ISSUED · ✅ PASS |
| G6 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G6.md` ✅ ISSUED · ✅ PASS |
| G7 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G7.md` ✅ ISSUED |
| G8 | Pending — to be issued with M8 mandate |
| G9 | Pending — Nimrod content approval |

---

## Reference Documents

| Document | Location |
|----------|---------|
| Canonical Glossary | `docs/GLOSSARY.md` |
| RTL Development Guide | `docs/RTL_DEVELOPMENT_GUIDE.md` |
| Operations Runbook | `docs/OPERATIONS.md` |
| Database Schema (29 tables) | `docs/DATABASE_SCHEMA_SPEC_HE.md` (legacy Hebrew) |
| Pipeline Algorithms | `docs/PIPELINE_ALGORITHMS_HE.md` (legacy Hebrew) |
| Normalizer Spec | `docs/NORMALIZER_SPEC_HE.md` (legacy Hebrew) |
| Product Catalog (67 products) | `docs/PRODUCT_CATALOG_V1.md` (original 29 + expansions) |
| Source Map (20 sources) | `docs/SOURCE_MAP_MASTER_HE.md` (legacy Hebrew) |
| Architecture Decisions | `docs/ARCHITECTURE_DECISIONS_HE.md` (legacy Hebrew) |
| Privacy Policy | `docs/PRIVACY_POLICY.md` |
| uPress Validation Plan | `docs/UPRESS_VALIDATION_PLAN_HE.md` (M7 gate) |
| Documentation Hub (English) | `documentation/README.md` |
| Normalizer Baseline | `data/normalizer_baseline.json` |

> All `_HE.md` spec documents are legacy Hebrew.
> English mandates and `documentation/` hub are the authoritative implementation and QA guides.

---

## Post-M6 Pipeline Resolution Achievement

After M6, a focused initiative improved normalizer resolution from 38.6% to **100%**:

| Metric | Baseline (post-M6) | After Resolution Work | Delta |
|--------|--------------------|-----------------------|-------|
| Resolution rate | 38.6% | **100%** | +61.4pp |
| Unresolvable items | 262 | **0** | −262 (−100%) |
| Normalized observations | 165 | **174** | +9 |
| Ignored (scope-skip) | 68 | **334** | +266 |
| Scope-skip rules | 13 | **301** | +288 |
| Product aliases | 121 | **232** | +111 |
| Products in catalog | 29 | **67** | +38 |
| Alembic migrations | 016 | **029** | +13 |

Key artifacts:
- `_COMMUNICATION/TEAM_100/reports/2026-03-31_PIPELINE_RESOLUTION_SIGNOFF_TEAM100.md`
- `_COMMUNICATION/TEAM_100/reports/2026-03-31_NORMALIZER_SUCCESS_IMPROVEMENTS_NIMROD_PLAN_TEAM100.md`
- `data/normalizer_baseline.json` — frozen baseline snapshot
