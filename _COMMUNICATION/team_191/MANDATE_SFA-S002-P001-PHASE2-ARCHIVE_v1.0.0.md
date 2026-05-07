---
id: MANDATE_SFA-S002-P001-PHASE2-ARCHIVE_v1.0.0
from: team_100
to: team_191 (Git, Archive & File Governance)
date: 2026-05-07
type: ARCHIVE_MANDATE
project: SmallFarmsAgents (spoke)
status: OPEN
authority: ADR042 / Iron Rule #15
---

# Archive Mandate — SFA-S002-P001 Phase 2 Complete

Phase 2 is COMPLETE. WP001 + WP002 both LOD500_LOCKED.
Artifact archive required per Iron Rule #15 (ADR042).

## WPs to archive

| WP | Status | Artifacts location |
|----|--------|--------------------|
| SFA-S002-P001-WP001 | LOD500_LOCKED | `_COMMUNICATION/TEAM_10/SFA-S002-P001-WP001/` |
| SFA-S002-P001-WP002 | LOD500_LOCKED | `_COMMUNICATION/TEAM_10/SFA-S002-P001-WP002/` |

Also archive Phase 1 WPs still outstanding (from prior Phase 1 archive mandate):
- WP003, WP004, WP006, WP007, WP008 artifacts in `_COMMUNICATION/team_*/SFA-S002-P001-WP*/`

## Action

Move all completed WP artifacts to `_archive/SFA-S002-P001/` maintaining directory structure.
Commit: `archive(S002): Phase 1+2 WP artifacts → _archive/`

This resolves validate_aos.sh Check 15 (pre-existing FAIL across all Phase 1+2 sessions).

## Authority limits
- MAY move (not delete) artifacts to `_archive/`
- MAY NOT modify `_aos/roadmap.yaml` or `_aos/governance/`
- MAY NOT touch application source code

*Mandate issued 2026-05-07 by team_100.*
