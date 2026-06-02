# QA re-review request — G-V1.1 (post-remediation)

**Date:** 2026-04-09  
**From:** Team 10  
**To:** Team 50 (QA)  
**Prior report:** QA-RPT-20260405-G-V1-1 (`_COMMUNICATION/TEAM_50/reports/2026-04-05_GATE_G_V1_1_REPORT_TEAM50.md`)  
**Remediation map:** `_COMMUNICATION/TEAM_10/reports/2026-04-09_V1_1_QA_FINDINGS_REMEDIATION_TEAM10.md`

## Preconditions for certified re-run

Team 50 should re-run the mandate **only when all** of the following hold:

1. **Python 3.11+** interpreter (project `requires-python >=3.11`; `.python-version` = `3.11`).
2. **PostgreSQL reachable** at `DATABASE_URL` (not connection refused); `alembic current` shows **073**; `organic_market_agent.db.check` passes.
3. **Completion package** status **COMPLETE** (Phase B/E + A2 export + matrices evidence); **Team 190** completion-package **PASS** on final v1.1 package.
4. **WordPress:** M9C blog draft at slug `farm-not-profitable` (operator action per A4).

## Remediation specified by Team 10 (apply in Agent mode if not yet merged)

The following are **tracked** in `_COMMUNICATION/TEAM_10/reports/2026-04-09_V1_1_QA_FINDINGS_REMEDIATION_TEAM10.md`. Do not treat as done until present on `main` / release branch.

- **T01 (no-DB):** `tests/conftest.py` — `require_postgres` / `postgres_reachable`; `tests/test_db_health.py` — skip entire module when DB down; `test_t14_runs_list_shows_manager_columns` — depend on `require_postgres` (no false failures when Postgres is off).
- **T02–T03, T06–T07, T11:** `scripts/sql/g_v1_1_t*.sql` — copy from LOD400 §A2.3 / §A1 / basket tier distribution (operator paste + evidence).
- **T08–T10:** `scripts/sql/g_v1_1_c1_eggs_matrix.sql`, `g_v1_1_c2_passion_fruit_audit.sql`, `g_v1_1_c3_blueberries_audit.sql` — same queries as LOD400 §C1.1–C3.1 with **`s.name AS source_name`** (schema uses `sources.name`, not `name_he`).
- **T14:** Vision block paragraph with link to `https://nimrod.bio/blog/farm-not-profitable/` in `organic_market_agent/publisher/templates/public_report_body.html`.
- **Environment pin:** repo-root `.python-version` → `3.11` (pyenv).
- **CHANGELOG:** `[Unreleased]` entry for this remediation wave.

## Requested QA actions

1. Re-execute **T01–T16** per `QA_MANDATE_G_V1_1.md` and Team 100 briefing §0.
2. Replace gate narrative with a **new dated** Team 50 report if outcome changes.
3. Unblock `2026-03-30_V1_1_QA_REQUEST_TEAM10.md` only after **PASS** on completion preconditions + mandate.

**[USER ACTION REQUIRED]** — Nimrod: Postgres + Phase B/E + WP draft + Team 190 sign-off before certified QA.
