---
id: MISSION_SFA-CROP-DATA-SCOUT_2026-05-26_v1.0.0
from: team_10 (sfa_build, on behalf of team_00 Principal direction)
to: team_80
date: 2026-05-26
type: RESEARCH_MISSION
project: smallfarmsagents
related_program: SFA-S003-P002 (ספר גידולים crop book)
expects_response: true
status: PENDING_TEAM_00_APPROVAL
priority: NORMAL
sla_days: 2
cost_cap_usd: 5
classification: scout (advisory only — not a WP)
---

# MISSION — SFA Crop Data Scout

**Objective:** Web-scout free / open data sources (databases, tables, charts,
APIs) that would meaningfully complement the existing SFA crop book.

**Deliverable:** Shortlist of 5-12 candidates, each with a fixed-format parameter
row + full link, so team_00 can decide for EACH candidate whether to ingest
(future WP-C) or skip.

---

## 1. Context — what already exists in the DB (do NOT duplicate)

Per the SFA-S003-P002 program (LOD500_LOCKED, tag `S003-P002-WP-B-v1.0.0`):

| Tier | Source | Coverage | What we already have |
|------|--------|----------|----------------------|
| EX | team_00 manual overrides | 5 rows (ארוגולה DTM) | Hard truth, very narrow |
| PR | JMF MasterClass (Excel + PDF) | ~50 crops | DTM, harvest window, yield, price, growing tasks templates, cultivar notes, pest/disease narratives (from JMF book), flame-weed + biopesticide schedules |
| OP | Tend 2022 (Israeli farm) | ~52 crops, 242 varieties | DTM, harvest window, price, spacing, task timing patterns, harvest aggregates (cycles/season, peak week, yield ranges) |

**Scalar fields covered already:** `days_to_maturity`, `harvest_window_max_days`,
`avg_yield_per_bed_m`, `documented_price`, `in_row_spacing_cm`, `rows_per_bed`,
`planting_method`, `days_in_gh_total`, `days_to_first_potting`,
`days_to_germinate_gh` (partial), `rootstock_variety`, harvest seasonality stats.

**Narrative/template fields covered already:** growing-task templates per crop
(JMF + Tend), per-crop pest/disease notes, harvest markers, storage handling,
rotation/companion notes, cultivar recommendations (all from JMF NI tier).

---

## 2. Gaps — where supplementary sources would help

The scout should bias toward sources that fill these gaps, ranked high to low:

| Priority | Gap | Why it matters |
|---|---|---|
| HIGH | **Germination temperature ranges** (min/optimal/max °C) per crop | Currently NONE. Critical for planting calendar in Mediterranean/Israeli climate. |
| HIGH | **Frost tolerance** classification per crop (hardy / semi-hardy / tender) | Currently NONE. Drives season selection. |
| HIGH | **Soil pH preferences** per crop | Currently NONE. Drives bed prep + amendments. |
| HIGH | **Israeli/Mediterranean specifics** — local trial data, planting dates for IL climate zones | We have Tend (Israel) but only one farm; need regional/state guidance. |
| MEDIUM | **Companion planting matrix** | Currently only narrative in JMF; structured matrix would be more usable. |
| MEDIUM | **Seed weight per gram** / seeds-per-100g — for seeding density calc | Partial in DIRECT SEEDING CHART (densities only). |
| MEDIUM | **Nutrient demand** per crop (N/P/K typical removal) | Currently NONE. Drives fertilization planning. |
| MEDIUM | **Days-to-germination per soil temp** (germination curves) | Currently only `days_to_germinate_gh` (partial). |
| MEDIUM | **Variety-specific data** beyond JMF CULTIVARS (136 entries) | JMF list is Quebec-biased; need Mediterranean-adapted varieties. |
| LOW | Pest/disease taxonomy + ID references | Have JMF narrative; structured taxonomy would help UI. |
| LOW | Post-harvest storage temp/RH ranges | Have JMF narrative; structured table would help. |
| LOW | Cover crops / green manure data | JMF has CAVER CROP CHART (1 page); deeper data would be a plus. |

---

## 3. In-scope source categories (suggested — not exhaustive)

