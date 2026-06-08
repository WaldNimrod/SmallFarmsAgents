---
id: SFA-S003-P004-WP-CB-CALC-ARCHIVE
mandate_from: team_100 (Chief Architect)
mandate_to: team_191 (Git/Files — archival authority)
re: IR#15 archive of WP-CB-CALC comms (WP is COMPLETE / LOD500_LOCKED)
created: 2026-06-08
status: OPEN — final closure step (also unblocks the push: validate Check 15)
---

# MANDATE — team_191: archive WP-CB-CALC (IR#15)

WP-CB-CALC is **COMPLETE / LOD500_LOCKED** (team_190 L-GATE_V PASS 2026-06-08; roadmap closure committed
locally @ `5ef2897`, **unpushed** — pre-push `validate_aos` Check 15 blocks until this archive lands).
Archive the WP comms per IR#15, then push.

## Scope — MOVE to `_archive/SFA-S003-P004-WP-CB-CALC/<team>/` (preserve per-team structure)
**WP folders (tracked + untracked mixed — use `mv` then `git add -A`):**
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-CALC/` (LOD_DESIGN, MOCKUP_RETURN/ITERATION, FROST_DATES_APPROVED, L-GATE_QA verdicts v1/v2/v3, LOD500-VERDICT, evidence_2026-06-07/, evidence_2026-06-08/)
- `_COMMUNICATION/TEAM_190/SFA-S003-P004-WP-CB-CALC/` (L-GATE_D verdict)
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-CALC/`

**Loose CALC files:**
- `_COMMUNICATION/TEAM_190/VALIDATION_REQUEST_WP-CB-CALC_2026-06-07.md`, `MANDATE_VALIDATION_WP-CB-CALC_LGATE-V_2026-06-07.md`
- `_COMMUNICATION/TEAM_50/MANDATE_QA_WP-CB-CALC_{B-now,full,LIVE}_*.md`
- `_COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md`, `RETURN_REPLY_CALC_MOCKUPS_2026-06-07.md`, `FROST_REGIONS_AND_SPEC_LOCK_2026-06-07.md`
- `_COMMUNICATION/team_191/MANDATE_ARCHIVE_WP-CB-CALC_2026-06-08.md` (this file, on completion)

## ⚠ DO NOT touch / move
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/` — **stays** (it is the `spec_ref` target; must keep resolving). Do NOT archive it.
- `_COMMUNICATION/TEAM_100/UI_REDESIGN_2026-06/` and `SFA-S003-P004-WP-CB-UI-REDESIGN/` — parallel UI session WIP.
- Other OPEN WPs' comms: `SFA-S003-P004-WP-CB-{CROPDATA-DATES,WATER,DEEP-PROVENANCE,FROST-DATA}/`.
- The shared scope report `REPORT_WP-CB-MOBILE_FOLLOWUPS_calc-and-deep-provenance_2026-06-07.md` — shared with the still-OPEN WP-CB-DEEP-PROVENANCE; **leave in place**.
- `.claude/launch.json`.

## Required ref update (so spec_refs keep resolving)
After moving, update the WP-CB-CALC roadmap entry **`design_ref`**:
`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md`
→ `_archive/SFA-S003-P004-WP-CB-CALC/team_100/LOD_DESIGN_2026-06-07_v1.0.0.md`
(`spec_ref` → work_packages is unchanged.)

## Closure artifacts (create under `_archive/SFA-S003-P004-WP-CB-CALC/`)
- `MANIFEST.md` — list of archived files.
- `CLOSURE_RECORD.md` — WP id, scope (14/15 live; water deferred), gates (L-GATE_D PASS_WITH_FINDINGS→cleared · L-GATE_QA PASS v3 · L-GATE_V PASS→LOD500_LOCKED), build `0a993e9`, live `sfa.nimrod.bio/calc/`, open follow-ups (WP-CB-WATER/CROPDATA-DATES/FROST-DATA/UI-REDESIGN).

## Finish
`validate_aos.sh` → **0 FAIL** (Check 15 clears) → commit (team_191) → push `main`. Verify ancestry after.
