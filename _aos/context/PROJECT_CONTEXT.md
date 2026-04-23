# PROJECT CONTEXT — SmallFarmsAgents

## AOS environment (read first)

- **Repository role:** **Spoke** — product + governance (L0); organic market domain; not the AOS hub.
- **Profile:** L0 — `_aos/metadata.yaml` (lean-kit snapshot in `_aos/lean-kit/`).
- **AOS structured WP / gate / lod state:** This repo runs **L0 governance** without an in-tree AOS v3 dashboard engine. **`_aos/roadmap.yaml`** remains the practical registry for AOS work packages and gates **for file-based workflows**. If this project is later connected to a **shared AOS v3 PostgreSQL** used for structured AOS state, mutations must follow **API + `deploy_cascade()`** per hub `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` and `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (Iron Rule #7) — same rules as other profiles when the DB is online.
- **Application / domain data:** Product database and code under `organic_market_agent/`, `hub/`, etc. — domain SSoT per `CODE_STANDARDS` / WP specs (separate from AOS governance files).
- **Roadmap file:** `_aos/roadmap.yaml` — AOS WP list + `gate_history[]`; single-writer per Iron Rule unless/until ADR034 DB path is active.
- **Boundaries:** `_aos/project_identity.yaml` (`organic_market` domain — forbidden patterns enforced by `validate_aos.sh` Check 12)
- **Hub (methodology read-only):** `/Users/nimrod/Documents/agents-os` — do not author hub files from this repo
- **Validation:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — require **0 FAIL** before AOS/gate language in reporting. **PASS/SKIP counts drift** as lean-kit adds checks. As of **2026-04-22** (Team 190, production parity work): **26 PASS / 9 SKIP / 0 FAIL** on this spoke (see `CHANGELOG.md` [Unreleased] and `_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md`). Older notes citing **17 / 2 / 0** are superseded for count expectations, not for the **0 FAIL** rule.

## Team entry

- **Architecture / specs:** `_aos/context/ACTIVATION_ARCH.md` or `_COMMUNICATION/team_100/` mandates
- **Implementation (Python/data):** `_aos/context/ACTIVATION_BUILDER.md` or Team 110 routing
- **Validation:** `_aos/context/ACTIVATION_VALIDATOR.md` — L-GATE_BUILD / cross-engine vs builder

## Domain profile

### What this product is

Community AI agent platform for **Israel's organic farming market**. Core product: **OrganicMarketAgent** — community price index for organic vegetables (scraping/normalizing Israeli retail + farm sources). Stack: Python 3.11, PostgreSQL, FastAPI, Alembic, Docker. **Domain id:** `organic_market` (Hebrew NLP, price normalization).

### Current focus

Active milestone and WPs: `_aos/roadmap.yaml`. Run `validate_aos.sh` before any gate declaration. Human process and narrative roadmap: [`_COMMUNICATION/ROADMAP.md`](../../_COMMUNICATION/ROADMAP.md) (e.g. v5.0+ Post-M9 direction). Historical phases (M1–M9) are background only for domain code — current truth for AOS WPs is `roadmap.yaml` + LOD for assigned work packages.

### WordPress / uPress — public market index (as of 2026-04)

- **Served tree:** Pipeline FTPS must upload to the same `wp-content/...` tree the themed page loads from (typically `wp-content/uploads/market/`), via **`UPRESS_UPLOAD_PATH`** and **`UPRESS_PUBLIC_BASE`** on the publish host. [`AGENTS.md`](../../AGENTS.md) describes the **live** page: `[sfagent_market_report]` + `public_report_body.html` + `sfagent-base.css` — not standalone `public_report.html` alone.
- **Code / config (reference):** [`organic_market_agent/publisher/ftps_upload.py`](../../organic_market_agent/publisher/ftps_upload.py) — optional `UPRESS_VERIFY_PUBLIC_MANIFEST`, `UPRESS_EZCACHE_PURGE_*` (ezCache after upload); [`organic_market_agent/utils/config.py`](../../organic_market_agent/utils/config.py); shortcode + theme: [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py). Dotenv: [`.env.example`](../../.env.example).
- **Runbooks (full procedures):** [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md), [`documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md).
- **uPress + hosting normative spec:** [`docs/UPRESS_WORDPRESS_STANDARD_v2.md`](../../docs/UPRESS_WORDPRESS_STANDARD_v2.md) — credentials, FTPS, REST, panels (cross-project on this host: server **s887**).
- **Production data parity (2026-04) — sign-off and QA:** Team 10 sign-off: [`_COMMUNICATION/TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](../../_COMMUNICATION/TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md); Team 50 findings: [`_COMMUNICATION/TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md`](../../_COMMUNICATION/TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md); Team 190 final **PASS:** [`_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md`](../../_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md). Session log / close-out: [`CHANGELOG.md`](../../CHANGELOG.md) [Unreleased] — *Communication — QA + validation* and *Operations — FTPS path parity*.

### Standards / SSOT

- Application code standards: `_aos/context/CODE_STANDARDS.md` (if present) and package `organic_market_agent/`
- Tests: `tests/` — maintain bar established in pre-AOS QA cycles
- Documentation: **English** hub at [`documentation/README.md`](../../documentation/README.md) (topic index; archive policy, troubleshooting). Cross-repo boundaries: [`documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`](../../documentation/external-references/CROSS_PROJECT_BOUNDARIES.md)
- Integration / handoff: `_COMMUNICATION/`, `hub/` data integration as specified per WP
- AOS data authority (when AOS DB shared): hub ADR034 (read-only path above)

### Repository map (quick)

| Area | Purpose |
|------|---------|
| `organic_market_agent/` | Main Python package |
| `hub/` | Data hub integration |
| `scripts/` | Operational scripts |
| `tests/` | Test suite |
| `_aos/context/` | AOS + domain context (`PROJECT_CONTEXT.md`, `ACTIVATION_*.md`); read with `_aos/roadmap.yaml` at session start |
| `_aos/work_packages/` | LOD specs |
| `_COMMUNICATION/` | Team reports, `ROADMAP.md`, templates |
| `documentation/` | English operator/AI documentation hub (see `documentation/README.md`) |
