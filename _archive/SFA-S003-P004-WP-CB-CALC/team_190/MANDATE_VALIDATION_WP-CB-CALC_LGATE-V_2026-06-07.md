---
id: SFA-S003-P004-WP-CB-CALC-LGATE-V
mandate_from: team_100 (Chief Architect — builder engine: Claude Opus)
mandate_to: team_190 (constitutional / final validation — cross-engine, non-Claude per IR#1/#5)
re: L-GATE_V final validation of WP-CB-CALC (deployed to production)
created: 2026-06-07
status: OPEN — final constitutional validation requested
prior_gates:
  - L-GATE_D PASS_WITH_FINDINGS (team_190, Cursor/Composer) — findings cleared
  - L-GATE_QA PASS v2.0.0 (team_50, Cursor/Composer) — branch
  - team_99 deploy + live smoke PASS
---

# MANDATE — team_190 L-GATE_V: WP-CB-CALC (final, constitutional)

WP-CB-CALC is built, cross-engine QA'd (PASS), and **deployed to production**. Requesting the **final, constitutional L-GATE_V** verdict (the immutable gate, IR#5). Builder = Claude (Opus); validator must be **non-Claude** (IR#1).

## What to validate
- **Scope delivered:** calculator 6/14 → **14/15 goals live** (water #0 deferred → WP-CB-WATER). Engines: scalar ports (transplants/seed_cost), date engine `SFA_DATEC` (sow_date/harvest/succession/frost/nursery), quantity-first compare basket. Server plumbing (date numerics whitelist + `SFA_CROP_BOOK_TXT` categorical channel). `frost_regions.json` (team_00 approved interim).
- **Code on main @ `2f31d89`** (pushed); live @ `sfa.nimrod.bio/calc/` assets `?v=1780865050`.
- **Specs:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/{REGISTER,LOD400_spec}.md` + LOD_DESIGN.

## Evidence (builder-side)
- PHPUnit **224/224**; `validate_aos.sh` **0 FAIL** (30 PASS / 21 SKIP).
- Date math **parity-verified vs the real `calculators.py`** (sow 16/06/2026; harvest 15/09→27/10; succession; frost 11/03→26/08; nursery 3 trays·03/04).
- team_50 FULL QA **PASS v2** (0 blockers/major) + team_99 deploy live smoke PASS.

## Constitutional checks requested
- **IR#1 cross-engine:** builder (Claude) ≠ this validator (non-Claude). Confirm.
- **IR#4 single-writer roadmap;** **IR#3 spec_ref** repo-internal + resolve.
- **Directory authority:** team_100 wrote only `_COMMUNICATION/team_100|35|50|190/`, `_aos/roadmap.yaml`, `_aos/work_packages/`, and `sfa_delivery/` app source (builder role). No `_aos/governance/` edits.
- **IR#7 API-only when DB online:** no structured DB mutations performed.
- **Product integrity:** quantity-first (no "profit"/"margin"; ₪ secondary); **no fabricated numbers** (honest nodata/soon states); frost_free → honest open window.
- **Deferrals tracked:** water (WP-CB-WATER), CSS polish F-02/F-03/F-04 (UI-redesign pass), crop date-data coverage (WP-CB-CROPDATA-DATES), frost-date refinement (WP-CB-FROST-DATA).

## Verdict
Issue the L-GATE_V verdict (PASS → LOD500_LOCK, or findings) via `_COMMUNICATION/team_100/`. On LOD500_LOCK, team_191 archives the WP per IR#15.
