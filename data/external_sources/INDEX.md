# External Sources Index — SFA Crop Book

**Generated:** 2026-05-26
**Total files copied:** 74 (~40 MB)
**Coverage:** Israeli sources + Tend multi-year + JMF extensions + Curtis Stone + misc
**Companion docs:**
- `_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/MISSION_v1.0.0.md` (web scout mandate)
- `_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/LOCAL_FILES_MAPPING_v1.0.0.md` (initial scan)
- `data/external_sources/_extraction_metadata.json` (machine-readable per-file metadata)

## Conventions

- **Source binaries gitignored** (XLSX/DOCX/PDF/JPG/CSV); only INDEX.md + raw_text/ + sample_extracts/ are committed.
- **File codes:** `L01`-`L49` match the local-files mapping; canonical filenames in `data/external_sources/<subdir>/<L##>_<descriptor>.<ext>`.
- **Quality score:** S (signal — exact gap-fill), M (medium — partial), L (low — supplementary), X (skip).
- **Quantity score:** XL (>500 rows / >50pp), L (100-500 / 10-50pp), M (20-100 / 3-10pp), S (<20 / <3pp).
- **Language:** he / en / it / fr / mixed.

---

## 🟢 TIER 1 — INGEST IMMEDIATELY (signal-quality, ready to parse)

| Code | File | Q-sig | Q-qty | Lang | Fields verified by scan | Wave |
|---|---|:---:|:---:|:---:|---|:---:|
| **L01** | `israeli/L01_GROWORGANIC_sowing_dates_base.xlsx` | **S** | M | he | Sowing/planting per crop × season (Spring/Summer/Fall/Winter) with markers EQX/S22/EFS/ECS; legend `S=שתילים, X=זרעים`. Sheet `גיליון1` is 86 rows × 26 cols. **HIGH-gap: Israeli planting calendar** | 1 |
| **L03** | `israeli/L03_IDAN_winter_planning.xlsx` | **S** | L | he | Sheet `תוכנית גידול` 203 rows × 19 cols. Per crop/variety: planting date, germ date, harvest start, harvest end, area m², bed marker, rows/bed, in-row spacing, plants/m², total plants, total yield kg. Plus summary rows: planting→harvest days, harvest duration, monthly availability. **HIGH-gap: 2nd Israeli grower data** | 1 |
| **L04** | `israeli/L04_IDAN_summer_planning.xlsx` | **S** | L | he | Same structure as L03 for summer crops (150 rows × 17 cols). First entry: cherry tomato red, planted 13/4/2017, 75 days planting→harvest, 3-5 months harvest duration, May-Oct availability | 1 |
| **L36** | `israeli/L36_BUSTAN_sowing_calendar.pdf` | **S** | S | he | 1-page Israeli edible-garden calendar from גינת בוסתן. Columns: crop, growing notes, sowing/planting per **calendar month**. Legend: `ז=זריעה, ש=שתילה, ש/ז=either, ז*=after germination`. **HIGH-gap: Israeli monthly calendar** | 1 |
| **L12** | `jmf_extension/L12_cover_crop_chart.pdf` | **S** | S | en | 1-page JMF cover crop chart with **germination temperature (°F+°C), USDA hardiness zone, sowing window, inoculum, winter survival**. Crops: Clover (Crimson/Red), Common Vetch, Field Peas, Hairy Vetch, Melilot, Barley, Buckwheat, Fall Rye, Oat, Spring Wheat, Winter Wheat. **HIGH-gap: germination temperature & hardiness zone** | 1 |
| **L07/Tend 2019** | `tend_multi_year/Tend_2019_*.csv` | M | XL | en+he | CROP_PLAN 442 rows, GREENHOUSE_PLAN 255 rows, **HARVESTS 1,884 rows**, NOTES 31, TASKS 566, SEED_LIST 382. Same schema as Tend_2022 already loaded. **3.8× more harvest data** | 1 |
| **L07/Tend 2020** | `tend_multi_year/Tend_2020_*.csv` | M | XL | en+he | CROP_PLAN 724, GREENHOUSE_PLAN 479, **HARVESTS 3,720**, NOTES 51, TASKS 1,101, SEED_LIST 610. **Richest year — 7.6× Tend_2022 harvest volume** | 1 |
| **L07/Tend 2021** | `tend_multi_year/Tend_2021_*.csv` | M | XL | en+he | CROP_PLAN 552, GREENHOUSE_PLAN 318, HARVESTS 1,723, NOTES 35, TASKS 825, SEED_LIST 412 | 1 |

