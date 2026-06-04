# Tend → SFA Field-Exact Schema Mapping (WP003 final deliverable)

**WP:** SFA-S004-P001-WP003 · **Date:** 2026-06-05 · **Author:** Team 100
**Basis:** Real in-repo Tend exports from the principal's own farm (`data/external_sources/sample_extracts/tend_multi_year__Tend_{2018-2021}_*.txt`) cross-referenced against the live importer (`organic_market_agent/crop_book/importer/tend.py`, `tend_overlay.py`), migration `046_tend_overlay.py`, `constants.py` maps, `canon/topics.py`, `calculator_meta.py`, `models.py`. NOT public-docs inference.

## Headline: schema is rock-stable (2018→2021)
All 6 export types have **byte-identical column headers across all 4 years** — zero column drift. A single fixed schema is safe to build against. Counts: CROP_PLAN **64 cols**, GREENHOUSE_PLAN 35, TASKS 30, HARVESTS 9, SEED_LIST 12, NOTES 5. Row volumes scale (CROP_PLAN 60→552; HARVESTS 0→3,720; TASKS 97→1,101) but columns never change.

SFA target: 13-topic taxonomy (`varieties, spacing, equipment, soil, bedprep, sowing, irrigation, care, pest, harvest, storage, succession, yield_inc`) · 14 calculators (IDs 1–14) · farmOS entities Plant/Land/Seed **Asset**, seeding/transplanting/harvest/input/activity/observation **Log**, **Quantity**, **Term**.

## CROP_PLAN — the 64-column core (key fields)
Crop identity: Category, Family Name, Crop (EN), Crop Type, Variety (often Hebrew). Method/stage: Planting Method, Harvest Stage. Nursery: GH Sow Date, Days/dates to 1st/2nd/3rd potting-up, Days In Greenhouse, #Of Flats, Flat/pot type, Seeds per cell, [3× potting-up flat/cell/count]. Calendar: Field Sowing Planting Date (the field anchor), DTM, Harvest Window, First/Last Harvest. Spatial: Planting Amount (`bed m`), Location (`farm,subfarm,block,beds`), In-Row Spacing (+Unit cm/inch), Rows Per Bed, **Between row spacing** (col 57). Seed: Estimated loss, Total Transplants, Total Seed Needed, Average seed weight (+unit seeds/g), Total Weight Needed (+g), Extra Seed %, **Seed spec=Organic**. Economics: Harvest Unit, **Avg Yield Rate** (`bn|kg/row m`), **Avg. Sales Price** (`₪x/unit`), Est. Yield, Est. Revenue, Est. Rev./unit. Lifecycle: Growing Cycle (Annual/Perennial/Biennial), Rootstock, Harvest Season, First Fruiting Year. Notes. Equipment: **Seeder (Jang JP-1), Front gear, Rear gear, Roller plate**.

### CROP_PLAN mapping (topic · calculator I/O · farmOS entity · importer-covered)
- Identity (Category/Family/Crop/Variety/CropType) → `varieties` → Plant/variety Terms → **importer YES** (name_en/he, family, category, variety).
- Planting Method → `sowing` → calc #4,#5 I → seeding-vs-transplanting Log → YES.
- DTM / Harvest Window / Harvest Stage / Harvest Unit → `harvest` → #4,#5,#11 / #7,#8 → Plant attr + harvest Log/Quantity → YES.
- In-Row Spacing / Rows Per Bed → `spacing` → #1,#2,#10 → Plant attr → YES (inch→cm convert).
- **Between row spacing (col 57)** → `spacing` → #10 → **NO (gap; calc #10 currently uses `bed_width` assumption)**.
- Avg Yield Rate → `yield_inc` → #7,#8,#9,#13 → Plant attr `yield_per_bed_m` → YES.
- Avg. Sales Price → `yield_inc` → #9,#13 → price attr → YES **numeric only — UNIT dropped (gap)**.
- Est. Yield/Revenue/Rev-per-unit → derived (calc outputs), not stored.
- Growing Cycle / Rootstock / First Fruiting Year → `varieties` → Plant attrs → YES.
- Days In Greenhouse / potting-up → `sowing` → #3,#4 → nursery → partial (overlay GH parser).
- Seeder/gears/roller → `equipment` → Equipment asset/Plant attr → YES (all 4).
- Field Sowing Date / First-Last Harvest / Planting Amount (bed m) / Location / flats / transplant & seed counts → dated/per-planting realization → seeding/transplanting/harvest Logs + Land asset → **NO (scoped as enrichment stats today, not facts)**.
- Seed spec=Organic → cert Term on Seed asset → **NO (cert gap)**.

