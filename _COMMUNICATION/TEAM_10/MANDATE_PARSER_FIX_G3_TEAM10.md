# ~~Mandate — Team 10: Parser Fix + G3 Data Re-run~~ [SUPERSEDED]

> **SUPERSEDED — 2026-03-30**
> All code fixes described in this document (Fixes 1–4) have been applied directly
> by Team 100 to the codebase. This document is kept as an audit trail only.
>
> **Active mandate for Team 10:** `MANDATE_PARSER_GUARD_REINGESTION_G3_TEAM10.md`

---
**From:** Team 100 (Architecture)
**Date:** 2026-03-30
**Priority:** BLOCKING — Gate G3 requires at least 1 row in normalized_observations
**Context:** G3 QA found 0 resolved observations. Root cause: parsers emit rows with raw_price_text=None.

---

## Root Cause Analysis

Team 100 inspected the 1635 unresolvable items in the DB. Finding:

```
all 1635 items: raw_price_text = NULL
```

Two bugs in the parsers:

### Bug 1: `simple_product_grid._try_list` always yields raw_price_text=None

```python
# CURRENT (broken) — in _try_list:
items.append(
    RawItem(
        raw_product_name=text[:200],
        raw_price_text=None,    # ← never populated
        ...
    )
)
```

`_try_list` extracts every `<div>/<li>/<article>` containing any digit (phone numbers,
navigation, dates...) as "product names" with no price. This produces 100% garbage rows
that will always fail normalization at `price_parser`.

### Bug 2: `easyfarm_catalog` does not filter price-less rows

```python
# CURRENT (broken):
items.append(
    RawItem(
        raw_product_name=name_el.get_text(...) if name_el else None,
        raw_price_text=price_el.get_text(...) if price_el else None,  # can be None
        ...
    )
)
```

If no price element is found in a row, the item is still saved with `raw_price_text=None`.

---

## Fix 1: `organic_market_agent/parsers/simple_product_grid.py`

Replace `_try_list` with a version that requires identifiable name AND price elements.
Items without both are silently skipped — they are noise, not products.

```python
def _try_list(self, soup: BeautifulSoup) -> list[RawItem]:
    """Fallback for div/li/article based product listings.

    Requires both a name element and a price element per row.
    Rows missing either are skipped — they are page noise, not products.
    """
    items: list[RawItem] = []
    for el in soup.find_all(["li", "div", "article"]):
        name_el = el.select_one(
            ".name, .title, .product-name, h3, h4, "
            "[class*='name'], [class*='title'], [class*='product']"
        )
        price_el = el.select_one(
            ".price, [class*='price'], [class*='cost'], "
            "span.amount, .item-price"
        )
        if name_el is None or price_el is None:
            continue

        name_text = name_el.get_text(strip=True)
        price_text = price_el.get_text(strip=True)

        if not name_text or not self._PRICE_RE.search(price_text):
            continue

        items.append(
            RawItem(
                raw_product_name=name_text[:200],
                raw_price_text=price_text[:50],
                raw_unit_text=None,
                raw_quantity_text=None,
                raw_payload_json={"raw_name": name_text, "raw_price": price_text},
            )
        )
    return items
```

---

## Fix 2: `organic_market_agent/parsers/easyfarm_catalog.py`

Skip rows where name or price could not be extracted:

```python
    for row in rows:
        name_el = row.select_one(self._selectors["name"])
        price_el = row.select_one(self._selectors["price"])
        unit_el = row.select_one(self._selectors["unit"])
        qty_el = row.select_one(self._selectors["quantity"])

        raw_product_name = name_el.get_text(strip=True) if name_el else None
        raw_price_text = price_el.get_text(strip=True) if price_el else None

        # Skip rows with no product name or no price — they are extraction failures.
        if not raw_product_name or not raw_price_text:
            continue

        items.append(
            RawItem(
                raw_product_name=raw_product_name,
                raw_price_text=raw_price_text,
                raw_unit_text=unit_el.get_text(strip=True) if unit_el else None,
                raw_quantity_text=qty_el.get_text(strip=True) if qty_el else None,
                raw_payload_json={},
            )
        )
```

---

## Fix 3: `organic_market_agent/normalizer/engine.py`

Add defensive truncation of `unresolvable_reason` before writing to DB.
The column is now TEXT (no hard limit), but long strings degrade admin UI readability.
Cap at 500 characters:

