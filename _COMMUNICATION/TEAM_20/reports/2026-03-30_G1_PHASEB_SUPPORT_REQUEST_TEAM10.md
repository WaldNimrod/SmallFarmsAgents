# Team 20 — G1 Phase B support request (from Team 10)

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**To:** Team 20 (Infrastructure)  
**Subject:** Unblock **Gate G1** so Team 50 can file formal G1 QA sign-off

## Context

Team 50 issued [`_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md`](../TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md): **Gate G2 is BLOCKED** because **Gate G1 is not formally open** — there is no `*_QA_G1_TEAM50.md` (or equivalent) under `_COMMUNICATION/TEAM_50/reports/`.

M2 implementation is complete from Team 10’s side, but **process order** requires G1 before G2 per [`QA_MANDATE_G2.md`](../TEAM_50/QA_MANDATE_G2.md) prerequisites and [`ROADMAP.md`](../ROADMAP.md).

## Requested actions (Team 20)

1. **Confirm** M1 Phase A deliverables remain valid for **G1 Phase B** validation per [`QA_MANDATE_G1.md`](../TEAM_50/QA_MANDATE_G1.md) (migrations, seed, `db.check`, `tests/test_db_health.py`).

2. **Provide or document** a **compliant validation environment** for Team 50 (and for reproducible G2 evidence) with:
   - **Python 3.11+** (mandate reminder in G1/G2 QA mandates)
   - **PostgreSQL 15+** — **direct install** per stack lock (Docker was used only for ephemeral engineering evidence; QA prefers parity with production setup)
   - Working **`DATABASE_URL`** and **`RAW_FILES_ROOT`**
   - `alembic upgrade head` on a clean database + seed revisions **002–005**

3. **Coordinate** with **Team 50** so they can execute Phase B and file:
   - `_COMMUNICATION/TEAM_50/reports/{date}_QA_G1_TEAM50.md` with **PASS** (or approved **CONDITIONAL PASS**).

## Out of scope for Team 20 (informational)

- Team 10 does **not** ask Team 20 to change application feature code for this request.
- Seed/profile alignment for benchmark JSON vs HTML (if any) remains a **data/architecture** topic; flag to Team 100 if schema or seed corrections are needed.

## References

- Team 50 G2 QA report: `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md`
- Roadmap M1 / G1: `_COMMUNICATION/ROADMAP.md`
