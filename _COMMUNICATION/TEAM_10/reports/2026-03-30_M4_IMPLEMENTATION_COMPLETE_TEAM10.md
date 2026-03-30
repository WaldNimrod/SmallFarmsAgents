# M4 implementation complete — Team 10

**Date:** 2026-03-30  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md`  
**Status:** Implemented; ready for Team 50 G4 review.

## Delivered components

| Area | Location |
|------|----------|
| AggregatorEngine | `organic_market_agent/aggregator/engine.py` |
| QAEngine (QA001–QA003) | `organic_market_agent/aggregator/qa_engine.py` |
| PublishEngine | `organic_market_agent/publisher/engine.py` |
| HTML template (RTL, Bootstrap 5) | `organic_market_agent/publisher/templates/public_report.html` |
| Static viewer | `organic_market_agent/publisher/viewer.py` |
| Admin dashboard | `organic_market_agent/admin/` (Flask `create_app`, routes, templates under `templates/admin/`) |
| CLI | `organic_market_agent/__main__.py`: `run_viewer`, `run_admin` |
| Exception | `PublishAbortError` in `organic_market_agent/utils/exceptions.py` |

## Test commands

```bash
python3 -m pytest tests/test_aggregator.py tests/test_publisher_local.py -v
python3 -m pytest tests/ -q
```

## Test counts (mandate)

- `tests/test_aggregator.py`: 9 tests (threshold, empty day, UPSERT idempotency, weekly rollup, stddev when n=1, QA001–QA003).
- `tests/test_publisher_local.py`: 6 tests (abort, JSON/HTML, manifest staleness ×3, manifest keys).

## Truncated artifact examples

**`public_report.json` (shape):** `generated_at`, `report_date`, `products[]` with `product_id` (product **code**), `canonical_name_he`, `avg_price` (from `unweighted_avg_price`), `normalized_unit`, `sample_size`, `distinct_sources`, etc.

**`manifest.json`:** `last_published_at`, `report_date`, `product_count`, `staleness_level` (`current` / `warning` / `irrelevant` vs generation vs reference clock), `community_sources`.

## Deviations / notes

1. **Aggregation scope:** `normalized_observations` filtered to `market_scope IN ('community','benchmark')` and `flag_status = 'ok'`, with quarantined `raw_extracted_items` excluded. **`verification` scope is not aggregated** into `daily_aggregates` (CHECK on table allows only community/benchmark).
2. **Price field:** Stats use `COALESCE(normalized_price_value, price_amount)` in SQL.
3. **Staleness:** Publish HTML banner when latest `last_observed_at` is **> 3 days** before `reference_now`. Manifest `staleness_level` uses **> 7 days = irrelevant** (plan / M3 spec).
4. **QA001 integration test:** Requires **≥ 11 active sources** (ten prices at 10, one at 500 on the same calendar day) so the observation exceeds mean + 3σ; environments with fewer sources **skip** that test (rule is still exercised in code for real runs).
5. **Weekly `distinct_sources`:** Rolled as `max(d.distinct_sources)` over days in the week (not re-counting unique sources across the week).

## Blockers

None known.
