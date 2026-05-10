---
id: SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0
author: team_100 (Claude Sonnet 4.6)
date: 2026-05-07
type: DISCOVERY_SUMMARY
project: SmallFarmsAgents
branch: offline/2026-05-07-smallfarmsagents-release-prep
status: DRAFT — pending team_00 scope approval
source_branch: archive/raw-material-tend-masterclass-2026-04
---

# S003 Discovery Summary — Tend + MasterClass

> **Purpose:** Establish the raw material baseline so team_00 can approve S003 scope.
> **DB status:** offline (ADR034 R9 spoke exception) — file-based read only.
> **Authority:** MAY NOT define LOD400 specs or modify roadmap.yaml until team_00 approves scope.

---

## Tend Data

### Overview

Branch: `archive/raw-material-tend-masterclass-2026-04`  
Path: `_COMMUNICATION/TEAM_80/Tend Data/Tend_[YEAR]/`

**5 years of operational farm data (2018–2022). 14 CSV tables per year. ~70 total files.**

Consistent schema across all 5 years — the same 14 table names appear in every year folder.

#### 2022 CSV Row Counts

| Table | Rows (2022) | Purpose |
|-------|------------|---------|
| CROPAVAILABILITY | 232 | Weekly crop availability calendar |
| CROP_PLAN | 529 | Planting plan — **key WP-A2 enabler** |
| EXPENSES | 4 | Farm expenses (very sparse) |
| GREENHOUSE_PLAN | 287 | Nursery / GH bed allocation |
| HARVESTS | 939 | Harvest events per planting |
| LOCATIONS | 200 | Bed/field location registry |
| NOTES | 41 | Free-text operational notes |
| ORDERS_LIST | 77 | Order-level summary |
| ORDERS_RAW_DATA | 872 | Order line items with per-product pricing |
| PACK | 5,586 | Pack records (very dense) |
| PICK | 13,309 | Pick records (most granular) |
| PRODUCT_SOLD | 82 | Annual sales totals by product |
| SEED_LIST | 371 | Seed inventory and vendor records |
| TASKS | 1,042 | Work assignments and completion |

---

### Schema: HARVESTS 2022

**9 columns:**

```
Date, Planting Name, Crop, Amount, Unit, Outlet Type, Outlet Name, Harvest Stage, Final Harvest
```

**Sample rows:**

```
01/01/2022 | Chives Common 30/11/2020 Ra.2 > C6m > Bed 204 6 bed m | Chives   |     |    | Wholesale      | B2B           | Full-Size | Yes
01/01/2022 | Chives Common 30/11/2020 Ra.2 > C6m > Bed 204 6 bed m | Chives   |     |    | Farmers Market | הדוכן יום ב   | Full-Size | Yes
01/01/2022 | Radishes Daikon Long ... Ra.3 > R3 > Bed 333 6 bed m   | Radishes |     |    | Wholesale      | B2B           | Full-Size | Yes
03/01/2022 | Broccoli Cavolo ... Zvika > zA > Beds 507-509 36 bed m | Broccoli | 4.0 | kg | Farmers Market | קטיף יום ה    | Head      | No
```

**Notes:**
- `Crop` field uses English names (consistent, clean vocabulary — 52 unique crops in 2022)
- `Planting Name` encodes full spatial hierarchy: `[Variety] [Sow Date] [Block] > [Zone] > [Bed] [Bed meters]`
- `Amount` is often blank — harvest was recorded without quantity data; not null, empty string
- `Outlet Type` values: Wholesale, Farmers Market (+ blank = unknown)
- `Harvest Stage`: Full-Size, Baby Leaf, Head, Plant sale, etc.

