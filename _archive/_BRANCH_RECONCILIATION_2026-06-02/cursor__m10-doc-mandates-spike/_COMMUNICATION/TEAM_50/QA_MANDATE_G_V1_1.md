# QA Mandate — Gate G-V1.1 (Consolidated CQ + M10.x + M9C)

**Mandate ID:** QA-MANDATE-G-V1-1  
**Date:** 2026-04-08  
**Version:** 1.1 (updated 2026-04-08 — added LOD400 spec + EXEC mandate references; T05 criterion clarified)  
**Issued by:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**Preflight:** Team 190 (constitutional validation of completion package before this QA)  
**Scope:** All work in `MANDATE_V1_1_CONSOLIDATED_TEAM10.md` (LOD200 base) superseded at implementation detail by:

- **Primary binding spec:** `SPEC-20260408-PHASE-A-LOD400` → `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`
- **Execution order:** `MANDATE-20260408-V1-1-LOD400-EXEC` → `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md`
- **Coordination:** `HANDOFF-20260408-V1-1-ORCH-TEAM10` → `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md`

When LOD400 spec and the consolidated mandate conflict, **the LOD400 spec governs** at implementation detail. The consolidated mandate remains binding for policy decisions not addressed at LOD400.  
**Precondition:** Team 10 completion report + Team 190 PASS

---

## 1. Context

Version 1.1.0 consolidates 9 catalog quality packages (CQ-P01 through CQ-P09), M10.x pragmatic optimization, and M9C content placeholder into a single release gate. This replaces the previous per-package QA cycles.

**Binding references:**
- `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md`
- `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` (ARCH-20260406-CQ-MASTER)
- `_COMMUNICATION/TEAM_100/reports/2026-04-07_VERSION_1_0_0_DECLARATION_TEAM100.md`

---

## 2. Test Cases

### T01 — Regression: Full Test Suite
**Type:** Regression  
**Priority:** CRITICAL  
**Command:** `pytest tests/ -m "not upress"`  
**Pass criterion:** 0 failures. Skipped tests documented.

### T02 — Alias Resolution: Unresolvable Count
**Type:** Data Quality  
**Priority:** CRITICAL  
**SQL:**
```sql
SELECT COUNT(DISTINCT raw_product_name)
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable' AND is_quarantined = false;
```
**Pass criterion:** Result <= 20

### T03 — Alias Resolution: SRC021 Count
**Type:** Data Quality  
**Priority:** HIGH  
**SQL:**
```sql
SELECT COUNT(DISTINCT rei.raw_product_name)
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE s.code = 'SRC021' AND rei.extraction_status = 'unresolvable' AND rei.is_quarantined = false;
```
**Pass criterion:** Result <= 10

### T04 — Published Product Count
**Type:** Data Quality  
**Priority:** CRITICAL  
**Method:** Parse `output/public/public_report.json`, count `products[]` entries  
**Pass criterion:** Count >= 77 (no regression from v1.0.0)

### T05 — PRD027 Duplicate Resolution
**Type:** Data Quality  
**Priority:** HIGH  
**Method:** Parse `output/public/public_report.json`, count entries with `product_id = "PRD027"`  
**Pass criterion:** ≤ 1 entry for PRD027 (0 = below publish threshold: PASS with note; 1 = confirmed large-basket observations: PASS; 2+ = FAIL — duplicate not deduped)

### T06 — Cherry/Tomato Guard
**Type:** Data Integrity  
**Priority:** CRITICAL  
**SQL:**
```sql
SELECT COUNT(*) FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001' AND pa.is_active = true
  AND (pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
    OR pa.alias_text_normalized LIKE '%צ''רי%');
```
**Pass criterion:** Result = 0

### T07 — Inactive Basket Codes Guard
**Type:** Data Integrity  
**Priority:** CRITICAL  
**SQL:**
```sql
SELECT COUNT(*) FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029') AND pa.is_active = true;
```
**Pass criterion:** Result = 0

### T08 — Eggs Source x Unit Matrix
**Type:** Documentation  
**Priority:** HIGH  
**Method:** Verify completion report contains source x unit matrix for PRD067  
**Pass criterion:** Matrix present with all active sources; >= 90% observations correctly mapped

### T09 — Passion Fruit Classification
**Type:** Documentation  
**Priority:** HIGH  
**Method:** Verify completion report contains source x unit matrix for PRD072 with per-source classification  
**Pass criterion:** Matrix present; each "יחידה" source classified as genuine per-fruit or mislabeled

### T10 — Blueberries Research Table
**Type:** Documentation  
**Priority:** MEDIUM  
**Method:** Verify completion report contains `source x pack_description x grams_if_known` table for PRD086  
**Pass criterion:** Table present; >= 50% of sources have grams determined

### T11 — CSA Basket Tier Assignment
**Type:** Functional  
**Priority:** HIGH  
**Method:** Query `normalized_observations` for basket products from CSA sources; verify tier assignment logic  
**Pass criterion:** >= 1 CSA source produces reproducible tier assignment to PRD025/026/027

### T12 — Pantry ADR
**Type:** Documentation  
**Priority:** MEDIUM  
**Method:** Verify Team 100 signed ADR exists for PRD087–PRD100 pack weight comparison at `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md`  
**Pass criterion:** ADR document present with chosen approach, authored by Team 100 (not Team 10). If ADR is not yet filed, verify the C3 notification report from Team 10 exists — this is an intermediate PASS condition.

### T13 — M9C WhatsApp Protocol
**Type:** Documentation  
**Priority:** HIGH  
**Method:** Verify `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` exists with intake process  
**Pass criterion:** Document present with submission, processing, and pipeline integration steps

### T14 — M9C Blog Placeholder
**Type:** Functional  
**Priority:** MEDIUM  
**Method:** Verify blog placeholder template exists and public page vision block links to it  
**Pass criterion:** Placeholder ready for Team 80 content injection

### T15 — Privacy Audit
**Type:** Security  
**Priority:** CRITICAL  
**Method:** Grep `output/public/public_report.json` and all `output/public/*.html` for source codes (SRC0xx), source names, source URLs  
**Pass criterion:** Zero matches. Any violation = automatic FAIL.

### T16 — Pipeline End-to-End
**Type:** End-to-End  
**Priority:** CRITICAL  
**Method:** Full pipeline run: `run_ingestion --normalize` -> `run_aggregator` -> `run_publisher`  
**Pass criterion:** Pipeline completes without error; published artifacts valid

---

## 3. Gate Decision Matrix

| Result | Condition |
|--------|-----------|
| **PASS** | All CRITICAL pass + all HIGH pass + MEDIUM at least documented |
| **CONDITIONAL PASS** | All CRITICAL pass + at most 2 HIGH have documented waivers from Team 100 |
| **FAIL** | Any CRITICAL fails, OR 3+ HIGH fail, OR privacy violation (T15) |

**Privacy override:** Any T15 failure is an automatic FAIL regardless of other results.

---

## 4. Deliverables

Team 50 produces:
- QA findings report: `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_GATE_G_V1_1_REPORT_TEAM50.md`
- Decision: PASS / CONDITIONAL PASS / FAIL
- If CONDITIONAL: list conditions for closure

---

## 5. Preconditions

Before Team 50 begins:
1. Team 10 completion report filed
2. Team 190 package validation PASS on the completion report
3. Alembic migrations applied and stable
4. Full pipeline run completed (E1 in mandate)

---

**Issued by:** Team 100 (Architecture)  
**Date:** 2026-04-07
