---
document_type: MANDATE
version: "1.0"
---

# Mandate — CSA Basket Sources & Phase B Retail Integration (M10.5)

**Mandate ID:** MANDATE-20260404-M10-5-CSA-RETAIL
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-04
**Priority:** HIGH
**Gate dependency:** Blocks full G10 closure
**Prerequisite:** M10.4 must be substantially complete (headless infrastructure available)
**Status:** ACTIVE

---

## 1. Objective

Integrate two distinct source categories into the pipeline:
1. **CSA Basket sources** (SRC033–SRC035) — community-supported agriculture farms selling fixed-price baskets
2. **Phase B Retail** (SRC036 — Teva Shuk) — a retail marketplace selling organic + conventional products, requiring organic-only filtering

These source types require different handling from the price-grid growers already in the system.

---

## 2. Background

### CSA Basket Sources

CSA farms sell curated baskets rather than individual items. The existing normalizer handles basket products (`is_basket_product = true`, `normalized_price_value = NULL`), but no CSA-specific collector or parser exists yet.

| Source | Name | URL | Platform | Model |
|--------|------|-----|----------|-------|
| SRC033 | חוות שורשים | `https://www.havatshorashim.co.il/` | Custom HTML | Fixed baskets (S/M/L) |
| SRC034 | משק אורגני — המעפיל | `https://www.meshekorgani.co.il/` | Custom HTML | Weekly basket subscription |
| SRC035 | משק יוסף | `https://www.meshek-yosef.co.il/` | Custom HTML | Basket + individual items |

### Phase B Retail — Teva Shuk

| Source | Name | URL | Platform | Challenge |
|--------|------|-----|----------|-----------|
| SRC036 | טבע שוק | `https://www.teva-shuk.co.il/` | Sellio (Next.js / Redux) | Mixed catalog: organic + conventional; 129 products observed, ~30% organic |

Key challenge: Teva Shuk sells both organic and conventional produce. The system must filter to organic-only items to avoid contaminating community price data.

---

## 3. Deliverables

### Part A: CSA Basket Sources (SRC033–SRC035)

| ID | Deliverable | Details |
|----|-------------|---------|
| DA1 | HTML Analysis | Deep analysis of each CSA site's HTML structure — identify basket names, prices, sizes |
| DA2 | Parser(s) | New parser class(es) for CSA sites in `organic_market_agent/parsers/`. May share a `CsaBasketParser` if structure is similar, or individual parsers per site |
| DA3 | Engine registration | Register parser type(s) in `_PARSER_MAP` and update `chk_np_normalizer_type` constraint |
| DA4 | Fetch + normalizer profiles | Create profiles via Alembic data migration |
| DA5 | Source activation | Set `is_active = true`, `status = 'active'`, `source_group = 'basket_csa'`, `sales_channel = 'csa_basket'` |
| DA6 | Basket product mapping | Map basket names to existing or new basket products (`סל ירקות גדול`, `סל ירקות קטן`, `סל ירקות בינוני`) |
| DA7 | Pipeline run | Run ingestion → normalization for each CSA source |
| DA8 | Publish verification | CSA baskets should appear in published report with basket emoji (🧺) and appropriate unit |

### Part B: Phase B Retail — Teva Shuk (SRC036)

| ID | Deliverable | Details |
|----|-------------|---------|
| DB1 | Platform analysis | Deep analysis of `teva-shuk.co.il` — Sellio platform uses Next.js with `__NEXT_DATA__` or Redux store in page source |
| DB2 | `SellioParser` | New parser in `organic_market_agent/parsers/sellio.py` — extract products from Sellio's Next.js data layer |
| DB3 | Organic filter strategy | Implement one of the following approaches (Team 10 to recommend): |
|     | | **Option A:** Parse only from the "אורגני" category/tag if the site has one |
|     | | **Option B:** Add `is_organic_flag` field to raw extraction; filter during normalization |
|     | | **Option C:** Use scope-skip rules to ignore non-organic items by name pattern |
| DB4 | Engine registration | Register `'sellio'` in `_PARSER_MAP` and update constraint |
| DB5 | Fetch + normalizer profiles | Create profiles; include organic filter configuration in `selector_profile` |
| DB6 | Source activation | Set `is_active = true`, `status = 'active'` |
| DB7 | Dictionary optimization | Add aliases, products, scope-skip rules for Teva Shuk items |
| DB8 | `display_bucket` verification | Confirm SRC036 `display_bucket = 'store'` — products with Teva Shuk data should be filterable as "חנויות" |

### Part C: Quality Assurance Artifacts

| ID | Deliverable | Details |
|----|-------------|---------|
| DC1 | Unit tests — CSA | `tests/test_csa_parsers.py` — at least 3 tests per CSA parser |
| DC2 | Unit tests — Sellio | `tests/test_sellio_parser.py` — at least 5 tests |
| DC3 | Organic filter test | Verify non-organic items from Teva Shuk are NOT included in normalized observations |
| DC4 | Resolution verification | ≥85% resolution rate for each new source |
| DC5 | Publish + upload | Run `catalog_renormalize` + `run_publisher --upload` |

