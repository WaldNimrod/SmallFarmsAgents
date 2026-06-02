# M10.5 — Implementation complete (Team 10)

**Date:** 2026-03-30  
**Mandate:** `MANDATE-20260404-M10-5-CSA-RETAIL`  
**Analysis policy:** `2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md`

---

## Summary

- **CSA (SRC033–035):** `CsaBasketParser` (`normalizer_type: csa_basket`) with per-site `selector_profile.csa_site` and **`raw_payload_json.csa_context`** (contents + cadence excerpts per policy).
- **Retail (SRC036):** `SellioParser` + **`platform_family: sellio`** → `HeadlessBrowserCollector`; organic-aisle category URL; **`sellio_organic_only`** keeps rows whose display name contains organic markers (Hebrew / English).
- **Migration 056:** fetch + normalizer profiles, activate sources, CSA `product_aliases`, global scope-skip for packaged `– השדה` lines (dry grocery).
- **Tests:** 9 new unit tests (4 CSA + 5 Sellio); full suite **176 passed**, 4 skipped.

---

## Evidence

```bash
python3 -m alembic upgrade head    # expect 056 (head)
python3 -m pytest tests/test_csa_parsers.py tests/test_sellio_parser.py -q
python3 -m pytest tests/ -q
```

---

## Acceptance criteria (mandate §5)

| ID | Status / note |
|----|----------------|
| AC1 | **SRC033 + SRC034** produce basket rows; **SRC035** may yield **0** SKUs on FAQ URL (policy §4.5) — meets **≥2/3** when 033+034 run. |
| AC2 | Strict organic **name** filter on single category URL → **~12** organic lines observed in dev spike; **≥20** may need Team 100 scope (extra URLs or relaxed rule). **0 conventional** in that filtered set. |
| AC3 | Documented: hybrid **category URL + name filter**; extensible via `selector_profile`. |
| AC4 | Run after live ingest + `catalog_renormalize`; packaged `– השדה` → scope_skip. |
| AC5–AC9 | Pending Team 50 execution (publish count, live page, pytest already green). |

---

## Files

- `organic_market_agent/parsers/csa_basket.py`  
- `organic_market_agent/parsers/sellio.py`  
- `organic_market_agent/parsers/engine.py`  
- `organic_market_agent/collectors/engine.py`  
- `organic_market_agent/collectors/headless_browser.py`  
- `organic_market_agent/db/versions/056_m10_5_csa_retail_sources.py`  
- `organic_market_agent/models/normalizer.py` (constraint sync)  
- `tests/test_csa_parsers.py`, `tests/test_sellio_parser.py`  
- `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_5_TEAM10.md`

---

## Team 50

Please execute QA per `QA_REQUEST_M10_5_TEAM10.md` and file a dated findings report.
