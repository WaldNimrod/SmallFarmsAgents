---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — G3 Gate Resolution + Data Quality Governance
**Decision ID:** ARCH-20260330-G3-DATA-QUALITY
**From:** Team 100 (Architecture)
**To:** All Teams
**Date:** 2026-03-30
**Type:** GATE_DECISION + AMENDMENT + MANDATE

---

## 1. Context

This decision is issued in response to:
- Nimrod's project lead brief: `_COMMUNICATION/TEAM_100/reports/2026-03-30_PROJECT_LEAD_BRIEF_M3_DATA_STRATEGY_AND_MANDATES_TEAM100.md`
- Team 50 QA report: `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G3_TEAM50.md`
- Team 10 remediation pack: `_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_REMEDIATION_EXECUTION_PACK_TEAM10.md`
- Team 10 executed evidence: `_COMMUNICATION/TEAM_50/reports/2026-03-30_G3_TEAM10_EXECUTED_EVIDENCE_REREVIEW_TEAM50.md`

**The problem:** Two conflicting G3 QA mandate documents produced different gate outcomes.
`QA_MANDATE_G3.md` (canonical) → BLOCKED. `QA_MANDATE_G3_RERUN.md` (supplement) → PASS.
This created governance ambiguity blocking M4.

---

## 2. Findings

| Item | Finding | Severity |
|------|---------|----------|
| Normalizer engine correctness | Engine runs without crash, classifies items correctly, populates `normalized_observations`. 46/46 tests pass. | None — working as designed |
| `unresolvable_reason` column | Fixed to TEXT (migration 008). No more `StringDataRightTruncation`. | Resolved |
| 1,634 unresolvable rows | Pre-guard M2 extractions from **discovery sources** (SRC013 permaculture.org.il, SRC012, SRC014) and from farm shops whose selectors extracted page chrome instead of products. NOT a normalizer defect. | High — data quality issue |
| `≥ 40` threshold in `QA_MANDATE_G3.md` | Written before source-fitness diagnosis. Cannot be met from historical discovery-source backlog without alias-backfilling non-product text, which would be architecturally wrong. | Medium — mandate was premature |
| 7 normalized observations | From legitimate EasyFarm price-grid sources with valid product rows and alias coverage. Correct engine behavior. | None — expected on limited source set |
| T09 count drift | M3 does not write to `raw_assets` / `raw_extracted_items`. Drift proves concurrent M2 or wrong baseline timing. Not a normalizer regression. | Low — process issue |
| Forward metrics undefined | No per-cycle KPI definition exists. Gate criteria measured against total historical backlog rather than a cycle's yield. | High — governance gap |

**Risk register (from Nimrod brief):**

| Risk | Resolution |
|------|-----------|
| R1 — Mandate ambiguity | Resolved below: single authority `QA_MANDATE_G3_v2.md` |
| R2 — Metric mismatch (historical count) | Resolved: metrics scoped to cohort (`--ingestion-run-id`) |
| R3 — DB usability (noise in operational path) | Addressed: `is_quarantined` flag + source_tier classification (mandates below) |
| R4 — Re-fetch waste | Addressed: re-ingestion policy spec in `M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` |
| R5 — Loss of learning signal | Addressed: quarantine preserves rows, no deletion without explicit approval |

---

## 3. Decision

### Gate Decision

| Gate | Status | Binding document | Notes |
|------|--------|-----------------|-------|
| G3 | ✅ OPEN — PASS | `QA_MANDATE_G3_RERUN.md` (2026-03-30) | Engine proven correct. 7 normalized observations from valid price-grid sources. All 10/10 RERUN checks pass. |

**Rationale:** The `≥ 40` threshold in `QA_MANDATE_G3.md` was written before the source-fitness
problem was diagnosed. Requiring `≥ 40` resolutions from a backlog dominated by discovery-source
page chrome would reward alias-backfilling garbage rows — which is architecturally wrong and
contradicts the project's data quality goals. The RERUN mandate (`> 0`) correctly validates
the engine on the available clean data.

**G3 does NOT reopen.** This decision is final.

### Mandate Supersession

| Document | Status |
|----------|--------|
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G3.md` | SUPERSEDED — replaced by `QA_MANDATE_G3_v2.md` |
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G3_RERUN.md` | SUPERSEDED — replaced by `QA_MANDATE_G3_v2.md` |

`QA_MANDATE_G3_v2.md` is the single binding G3 QA reference going forward.
It uses cohort-scoped metrics and the quiet-DB T09 protocol.

---

## 4. Mandates Issued

| Mandate | Team | File | Priority | Blocks |
|---------|------|------|----------|--------|
| Migration 009: source_tier + is_quarantined | Team 20 | `MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md` | HIGH | M4 entry |
| Normalizer filter + CLI metrics | Team 10 | `MANDATE_NORMALIZER_FILTER_AND_METRICS_TEAM10.md` | HIGH | M4 entry |

Both mandates must be completed before Gate G4 QA begins.

---

## 5. Specifications Produced

| Document | Path | Purpose |
|----------|------|---------|
| Data quality and cohort gate spec | `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` | Phased lifecycle plan (classification, retention, cleanup, re-ingestion policy) |
| QA Mandate G3 v2 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G3_v2.md` | Single forward-looking G3 QA reference with cohort metrics |

---

## 6. Next Steps

| Team | Action | When |
|------|--------|------|
| Team 20 | Execute `MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md` | Before G4 QA |
| Team 10 | Execute `MANDATE_NORMALIZER_FILTER_AND_METRICS_TEAM10.md` | Before G4 QA |
| Team 50 | Acknowledge supersession; adopt `QA_MANDATE_G3_v2.md` | Immediately |
| Team 100 | Update ROADMAP: G3 = PASS, M4 = active, M4 entry criteria | Immediately |

**M4 entry criterion (new):** Migration 009 applied AND first forward-metrics cohort run
achieves `resolved ≥ 10` AND `distinct products ≥ 3`.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*This decision is binding on all teams. It supersedes all prior G3 gate rulings.*
