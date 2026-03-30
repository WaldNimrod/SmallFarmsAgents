# Team 20 — Notice: ORM aligned to migration 008 (`unresolvable_reason`)

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**To:** Team 20 (Infrastructure)

## Summary

Alembic **008** alters `raw_extracted_items.unresolvable_reason` to **TEXT**. The SQLAlchemy model previously still declared **VARCHAR(200)**.

## Change (Team 10)

- **File:** `organic_market_agent/models/runs.py`  
- **Field:** `RawExtractedItem.unresolvable_reason` now uses **`sqlalchemy.Text`** to match the database.

No migration required from Team 20 for this alignment (008 already applied). This is **documentation / ORM parity** only.

## Action for Team 20

- Acknowledge in your next infra report if desired.  
- No code change required unless you prefer a different typing style in models.