```python
        if ctx.stage_failed in BLOCKING_STAGES:
            item.extraction_status = "unresolvable"
            item.unresolvable_reason = (ctx.unresolvable_reason or "")[:500]
            counts["unresolvable"] += 1
            continue

        if ctx.product_id is None or ctx.price_amount is None or ctx.display_unit_id is None:
            item.extraction_status = "unresolvable"
            item.unresolvable_reason = (
                ctx.unresolvable_reason or "missing product_id, price, or display_unit after stages"
            )[:500]
            counts["unresolvable"] += 1
            continue
```

---

## Fix 4: `tests/test_normalizer.py` — fix test_normalizer_engine_resolves_one_row

The current skip condition requires a source-scoped alias (`source_id IS NOT NULL`).
All seed aliases are global (`source_id=NULL`). Fix the skip to use any active alias:

```python
def test_normalizer_engine_resolves_one_row(db_session):
    # Use any active alias — global or source-scoped.
    pa = db_session.scalar(
        sa.select(ProductAlias)
        .where(ProductAlias.is_active.is_(True))
        .limit(1)
    )
    if pa is None:
        pytest.skip("No product aliases in DB for integration test")

    # If alias is global (source_id=None), pick any active source.
    source_id = pa.source_id
    if source_id is None:
        source_id = db_session.scalar(
            sa.select(Source.id).where(Source.is_active.is_(True)).limit(1)
        )
    if source_id is None:
        pytest.skip("No active source in DB")

    np_id = db_session.scalar(
        sa.select(NormalizerProfile.id).where(NormalizerProfile.source_id == source_id)
    )
    ir = IngestionRun(run_type="manual", triggered_by="test", sources_total=1)
    db_session.add(ir)
    db_session.flush()
    sfr = SourceFetchRun(
        ingestion_run_id=ir.id,
        source_id=source_id,
        status="success",
    )
    db_session.add(sfr)
    db_session.flush()
    checksum = uuid.uuid4().hex
    ra = RawAsset(
        source_id=source_id,
        source_fetch_run_id=sfr.id,
        storage_path=f"test/normalizer_engine_{checksum[:8]}.bin",
        file_type="html",
        checksum_sha256=checksum,
        bytes_size=10,
    )
    db_session.add(ra)
    db_session.flush()
    rei = RawExtractedItem(
        source_fetch_run_id=sfr.id,
        raw_asset_id=ra.id,
        normalizer_profile_id=np_id,
        raw_product_name=pa.alias_text,
        raw_price_text="9.99",
        raw_unit_text="kg",
        extraction_status="extracted",
    )
    db_session.add(rei)
    db_session.commit()

    eng = NormalizerEngine()
    counts = eng.run(db_session, ingestion_run_id=ir.id)
    assert counts["resolved"] >= 1
    db_session.refresh(rei)
    assert rei.extraction_status == "normalized"
```

---

## Step 5: Re-run Ingestion for EasyFarm Sources

After applying the parser fixes, re-ingest the EasyFarm sources. These now have
`selector_profile` JSONB populated (from migration 007). The parsers must read this
from DB via `selector_overrides`.

Check that `run_ingestion.py` (or the collector) passes `selector_profile` from
`source_fetch_profiles` to the EasyFarm parser. If not, add this wiring.

Then run:
```bash
python -m organic_market_agent run_ingestion --normalize
```

Verify after the run:
```sql
SELECT COUNT(*) FROM normalized_observations;
-- Expected: > 0
```

If EasyFarm sources still produce 0 items (live DOM may differ), contact Team 100
with a sample of the fetched HTML so selectors can be updated.

---

## Verification

```bash
# Full test suite — all tests must pass (0 failures, ≤1 skipped)
python3.11 -m pytest tests/ -q

# Verify parser fixes don't break existing tests:
python3.11 -m pytest tests/test_parsers.py -v

# Verify normalizer test:
python3.11 -m pytest tests/test_normalizer.py -v
```

Expected:
- `tests/test_normalizer.py::test_normalizer_engine_resolves_one_row` → PASSED (not skipped)
- All 45 tests pass, 0 skipped

---

## Submission

File your completion report at:
`_COMMUNICATION/TEAM_10/reports/2026-03-30_PARSER_FIX_G3_COMPLETE_TEAM10.md`

Include:
- Confirmation of all 4 fixes applied
- `pytest tests/` output (all pass)
- `run_normalizer` output after re-ingestion (resolved count > 0)
- `SELECT COUNT(*) FROM normalized_observations;` result
