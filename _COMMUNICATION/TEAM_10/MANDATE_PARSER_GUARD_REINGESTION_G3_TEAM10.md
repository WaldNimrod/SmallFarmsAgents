# Mandate — Team 10: Parser Guard + Re-ingestion for G3
**From:** Team 100 (Architecture)
**Date:** 2026-03-30
**Priority:** BLOCKING — Gate G3 requires normalized_observations > 0
**Prerequisite:** Migration 008 applied (Alembic v008). Confirm with `alembic current`.

---

## Context — What Team 100 Already Applied

The following code fixes are **already in the codebase**. Do NOT re-implement them.
Verify they exist and move straight to the tasks below.

| File | Fix |
|------|-----|
| `parsers/simple_product_grid.py` | `_try_list` requires distinct name+price elements; skips noise |
| `parsers/easyfarm_catalog.py` | Skips rows where `raw_price_text` is None |
| `normalizer/engine.py` | `unresolvable_reason` capped at 500 chars |
| `tests/test_normalizer.py` | `test_normalizer_engine_resolves_one_row` uses any active alias |
| `tests/test_parsers.py` | `_try_list` test updated to expect `[]` for unstructured HTML |

Quick verification:
```bash
python3.11 -m pytest tests/ -q
# Expected: 46 passed, 0 skipped
```

---

## Task 1 — Add Defensive Guard in `parsers/engine.py`

**File:** `organic_market_agent/parsers/engine.py`

The `ParserEngine` currently writes every item the parser returns to DB, even if
`raw_price_text` or `raw_product_name` is None. Add a guard before the DB write
to skip incomplete items and log a warning:

**Locate this block** (around line 91):

```python
        db_items: list[RawExtractedItem] = [
            RawExtractedItem(
                source_fetch_run_id=raw_asset.source_fetch_run_id,
                ...
            )
            for item in raw_items
        ]
```

**Replace it with:**

```python
        valid_items = [
            item for item in raw_items
            if item.raw_product_name and item.raw_price_text
        ]
        skipped_count = len(raw_items) - len(valid_items)
        if skipped_count:
            logger.warning(
                "ParserEngine: skipped %d incomplete items (no name or price) for source=%s",
                skipped_count,
                source.code,
            )

        db_items: list[RawExtractedItem] = [
            RawExtractedItem(
                source_fetch_run_id=raw_asset.source_fetch_run_id,
                raw_asset_id=raw_asset.id,
                normalizer_profile_id=np_row,
                raw_product_name=item.raw_product_name,
                raw_price_text=item.raw_price_text,
                raw_unit_text=item.raw_unit_text,
                raw_quantity_text=item.raw_quantity_text,
                raw_payload_json=item.raw_payload_json,
                extraction_status="extracted",
            )
            for item in valid_items
        ]
```

After the change, update the log line at the end of the method to reflect `valid_items`:

```python
        logger.info(
            "ParserEngine: wrote %d raw_extracted_items for source=%s (%d skipped)",
            len(db_items),
            source.code,
            skipped_count,
        )
        return len(db_items)
```

---

## Task 2 — Re-run Ingestion for EasyFarm Sources

The EasyFarm sources (SRC002, SRC004, SRC005, SRC006) now have `selector_profile`
populated in DB (from migration 007). The wiring to pass these selectors to the
parser already exists in `run_ingestion.py` → `parsers/engine.py` → `EasyFarmCatalogParser`.

Run each source and normalize in the same pass:

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
source .env

python3.11 -m organic_market_agent run_ingestion --source-code SRC002 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC004 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC005 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC006 --normalize
```

After each run, inspect the output line:
```
IngestionRun #N: status=completed succeeded=1 failed=0 skipped=0 community_ok=1
Normalizer: resolved=X unresolvable=Y skipped=0
```

**If `resolved=0` for all four sources** — the live DOM has changed and selectors
no longer match. In that case:
1. Run the ingestion without `--normalize` to save the raw HTML
2. Inspect the raw file stored in `raw_files/`
3. Open the HTML and identify the correct CSS selectors for product rows, names, and prices
4. File a report to Team 100 at `_COMMUNICATION/TEAM_100/reports/` requesting a selector update
5. Do NOT block the G3 report — document the selector drift as a known issue

**If `resolved > 0`** — continue to Task 3.

---

## Task 3 — Verify normalized_observations

```bash
source .env
python3.11 -c "
from organic_market_agent.db.session import get_session
from sqlalchemy import text
with get_session() as s:
    n = s.execute(text('SELECT COUNT(*) FROM normalized_observations')).scalar()
    print(f'normalized_observations: {n}')
    e = s.execute(text(\"SELECT COUNT(*) FROM raw_extracted_items WHERE extraction_status='extracted'\")).scalar()
    print(f'still extracted (unprocessed): {e}')
    u = s.execute(text(\"SELECT COUNT(*) FROM raw_extracted_items WHERE extraction_status='unresolvable'\")).scalar()
    print(f'unresolvable: {u}')
"
```

**Pass criterion:**
- `normalized_observations > 0`
- `still extracted = 0` (all items processed)

---

## Task 4 — Run Full Test Suite

```bash
python3.11 -m pytest tests/ -q
```

**Pass criterion:** `46 passed, 0 skipped, 0 failures`

---

## Completion Report

File at: `_COMMUNICATION/TEAM_10/reports/2026-03-30_PARSER_FIX_G3_COMPLETE_TEAM10.md`

Include:

1. **Task 1 confirmed** — `parsers/engine.py` guard added (paste the changed lines)
2. **Task 2 — ingestion results** — paste output for each of the 4 sources:
   ```
   SRC002: IngestionRun #N: ... | Normalizer: resolved=X unresolvable=Y
   SRC004: ...
   SRC005: ...
   SRC006: ...
   ```
   If selector drift occurred: document which sources and note "selector drift — filed to Team 100"
3. **Task 3 — DB counts:**
   ```
   normalized_observations: N
   still extracted: 0
   unresolvable: M
   ```
4. **Task 4 — pytest:** `46 passed, 0 skipped`
5. **Request to Team 50:** "Please execute QA_MANDATE_G3_RERUN.md"
