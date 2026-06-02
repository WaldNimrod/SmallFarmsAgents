# Team 190 — Validation Request: Phase A & Phase B LOD400 Specification Packages

**Document ID:** VALREQ-20260408-PHASES-AB  
**Date:** 2026-04-08  
**From:** Team 100 (Architecture)  
**To:** Team 190 (Package Validation — Constitutional Preflight)  
**Re:** LOD400 specification packages for Phase A (v1.1.0) and Phase B (M11 / v1.2.0)  
**Priority:** HIGH — Phase A unblocks Team 10 implementation start  
**Result expected:** PASS / FAIL with findings per checklist item below

---

## 1. Context

Team 100 has produced two LOD400 specification documents as part of the current program:

| Package | Document | ID |
|---------|----------|----|
| **Phase A** | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` | SPEC-20260408-PHASE-A-LOD400 |
| **Phase B** | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md` | SPEC-20260408-PHASE-B-LOD400 |

These documents supersede or expand the LOD200 plans in:
- `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` (ARCH-20260406-CQ-MASTER)
- `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` (MANDATE-20260407-V1-1-CONSOLIDATED)
- `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` (MANDATE-20260407-M11-SPECS)

**Team 190 preflight scope:** Validate that both LOD400 packages are constitutionally sound before Team 100 hands Phase A to Team 10 for implementation and begins Phase B authoring. Team 190 does NOT run live tests or validate code — this is a governance and document quality check.

---

## 2. Scope and Non-Scope

### In scope for this preflight

- Document governance (format, ID convention, binding references, conflict resolution)
- Internal consistency (exit criteria are binary/testable, dependencies are explicitly stated)
- Contract completeness (does the spec give implementing teams enough information to act?)
- Cross-document consistency (Phase A and Phase B do not contradict each other or the ROADMAP)
- Escalation paths (are ambiguous decisions routed to Team 100 correctly?)

### Explicitly out of scope

- Technical correctness of the `basket_tier_resolver.py` implementation code (Team 50 validates this)
- Live database or pipeline verification (operator responsibility at execution time)
- Team 80 content for FarmCostAgent §4 (not yet produced — marked as pending placeholder)
- The actual M11 documents (Items 8, 9, 10) — those do not exist yet; this preflight validates the SPEC of those documents, not the documents themselves

---

## 3. Preflight Checklist

Team 190 must evaluate each item as **PASS**, **FAIL**, or **N/A** with brief evidence note.

### 3.1 Document Governance

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| G1 | SPEC-20260408-PHASE-A-LOD400 has a valid Document ID following naming convention `SPEC-YYYYMMDD-PHASE-X-LOD400` | | |
| G2 | SPEC-20260408-PHASE-B-LOD400 has a valid Document ID following naming convention | | |
| G3 | Both documents state their `Binding authority` and relationship to superseded LOD200 documents | | |
| G4 | Both documents state their author (Team 100) and date | | |
| G5 | Phase A cites its mandate (MANDATE-20260407-V1-1-CONSOLIDATED) and gate (G-V1.1) | | |
| G6 | Phase B cites its mandate (MANDATE-20260407-M11-SPECS) and gate (Team 100 + Nimrod) | | |
| G7 | Both documents are consistent with ROADMAP.md v6.0 milestone sequence (v1.1.0 before v1.2.0) | | |
| G8 | Phase A `[Unreleased]` reference is correct — verifies CHANGELOG correction was applied | | |

### 3.2 Phase A — Implementation Spec (SPEC-20260408-PHASE-A-LOD400)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| A1 | Section 0 (LOD400 corrections table) is present with at least 5 findings | | |
| A2 | All 6 phases (pre-work, A, B, C, D, E) are present with task breakdowns | | |
| A3 | Phase A tasks (A1–A4) each have: owner, effort, files involved, step-by-step, SQL/commands, exit criteria | | |
| A4 | Exit criteria in all sections are binary (checkboxes with objective conditions — not "as appropriate") | | |
| A5 | Migration numbering: Phase A notes that migration 072 is the first new migration, with explicit rule: "coordinate with Team 20 to assign numbers in order" | | |
| A6 | `basket_tier_resolver.py` specification (§C4.2) includes: function signature `resolve_basket_tier(csa_context_json, price_amount, session) -> (Optional[str], str)`, tier ranges table, resolution order, all edge cases | | |
| A7 | `basket_tier_resolver.py` integration with `basket_handler.py` is described: call order, when called, what it modifies on ctx | | |
| A8 | Test cases for basket tier resolver: ≥ 8 named test cases are specified with input and expected output | | |
| A9 | PRD027 investigation is reframed as "confirm + verify" (not "fix a bug") | | |
| A10 | WhatsApp Protocol (A4) lists ≥ 6 required document sections with content requirements | | |
| A11 | CQ-P08 (cherry guard) is marked as "audit + confirm" (not "new migration unless drift found") | | |
| A12 | CQ-P09 (basket codes) is marked as "audit + confirm" (not "new migration unless drift found") | | |
| A13 | Phase B (B1) includes the pre-run uniqueness test (`test_publish_one_row_per_product_code`) as a STOP condition if it fails | | |
| A14 | Phase E (E1) includes a privacy audit command (grep for SRC codes) | | |
| A15 | Escalation protocol table is present (new product codes, ambiguous aliases, tier range adjustments) | | |
| A16 | Completion report requirements section lists ≥ 10 required items | | |

