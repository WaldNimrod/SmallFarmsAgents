---
id: MANDATE_SFA-S003-P002-WP-UI-patch01_L-GATE_V_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (Senior Constitutional Validator — NON-CLAUDE engine)
date: 2026-05-28
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-UI-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 CROSS-ENGINE MANDATORY. Builder=team_10 (Claude Sonnet). You MUST be a non-Claude engine (GPT-5.5/Cursor/Codex/Gemini). If you are any Claude model, STOP and decline — engine collision voids the gate."
blocked_by: "team_50 QA_PASS"
---

# L-GATE_V Mandate — SFA-S003-P002-WP-UI-patch01

**Constitutional + functional validation.** Final gate before LOD500_LOCKED.
Runs AFTER team_50 QA_PASS. Independent of builder + QA (cross-engine per IR#1).

## 1. Inputs
- Spec (19 ACs): `_aos/work_packages/S003/SFA-S003-P002-WP-UI-patch01/LOD400_spec.md`
- BUILD_REPORT: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI-patch01/BUILD_REPORT_v1.0.0.md`
- QA_REPORT: `_COMMUNICATION/team_50/SFA-S003-P002-WP-UI-patch01/QA_REPORT_v1.0.0.md`
- DECISION: `_COMMUNICATION/team_00/DECISION_WP-UI-followup_2026-05-28_v1.0.0.md`
- Builder branch: `claude/sfa-ui-patch01`

## 2. Validate — independently (do not trust BUILD/QA reports)
Re-verify all 19 ACs by direct execution. Then run the constitutional checks:

| # | Constitutional check | Pass condition |
|---|----------------------|----------------|
| C1 | Directory authority | builder touched only the 7 in-scope files + tests; no `_aos/` edits |
| C2 | IR#4 single roadmap writer | no `roadmap.yaml` change in builder commit |
| C3 | IR#1 cross-engine | builder = Sonnet, you = non-Claude; QA = Haiku (3 distinct) |
| C4 | No community write surface | no POST / no DB write / no `community_contributions` (LV-S-1 parent binding upheld) |
| C5 | Locked-file integrity | no LOD500_LOCKED parent WP-UI file modified beyond the 5 scoped code files |
| C6 | vendor/ policy | `vendor/` not committed (Option B) |
| C7 | Scope hygiene | unrelated parallel-session files (`data/jmf/`, `data/external_sources/`, `.env.example`, `CHANGELOG.md`) NOT in builder commit |
| C8 | Deferred-item honesty | A (og-default image) + D (8 heroes + `modules.php hero_url`) correctly deferred, not faked |

## 3. Output
- **VERDICT:** `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch01/LGATEV-VERDICT_v1.0.0.md`
  - Verdict: PASS | PASS_WITH_FINDINGS | FAIL
  - Your engine + version (must be non-Claude)
  - 19-AC independent results + C1..C8 results
  - Findings (id/severity/category/summary/owner) if any
  - Recommendation: advance to LOD500_LOCKED, or remediation loop
- Notify team_100 via `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-UI-patch01-LGATEV-VERDICT-2026-XX-XX.md`.

## 4. Notes
- DB is online (PostgreSQL 16.13) but this patch makes NO structured DB mutation
  (CommunityFeed reads a JSON file). No API-side verification needed for DB state.
- Deploy is explicitly OUT of this gate (gated on team_00 media → bundled deploy
  re-validation later). Validate code + governance only.
- This is a SMALL/LOW-risk patch; a clean PASS is expected. Flag any builder
  scope-creep (the parent WP-UI had an F-190 PROCESS finding for builder overreach
  — hold this build to the 7-file scope).
