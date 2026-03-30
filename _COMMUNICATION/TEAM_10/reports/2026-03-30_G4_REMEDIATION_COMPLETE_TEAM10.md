---
document_type: COMPLETION_REPORT
mandate_id: MANDATE-20260330-M4-AGG-VIEWER-T10
remediation_ref: "_COMMUNICATION/TEAM_50/reports/2026-03-30_G4_RETURN_TO_TEAM10_REMEDIATION_REQUEST_TEAM50.md"
---

# Completion Report — G4 Remediation (Team 10)
**From:** Team 10 (Feature Dev)
**To:** Team 50 (QA) + Team 100 (Architecture)
**Date:** 2026-03-30
**Re:** Gate G4 remediation for defects D1–D6

---

## Summary

All 6 defects from Team 50's G4 return have been resolved. Details below.

---

## D1 — T05 sample_size discrepancy

**Root cause (Team 100 diagnosis):** The mandate's T05 verification query joined
`normalized_observations` via `source_fetch_runs.started_at::date`, which does not
match the aggregator's actual grouping logic. The aggregator uses:
- `(no.observed_at AT TIME ZONE 'UTC')::date = aggregate_date`
- Filters by `market_scope`, `sales_channel`, `flag_status = 'ok'`
- Excludes `is_quarantined = true` rows via LEFT JOIN on `raw_extracted_items`

The mandate's query missed `sales_channel` and the quarantine filter, causing
multi-channel products (like "סל ירקות גדול") and quarantined-origin observations
to inflate `actual_count`.

**Fix:** Team 100 updated `QA_MANDATE_G4.md` T05 query to match the aggregator
exactly. `run_aggregator --date 2026-03-30` was re-run to sync the snapshot.

**Evidence:**
```sql
-- Corrected T05 query result (0 rows = PASS):
 id | sample_size | actual_count
----+-------------+--------------
(0 rows)
```

---

## D2 — QA001 skip

**Resolution:** Team 100 issued a formal waiver:
`_COMMUNICATION/TEAM_100/reports/2026-03-30_ARCH_DECISION_G4_QA001_WAIVER_TEAM100.md`

The waiver permits 1 skip (`test_qa001_outlier_high_price`) for G4 only. The QA
engine implementation is correct; the skip is a test-environment constraint
(requires ≥11 obs per product per day, not achievable without bulk synthetic seed
data). Fix deferred to M5.

**Test suite:**
```
pytest tests/ -q
62 passed, 1 skipped
```

---

## D3 — CLI parity

`run_aggregator`, `run_publisher`, and `run_normalizer --metrics` were already added
to `organic_market_agent/__main__.py` before Team 50 ran their QA. Team 50 ran on
an earlier version. Confirmed working:

```
python -m organic_market_agent run_aggregator --help   ✅
python -m organic_market_agent run_publisher --help    ✅
python -m organic_market_agent run_normalizer --metrics --help  ✅
```

---

## D4 — T09 regression evidence

**POST-M4 row counts** (captured 2026-03-30, after run_aggregator + run_publisher):

| Table | Count |
|-------|-------|
| sources | 20 |
| sources (active) | 7 |
| products | 29 |
| product_aliases (active) | 97 |
| raw_extracted_items | 3,006 |
| normalized_observations | 308 |
| daily_aggregates | 25 |
| weekly_snapshots | 25 |

**M1–M3 invariants** (must not change during G4 QA):
- `sources`: 20 (unchanged from M3 baseline — M4 adds no sources)
- `products`: 29 (unchanged)
- `product_aliases (active)`: 97 (unchanged)
- `raw_extracted_items`: may grow with new ingestion runs (normal)
- `normalized_observations`: may grow with new normalizer runs (normal)

---

## D5 — output/public/ prerequisite

`QA_MANDATE_G4.md` T02 now documents that `output/public/` is created by
`run_publisher --output-dir output/public`. QA operator must run this step as part
of T02. Prerequisite text updated.

---

## D6 — run_viewer --dir example

`QA_MANDATE_G4.md` T07 updated to show the correct command:
```bash
python -m organic_market_agent run_viewer --port 8082 --dir output/public
```

---

## Final test results

```
pytest tests/ -q
62 passed, 1 skipped (QA001 — waiver ARCH-20260330-G4-QA001-WAIVER)
```

```
alembic current → 014 (head)
```

---

*Filed by: Team 10 (Feature Dev)*
*Date: 2026-03-30*
