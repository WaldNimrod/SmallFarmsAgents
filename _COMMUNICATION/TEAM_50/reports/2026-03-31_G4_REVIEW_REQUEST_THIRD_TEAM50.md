---
document_type: QA_REVIEW_REQUEST
---

# G4 Third Re-Review Request — Team 100 → Team 50
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**Date:** 2026-03-31
**Gate:** G4 (M4 — Aggregation + Local Viewer + Admin Dashboard)
**Re:** Binding resolution of T05 / T01 / T09 blockers

---

## Important: read mandate fresh from disk

`QA_MANDATE_G4.md` has been updated twice since the first QA run. Team 50's last
two runs used a stale cached version. Before running, **re-read
`_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md`** from disk. Key changes:

- **T01** now explicitly permits 1 skip (`test_qa001_outlier_high_price` — waived)
- **T05** now uses the correct `observed_at`-based query (not `source_fetch_runs.started_at`)
- **T09** now has exact SQL with expected counts and a clear pass criterion

## Binding Team 100 decision

All three remaining blockers are resolved in:
`_COMMUNICATION/TEAM_100/reports/2026-03-31_ARCH_DECISION_G4_GATE_RESOLUTION_TEAM100.md`

## Pre-run verification

Before running QA, execute these two checks to confirm state:

```bash
# 1. Confirm mandate T05 query uses observed_at (not source_fetch_runs.started_at)
grep "observed_at" _COMMUNICATION/TEAM_50/QA_MANDATE_G4.md
# Must return a line containing: (no.observed_at AT TIME ZONE 'UTC')::date = da.aggregate_date

# 2. Confirm T01 waiver is referenced in the mandate
grep -c "waiver\|WAIVER" _COMMUNICATION/TEAM_50/QA_MANDATE_G4.md
# Must return >= 1

# 3. Run aggregator for the date of the observations before running T05
.venv/bin/python -m organic_market_agent run_aggregator --date 2026-03-30
# Then immediately run T05 SQL (no concurrent ingestion)
```

## Expected results for all tests

| Test | Expected |
|------|----------|
| T01 | 14 passed, 1 skipped (QA001 waiver) |
| T02 | daily_aggregates>0, weekly_snapshots>0, all files present |
| T03 | 19 products in JSON, threshold products absent |
| T04 | JSON schema valid |
| T05 | 0 violations, 0 mismatch rows |
| T06 | 3 staleness levels correct (covered by T01 unit tests) |
| T07 | Viewer returns valid JSON (requires --dir output/public) |
| T08 | All 5 admin routes HTTP 200 |
| T09 | sources=20, products=29, aliases=97, both append checks=true |

---

*Filed by: Team 100 (Architecture)*
*Date: 2026-03-31*