**Coverage:** importer persists ~22 of 64 cols — the crop-knowledge/planning/yield/price facts. Not yet sourced: per-planting realization (dates, amounts, counts), organic cert, between-row spacing, price unit.

## Other exports
- **GREENHOUSE_PLAN (35):** nursery lifecycle; importer extracts only `Days In Greenhouse`→`days_in_gh_total` + first-potting (OP enrichment, weight 0.55); 33 cols ignored.
- **TASKS (30) — Execute pillar:** Due/Completed Date, Task Type (Direct Sow/Transplant/Greenhouse Sow/Weed/Pest&Disease/Fertilize&Amend/Trellis/Irrigate…), Assignees, Plantings/Location Assigned, Method/Sub-method, **Input, Manufacturer, OMRI (organic), Application Rate Amount/Unit/Area**, Name Of Pest Identified, Number Of Minutes, **Lines Of Drip, 360/180 Pipe #Lines/Minutes/Heads, Total Inches, Total Gallons**, Completed, **Total Labor Hours**. Importer reads only Task Type/Method/Sub-method/Input/Description/Plantings → `crop_task_templates` (11-whitelist/10-blacklist/20 enum). **All irrigation/drip/OMRI/labor/rate columns DISCARDED.**
- **HARVESTS (9) — production→sales:** Date, Planting Name (rich), Crop, Amount, Unit, **Outlet Type (`Farmers Market`), Outlet Name (`הדוכן יום ב`)**, Harvest Stage, Final Harvest. Importer aggregates to (crop,season,year) `crop_harvest_stats` only. **Outlet Type/Name DISCARDED (production→sales loop OPEN — matches CI finding #3).**
- **SEED_LIST (12):** procurement (Total Seeds/Weight Needed, per-planting, Extra Seed Order %, `Planting Seed Spec=Organic`). **No parser — feeds calc #14 + inventory.**
- **NOTES (5):** Date/Creator/Note(Hebrew)/Plantings/Location. **No parser → observation Log target.**

## Gaps — SFA fields with NO Tend source
calc #12 fertilizer (`nutrient_removal_n/p/k/ca/mg`), pest profiles (structured), storage params, `succession_interval_weeks` (calc #6 — derive from repeated sow dates), `frost_tolerance_class` (calc #11 — authored), `price_documented_unit` (embedded in Avg Sales Price but parser drops it).

## Phase-0 TODO (importer → full farmOS-headless target)
1. SEED_LIST parser → Seed assets + procurement Quantities (calc #14) + organic cert.
2. NOTES parser → observation Logs (preserve Hebrew).
3. **Per-planting realization** → real-timestamp seeding/transplanting/harvest Logs + Plant/Land asset refs (today: crop-generic templates + season aggregates only).
4. **Irrigation/water telemetry** (TASKS drip block → Total Gallons) → irrigation input Log Quantities.
5. **Labor telemetry** (Total Labor Hours/Minutes) → activity Log labor Quantity → profit-calc realism.
6. **Organic-cert capture** (3 sources: CROP_PLAN Seed spec, TASKS OMRI, SEED_LIST Planting Seed Spec) → cert Term.
7. **Sales-channel link** (HARVESTS Outlet Type/Name) → sale Log + channel Term — **closes the production→sales wedge.**
8. **Avg Sales Price unit parser** (`/bn`,`/kg`,`/cs`) → `price_documented_unit` (calc #9/#13). One-line fix.
9. **Between row spacing** (col 57) → calc #10 real value (vs `bed_width` assumption).
10. **Location hierarchy parser** (`Ramim,Ra.1,Block L1,Beds 109`) → Land asset tree.
11. **Pest profile** (Name Of Pest + Manufacturer + Application Rate) → structured pest topic + material Terms.
12. **Application Rate** → input Log rate Quantity.
13. **Crop-map audit** — TEND_CROP_MAP gates everything; audit vs full 552-row 2021 CROP_PLAN (unmapped crops silently skipped).

**Bottom line for Phase 0:** Tend's schema is stable and trustworthy enough to hard-code. The importer extracts crop-knowledge facts well but discards nearly all Execute-pillar event data (dated Logs, irrigation/water, labor, organic-cert, sales-channel) — exactly what the farmOS-headless target + the production→sales wedge need. Those discards = the bulk of the Phase-0 build list (items 1–13).
