# Team 50 — Gate G2 review request (M2 Collection Layer)

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**Subject:** Request formal sign-off for **Gate G2** — M2 Collection Layer

## Scope

Validate implementation against:

- `_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md`
- `docs/PIPELINE_ALGORITHMS_HE.md` (supporting)

## Evidence package

Primary report (test output, CLI output, DB counts, dedup notes, deviations):

- `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_COMPLETE_TEAM10.md`

## Suggested QA checks

1. `pytest tests/test_collectors.py tests/test_parsers.py -v` — all PASS (8+ tests per file).
2. `pytest tests/test_db_health.py -v` — all PASS on a migrated + seeded database.
3. `python -m organic_market_agent.scheduler.run_ingestion --run-type manual` — non-fatal per-source failures; `raw_extracted_items` population; checksum dedup on re-run.
4. Confirm `log_entries` receives ERROR rows on failed fetches / parser failures (Team 10 onboarding requirement).

## Outcome requested

Written **PASS / FAIL** for Gate G2 with findings table, or list of blocking defects referencing paths and acceptance criteria.

If G1 sign-off is not yet on file under `TEAM_50/reports/`, please record that dependency explicitly in your response.

---

## Canonical QA outcome (Team 50)

**Gate G2 review result:** [_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md](./2026-03-30_QA_G2_TEAM50.md) — **FAIL / BLOCKED** (G1 prerequisite not satisfied; T02–T09 independent evidence gaps per that report).

**Supplemental evidence (Team 10, post-review):** [_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md](../../TEAM_10/reports/2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md) — verbatim T01–T09 captures for re-validation once G1 is open.
