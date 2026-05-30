---
id: MANDATE_SFA-S003-P002-WP-UI-patch04-ARCHIVE_v1.0.0
from: team_100 (Chief Architect)
to: team_191 (Git/Files/Archive)
cc: team_00, team_10, team_50, team_190
date: 2026-05-30
type: archive_mandate
wp: SFA-S003-P002-WP-UI-patch04
trigger: ADR042 closure — team_190 L-GATE_V R2 PASS (non-Claude)
status: EXECUTED
---

# Archive Mandate — WP-UI-patch04 (Crop-book completeness + global navigation)

L-GATE_V **R2 PASS** (team_190, non-Claude) at build a7a787a, deployed live to uPress
`sfa.nimrod.bio`. Per ADR042: archive then LOD500_LOCKED.

## Request (executed in this team_100 session, team_191 steward role)
Produce `_archive/SFA-S003-P002-WP-UI-patch04/ARCHIVE_MANIFEST.md`:
- gate chain: E (team_00) → S (team_100) → B (team_10 Sonnet A∥B→C) → QA (team_50 Haiku) →
  DEPLOY (team_100 → uPress) → V R1 FAIL → remediation → V R2 PASS (team_190)
- build a7a787a; cross-engine builder Sonnet ≠ QA Haiku ≠ validator non-Claude (IR#1)
- artifacts: BUILD_REPORT (team_10), QA_REPORT (team_50), L-GATE_V mandate + R1 verdict +
  R2 mandate + R2 verdict (team_190)
- preserved in place: LOD400_spec.md, live `sfa_delivery/` + `sfa_ingest_push.py`, roadmap row

## Open / carried forward (P2 — NOT part of "complete")
- `crop_cover_crops` re-seed (source data is PDF-parse junk; not pushed; page empty-state).
- market→crop-book convenience cross-links resolve 0 live (name-match miss; suppressed, no 404).
- `crop_knowledge_notes` 100% internal-gated → §Notes empty by design (governance gate honored).

— team_100 (Claude Opus 4.8) 2026-05-30