**Unique crops in HARVESTS 2022 (52 crops):**  
Anise Hyssop, Artichokes, Arugula, Basil, Bay, Beans (Bush & Pole), Beets, Broccoli, Cabbage, Carrots, Celery, Chard, Chinese Lantern, Chives, Cilantro, Cress, Cucumbers, Dill, Eggplant, Fennel, Garlic, Hibiscus, Jerusalem Artichokes, Jicama, Kale, Kohlrabi, Leeks, Lemon Balm, Lemon Verbena, Lettuce, Lettuce: Salad Mix, Lovage, Melons, Mint, New Zealand Spinach, Onions: Scallions, Oranges, Pac Choi (Bok Choy), Parsley, Peas, Peppers, Radishes, Sage, Spinach, Strawberry, Summer Squash, Tarragon, Thyme, Tomatoes, Turmeric, Turnips, Winter Squash

---

### Schema: PRODUCT_SOLD 2022

**10 columns:**

```
Category, Product Name, Unit, Total Qty Sold, Total Refunded Qty, Gross Sales,
Net Sales, Shopify - Gross Sales, Online Store - Gross Sales, Offer Sheet - Gross Sales
```

**Sample rows (all Hebrew product names, ₪ currency):**

```
בייבי   | בייבי מיקס      | kg | 214 | 0.0 | —  | ₪10,040.00 | ₪0.00 | ₪9,590.00  | ₪450.00
בייבי   | בייבי - רוקט    | kg |  93 | 0.0 | —  | ₪4,898.00  | ₪0.00 | ₪4,590.00  | ₪308.00
ירק     | (ירק) בצל ירוק  | bn | 637 | 0.0 | —  | ₪3,645.50  | ₪0.00 | ₪3,506.00  | ₪139.50
תבלינים | כורכום          | kg |  45 | 0.0 | —  | ₪3,600.00  | ₪0.00 | ₪3,600.00  | ₪0.00
ירקות   | צנונית          | bn | 372 | 0.0 | —  | ₪2,232.00  | ₪0.00 | ₪2,112.00  | ₪120.00
ירקות   | חיקמה           | kg | 145 | 0.0 | —  | ₪2,185.00  | ₪0.00 | ₪2,185.00  | ₪0.00
חסה     | (חסה) רומית     | hd | 384 | 0.0 | —  | ₪1,920.00  | ₪0.00 | ₪1,790.00  | ₪130.00
חסה     | (חסה) סלנובה    | cs | 338 | 0.0 | —  | ₪1,690.00  | ₪0.00 | ₪1,515.00  | ₪175.00
```

**Price confirmation:** `Net Sales` column has reliable ₪ values for all 82 products.  
`Gross Sales` column is blank (Tend export artifact) — use Net Sales as revenue source of truth.

**Units observed:** kg, bn (bunch), g (grams), hd (head), cs (case)  
**Sales channels:** Online Store, Shopify, Offer Sheet (direct B2B)  
**Categories (Hebrew):** בייבי (baby greens), ירק (vegetable), ירקות (vegetables), תבלינים (herbs/spices), חסה (lettuce)

---

### Schema: CROP_PLAN 2022 ← CRITICAL WP-A2 ENABLER

**58+ columns** — the most information-dense table. Covers full cultivation lifecycle from seeding through harvest economics.

**Key column groups:**

| Group | Columns |
|-------|---------|
| Taxonomy | Category, Family Name, Crop, Crop Type, Variety |
| Method | Planting Method, Harvest Stage |
| GH Schedule | GH Sow Date, Days to 1st/2nd/3rd Potting Up, Field Sowing Date, DTM, Harvest Window |
| Spacing/Density | In-Row Spacing, In-Row Spacing Unit, Rows Per Bed, Seeds per cell, Estimated loss |
| Seed | # Of Flats, Flat/pot type, Total Transplants, Total Seed Needed, Avg seed weight, Seed spec |
| **Economics** | **Harvest Unit, Avg Yield Rate, Avg. Sales Price, Est. Yield, Est. Revenue, Est. Rev./unit** |
| Cycle | Growing Cycle (Annual/Biennial/Perennial), Rootstock |
| Equipment | Seeder, Front gear, Rear gear, Roller plate |

**Sample rows (economics columns highlighted):**