---

## 🟡 TIER 2 — INGEST AFTER STRUCTURED EXTRACTION (Hebrew narrative DOCX/PDF — needs LLM extraction)

| Code | File | Q-sig | Q-qty | Lang | Content scan | Wave |
|---|---|:---:|:---:|:---:|---|:---:|
| **L02** | `israeli/L02_AOSNOT_variety_info.docx` | **S** | XL | he | 1.3MB Hebrew **per-crop encyclopedia**. Each entry has: כללי (general), שתילה (planting), גיזום (pruning), תנאי השקיה, תנאי אור, תאריך שתילה, מזיקים, קצב צימוח, **עמידות (frost/cold resistance)**, אזורים בארץ, **תאריך פריחה**, **תאריך תנובה**, האבקה, שם לטיני. Per-crop NI-tier extraction will yield ~10 structured fields/crop. **MAJOR HIGH-gap filler** | 2 |
| **L11** | `israeli/L11_variety_trials_2021.pdf` | **S** | M | he | 14-page **official שה"מ (Israeli Extension Service)** variety trial — hydroponic lettuce, summer 2021. Authors: זקס, עומרי×2, ברנהולץ. ~10 lettuce varieties tested; structured scores (color, heart closure, twisting, blistering, disease, taste, bolting, overall). Government-authoritative variety data. **NI tier (hard override)** for IL lettuce | 2 |
| **L14** | `jmf_extension/L14_FT_FINALE_NURSERYSEEDING.pdf` | M | M | en | 13-page JMF Fiche Technique on nursery seedling production. Already-noted gap from prior WP-B2. Per-crop: days in plug cells, seeds per cell, potting mix type, **germination temperature**, container type, days before potting up | 2 |
| **L13** | `jmf_extension/L13_cover_crops_guide.pdf` | M | M | en | 7-page JMF cover crops guide (companion to L12 chart). Narrative + 4 main functions, planting periods | 2 |
| **L16** | `jmf_extension/L16_seeding_in_cell_flats.pdf` | M | S | en | 3-page JMF seeding-in-cell-flats protocol. Nursery technique extension | 2 |
| **L09** | `israeli/L09_hydro_vegetable_guide.pdf` | L | L | he | 24-page **official שה"מ hydroponic vegetable manual** by זקס, אדלר, עומרי et al. TOC: DWC, NFT, comparison table, which crops fit hydro, water quality, structure, irrigation. Largely hydro-specific but has comparison tables useful for some crops | 2 |
| **L10** | `israeli/L10_DR_ZACKS_leafy_hydro_survey.pdf` | M | L | he | 52-page survey by ד"ר מולי זקס on leafy hydroponics in Israel. Need full extraction to assess (cover page only is contact info) | 2 |
| **L49** | `israeli/L49_IDAN_market_gardening_tech.xlsx` | M | L | he | 4 sheets, 192 rows × 17 cols planning + 74×21 plot map by month. **2018 update** of L03/L04 (newer Idan data). Sheet `תוכנית גידול` similar fields; sheet `מפת חלקה` is month-by-row plot tracker | 2 |
| **L40** | `urban_farmer/L40_curtis_crop_profiles.xlsx` | M | M | en | **Curtis Stone Master Chart**: 23 crops × 29 columns. Has Avg DTM from seed date, harvest season, Crop Type, **CVR (5/5 Curtis-Value-Rating)**, Quick/Steady (Q/S), DS/TR, Bed Size, Walkway width, When to DS, When to TRN, Jang Roller, EW Plate. **Cross-validation for blending vs JMF/Tend** | 2 |

---

## 🟠 TIER 3 — SECONDARY VALUE (peek then decide; some are scanned/needs OCR)

