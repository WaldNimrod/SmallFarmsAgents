# ARCHIVE_MANIFEST — SFA-S003-P004-WP-CB-UI-REDESIGN

**Archived:** 2026-06-08 · **By:** team_100 (closure) · **Terminal state:** LOD500_LOCKED
**Iron Rule #15 / POST_GATE_ARCHIVE_PROCEDURE** · L-GATE_VALIDATE PASS → archive on closure.

## Outcome

Full redesigned public version of SFA — **LIVE on `sfa.nimrod.bio`**. 7 public surfaces
(home · crop-book index · crop page · market · assumptions · calc re-skin) + internal
cropdata_entry tool, built from the team_35 LOD300 mockups; DSX-1 icon set + DSX-2 type
floor folded into the production design system.

## Gate record

| Gate | Result | Validator | Engine |
|------|--------|-----------|--------|
| L-GATE_E (REGISTER) | REGISTER | team_00 | — |
| L-GATE_BUILD | COMPLETE | team_100 | Claude Code (builder) |
| L-GATE_VALIDATE | **PASS** (VC-1..VC-10) | team_190 | Cursor / Composer (non-Claude — IR#1/#5) |
| DEPLOY | **LIVE** | team_100 | FTPS → uPress (team_00 authorized) |

## Evidence

- Tests: PHPUnit **226/226**; browser-QA `qa_probe.mjs` **16/16** local + **14/14 production** (zero overflow).
- Engine lock: `crop-book-v1.js` diff **0 bytes** (WP-CB-CALC LOD500 engine untouched).
- `validate_aos.sh`: 0 FAIL.
- Live smoke: all 7 surfaces + 2 new assets HTTP 200; redesign confirmed serving (`.hdr`/`.shell`/`redesign.css`, `stagenav`/`cb-crop-detail`).

## Build manifest (code — branch feat/wp-cb-ui-redesign, baseline 8d03f2e → merged to main)

- DS/shell: `sfa_delivery/public_assets/css/redesign.css`, `public_assets/img/ui-icons.svg`, `templates/_layout.php`
- Templates: `templates/pages/{hub_home,book_entry,book_crop,market_list,assumptions,calc_dash,cropdata_entry}.php`
- Controllers: `app/Controllers/{CropBookViewController,MarketViewController,AssumptionsController}.php`, `app/routes.php`
- Tests: `tests/{ClassBRouteTest,CropBookV1RouteTest,CropCardIconTest,RouteSmokeTest}.php`

## Archived artifacts (this directory)

- `team_35/handoff_ui_redesign/` — LOD300 hi-fi mockups + mock.css/mock-v2.css/sfa-icons.js + watercolors
- `team_100/` — WORKPLAN, BRIEF, MANDATE(team_35 refine), HANDOFF, COMPLETION_REPORT
- `team_190/` — L-GATE_VALIDATE MANDATE, MSG, VERDICT (PASS)

## Open follow-ups (registered, NOT blocking — see roadmap notes)

1. Content WP — `description_md` + `care.{watering,fertilizing,pests}_md` (honest empty-states until then).
2. `water` goal (#0) → WP-CB-WATER (no model + no data).
3. cropdata_entry backend persistence WP (delivery tier is read-only; staging only today).
4. DSX-1 emoji fold for untouched legacy surfaces (`search_results`, `community`, `crop_calendar` macro) — team_190 advisory.