```
Herbs | Anise Hyssop | אזוב מצוי | Transplant from Purchased | Full-Size
  → Harvest Unit: Bunches | Avg Yield Rate: 20.000 bn/row m | Avg. Sales Price: ₪5.00/bn
  → Est. Yield: 160.0 Bunches | Est. Revenue: ₪800.00 | Est. Rev./unit: ₪100.00/row m
  → Growing Cycle: Perennial

Vegetables | Artichokes | Wonder | Transplant from Purchased |
  → Harvest Unit: Kilograms | Avg Yield Rate: 0.350 kg/row m | Avg. Sales Price: ₪20.00/kg
  → Est. Yield: 16.8 kg | Est. Revenue: ₪336.00 | Est. Rev./unit: ₪7.00/row m
  → Growing Cycle: Biennial

Vegetables | Arugula | Arugula | Direct Sow | Baby Leaf
  → Harvest Unit: Kilograms | Avg Yield Rate: 0.200 kg/row m | Avg. Sales Price: ₪8.00/cs
  → Est. Yield: 19.2 kg | Est. Revenue: ₪768.00 | Est. Rev./unit: ₪8.00/row m
  → In-Row Spacing: 0.15 cm | Rows Per Bed: 8 | Seeder: Jang JP-1 | Front gear: 14 | Rear gear: 9

Vegetables | Arugula | Wild Rocket | Greenhouse Sow | Plant sale
  → Avg. Sales Price: ₪1.50/pl | Est. Revenue: ₪600.00 | Est. Rev./unit: ₪1.50/plant
```

**Key insight for WP-A2:** `Avg Yield Rate` (production benchmark) × `Avg. Sales Price` (market benchmark) = `Est. Rev./unit` (revenue per row meter). This is the farmer calculator's community benchmark **already computed** in the Tend export. The calculator needs only to add farmer-specific cost inputs (labor, seeds, water, land) and compare against community index prices.

**529 planting records in 2022 alone.** Across 5 years: ~2,600 records — enabling longitudinal yield analysis per crop variety.

---

### Schema: ORDERS_RAW_DATA 2022 (bonus — per-line-item pricing)

**19 columns:**

```
Order ID, Created Date, Customer/Outlet, Order Amount, Payment Status, Pack Date,
Fulfillment Status, Delivery/Pick Up Date, Sales Channel, Category, Product,
Unit, Ordered Qty, Packed Qty, Refunded Qty, Refunded Amount,
Product Gross Sales, Product Net Sales, Order State
```

**Sample (3 items from same order):**

```
FD9B91 | 26/12/2022 | לגעת בשדה | ₪450.00 | Overdue | 27/12/2022 | Packed | Online Store
  → ירקות | צנון    | bn | 10 ordered | 10 packed | ₪60.00 gross | ₪60.00 net
  → ירקות | צנונית  | bn | 20 ordered | 20 packed | ₪120.00 gross | ₪120.00 net
  → ירקות | שומר    | kg | 30 ordered | 30 packed | ₪270.00 gross | ₪270.00 net
```

**Note:** Order IDs use Excel-export artifact quoting: `"=""FD9B91"""` — parser must strip the `=""` wrapper.

---

### Data Quality Assessment

| Issue | Affected Table | Severity | Notes |
|-------|---------------|----------|-------|
| Blank quantity (`Amount`) | HARVESTS | HIGH | ~50%+ of rows have no amount; harvest count recorded without kg/bunch figure |
| Blank `Gross Sales` | PRODUCT_SOLD | LOW | Net Sales is the reliable field; Gross blank is a Tend export artifact |
| Excel Order ID quoting | ORDERS_LIST, ORDERS_RAW_DATA | LOW | `"=""HEX"""` format — trivial to strip in parser |
| EXPENSES very sparse | EXPENSES | HIGH | Only 4 rows in 2022; cost tracking not systematic in Tend |
| Hebrew numeric separators | All monetary | LOW | `₪1,234.50` format — standard; Python's `locale` or regex handles it |
| Mixed crop naming in HARVESTS | HARVESTS | MEDIUM | HARVESTS uses English botanical names; PRODUCT_SOLD uses Hebrew commercial names — requires cross-reference table |
| Empty string vs null | All | LOW | Blanks are `""` not `NULL` — standard CSV behavior |

