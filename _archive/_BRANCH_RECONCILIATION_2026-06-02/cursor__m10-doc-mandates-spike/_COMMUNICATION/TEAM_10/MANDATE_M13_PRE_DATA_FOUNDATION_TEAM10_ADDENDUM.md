# ADDENDUM — M13-PRE data foundation (Nimrod direction)

**Effective date:** 2026-04-06  
**Parent mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md`  
**Issued by:** Team 10 (documentation of product direction); binding mandate revision remains with Team 100 if a formal superseding document is required.

---

## Purpose

This addendum **does not delete or rewrite** the original M13-PRE mandate. It records **Nimrod’s direction** so M13 can close without deadlock when live data does not meet every numeric threshold in §4 of the parent mandate.

---

## Waivers (blocking)

**§4 of the parent mandate (“all criteria before M13-B”) is waived as a hard gate** effective 2026-04-06.

- M13-B and M13-C may proceed when:
  1. **Publish succeeds** with the existing engine rule of **≥2 distinct community sources** in the rolling window (unchanged).
  2. **Privacy** rules in the M13 architectural approval remain **unchanged** and are verified on public JSON/HTML.
  3. **Team 50** runs **Gate G11** and issues **PASS** or **CONDITIONAL PASS** with an explicit **waiver list** (e.g. published product count below legacy “≥90”, partial mypips coverage, SRC035 basket extraction policy).

Team 50 may run M13-PRE–style checks **in parallel** for traceability; outcomes are **informational** unless a waiver is refused on safety/privacy grounds.

---

## Optimization backlog

The **original §4 numeric criteria** (mypips 5/9, CSA counts, SRC036 resolution %, published product count ≥90, etc.) remain the **optimization backlog** for a **future milestone** (see ROADMAP: **M10.x optimization** / deferred G10 final closure).

---

## Evidence

- Data snapshot + freeze narrative: `_COMMUNICATION/TEAM_10/reports/2026-04-06_M13_DATA_SNAPSHOT_AND_M10_FREEZE_TEAM10.md`
- Roadmap: `_COMMUNICATION/ROADMAP.md` **v5.4**
- **G-PRE-5 (≥90 products) — formal Team 100 waiver:** `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` (**ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**); QA gate record: `_COMMUNICATION/TEAM_50/reports/2026-04-05_M13_PRE_GPRE_QA_FINDINGS_TEAM50.md` (**CONDITIONAL PASS**)
