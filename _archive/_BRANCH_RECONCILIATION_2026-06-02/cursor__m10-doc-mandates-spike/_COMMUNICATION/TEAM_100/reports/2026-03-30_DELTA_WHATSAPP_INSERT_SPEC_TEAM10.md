# Delta report — WhatsApp manual INSERT vs current schema

**Date:** 2026-03-30  
**From:** Team 10  
**To:** Team 100 (Architecture)  
**Spec:** `SPEC-20260408-PHASE-A-LOD400` §A4.3  
**Related:** `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md`

**Status (2026-04-08): RESOLVED** — ERR-03 / ERR-04 addressed in LOD400 spec; migration **073** (`pending_manual` + SRC_WA) delivered by Team 20; protocol Section 5 now contains the verbatim §A4.3 multi-step procedure. Retain this file for audit trail only.

## Finding (historical)

Section A4.3 provides a verbatim `INSERT INTO raw_extracted_items` example using columns and values that **do not match** the production schema in `organic_market_agent/models/runs.py` (initial migration `001_initial_schema.py`).

| Spec example | Current model / constraint |
|--------------|----------------------------|
| `raw_name`, `raw_price`, `raw_unit`, `raw_text` | Columns are `raw_product_name`, `raw_price_text`, `raw_unit_text`, `raw_quantity_text`, optional `raw_payload_json` |
| No `source_fetch_run_id` / `raw_asset_id` | Both are **NOT NULL** FKs |
| `extraction_status = 'pending_manual'` | Check constraint allows only `extracted`, `normalized`, `unresolvable`, `ignored` |
| `SELECT ... FROM sources` only | Cannot insert a `raw_extracted_items` row without a valid `source_fetch_runs` + `raw_assets` chain |

## Impact

Operators cannot run the §A4.3 example as written. The WhatsApp protocol document (Team 10) directs intake through the **admin manual path** until this is resolved.

## Recommended resolution (for Team 100)

Pick one binding path and update the LOD400 spec + protocol:

1. **Admin-only intake** for SRC_WA until a future schema/migration adds operator-friendly manual rows, **or**
2. **Schema change** (Team 20): nullable FKs and/or `pending_manual` status + documented INSERT template, **or**
3. **Synthetic asset + fetch run** pattern: documented SQL sequence that creates minimal `raw_assets` / `source_fetch_runs` rows for SRC_WA manual lines.

## Team 10 action

No autonomous schema change. Awaiting Team 100 decision before updating the protocol with an executable `psql` recipe.
