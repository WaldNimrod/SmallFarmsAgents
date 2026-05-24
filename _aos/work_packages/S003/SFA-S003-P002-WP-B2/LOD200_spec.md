---
id: SFA-S003-P002-WP-B2-LOD200
type: lod200_placeholder
wp: SFA-S003-P002-WP-B2
version: 0.0.1-placeholder
status: PLACEHOLDER_PENDING_TEAM_110
parent_phase: S003-P002
created_at: 2026-05-24
created_by: team_10 (canonical placeholder under team_00 authorization)
---

# SFA-S003-P002-WP-B2 — LOD200 (PLACEHOLDER)

**This file is a PLACEHOLDER.** It exists so the roadmap `spec_ref` resolves
under validate_aos.sh Check 4. The real LOD200 specification is to be authored
by **team_110** per the activation prompt at:

`_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/ACTIVATION_PROMPT.md`

## Source of Truth

All program scope, data sources, schemas, and acceptance criteria targets are
defined in the canonical program brief:

`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`

## Mission (one-liner)

JMF PDF extraction layer — first concrete `NIImporter` subclass from the WP-A
skeleton. LLM-assisted extraction from THE MARKET GARDENER ebook + Fiche
Technique PDFs into structured per-crop knowledge fields. **NI tier** (hard
override). Depends on WP-B1 crop_id mappings.

## team_110 instructions

Replace this file with a full LOD200 spec. Pay special attention to:
- GCR_2 evaluation (new `crop_knowledge_notes` table relationship on `Crop`)
- LLM extraction caching contract (`data/jmf/extracted/` strategy)
- Cross-engine review of extracted JSON before commit

## Authorization

Registered in `_aos/roadmap.yaml` 2026-05-24 under team_00 in-session grant.
gate_history: L-GATE_E PASS by team_00. Awaiting LOD200 authoring → L-GATE_S.

---

_Placeholder authored by team_10 (Claude Sonnet 4.6) 2026-05-24._
