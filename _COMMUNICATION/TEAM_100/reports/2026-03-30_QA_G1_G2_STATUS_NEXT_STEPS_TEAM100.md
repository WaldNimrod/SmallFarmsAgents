# QA status — G1 / G2 and recommended architecture follow-ups

**Date:** 2026-03-30  
**From:** Team 50 (QA), with **Project Lead (Nimrod)** direction on pacing  
**To:** Team 100 (Architecture)  
**Subject:** Summary for next-step review after validation-host checks and live ingestion evidence

---

## 1. Purpose

Team 100 is asked to **prioritize and decide** open architecture / mandate items so implementation can proceed cleanly while **formal gate paperwork** catches up.

**Project Lead direction (operational):** For **current** validation goals, the executed checks and observed ingestion behavior are **sufficient to allow continued development** (M3 prep, collector/parser hardening, seed fixes). This does **not** remove the need for written gate sign-off, alias seed correction, and mandate clarifications below.

---

## 2. Executive summary

| Area | State (high level) |
|------|---------------------|
| **Stack / G1 validation host** | Team 20 delivered Homebrew **PostgreSQL 15.17** + **Python 3.11.15** handoff: `_COMMUNICATION/TEAM_20/reports/2026-03-30_G1_VALIDATION_ENV_READY_TEAM20.md`. |
| **G1 automated + migration evidence** | On that class of host: `pytest tests/test_db_health.py` **7/7 PASS**; `db.check` **RESULT: PASS**; `alembic downgrade base` → `upgrade head` → `db.check` **PASS**; import sanity **OK**. |
| **G1 data rule (T10)** | SQL check for “every active product has ≥1 active alias” returns **13 products without aliases** (codes include PRD012, PRD014–PRD016, PRD018–PRD024, PRD027–PRD028). This is a **High**-weight failure vs `QA_MANDATE_G1.md` T10 — recommend **seed/migration fix** (Team 20) or **mandate exception** (Team 100) before a clean **G1 PASS**. |
| **G2 unit layer** | `pytest tests/test_collectors.py tests/test_parsers.py` — **20/20 PASS** under Python 3.11. |
| **G2 live ingestion (sample)** | Full manual run completed (~8+ minutes wall time): **`EXIT=0`**, summary line **`status=partial`**, **`succeeded=16`**, **`failed=4`**, **`community_ok=13`** — consistent with external SSL/403 and parser mismatches on some sources, not a hung process. |
| **Formal QA reports on file** | `*_QA_G1_TEAM50.md` is **not** yet present under `_COMMUNICATION/TEAM_50/reports/`; existing `2026-03-30_QA_G2_TEAM50.md` predates G1 open and **blocked** G2 on prerequisite — **ROADMAP / execution mandate** expect a **dated G1 report** when claiming G1 open. |

---

## 3. What Team 50 recommends Team 100 decide next

These items already have partial threads in `_COMMUNICATION/TEAM_100/reports/` or Team 10; Team 50 groups them for **single-queue** handling.

### 3.1 Gate G1 — product alias completeness (T10)

- **Issue:** Mandate T10 expects **zero** rows from the “missing alias” query; current seed leaves **13** active products uncovered.
- **Options:** (a) Team 20 extends seed (preferred for catalog integrity), (b) Team 100 documents intentional catalog exception, (c) adjust mandate if spec changed.

### 3.2 Gate G2 — T06 dedup criteria vs live HTTP

- **Issue:** Strict T06 (“second run: all fetch runs `skipped`, `new_assets = 0`”) conflicts with **changing** remote payloads between runs.
- **Already filed:** `_COMMUNICATION/TEAM_100/reports/2026-03-30_T06_DEDUP_CRITERIA_CLARIFICATION_REQUEST_TEAM10.md`
- **Ask:** Team 100 picks one path: amend mandate, environmental fixture rule, or strict criterion with controlled endpoints.

### 3.3 M2 implementation / seed alignment (Team 10 + Team 20)

- **EasyFarm:** Fetches succeed but **0 rows** extracted on several live pages — selector strategy vs DB-driven `selector_profile` (see Team 10 handoff).
- **SRC018–SRC020:** HTML fetched where JSON parser expected — `fetch_mode` / `entry_url` / parser map alignment (Team 10 completion report and M2 handoff to Team 100).

### 3.4 Environment semantics for other workstations

- **Docker `postgres` in `docker ps`:** Team 20 clarified G1 evidence must use **`DATABASE_URL` to Homebrew**, not a mapped Docker port. Team 100 may add a one-line **architecture note** so QA and onboarding stay aligned.

---

## 4. Suggested sequencing (non-binding)

1. **Team 100** resolves **T06** wording and **T10** expectation (or accepts CONDITIONAL G1 with explicit conditions).  
2. **Team 50** files **`{date}_QA_G1_TEAM50.md`** with PASS or **approved CONDITIONAL PASS** per `MANDATE_QA_EXECUTION_G1_THEN_G2_TEAM50.md`.  
3. **Team 20** applies alias seed fix if that is the chosen path for T10.  
4. **Team 50** re-runs **full** `QA_MANDATE_G2.md` (including second ingestion + T07) and files a **new** `{date}_QA_G2_TEAM50.md` referencing the G1 report.  
5. **Team 10** continues **M3-ready** work in parallel where it does not depend on closed G2 (per Project Lead “continue development” direction).

---

## 5. References (canonical paths)

| Document | Notes |
|----------|--------|
| `_COMMUNICATION/TEAM_50/MANDATE_QA_EXECUTION_G1_THEN_G2_TEAM50.md` | Order: G1 evidence first, then G2. |
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` | T01–T13 definitions. |
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` | T01–T12 definitions. |
| `_COMMUNICATION/TEAM_20/reports/2026-03-30_G1_VALIDATION_ENV_READY_TEAM20.md` | Validation host recipe. |
| `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_COMPLETE_TEAM10.md` | M2 implementer evidence. |
| `_COMMUNICATION/TEAM_100/reports/2026-03-30_M2_COMPLETION_HANDOFF_TEAM100.md` | Team 10 → Team 100 decision queue. |
| `_COMMUNICATION/TEAM_100/reports/2026-03-30_T06_DEDUP_CRITERIA_CLARIFICATION_REQUEST_TEAM10.md` | T06 clarification request. |
| `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md` | Earlier G2 assessment (prerequisite + static checks). |

---

## 6. Acceptance note (Team 100)

Please record **decisions** (and any mandate edits) in `_COMMUNICATION/TEAM_100/reports/` so Team 50 can score gates without ad hoc interpretation.

**No user action required** in this document beyond Team 100 review and Team 20/10 execution of chosen fixes.
