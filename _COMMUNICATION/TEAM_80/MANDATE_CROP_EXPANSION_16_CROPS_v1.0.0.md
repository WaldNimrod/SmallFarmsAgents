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

# Mandate — Web Data Scouting: 16 New Crops (v1.0.0 CORRECTED)

## Correction Note (2026-05-27)

The original mandate listed עגבניית שרי as zero-data. **Incorrect.** Investigation showed:
- עגבניית שרי has Idan 2017 data (spacing, rows, yield) already in DB
- JMF and Tend CSVs both contain cherry tomato data; routing was partially blocked (tech fix pending)
- Cherry tomato is therefore NOT a candidate for full web research by Team 80 for core fields

Crops with partial Idan 2017 data (spacing/rows/yield) that still need DTM + other fields:
עגבניית שרי, אבטיח, כרובית, במיה, תירס, תפוח אדמה, אדממה.

---

## Current Data Coverage (post-ingestion state)

Legend: ✅ = ≥2 sources · ⚠ = 1 source (Idan only) · ❌ = completely missing

| Crop | DTM | Spacing | Rows/bed | Planting | Yield/m² | Avg yield/bed-m | Seeds/g | Germ°C | Frost | H.Window | Succession | Soil pH |
|------|-----|---------|----------|----------|----------|----------------|---------|--------|-------|----------|------------|---------|
| אוסנה (Blackberry) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| עגבניית שרי (Cherry Tomato) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| אבטיח (Watermelon) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| כרובית (Cauliflower) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| בטטה (Sweet Potato) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| במיה (Okra) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| פול (Fava Bean) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ציקוריה (Chicory) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| תירס (Sweet Corn) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| תפוח אדמה (Potato) | ❌ | ⚠ | ⚠ | ❌ | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| חומוס (Chickpea) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| שומשום (Sesame) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| חמניה (Sunflower) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| חיטה (Wheat) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| סויה (Soybean) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| אדממה (Edamame) | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Inline Prompt for Team 80 (copy below this line)

Copy everything inside the code block below and paste it as your first message into a new Claude.ai conversation.

---

