# CSA / basket source candidates — inventory and web discovery

**Date:** 2026-04-06  
**Team:** Team 10  
**Plan:** CSA sources expansion (LOD for M13 basket UI + go-live diversity)

---

## 1. SQL inventory (connected dev DB)

### 1.1 `basket_csa` / `csa_basket` sales channel

| code   | name                 | status   | active | Latest-run `raw_rows` | `normalized_observations` |
|--------|----------------------|----------|--------|-------------------------|-----------------------------|
| SRC003 | ח'ביזה               | active   | true   | 5                       | 25                          |
| SRC007 | סלסילה               | active   | false  | 0                       | 0                           |
| SRC033 | חוות שורשים          | active   | true   | 3                       | 6                           |
| SRC034 | משק אורגני — המעפיל  | active   | true   | 2                       | 2                           |
| SRC035 | משק יוסף             | active   | true   | 0                       | 0                           |
| SRC038 | הענתיות (mypips)     | candidate| false  | (n/a recent)            | —                           |

### 1.2 Normalizer types

- **`csa_basket`:** SRC033, SRC034, SRC035 only (static `CsaBasketParser`).
- **`basket_only`:** SRC003, SRC007 (`SimpleProductGridParser` + easyFarm-style selectors for SRC003).

### 1.3 Distinct farms with basket-class observations today

Beyond static CSAs, **SRC002** (easyFarm) exposes **daily organic basket lines** (e.g. `סל אורגני משפחתי ליום`, `סל אורגני רגיל ליום …`) — already **normalized** (mapped to basket catalog products). **SRC004** exposes **ארגז ירקות גדול** (normalized); **ארגז ירקות מקומי** / **קיימא** remain **ignored** by global scope rule **id 68** (`contains` `ארגז ירקות מקומי`) — do not remove without Team 100.

**Conclusion:** For “≥3 farms,” the DB already has **Chubeza (SRC003) + Shorashim + Meshek Organi** plus **Sabta (SRC002)** basket lines. **SRC035** remains 0 SKU per [M10.5 CSA analysis policy](_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md) §4.5.

---

## 2. SOURCE_MAP crosswalk (docs/SOURCE_MAP_MASTER_HE.md)

| Map ID | Role in map              | Ingest today? | Parser path (A–D) |
|--------|--------------------------|---------------|-------------------|
| SRC003 | Core CSA / boxes         | Yes           | B — easyFarm `basket_only` |
| SRC007 | Salsila baskets          | No (inactive) | C — static HTTP insufficient (see §3); headless TBD |
| SRC002–006 | easyFarm shops      | Mixed         | B — catalog; basket lines where present |
| SRC008–011 | Standalone / aggregator | Various      | B/C depending on site |

**A** = static marketing `CsaBasketParser` + `csa_site`  
**B** = easyFarm / grid + aliases  
**C** = headless / JS catalog  
**D** = legal or candidate-only  

---

## 3. Web discovery (§4.1 checklist, sampled 2026-04-06)

| URL / host | HTTP | Price + named basket in static HTML? | Notes |
|------------|------|--------------------------------------|--------|
| salsila.co.il (home + `/cat/הסלסילה-השבועית`) | 200 | No in static snapshot | `product_title` shell; weekly grid client-rendered — matches migration 012 rationale |
| arugot.org/he/shop-2/ | 200 | No (for produce) | WooCommerce `li.product` = therapeutic services, not vegetable baskets |
| bustan.org.il | 200 | No | No `סל…N ש"ח` paragraph in homepage sample |
| chubeza.co.il (public) | 200 | No in sampled text | Subscription UX on easyFarm subdomain (SRC003), not public homepage |
| hashomer.org.il | 200 | No | No paragraph basket pattern in homepage sample |
| green.org.il | 200 | No | No matches |
| organic.org.il | 200 | No | No basket price lines in sample |
| Many `*.co.il` farm guesses | DNS / reset | — | Environment DNS limits; validate on operator network |

**Outputs:** **No new third static CSA URL** was verified in this session beyond existing SRC033/034 patterns. **Next step:** operator-led validation of 2–3 farm URLs (Wix/WordPress “מחירון סל” pages), then attach with parser `shekel_line_baskets` (see code) or dedicated `csa_site`.

---

## 4. Engineering delivered in repo (see CHANGELOG)

1. **`csa_site: shekel_line_baskets`** — generic extractor for multiple `(סל|ארגז)…(\d+) ש"ח` lines in one HTML page (with optional `shekel_require_organic` in `selector_profile`).
2. **Migration `066`** — forward-looking **global aliases** for common Hebrew basket phrases; **SRC075** placeholder source (**inactive** `sources` + `source_fetch_profiles`) with `shekel_line_baskets` profile — replace `entry_url`/`base_url` with a **distinct** validated farm before activation (placeholder points at Meshek Organi basket URL only as a known-good HTML shape).

---

## 5. Recommendations

1. **Do not** re-enable SRC007 without a **headless** proof on the weekly category URL and Team 100 alignment (cost = Sellio-class).
2. **Prefer** new farms using **same paragraph pattern as SRC034** — lowest maintenance; use **`shekel_line_baskets`** until a site needs custom logic (then add a dedicated `csa_site`).
3. **SRC035:** only after a URL with stable priced SKUs is approved (policy §4.5).
4. **Publish:** extra basket sources help **observation diversity**; **G-PRE-5** still depends on **≥2 distinct sources per product bucket** — coordinate with mypips/retail coverage.
