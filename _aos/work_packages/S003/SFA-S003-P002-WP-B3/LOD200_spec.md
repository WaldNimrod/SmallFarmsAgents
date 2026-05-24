---
id: SFA-S003-P002-WP-B3-LOD200
type: lod200_placeholder
wp: SFA-S003-P002-WP-B3
version: 0.0.1-placeholder
status: PLACEHOLDER_PENDING_TEAM_110
parent_phase: S003-P002
created_at: 2026-05-24
created_by: team_10 (canonical placeholder under team_00 authorization)
---

# SFA-S003-P002-WP-B3 — LOD200 (PLACEHOLDER)

**This file is a PLACEHOLDER.** It exists so the roadmap `spec_ref` resolves
under validate_aos.sh Check 4. The real LOD200 specification is to be authored
by **team_110** per the activation prompt at:

`_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/ACTIVATION_PROMPT.md`

## Source of Truth

All program scope, data sources, schemas, and acceptance criteria targets are
defined in the canonical program brief:

`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`

## Mission (one-liner)

Tend Israel adaptation overlay — **OP tier** layers on the JMF PR baseline.
Tend TASKS.CSV pattern extraction with **recurring template whitelist**
(team_00 directive: no one-off records). Tend HARVESTS.CSV aggregated to
`crop_harvest_stats` (statistics only — NEVER per-record). Depends on WP-B1.

## team_110 instructions

Replace this file with a full LOD200 spec. Pay special attention to:
- Tend task_type whitelist (confirm final list with team_00 before LOD400 lock)
- Harvest aggregation grain — by (crop, year, season); confirm season enum
- crop_harvest_stats table additive scope (migration 046)
- Engine integration: OP tier blends with JMF PR via WP-A reconciler

## Authorization

Registered in `_aos/roadmap.yaml` 2026-05-24 under team_00 in-session grant.
gate_history: L-GATE_E PASS by team_00. Awaiting LOD200 authoring → L-GATE_S.

---

_Placeholder authored by team_10 (Claude Sonnet 4.6) 2026-05-24._
