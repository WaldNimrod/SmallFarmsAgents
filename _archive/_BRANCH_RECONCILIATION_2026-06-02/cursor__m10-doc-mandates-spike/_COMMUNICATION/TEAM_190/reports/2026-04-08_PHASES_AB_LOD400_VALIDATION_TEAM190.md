# Team 190 — Package Validation: Phase A & B LOD400 Specs

Date: 2026-04-08
Package: VALREQ-20260408-PHASES-AB
Result: FAIL

## Checklist Results

| Item | Result | Evidence |
|------|--------|----------|
| G1 | PASS | Phase A header includes `SPEC-20260408-PHASE-A-LOD400` at `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md:3`. |
| G2 | PASS | Phase B header includes `SPEC-20260408-PHASE-B-LOD400` at `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md:3`. |
| G3 | FAIL | Phase A states both supersession and binding authority at `...PHASE_A...:8` and `:1327`; Phase B states binding authority at `...PHASE_B...:593` but does not explicitly state its relationship to superseded / expanded LOD200 source documents in the same canonical manner. |
| G4 | PASS | Both docs state author/date at Phase A `:4-5` and Phase B `:4-5`. |
| G5 | PASS | Phase A cites consolidated mandate and gate at `...PHASE_A...:7-10`. |
| G6 | PASS | Phase B cites M11 mandate and gate at `...PHASE_B...:7-10`. |
| G7 | PASS | ROADMAP establishes v1.1.0 active before v1.2.0 planned at `_COMMUNICATION/ROADMAP.md:18-19,684-689`; Phase A/Phase B align with that ordering. |
| G8 | PASS | Phase A correction F6 and pre-work reference `[Unreleased]` at `...PHASE_A...:25,29-34`; CHANGELOG shows correction under `[Unreleased]` at `CHANGELOG.md:10-19`. |
| A1 | PASS | Section 0 present with 6 findings at `...PHASE_A...:14-25`. |
| A2 | PASS | Pre-work and Phases A–E are present with task breakdowns at `...PHASE_A...:29-1290`. |
| A3 | FAIL | A1–A3 include commands/SQL and exit criteria; A4 has owner/files/structure/exit criteria at `...PHASE_A...:446-531` but no executable SQL/command block, despite checklist requiring SQL/commands for each A-task. |
| A4 | PASS | Exit criteria are checkbox/objective in A1 `:166-176`, A2 `:333-343`, A3 `:435-442`, A4 `:524-531`. |
| A5 | PASS | Migration 072 and Team 20 coordination rule appear at `...PHASE_A...:187-194`. |
| A6 | PASS | `resolve_basket_tier(csa_context_json, price_amount, session)` spec, tier tables, resolution order, and edge cases are fully specified at `...PHASE_A...:831-975`. |
| A7 | PASS | `basket_handler.py` integration, call order, and ctx mutation are described at `...PHASE_A...:1023-1051`. |
| A8 | PASS | 8 named test cases with inputs and expected outputs are specified at `...PHASE_A...:1054-1155`. |
| A9 | PASS | PRD027 is reframed as `confirm + verify`, not bug-fix, at `...PHASE_A...:20,557-567,621-650`. |
| A10 | PASS | WhatsApp protocol requires 7 sections with content requirements at `...PHASE_A...:460-513`. |
| A11 | PASS | CQ-P08 is marked `audit + confirm only` at `...PHASE_A...:22,66-176`. |
| A12 | PASS | CQ-P09 is marked `audit + confirm only` at `...PHASE_A...:23,66-176`. |
| A13 | PASS | Pre-run uniqueness test and STOP condition appear at `...PHASE_A...:557-568`. |
| A14 | FAIL | Phase E includes a Python regex privacy audit at `...PHASE_A...:1259-1275`, but does not include the required grep-based SRC audit command requested in the validation checklist. |
| A15 | PASS | Escalation protocol table appears at `...PHASE_A...:1313-1321`. |
| A16 | PASS | Completion report requirements list 11 required items at `...PHASE_A...:1293-1310`. |
| B1 | PASS | Section 0 addresses FarmCostAgent naming bridge and Team 80 source material at `...PHASE_B...:18-20`. |
| B2 | PASS | Execution order explicitly states Items 8 and 9 in parallel; Item 10 waits for Item 8 draft stability at `...PHASE_B...:37-46`. |
| B3 | PASS | Item 8 structure lists mandatory Sections 1–8 with content requirements at `...PHASE_B...:61-198`. |
| B4 | PASS | Item 8 role table contains all 5 roles and WP capability column at `...PHASE_B...:83-89`. |
| B5 | PASS | Pre-login disabled-state wireframe is present at `...PHASE_B...:101-129`. |
| B6 | PASS | Item 8 implementation options compares 3 options and recommends Option A at `...PHASE_B...:132-140`. |
| B7 | PASS | Item 9 input model specifies 10 input fields and output model specifies at least 6 outputs at `...PHASE_B...:255-280`. |
| B8 | PASS | Team 80 input is marked placeholder with explicit fallback at `...PHASE_B...:282-293`. |
| B9 | PASS | Item 9 open questions list 4 questions at `...PHASE_B...:343-350`. |
| B10 | PASS | Item 10 specifies 6 visible fields and 4 hidden fields at `...PHASE_B...:380-395`. |
| B11 | PASS | Server-side validation table lists 7 rules with rejection messages at `...PHASE_B...:397-409`. |
| B12 | PASS | Pipeline integration specifies `raw_extracted_items`, `pending_moderation`, and `community_submission` at `...PHASE_B...:411-437`. |
| B13 | PASS | Form panel wireframe with RTL note appears at `...PHASE_B...:463-500`. |
| B14 | PASS | Cross-reference matrix contains 6 entries at `...PHASE_B...:512-523`. |
| B15 | PASS | Verification checklist contains 34 binary checkboxes covering Items 8/9/10, cross-ref, and sign-off at `...PHASE_B...:527-573`. |
| B16 | PASS | Final sign-off requires Nimrod review, completion report, and v1.2.0 tag at `...PHASE_B...:568-587`. |
| B17 | PASS | No-Team-50-QA rule is explicit at `...PHASE_B...:10` and aligns with `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md:100-102`. |
| X1 | PASS | Phase A contains no prerequisite dependency on Phase B features; it is self-contained for v1.1.0 throughout `...PHASE_A...`. |
| X2 | PASS | Phase B precondition states G-V1.1 PASS before M11 active priority at `...PHASE_B...:9`; ROADMAP matches at `_COMMUNICATION/ROADMAP.md:686-689`. |
| X3 | PASS | Version mapping is consistent: Phase A v1.1.0 (`...PHASE_A...:1,7`), Phase B v1.2.0 (`...PHASE_B...:8`), ROADMAP `:18-19`. |
| X4 | FAIL | Neither Phase A nor Phase B references `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md`; repository search against both specs returned no matches. |
| X5 | PASS | No Phase B M11 direction contradicts the Phase A `basket_tier_resolver.py` policy; the documents operate on separate scopes and do not conflict. |

