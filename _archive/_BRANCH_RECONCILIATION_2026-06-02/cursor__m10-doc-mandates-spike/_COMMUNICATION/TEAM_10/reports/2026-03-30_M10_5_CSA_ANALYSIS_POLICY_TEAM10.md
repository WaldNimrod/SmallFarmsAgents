# M10.5 — CSA basket data value and analysis policy (Team 10)

**Date:** 2026-03-30  
**Mandate:** `MANDATE-20260404-M10-5-CSA-RETAIL`  
**Audience:** Team 100 (architecture), project lead (Nimrod), Team 50 (QA)

---

## 1. Problem

A **headline basket price without context** (what varies inside the basket, how often it changes, pickup vs delivery, cutoffs) is a weak signal for the OrganicMarketAgent community index and can mislead cross-farm comparison. This policy defines **minimum context** and **V1 capture rules** before CSA rows are treated as “complete” for public transparency.

---

## 2. Site examination (SRC033–SRC035)

| Source | Platform | Pricing page (fetch target) | What is machine-readable in V1 |
|--------|----------|-----------------------------|----------------------------------|
| **SRC033** havatshorashim | Wix | `/organic-basket` | Structured text flow: **סל קטן / סל גדול / סל סטודנטים** with **₪** prices; separate **עלות משלוח** lines; narrative blocks for **weekly variability**, **delivery windows**, **“מה יש בסל”** (seasonal examples). |
| **SRC034** meshekorgani | Wix | `/basket` | Single paragraph with **two basket SKUs** (משפחתי 165 ש"ח, בסיסי 125 ש"ח); follow-on lines with **vegetable counts** (14 vs 10 types) and **weight hints** (כקילו / ~600g). **משלוח חינם** stated. |
| **SRC035** meshek-yosef | WordPress | `/סל-אורגני-עד-הבית/` (encoded URL) | **Delivery fees** and **minimum order (110 ש"ח)** in prose; **no stable product grid** on this URL in static HTML. Shop catalog appears **off-site / JS-heavy** — not used in this V1 delivery. |

---

## 3. Consultation (async)

- **Nimrod (product):** CSA price must ship with **content and logistics context** where the site provides it; defer fake “price-only” rows when context is missing.  
- **Team 100:** No new publish-schema columns in V1; use **`raw_payload_json`** for `csa_context` and publisher may surface footnotes later; **`is_basket_product`** path unchanged (`normalized_price_value` NULL for baskets).

---

## 4. Analysis policy — V1 rules

### 4.1 Minimum viable context (index-worthy)

A CSA **basket** line is **index-worthy** in V1 only if **all** hold:

1. **Named basket SKU** (e.g. small / large / family / student) parseable from the page.  
2. **Numeric price** in ILS tied to that SKU.  
3. **`raw_payload_json.csa_context`** populated with **at least one** of:  
   - `contents_summary` — short excerpt from the site about typical contents or counts; or  
   - `cadence_or_delivery_note` — excerpt about pickup/delivery rhythm, day-of-week, or cutoff language **if present**.

If (1)+(2) hold but (3) cannot be filled from the same page snapshot, the row may still be ingested but **`csa_context.context_incomplete: true`** must be set for QA visibility.

### 4.2 Dimensions committed in V1 vs deferred

| Dimension | V1 | Deferred |
|-----------|----|----------|
| Basket label + price | Yes | — |
| Contents / counts snippet | Yes (when present) | Full structured BOM |
| Pickup vs delivery / day / cutoff | Yes (free-text excerpt when present) | Normalized calendar model |
| Subscription terms | Excerpt only | Legal parsing |
| Per-item add-ons | Only where SRC035 grid exists | SRC035 full catalog |

### 4.3 Field mapping

- **`raw_payload_json` keys (CSA):**  
  - `parser`: `"csa_basket"`  
  - `csa_site`: `havat_shorashim` \| `meshek_organi` \| `meshek_yosef` \| `shekel_line_baskets` (generic multi-line `סל`/`ארגז` + `ש"ח`; optional `shekel_require_organic` in `selector_profile`)  
  - `csa_context`: `{ "contents_summary"?: str, "cadence_or_delivery_note"?: str, "context_incomplete"?: bool }`

### 4.4 Public transparency

- Baskets remain **`is_basket_product`**; public copy continues to use the **basket** presentation (e.g. 🧺) per existing publisher rules.  
- Glossary alignment: use English internal keys above; no Hebrew in code or JSON keys.

### 4.5 SRC035 handling

Until a **stable, automatable** price grid exists under the approved `base_url`, **SRC035** may produce **zero basket SKUs** from the chosen entry URL. **Do not fabricate prices.** Ingestion may complete with zero `raw_extracted_items`; remediation = future URL/Playwright scope with Team 100 approval. **AC1 (“≥2 of 3 CSA”)** is met by **SRC033 + SRC034** if SRC035 is blocked by data availability.

---

## 5. Teva Shuk (SRC036) — retail transparency note

SRC036 uses **Sellio** with **client-rendered** grids. V1 uses **Playwright** (`platform_family: sellio`) plus **`SellioParser`** on rendered HTML. **Organic-only strategy (mandate DB3):** **Option A + C hybrid** — primary `entry_url` targets an **organic-labelled category**; parser applies **`organic_only`** filter: keep lines whose display name contains **אורגני / אורגנית / אורגניים** (and common Latin “organic” for robustness). Documented as extensible to additional category URLs via `selector_profile` without schema change.

---

## 6. Gate for Part A implementation

Parsers and migrations **must** populate `csa_context` per §4.1–4.3 for SRC033 and SRC034. SRC036 must satisfy mandate organic filter tests. SRC035 follows §4.5.
