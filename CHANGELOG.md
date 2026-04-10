# Changelog

All notable changes to OrganicMarketAgent are documented in this file.

**Format:** Each entry includes date, team, scope, and description.
**Rule:** Every code change must be logged here before the session ends. At the end of a significant phase, documentation is updated with all entries and a version bump is issued.

---

## [Unreleased]

_(Log new changes here as they happen. Move to a versioned section at milestone end.)_

### Documentation — waldhomeserver / Team 61 (Team 100)

- **Added** [`documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md) — canonical file-based handoff (Mac `~/Documents/_agent_comm/outbox/` → `scp` → `~/agent_comm/inbox/`), hosts, verification, anti-patterns.
- **Updated** [`documentation/05-admin-and-operations/README.md`](documentation/05-admin-and-operations/README.md), [`documentation/README.md`](documentation/README.md), [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc) — linked summary for agents.

### Documentation — development workstation scheduler (Team 100)

- **Added** [`documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md`](documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md) — no automated daily ingestion on developer laptops; manual/on-demand only.
- **Updated** [`docs/OPERATIONS.md`](docs/OPERATIONS.md) — warning at top; [`documentation/05-admin-and-operations/README.md`](documentation/05-admin-and-operations/README.md); [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc).

### Communication — Team 10

- **Added** [`_COMMUNICATION/TEAM_10/reports/2026-04-10_SYSTEM_STATUS_DEV_AND_WALD_SERVER_TEAM10.md`](_COMMUNICATION/TEAM_10/reports/2026-04-10_SYSTEM_STATUS_DEV_AND_WALD_SERVER_TEAM10.md) — dev vs waldhomeserver snapshot and 2026-04-10 ingestion run analysis.

### Communication — Team 100 / process (corrective)

- **Removed** misplaced Famely Neusletter-only report from `_COMMUNICATION/TEAM_80/reports/` (that product is **not** versioned in SmallFarmsAgents; Neusletter artifacts belong in the Famely repo or `~/Documents/_agent_comm/`).
- **Added** [`documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`](documentation/external-references/CROSS_PROJECT_BOUNDARIES.md) — which artifacts belong in this repo vs other MyFarmAgents products; root-cause note on workspace confusion.
- **Added** [`_COMMUNICATION/TEAM_80/reports/README.md`](_COMMUNICATION/TEAM_80/reports/README.md) — SFA-only scope for this folder.
- **Updated** [`_COMMUNICATION/README.md`](_COMMUNICATION/README.md), [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc), [`documentation/external-references/README.md`](documentation/external-references/README.md), [`documentation/README.md`](documentation/README.md) — repository scope pointers.
- **Added** [`AGENTS.md`](AGENTS.md) — short default product scope for AI agents at repo root.

### Admin UI — `/runs` template (Team 10)

- **Fixed** [`organic_market_agent/admin/templates/admin/runs.html`](organic_market_agent/admin/templates/admin/runs.html) — removed a stray `{% endif %}` introduced with the stale-running alert so `{% if current_user.is_authenticated %}` / `{% else %}` nest correctly (resolves Jinja2 `TemplateSyntaxError: Encountered unknown tag 'else'` on `/runs`).
- **Added** [`tests/test_admin_jinja_templates.py`](tests/test_admin_jinja_templates.py) — compile check for `admin/runs.html` to catch similar regressions.

### Accessibility Compliance — WP Accessibility (Team 100)

- **Installed** WP Accessibility v2.3.3 (Joe Dolson) — activated by Nimrod via WP Admin
- **Updated** `flatsome-child/functions.php` — added `sfagent_configure_wpa()` one-time config (focus outlines with `#4c3113` brown matching site theme), `sfagent_wpa_hebrew_labels()` filter for Hebrew form labels (חיפוש, שם, אימייל, אתר, תגובה), `sfagent_accessibility_statement_shortcode` for Israeli law IS 5568 compliance page
- **Active features:** Keyboard focus outlines, form label injection (Hebrew), tabindex cleanup, viewport scaling fix, target attribute removal, RTL/lang detection
- **Zero UI interference:** No toolbar or floating widget — all fixes are code-level
- **Active plugins now:** 12 total (added: wp-accessibility)

### M9 Phase 8 — SEO, Caching, Forms Finalization (Team 100)

**SEO Migration:**
- **Disabled** AIOSEO plugin via FTPS (renamed `all-in-one-seo-pack` to `.disabled`). Yoast SEO installed by Nimrod via uPress premium library with data import from AIOSEO.

**Caching:**
- ezCache (uPress native) installed by Nimrod, replacing WP Rocket (removed from server by Nimrod).

**Contact Form (zero-plugin replacement for WPForms):**
- **Updated** `flatsome-child/functions.php` — removed all WPForms dequeue code (dead after plugin removal), added `sfagent_contact_form` shortcode (name, email, phone, message fields), `sfagent_handle_contact_form` submission handler via `admin-post.php` with nonce + honeypot anti-spam + `wp_mail()`, `sfagent_contact_form_styles` conditional CSS loader
- **Updated** `flatsome-child/style.css` — removed 381 bytes of dead WPForms CSS rules (`.wpforms-one-third`, `.wpforms-first`, `div.wpforms-container-full`)

**Active plugins now:** admin-menu-editor, booter-bots-crawlers-manager, duplicate-post, ezcache, google-analytics-for-wordpress, tiny-compress-images, types, validator-pizza, wordpress-seo (Yoast), wp-views, wpconsent-cookies-banner-privacy-suite (11 total, including 2 new Nimrod additions)

### M7 Implementation — Public Publishing / Go-Live (Team 100)

**Config & Foundation:**
- **Added** uPress FTPS config properties to `Config` class (host, port, user, pass, public base, upload path, page slug, `upress_configured()`)
- **Added** FTPS alert tags: `TAG_FTPS_UPLOAD_SUCCESS`, `TAG_FTPS_UPLOAD_FAILURE`, `TAG_FTPS_UPLOAD_PARTIAL`
- **Added** Migration 030: `upload_enabled` boolean column on `scheduler_config` (default false)

**FTPS Upload Module:**
- **Created** `organic_market_agent/publisher/ftps_upload.py` — `ReusedSessionFTP_TLS` subclass (critical: TLS session reuse prevents 425 errors), `upload_artifacts()` with retry logic (3 attempts, exponential backoff), `FtpsUploadResult` dataclass, `MissingCredentialsError`
- **Created** `tests/test_ftps_upload.py` — 8 unit tests (mocked FTP): all-success, partial failure, total connection failure, missing local file, dry-run, missing credentials, TLS connection, quit cleanup

**PublishEngine Enhancements:**
- **Updated** `organic_market_agent/publisher/engine.py` — versioned filenames (`public_report-{ts}.json/html`, `public_report_body-{ts}.html`), fixed-name copies, `manifest_last_good.json`, manifest v2 schema (`schema_version`, `artifact_version`, `staleness_days`, `artifacts{}`, `fixed_names{}`, `upload_base`), body fragment rendering, file list in summary
- **Created** `organic_market_agent/publisher/templates/public_report_body.html` — scoped CSS body fragment for WordPress embedding (`.sfagent-market-report` wrapper, no `<html>`/`<head>`)
- **Updated** `tests/test_publisher_local.py` — 3 new tests (body fragment, versioned filenames, manifest_last_good), updated manifest key assertions for v2 schema

**Pipeline & CLI Integration:**
- **Updated** `organic_market_agent/scheduler/pipeline.py` — FTPS upload phase after publish (checks `upload_enabled` from scheduler_config + `config.upress_configured()`), creates pipeline alerts on success/partial/failure
- **Updated** `organic_market_agent/scheduler/runner.py` — reads `upload_enabled` from `SchedulerConfig`, passes `skip_upload` to `run_pipeline`
- **Updated** `organic_market_agent/__main__.py` — `--upload` flag on `run_publisher`, new `run_upload` standalone CLI command (reads manifest for file list, supports `--dry-run`)

**WordPress Integration:**
- **Created** `scripts/wp_shortcode_install.py` — downloads `functions.php` from flatsome-child via FTPS, appends `[sfagent_market_report]` shortcode if missing, creates WordPress page at `/SmallFarmsAgent` via WP REST API

**Tests:**
- **Created** `tests/test_upress_validation.py` — U01–U12 live server validation tests (marked `@pytest.mark.upress`): login, TLS, write, overwrite, versioned upload, manifest order, public HTTP access, cache TTL, WP page, JSON endpoint, manifest_last_good, full upload cycle
- **Created** `tests/test_pipeline_upload.py` — 2 integration tests (mocked): upload called when enabled, upload skipped when disabled

**QA & Documentation:**
- **Created** `_COMMUNICATION/TEAM_50/QA_MANDATE_G7.md` — 12 test criteria, gate pass matrix

### M7 Planning (Team 100)

- **Reviewed** Team 10's M7 work plan v1; upgraded to v2 with 5 binding architectural decisions
- **Added** concrete implementation specs: FTPS module interface, manifest v2 schema, upload protocol, body fragment spec, WordPress shortcode, pipeline integration, rollback table
- **Added** M7 feedback report for Team 10 with action items for all teams
- **Fixed** identified gaps: test rewrite requirements, known bugs in mandate test code, cleanup protocol, migration 030 for upload_enabled
- **Updated** plan to v2.1: Nimrod approved M7; child theme `flatsome-child` for shortcode; page slug `/SmallFarmsAgent`
- **Created** `.env.upress` credentials template for Nimrod — fully filled (FTPS, phpMyAdmin, WP admin, DB creds)
- **Updated** `.env.example` with FTPS configuration block (port 21)
- **Updated** `ROADMAP.md` — M7 approval recorded, transport and work plan reference added

### M7 Server Validation (Team 100 — 2026-03-31)

- **CONFIRMED** transport: FTPS (FTP over TLS) on port 21; SSH/SFTP port 22 is blocked
- **CONFIRMED** FTP root = WordPress root (no `public_html/` prefix)
- **CONFIRMED** child theme: `flatsome-child` with existing `functions.php` (WooCommerce overrides)
- **Created** `wp-content/uploads/market/` directory on uPress server
- **Extracted** DB credentials from `wp-config.php` → added to `.env.upress`
- **Updated** M7 work plan v2.1: all SFTP references corrected to FTPS, upload path corrected, M7-0b marked DONE, all §10 items marked complete
- **Updated** `.env.example` port default: 22 → 21
- **CRITICAL**: `ReusedSessionFTP_TLS` subclass required — standard `FTP_TLS` gets 425 errors without TLS session reuse

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
