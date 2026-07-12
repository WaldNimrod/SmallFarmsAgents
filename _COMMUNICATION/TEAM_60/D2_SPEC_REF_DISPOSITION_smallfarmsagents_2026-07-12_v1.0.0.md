---
id: D2_SPEC_REF_DISPOSITION_smallfarmsagents_2026-07-12_v1.0.0
type: DISPOSITION RECORD
from: team_60 (DevOps/Platform)
to: team_120 (Ambassador — custodian), team_100 (Chief System Architect)
date: 2026-07-12
domain: smallfarmsagents (SFA)
wp: AOS-V5-M11-WP-FLEET-VERSION-HYGIENE-SWEEP (hub-native, file-canonical — ADR034 R10)
re: CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md §6 (D2 masked Check-4 spec_ref)
---

# D2 spec_ref fix-or-waive — SFA — disposition record

Executes §6 of the centralized sweep review for SFA's 2 broken `spec_ref` items.

## 1. `SFA-S003-P004-WP-CB-CONTENT` — WAIVED

**Broken ref:** `spec_ref: "_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CONTENT/SPEC_2026-06-09_v1.0.0.md"`

**Verification:** fleet-wide `find . -iname "SPEC_2026-06-09*"` from the domain root returns zero results. The file
does not exist live or archived anywhere in the tree, despite the WP's own `_archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md`
citing it as an evidence artifact at line 32.

**Disposition:** WAIVE (not FIX) — the review's own rule is *"FIX (repoint) where the real artifact exists; formal
per-domain WAIVER where it is genuinely gone/never produced."* No real artifact exists to repoint to; nothing was
invented.

**Actions taken:**
- `_aos/roadmap.yaml`, `SFA-S003-P004-WP-CB-CONTENT` row — appended to the existing top-level `notes:` field:
  *"D2 spec_ref WAIVED per CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md §6 —
  SPEC_2026-06-09_v1.0.0.md pre-existing gap, never produced, not this sweep's. Per that review's §10 item 3, this
  waiver requires team_100 sign-off to count toward certified 0-FAIL — pending as of this pass."*
- `_archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md` — added a matching "2026-07-12 disposition (team_60)"
  addendum immediately after the existing pre-existing-gap note (line ~91-95), cross-referencing the roadmap note.
- `spec_ref` field itself was **left unchanged** (still points at the missing file) — waiving the gap is a status
  disposition, not a fabricated repoint. No document content invented.

**Outstanding:** per the review's §10 item 3, this waiver is **team_60's proposed disposition** but requires
**team_100 sign-off** before it counts toward a certified 0-FAIL for this domain. Flagged, not self-certified.

## 2. `SFA-S003-P001-WP001` — already fixed, no action

**Current ref:** `spec_ref: "_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md"`

**Verification (re-run this pass):** the file exists at that exact path (confirmed via `ls -la`, 27927 bytes,
dated 2026-05-23). The review listed this as *"spec_ref repoint outstanding since 2026-05-22"* — that repoint has
since been completed (by an earlier, unattributed pass) and the current `roadmap.yaml` state already reflects the
fix.

**Disposition:** already fixed, no action needed.

---
*team_60 · 2026-07-12 · M11 fleet version-hygiene sweep, SFA domain, D2 execution.*