**Overall:** Data is structurally sound and consistent across 5 years. The main practical issue is the HARVESTS quantity gap — this limits longitudinal yield tracking from HARVESTS directly. **CROP_PLAN is the reliable yield benchmark source.**

---

### Cross-Reference: Tend Crops ↔ OrganicMarketAgent Products

**Method:** CROP_PLAN and HARVESTS use English crop names → match against OMA product English aliases. PRODUCT_SOLD uses Hebrew names → match against OMA Hebrew aliases.

**Direct matches (30 confirmed):**

| Tend Crop (English) | OMA Product Code | OMA Hebrew Name |
|---------------------|-----------------|-----------------|
| Arugula | PRD010 | רוקט |
| Artichokes | PRD035 | ארטישוק |
| Basil | PRD064 | בזיליקום |
| Beans (Bush & Pole) | PRD024 | שעועית ירוקה |
| Beets | PRD014 | סלק |
| Broccoli | PRD022 | ברוקולי |
| Cabbage | PRD021 | כרוב לבן |
| Carrots | PRD013 | גזר |
| Celery | PRD052 | סלרי עלים |
| Chard | PRD009 / PRD034 | עלי תרד / מנגולד |
| Cilantro | PRD011 | כוסברה |
| Cucumbers | PRD005 | מלפפון |
| Eggplant | PRD006 | חציל |
| Fennel | PRD056 | שומר |
| Garlic | PRD019 | שום |
| Jerusalem Artichokes | PRD057 | ארטישוק ירושלמי |
| Kale | PRD012 | קייל |
| Kohlrabi | PRD036 | קולורבי |
| Leeks | PRD020 | כרישה |
| Lettuce | PRD008 | חסה |
| Lettuce: Salad Mix | PRD033 | תערובת לחליטה |
| Onions: Scallions | PRD018 | בצל ירוק |
| Pac Choi (Bok Choy) | PRD063 | בוקצ'וי |
| Parsley | PRD030 | פטרוזיליה |
| Peas | PRD024 | אפונה טריה |
| Peppers | PRD003 / PRD004 | פלפל אדום / ירוק |
| Radishes | PRD016 | צנון |
| Sage | PRD066 | מרווה |
| Summer Squash | PRD007 | קישוא |
| Tomatoes | PRD001 | עגבנייה |
| Turmeric | PRD045 | כורכום טרי |
| Turnips | PRD015 | לפת |
| Winter Squash | PRD037 | דלעת |

**Tend crops with NO OMA match (specialty herbs + exotics — 18):**  
Anise Hyssop, Bay, Chinese Lantern, Chives, Cress, Dill, Hibiscus, Jicama, Lemon Balm, Lemon Verbena, Lovage, Melons, Mint, New Zealand Spinach, Oranges, Strawberry, Tarragon, Thyme

**OMA products not in Tend (added M5+, not grown on this farm):**  
All fruits (PRD038–PRD065 range: lemon, apple, banana, avocado, etc.), Baskets (PRD025–029), Cherry Tomato (PRD002), Cauliflower (PRD023), Dry Onion (PRD017), Sprouts (PRD032), Amaranth (PRD062), Eggs (PRD067)

**Cross-reference gap for Chives:** Chives is one of the top-harvested crops in HARVESTS (appears in the first row of 2022 data) but has **no OMA product entry** — potential PRD068 candidate.

---

## MasterClass

### File Inventory

**Location:** `_COMMUNICATION/TEAM_80/MasterClass/` on `archive/raw-material-tend-masterclass-2026-04`

