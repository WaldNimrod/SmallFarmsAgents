# LOD400 — SFA-S002-P001-WP002 — MyPIPS Source Integration + Branch Cleanup

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP002
**Type:** LOD400_SPEC
**Status:** STUB — full LOD400 authoring pending (next phase)

---

## Scope (carried from program package §4)

- Audit `cursor/mypips-communication-and-handoffs` MyPIPS portion: classify each store discovery as COMPLETED / FAILED / PARTIAL.
- Integrate COMPLETED sources into `organic_market_agent/sources/` (collectors).
- Document FAILED experiments in `_COMMUNICATION/TEAM_100/SFA-S002-P001/MYPIPS_AUDIT.md`.
- Complete PARTIAL sources where feasible.
- Final state: branch `cursor/mypips-communication-and-handoffs` is empty of in-scope work (raw material preserved).

## Critical constraint

**Tend farm exports (CSV/ZIP) + MasterClass PDFs MUST NOT BE MODIFIED OR MERGED.** Builders touch only the MyPIPS store-discovery portion of the branch. Raw material is reserved for the next dev phase.

## Pending sections (to be authored in LOD400 phase)

- MyPIPS audit deliverable schema (per-store: status / endpoint / parser / blocker / decision)
- Acceptance Criteria
- Source ingestion pattern (existing collectors structure)
- Branch cleanup procedure (filter-branch / interactive rebase / extract-and-discard)
- Raw material preservation verification

## Depends on

WP001 (M10 thaw provides updated source-handling layer).

## References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Source branch: `cursor/mypips-communication-and-handoffs@732121e`

*Stub. Full LOD400 spec required before L-GATE_S verdict.*
