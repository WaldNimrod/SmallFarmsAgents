---
id: LOCAL_FILES_MAPPING_SFA-CROP-DATA-SCOUT_2026-05-26_v1.0.0
from: team_10 (local file system scan by Claude Code)
to: team_00 + team_110
date: 2026-05-26
scope: Local crop-relevant files in Documents/ tree (Mac + old MacBook backup)
total_files_scanned: 2,971
relevant_files: 67 (filtered for crop knowledge value)
---

# Local Files Mapping — Crop Data Sources

Companion to the web scout (team_80 `MISSION_v1.0.0.md`). This document maps
**files already on Nimrod's Mac** that are candidates for ingestion into the
SFA crop book — sorted by value/effort. The user picks INGEST / SKIP per row.

---

## Directories scanned

| Root | Files (relevant) |
|------|------------------|
| `~/Documents/Market Gardening/` | 2 PDFs (mostly empty — live folder) |
| `~/Documents/old Mac BackUpp/Market Gardening/` | 225 files (138 PDF, 41 XLSX, 34 JPG, etc.) |
| `~/Documents/old Mac BackUpp/מהגינה של נימרוד/` | 2,706 files (huge, mostly photos/accounting) |
| `~/Documents/israel Microgreens/` | 40 files (mostly hydroponic catalogs) |

**Filter applied:** crop knowledge / growing protocol / variety / planting calendar
content only. Excluded: photos of garden, accounting, BCS machinery, water permits,
Bubbler wash equipment, business operations spreadsheets, marketing material.

---

## 🟢 TIER 1 — HIGH VALUE, READY TO INGEST (structured, Israeli/Hebrew, fills HIGH gaps)

| # | File | Size | What's in it | Fills gap | Recommendation |
|---|------|------|--------------|-----------|----------------|
| L-01 | `מהגינה של נימרוד/תכנוני גידול ונתונים/קבצי נתונים/מועדי זריעה ונתוני בסיס - GROWORGANIC.INFO.XLSX` | 24K | Israeli **sowing dates + base growing data** scraped from groworganic.info (Hebrew site) | HIGH: Israeli planting calendar; germination temp | **INGEST** — exact fill for top gap |
| L-02 | `מהגינה של נימרוד/תכנוני גידול ונתונים/אוסנות מידע לפי זנים.DOCX` | 1.3M | "Information storage by varieties" — large Hebrew variety database | HIGH: Mediterranean-adapted varieties | **INGEST** — variety enrichment for IL conditions |
| L-03 | `Market Gardening/עידן - נתונים דרופבוקס/טבלאות תכנון - גידולי חורף.XLSX` | 40K | **Idan Eliakim's** Israeli **winter** crop planning tables | HIGH: Israeli season planning | **INGEST** — 2nd Israeli farmer data point |
| L-04 | `Market Gardening/עידן - נתונים דרופבוקס/טבלאות תכנון - גידולי קיץ.XLSX` | 32K | Idan's **summer** crop planning tables | HIGH: Israeli season planning | **INGEST** — paired with L-03 |
| L-05 | `Market Gardening/עידן - נתונים דרופבוקס/שתילים וזרעים - קיץ 2018-9.XLSX` + `חורף 2018-9` | 16K each | Idan's **seedlings + seeds order tables** with timing | MEDIUM: seed-weight, varieties for IL | INGEST |
| L-06 | `מהגינה של נימרוד/תכנוני גידול ונתונים/חיפויים ובתים.XLSX` | 24K | "Covers and tunnels" — protected cropping per crop | LOW (new gap): tunnel/row-cover per crop | INVESTIGATE — peek before deciding |
| L-07 | `מהגינה של נימרוד/Tend Data/Tend_2018/*.CSV` | ~1MB | **4 more Tend years** (2018, 2019, 2020, 2021) — same structure as Tend_2022 we already loaded | HIGH: more years = better statistical stability | INGEST (extends WP-B3 OP-tier history) |
| L-08 | Same as L-07 for Tend_2019, Tend_2020, Tend_2021 |  |  |  | INGEST as batch |

---

## 🟡 TIER 2 — HIGH VALUE, SEMI-STRUCTURED (PDFs, Hebrew narrative)

