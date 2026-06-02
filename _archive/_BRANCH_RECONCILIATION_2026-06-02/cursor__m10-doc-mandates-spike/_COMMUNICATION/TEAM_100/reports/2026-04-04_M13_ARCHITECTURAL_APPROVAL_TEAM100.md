---
document_type: ARCHITECTURE_APPROVAL
version: "1.0"
---

# Architectural Approval — M13 Public Product Details Module, CSA Standardization & Channel Variants

**Approval ID:** ARCH-20260404-M13-APPROVED-PENDING-PRE
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev), Team 50 (QA), Nimrod (product)
**Date:** 2026-04-04
**Proposal reviewed:** `_COMMUNICATION/TEAM_10/reports/2026-03-31_PUBLIC_INDEX_DETAILS_CSA_UNIFIED_PROPOSAL_TEAM10.md`
**Gate:** G11 (new)

---

## Decision

**APPROVED — with prerequisite phase (M13-PRE) and binding constraints.**

Team 10's proposal is architecturally sound. The unified module approach (one pattern, channel-specific panels) is the correct design. This approval formalizes all binding decisions, answers the 7 open questions, and registers M13 in the roadmap.

---

## Critical Finding: M10 Data Readiness

M13 depends on stable data from CSA and mypips sources. Current state:

| Sub-phase | Status | Blocker |
|-----------|--------|---------|
| M10.4 (mypips) | Mandate issued, not yet implemented | No mypips data flowing |
| M10.5 (CSA + Sellio) | QA **FAILED** (5 critical) | SRC034=0 items, SRC036=0% resolution, product count dropped to 74 |

**Architectural decision:** M13 requires a prerequisite phase (M13-PRE) that defines exact LOD 400 remediation criteria for M10.4/M10.5. See `MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md`.

---

## Privacy Constraint (BINDING — applies to all M13 work)

Per product direction: **no public-facing output may identify a specific farm, vendor, or source.**

| Category | Rule |
|----------|------|
| **PROHIBITED in public JSON/HTML** | Source codes, source names, source labels, source URLs, any field from which a specific farm identity can be inferred |
| **PERMITTED** | Source count per product, aggregated price statistics, anonymized context excerpts, display_bucket category labels ("grower", "store", "chain") |
| **Internal only** | `source_breakdown` with codes (admin dashboard, pipeline logs) |

**Impact:** Team 10's proposed `source_breakdown[].code` and `source_breakdown[].label_he` are **rejected** from the public schema. Replace with `source_count: int`.

---

## Binding Architectural Decisions (Answers to Proposal §7)

### Q1: Publish schema structure
**Decision: Extend `products[]` inline.**

Each product entry gets an optional `details` object. No parallel `product_details[]` array. Reasons: simpler key matching, smaller payload, consistent with current structure.

- Bump `MANIFEST_SCHEMA_VERSION` from `"2.0"` to `"3.0"` when `details` is first published
- Add `"report_schema_version": "3.0"` to `public_report.json` top level for forward compatibility

### Q2: Basket identity in public table
**Decision: One aggregated row per basket size (PRD025, PRD027, PRD028).**

Baskets aggregate across all contributing sources exactly like price-grid items. The details module shows `source_count` (e.g., "based on 3 sources") but never farm names.

### Q3: Price chart granularity
**Decision:**
- Price-grid items: daily median, capped at **30 calendar days**
- Basket items: weekly median (one point per ISO week), capped at **12 weeks**
- Minimum threshold: **3 data points** before rendering a chart; below that, display "אין מספיק נתונים להצגת מגמה"

### Q4: Historical text (CSA wording)
**Decision: Versioned JSON artifacts only (no DB table).**

CSA wording snapshots ride the `public_report-{version}.json` artifacts. No `published_basket_snapshot` table in V1. A dedicated table may be added later via migration if historical text query requirements emerge.

### Q5: Stores vs. growers display
**Decision: Same table with filter buttons (already implemented).**

The existing `display_bucket` filter bar (all / growers / stores / chains) is correct. No separate table needed.

### Q6: Performance budget
**Decision:**
- Max `price_series` points per product: **30** (daily) or **12** (weekly for baskets)
- Max JSON report size: **500 KB** soft limit; if exceeded, truncate `price_series` to most recent 15 points first
- Publisher must log a warning if report exceeds 500 KB

### Q7: Gate assignment
**Decision: New gate G11.**

QA mandate: `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md`

Team 50 validates:
- Publish schema stability (v3 backward-compatible read by existing WP shortcode)
- Accessibility (RTL, keyboard focus trap in details module)
- Price chart rendering (correct data, no NaN/Infinity)
- Privacy compliance (no source identification in public output)
- Regression on existing published products

---

## Approved Publish JSON v3 Schema

