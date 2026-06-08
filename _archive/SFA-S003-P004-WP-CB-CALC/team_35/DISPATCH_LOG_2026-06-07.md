# DISPATCH LOG — team_35 → team_100 (WP-CB-CALC mockups)

**Date:** 2026-06-07 · **From:** team_35 (design) · **To:** team_100 (calc engine)
**Re:** reply to `SFA-S003-P004-WP-CB-CALC-MANDATE-MOCKUPS`

## Delivered (canonical, IR#6)
- **Return artifact:** [`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/MOCKUP_RETURN_team35_2026-06-07_v1.0.0.md`](../../team_100/SFA-S003-P004-WP-CB-CALC/MOCKUP_RETURN_team35_2026-06-07_v1.0.0.md) — routed to the recipient's WP dir as the mandate (§6) requested.
- **Mockups:** `_COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/{calc.html, cropdata_entry.html, assumptions.html}` on `mock.css` (LOCKED tokens).

## Contents
- §1 mockup inventory · §2 **15-goal → result-shape + inputs mapping** (the 5 shapes) · §3 **6 UI-driven server/data flags** · §4 design guidance · §5 + top callout: **4 design-blocking questions**.

## Awaiting from team_100 (blocks LOD400 presentation lock)
1. Frost region canonical list (+ default).
2. `compare` (#13) scope — all crops vs shortlist *(possible team_00 product call)*.
3. `nursery` (#3) anchor — dedicated field-set date vs reuse target.
4. `seed_cost` (#14) — own goal vs sub-line.
+ confirmation that the 6 server flags (incl. builder relabel + frost-region JSON asset) are folded into the spec.

## Round 2 — team_100 replied (`FROST_REGIONS_AND_SPEC_LOCK_2026-06-07`)
- team_100 **LOCKED** the presentation spec to our mockups (shapes, badges, anchor, no-data, `SFA_CROP_BOOK_TXT`, relabels).
- 2 residuals resolved on our side → `MOCKUP_ITERATION_team35_2026-06-07_v1.1.0.md`:
  1. **#13 → selected-crop basket** (team_00 decision) — done in `calc.html`.
  2. **Region picker** wired to frozen keys (`coastal`⭐/`judean_hills`/`jordan_valley`/`northern_negev`/`upper_galilee`) + frost_free honest-window.
- Q1–Q4 all resolved: regions=answered; #13=basket (Q2); nursery anchor + seed_cost=locked as mocked (Q3/Q4).

## Status
**Design residuals CLOSED.** One **team_00 action** outstanding: approve the DRAFT frost-date table so engine ships `frost_regions.json` (gates frost #11 / B-later only).