---

## 4. Architecture Decisions

### CSA Basket Handling

The normalizer already supports basket products:
- `is_basket_product = true` → `normalized_price_value = NULL`
- Baskets contribute to basket-level aggregation, not per-item price comparisons
- Basket products display with 🧺 emoji in the public report

New consideration: CSA baskets often have a fixed weekly/bi-weekly price. The observation frequency differs from daily-price-grid sources. The `rolling_aggregate.py` 7-day window should naturally accommodate this — one observation per week is sufficient.

### Organic Filtering for Retail Sources

This is the first retail source with mixed organic/conventional products. The chosen filtering strategy becomes the **standard for all future Phase B retail sources**. Team 10 must:

1. Document the chosen approach in the completion report
2. Explain why it was chosen over alternatives
3. Ensure it's extensible to future retail sources (supermarket chains)

### Display Bucket Integration

CSA sources are classified as `display_bucket = 'grower'` with `source_group = 'basket_csa'`. Their products will appear under the "מגדלים" filter.

Teva Shuk is `display_bucket = 'store'`. Its products will appear under the "חנויות" filter. This is the **first store-only source** being activated, which means the "חנויות" filter button will become functional.

---

## 5. Acceptance Criteria

| # | Criterion | Threshold |
|---|-----------|-----------|
| AC1 | CSA basket sources extract basket products | ≥2 of 3 CSA sources producing data |
| AC2 | Teva Shuk extracts organic-only products | ≥20 organic items extracted, 0 conventional |
| AC3 | Organic filter is documented and extensible | Architecture decision documented |
| AC4 | Resolution rate per new source | ≥85% |
| AC5 | Published product count | ≥90 (currently 83) |
| AC6 | "חנויות" filter shows Teva Shuk data on live page | Functional on nimrod.bio |
| AC7 | All existing tests pass (no regression) | 0 failures |
| AC8 | New unit tests | ≥8 tests PASS (3+ CSA, 5+ Sellio) |
| AC9 | Live page updated | HTTP 200, new products visible |

---

## 6. Source-Specific Technical Notes

### SRC033 — חוות שורשים (havatshorashim.co.il)

From Team 100 spike:
- Static HTML site
- Basket products with sizes (small, medium, large)
- May require `StandaloneHTMLCollector` (already available)

### SRC034 — משק אורגני (meshekorgani.co.il)

From Team 100 spike:
- Static HTML
- Subscription model — may show weekly basket price

### SRC035 — משק יוסף (meshek-yosef.co.il)

From Team 100 spike:
- Static HTML
- Hybrid: sells baskets AND individual items
- Individual items should be extracted as normal price-grid items

### SRC036 — טבע שוק (teva-shuk.co.il)

From Team 100 spike:
- Sellio platform (Next.js + Redux)
- `__NEXT_DATA__` JSON in page source contains full product catalog
- 129 products observed, mixed organic/conventional
- Similar extraction pattern to Rexail (existing `rexail.py` parser) — consider shared utilities
- `storeProductsByCategoryId` pattern may be usable

---

## 7. Out of Scope

- Additional Phase B retail sources beyond SRC036
- Supermarket chain integration
- Modifying the existing filter bar UI (already supports `store` type)
- mypips sources (covered by M10.4)
- Changes to basket aggregation logic (existing normalizer handles it)

---

## 8. QA and Sign-off Process

```
Step 1: Team 10 implements and files Completion Report
        → _COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M10_5_COMPLETION_TEAM10.md

Step 2: Team 10 files QA Review Request to Team 50
        → _COMMUNICATION/TEAM_50/QA_REQUEST_M10_5_TEAM10.md

Step 3: Team 50 validates:
        - All acceptance criteria AC1–AC9
        - Full pytest suite green
        - Organic filter correctness verified
        - Live page renders correctly with new data
        - "חנויות" filter functional
        → Files QA report with PASS/FAIL

Step 4: Team 100 architectural review
        → Verifies organic filter strategy is sound and extensible
        → Reviews basket handling for CSA sources
        → Signs off on M10.5 sub-gate

Step 5: Return completion notice to Team 100
        → _COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M10_5_COMPLETION_NOTICE_TEAM10.md
```

---

## 9. Dependencies

| Dependency | Required By | Status |
|------------|-------------|--------|
| M10.4 headless infrastructure | DB2 (Sellio may need JS rendering) | ACTIVE |
| Existing Rexail parser | DB2 (shared patterns with Sellio) | ✅ Available |
| Basket normalizer logic | DA6 (basket product handling) | ✅ Available |
| `display_bucket` filter | DB8 (store filter) | ✅ Available |

**Note:** If Sellio (`teva-shuk.co.il`) serves product data via `__NEXT_DATA__` without JS rendering, Team 10 MAY proceed with DB1–DB8 without waiting for M10.4 headless infrastructure. If JS rendering is required, M10.4 D1–D4 must be complete first.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
