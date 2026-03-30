# Project Lead brief — M3 normalizer, data quality, and gate/mandate alignment

**Date:** 2026-03-30  
**From:** Nimrod (Project Lead)  
**To:** Team 100 (Architecture)  
**Cc:** Team 50 (QA), Team 10 (Feature Dev), Team 20 (Infrastructure) — for awareness  
**Subject:** Define precise mandates and phased specification: forward-looking accuracy, cohort metrics, historical noise control, and development-friendly data volume

---

## 1. Purpose

This document captures **project direction** and **requests to Team 100** to translate it into **binding architecture**: updated mandates, phased plans, and a full specification so implementation and QA can proceed without contradicting goals.

The historical raw backlog accumulated during early M2/M3 validation is **not** treated as the primary success metric. **Forward progress** depends on:

1. **How accurately** the system collects and normalizes **relevant** price/product signals **per agreed cycle** (sources, products, pass rates).  
2. **Stopping** repeated low-value re-fetch where checksum dedup already applies, and **optimizing the analysis path** so **most eligible rows** normalize while **ineligible rows** do not pollute the core analytical surface.  
3. **Retaining** rejections in a form that supports **measurement, triage, and normalizer improvement** — without forcing legacy noise through the same gates as catalog-quality observations.

---

## 2. Current situation (factual)

### 2.1 Pipeline and gates

- **M1/M2** foundation and collection layer exist; **M3** (normalizer engine) is implemented.  
- **Gate G3** QA has produced **conflicting outcomes** depending on which document is applied:
  - **Canonical** [`_COMMUNICATION/TEAM_50/QA_MANDATE_G3.md`](../TEAM_50/QA_MANDATE_G3.md) requires, among other things, **≥ 40** `normalized_observations` and strict regression counts on M1/M2 tables — **not met** on the current dev corpus (on the order of **single-digit** normalized rows vs **thousands** of `raw_extracted_items`, mostly **`unresolvable`**).
  - **Supplement** [`_COMMUNICATION/TEAM_50/QA_MANDATE_G3_RERUN.md`](../TEAM_50/QA_MANDATE_G3_RERUN.md) relaxes some thresholds (e.g. `normalized_observations` **> 0**) and **passes** on technical fixes (migration **008**, `TEXT` column, truncation cap, tests **46/46**).

### 2.2 Technical remediation already done

- **`unresolvable_reason`**: widened to **TEXT** (Alembic **008**); application caps written length; **no** `StringDataRightTruncation` crash on long messages.  
- **ORM** aligned to **Text** for `RawExtractedItem.unresolvable_reason`.  
- **Unit/integration tests** green on the current suite.

### 2.3 Root cause of “volume failure” (not a crash)

Team 10 **Phase A diagnosis** and QA evidence indicate that bulk `unresolvable` rows are dominated by:

- **`no alias match`** on **non-product** or **UI/chrome** text captured as `raw_product_name`.  
- **`empty raw_price_text`** and similar **extraction** gaps.  
- Heavy concentration on **large HTML / discovery-style** sources (e.g. high row counts per source) that are **not** vegetable price grids.

So the bottleneck is **data fitness + alias/parser policy + source scope**, not “the normalizer engine does not run.”

### 2.4 Regression testing noise (T9)

M3 does **not** insert into `raw_assets` / `raw_extracted_items`. Count drift during QA sessions indicates **concurrent ingestion** or **non-quiescent DB** — Team 10 proposed a **quiet-DB protocol** for reproducible T9. This remains a **process** requirement unless the mandate explicitly allows documented expected deltas.

---

## 3. Risks

| Risk | Description |
|------|-------------|
| **R1 — Mandate ambiguity** | Two G3 QA documents imply **different** “gate open” criteria; ROADMAP and teams lack a **single** authority. |
| **R2 — Metric mismatch** | Optimizing for **historical row count** or **≥40 on full backlog** rewards **ingesting noise** instead of **accurate, catalog-aligned** observations. |
| **R3 — DB usability** | Keeping unlimited **low-value** `raw_extracted_items` in the **same** operational path as price-relevant rows **obscures KPIs** and **slows** dev/QA cycles. |
| **R4 — Re-fetch waste** | Without clear **cycle** and **cohort** definitions, operators may re-run full ingestion **without** improving analytical yield. |
| **R5 — Loss of learning signal** | Aggressive **deletion** of rejected rows would **remove** material needed to improve parsers and aliases; need a **designed** retention/analytics path. |

---

## 4. Project Lead findings and intent

1. **Historical bulk data** from early broad scraping is **low strategic value** as a gate criterion; it should not block declaring **M3 engine “done”** if the **engine and tests** are sound and **forward** metrics are defined.  
2. **Success** should be expressed as **per-cycle** (or per-**ingestion_run**) **quality and coverage**: sources attempted, fetch success, rows classified as price-relevant, **normalization rate**, **distinct catalog products** with at least one valid observation, and breakdown of **failure reasons**.  
3. **Noise** should be **reduced** to a **development-friendly volume** via architecture and process: **early filtering**, **source gating**, **quarantine/archive**, **re-ingestion policy**, and optional **one-time historical cleanup** — all **specified** by Team 100, not ad hoc.  
4. **What does not normalize** must remain **available for analysis** (reason codes, optional separate table or partition, export path) **without** being treated as first-class “failed gate” material forever.

