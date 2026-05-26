---
id: SFA-S003-P002-WP-C4-LOD200
wp: SFA-S003-P002-WP-C4 — Web Sources (multi-engine team_80 scout output)
gate: L-GATE_S (LOD200 — placeholder pending team_80 multi-engine feedback)
status: PRE_LOD400_PENDING_TEAM_80_FEEDBACK
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-A
  - SFA-S003-P002-WP-B (LOD500_LOCKED)
depends_on: [SFA-S003-P002-WP-C1]
soft_depends_on: [team_80 web scout feedback from multiple engines]
brief_ref: _COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/MISSION_v1.0.0.md
mission_status: AWAITING_TEAM_80_MULTI_ENGINE_FEEDBACK
---

# LOD200 — WP-C4: Web Sources Integration (multi-engine team_80 scout)

## 1. Mission

Ingest the consolidated shortlist of free / open web crop data sources
identified by **team_80 web scout** (running on multiple engines: Perplexity,
ChatGPT, Claude Chat, Gemini). User team_00 will route team_80's
prompt to each engine, collect their FINDINGS, and team_10 will merge them into
a single consolidated mandate for WP-C4 LOD400.

**Why multi-engine:** different web search engines find different sources;
running team_80 on 3-4 engines maximizes recall + cross-validates citations.

## 2. Current status (2026-05-26)

| Step | Status |
|------|--------|
| Mission filed | ✅ `_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/MISSION_v1.0.0.md` |
| Pre-approval granted | ✅ (team_00 in-session) |
| Activation prompt ready | ✅ `_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/ACTIVATION_PROMPT.md` (inline web-session mode) |
| **Multi-engine execution** | ⏳ **IN PROGRESS** — team_00 routing to ≥3 engines |
| Feedback consolidation | ⏳ pending |
| WP-C4 LOD400 authoring | ⏳ blocked on feedback |

## 3. Anticipated in-scope (refined after feedback)

Based on team_80's MISSION §2 gap list (HIGH-priority pull):

- **HIGH-gap candidates (likely):**
  - USDA PLANTS / GRIN database (germination temp, hardiness zone per crop)
  - FAO ECOCROP (environmental requirements per crop, EN)
  - Cornell / UC Davis / Penn State extension structured tables
  - שה"ם Israeli planting calendars (if not already covered by C1+C2)
  - Mediterranean climate adaptation databases (ICARDA, CIHEAM)
  - Companion planting structured matrices

- **MEDIUM-gap candidates (possibly):**
  - Seed weight / seeds-per-gram databases
  - NPK demand databases (Cornell, university extension)
  - EPPO Global Database (pest/disease taxonomy)
  - Open seed networks (Seed Savers, Real Seeds)

- **LOW-gap candidates (skip unless feedback strongly recommends):**
  - Pest/disease imagery databases (don't have image use yet)
  - Cover crop databases (already covered by C1 L12)

## 4. Out-of-scope (irrespective of feedback)

- Subscription-only databases
- Sources without clear license/TOS for data extraction
- Sources requiring web scraping of dynamic content (defer; need separate WP)
- Sources duplicating PR/OP/NI coverage already loaded by C1+C2+C3

## 5. Data model (anticipated)

Probably no new tables — most web sources fit existing:
- `crop_variety_source_values` for scalar fields
- `crop_knowledge_notes` (extend `note_type` enum if needed) for narrative
- `crop_planting_calendar` (from C1) for any new regional calendar sources

**Possible new table** (if multi-engine feedback strongly recommends):
`crop_pest_disease_taxonomy` — structured pest/disease reference (deferred to
LOD400 if needed).

## 6. Trust-layer placement (anticipated)

| Source quality | Tier | Weight |
|----------------|------|--------|
| USDA / FAO / official gov databases | PR | 0.70 |
| University extension (Cornell, UC Davis) | PR | 0.70 |
| Seed company tech sheets (JSS, Real Seeds) | OP | 0.55 |
| Mediterranean specialty (ICARDA) | PR | 0.70 |

NI tier reserved for explicit user-curated overrides (not auto from web).

## 7. Dependencies

- Hard: WP-C1 LOD500_LOCKED (need consolidated baseline before adding more sources)
- Hard: team_80 multi-engine FEEDBACKS consolidated by team_10
- Soft: WP-C2 + WP-C3 should also be advanced to avoid mid-stream schema changes

## 8. LOD500_LOCKED untouched — same as C1/C2/C3

## 9. GCR requirements

**UNKNOWN** — depends on feedback. If a recommended source requires a new
table → file GCR before LOD400 lock. If only enum extensions → additive
migration sufficient.

## 10. AC count target: TBD (~8-15 depending on candidate count)
## 11. Test count target: TBD (~10-20)

## 12. Open questions (to be resolved by team_80 feedback)

1. How many INGEST-recommendation candidates do the multi-engine scouts agree
   on? (Consensus = higher confidence; divergence = needs team_00 arbitration.)
2. Which specific gaps remain UNCOVERED even after C1+C2+C3 ingest?
3. Are there sources that require web scraping vs simple download? (Scraping
   may need separate WP-D.)
4. License classification of recommended sources — any ambiguous ones to defer?

## 13. Activation path

When team_80 multi-engine FEEDBACKS arrive:
1. team_10 (this session or fresh) consolidates 3-4 FINDINGS reports into
   `_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/CONSOLIDATED_FINDINGS_v1.0.0.md`
2. team_10 authors WP-C4 LOD400 referencing consolidated findings
3. Roadmap entry updated: `lod_status: LOD400_LOCKED`, `current_lean_gate: L-GATE_B`
4. team_190 L-GATE_S validation
5. team_10 builder mandate
6. Standard build → L-GATE_V → LOD500_LOCKED → COMPLETION_REPORT flow

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.
LOD400 deferred pending team_80 multi-engine feedback consolidation.*