- USDA: PLANTS database, Vegetable Cultivar Reports, Plant Hardiness Zones, ARS GRIN
- FAO: Crop calendar, ECOCROP, FAOSTAT
- University extensions: Cornell, UC Davis, Penn State, Texas A&M, UK RHS
- Israeli/Mediterranean: שה"ם (שירות ההדרכה והמקצוע), מכון וולקני (Volcani Institute / ARO), משרד החקלאות, ICARDA, CIHEAM
- Organic/biointensive: Rodale Institute, IFOAM, FiBL, Johnny's Selected Seeds (public tech sheets)
- EU: EPPO Global Database, COST Action vegetable databases
- Climate-aware: AgWeather, CLIMWAT, NOAA growing degree days
- Open seed networks: Seed Savers Exchange (public catalog data), Real Seeds, Kokopelli

---

## 4. Out-of-scope

- ❌ Subscription-only databases (no public free tier)
- ❌ Sources without clear license / TOS for data extraction
- ❌ Site-specific blogs / personal grower notes (not authoritative)
- ❌ Audio/video-only sources (we need structured or table data)
- ❌ Re-cataloging what JMF already covers (CROP CHART, CULTIVARS narrative, etc.)
- ❌ Implementation / DB schema design — that's a future WP-C
- ❌ Multi-source reconciliation analysis — also future WP

---

## 5. REQUIRED OUTPUT FORMAT (binding)

Deliver a single markdown report at:
`_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/FINDINGS_v1.0.0.md`

For EACH candidate source (5-12 total recommended), produce a structured row
with EXACTLY these 14 parameters:

```yaml
---
candidate_id: CS-NN
name: "<authoritative name of source>"
url: "<full canonical URL — direct to data, not landing page when possible>"
source_type: "database | table | chart | api | downloadable_dataset"
owner: "<organization>"
license: "<public_domain | CC-BY | CC-BY-SA | gov-open | terms_of_use | unclear>"
language: "<en | he | both | other>"
coverage_crops: "<count or scope, e.g., '~200 vegetables' or '50 crops, NE US focus'>"
gap_addressed: "<one or more from §2 gap list>"
data_format: "<HTML table | CSV | XLSX | JSON | API | PDF chart | scraped_html>"
update_cadence: "<annual | static | live | unknown>"
extraction_effort: "<low | medium | high>"
relevance_to_israel: "<high | medium | low | none>"
recommendation: "INGEST | SKIP | INVESTIGATE_FURTHER"
recommendation_reason: "<1-2 sentences — why this verdict>"
---

### CS-NN — <name>

<2-4 sentence description of what the source provides, what fields it covers,
and how it complements existing SFA data.>

**Sample data snippet** (verbatim from source, ≤5 lines, with cited URL):
```
<sample>
```

**Concerns / caveats** (if any):
- <concern 1>
- <concern 2>
```

Repeat for each candidate. End with a **summary table** ranking all candidates
by `gap_addressed` priority + `recommendation`.

---

## 6. Constraints (Iron Rules)

- IR#9 (universal team numbering): you are team_80, deliver to `_COMMUNICATION/team_80/`
- team_80 IR#1: artifacts must include sources + evidence
- team_80 IR#2: findings must be actionable (each row has a clear recommendation)
- team_80 IR#3: this mission requires team_00 explicit approval before kickoff
  (see PRE_APPROVAL_REQUEST_v1.0.0.md)
- team_80 IR#4: deliver findings to architecture team (team_110), not implementation
- team_80 IR#6: identity header mandatory on output
- team_80 IR#7: NEVER write to `_aos/`. Only `_COMMUNICATION/team_80/`.

---

## 7. Success criteria

Mission is COMPLETE when:
- [ ] 5-12 candidate sources documented per §5 format
- [ ] Each candidate has full URL + sample data snippet (verified accessible)
- [ ] Each candidate has explicit INGEST/SKIP/INVESTIGATE recommendation with reason
- [ ] Summary ranking table at end of FINDINGS report
- [ ] No source from §4 out-of-scope list included
- [ ] No duplicate of existing PR/OP/EX coverage (per §1)
- [ ] Hebrew sources searched in Hebrew when applicable (שה"ם / וולקני)
- [ ] All URLs verified to resolve (not 404)
- [ ] Cost stays within $5 cap (per pre-approval block)

---

*MISSION_TEMPLATE | team_10 → team_80 | issued 2026-05-26 pending team_00 approval*