### 3.3 Phase B — M11 Spec (SPEC-20260408-PHASE-B-LOD400)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| B1 | Section 0 (LOD400 corrections) addresses "FarmCostAgent" naming bridging and Team 80 source material | | |
| B2 | Execution order is explicit: Items 8 and 9 parallel; Item 10 waits for Item 8 draft stability | | |
| B3 | Item 8 document structure lists all required sections (minimum §1–§8) with content requirements per section | | |
| B4 | Item 8 §2 role definitions: role table contains all 5 roles (guest/subscriber/pending_farmer/farmer/admin) with WP capability column | | |
| B5 | Item 8 §3 wireframe: pre-login disabled state mockup is present (ASCII or description) | | |
| B6 | Item 8 §4 implementation options: at least 3 options compared with a recommended approach | | |
| B7 | Item 9 §3 input/output model: all 10 input fields and 6 output fields are specified | | |
| B8 | Item 9 §4 Team 80 input: marked as placeholder with explicit fallback ("Team 100 drafts based on strategy docs") | | |
| B9 | Item 9 §8 open questions: at least 4 questions listed (platform location, storage, AI model, Team 80 involvement) | | |
| B10 | Item 10 §2 form fields: all 6 visible fields specified with type/label/validation/required; 4 hidden fields specified | | |
| B11 | Item 10 §3 server-side validation table: ≥ 5 validation rules with rejection messages | | |
| B12 | Item 10 §4 pipeline integration: target table (`raw_extracted_items`), extraction_status (`pending_moderation`), source_type (`community_submission`) all specified | | |
| B13 | Item 10 §7 wireframe: form panel mockup present with RTL note | | |
| B14 | Cross-reference matrix (§6 of Phase B spec) contains ≥ 6 entries linking the three documents | | |
| B15 | Verification checklist (§7 of Phase B spec) contains ≥ 25 binary checkboxes covering all three items | | |
| B16 | Final sign-off procedure: Nimrod review + completion report + v1.2.0 tag are explicitly required | | |
| B17 | "No Team 50 QA" rule for M11 is confirmed (per MANDATE-20260407-M11-SPECS) | | |

### 3.4 Cross-Package Consistency

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| X1 | Phase A does not reference any Phase B features as prerequisites (Phase A is self-contained for v1.1.0) | | |
| X2 | Phase B precondition is stated: "G-V1.1 PASS before M11 becomes active priority" | | |
| X3 | No version number conflicts: Phase A → v1.1.0; Phase B → v1.2.0 (consistent with ROADMAP v6.0) | | |
| X4 | Both specs reference the same CANONICAL_PROGRAM_BRIEF (`_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` BRIEF-20260407-PHASE-AB-CANONICAL) | | |
| X5 | The `basket_tier_resolver.py` spec in Phase A does not conflict with any M11 architectural decisions in Phase B | | |

---

## 4. Preflight Result Format

Team 190 files its findings at:
`_COMMUNICATION/TEAM_190/reports/2026-04-08_PHASES_AB_LOD400_VALIDATION_TEAM190.md`

Use the following format:

```markdown
# Team 190 — Package Validation: Phase A & B LOD400 Specs

Date: YYYY-MM-DD
Package: VALREQ-20260408-PHASES-AB
Result: PASS / PASS_WITH_NOTES / FAIL

## Checklist Results
[Table with G1–G8, A1–A16, B1–B17, X1–X5 — PASS/FAIL/N/A per item]

## Findings (FAIL items only)
[Numbered list: finding, location in document, recommended fix]

## Notes (advisory, non-blocking)
[Any observations that do not constitute FAIL but warrant Team 100 attention]

## Decision
PASS → Team 100 may proceed to hand Phase A to Team 10 and begin Phase B authoring
FAIL → Team 100 must address all FAIL items and resubmit
PASS_WITH_NOTES → Team 100 may proceed; notes are advisory
```

---

## 5. Timeline

Team 190 is requested to complete this preflight within **1 session**. If any FAIL items are found, Team 100 will address and resubmit the same day.

---

## 6. Binding References

| Document | Path |
|----------|------|
| Phase A LOD400 spec | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` |
| Phase B LOD400 spec | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md` |
| Canonical program brief | `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` |
| ROADMAP | `_COMMUNICATION/ROADMAP.md` (v6.0) |
| CQ master arch approval | `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` |
| v1.1.0 consolidated mandate | `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` |
| G-V1.1 QA mandate | `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` |
| M11 specs mandate | `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` |

---

**Submitted by:** Team 100 (Architecture)  
**Document ID:** VALREQ-20260408-PHASES-AB  
**Date:** 2026-04-08