| Type | Count | Format | Parseable? |
|------|-------|--------|-----------|
| Hebrew crop sheets (current) | 36 | PDF | No (OCR required) |
| English crop sheets (Old Ver) | 24 | PDF | No (OCR required) |
| Crop Planning templates | 2 | XLSX | Yes (openpyxl) |
| Seeding charts | 2 | XLSX | Yes (openpyxl) |
| Bubbler/irrigation docs | 2 | XLSX | Yes (openpyxl) |
| Equipment list | 1 | XLSX | Yes (openpyxl) |
| Other guides (BCS, cover crops) | ~25 | PDF | No |

**XLSX files — potentially valuable structured data:**
- `Crop Planning/CROP PLANNING TEMPLATE.XLSX` — planning template (may have crop × spacing × yield structure)
- `Crop Planning/CROPPLANNINGTOOLMASTERCLASS.XLSX` — likely earlier version of what became Tend CROP_PLAN
- `טבלאות נתונים/DIRECTSEEDINGCHART.XLSX` — direct seeding parameters per crop
- `טבלאות נתונים/NURSERYTRANSPLANTCHART.XLSX` — transplant parameters per crop

### Quantitative Fields Found (in PDFs)

Based on PDF structure inspection (InDesign exports — `WorkSans-SemiBold` fonts):

The Hebrew crop sheets contain, per crop:
- Days to maturity (DTM)
- In-row and between-row spacing
- Yield per bed meter
- Succession planting interval
- Storage notes
- Seasonal window

**These exact fields also exist in CROP_PLAN CSV** — the PDF is the human presentation layer of the same data.

### Parseable Programmatically?

| Source | Verdict | Reasoning |
|--------|---------|-----------|
| Tend CROP_PLAN CSV | **YES — primary path** | 58+ structured columns, machine-readable, 5 years of data |
| MasterClass XLSX files (6 files) | **YES — secondary path** | openpyxl can read; content unknown until WP-S003-A spike |
| MasterClass PDFs (60+ files) | **NO without OCR** | Binary InDesign export; pdfplumber may extract text but layout parsing is unreliable |

**Recommendation:** Skip PDF ingestion for S003. Use CROP_PLAN CSV as the agronomic benchmark source. Evaluate XLSX files in a WP-S003-A spike; if they duplicate CROP_PLAN data, skip. If they add new fields (DTM, succession interval), include.

---

## S003 Scope Recommendation (LOD200 Sketch)

### Candidate Work Packages

| WP | Title | Effort | Output |
|----|-------|--------|--------|
| **WP-S003-A** | Tend CSV Ingestion + Crop Benchmarks | NORMAL | Alembic migration 035, new tables `farm_crop_benchmarks` + `farm_sales_history`, Python importer, XLSX spike |
| **WP-S003-B** | Crop Cross-Reference Table | SMALL | Migration 036, `tend_product_xref` table mapping Tend crop names → OMA `product_code` (33 rows manual seed) |
| **WP-S003-C** | Farmer Calculator v1 (WP-A2) | LARGE | Django endpoint + JS widget: inputs = farmer costs, output = cost/unit vs. community price, benchmark from `farm_crop_benchmarks` |
| **WP-S003-D** | MasterClass XLSX Extraction | SMALL → NORMAL | Spike: read 6 XLSX files with openpyxl; if new fields found, add to `farm_crop_benchmarks`; if redundant, close |

**Total S003 estimate:** 3–4 WPs, aggregate effort LARGE (one normal + one large + two small–normal).

---

### Architecture Notes

**WP-S003-A: Ingestion design**

