# Team 10 — M3 Normalizer Engine implementation summary

**Date:** 2026-03-30  
**Milestone:** M3 — Normalizer Engine  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md`

## Delivered

- Package `organic_market_agent/normalizer/`: `context.py` (`NormContext`), seven stage modules (`alias_resolver`, `organic_flag`, `price_parser`, `unit_resolver`, `quantity_parser`, `price_normalizer`, `basket_handler`), `confidence.py`, `engine.py` (`NormalizerEngine`), `run_normalizer.py`.
- **CLI:** `python -m organic_market_agent run_normalizer` [--source-id] [--ingestion-run-id]; also `python -m organic_market_agent.normalizer.run_normalizer`.
- **Ingestion:** `python -m organic_market_agent.scheduler.run_ingestion --normalize` runs the normalizer after commit for the same `ingestion_run_id`.
- **Tests:** `tests/test_normalizer.py` — 18 tests (14 run without DB; 4 integration tests skip if PostgreSQL is unavailable).

## Behaviour notes

- `NormalizerEngine.run` joins `RawExtractedItem` → `SourceFetchRun`; filters optional `ingestion_run_id`, `source_id`.
- Blocking failures: alias and price parse → `extraction_status='unresolvable'`; missing `product_id` / `price_amount` / `display_unit_id` after stages → unresolvable (no `NormalizedObservation` row).
- `unit_resolver` applies `normalizer_rules` (`unit_map`) using `match_pattern` + `match_type`, then built-in map, then product default unit.
- `price_normalizer` maps `UnitConversion.conversion_type` to `normalization_method` (`exact` → `unit_conversion_exact`; else `unit_conversion_heuristic`); no conversion → `direct`.

## Gate G3 / QA (not executed here)

Full mandate checklist (≥40 `normalized_observations`, basket SQL, confidence range, DB-driven alias re-run, `pytest tests/`) requires:

1. **Gate G2 open** (per roadmap).
2. **Alembic 006 + 007** applied (Team 20 seed patch per mandate pre-condition).
3. **PostgreSQL** available for integration tests and live normalizer runs.

## References

- `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md`
- `_COMMUNICATION/ROADMAP.md` (G3)