## Findings (FAIL items only)

1. Missing explicit supersession / expansion statement in Phase B
   - Checklist item: G3
   - Location: [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md](/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md):3-10 and :593
   - Issue: The document has binding authority, mandate, target version, and gate, but unlike Phase A it does not explicitly state which LOD200 source documents it expands or supersedes.
   - Required fix: Add a header-level canonical line, e.g. `Expands LOD200: _COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md ...` and, if intended, also cite the canonical brief and any other governing LOD200 source.

2. A4 lacks executable command / SQL content
   - Checklist item: A3
   - Location: [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md](/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md):446-531
   - Issue: A4 includes owner, effort, files, required sections, and exit criteria, but no executable command block or SQL block. The checklist explicitly requires owner, effort, files, step-by-step, SQL/commands, exit criteria for each A-task.
   - Required fix: Add at least one concrete execution block for A4, such as a WP REST page-creation `curl` example, a documented admin action command sequence, and/or the referenced `psql INSERT` example for operator entry.

3. Phase E privacy audit does not include the required grep-based SRC scan
   - Checklist item: A14
   - Location: [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md](/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md):1259-1275
   - Issue: The spec includes a Python-based privacy audit, but the validation request explicitly asks for a grep command for SRC leakage.
   - Required fix: Add a shell command such as `grep -R -n -E 'SRC[0-9]{3}' output/public/` and state the expected zero-match condition alongside the existing Python check.

4. Both LOD400 specs omit the canonical program brief reference
   - Checklist item: X4
   - Location: [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md](/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md), [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md](/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md)
   - Issue: Validation request X4 requires both specs to reference the same canonical brief: `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` (BRIEF-20260407-PHASE-AB-CANONICAL). No such reference exists in either doc.
   - Required fix: Add a consistent canonical-brief reference to both documents near the header / governance block.

## Notes (advisory, non-blocking)

1. Phase A C4 has a small internal consistency drift: file list says `tests/test_basket_tier_resolver.py` is `NEW — ≥ 4 test cases` at `...PHASE_A...:827-829`, while detailed test spec and exit criteria require ≥ 8 at `:1054-1179`. The stronger requirement is clear, but the file table should be aligned.

2. Item 9 output model in Phase B lists 7 outputs, while the validation checklist asks for 6 output fields. This is not a blocker because the minimum is exceeded, but Team 100 may want to standardize the exact expected output set.

3. The constitutional-package-linter skill references `scripts/lint_constitutional_package.py`, but that script is not present in this workspace. This did not block constitutional review, but it prevents automated preflight reuse.

## Decision
FAIL → Team 100 must address all FAIL items and resubmit.

Resubmission scope is limited and precise:
- add explicit Phase B supersession / expansion wording,
- add canonical brief references to both specs,
- add executable A4 command content,
- add grep-based privacy audit command in Phase A E1.

Once those are corrected, this package is a strong candidate for same-session revalidation.
