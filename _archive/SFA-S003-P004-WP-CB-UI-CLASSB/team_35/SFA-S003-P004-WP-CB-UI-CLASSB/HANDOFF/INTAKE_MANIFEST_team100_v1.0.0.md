# INTAKE MANIFEST — Class B design package — team_100 — v1.0.0

**Date:** 2026-06-02 · **WP:** SFA-S003-P004-WP-CB-UI-CLASSB · **From:** team_35 → **Intake by:** team_100

## Provenance
Source: `SFA Small Farms Agents (5).zip` (team_35, 2026-06-02 14:11). Extracted verbatim into this `HANDOFF/`
folder. 41 files. Response to `…/DESIGN_MANDATE_team35_v2-surfaces_2026-06-02_v1.0.0.md`.

## Integrity checks (team_100)
- `design/tokens.css` sha256 `17e7719f…` — **byte-identical** to the v1 HANDOFF_PACKAGE tokens. ✅ no palette drift.
- `design/cropbook-v1.css` / `cropbook-v1.js` — byte-identical to v1. ✅ Class A contract unchanged.
- NEW: `design/Board-B-*.html`, `design/classb.css` (42KB, ~35 component families), `design/classb.js` (1.4KB),
  `spec/B_COMPONENTS-TEMPLATES-classb-delta.md` (§30–42 + routes + partials + §3.8 Mobbin table).
- Board-A (`Board-A-Book-and-Calculator.html`) included for completeness — that is the already-delivered Class A
  (do NOT rebuild; reference only).

## Coverage vs the mandate (7 surfaces + shell)
All requested surfaces delivered: app-shell refine (§3.1), hub (§3.2), market list+detail (§3.3), search (§3.4),
community (§3.5), about/tiers (§3.6), account (§3.7). §3.8 Mobbin patterns embedded as `.patref` chips per frame.

## team_100 assessment
- Package is precise + buildable; reuses the existing kit (`.prov`, `.tier--*`, `.reqinfo`, `.contrib`, `.aud`,
  `.ptable`, `.fchip`) — minimal new surface area.
- **Data is largely already available** in the delivery tier (market history/graph/sources/freshness via
  `MarketViewController` + `product_prices` + `/api/v1/market/{slug}/history`; contribute via
  `AssumptionsController::contribute`; tiers/modules via `Modules::all()`). No new schema required.
- New code needed: `AccountController` + `account_landing.php` (visual shell only) + the classb.css/js port + the
  per-surface templates.

## Open questions → recorded in LOD400 §9 for team_00
Community feed-less (team_35 already removed it) · account scope (shell-only v1) · graph time-ranges (7+28 live) ·
search suggestions (client-side) · market units + freshness thresholds. LOD400 locks to v1.0.0 on team_00 answers.

## Disposition
Embedded into `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md` (DRAFT v0.9.0). WP advanced
ELIGIBLE → LOD400_DRAFT → (after team_00 §9) team_190 L-GATE_S.
