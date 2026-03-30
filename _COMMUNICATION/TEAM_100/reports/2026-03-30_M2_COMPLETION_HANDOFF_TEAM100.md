# Team 100 — M2 Collection Layer completion handoff

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**To:** Team 100 (Architecture)

## Summary

Team 10 has implemented **M2 — Collection Layer** per `MANDATE_M2_COLLECTION_LAYER.md`: collectors, parsers, ingestion CLI, unit tests, and ERROR persistence to `log_entries` (Team 10 onboarding alignment).

Full evidence (commands, pytest output, DB metrics, dedup, deviations) is in:

- `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_COMPLETE_TEAM10.md`

## Requests for architecture (optional decisions)

1. **EasyFarm selector drift:** Live pages fetched but `easyfarm_catalog` often extracts 0 rows. Confirm whether Team 10 should expand default selectors vs mandating per-source `selector_profile` in DB only.

2. **Seed profile vs parser mismatch:** Some sources use `fetch_mode='html_page'` with `normalizer_type` that maps to JSON parsers. Confirm corrected `fetch_mode` / `entry_url` strategy for benchmark rows in seed (Team 20 data) vs parser map.

3. **G2 gate:** Team 50 has been asked to sign off G2 (`_COMMUNICATION/TEAM_50/reports/2026-03-30_G2_REVIEW_REQUEST_M2_TEAM50.md`). Architecture acknowledgment of any listed deviations is appreciated before M3 mandate issuance.

## No code changes requested from Team 100

This is a completion notification and decision queue only.
