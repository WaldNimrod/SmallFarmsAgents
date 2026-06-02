# Team 10 — M11 specification program orchestration (post–G-V1.1)

**Document ID:** HANDOFF-20260330-M11-ORCH-TEAM10  
**Date:** 2026-03-30  
**Issued by:** Team 10 (orchestration draft; architecture binding docs remain Team 100)  
**Status:** DRAFT — **do not execute until G-V1.1 PASS** (precondition in Phase B LOD400 spec)

---

## Purpose

Package 2 of the program (v1.2.0, **specification-only** milestone M11) is **not** v1.1.0 code work. Team 10’s role is **orchestration**: schedule Team 100 authoring, ensure Team 80 inputs where required, route Nimrod review, and file cross-team artifacts on time.

---

## Governing documents (read order)

1. [docs/GLOSSARY.md](../../docs/GLOSSARY.md)
2. [_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md](../TEAM_100/reports/2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md) (SPEC-20260408-PHASE-B-LOD400)
3. [_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md](../TEAM_100/MANDATE_M11_SPECS_TEAM100.md)
4. [_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md](../TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md)

Conflict rule: same as v1.1 HANDOFF — **spec wins**; delta reports to Team 100.

---

## Preconditions

- **G-V1.1 PASS** for v1.1.0 (OrganicMarketAgent release gate).
- Team 100 capacity for three M11 deliverables (Items 8, 9, 10 per Phase B spec).

---

## Actor map

| Actor | Responsibility |
|-------|----------------|
| **Team 100** | Author M11 documents; verification checklist §6 of Phase B spec |
| **Team 80** | Input to Item 9 (FarmCostAgent / CostModel bridge) per Phase B spec |
| **Nimrod** | Review and sign-off; tag **v1.2.0** when criteria met |
| **Team 10** | Orchestration only — **no production code** for M11 |
| **Team 50** | Not in critical path for M11 (docs-only milestone unless roadmap adds QA) |

---

## Execution order (from Phase B spec §2)

Follow **§2 Execution Order and Parallelism** in `2026-04-08_PHASE_B_LOD400_SPEC_TEAM100.md` exactly — including dependency **Item 8 before Item 10**.

Orchestration tasks for Team 10:

1. Confirm G-V1.1 PASS in `_COMMUNICATION/ROADMAP.md` or Team 50 findings.
2. Open a dated orchestration note in `_COMMUNICATION/TEAM_10/reports/` with a **living checklist** mirroring Phase B §6 verification items.
3. Request Team 80 artifacts needed for Item 9 (per spec §code-vs-plan table B1–B4).
4. Track Nimrod review gate; no `v1.2.0` tag messaging until Team 100 completion report is filed per Phase B spec.

---

## Handoffs (canonical)

| When | File location | Content |
|------|---------------|---------|
| Need Team 80 input | `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M11_TEAM80_REQUEST_TEAM10.md` | Item 9 questions, deadlines, file paths for handoff packs |
| Blocked on Nimrod | `_COMMUNICATION/TEAM_10/reports/BLOCKED_*` or dated READY note | `[USER ACTION REQUIRED]` |
| Spec ambiguity | `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_DELTA_REPORT_*` | No guessing |

---

## Exit criteria (summary)

- All three M11 documents exist, cross-referenced per Phase B §5.
- Team 100 §6 checklist complete + completion report filed.
- Nimrod review recorded.
- Repository tagged **v1.2.0** per Phase B spec.

---

*This handoff does not replace Team 100 mandates; it coordinates execution after v1.1.0 ships.*
