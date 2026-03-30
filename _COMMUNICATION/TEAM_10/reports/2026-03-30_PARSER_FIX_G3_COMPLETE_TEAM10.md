# Team 10 — Parser guard + G3 re-ingestion mandate (completion)

**Date:** 2026-03-30  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_PARSER_GUARD_REINGESTION_G3_TEAM10.md`

## 1. Task 1 — `parsers/engine.py` guard (confirmed)

Incomplete parser rows (missing `raw_product_name` or `raw_price_text`) are filtered before `RawExtractedItem` insert; a warning logs how many were skipped; the info line includes `skipped_count`.

Reference: [`organic_market_agent/parsers/engine.py`](../../organic_market_agent/parsers/engine.py) — block building `valid_items`, `skipped_count`, `db_items` from `valid_items`, and updated `logger.info`.

## 2. Task 2 — Re-ingestion commands (operator)

Per mandate, run on a host with `.env`, DB at Alembic head (≥008 per mandate), and network:

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
source .venv/bin/activate  # if used
set -a && source .env && set +a

python3.11 -m organic_market_agent run_ingestion --source-code SRC002 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC004 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC005 --normalize
python3.11 -m organic_market_agent run_ingestion --source-code SRC006 --normalize
```

**CLI wiring:** `python -m organic_market_agent run_ingestion` is now registered in [`organic_market_agent/__main__.py`](../../organic_market_agent/__main__.py) (delegates to `scheduler.run_ingestion`).

**Results (this session):** Not executed here — no PostgreSQL available in the automation environment. **Team 10 / operator:** paste the four lines below into this section after running the commands:

```
SRC002: IngestionRun #N: ... | Normalizer: resolved=X unresolvable=Y
SRC004: ...
SRC005: ...
SRC006: ...
```

**Selector drift:** If all four show `resolved=0`, follow mandate §Task 2 (save raw HTML, inspect, file `_COMMUNICATION/TEAM_100/reports/` selector update request). **Do not block G3** on that outcome — document as known issue per mandate.

## 3. Task 3 — DB counts (operator)

```bash
set -a && source .env && set +a
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

**Paste when run:**

```
normalized_observations: N
still extracted: 0
unresolvable: M
```

Pass: `normalized_observations > 0` and `still extracted = 0`.

## 4. Task 4 — Pytest

**Target:** `46 passed, 0 skipped, 0 failures` (per mandate; requires PostgreSQL for `tests/test_db_health.py` and for normalizer integration tests not to skip).

**This session:** Full `pytest tests/` could not reach 46/0/0 without a live DB on `DATABASE_URL`.

## 5. Request to Team 50

Please execute **`QA_MANDATE_G3_RERUN.md`** (or current Gate G3 QA mandate) against this branch after Tasks 2–4 evidence is attached above.
