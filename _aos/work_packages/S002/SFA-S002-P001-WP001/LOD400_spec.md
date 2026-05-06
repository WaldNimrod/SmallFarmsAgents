# LOD400 — SFA-S002-P001-WP001 — M10 Thaw + Completion

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP001
**Type:** LOD400_SPEC
**Status:** STUB — full LOD400 authoring pending (next phase)

---

## Scope (carried from program package §4)

Revive parked work from `cursor/m10-doc-mandates-spike` (commit `bb981ed`):
- Migrations 072 (`cq_p01_alias_batch.py`), 073 (`src_wa_pending_manual.py`)
- `organic_market_agent/normalizer/basket_tier_resolver.py` + tests (PRD025/026/027 small/medium/large basket tiers)
- LOD400 communications v1.1, dev stack docs, SQL verification scripts

Reconcile against current main (58 commits ahead). Deliverable: clean rebase or extracted-and-reapplied changes, all tests green.

## Pending sections (to be authored in LOD400 phase)

- Acceptance Criteria (AC-01 .. AC-NN)
- File-level change list (every file to add/modify/delete)
- Test plan (unit + integration)
- Migration safety review (072/073)
- Conflict-surface analysis (M10 spike vs current main)
- Cross-references to canon (PRD025/026/027 ARCH spec)

## References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Source branch: `cursor/m10-doc-mandates-spike@bb981ed`

*Stub created during program initialization. Full LOD400 spec required before L-GATE_S verdict.*
