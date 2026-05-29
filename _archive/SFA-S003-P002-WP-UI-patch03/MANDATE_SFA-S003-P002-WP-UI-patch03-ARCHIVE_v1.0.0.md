---
id: MANDATE_SFA-S003-P002-WP-UI-patch03-ARCHIVE_v1.0.0
from: team_100 (Chief Architect)
to: team_191 (Git/Files/Archive)
cc: team_00, team_10, team_50, team_190
date: 2026-05-29
type: archive_mandate
wp: SFA-S003-P002-WP-UI-patch03
trigger: ADR042 closure — team_190 L-GATE_V PASS (non-Claude Composer 2.5)
status: EXECUTED
---

# Archive Mandate — WP-UI-patch03 (Crop-book detail UX + agronomic data surfacing)

L-GATE_V **PASS** issued by team_190 (Composer 2.5 / Cursor, non-Claude — IR#1) at build 509c5f5,
deployed live to uPress `sfa.nimrod.bio`. Per ADR042, archive then LOD500_LOCKED.

## Request (executed in this team_100 session, team_191 steward role)
Produce `_archive/SFA-S003-P002-WP-UI-patch03/ARCHIVE_MANIFEST.md`:
- gate chain: E (team_00) → S (team_100) → B (team_10 Sonnet A∥B) → QA (team_50 Haiku) →
  DEPLOY (team_100 → uPress) → V (team_190 Composer 2.5, PASS)
- build 509c5f5 (initial 1e98c1a + team_00-directed fixes 2e381d7 backfill, 509c5f5 delta-compare)
- cross-engine: builder Sonnet ≠ QA Haiku ≠ validator Composer (IR#1)
- artifacts: BUILD_REPORT (team_10), QA_REPORT (team_50), L-GATE_V_MANDATE + L-GATE_V_VERDICT (team_190)
- preserved in place: LOD400_spec.md, live `sfa_delivery/` + `sfa_ingest_push.py`, roadmap row

## Open / carried forward (NOT part of this archive's "complete")
- Durability: home-server Postgres at head 034 (no crop schema) → crop data re-pushed manually
  from Mac; canonical pipeline alignment (server DB upgrade) is a separate follow-up.

— team_100 (Claude Opus 4.8) 2026-05-29
