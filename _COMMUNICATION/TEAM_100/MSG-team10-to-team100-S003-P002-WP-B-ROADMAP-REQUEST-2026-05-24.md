---
id: MSG-team10-to-team100-S003-P002-WP-B-ROADMAP-REQUEST-2026-05-24
schema_version: aos_v1_team_messaging
from_team: team_10
to_team: team_100
type: roadmap_change_request
subject: "Register 3 new work packages (WP-B1/B2/B3) for S003-P002 — multi-source crop knowledge base"
date: 2026-05-24T00:00:00Z
related_wp: SFA-S003-P002-WP-B
expects_response: true
status: SENT
priority: NORMAL
artifact_paths:
  - _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
---

## Roadmap Registration Request — S003-P002-WP-B Program

Following the LOD500_LOCKED close-out of `SFA-S003-P002-WP-A` (commit `594cbc8`),
team_00 has directed expansion of the data layer to a 3-WP program. This MSG
requests canonical roadmap registration of the three new work packages.

**Source brief:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`

---

## Action required in hub `_aos/roadmap.yaml`

Append the following three entries after the existing `SFA-S003-P002-WP-A` block
(line ~768 in the spoke snapshot). Use the same indentation and YAML style as
the existing S003-P002 entries.

```yaml
- id: SFA-S003-P002-WP-B1
  label: "ספר גידולים: JMF Excel Base Layer — Multi-Source Knowledge Foundation"
  status: ELIGIBLE
  track: A
  effort: LARGE
  current_lean_gate: L-GATE_E
  lod_status: PRE_LOD200
  assigned_builder: sfa_build
  assigned_validator: external
  created_at: "2026-05-24"
  milestone_ref: "S003"
  depends_on: ["SFA-S003-P002-WP-A"]
  brief_ref: "_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md"
  notes: "JMF MasterClass Excel ingestion: CROP CHART + CROP ASSOCIATED TASKS +
    DIRECT SEEDING CHART + NURSERY CHART + CULTIVARS. New table
    crop_task_templates (migration 044). PR-tier source values populate
    enrichment baseline. Authorization pending team_00 LOD200 approval.
    Brief: PROGRAM_BRIEF_v1.0.0.md."
  profile: L0

- id: SFA-S003-P002-WP-B2
  label: "ספר גידולים: JMF PDF Extraction Layer — AI-assisted NI Source"
  status: PROPOSED
  track: A
  effort: LARGE
  current_lean_gate: L-GATE_E
  lod_status: PRE_LOD200
  assigned_builder: sfa_build
  assigned_validator: external
  created_at: "2026-05-24"
  milestone_ref: "S003"
  depends_on: ["SFA-S003-P002-WP-B1"]
  brief_ref: "_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md"
  notes: "Extract per-crop narrative knowledge from THE MARKET GARDENER book +
    Fiche Technique PDFs. Implements first concrete NIImporter subclass from
    WP-A skeleton. LLM-assisted extraction with cached JSON to
    data/jmf/extracted/. NI tier hard-override. May require GCR_2 (new
    crop_knowledge_notes table relationship on Crop model). Brief:
    PROGRAM_BRIEF_v1.0.0.md."
  profile: L0

- id: SFA-S003-P002-WP-B3
  label: "ספר גידולים: Tend Israel Adaptation Overlay — Local Layer"
  status: PROPOSED
  track: A
  effort: MEDIUM
  current_lean_gate: L-GATE_E
  lod_status: PRE_LOD200
  assigned_builder: sfa_build
  assigned_validator: external
  created_at: "2026-05-24"
  milestone_ref: "S003"
  depends_on: ["SFA-S003-P002-WP-B1"]
  brief_ref: "_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md"
  notes: "Tend TASKS.CSV pattern extraction (recurring templates only, whitelist
    enforced). Tend GREENHOUSE_PLAN population. Tend HARVESTS aggregated to
    crop_harvest_stats (no per-record insertion per team_00 directive). New
    migration 046. OP tier overlays JMF PR baseline via reconciler. Brief:
    PROGRAM_BRIEF_v1.0.0.md."
  profile: L0
```

---

## Program-level facts

| Fact | Value |
|------|-------|
| Phase parent | S003-P002 (open since 2026-05-23) |
| First completed WP in phase | WP-A → LOD500_LOCKED 2026-05-24 (commit `594cbc8`) |
| Three new WPs total | WP-B1 + WP-B2 + WP-B3 |
| Build sequence | B1 → (B2 + B3 in parallel) |
| Authorization scope | team_00 directive 2026-05-24 in-session |
| LOD200 author | team_110 (after handoff this session) |
| LOD400 validator | team_190 cross-engine (IR#1) |

## Iron Rule #4 compliance
This MSG is filed in `_COMMUNICATION/TEAM_100/` (team_100 inbox). The roadmap
mutation itself is **NOT** committed by team_10. Awaiting team_100 action.

---

*Sent 2026-05-24 by sfa_build (team_10 / Claude Sonnet 4.6).*
