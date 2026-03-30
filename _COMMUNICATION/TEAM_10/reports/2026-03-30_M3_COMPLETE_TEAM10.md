# Team 10 — M3 Complete (Gate G3 submission draft)

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**Milestone:** M3 — Normalizer Engine  
**Status:** **Implementation complete** — formal G3 evidence pending prerequisites below.

## Prerequisites for final sign-off (Team 50 / Gate G3)

- [ ] **Gate G2 open** (Team 50 written G2 PASS on file).
- [ ] **Alembic revisions 006 + 007** applied (Team 20 mandate pre-condition per M3 mandate).
- [ ] **PostgreSQL** direct install, Python 3.11+ (per stack lock / QA mandates).

## Implementation reference

- Technical summary: [_COMMUNICATION/TEAM_10/reports/2026-03-30_M3_IMPLEMENTATION_TEAM10.md](./2026-03-30_M3_IMPLEMENTATION_TEAM10.md)
- Mandate: `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md`

## Gate G3 checklist (paste evidence when re-running QA)

### Environment

- Python version: _(3.11+)_
- PostgreSQL version: _(15+ direct install)_
- Alembic revisions applied: _(001–007 when 006–007 exist)_

### Output: `python -m organic_market_agent run_normalizer`

_(paste full CLI output after ingestion + normalize)_

### DB counts after normalizer run

- `raw_extracted_items` (`extraction_status='normalized'`): _N_
- `raw_extracted_items` (`extraction_status='unresolvable'`): _N_
- `normalized_observations`: _N_ (mandate: ≥ 40 for full demo)

### DB-driven alias test

_(describe: new alias inserted, normalizer re-run, `product_id` resolved)_

### Output: `pytest tests/test_normalizer.py -v`

_(all PASS)_

### Output: `pytest tests/ -v`

_(full suite PASS)_

### Basket policy verification

```sql
SELECT COUNT(*) FROM normalized_observations
WHERE is_basket_product = true AND normalized_price_value IS NOT NULL;
```

→ must be **0**.

### Confidence score range

```sql
SELECT MIN(confidence_score), MAX(confidence_score) FROM normalized_observations;
```

→ must be in **[0.10, 1.00]**.

## Next step (Team 10 → Team 50)

After G2 open and DB at revision 007: file `_COMMUNICATION/TEAM_50/reports/{date}_G3_REVIEW_REQUEST_M3_TEAM50.md` with this document + pasted checklist evidence.
