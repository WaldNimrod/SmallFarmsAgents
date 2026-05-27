---
document_type: MANDATE
version: "1.0.0"
mandate_id: SFA-MANDATE-CROP-16-v1.0.0
from: team_10 (sfa_build, on behalf of team_00 Principal)
to: team_80 (Product & Research)
date: 2026-05-27
priority: HIGH
status: ACTIVE
sla_days: 5
cost_cap_usd: 10
expects_response: true
response_artifact: CROP_DATA_FINDINGS_16_CROPS_v1.0.0.md
---

# Mandate — Web Data Scouting: 16 New Crops

## Background

The SFA crop book (`crops` table) has just been expanded with 16 new crops.  
All 16 have **zero structured data** — no source_values, no knowledge_notes.

Before these crops can appear on the live product page, we need **at least 2
independent sources** per core data point, so the reconciler can produce a
reliable consensus value.

This mandate authorises team_80 to run a focused web research sprint.

---

## Crops List

| id | Hebrew | English | Family | Category |
|----|--------|---------|--------|----------|
| 61 | אוסנה | Blackberry | ורדיים (Rosaceae) | fruits |
| 73 | עגבניית שרי | Cherry Tomato | סולניים (Solanaceae) | fruits |
| 74 | אבטיח | Watermelon | דלועיים (Cucurbitaceae) | fruits |
| 75 | כרובית | Cauliflower | מצליבים (Brassicaceae) | vegetables |
| 76 | בטטה | Sweet Potato | לשוניתניים (Convolvulaceae) | vegetables |
| 77 | במיה | Okra | חלמיתיים (Malvaceae) | vegetables |
| 78 | פול | Fava Bean | קטניות (Fabaceae) | vegetables |
| 79 | ציקוריה | Chicory / Endive | מורכבים (Asteraceae) | vegetables |
| 80 | תירס | Sweet Corn | דשאיים (Poaceae) | vegetables |
| 81 | תפוח אדמה | Potato | סולניים (Solanaceae) | vegetables |
| 82 | חומוס | Chickpea | קטניות (Fabaceae) | vegetables |
| 83 | שומשום | Sesame | שומשומיים (Pedaliaceae) | herbs |
| 84 | חמניה | Sunflower | מורכבים (Asteraceae) | vegetables |
| 85 | חיטה | Wheat | דשאיים (Poaceae) | vegetables |
| 86 | סויה | Soybean | קטניות (Fabaceae) | vegetables |
| 87 | אדממה | Edamame | קטניות (Fabaceae) | vegetables |

---

## Data Points Required — Priority A (Critical)

These 6 fields are required before a crop can appear in the production planner.
We need **≥ 2 independent sources** for each crop × field combination.

| Field | Description | Typical unit | Example value |
|-------|-------------|-------------|---------------|
| `days_to_maturity` | Days from transplant (or direct seed) to first harvest | days | 60–90 |
| `in_row_spacing_cm` | Distance between plants within the row | cm | 30–45 |
| `rows_per_bed` | Number of rows on a 75–90 cm bed | integer | 2–4 |
| `planting_method` | `transplant` or `direct` | enum | `direct` |
| `yield_per_m2_kg` | Marketable yield per square metre | kg/m² | 2.5 |
| `avg_yield_per_bed_m` | Marketable yield per linear bed metre | kg/bed-m | 0.8 |

---

## Data Points Required — Priority B (Important)

These are needed for scheduling, seed ordering, and soil management.  
Minimum **1 source** per crop; **≥ 2** preferred.

| Field | Description | Unit |
|-------|-------------|------|
| `seeds_per_gram` | Seed count per gram | count/g |
| `germination_temp_c_opt` | Optimal germination temperature | °C |
| `frost_tolerance_class` | `hardy` / `half_hardy` / `tender` | enum |
| `harvest_window_max_days` | Days between first and last harvestable day | days |
| `succession_interval_weeks` | Weeks between successive plantings | weeks |
| `soil_ph_target` | Ideal soil pH for production | pH |

---

## Data Points Required — Priority C (Narrative / NI)

For each crop, please find at least 1 authoritative source (extension service,
university, Israeli MOA/SHAHAM) covering the following narrative points:

| note_type | Description |
|-----------|-------------|
| `growing_tip` | General production tips for small-scale/market-garden context |
| `israeli_regions` | Which Israeli regions are suitable (climate zones, elevation) |
| `frost_tolerance` | Narrative description of frost tolerance (in Hebrew preferred) |
| `nursery_specific` | Seedling / transplant specific notes (if transplanted) |

---

## Scope & Prioritisation

Not all crops are equally urgent. Please work in this order:

