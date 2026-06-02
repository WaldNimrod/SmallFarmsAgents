# Proposal — Public index product details module, CSA standardization, channel variants

**From:** Team 10 (Feature Dev)  
**To:** Team 100 (Architecture) — *review when available*; Team 50 (QA); Nimrod (product)  
**Date:** 2026-03-31  
**Status:** DRAFT FOR REVIEW (Team 100 unavailable — submitted as complete package for later sign-off)  
**Related:** `2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md`, M10.5 implementation, `docs/GLOSSARY.md`

---

## 1. Purpose

Define a **single, extensible “product details” surface** on the public dynamic index (WordPress / embedded body fragment) with:

- A **details module for every published row** (drill-down: extra context, and over time **price history chart**).
- **Variant configurations** of the same module shell for **grower / CSA basket / store / retail chain** (not four separate UIs — one pattern, channel-specific panels).
- A **roadmap-tracked** work package for **basket (CSA) standardization** that avoids heavy query sprawl and keeps publish artifacts predictable.

This document states **principles**, a **recommended architecture**, **open questions**, and **phasing** so Team 100 can approve or adjust with minimal rework.

---

## 2. Design principles (from product direction)

| Principle | Implication |
|-----------|-------------|
| **One module pattern** | Shared shell: open/close, title, tabs or sections, RTL, accessibility. Channel = **config + optional blocks**, not a forked template per source. |
| **Progressive disclosure** | Table stays scannable; depth lives in the module (text, chart, source list). |
| **No query explosion** | Prefer **pre-aggregated publish payloads** (JSON built at `run_publisher`) over ad-hoc WordPress → DB or multi-join runtime APIs in V1. |
| **Standardize baskets at the edge** | Parsers map heterogeneous sites → a **small canonical “basket offer” shape**; publisher merges into `public_report` without N×1 tables unless history requires it. |
| **Channel variants** | `display_bucket` / `sales_channel` / `source_group` drive which **detail panels** render (e.g. CSA: contents + cadence; store: SKU note + organic flag; chain: benchmark disclaimer). |

---

## 3. Unified product details module (all rows)

### 3.1 UX scope (M13 core)

- **Trigger:** row action (e.g. “פרטים” / chevron) on each product line in the public table.
- **Content (baseline, all channels):**
  - Canonical name, unit, last observation window, **source list** with codes or display names.
  - **Price band** recap (min / max / avg already in table — may collapse in module).
  - **Price-over-time chart:** requires **time series** in publish JSON or a compact `sparkline_points[]` (e.g. daily or weekly median for last N days — exact resolution TBD).
- **Non-functional:** RTL, keyboard focus trap in modal (or inline expand), mobile layout per `RTL_DEVELOPMENT_GUIDE.md`.

### 3.2 Channel variants (same module, different blocks)

| Variant key (logical) | Driven by | Extra blocks (examples) |
|----------------------|-----------|---------------------------|
| `grower_price_grid` | `display_bucket=grower`, non-basket | Organic note, source link, optional confidence |
| `basket_csa` | `source_group=basket_csa` or product `is_basket_product` | **Extended:** `contents_summary`, `cadence_or_delivery_note`, subscription disclaimer, “contents vary” |
| `store_retail` | `display_bucket=store` | Store name, organic-only note for mixed catalogs, link to storefront |
| `chain_benchmark` | `market_scope` / tier benchmark | Benchmark disclaimer, methodology link |

Implementation suggestion: **`details_variant`** string + **`details_blocks`** array in JSON; front-end maps variant → registered block components (static WP script).

### 3.3 Data contract (publish JSON extension — draft)

Extend each `products[]` entry (or parallel array keyed by `product_id` + bucket) with optional:

```json
{
  "details_variant": "basket_csa",
  "details": {
    "source_breakdown": [{"code": "SRC033", "label_he": "...", "last_observed_at": "..."}],
    "price_series": [{"d": "2026-03-24", "v": 128.5}],
    "csa": {
      "contents_summary": "...",
      "cadence_or_delivery_note": "...",
      "context_incomplete": false
    },
    "store": null,
    "benchmark": null
  }
}
```

**Team 100 must confirm:** schema version bump (`manifest.schema_version` / report version), backward compatibility for embedded WP pages.

---

## 4. CSA / baskets — standardization without data sprawl

### 4.1 Problem

Sources express baskets as **free text + different pricing models** (weekly box, S/M/L, add-ons). We already capture **policy context** in `raw_payload_json.csa_context` (M10.5). The public index still lacks a **stable, comparable** surface.

### 4.2 Recommended model (lean)