| # | File | Size | What's in it | Fills gap | Recommendation |
|---|------|------|--------------|-----------|----------------|
| L-09 | `israel Microgreens/תוכניות חממה מהגינה/מידע כללי/חוברת הדרכה גידול ירקות בהידרופוניקה.PDF` | 2.1M | **Hebrew hydroponic vegetable growing manual** | MEDIUM: hydro-specific protocols | INVESTIGATE (might be too hydro-specific for soil farming) |
| L-10 | `israel Microgreens/תוכניות חממה מהגינה/מידע כללי/דר מולי זקס תמונת גידולי עלים בהידרופוניקה בארץ.PDF` | 6.6M | **Dr. Moli Zacks survey** — leafy hydroponics state-of-art in Israel | MEDIUM: IL leafy-greens benchmarks | INVESTIGATE |
| L-11 | `israel Microgreens/תוכניות חממה מהגינה/ניסוי זנים חדשים 2021.PDF` | 3.0M | **New variety trials 2021** — Israeli new-cultivar test results | HIGH: Mediterranean variety data | **INGEST** (NI tier) |
| L-12 | `Market Gardening/MasterClass/CAVER CROP CHART.PDF` | small | Cover crop chart (JMF) — 1 page | LOW: cover crops | INVESTIGATE — single-page PDF |
| L-13 | `Market Gardening/MasterClass/COVERCROPS-1547050278830.PDF` | 7pp | JMF cover crops guide | LOW | INVESTIGATE |
| L-14 | `Market Gardening/MasterClass/FT_FINALE_NURSERYSEEDING_ENG.PDF` | 13pp | Nursery seeding protocol (JMF FT) — **NOT yet ingested by WP-B2** | MEDIUM: nursery protocols | INGEST (extends WP-B2 NI tier) |
| L-15 | `Market Gardening/MasterClass/FT_FINALE_PHYTOPROTECTION*.PDF` | 3pp | Biopesticide guide (JMF FT) | LOW (overlaps with `FT_BIOPESTICIDE` already ingested) | SKIP |
| L-16 | `Market Gardening/MasterClass/SEEDINGINCELLFLATS-1515371257772.PDF` | 3pp | Seeding in cell flats (JMF) | MEDIUM: nursery-cell protocol | INVESTIGATE |
| L-17 | `Market Gardening/MasterClass/FT_FINALE_DESIGN_NURSERY_ENG.PDF` | 13pp | Nursery design (JMF FT) | LOW: facility design | SKIP |
| L-18 | `Market Gardening/MasterClass/FT_FINALE_INTROTOBIOINTENSIVEAG_EN.PDF` | small | Intro to bio-intensive (JMF FT) | LOW: methodology | SKIP |
| L-19 | `Market Gardening/MasterClass/FT_FINALE_FILETANTIINSECTES_ENG.PDF` | small | Insect netting (JMF FT) | LOW: equipment | SKIP |
| L-20 | `Market Gardening/MasterClass/FT_FINALE_HIHOSE_ENG.PDF` | small | Hi-hose / micro-irrigation (JMF FT) | LOW: irrigation tooling | SKIP |
| L-21 | `Market Gardening/MasterClass/FT_FINALE_CONTRUCTIONTUNNELCHENILLE_ENG.PDF` | small | Caterpillar tunnel construction (JMF FT) | LOW: structure | SKIP |
| L-22 | `Market Gardening/MasterClass/IRRIGATIONSETUP-1539184577324.PDF` | 3pp | Irrigation setup (JMF) | LOW: facility | SKIP |
| L-23 | `Market Gardening/MasterClass/WASHINGITINERARYCHART_-200819-112151.PDF` | 3pp | Wash-line chart (JMF) | LOW: post-harvest workflow | SKIP |
| L-24 | `Market Gardening/MasterClass/TABLEAUXITINERAIRE_LAVAGE_EN_LETTRE.PDF` | small | Wash itinerary (JMF) | LOW: post-harvest | SKIP |
| L-25 | `Market Gardening/MasterClass/FICHESALLEDECONDITIONNEMENT_EN.PDF` | small | Packhouse fact sheet (JMF) | LOW: facility | SKIP |
| L-26 | `Market Gardening/MasterClass/בין התלמים.PDF` | ? | Hebrew JMF-style content ("Between the Furrows") | INVESTIGATE — could be HIGH (Hebrew version of JMF book?) | INVESTIGATE FIRST |