**Tier 1 — Highest commercial priority (cover all Priority A + B fields):**
- עגבניית שרי (Cherry Tomato) — highest-value market garden crop
- כרובית (Cauliflower) — common Israeli winter crop
- בטטה (Sweet Potato) — growing market demand
- במיה (Okra) — strong Israeli local demand
- פול (Fava Bean) — winter staple

**Tier 2 — Cover Priority A fields, Priority B best-effort:**
- אבטיח (Watermelon)
- ציקוריה (Chicory/Endive)
- תירס (Sweet Corn)
- תפוח אדמה (Potato)
- אדממה (Edamame)

**Tier 3 — Priority A only; note that some are niche / field crops:**
- אוסנה (Blackberry) — perennial fruit, different lifecycle
- חומוס (Chickpea) — field scale, not market garden
- שומשום (Sesame) — specialty; Israeli production context important
- חמניה (Sunflower) — edible-seed context (not ornamental)
- חיטה (Wheat) — wheatgrass / cover crop / grain context
- סויה (Soybean) — field scale

---

## Source Guidance

### Preferred sources (highest credibility)

| Source type | Examples |
|-------------|---------|
| Israeli MOA / SHAHAM extension guides | shaham.moag.gov.il, moag.gov.il |
| Hebrew agricultural periodicals | גלרוב, ירקנות, עלון הנוטע |
| Cornell Cooperative Extension / UC ANR / UGA Extension | cce.cornell.edu, ucanr.edu |
| ATTRA National Sustainable Agriculture | attra.ncat.org |
| Johnny's Selected Seeds crop library | johnnyseeds.com/growers-library |
| Rodale Institute | rodaleinstitute.org |
| Haifa Chemicals crop nutrition library | haifa-group.com/crops |

### Minimum quality bar
- Source must be publicly accessible (no paywall)
- Source must be traceable (full URL + retrieval date)
- Data must be specific to the crop (not a general vegetable guide)
- Prefer **small/market-farm scale** data over industrial-scale field data

### Language
- Hebrew sources preferred for `israeli_regions`, `frost_tolerance` (narrative)
- English acceptable for all structured fields (Priority A + B)

---

## Deliverable Format

Create file:
`_COMMUNICATION/TEAM_80/CROP_DATA_FINDINGS_16_CROPS_v1.0.0.md`

**One section per crop**, in Tier order:

```markdown
## עגבניית שרי — Cherry Tomato (id=73)

### Priority A fields

| field | value | unit | source_name | source_url | notes |
|-------|-------|------|------------|-----------|-------|
| days_to_maturity | 65 | days | Johnny's Seeds | https://... | from transplant |
| days_to_maturity | 70 | days | Cornell CCE | https://... | field average |
| in_row_spacing_cm | 30 | cm | Johnny's Seeds | https://... | |
| rows_per_bed | 2 | — | UC ANR | https://... | 90cm bed |
| planting_method | transplant | — | Cornell | https://... | |
| yield_per_m2_kg | 3.5 | kg/m² | UC ANR | https://... | |

### Priority B fields

| field | value | unit | source_name | source_url |
|-------|-------|------|------------|-----------|
| seeds_per_gram | 280 | count/g | Johnny's | https://... |
...

### Priority C — Narrative notes

**growing_tip:** [1–3 sentences; source: ...]
**israeli_regions:** [which regions suit this crop; source: ...]
**frost_tolerance:** [narrative, preferably Hebrew; source: ...]
```

---

## Budget & SLA

- **Budget cap:** $10.00 total (web searches, no paid databases)
- **SLA:** 5 working days from mandate receipt
- **Minimum deliverable:** Tier 1 crops (5 crops) fully covered, Priority A fields
- **Target deliverable:** All 16 crops, Priority A + B fields

---

## Notes

1. **עגבניית שרי vs עגבנייה:** Cherry Tomato is a **distinct crop** (id=73) from
   regular Tomatoes (id=49). Do not mix sources. Cherry tomato spacing/yield
   differs significantly from beefsteak/slicing varieties.

2. **אדממה vs סויה:** Edamame (id=87) is immature soybean harvested at the green
   stage (R6). Yield and maturity data differ from dry soybean (id=86). Use
   edamame-specific sources for id=87.

3. **Israeli context:** For `israeli_regions` and `frost_tolerance`, Israeli
   agroclimatic zones apply (Galilee highlands, coastal plain, Negev, Jordan
   Valley). Where found, note which zone the data pertains to.

4. **Perennials:** אוסנה (Blackberry) is a perennial. `days_to_maturity` refers
   to days from bud burst to ripe berry in the productive season (year 2+),
   not from planting.

---

*Issued by team_10 (sfa_build) on behalf of team_00 · 2026-05-27*
*SmallFarmsAgents · SFA-S003-P002 crop book expansion*
