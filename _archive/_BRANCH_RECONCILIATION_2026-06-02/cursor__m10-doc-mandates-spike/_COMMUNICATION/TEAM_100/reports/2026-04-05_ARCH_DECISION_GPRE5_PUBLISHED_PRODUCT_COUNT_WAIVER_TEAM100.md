---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — G-PRE-5 Published Product Count (≥90) Waiver

**Decision ID:** ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER  
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA), Team 10 (Feature Dev), Nimrod (project lead)  
**Date:** 2026-04-05  
**Type:** AMENDMENT / GATE_CLARIFICATION  

---

## 1. Context

Team 50 executed `_COMMUNICATION/TEAM_50/QA_MANDATE_M13_PRE_GPRE_TEAM50.md` and filed `_COMMUNICATION/TEAM_50/reports/2026-04-05_M13_PRE_GPRE_QA_FINDINGS_TEAM50.md`. All G-PRE checks **G-PRE-1..4, G-PRE-6, G-PRE-7** passed. **G-PRE-5** measured **`len(public_report.json['products'])` = 76** after coordinated `catalog_renormalize` + `run_publisher`, below the literal **≥90** threshold in M13-PRE §4 / G-PRE-5.

The shortfall is **not** a pipeline defect: it follows **binding publish policy** (minimum distinct community sources per product, rolling aggregation window, and catalog rules) documented in `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` and Team 10 evidence. Reaching **≥90** published rows is a **data-breadth / time-window optimization**, not a blocker for **M13-B** (public product-details UI) when the rest of G-PRE is green.

**References:**

- `_COMMUNICATION/TEAM_50/reports/2026-04-05_M13_PRE_GPRE_QA_FINDINGS_TEAM50.md` — QA execution  
- `_COMMUNICATION/TEAM_50/QA_MANDATE_M13_PRE_GPRE_TEAM50.md` — §6 G-PRE-5, §8 CONDITIONAL PASS rule  
- `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md` — §4 combined gate  
- `_COMMUNICATION/TEAM_10/reports/2026-04-05_M13_PRE_DATA_FOUNDATION_TEAM10.md` — measured publish count  

---

## 2. Findings

| Item | Finding | Severity |
|------|---------|----------|
| G-PRE-5 literal threshold | **76** &lt; **90** under current publish rules | Medium (documentation / expectation only) |
| Other G-PRE criteria | All passed on certified workspace | — |
| M13-B dependency | Needs stable real data + publish path; **not** a hard floor of 90 distinct published products on day one | Low |

---

## 3. Decision

**Team 100 waives the literal G-PRE-5 requirement `published product count ≥ 90` for the M13-PRE G-PRE-1..7 gate cycle executed against the 2026-04-04/05 certified artifacts.**

- **Accepted state:** Any **`len(products)`** produced under the **same** publisher rules as that QA run, **provided** it reflects good-faith `catalog_renormalize` + `run_publisher` (not a broken or empty publish). The certified finding of **76** is **accepted** as sufficient for this waiver.
- **QA classification:** Per `QA_MANDATE_M13_PRE_GPRE_TEAM50.md` §8, **G-PRE-5** is **CONDITIONAL PASS** with this document as the **written Team 100 waiver** (reference **Decision ID** above).
- **Ongoing work:** Team 10 may continue **optional** breadth improvements (sources, aliases, window tuning) to increase published product count; **no** re-gate on G-PRE-5 alone until Team 100 revises this decision.

**Authorized by:** Nimrod (project lead), recorded by Team 100.

### Gate Decision (G-PRE)

| Gate | Status | Notes |
|------|--------|-------|
| G-PRE-5 | CONDITIONAL PASS | Waiver **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**; literal ≥90 waived for this cycle |
| G-PRE-1..7 (combined) | CONDITIONAL PASS | All other checks PASS; G-PRE-5 closed via waiver |

---

## 4. Mandates Issued

**None.** Team 10 proceeds with M13-B per roadmap; Team 50 may annotate findings with this waiver reference without a full re-run unless a future mandate requires it.

---

## 5. Next Steps

| Team | Action | When |
|------|--------|------|
| Team 50 | Cite this decision in G-PRE findings; record **CONDITIONAL PASS** for G-PRE-5 / combined gate | Immediately |
| Team 10 | Continue M13-B; treat ≥90 as **stretch** for publish breadth, not a stop-ship | Ongoing |

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-05*  
*This decision is binding on all teams unless overridden by Nimrod.*
