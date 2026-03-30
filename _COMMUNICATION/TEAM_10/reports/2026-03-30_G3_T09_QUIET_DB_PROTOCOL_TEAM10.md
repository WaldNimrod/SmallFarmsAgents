# Team 10 — G3 T09 quiet-DB protocol (regression counts)

**Date:** 2026-03-30  
**See also:** Full pack in `2026-03-30_G3_REMEDIATION_EXECUTION_PACK_TEAM10.md` (Phase C).

## Why T09 drifted

[`QA_MANDATE_G3.md`](../../TEAM_50/QA_MANDATE_G3.md) T09 compares absolute counts on `raw_assets` and `raw_extracted_items`. The M3 normalizer **does not insert** into those tables. Count changes during a “normalizer-only” window imply **parallel ingestion**, **cron**, or a **baseline taken at the wrong time**.

## Protocol

1. Use an **isolated QA database** (or ensure **no other writer**).  
2. Execute the T09 `UNION ALL` query; **save output** as `t09_baseline.txt` with timestamp.  
3. Perform **only** the G3 step under test (e.g. one `run_normalizer` pass).  
4. Run T09 again; save as `t09_after.txt`.  
5. If **ingestion** is part of the test narrative, capture baseline **before** ingestion and **document expected row growth** on M2 tables.

## Pass interpretation

- **Catalog tables** (`measurement_units`, `products`, `sources`): should be **unchanged** during normalizer-only G3.  
- **M2 tables**: may change **only** when ingestion is explicitly in scope; otherwise investigate concurrency.
