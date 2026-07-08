# BRIEF (REGISTER) — SFA-S003-P004-WP-CB-MARKET-DETAIL — team_100 — v1.0.0

**Date:** 2026-06-08 · **Author:** team_100 · **WP:** SFA-S003-P004-WP-CB-MARKET-DETAIL
**Type:** REGISTER brief (pre-spec) · **Status:** REGISTERED — awaits design + LOD400 spec

## Problem
`WP-CB-UI-REDESIGN` redesigned the market **index** (`market_list.php`) into a card
drill-down, but the **per-product detail page** — `market_product.php`, route
`/market/{slug}` — still carries the **old design + OS color-emoji**. It is functional
(HTTP 200) but visually inconsistent with the shipped redesign.

## Scope (to be specified at LOD400)
- Re-skin / redesign `market_product.php` to the new DS (`redesign.css` / mock-v2 / DSX-1 / DSX-2).
- Reuse the aggregates `MarketViewController` already produces (min/median/max, source/observation
  counts, **sparkline + 28-day trend** via `fetchSeriesAll()`).
- Decide: keep the existing `pgraph` / `phist` / `rangesel` detail contract (and re-skin it), OR
  fold the detail into the same `.pcard` drill-down pattern as the index.
- **Owns the `market_product.php` emoji fold** — explicitly EXCLUDED from `WP-CB-DSX1-SWEEP` to avoid
  double-work / merge conflict.

## Out of scope
The market index (done), the ingest pipeline, the calc engine.

## Inputs
- `sfa_delivery/templates/pages/market_product.php` (current detail page) + `MarketViewController::detail`.
- The shipped DS: `redesign.css`, `ui-icons.svg`.
- Reference: the `WP-CB-UI-REDESIGN` market_list build (`market_list.php` + WI-5 commit `f465229`).

## Next step
team_00 schedules; design (team_35) + LOD400 spec (team_100) before build. No agent/runtime
dependency — `market_product` reads the same MySQL mirror already populated.