```json
{
  "report_schema_version": "3.0",
  "generated_at": "2026-04-10T06:00:00Z",
  "report_date": "2026-04-10",
  "index": { "mode": "rolling_7d", "window_days": 7 },
  "data_quality": {},
  "products": [
    {
      "product_id": "PRD001",
      "canonical_name_he": "עגבניות",
      "category": "fruiting_vegetables",
      "market_scope": "community",
      "source_types": ["grower"],
      "meets_publish_threshold": true,
      "sample_size": 5,
      "distinct_sources": 3,
      "min_price": 8.0,
      "max_price": 14.0,
      "avg_price": 10.5,
      "median_price": 10.0,
      "stddev_price": 2.1,
      "normalized_unit": "kg",
      "last_observed_at": "2026-04-09T12:00:00Z",
      "details": {
        "details_variant": "grower_price_grid",
        "source_count": 3,
        "price_series": [
          {"d": "2026-03-11", "v": 10.0},
          {"d": "2026-03-12", "v": 10.5}
        ],
        "csa": null,
        "store": null,
        "benchmark": null
      }
    },
    {
      "product_id": "PRD025",
      "canonical_name_he": "סל ירקות קטן",
      "category": "baskets",
      "market_scope": "community",
      "source_types": ["grower"],
      "meets_publish_threshold": true,
      "sample_size": 2,
      "distinct_sources": 2,
      "min_price": 80.0,
      "max_price": 95.0,
      "avg_price": 87.5,
      "median_price": 87.5,
      "stddev_price": null,
      "normalized_unit": "סל קטן",
      "last_observed_at": "2026-04-09T12:00:00Z",
      "details": {
        "details_variant": "basket_csa",
        "source_count": 2,
        "price_series": [
          {"d": "2026-W11", "v": 85.0},
          {"d": "2026-W12", "v": 87.5},
          {"d": "2026-W13", "v": 90.0}
        ],
        "csa": {
          "contents_summary_generalized": "10-14 זנים של ירקות אורגניים עונתיים, כ-3-5 ק\"ג",
          "cadence_note": "משלוח/איסוף שבועי",
          "context_incomplete": false
        },
        "store": null,
        "benchmark": null
      }
    }
  ]
}
```

---

## Approved Variant Mapping Logic

```
if is_basket_product and category == "baskets":
    variant = "basket_csa"
elif display_bucket == "store":
    variant = "store_retail"
elif market_scope == "benchmark":
    variant = "chain_benchmark"
else:
    variant = "grower_price_grid"
```

---

## CSA Context Generalization (privacy-safe merge)

When multiple CSA sources contribute to a basket product, the publisher must:
1. Collect all `csa_context` objects from contributing `raw_payload_json` entries
2. Merge into a generalized summary: take the most detailed `contents_summary` and `cadence_note` across sources, strip any farm-identifying language
3. Set `context_incomplete: true` if any contributing source had `context_incomplete: true`

---

## M13 Phasing (Approved)

| Phase | Team | Dependency | Scope |
|-------|------|------------|-------|
| M13-PRE | Team 10 | Immediate | Data foundation: M10.4 completion + M10.5 remediation at LOD 400 |
| M13-A | Team 10 | M13-PRE mandate issued | Publisher JSON v3 extensions: `details`, `price_series`, variant logic |
| M13-B | Team 10 + Nimrod WP | M13-PRE complete + M13-A complete | Frontend details module: accordion, chart, variant blocks |
| M13-C | Team 50 | M13-A + M13-B complete | QA validation per G11 mandate |
| M13-D | Team 100 | Team 50 QA PASS | Architectural sign-off, schema v3 frozen |

---

## Source Sufficiency Assessment (Team 100 position)

| Segment | Current | Team 100 Position |
|---------|---------|-------------------|
| Grower price grids | 14 active, 100% resolution | Sufficient for details module |
| CSA baskets | 1/3 producing data (SRC033 only) | **Insufficient** — M13-PRE must fix SRC034 |
| Stores | SRC036 at 0% resolution | **Insufficient** — M13-PRE must fix aliases |
| mypips | 0/9 active | **Insufficient** — M10.4 must complete |
| Chains/benchmark | Future | Not required for M13 V1 |

Minimum for M13-B start: **2 CSA sources + 3 mypips sources + SRC036 with >0 normalized items**.

---

## Waivers Issued

| ID | Original Threshold | Waived To | Reason |
|----|-------------------|-----------|--------|
| W-M10.5-AC2 | SRC036 organic extraction >= 20 | >= 12 | 12 genuine organic items from single retail source is valid V1 start; extensible via selector_profile |

---

## Risks Accepted

1. Chart.js CDN dependency for public page (already used in admin; acceptable for V1)
2. CSA context generalization may lose per-farm nuance (acceptable: privacy trumps precision)
3. Basket aggregation hides individual farm pricing (by design: privacy constraint)

---

## Related Documents

| Document | Path |
|----------|------|
| Team 10 Proposal | `_COMMUNICATION/TEAM_10/reports/2026-03-31_PUBLIC_INDEX_DETAILS_CSA_UNIFIED_PROPOSAL_TEAM10.md` |
| M13-PRE Mandate | `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md` |
| G11 QA Mandate | `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md` |
| M10.5 QA Findings | `_COMMUNICATION/TEAM_50/reports/2026-04-05_M10_5_QA_FINDINGS_TEAM50.md` |
| M10.4 Mandate | `_COMMUNICATION/TEAM_10/MANDATE_M10_4_HEADLESS_MYPIPS_TEAM10.md` |
| M10.5 Mandate | `_COMMUNICATION/TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md` |

---

*Approved by: Team 100 (Architecture)*
*Date: 2026-04-04*
