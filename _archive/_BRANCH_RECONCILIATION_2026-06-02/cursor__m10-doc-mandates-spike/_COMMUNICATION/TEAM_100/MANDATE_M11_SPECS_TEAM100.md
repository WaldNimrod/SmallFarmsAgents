# Mandate — M11 Specification Documents

**Mandate ID:** MANDATE-20260407-M11-SPECS  
**Date:** 2026-04-07  
**Issued by:** Team 100 (Architecture)  
**To:** Team 100 (Architecture, self-assigned) + Team 80 (Product & Strategy, FarmCostAgent input)  
**Priority:** MEDIUM (after v1.1.0 release)  
**Target version:** v1.2.0  
**Status:** PLANNED — activates after G-V1.1 closure

---

## 1. Context

M11 is a planning milestone that produces specification documents only — no code. Its outputs define the architectural direction for farmer interaction, cost analysis, and data submission, feeding future implementation milestones (M12+, currently out of scope).

M11 depends on v1.1.0 being released (stable data foundation + catalog quality).

---

## 2. Deliverables

### Item 8: WordPress Farmer Roles — Architecture Decision Record

**Lead:** Team 100  
**Output:** `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_ADR_WORDPRESS_FARMER_ROLES_TEAM100.md`

Content:
- Role definitions: `guest` (view-only), `registered` (limited), `pending_farmer` (awaiting approval), `farmer` (full interaction), `admin` (approve)
- Registration flow: "אני חקלאי" checkbox, approval workflow
- WordPress implementation options: native roles vs custom plugin vs membership plugin
- Security considerations: what data farmers can see/edit
- Pre-login UX: disabled fields with "זמין לחקלאים מאומתים" hint
- Migration path from current anonymous-only public page
- Recommended approach with rationale

**Acceptance:** Document reviewed by Team 100 + Nimrod.

---

### Item 9: FarmCostAgent — Concept Brief

**Lead:** Team 100 + Team 80  
**Output:** `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_CONCEPT_BRIEF_FARMCOSTAGENT_TEAM100.md`

Content:
- Problem statement: farmers lack accessible cost analysis tools
- Proposed agent capabilities: cost breakdown, profitability analysis, scenario comparison
- Relationship to SmallFarmsAgent (shared data, separate interface)
- Technical architecture sketch: data sources, AI model, output format
- MVP scope vs full vision
- Integration points with existing OMA infrastructure
- Team 80 product perspective: target user, value proposition, differentiation

**Acceptance:** Document reviewed by Team 100 + Team 80 + Nimrod.

---

### Item 10: In-Page Submission Form — Technical Specification

**Lead:** Team 100  
**Dependency:** Item 8 (Farmer Roles ADR) must be complete  
**Output:** `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_SPEC_INPAGE_SUBMISSION_FORM_TEAM100.md`

Content:
- Form fields: product, price, unit, source context, date
- Authentication requirement: farmer role (from Item 8)
- Data validation: range checks, duplicate detection, abuse prevention
- Pipeline integration: submitted data -> `raw_extracted_items` with source_type = "community"
- WordPress implementation: shortcode, REST API, or hybrid
- Privacy: submitted data anonymized in public output (consistent with existing privacy policy)
- Moderation workflow: admin review before data enters pipeline

**Acceptance:** Document reviewed by Team 100 + Nimrod.

---

## 3. Out of Scope

- Code implementation of any of the above (that's M12+)
- Database schema changes
- WordPress plugin installation or configuration
- AI model training or API integration
- User-facing UI changes

---

## 4. Verification

- [ ] Farmer Roles ADR complete and reviewed
- [ ] FarmCostAgent concept brief complete and reviewed
- [ ] In-Page Submission Form spec complete and reviewed
- [ ] All three documents cross-reference each other where applicable
- [ ] Nimrod sign-off on direction

---

## 5. Gate

M11 is a planning milestone. Gate is Team 100 self-sign-off + Nimrod review. No Team 50 QA required (documents only).

After completion: tag **v1.2.0**.

---

## 6. Completion Report

File at: `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M11_SPECS_COMPLETION_TEAM100.md`

---

**Issued by:** Team 100 (Architecture)  
**Date:** 2026-04-07