---

## 5. Requests to Team 100 (deliverables)

Team 100 is asked to **produce written mandates and specifications** (English, canonical paths under `_COMMUNICATION/TEAM_100/` and/or `docs/` per your conventions) that include:

### 5.1 Single authority for Gate G3 (and downstream)

- **Decide** whether **canonical G3**, **G3 RERUN**, or a **new merged mandate** is the **only** QA source of truth for ROADMAP.  
- Issue a **short architecture decision** (ADR-style) recorded in `TEAM_100/reports/` so Team 50 can sign **one** PASS/FAIL.

### 5.2 M3 “forward metrics” mandate (product + QA)

- Define **minimum acceptable** metrics **per cycle** (e.g. minimum **sources**, minimum **normalized** rows **or** minimum **distinct products**, maximum allowed **unresolvable rate** on a **defined vegetable-relevant cohort**).  
- Specify whether **cohort-scoped** normalizer runs (`--ingestion-run-id` or equivalent) are **allowed** for gate evidence and how they must be **documented** in QA reports.  
- Align with existing publish rules (e.g. community sources, thresholds) where applicable — or document **explicit** exceptions for **dev/staging**.

### 5.3 Data lifecycle and noise-control specification (phased)

A **phased plan** (e.g. Phase 0–3) covering at minimum:

| Phase | Suggested content (Team 100 to refine) |
|-------|----------------------------------------|
| **Classification** | Taxonomy of `raw_extracted_items`: price-relevant vs noise vs “needs review”; when parsers **must not** insert rows into the normalization queue. |
| **Retention** | What stays in **hot** tables vs **quarantine/archive**; retention TTL if any; what is **safe to delete** vs **must keep** for improvement loops. |
| **Historical cleanup** | **One-time** or **batched** reduction of exaggerated historical noise to a **sane** row count for **local dev/QA** — with **backup**, **idempotency**, and **no silent loss** of audit trail without explicit approval. |
| **Re-ingestion policy** | When full re-fetch is required vs when **normalize-only** or **selector/alias** change suffices. |

### 5.4 Team boundaries

- **Team 20**: migrations, seed changes, optional new tables/partitions for quarantine — per spec.  
- **Team 10**: parsers, collector filters, normalizer hooks — per spec.  
- **Team 50**: QA mandates updated to match **new** metrics and **quiet-DB** rules where T9 applies.

### 5.5 Documentation outputs expected

1. **`M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md`** (or equivalent name) — full behavioral spec.  
2. **`QA_MANDATE_G3_v2.md`** (or superseding amendment) — single Team 50 checklist.  
3. **ROADMAP patch recommendation** — one paragraph + checkbox updates for Gate G3 and M4 entry criteria.

---

## 6. Explicit non-goals (unless Team 100 expands scope)

- This brief does **not** require Team 100 to implement code.  
- It does **not** prescribe exact SQL for cleanup — Team 100 specifies; Team 20/10 execute.

---

## 7. References for Team 100 (evidence trail)

| Document | Relevance |
|----------|-----------|
| [`_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G3_TEAM50.md`](../TEAM_50/reports/2026-03-30_QA_G3_TEAM50.md) | Dual outcome; canonical vs RERUN |
| [`_COMMUNICATION/TEAM_50/reports/2026-03-30_G3_TEAM10_EXECUTED_EVIDENCE_REREVIEW_TEAM50.md`](../TEAM_50/reports/2026-03-30_G3_TEAM10_EXECUTED_EVIDENCE_REREVIEW_TEAM50.md) | Team 10 executed counts and interpretation |
| [`_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_REMEDIATION_EXECUTION_PACK_TEAM10.md`](../TEAM_10/reports/2026-03-30_G3_REMEDIATION_EXECUTION_PACK_TEAM10.md) | Phases B1–B3, governance options |
| [`_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_T09_QUIET_DB_PROTOCOL_TEAM10.md`](../TEAM_10/reports/2026-03-30_G3_T09_QUIET_DB_PROTOCOL_TEAM10.md) | T9 reproducibility |
| [`_COMMUNICATION/TEAM_50/QA_MANDATE_G3.md`](../TEAM_50/QA_MANDATE_G3.md) | Canonical gate tests |
| [`_COMMUNICATION/TEAM_50/QA_MANDATE_G3_RERUN.md`](../TEAM_50/QA_MANDATE_G3_RERUN.md) | Post-fix supplement |

---

## 8. Acceptance

**Team 100** acknowledgment and a dated **response plan** (target deliverable dates for each artifact in §5.5) in `_COMMUNICATION/TEAM_100/reports/` satisfies this brief’s **intake** requirement.

**[USER ACTION REQUIRED]:** None beyond Team 100 assignment; Nimrod available for clarification on trade-offs (e.g. how aggressive historical cleanup may be).
