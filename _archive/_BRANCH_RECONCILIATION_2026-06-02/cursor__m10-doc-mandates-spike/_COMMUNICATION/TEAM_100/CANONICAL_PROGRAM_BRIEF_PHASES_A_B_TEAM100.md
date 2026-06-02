# Canonical program brief — Team 100 (Phases A & B)

**Document ID:** BRIEF-20260407-PHASE-AB-CANONICAL  
**Date:** 2026-04-07  
**Issued by:** Team 100 (Architecture)  
**Audience:** Team 100 (primary), Team 10 (orchestration), Team 50 / Team 190 (gates), Nimrod  
**Status:** ACTIVE — single canonical index for current OrganicMarketAgent program direction  
**Language:** English (inter-team canonical); Nimrod may use Hebrew in direct conversation.

---

## 1. Purpose of this document

This file is the **one canonical message** for Team 100 defining:

1. **What we are doing now** (program goal).  
2. **Phase A** — deliver items **1–9** (catalog quality packages **CQ-P01–CQ-P09**) as part of **v1.1.0**.  
3. **Phase B** — **complete M11 in full** (all spec deliverables, verification, and **official gates** as already defined), producing **v1.2.0** tagging and documented sign-off.  
4. A **master bibliography** of every plan, mandate, gate, and evidence artifact prepared for these tracks.

If another document conflicts, **resolve in favor of**: this brief for **intent and phase ordering**; **`_COMMUNICATION/ROADMAP.md`** for milestone/version truth; **`MANDATE_V1_1_CONSOLIDATED_TEAM10.md`** for **v1.1.0 execution detail**; **`MANDATE_M11_SPECS_TEAM100.md`** for **M11 spec scope**.

---

## 2. Current program goal (Nimrod direction)

| Layer | Goal |
|-------|------|
| **Data & catalog** | Stable, comparable community price index: correct **aliases**, **units**, **basket tiers**, **pantry comparison path** (ADR), and **regression guards** (tomato/cherry; PRD028/029 merge targets). |
| **Release** | Ship **v1.1.0** under **one consolidated gate (G-V1.1)** after Team 10 completion + **Team 190** preflight + **Team 50** QA. |
| **Specification forward** | After v1.1.0 closure, **finish M11 completely** — three spec artifacts, internal verification checklist, **Team 100 + Nimrod sign-off**, tag **v1.2.0**, per existing M11 mandate (no code in M11). |

---

## 3. Phase A — Items 1–9 (CQ-P01–CQ-P09) → v1.1.0

**Mapping (recommendation list → packages):** same as `ROADMAP.md` § Post-M13 — Catalog Quality Packages.

| # | Package | Summary |
|---|---------|---------|
| 1 | **CQ-P01** | Unresolvable alias backlog clearance (export → aliases / scope rules → renormalize). |
| 2 | **CQ-P02** | Full ingestion run to completion → normalize → aggregate → publish. |
| 3 | **CQ-P03** | Eggs (PRD067): per-source unit semantics (12-pack convention). |
| 4 | **CQ-P04** | Passion fruit (PRD072): kg vs pack disambiguation. |
| 5 | **CQ-P05** | Blueberries (PRD086): tray/pack size by source (research table). |
| 6 | **CQ-P06** | Pantry dry goods: pack-weight comparison **ADR** (implementation phased). |
| 7 | **CQ-P07** | CSA / Gadi-style baskets: line-count (or equivalent) → **PRD025/026/027** tier policy. |
| 8 | **CQ-P08** | Tomato vs cherry regression guard (**PRD001** vs **PRD002**). |
| 9 | **CQ-P09** | Inactive **PRD028/PRD029**: no active aliases; targets **PRD027/PRD026**. |

**Execution orchestration:** **Team 10** (primary), **Team 20** (migrations), **Team 80** (research support where noted), **Team 100** (policy / scope-change approvals).

**Architectural binding (LOD 200 thresholds, phasing, SQL patterns):**  
`_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` (**ARCH-20260406-CQ-MASTER**).

**Single consolidated implementation mandate (replaces per-package-only governance for the release):**  
`_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` (**MANDATE-20260407-V1-1-CONSOLIDATED**).

**Official QA gate for Phase A completion:**  
`_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` (**G-V1.1**).

**Preflight before Team 50:** **Team 190** constitutional / package validation on the **v1.1.0 completion bundle** (same pattern as M10.2/M10.3 preflight reports under `_COMMUNICATION/TEAM_190/reports/`).

