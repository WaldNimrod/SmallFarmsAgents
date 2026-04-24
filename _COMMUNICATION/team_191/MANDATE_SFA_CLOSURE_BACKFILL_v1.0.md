---
id: MANDATE_SFA_CLOSURE_BACKFILL_v1.0
from: team_100 (Chief System Architect)
to: team_191 (Git, Archive & File Governance)
date: 2026-04-24
type: ARCHIVE_CLOSURE_BACKFILL
project: SmallFarmsAgents (spoke)
status: OPEN
authority: ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md
---

# Archive Closure Backfill Mandate — SmallFarmsAgents

Audit of 1 COMPLETE WP: **0 CLEAN, 1 needs action.**

---

## Cat B — lod_status=LOD500, not LOD500_LOCKED, no archive (1 WP)

| WP ID | lod_status |
|-------|-----------|
| SFA-S001-P001-WP001 | LOD500 |

Action: create `_archive/SFA-S001-P001-WP001/`, copy `_aos/work_packages/SFA-S001-P001-WP001/` if exists,
write ARCHIVE_MANIFEST.md, update DB to LOD500_LOCKED.

---

## Completion

Write report to: `_COMMUNICATION/team_191/REPORT_SFA_CLOSURE_BACKFILL_v1.0.md`

Working directory: /Users/nimrod/Documents/SmallFarmsAgents/
