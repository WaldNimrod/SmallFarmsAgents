# Changelog

All notable changes to OrganicMarketAgent are documented in this file.

**Format:** Each entry includes date, team, scope, and description.
**Rule:** Every code change must be logged here before the session ends. At the end of a significant phase, documentation is updated with all entries and a version bump is issued.

---

## [Unreleased]

_(Log new changes here as they happen. Move to a versioned section at milestone end.)_

---

## [0.6.1] — 2026-03-31

### Pipeline Resolution Improvement (Team 100 + Team 10)

- **Fixed** 1 false positive in scope-skip rules: Rule 51 (קלמנטינה) incorrectly caught fresh produce PRD055; deactivated with annotation
- **Added** 9 base aliases for last unresolvable products (לימון, תפוז, פפאיה, פלפל ירוק, פלפל רמירו, קולורבי, מנגולד, סלרי עלים, תפוח אדמה)
- **Cleaned** 64 test normalizer_rules (m5-rule-* / m5-rd-* patterns) and 9 quarantined test fixtures
- **Fixed** 2 failing aggregator tests: date-scoped alert queries in `test_aggregator_two_source_wide_spread_suppresses_publish_and_alerts` and `test_aggregator_second_run_same_suppression_no_duplicate_alert`
- **Achieved** 100% resolution rate (174 normalized, 0 unresolvable, 334 ignored)

### Documentation Refresh (Team 100)

- **Updated** `.cursor/rules/project-context.mdc` — full rewrite with current counts, routes, normalizer stages, maintenance commands
- **Updated** `_COMMUNICATION/ROADMAP.md` — v1.8→v1.9, added pipeline resolution metrics, updated reference docs
- **Updated** `README.md` — expanded with quick start, current state, project structure
- **Updated** `docs/GLOSSARY.md` — v1.0→v1.1, added 11 new terms (scope-skip, catalog inbox, automation)
- **Updated** `documentation/` hub — all 8 section READMEs refreshed with current architecture, counts, routes
- **Updated** all 4 team onboarding files — corrected counts, gate statuses, mandate tables, tech stack

---

## [0.6.0] — 2026-03-31

### M6 Automation + Resilience (Team 10 + Team 20)

- **Added** `scheduler_config` table and `pipeline_alerts` table (migration 016)
- **Added** `scheduler/runner.py` — cron entrypoint with self-gating, overlap guard, alert on outcome
- **Added** `scheduler/pipeline.py` — extended with `source_code`, `skip_normalize`, `skip_publish` for focused runs
- **Added** `/scheduler` admin blueprint — schedule control, cleanup trigger
- **Added** `/alerts` admin blueprint — mark-read, bulk mark-all
- **Added** Chart.js dashboard graphs (14-day resolution rate, source success/fail stacked bar)
- **Added** Alert badge in nav + unread alerts panel on dashboard
- **Added** Log cleanup (deletes old `source_fetch_runs` + cascade)
- **Added** `docs/OPERATIONS.md` — cron line and verification
- **Added** `tests/test_runner.py`, `tests/test_scheduler_routes.py`

---

## [0.5.0] — 2026-03-31

### M5 Admin UI (Team 10 + Team 20)

- **Added** Flask-Login + bcrypt authentication (migration 015 seeds admin user)
- **Added** Full CRUD for `ProductAlias` and `NormalizerRule` in admin UI
- **Added** `observation_flags` view, audit log viewer
- **Added** Background pipeline triggers from admin UI
- **Added** `tests/test_admin_routes.py` (11 tests)

---

## [0.4.0] — 2026-03-31

### M4 Aggregation + Local Viewer + Admin Dashboard (Team 10 + Team 20)

- **Added** `AggregatorEngine` — daily_aggregates, weekly_snapshots
- **Added** `QAEngine` — outlier detection, missing source alerts, duplicate detection
- **Added** `PublishEngine` — local publish (public_report.json/html, manifest.json)
- **Added** Local viewer (`localhost:8080`)
- **Added** Admin monitoring dashboard (Flask, read-only initially)
- **Added** Price dispersion rules (2-source spread, multi-source σ)
- **Added** `tests/test_aggregator.py`, `tests/test_publisher_local.py`, `tests/test_price_rules.py`

---

## [0.3.0] — 2026-03-30

### M3 Normalizer Engine (Team 10)

- **Added** `NormalizerEngine` — 8-stage pipeline (scope_skip, alias, organic, price, unit, quantity, price_norm, basket, confidence)
- **Added** `catalog_scope_skip_rules` support
- **Added** Blocking failure on alias/price stages → unresolvable
- **Added** `tests/test_normalizer.py` (18 tests)

---

## [0.2.0] — 2026-03-30

### M2 Collection Layer (Team 10)

- **Added** `CollectorEngine` + `BaseCollector` with retry, timeout, checksum dedup
- **Added** 3 collectors: EasyFarm, StandaloneHTML, GovtBenchmark
- **Added** `ParserEngine` dispatcher + 3 parsers
- **Added** `IngestionRunner` CLI
- **Added** `tests/test_collectors.py`, `tests/test_parsers.py`

---

## [0.1.0] — 2026-03-30

### M1 Local Foundation (Team 20)

- **Added** Python project skeleton (`organic_market_agent/` package)
- **Added** PostgreSQL 15 via Docker, Alembic migrations (001–005)
- **Added** SQLAlchemy 2.x models for all 23 tables
- **Added** Seed data: 11 units, 29 products, 20 sources, initial aliases
- **Added** `tests/test_db_health.py`