---

## 4. Phase B — M11 complete to end + official gates → v1.2.0

**Scope:** M11 is **specification only** (no production code). All tasks through the **end of M11** means:

| Deliverable | Output path pattern |
|-------------|---------------------|
| Item 8 — WordPress farmer roles | `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_ADR_WORDPRESS_FARMER_ROLES_TEAM100.md` |
| Item 9 — FarmCostAgent concept | `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_CONCEPT_BRIEF_FARMCOSTAGENT_TEAM100.md` |
| Item 10 — In-page submission form | `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_SPEC_INPAGE_SUBMISSION_FORM_TEAM100.md` |

**Mandate (full checklist, verification, gate rule):**  
`_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` (**MANDATE-20260407-M11-SPECS**).

**Official gates (as defined there):**

1. All three documents complete and **cross-referenced** where required.  
2. **Team 100** verification checklist satisfied (see mandate §4).  
3. **Nimrod sign-off** on direction.  
4. **Completion report:** `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M11_SPECS_COMPLETION_TEAM100.md`.  
5. **Tag v1.2.0** after closure.

**Note:** M11 explicitly states **no Team 50 QA** (documents only). If Nimrod later promotes M11 outputs to an implementation milestone, a **new** gate and QA mandate will be issued.

**Precondition:** **G-V1.1 closed** (v1.1.0 stable) before treating M11 as the active execution priority.

---

## 5. Master bibliography (plans & evidence)

### 5.1 Roadmap & version truth

| Document | Path |
|----------|------|
| Development roadmap (v6.0+) | `_COMMUNICATION/ROADMAP.md` |
| v1.0.0 declaration | `_COMMUNICATION/TEAM_100/reports/2026-04-07_VERSION_1_0_0_DECLARATION_TEAM100.md` |

### 5.2 Phase A — Architecture, execution, QA

| Document | Path |
|----------|------|
| CQ master arch approval (LOD 200) | `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` |
| Consolidated v1.1.0 mandate (Team 10) | `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` |
| QA mandate G-V1.1 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` |
| Prior CQ-only mandate (superseded by consolidated) | `_COMMUNICATION/TEAM_10/MANDATE_CQ_CATALOG_QUALITY_TEAM10.md` |

### 5.3 Phase B — M11

| Document | Path |
|----------|------|
| M11 specs mandate | `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` |

### 5.4 Catalog scan & metrics (context / evidence)

| Document | Path |
|----------|------|
| Exec summary (HE, Nimrod) | `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_EXEC_SUMMARY_HE_NIMROD.md` |
| Exceptions register | `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_EXCEPTIONS_REGISTER_TEAM10.md` |
| Technical run report | `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_RUN_REPORT_TEAM10.md` |
| Metrics helper | `scripts/catalog_scan_collect_metrics.py` |
| Baseline / metrics JSON (examples) | `data/catalog_scan_baseline_before.json`, `data/catalog_scan_metrics_before.json` (and siblings if present) |

### 5.5 Team 190 (preflight pattern)

| Document | Path |
|----------|------|
| Example preflight reports | `_COMMUNICATION/TEAM_190/reports/2026-04-04_M10_2_PACKAGE_VALIDATION_TEAM190.md`, `..._M10_3_...` |

### 5.6 Canonical terminology

| Document | Path |
|----------|------|
| Glossary | `docs/GLOSSARY.md` |

---

## 6. Role summary

| Team | Phase A (v1.1.0) | Phase B (M11) |
|------|------------------|---------------|
| **Team 100** | Owns ARCH-20260406-CQ-MASTER; approves scope changes; maintains this brief | Authors / reviews all M11 specs; runs §4 verification; co-signs with Nimrod |
| **Team 10** | Orchestrates implementation per consolidated mandate | No code; may support Team 80 input for FarmCostAgent brief |
| **Team 20** | Migrations as scoped | — |
| **Team 50** | **G-V1.1** QA | Not required for M11 (per M11 mandate) |
| **Team 190** | Preflight on v1.1.0 completion package | Optional if M11 package uses constitutional format |
| **Nimrod** | Product direction, waivers, operator runs | Final M11 direction sign-off |

---

## 7. Changelog

| Date | Change |
|------|--------|
| 2026-04-07 | Initial canonical brief (Phases A & B + full bibliography). |

---

**Maintainer:** Team 100. **Update this file** when phase status changes (e.g. G-V1.1 PASS, M11 completion) or when new canonical artifacts supersede paths above.