1. **Canonical “basket offer”** (logical, not necessarily a new DB table in V1):
   - `basket_kind` (enum: `small`, `medium`, `large`, `family`, `student`, `custom_text`)
   - `display_label_he` (short, from site or normalized)
   - `price_amount` + `price_cadence` (`per_week`, `per_delivery`, `one_time` — optional)
   - `context` (structured text fields aligned with analysis policy)
   - `source_id`, `product_id` (catalog basket SKU)

2. **Materialization point:** **at publish time**, join latest normalized observations + latest REI payload (or a thin **publish_staging** query) into **`details.csa`** only for basket rows. Avoid a long-lived `csa_offers` table until we need **multi-week history of offer text** (see questions).

3. **Standardization layer:** Team 10 maintains a **small mapping table in DB** (or JSON config per `csa_site`) from parser-specific labels → `basket_kind` + `display_label_he` so the UI does not branch per farm name.

### 4.3 When a new table is justified

Add **`published_basket_snapshot`** (or similar) **only if**:

- We must query “how did חווה X describe its large basket in week W” in admin or public history, **and**
- Storing only in `public_report-{ts}.json` is insufficient.

Otherwise, **versioned JSON artifacts** + existing `daily_aggregates` / `normalized_observations` suffice for **price charts**; text context can ride **publish snapshot**.

---

## 5. Price history chart — data source

| Option | Pros | Cons |
|--------|------|------|
| **A.** Precompute `price_series[]` in publisher from `daily_aggregates` or `normalized_observations` | No new API; WP reads static JSON | Publisher work; window length policy |
| **B.** Separate minimal JSON `series/{product}.json` | Smaller main report | Extra files + manifest entries |
| **C.** On-demand API | Flexible | Conflicts with “local static publish” architecture |

**Recommendation:** **Option A** for V1, capped points (e.g. last 30 calendar days or last 12 weekly buckets for baskets).

---

## 6. Source sufficiency (honest assessment)

| Segment | Current relevance (indicative) | Gap |
|---------|-------------------------------|-----|
| **Grower price grids** | Multiple active community sources | OK for per-kg index |
| **CSA baskets** | SRC033, SRC034 strong parsers; SRC035 thin on chosen URL | Need more farms **or** deeper URLs / Playwright for shop |
| **Stores (e.g. Teva)** | SRC036 Sellio + organic filter; count of strict organic lines may be &lt; mandate target | May need **more categories** or relaxed rule with Team 100 |
| **Chains** | Benchmark / future — not same community rules | Variant UI + clear disclaimer |

**Conclusion:** For a **rich CSA module**, we likely need **either** more basket-dedicated sources **or** agreed **lower bar** for “community basket index” until coverage grows. This is a **product + Team 100** call.

---

## 7. Open questions (for Team 100 / Nimrod)

1. **Publish schema:** Single `products[]` extension vs. top-level `product_details[]` keyed by stable id?
2. **Basket identity:** Is one catalog row (e.g. PRD025) enough for “סל קטן” across farms, or do we expose **per-source rows** in the public table for baskets?
3. **Price chart granularity:** Daily vs. weekly for baskets; minimum points before showing chart?
4. **Historical text:** Do we freeze **CSA wording** per publish only, or store editable history in DB?
5. **Stores vs. growers:** Should **store** prices appear in the **same** table with a badge, or only under “חנויות” filter (already partially there)?
6. **Performance budget:** Max JSON size per report; cap on `price_series` points per product?
7. **Gate:** Does M13 require a new QA mandate (G11?) or fold under post–G10 regression + UX checklist?

---

## 8. Proposed roadmap placement (see ROADMAP.md M13)

**M13 — Public product details module & channel variants**

- **Phase A (Team 10):** Publish JSON extensions; publisher queries for `price_series`; basket `details.csa` assembly; unit tests on payload shape.
- **Phase B (Team 10 + Nimrod WP):** Filter bar refinement; modal/accordion module; variant templates; chart (e.g. Chart.js from mandate-compatible CDN).
- **Phase C (Team 50):** Accessibility, RTL, regression on static publish; optional E2E snapshot.
- **Phase D (Team 100):** Formal sign-off on schema + basket rules.

**Dependency:** Stable `public_report` v2/v3 contract; recommend **after** G10 closure or in parallel with M10.4/10.5 hardening as agreed.

---

## 9. Deliverables checklist (this proposal)

- [x] Written proposal (this file)
- [x] Roadmap M13 stub + reference
- [ ] Team 100 approval record (pending)
- [ ] QA mandate or checklist (pending Team 50 / Team 100)

---

*End of draft — Team 10 ready for review cycle when Team 100 is available.*
