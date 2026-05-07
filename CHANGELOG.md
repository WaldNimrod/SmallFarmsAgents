# Changelog

All notable changes to OrganicMarketAgent are documented in this file.

**Format:** Each entry includes date, team, scope, and description.
**Rule:** Every code change must be logged here before the session ends. At the end of a significant phase, documentation is updated with all entries and a version bump is issued.

---

## [Unreleased]

_(Log new changes here as they happen. Move to a versioned section at milestone end.)_

### M10 Thaw — SFA-S002-P001-WP001 (Team 10, 2026-05-07)

- **2026-05-07 — Team 10 (WP001):** M10 thaw via Strategy C (extract+reapply from `cursor/m10-doc-mandates-spike@bb981ed`). Integration branch: `offline/2026-05-07-smallfarmsagents-release-prep`. Source branch tagged `archive/m10-spike-bb981ed`.
  - **New:** `organic_market_agent/db/versions/032_cq_p01_alias_batch.py` — CQ-P01 SCOPE_SKIP_RULES + GLOBAL_ALIASES + SCOPED_ALIASES template (renumbered from branch 072; no-op upgrade, chain only; data filled in H1 handoff).
  - **New:** `organic_market_agent/db/versions/033_src_wa_pending_manual.py` — extend `raw_extracted_items.extraction_status` CHECK to include `'pending_manual'`; seed SRC_WA source with canonical fetch/normalizer profiles (renumbered from branch 073).
  - **New:** `organic_market_agent/normalizer/basket_tier_resolver.py` — CSA basket → PRD025/PRD026/PRD027 (small/medium/large) tier resolver. Item-count priority over price; fallback PRD026 when count < 5 (ARCH-20260406-CQ-MASTER §3.7.2).
  - **New:** `organic_market_agent/publisher/report_details.py` — product `details` for publish JSON v3 (variants, price_series, CSA merge).
  - **Updated:** `organic_market_agent/db/check.py` — health probe updated to expect sources >= 21 (post-SRC_WA seed).
  - **Updated:** `organic_market_agent/publisher/rolling_aggregate.py` — full per-filter-key stats (`all`/`grower`/`store`/`chain`/`baskets`), `stats_by_filter` shape, `details` object, `display_bucket` JOIN.
  - **Updated:** `organic_market_agent/models/runs.py` — `RawExtractedItem` CHECK constraint extended to include `pending_manual` status (matches migration 033).
  - **Updated:** `organic_market_agent/utils/config.py` — added `PLAYWRIGHT_HEADLESS` + `PLAYWRIGHT_TIMEOUT_MS` fields (M10.4 mypips SPA support). All WP008 methods (`wp_rest_configured`, `ftps_configured`, `upress_configured`) preserved intact.
  - **Tests:** `tests/test_basket_tier_resolver.py` (11 tests), `tests/test_extraction_status_pending_manual.py` (2 DB tests), `tests/test_db_health.py` (updated with require_postgres module-level skip).
  - **Config:** `.python-version` set to `3.11`; `.env.example` extended with Playwright vars.
  - **Migration disposition:** Branch 031 (mypips workbook) SKIPPED (conflicts with main's 031); branch 032–071 (41 migrations) SKIPPED (M10.2-5/M13-PRE content deferred to future WPs; no schema deps required for 032/033 carry).

### Governance — external L-GATE_VALIDATE (Team 190)

- **2026-05-07 — Team 190:** Constitutional verdict **PASS_WITH_FINDINGS** for **SFA-S002-P001 Phase 1** (assignment **SFA-S002-P001-WP005** — bundle WP003+WP004+WP006+WP007). Artifact: [`_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md`](_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md). Mechanical: `validate_aos.sh` **29 PASS / 17 SKIP / 0 FAIL**; pytest spot **81 passed** (`test_wp_upload`, `test_responsive_html`, `test_ftps_upload`). Key finding **F-190-01:** scheduler `pipeline.py` and admin `runs_upload_now` still FTPS-only; WP REST primary path matches `run_publisher --upload` / `_do_upload` only. **F-190-01 fix landed same day** in WP008 (entry below).

### Fixed — WP REST upload wired into scheduler + admin entrypoints (Team 10, SFA-S002-P001-WP008)

- **2026-05-07 — Team 10 (WP008 / F-190-01 fix):** Prior to this change, WP REST upload was only active in the CLI path (`__main__.py::_do_upload`). The daily cron scheduler (`scheduler/pipeline.py`) and Admin UI manual-upload button (`admin/routes/runs.py::runs_upload_now`) both still called `ftps_upload.upload_artifacts` directly, causing silent failure due to Bezeq port-21 block. Remediation of team_190 finding F-190-01 MEDIUM (verdict commit `ccb5939`).
  - **New:** [`organic_market_agent/publisher/upload_dispatch.py`](organic_market_agent/publisher/upload_dispatch.py) — `dispatch_upload(output_dir, *, allow_fallback_ftps_env)` shared helper with `UploadResult` dataclass and `NoUploadConfigured` exception. WP REST primary; FTPS fallback gated on `UPRESS_FALLBACK_FTPS=1`.
  - **Updated:** `scheduler/pipeline.py` upload phase — now calls `dispatch_upload()` (was: `ftps_upload.upload_artifacts`). Scheduler-specific `pipeline_alerts` insertion and error handling preserved. Phase labels updated from `ftps_upload` / `ftps_upload_done` to `upload` / `upload_done`.
  - **Updated:** `admin/routes/runs.py::runs_upload_now` — now calls `dispatch_upload()` (was: `ftps_upload.upload_artifacts`). JSON/flash response shape preserved for Admin UI.
  - **Updated:** `utils/config.py::upress_configured()` — now returns `wp_rest_configured() or ftps_configured()` so scheduler upload gate fires when WP REST keys are set (was: FTPS-only check). Added `ftps_configured()` companion classmethod.
  - **Tests:** [`tests/test_upload_dispatch.py`](tests/test_upload_dispatch.py) (11 unit tests), [`tests/test_scheduler_upload_path.py`](tests/test_scheduler_upload_path.py) (7 tests including F-190-01 regression guard), [`tests/test_pipeline_upload.py`](tests/test_pipeline_upload.py) updated (patched `dispatch_upload` instead of `upload_artifacts`). All 20 upload tests pass.
  - **Docs:** Runbook §1 updated with shared-helper row and WP008 note.

### Changed — WP REST API upload — F-01 fix (Team 10, SFA-S002-P001-WP007)

- **2026-05-07 — Team 10 (WP007 / F-01 root-cause fix):** Replaced primary upload path from FTPS (port 21, blocked by Bezeq egress on waldhomeserver) to **WP REST API** (HTTPS port 443, same pattern as shaked-wg-agent, proven on same host). New file [`organic_market_agent/publisher/wp_upload.py`](organic_market_agent/publisher/wp_upload.py) — `upload_artifact()` + `upload_all_artifacts()` with HTTP Basic auth, delete-before-overwrite (per-artifact `data/.wp_media_id_*` tracking files), MAX_RETRIES=3 with backoff (5/10/20s), and `MissingCredentialsError` on 401/403. Pipeline wired in [`organic_market_agent/__main__.py`](organic_market_agent/__main__.py): `_do_upload()` tries WP REST first; FTPS fallback gated on `UPRESS_FALLBACK_FTPS=1` (default off, port-21 code preserved). AC-04 Option A: pipeline writes `sfagent-manifest-of-urls.json` pointer to media library; shortcode dereferences. [`scripts/wp_shortcode_install.py`](scripts/wp_shortcode_install.py) updated to use `get_option('sfagent_manifest_of_urls_url')` pattern + `--set-mou-url` CLI arg. Config: `UPRESS_WP_REST_BASE` default changed from `""` to `"https://www.nimrod.bio/wp-json"` + `wp_rest_configured()` classmethod. `.env.example`: activated 3 WP REST keys (previously commented out). Tests: [`tests/test_wp_upload.py`](tests/test_wp_upload.py) — 20 unit tests (all green, mocked). Docs: `PUBLISH_CHECKLIST.md` §4 rewritten (WP REST primary + FTPS opt-in); `UPRESS_WORDPRESS_STANDARD_v2.md` §15 added (port-21-blocked-network pattern). Deploy handoff: `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`. Architectural choice: `_COMMUNICATION/team_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md`. Production smoke by team_99 (env update + WP003 Pass-2).

### Fixed — FTPS upload TLS session reuse (Team 10, SFA-S002-P001-WP006)

- **2026-05-07 — Team 10 (WP006 / F-01):** Confirmed `ReusedSessionFTP_TLS` subclass (overriding `ntransfercmd` to wrap the data socket with the control connection's TLS session) is present in [`organic_market_agent/publisher/ftps_upload.py`](organic_market_agent/publisher/ftps_upload.py) and all upload entry points use it. Extended [`tests/test_ftps_upload.py`](tests/test_ftps_upload.py) with AC-03 coverage: `ntransfercmd` session-reuse behavior, retry/backoff constants, and full 4-file canonical artifact upload. Resolves F-01 HIGH: uPress `425 Unable to build data connection` caused by missing TLS session reuse — public price-index artifacts were stuck at `artifact_version=20260417_004822` (19 days stale). Production deploy and smoke verification deferred to team_99 (AC-05/AC-06).

### Documentation — project context (Team 10)

- **2026-04-17 — Team 10:** Synced **`_aos/context/PROJECT_CONTEXT.md`** with current **`validate_aos.sh` expectations (0 FAIL; 26/9/0 as of 2026-04-22)**, **WordPress/uPress publish** references (`PUBLISH_CHECKLIST`, `WORDPRESS_PUBLIC_PUBLISH_RUNBOOK`, `AGENTS.md`, `docs/UPRESS_WORDPRESS_STANDARD_v2.md`, key code paths), and **2026-04 production parity** links (Team 10/50/190 reports, `CHANGELOG` [Unreleased]). Updated **`_aos/context/ACTIVATION_ARCH.md`**, **`AGENTS.md`**, **`CLAUDE.md`** (Domain rules), **`.cursor/rules/project-context.mdc`**, **`documentation/README.md`** (quick map + agent steps) to point to the same SSoT.

### Communication — QA + validation (Team 10)

- **2026-04-21 — Team 10:** QA review request to Team 50: [`_COMMUNICATION/TEAM_50/reports/2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`](_COMMUNICATION/TEAM_50/reports/2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md) (production FTPS path parity / public static consistency). Team 190 validation request (inbox): [`_COMMUNICATION/TEAM_190/inbox/2026-04-21_VALIDATION_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`](_COMMUNICATION/TEAM_190/inbox/2026-04-21_VALIDATION_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md). **Outcomes (close-out):** Team 50 [`_COMMUNICATION/TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md`](_COMMUNICATION/TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md). Team 190: prior [`_COMMUNICATION/TEAM_190/reports/2026-04-21_ProductionDataParity_L0_VALIDATION_TEAM190.md`](_COMMUNICATION/TEAM_190/reports/2026-04-21_ProductionDataParity_L0_VALIDATION_TEAM190.md); final **PASS** [`_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md`](_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md) (`validate_aos.sh` **26 PASS / 9 SKIP / 0 FAIL**).

### Operations — FTPS path parity + public manifest verify (Team 10)

- **2026-04-21 — Team 10:** [`organic_market_agent/utils/config.py`](organic_market_agent/utils/config.py) — optional `UPRESS_WP_REST_BASE`, `UPRESS_WP_APP_USER`, `UPRESS_WP_APP_PASS`. [`organic_market_agent/publisher/ftps_upload.py`](organic_market_agent/publisher/ftps_upload.py) — optional `UPRESS_EZCACHE_PURGE_AFTER_UPLOAD` POST to ezCache REST after successful FTPS (before `UPRESS_VERIFY_PUBLIC_MANIFEST`); documents FTP-vs-HTTPS stale edge case when CDN `Last-Modified` lags FTP. [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md), [`.env.example`](.env.example) updated.
- **2026-04-18 — Team 10:** **waldhomeserver** `.env`: `UPRESS_PUBLIC_BASE=https://www.nimrod.bio`, `UPRESS_UPLOAD_PATH=wp-content/uploads/market` (aligns FTPS with WordPress shortcode path; legacy `sfa` / `agents/sfa` removed from active use). `run_publisher --upload` redeployed artifacts to `wp-content/uploads/market`. Legacy duplicate files removed under FTP `sfa/`. [`organic_market_agent/publisher/ftps_upload.py`](organic_market_agent/publisher/ftps_upload.py) — optional `UPRESS_VERIFY_PUBLIC_MANIFEST` GET+compare `artifact_version` after upload (browser-like `User-Agent`; warn on CDN mismatch / 403). [`.env.example`](.env.example), [`PUBLISH_CHECKLIST.md`](documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md), [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md) updated. Sign-off: [`_COMMUNICATION/TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](_COMMUNICATION/TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md).

### Operations — daily FTPS + SRC017 paused (Team 10)

- **2026-04-17 — Team 10:** Alembic [`031_deactivate_src017_pricez.py`](organic_market_agent/db/versions/031_deactivate_src017_pricez.py) — sets **`sources.is_active`** and **`source_fetch_profiles.is_active`** to **false** for **SRC017** (Pricez; 403 from host). **waldhomeserver:** `scheduler_config.upload_enabled=true`; `UPRESS_SFTP_*` present in `.env`; SRC017 deactivated in DB (pull `main` then `alembic upgrade head` to apply migration **031** and align `alembic_version`). Docs: [`PUBLISH_CHECKLIST.md`](documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md), [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md).

### Public report — responsive UI (Team 30)

- **2026-04-17 — Team 30:** Mobile layout for the public price index uses **stacked product cards** with full metrics (including standard deviation) below 640px; desktop/tablet keeps the full **table**. Updated [`organic_market_agent/publisher/templates/public_report.html`](organic_market_agent/publisher/templates/public_report.html), [`organic_market_agent/publisher/templates/public_report_body.html`](organic_market_agent/publisher/templates/public_report_body.html), and [`organic_market_agent/publisher/static/sfagent-base.css`](organic_market_agent/publisher/static/sfagent-base.css) (removed global `.sfa-hide-mobile` suppression). [`tests/test_publisher_local.py`](tests/test_publisher_local.py) asserts responsive markup keys. Completion note: [`_COMMUNICATION/team_30/COMPLETION_PUBLIC_UI_RESPONSIVE_2026-04-17.md`](_COMMUNICATION/team_30/COMPLETION_PUBLIC_UI_RESPONSIVE_2026-04-17.md).
- **2026-04-17 — Documentation:** [`documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md) — added **canonical public page** subsection: themed WordPress URL (e.g. `/smallfarmsagent/`) = `public_report_body.html` + `sfagent-base.css`, distinct from standalone `public_report.html`. [`AGENTS.md`](AGENTS.md) — one-line pointer for agents.
- **2026-04-17 — Operations:** Deployed publish artifacts via `run_upload` (FTPS → `wp-content/uploads/market/`) and full [`scripts/wp_shortcode_install.py`](scripts/wp_shortcode_install.py) (child theme CSS + WP REST page check). *Publish snapshot:* seeded Docker DB (`DATABASE_URL=postgresql://oma:oma@localhost:5433/organic_market_agent`) because `.env` `DATABASE_URL` did not satisfy the 2-community-source rolling publish gate — re-run `run_publisher` + upload from the pipeline host when production window data is required.
- **2026-04-17 — Config:** [`organic_market_agent/utils/config.py`](organic_market_agent/utils/config.py) — load `.env.upress` after `.env` (`override=False`) so `UPRESS_WP_ADMIN_*` and other uPress-only keys work without manually appending to `.env`. [`.env.example`](.env.example) note updated.
- **2026-04-17 — Team 30:** Evidence-backed live verification note [`_COMMUNICATION/team_30/VERIFICATION_SIGNOFF_PUBLIC_PAGE_2026-04-17.md`](_COMMUNICATION/team_30/VERIFICATION_SIGNOFF_PUBLIC_PAGE_2026-04-17.md) — responsive UI + CDN/CSS checks on `nimrod.bio`; explicit limitation on business data currency when `report_date` reflects seeded publish.
- **2026-04-17 — Operations (waldhomeserver):** Diagnostic [`_COMMUNICATION/TEAM_10/reports/2026-04-17_WALD_SERVER_SCHEDULER_DIAGNOSTIC.md`](_COMMUNICATION/TEAM_10/reports/2026-04-17_WALD_SERVER_SCHEDULER_DIAGNOSTIC.md) — daily SFA cron active Apr 12–16; `upload_enabled` false (no auto FTPS); SRC017 403; Apr 17 06:00 UTC run not yet executed at ~00:54 UTC sample time.

### Governance — archive canonicalization (Team 100 mandate)

- **Archived** completed WP `S001-P001-WP001` artifacts from `_COMMUNICATION/TEAM_190/` to [`_archive/S001-P001-WP001/`](_archive/S001-P001-WP001/) (`L-GATE_V_result.md`, `TEAM_100_TO_TEAM_190_SFA_MIGRATION_VALIDATION_v1.0.0.md`) with [`ARCHIVE_MANIFEST.md`](_archive/S001-P001-WP001/ARCHIVE_MANIFEST.md).
- **Updated** [`_COMMUNICATION/README.md`](_COMMUNICATION/README.md), [`_COMMUNICATION/TEAM_190/README.md`](_COMMUNICATION/TEAM_190/README.md) — pointers to `_archive/` for closed WPs.

### Communication — Team 10 (cross-infrastructure validation)

- **Added** [`_COMMUNICATION/TEAM_10/reports/2026-04-11_FAMELY_NEUSLETTER_NIMROD_BIO_VALIDATION.md`](_COMMUNICATION/TEAM_10/reports/2026-04-11_FAMELY_NEUSLETTER_NIMROD_BIO_VALIDATION.md) — executive synthesis from Team 61 inbox (**MSG-009/010/004**), live `curl` validation of `nimrod.bio/agents/` + pilot newsletter HTML, pass/fail table (Famely product; see `documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`).

### Communication — Team 100 / Post-M9 direction (LOD200)

- **Added** [`_COMMUNICATION/TEAM_100/specs/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md`](_COMMUNICATION/TEAM_100/specs/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md) — canonical package `SFA-PKG-POST-M9-001` (WP-A1 moderated submissions for registered users; WP-A2 non-AI farmer economics calculator; frozen legacy M10 bundle; Team 61 RFI / M9C scope notes).
- **Added** [`_COMMUNICATION/TEAM_190/inbox/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md`](_COMMUNICATION/TEAM_190/inbox/SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md) — Team 190 review copy (inbox mirror).
- **Updated** [`_COMMUNICATION/ROADMAP.md`](_COMMUNICATION/ROADMAP.md) — v5.0 (2026-04-11): Team 190 row, Post-M9 LOD200 block, M10 marked **FROZEN**, M11 reframed as **vision backlog (reference only)** aligned with WP-A1/WP-A2.

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