---

## 🟠 TIER 3 — SECONDARY VALUE (microgreens, additional planning material)

| # | File | What's in it | Fills gap | Recommendation |
|---|------|--------------|-----------|----------------|
| L-27 | `Market Gardening/microgreens/MICRO-GREENS-YIELD-TRIAL-RESULTS-TECH-SHEET.PDF` | Microgreens yield trial results | NEW gap: microgreens (not in current scope) | SKIP unless microgreens is a future scope |
| L-28 | `Market Gardening/microgreens/MICROGREENS-VARIETY-LISTING-WEB.PDF` | Microgreens variety listing | Same as L-27 | SKIP unless expanding scope |
| L-29 | `Market Gardening/microgreens/ON THE GROW - MICROGREENS SEEDING GUIDE.PDF` (x2) | Microgreens seeding guide | Same | SKIP |
| L-30 | `Market Gardening/MasterClass/Crop Planning/CROPPLANNING2-1552412806328.PDF` | JMF crop planning v2 | LOW: meta-planning | SKIP (already have main JMF) |
| L-31 | `Market Gardening/MasterClass/Crop Planning/CROP PLANNING TEMPLATE.XLSX` | JMF empty crop planning template | LOW: template | SKIP |
| L-32 | `Market Gardening/MasterClass/Crop Planning/5 STEPS TO YOUR PLANNING.PDF` (x2) | JMF 5-step planning guide | LOW: methodology | SKIP |
| L-33 | `Market Gardening/MICRO-GREENS-YIELD-TRIAL-RESULTS-TECH-SHEET.PDF` (root copy) | Duplicate of L-27 | SKIP | SKIP |
| L-34 | `Market Gardening/THE MARKET GARDENER_ A SUCCESSF.PDF` (root copy, 209pp) | JMF book alternate edition | Already ingested (240pp version) | SKIP |
| L-35 | `Market Gardening/SMALL_CAN_BE_BEAUTIFULL_MICROFARMERS_MOREL_ET_AL_2017.PDF` | Academic paper on microfarming | LOW: theory | SKIP |
| L-36 | `Market Gardening/לוח-השנה-של-גינת-בוסתן-זריעה-ושתילה-של-ירקות.PDF` | **Israeli Bustan calendar — sowing & planting of vegetables** | HIGH: Israeli planting calendar! | **INGEST** — moved here because PDF (semi-structured) |
| L-37 | `Market Gardening/הרצאה - חקלאות קונבנציונאלית-אורגנית ואקולוגית.PAGES` | Hebrew lecture: conventional/organic/ecological | LOW: methodology lecture | SKIP |
| L-38 | `Market Gardening/microgreens/LIBRETTO-ORTO-WEB.PDF` (in זרעים ושתילים) | Italian vegetable garden manual | INVESTIGATE — Italian Mediterranean climate | INVESTIGATE |
| L-39 | `Market Gardening/microgreens/MESCLUN-1515369614506.PDF` (in זרעים ושתילים) | JSS mesclun guide | LOW: salad-mix specific | SKIP |
| L-40 | `Market Gardening/The Urban Farmer/urban farmer crop data/CURTIS CROP PROFILES SHEET.XLSX` | **Curtis Stone (Urban Farmer) crop profiles** | MEDIUM: 3rd source for blending | INGEST |
| L-41 | `Market Gardening/The Urban Farmer/urban farmer crop data/IMAGE (×34).JPG` | 34 scanned crop charts from Curtis Stone's book | MEDIUM: Curtis Stone reference tables (OCR needed) | INVESTIGATE |
| L-42 | `Market Gardening/The Urban Farmer/TUF Free Extras/NEW PLANTINGS SHEET 071917.XLSX` | TUF planting sheet template | LOW: template | SKIP |
| L-43 | `israel Microgreens/חומרים מהלקוח/leafey greens and lettace.xlsx` | Customer's leafy greens + lettuce data | MEDIUM: targeted leafy data | INVESTIGATE |
| L-44 | `israel Microgreens/חומרים מהלקוח/ישראל אורגניק גרינס.pdf` | Israeli organic greens supplier sheet | LOW: supplier catalog | INVESTIGATE |
| L-45 | `מהגינה של נימרוד/תכנוני גידול ונתונים/קבצי נתונים/רוכוז נתונים 2017 NEW.XLSX` | "2017 data summary NEW" (Nimrod's own 2017 farm data) | MEDIUM: pre-Tend Nimrod data | INVESTIGATE |
| L-46 | `מהגינה של נימרוד/תכנוני גידול ונתונים/קבצי נתונים/מפת חלקה - 2017.XLSX` | 2017 plot map | LOW: spatial layout | SKIP |
| L-47 | `מהגינה של נימרוד/תכנוני גידול ונתונים/קבצי נתונים/TEND EXPORT.XLSX` | Tend export snapshot | DUPLICATE: covered by Tend_2018-22 CSVs | SKIP |
| L-48 | `מהגינה של נימרוד/תכנוני גידול ונתונים/טכנולוגיה בגננות שוק/JM.XLSX` | JM (JMF?) market gardening tech notes | INVESTIGATE — possibly JMF translation | INVESTIGATE |
| L-49 | `מהגינה של נימרוד/תכנוני גידול ונתונים/טכנולוגיה בגננות שוק/עידן.XLSX` | Idan's market gardening tech notes | MEDIUM: Israeli grower notes | INVESTIGATE |

---

## ❌ TIER 4 — EXPLICITLY SKIP (out of scope per team_00 directives)

| Category | Count | Why skip |
|----------|-------|----------|
| Tend non-crop CSVs (EXPENSES, LOCATIONS, ORDERS_*, PACK, PICK, PRODUCT_SOLD) across 5 years | ~30 | Operational/financial, not crop knowledge (team_00 directive: skip) |
| BCS machinery (orders, manuals, contracts) | ~30 | Equipment, not crop data |
| Bubbler wash equipment | 6 | Equipment, not crop |
| TUF business templates (BUDGET, MOU, LEASE, SPOILAGE, SALES) | 8 | Business operations, not crop |
| Water/irrigation forms (טופס מים, WHATSAPP IMAGE water) | ~20 | Infrastructure permits |
| Garden photos (1,368 files in תמונות וסרטים) | 1,368 | Visual record, not crop data |
| Accounting & receipts (הנהלת חשבונות) | 291 | Financial |
| Graphics/branding (גראפיקה ותדמית) | 443 | Marketing assets |

---

## 🔍 NEED A QUICK PEEK BEFORE DECIDING (5 files worth opening)

These 5 are the highest-leverage "INVESTIGATE FIRST" items. If you want, I can
open each one and report its actual content in 1 paragraph:

1. **L-01** — `מועדי זריעה ונתוני בסיס - GROWORGANIC.INFO.XLSX` (probably the single best Israeli source)
2. **L-02** — `אוסנות מידע לפי זנים.DOCX` (1.3MB Hebrew variety database)
3. **L-26** — `בין התלמים.PDF` (could be Hebrew JMF book translation = huge)
4. **L-36** — `לוח-השנה-של-גינת-בוסתן-זריעה-ושתילה.PDF` (Israeli sowing calendar)
5. **L-40 + L-41** — Curtis Stone profiles XLSX + 34 scanned images

---

## Summary recommendation

| Tier | INGEST | INVESTIGATE | SKIP |
|------|--------|-------------|------|
| Tier 1 (HIGH structured) | **8** | 1 (L-06) | 0 |
| Tier 2 (HIGH PDF) | 2 (L-11, L-14) | 4 | 11 |
| Tier 3 (secondary) | 2 (L-36, L-40) | 7 | 8 |
| Tier 4 (out-of-scope) | 0 | 0 | ~1,800 |

**Suggested first batch** (lowest effort, highest gap-filling):
- L-01 (GROWORGANIC), L-03+L-04+L-05 (Idan Eliakim tables), L-07+L-08 (Tend 2018-2021 backfill), L-11 (variety trials 2021), L-14 (JMF nursery seeding)

This naturally becomes **WP-C1 (Israeli scout-loaded data)** + **WP-C2 (Tend multi-year backfill)** + **WP-C3 (JMF extension)**, separately from the web scout's WP-C.

---

*Generated by team_10 / Claude Code 2026-05-26 from local filesystem scan.*