| Code | File | Q-sig | Q-qty | Lang | Content scan | Wave |
|---|---|:---:|:---:|:---:|---|:---:|
| **L05a** | `israeli/L05a_IDAN_seedlings_winter_18-19.xlsx` | M | S | he | Bi-weekly seedling order tracker (21 rows × 12 cols). Crops × dates (18/9, 2/10, 16/10, ...) with cell values = `מגש` (tray) or `# שתילים`. **Succession planting pattern** | 3 |
| **L05b** | `israeli/L05b_IDAN_seedlings_summer_18-19.xlsx` | M | S | he | Same structure for summer half-year | 3 |
| **L06** | `israeli/L06_covers_and_tunnels.xlsx` | L | M | he | Sheet 1: 68×30 plot × month tunnel-coverage tracker (`hobbitHome` farm). Sheet 2: 29-row **SEED ORDER from FRANCHI Italy** — seed variety catalog with codes. Cross-source for L04 (tomato heritage varieties source) | 3 |
| **L41** | `urban_farmer/L41_curtis_chart_*.jpg` (34 images) | L | XL | en | 34 scanned pages from Curtis Stone's "The Urban Farmer" book — per-crop sections. Each page has structured header (Planting Specs, Varieties, DTM, Avg yield per bed, Avg gross profit per bed) + narrative. **L40 XLSX has most structured data; images add per-crop narrative**. OCR needed for ingestion | 3 |
| **L45** | `israeli/L45_2017_data_summary.xlsx` | M | L | he | 10 sheets. `מפת חלקה` 281 rows × 20 cols (plot map by month). `תכנית שתילה ומעקב` 100 rows × 23 cols (planting plan + tracking with status: גידול/קטיף). Nimrod's own 2017 farm operations data | 3 |
| **L43** | `israeli/L43_customer_leafy_greens.xlsx` | L | M | mixed | 11 sheets, mostly business/financial (cost per head, space per month, sales projections). Limited crop knowledge value. **Likely SKIP after deeper peek** | 3 |
| **L26** | `jmf_extension/L26_BEIN_HATLAMIM_hebrew.pdf` | X | S | he | ❌ **Disappointing**: NOT a Hebrew JMF translation. 1-page bank transfer receipt for payment to "חוות בין התלמים". **SKIP** | — |
| **L44** | `israeli/L44_israel_organic_greens.pdf` | X | S | en | 1-page wiring/spec diagram (`15pcs x 40W + 5pcs x 20W = 700Wmax`). **SKIP** | — |
| **L38** | `misc_investigate/L38_libretto_orto_italian.pdf` | ? | M | it | 9-page Italian gardening manual. PDF text extraction returned empty — likely scanned/image-based. **Needs OCR + Italian translation if pursued**. Defer unless Italian Mediterranean adaptation becomes priority | 3 |
| **L39** | `misc_investigate/L39_mesclun_guide.pdf` | L | S | en | JSS mesclun guide. Salad-mix specific, limited general value | — |

---

## ❌ TIER 4 — Tend 2018 (LOW VOLUME — verify before ingestion)

| Code | File | Reason |
|---|---|---|
| **Tend 2018** | `tend_multi_year/Tend_2018_*.csv` | CROP_PLAN 60 rows, TASKS 97 rows — but **HARVESTS=0, NOTES=0**. May be just initial setup data. **INVESTIGATE before ingesting; lower priority than 2019-2021** |

---

## Summary statistics

| Tier | Files | INGEST | Investigate | Skip |
|------|------:|-------:|------------:|-----:|
| 1 (HIGH signal-fill) | 8 | 8 | 0 | 0 |
| 2 (Needs extraction) | 9 | 9 | 0 | 0 |
| 3 (Secondary) | 9 | 3 (L05ab, L06) | 4 (L41, L45, L43, L38) | 2 (L26, L44) |
| 4 (Tend 2018) | 1 | conditional | 1 | 0 |
| Curtis images | 34 | OCR pass | 0 | 0 |
| Tend non-crop (5 yrs) | — | — | — | already skipped |

**Total local sources to INGEST/extract:** ~20 file groups; ~28 MB of structured/semi-structured data covering HIGH-gap fields: Israeli planting calendar (L01, L36), 2nd Israeli grower data (L03, L04, L05ab, L49), variety encyclopedia (L02), variety trial gov-data (L11), germination temp + hardiness (L12, L14), 3 additional Tend years (L07 × 2019/20/21 = ~8,000 rows of harvests).

---

## See `WAVE_PLAN_v1.0.0.md` for the 3-wave execution plan.
