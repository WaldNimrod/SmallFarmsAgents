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

### Public delivery tier — `sfa.nimrod.bio` (canonical, since 2026-05-23 / P003)

> **⚠ Anti-drift — read this before touching anything publish/deploy/host related.**
> The live site is a **Slim 4 / PHP 8 + PDO/MySQL app served from uPress** at `sfa.nimrod.bio`. It is **NOT** served from the home server, and it is **NOT** the old WordPress shortcode on `www.nimrod.bio`. "host" means three different machines — never conflate them:
>
> | Role | Machine | Serves end users? |
> |------|---------|-------------------|
> | **Web host** (the live site + MySQL) | **uPress** `sfa.nimrod.bio` | **YES — only here** |
> | **Backend / pipeline host** (Postgres SSoT, scrapers, cron) | **waldhomeserver** | **NO, never** |
> | **Deploy / push origin** (FTPS relay; egress allowlisted by uPress) | **waldhomeserver** | n/a — relay only |
>
> **The site MUST live on the uPress subdomain, never on the home server.** "waldhomeserver is the canonical OPS *deploy host*" = the machine you deploy *from*, not where the site runs.

- **BINDING ARCHITECTURE (SSoT):** [`documentation/02-architecture/sfa-delivery-tier.md`](../../documentation/02-architecture/sfa-delivery-tier.md) (§0 terminology, §1 two-tier) + [`documentation/02-architecture/README.md`](../../documentation/02-architecture/README.md) hard invariant.
- **UI code deploy (current):** [`documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`](../../documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md) — `scripts/ftp_deploy_sfa_ui.sh` (`composer install --no-dev` → `lftp mirror -R --delete` over FTPS:21 to uPress). Deploy must run from an allowlisted egress (waldhomeserver `46.235.231.114`); Mac's Bezeq IP is blocked.
- **Data push (current):** [`organic_market_agent/publisher/sfa_ingest_push.py`](../../organic_market_agent/publisher/sfa_ingest_push.py) — `POST https://sfa.nimrod.bio/api/v1/ingest`, HMAC-SHA256 signed, into the uPress MySQL read-mirror. Schema: [`documentation/03-data-and-schema/sfa-mysql-mirror.md`](../../documentation/03-data-and-schema/sfa-mysql-mirror.md).
- **Durability caveat (open follow-up):** the home-server Postgres is at head 034 (no crop-book schema), so the daily cron cannot maintain crop data — crop data is currently re-pushed manually from the Mac (head 057). Canonical pipeline alignment (server DB upgrade) is tracked in the S003 incident artifact.
- **SUPERSEDED (historical record only — do NOT treat as current):** the WordPress + WP REST API + mu-plugin delivery on `www.nimrod.bio` (S002 / M10 era, server `s887`). The www tier was severed 2026-05-28 (env + code + cron). Runbooks `UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`, `WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`, `PUBLISH_CHECKLIST.md`, `docs/UPRESS_WORDPRESS_STANDARD_v2.md`, and code `publisher/{wp_upload,ftps_upload,upload_dispatch,static_upload}.py` describe that retired tier — kept for audit, reviving requires a new DECISION. The 2026-04 production-data-parity sign-offs (Team 10/50/190 reports) belong to this superseded www tier.

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
