# WhatsApp data submission protocol

**Status:** Active (M9C / v1.1.0 Phase A)  
**Owner:** Team 10 (infrastructure); Team 80 (blog content separately)  
**Binding spec:** `SPEC-20260408-PHASE-A-LOD400` §A4 (`_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`)

---

## Section 1: Purpose

This protocol defines how community price observations reach the OrganicMarketAgent pipeline when farmers submit data via WhatsApp before an in-page submission form exists. It keeps intake consistent, protects privacy, and ensures only catalog-backed products enter normalization.

---

## Section 2: Submission message format

Required fields a farmer must provide in a WhatsApp message:

```
Mandatory:
- Product name (Hebrew, from catalog)
- Price (number in ILS)
- Unit (kg / unit / bunch / pack)
- Your farm/market name (for operator validation, NOT published)
- Date of price (today or up to 7 days ago)

Optional:
- Quantity (if selling in bulk, e.g., "5 kg for ₪30")
- Notes (quality grade, variety)
```

---

## Section 3: Operator intake steps

1. Receive WhatsApp message.
2. Validate format (all mandatory fields present).
3. Match product name to catalog ([`docs/PRODUCT_CATALOG_V1.md`](../../../docs/PRODUCT_CATALOG_V1.md) — canonical names).
4. Open admin UI `/aliases` — confirm product is in catalog, or flag for new product review.
5. Enter data via admin UI manual observation entry, or via the multi-step `psql` procedure in **Section 5** (verbatim LOD400 §A4.3).
6. Confirm source attribution to **SRC_WA** (seeded in migration **073** with `pending_manual` support — see Team 20 completion report).
7. Reply to farmer confirming receipt (optional but encouraged).

---

## Section 4: Pipeline integration path

- WhatsApp rows use `extraction_status = 'pending_manual'` after migration **073** extends `chk_rei_extraction_status`.
- `raw_extracted_items` requires `source_fetch_run_id` and `raw_asset_id` (NOT NULL). Use the **4-step** procedure in Section 5; do not use legacy single-row `INSERT` templates.
- Operator runs `python -m organic_market_agent catalog_renormalize` after batch entry where applicable, then `run_aggregator` and `run_publisher` for the next publish cycle.

---

## Section 5: Privacy rules

- Farm name / operator identity **never** enters `normalized_observations` or published output.
- Only aggregated price statistics are published (per [docs/PRIVACY_POLICY.md](../../../docs/PRIVACY_POLICY.md)).
- Source attribution in published output shows source counts and tiers, not individual farm names.

### Executable operator template (LOD400 §A4.3 — verbatim)

> **Schema note (ERRATA):** `raw_extracted_items` has no `source_id` column and no `raw_name`/`raw_price`/`raw_unit`/`raw_text` columns. The actual columns are `raw_product_name`, `raw_price_text`, `raw_unit_text`, and rows require FK links to `source_fetch_runs` and `raw_assets`. Additionally, `pending_manual` is a new extraction_status value that requires a migration to add it to the `chk_rei_extraction_status` CHECK constraint (included in migration that seeds SRC_WA). Use the corrected multi-step procedure below.

```sql
-- Operator manual entry for a WhatsApp community submission
-- Prerequisites:
--   1. Migration adding SRC_WA source row and 'pending_manual' to extraction_status CHECK must be applied.
--   2. Run via: psql "$DATABASE_URL"
-- Replace <YYYY-MM-DD> with today's date.

-- Step 1: Create a manual ingestion run for this batch
INSERT INTO ingestion_runs (run_type, status, triggered_by, sources_total, sources_succeeded, community_sources_succeeded)
VALUES ('manual', 'completed', 'operator_whatsapp', 1, 1, 1)
RETURNING id;
-- Record the returned id as <RUN_ID>

-- Step 2: Create a source_fetch_run entry for SRC_WA
INSERT INTO source_fetch_runs (ingestion_run_id, source_id, status)
SELECT <RUN_ID>, s.id, 'success'
FROM sources s WHERE s.code = 'SRC_WA'
RETURNING id;
-- Record the returned id as <SFR_ID>

-- Step 3: Create a raw_asset placeholder for the WhatsApp submission
INSERT INTO raw_assets (source_id, source_fetch_run_id, storage_path, file_type, checksum_sha256, bytes_size)
SELECT s.id, <SFR_ID>, 'whatsapp/manual_<YYYY-MM-DD>.txt', 'text', 'manual_entry', 0
FROM sources s WHERE s.code = 'SRC_WA'
RETURNING id;
-- Record the returned id as <ASSET_ID>

-- Step 4: Insert the raw_extracted_item with correct column names
INSERT INTO raw_extracted_items (
    source_fetch_run_id,
    raw_asset_id,
    raw_product_name,
    raw_price_text,
    raw_unit_text,
    extraction_status
)
VALUES (
    <SFR_ID>,
    <ASSET_ID>,
    'עגבניות שרי',           -- product name from WhatsApp (Hebrew, from catalog)
    '12.50',                   -- price in ILS (VARCHAR, not numeric)
    'ק"ג',                     -- unit as received
    'pending_manual'           -- requires 'pending_manual' in CHECK constraint
);

-- Verify the row was inserted
SELECT id, raw_product_name, raw_price_text, raw_unit_text, extraction_status
FROM raw_extracted_items
ORDER BY created_at DESC
LIMIT 1;
```

After batch entry: run `python -m organic_market_agent catalog_renormalize` to process all `pending_manual` rows.

---

## Section 6: Data validation criteria

- Price must be > 0 and < ₪1000/kg (flag outliers for review).
- Date must be within last 14 days.
- Product must exist in catalog (no new products via WhatsApp without Team 100 approval).
- Duplicate detection: same farm + same product + same date → reject duplicate.

---

## Section 7: Escalation

- Ambiguous product name → flag in `/catalog/pending-aliases`.
- Price seems very unusual → flag as `qa_flags` entry.
- Request for new product → escalate to Team 100 (`_COMMUNICATION/TEAM_100/reports/`).
