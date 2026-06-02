# Team 190 — Revalidation Request: Phase A & B LOD400 Specs (v2)

**Date:** 2026-04-08  
**From:** Team 100 (Architecture)  
**To:** Team 190 (Constitutional Preflight)  
**Reference:** VALREQ-20260408-PHASES-AB  
**Prior report:** `_COMMUNICATION/TEAM_190/reports/2026-04-08_PHASES_AB_LOD400_VALIDATION_TEAM190.md` (FAIL)  
**Status:** RESUBMISSION — all 4 blocking FAIL items addressed; 1 advisory note resolved

---

## Summary of Changes Made

All fixes were applied directly to the two LOD400 specification documents. No structural changes were made. Scope is limited to the 4 FAIL items and 1 advisory note from the prior report.

| Prior finding | Checklist item | Fix applied | Location |
|---|---|---|---|
| Phase B missing `Expands LOD200` statement | G3 | Added `Expands LOD200` line to Phase B header block | `PHASE_B_LOD400_SPEC_TEAM100.md` line 10 |
| A4 lacks executable command / SQL content | A3 | Added new section A4.3 with WP REST `curl` + `psql INSERT` blocks | `PHASE_A_LOD400_SPEC_TEAM100.md` A4 section |
| Phase E privacy audit missing grep-based SRC scan | A14 | Added shell `grep -R -n -E 'SRC[0-9]{3}' output/public/` block with zero-match condition | `PHASE_A_LOD400_SPEC_TEAM100.md` E1.3 section |
| Both specs missing canonical brief reference | X4 | Added `Canonical brief` line to Phase A and Phase B header blocks | Both spec files, header block |
| Advisory: C4.1 test count `≥ 4` vs `≥ 8` | (advisory) | Corrected to `≥ 8` in C4.1 files table | `PHASE_A_LOD400_SPEC_TEAM100.md` C4.1 |

---

## Revalidation Scope

Team 190 need only re-check the 4 previously failing items (G3, A3, A14, X4) and confirm the advisory note is resolved. All other 37 checklist items were PASS in the prior report and remain unchanged.

**Documents under revalidation:**

- Phase A: `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`
- Phase B: `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md`

---

## Evidence Map for Each Fix

### G3 — Phase B `Expands LOD200` statement

Phase B header now reads (lines 10–12):

```
**Gate:** Team 100 self-sign-off + Nimrod review (no Team 50 QA — documents only)  
**Expands LOD200:** `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` (MANDATE-20260407-M11-SPECS) — this document adds authoring precision, required section structures, wireframes, and verification checklists for all three M11 deliverables  
**Canonical brief:** `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` (BRIEF-20260407-PHASE-AB-CANONICAL)
```

### A3 — A4 executable commands

New section **A4.3 Executable Commands** added immediately before the old A4.3 (now renumbered A4.4). Contains:
1. `curl` command — WP REST API page creation with `status: draft`
2. `psql` `INSERT INTO raw_extracted_items` with all required fields
3. Post-entry `SELECT` verification query
4. `catalog_renormalize` call instruction
5. Fallback instruction if WP REST is unavailable (document as `MANUAL REQUIRED`)

### A14 — grep-based SRC leakage command

Added immediately after the existing Python privacy audit block in E1.3:

```bash
grep -R -n -E 'SRC[0-9]{3}' output/public/
# Expected output: (empty — no lines printed)
# Any match is a FAIL
```

### X4 — Canonical brief references

Phase A header now includes:
```
**Canonical brief:** `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` (BRIEF-20260407-PHASE-AB-CANONICAL)
```

Phase B header includes the same line (as part of the G3 fix block above).

---

## Expected Decision

PASS — all blocking items resolved, all advisory notes addressed.

Upon PASS, Team 100 will update `CHANGELOG.md` and proceed to orchestrate Phase A implementation via Team 10 mandate issuance.
