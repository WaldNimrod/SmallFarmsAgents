# M10.4 QA remediation — mypips parser forensics (Team 10)

**Date:** 2026-04-05  
**Context:** Team 50 T03 — only 5/9 priority sources had `raw_extracted_items` rows while T02 showed non-shell `raw_assets` for SRC042, SRC055, SRC062, SRC069.

## Hypothesis

Collection succeeded (HTML stored). The previous parser path depended on **`h6` titles** with price in sibling elements. Some mypips themes place the **product name in `h5`** (or only `strong`) and **price in `span`**, so the legacy loop never paired name+price and returned **zero** rows.

## Code response

[`MypipsParser`](organic_market_agent/parsers/mypips.py) now:

1. **Card-first:** For each `div.pips-card-content`, find the first **currency line** (₪ / NIS / ש״ח), then the first **heading (h2–h6) without currency** as the title (or `strong`/`b` fallback).
2. **Legacy fallback:** If no rows from cards, keep the previous **`h6` walk** for older HTML shapes.

Optional per-source **`card_selector`** remains in `selector_profile` (passed as parser overrides) for future Alembic tuning without code changes.

## Evidence to collect on re-QA

Re-run verbatim T03 SQL from `QA_MANDATE_M10_4_TEAM50.md` after **re-ingestion** for the four previously empty codes; expect **≥7/9** with `raw_rows > 0` if storefront DOM matches the above patterns.