```
You are a senior agronomist assistant performing structured web research for a small farm
planning system serving market farmers in Israel. Your task is to find and compile agronomic
data for 16 crops that are currently missing critical values in our database. The system
helps farmers plan bed-based growing schedules, so all measurements should target
**bed-based small farm scale** (75–90 cm wide beds).

---

## TASK

For each crop listed below, search the web and compile the best available data for every
field marked ❌ (completely missing) or ⚠ (single source — needs confirmation).
We need **at least 2 independent credible sources** per field.

Acceptable sources:
- University extension services (UC Davis, Cornell, Purdue, UF/IFAS, Wageningen, etc.)
- National agricultural research centers (USDA, INRAE, Volcani Institute / ARO Israel)
- Israeli/Mediterranean agricultural research (Shaham, MIGAL, Leket, Tahal)
- Authoritative seed company technical sheets (Johnny's Selected Seeds, High Mowing,
  Burpee Professional, Bejo, Hazera)
- Recognized crop handbooks (Knott's Handbook for Vegetable Growers, FAO crop guides)

Do NOT use: Wikipedia, general gardening blogs, wikihow, answers.com, any source without
a named author/institution, or AI-generated summaries without cited primary sources.

---

## CRITICAL NOTES — READ BEFORE STARTING

### Note 1 — עגבניית שרי (Cherry Tomato) is DISTINCT from regular tomato
Cherry tomato (Solanum lycopersicum var. cerasiforme) is a separate crop with different
spacing, yield, and growing characteristics from field/beefsteak tomatoes. Do NOT use
regular tomato sources for this crop. Look specifically for indeterminate cherry tomato
varieties (e.g., Sungold, Sweet 100, Black Cherry). Typical cherry tomato values:
DTM ~60–75 days from transplant; in-row spacing 45–60 cm; yield 3–8 kg/m² field,
higher in tunnel. We already have some Idan farm data (spacing ⚠, rows ⚠, avg yield ⚠)
— we need DTM + all other fields, and a confirming source for the Idan values.

### Note 2 — אדממה (Edamame) = סויה טרייה (fresh soybean, same plant)
Edamame and dry soybean (סויה) are the SAME plant (Glycine max), harvested at different
stages. Edamame = harvested fresh at R6 stage (pods fully filled, beans still green and
tender). The relevant DTM is ~70–95 days to fresh-pod harvest — NOT the dry-seed DTM
(~100–120+ days to hard dry bean). Spacing and yield also differ; edamame is often
planted more densely. Use sources that specifically address edamame / fresh green soybean.
We have 1 spacing value for edamame — need DTM + all other fields + spacing confirmation.

### Note 3 — Israeli/Mediterranean context
These crops are grown in Israel's climate zones (Mediterranean coast, Jordan Valley,
Northern valleys). Where Israeli-specific data is available, prefer it and flag it.
For DTM and planting windows, note whether the source is temperate vs. Mediterranean.

### Note 4 — Bed measurements
"Rows per bed" assumes 75–90 cm bed width. Yield per bed metre = yield/m² × 0.80 m.

---

## THE 16 CROPS — DATA COVERAGE STATUS

Legend: ❌ = completely missing · ⚠ = 1 source exists (Idan 2017 farm data), need
confirmation + DTM · ✅ = already have ≥2 sources (skip)

| # | Crop | Tier | DTM | Spacing | Rows/bed | Planting | Yield/m² | Seeds/g | Germ°C | Frost | H.Window | Succession | Soil pH |
|---|------|------|-----|---------|----------|----------|----------|---------|--------|-------|----------|------------|---------|
| 1 | עגבניית שרי (Cherry Tomato) | 1 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2 | כרובית (Cauliflower) | 1 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 3 | בטטה (Sweet Potato) | 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 4 | במיה (Okra) | 1 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 5 | פול (Fava Bean) | 1 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 6 | אבטיח (Watermelon) | 2 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 7 | תירס (Sweet Corn) | 2 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 8 | תפוח אדמה (Potato) | 2 | ❌ | ⚠ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 9 | אדממה (Edamame) | 2 | ❌ | ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 10 | ציקוריה (Chicory) | 2 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 11 | חומוס (Chickpea) | 2 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 12 | שומשום (Sesame) | 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 13 | חמניה (Sunflower) | 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 14 | חיטה (Wheat) | 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 15 | סויה (Soybean) | 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 16 | אוסנה (Blackberry) | 3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## FIELD DEFINITIONS

| Field | Definition | Units / Format |
|-------|-----------|---------------|
| **DTM** | Days to maturity — from transplant (T) or direct seed (D) to first harvest | Integer days; state T or D. If both methods exist, give both (e.g., "65T / 80D") |
| **Spacing** | In-row spacing between plants (not row-to-row distance) | cm |
| **Rows/bed** | Number of planting rows on a standard 75–90 cm wide bed | Integer (1, 2, 3, or 4) |
| **Planting method** | How the crop is established | transplant / direct seed / slip (sweet potato) / tuber (potato) |
| **Yield/m²** | Expected fresh weight yield under good management | kg/m² |
| **Seeds/g** | Approximate number of seeds per gram | Integer or range; write "N/A (vegetative)" for sweet potato, potato |
| **Germ°C** | Optimal soil temperature range for germination | °C range (e.g., "18–24") |
| **Frost** | Frost tolerance classification | hardy (survives hard frost) / half-hardy (survives light frost) / tender (no frost) |
| **H.Window** | Harvest window — days between first possible harvest and last before quality loss | Days; write "0" for single-harvest crops (grain, tubers) |
| **Succession** | Recommended interval between successive plantings for continuous supply | Weeks; write "N/A" if succession not applicable (perennials, single-season crops) |
| **Soil pH** | Target soil pH range | Numeric range (e.g., "6.0–7.0") |

---

## OUTPUT FORMAT — FOLLOW EXACTLY

For each crop, produce one section using this template:

---

### [N]. [Hebrew name] ([English name])

**Planting method:** [value]
*(Source 1: [Author/Organization, Year — Title or URL])*

**DTM:** [value] days from [transplant/direct seed]
*(Source 1: [...])*
*(Source 2: [...])*

**In-row spacing:** [value] cm
*(Source 1: [...])*
*(Source 2: [...])*
[Note if ⚠: "Idan 2017 farm record shows [X] cm — Source 2 [confirms / differs at Y cm]"]*

**Rows per 75–90 cm bed:** [value] rows
*(Source 1: [...])*
*(Source 2: [...])*

**Yield per m²:** [value] kg/m²
*(Source 1: [...])*
*(Source 2: [...])*

**Seeds per gram:** [value] seeds/g — OR — N/A (vegetative propagation)
*(Source 1: [...])*
*(Source 2: [...])*

**Germination temperature:** [value] °C
*(Source 1: [...])*
*(Source 2: [...])*

**Frost tolerance:** [hardy / half-hardy / tender]
*(Source 1: [...])*
*(Source 2: [...])*

**Harvest window:** [value] days
*(Source 1: [...])*
*(Source 2: [...])*

**Succession interval:** [value] weeks — OR — N/A
*(Source 1: [...])*

**Soil pH target:** [value]
*(Source 1: [...])*
*(Source 2: [...])*

**Israeli/Mediterranean notes:** [Any Israel or Mediterranean-climate specific data found —
e.g., Volcani Institute recommendations, planting calendar for Israel, local yield data.
Write "None found" if not applicable.]*

---

## QUALITY RULES

1. **Source every single value** — no number without a citation.
2. **Minimum 2 sources per field** — if you only found 1, write:
   `⚠ SINGLE SOURCE — [source]. Could not confirm independently.`
3. **If data not found after genuine search, write:**
   `❌ NOT FOUND — searched [sources tried] with no result.`
4. **Do not hallucinate sources** — only cite sources you actually accessed in this session.
5. **Cherry tomato ≠ regular tomato** — reject any source that is clearly about
   beefsteak/processing/slicing tomatoes when researching עגבניית שרי.
6. **Edamame ≠ dry soybean** — reject dry-bean DTM values for אדממה.
7. **Blackberry (אוסנה):** Note that commercial maturity is years from planting (perennial).
   DTM here means "days from new-season budbreak to ripe fruit" (~60–80 days depending
   on variety). Give both the years-to-establishment and the annual fruiting window.
8. **Wheat (חיטה):** Specify variety type (winter/spring soft/hard) and whether DTM is
   to soft dough, hard harvest, or grain dry-down.
9. **For ⚠ fields** (Idan 2017 value exists): confirm or note divergence — if confirming
   source differs by >20% from the Idan value, flag it explicitly.

---

## DELIVERABLE

A single structured document with all 16 crops researched, all fields filled, all sources
cited. Work Tier 1 first (crops 1–5), then Tier 2 (crops 6–11), then Tier 3 (crops 12–16).
If you reach context limits, stop at a clean crop boundary and state which crops remain.

Expected output length: approximately 5,000–9,000 words.
```

---

*Issued by team_10 (sfa_build) · 2026-05-27*
