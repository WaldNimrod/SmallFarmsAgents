# Team 100 — T06 dedup pass criteria: clarification request (from Team 10)

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**To:** Team 100 (Architecture)  
**Subject:** [`QA_MANDATE_G2.md`](../TEAM_50/QA_MANDATE_G2.md) **T06** vs live multi-source ingestion

## Issue

T06 pass criteria require, for the **second** `ingestion_runs.id` (`MAX(id)`):

1. `new_assets = 0` (no new `raw_assets` rows tied to that run’s `source_fetch_runs`), and  
2. **All** `source_fetch_runs.status = 'skipped'` for that run.

On **live** HTTP, any source whose response **bytes change** between runs produces a **new checksum**, so the collector correctly creates a **new** `RawAsset` and marks the fetch **`success`** — not `skipped`. Therefore strict T06 can **fail** even when checksum dedup is implemented correctly for **unchanged** payloads.

Team 50 flagged this tension against Team 10’s second-run CLI summary (`succeeded` counts only new successful fetches; **`skipped` is now also printed** in the CLI per Team 10 observability update).

## Request

Please either:

1. **Amend** `QA_MANDATE_G2.md` T06 to a criterion achievable on live internet (e.g. dedup verified on a **defined stable subset**, mock HTTP fixture, or “new_assets = 0 for sources whose payload hash unchanged”), **or**  
2. **Document** that T06 is **environmental** (requires frozen/mocked responses) and must be run on a designated QA fixture DB, **or**  
3. Confirm **strict** T06 as-is and accept that G2 evidence must use **non-live** or **single-source** controlled endpoints.

## References

- Team 50 G2 report: `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md` (T06 discussion)  
- QA mandate: `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` § T06  
- Evidence appendix (SQL truth): `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md`
