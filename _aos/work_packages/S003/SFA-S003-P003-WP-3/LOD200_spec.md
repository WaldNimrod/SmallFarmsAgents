# LOD200 — SFA-S003-P003-WP-3 — User-Facing Routes (crop-book + market) (STUB)

**Date:** 2026-05-23
**Status:** LOD200_DRAFT — **BLOCKED on WP-2 (Slim app + ingest must exist)** AND **conditionally awaits WP-B (team_35) LOD300 design book**. Full LOD400 authored when both unblock.

## Scope summary

Build the public-facing routes on `sfa.nimrod.bio`:

1. **`GET /`** — landing page (briefly intro both modules + nav)
2. **`GET /crop-book/`** — crop book grid (52 crops, category tabs, search, season filter, DTM filter)
3. **`GET /crop-book/<crop_id>/`** — crop detail (8 tabs: varieties, description, economics, care, equipment, sources, timeline, field-data)
4. **`GET /market/`** — market index (32 products, daily prices, freshness indicator, source attribution)
5. **`GET /market/<product_id>/`** — product detail (price history, sources, basket tiers if applicable)

## Stack details

- **Server-rendered HTML** by Slim routes + plain PHP templates (or Plates)
- **Vanilla JS** for client-side interactivity (tabs, search, filter — port current crop_book SPA logic to load from `/api/v1/...` endpoints)
- **CSS**: design tokens + components from WP-B design book (when team_35 ships LOD300)
- **RTL Hebrew, mobile-first, system fonts** (per WP-B constraints)

## Effort estimate

~2-3 days post-unblock by WP-2. Reuses current crop_book SPA JS heavily; mostly Jinja2→PHP template translation + design book application.

## Will be expanded to LOD400 when

- WP-2 LOD500_LOCKED (Slim app + DB + read APIs working)
- WP-B (team_35) LOD300 mockups + design book ready (or accept that v1 uses interim design and re-skin in WP-5)

---

*Stub LOD200 — authored 2026-05-23 by team_100. To be expanded post-WP-2 + WP-B.*