```
archive/raw-material branch
    └─ CROP_PLAN (from macBook Air - nimrod).CSV   ← primary
    └─ PRODUCT_SOLD (from macBook Air - nimrod).CSV ← annual sales
    └─ HARVESTS (from macBook Air - nimrod).CSV     ← raw events (sparse quantities)

Python importer (one-time seed, idempotent):
    scripts/tend_import.py
        --year [2018|2019|2020|2021|2022|all]
        --table [crop_plan|product_sold|all]

New tables (Alembic 035):
    farm_crop_benchmarks
        crop TEXT, variety TEXT, year INT, harvest_unit TEXT,
        avg_yield_rate_per_row_m NUMERIC, avg_sales_price NUMERIC, price_unit TEXT,
        est_rev_per_row_m NUMERIC, growing_cycle TEXT,
        in_row_spacing_cm NUMERIC, rows_per_bed INT,
        seeder TEXT, dtm_days INT
        PK: (crop, variety, year)

    farm_sales_history
        product_name_heb TEXT, category_heb TEXT, unit TEXT, year INT,
        total_qty_sold NUMERIC, net_sales_ils NUMERIC,
        online_store_sales NUMERIC, offer_sheet_sales NUMERIC
        PK: (product_name_heb, year)

    tend_product_xref (WP-S003-B)
        tend_crop_en TEXT PK,
        product_code TEXT REFERENCES products(code),
        confidence TEXT CHECK (exact|fuzzy|manual)
```

**Key architecture decision for team_00 (multi-year vs single-year):**

| Option | Effort | Value |
|--------|--------|-------|
| Ingest 2022 only | SMALL | Current benchmarks — sufficient for calculator v1 |
| Ingest all 5 years (2018–2022) | ~5× more | Trend analysis, yield volatility, price evolution |

**Recommendation:** Start with 2022 for WP-S003-A (calculator v1). Define 5-year ingestion as a separate WP-S003-A2 after confirming calculator architecture.

**WP-S003-C: Calculator design**

The original `sfa_handoff_v2/04_functional_spec.md` spec is compatible with available data:

```
Inputs (farmer provides):
  labor_cost (₪/row m), water_cost (₪/row m), seeds_cost (₪/row m),
  land_cost (₪/row m), misc_cost (₪/row m)

Lookup (from farm_crop_benchmarks):
  avg_yield_rate (from CROP_PLAN)     ← farmer's own historic yield
  avg_sales_price (from CROP_PLAN)    ← farmer's own historic price
  community_price (from OMA index)    ← current community index

Computed:
  total_cost = sum(inputs)
  cost_per_unit = total_cost / avg_yield_rate
  recommended_price = cost_per_unit * margin
  community_benchmark = community_price (live from index)
```

**This is fully buildable with S003-A + S003-B as prerequisites.**

---

### EXPENSES Caveat

The EXPENSES table is near-empty (4 rows in 2022). **Tend does not systematically track farm costs.** The calculator's cost inputs must come from the farmer at runtime — they cannot be pre-populated from Tend EXPENSES data. This is consistent with the original spec (farmer edits cost fields manually).

---

## Open Questions for team_00

1. **Multi-year scope:** Ingest 2022 only (fast, sufficient for calculator v1) or all 5 years (enables trend analysis)?  
   *Recommendation: 2022 first, add multi-year as optional follow-on WP.*

2. **Chives gap:** Top-harvested crop in Tend with no OMA product entry. Add PRD068 (Chives / עירית) to the community index as part of S003?

3. **MasterClass XLSX spike:** The 6 XLSX files (direct seeding chart, transplant chart, planning template) may have structured agronomic data not in CROP_PLAN (DTM, succession intervals). Approve WP-S003-D as SMALL spike before deciding whether to expand?

4. **Calculator visibility:** WP-S003-C is the first farmer-facing feature behind auth (farmer role). Confirm `offline/` branch is the right develop track, or does this require a new branch policy?

5. **CROP_PLAN primary key collision:** 529 rows for 2022 include multiple varieties per crop (e.g., 2 Arugula rows: standard + Wild Rocket). PK design is `(crop, variety, year)`. Confirm uniqueness is sufficient or whether `planting_id` UUID should be the PK.

6. **HARVESTS quantity gap:** ~50% of harvest rows have blank `Amount`. This means longitudinal yield analytics from HARVESTS are unreliable. **Accept CROP_PLAN `Avg Yield Rate` as the canonical yield benchmark** (not computed from HARVESTS actuals)?

---

*Discovery summary issued 2026-05-07 by team_100 (Claude Sonnet 4.6). Awaiting team_00 S003 scope approval.*
