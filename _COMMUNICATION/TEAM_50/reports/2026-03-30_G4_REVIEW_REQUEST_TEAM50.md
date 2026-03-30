# G4 review request — Team 50 (M4 aggregation, publish, admin)

**Date:** 2026-03-30  
**From:** Team 10  
**Gate:** G4 (per `_COMMUNICATION/ROADMAP.md` — align with M4 / aggregation & local viewer mandate)  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md`

## Summary

Team 10 requests **QA sign-off for M4**: `AggregatorEngine`, `QAEngine`, local `PublishEngine` (JSON/HTML/manifest), `run_viewer`, read-only Flask admin (`run_admin`), and tests `tests/test_aggregator.py` (≥8) + `tests/test_publisher_local.py` (≥6).

## Implementation reference

- Completion report: `_COMMUNICATION/TEAM_10/reports/2026-03-30_M4_IMPLEMENTATION_COMPLETE_TEAM10.md`
- Tests: `pytest tests/` (see report for commands)

## Ask

Please run the **mandate checklist** against the codebase, record **pass/fail per requirement**, and file a dated QA report under `_COMMUNICATION/TEAM_50/reports/`. Flag any **blockers for G4**.

## Known test caveat

`test_qa001_outlier_high_price` is **skipped** when the database has fewer than **11** active sources (integration data requirement for a stable mean + 3σ outlier). All other M4 tests are expected to pass when PostgreSQL is available.
