---
id: DECISION-SFA-S003-P002-WP-A-LOD200-2026-05-23
type: DECISION_RECORD
from: team_00 (Nimrod, Principal)
to: team_110, team_100, sfa_build
date: 2026-05-23
session_context: LOD200 advisory review — SFA-S003-P002-WP-A Data Enrichment Architecture
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md
status: FINAL — LOD200_LOCKED (team_00 advisory PASS)
---

# DECISION — SFA-S003-P002-WP-A LOD200 Advisory Review

## §1  Status

**LOD200 APPROVED.** All Q1–Q7 resolved. team_110 is authorized to finalize LOD200 v1.1.0.
team_100 routes to L-GATE_S after LOD200_LOCKED commit.

---

## §2  Decisions

### Q1 — Reconciler Architecture

**DECISION: A-1 (Weighted-Mean Blend) — ACCEPTED with two mandatory additions:**

**Addition 1 — General Outlier Rejection for Weighted-Mean:**
Any source value that deviates excessively from the distribution (error or extreme
outlier, not just domain-specific rules) must be excluded from the weighted-mean blend.
The implementation must apply a statistical outlier gate (Z-score or IQR method) per
field across all non-outlier-rejected source values before blending.
This is in addition to (not instead of) the existing domain-specific outlier rules
(e.g., DTM < 20 for leaf crops → OUTLIER_REJECTED).

**Addition 2 — Extended Source Hierarchy for Future Layers:**
The source taxonomy must be designed to accommodate two additional future source classes
not yet in the current spec:
- **Class NI (Nimrod-Input):** Files or links that team_00 will directly supply —
  crop data sheets, reference tables, external datasets curated by Nimrod. Trust
  position: between EX and PR. Suggested weight: 0.85. This class may be empty
  initially but the registry must reserve the slot.
- **Class UC (User-Community):** Future user-submitted data. Trust position: lowest,
  below WB. Suggested weight: 0.15. UC data requires a moderation gate before
  inclusion in weighted-mean (is_moderated flag or equivalent). This class is
  design-only in WP-A — no UC importer in scope yet.

**Updated trust hierarchy:**

| Class | Weight | Notes |
|-------|--------|-------|
| EX | 1.0 | Hard override — always wins, no blend |
| NI | 0.85 | Nimrod-provided files/links — very high trust |
| PR | 0.70 | JMF MasterClass |
| OP | 0.55 | Tend operational (multi-year → 0.75 if ≥3 years) |
| MK | 0.40 | OMA market index |
| WB | 0.30 | Web / 3rd-party |
| UC | 0.15 | User-Community — moderation gated |

### Q2 — UI Range Display

**DECISION: YES — surface both min/max range AND confidence score.**

### Q3 — OMA Market Price Scope

**DECISION: WP-B** — OMA integration deferred to Phase 2.

### Q4 — Web Sources

**DECISION: DEFER scope definition to WP-B eligibility.**
Nimrod will provide files or links as NI-class input within WP-A build period.
Web sources (WB class) are design-registered in WP-A but no importer in scope.

### Q5 — Confidence in Public SPA

**DECISION: YES** — confidence visible in public WordPress SPA.
Format: simplified (e.g., 1–3 dot quality indicator), not raw 0.0–1.0 score.

### Q6 — GCR_1 (models.py authorization)

**DECISION: PRE-AUTHORIZED by team_00. No separate GCR artifact required.**
This decision record serves as the authorization for the builder to modify
`organic_market_agent/crop_book/models.py` to add the three columns to
`CropVarietySourceValue` (trust_tier, confidence_weight, is_outlier_rejected)
as part of migration 042. team_100 references this record in the builder dispatch.

### Q7 — WP Structure

**DECISION: B-1 — Two separate WPs (WP-A + WP-B).**

---

## §3  Binding Constraints Added by This Decision

1. **Outlier gate is mandatory** for weighted-mean, not optional — add to AC matrix in LOD400.
2. **Source registry must reserve NI + UC slots** even if no importer exists in WP-A.
3. **NI importer architecture** (file/link → DB ingestion) must be sketched in LOD200 §5
   even if the actual files/links arrive during the WP-A build window.
4. **UC moderation gate** — LOD200 must specify the design contract (even if implementation
   is WP-B+), so the schema is compatible.

---

## §4  Authority Record

Approved by: **team_00 (Nimrod)** — in-session, 2026-05-23
Recorded by: team_110
Binding on: team_100 (routing + roadmap), sfa_build (builder dispatch)
GCR_1 pre-authorization: **GRANTED** by team_00 per this record

---

*DECISION v1.0.0 — 2026-05-23 | SFA-S003-P002-WP-A LOD200 Advisory PASS*
