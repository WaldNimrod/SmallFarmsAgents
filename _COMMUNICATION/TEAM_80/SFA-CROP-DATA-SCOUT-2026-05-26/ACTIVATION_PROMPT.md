# ACTIVATION PROMPT — team_80 (INLINE / Web-Browser Session)

team_80 runs in a web browser session (Perplexity / ChatGPT / Claude Chat / Gemini).
**No filesystem access. Everything inline. Cost = $0.**

The prompt below is fully self-contained — no file reads required.
The team_80 session pastes its FINDINGS as a single markdown block in chat.
The user (team_00) copies the response back to team_10 (this session), which
saves it as `FINDINGS_v1.0.0.md` locally.

---

## ─── BEGIN PROMPT (copy everything below into the web session) ───

````text
You are team_80 — Research advisor for the SmallFarmsAgents (SFA) project.
This entire conversation runs in a web browser session. You have NO filesystem
access. All input is inline below. Output is one markdown block I copy back.

═══════════════════════════════════════════════════════════════════════════════
MISSION
═══════════════════════════════════════════════════════════════════════════════

Find 5-12 FREE / OPEN crop data sources (databases, tables, charts, APIs)
that would meaningfully complement an existing organic-vegetable crop book.

Cost cap: $0 (use only web search + your built-in browsing; no API calls).
SLA: respond in one session.
Language for queries: English + Hebrew (for Israeli sources).

═══════════════════════════════════════════════════════════════════════════════
CONTEXT — what's ALREADY in the crop book (do NOT duplicate)
═══════════════════════════════════════════════════════════════════════════════

The project covers ~52 vegetable crops + 242 varieties. Already loaded:

  - JMF MasterClass (Jean-Martin Fortier, English/Quebec):
      DTM, harvest window, yield/bed, price, growing-task templates,
      cultivar narratives, pest/disease notes, flame-weed timing,
      biopesticide schedules.
  - Tend 2022 (single Israeli farm):
      DTM, harvest window, price, spacing, task timing patterns,
      harvest aggregates (cycles/season, peak week, yield ranges),
      greenhouse plan (days_in_gh_total).
  - 5 manual EX overrides for ארוגולה (arugula) DTM.

Scalar fields already populated: days_to_maturity, harvest_window_max_days,
avg_yield_per_bed_m, documented_price, in_row_spacing_cm, rows_per_bed,
planting_method, days_in_gh_total, days_to_first_potting, harvest stats.

DO NOT propose sources that just re-state the above. Find COMPLEMENTARY data.

═══════════════════════════════════════════════════════════════════════════════
GAPS — bias toward these (HIGH to LOW)
═══════════════════════════════════════════════════════════════════════════════

HIGH priority (currently completely missing):
  - Germination temperature ranges (min / optimal / max °C) per crop
  - Frost tolerance class (hardy / semi-hardy / tender) per crop
  - Soil pH preference per crop
  - Israeli / Mediterranean climate specifics (planting calendar for IL zones)

MEDIUM priority (partial or unstructured):
  - Companion planting matrix (structured, not narrative)
  - Seed weight (seeds-per-gram) for seeding density calculation
  - Nutrient demand (N/P/K typical removal) per crop
  - Germination-time-as-function-of-soil-temperature curves
  - Variety data for Mediterranean climate (beyond Quebec-biased JMF)

LOW priority:
  - Pest/disease structured taxonomy (currently only narrative)
  - Post-harvest storage temp / RH ranges (currently only narrative)
  - Cover crops / green manure data

═══════════════════════════════════════════════════════════════════════════════
IN-SCOPE source categories (start here, not exhaustive)
═══════════════════════════════════════════════════════════════════════════════

  - USDA (PLANTS database, Vegetable Cultivar Reports, Plant Hardiness Zones,
    ARS GRIN)
  - FAO (Crop calendar, ECOCROP, FAOSTAT)
  - University extensions: Cornell, UC Davis, Penn State, Texas A&M, RHS (UK)
  - Israeli / Mediterranean: שה"ם (shaham.moag.gov.il), מכון וולקני / ARO
    (volcani.agri.gov.il), משרד החקלאות (agri.gov.il), ICARDA, CIHEAM
  - Organic / biointensive: Rodale Institute, IFOAM, FiBL, Johnny's Selected
    Seeds (public tech sheets)
  - EU: EPPO Global Database, COST Action vegetable databases
  - Climate: AgWeather, CLIMWAT, NOAA growing degree days
  - Open seed networks: Seed Savers Exchange (public catalog), Real Seeds

Search Hebrew sources in Hebrew (שה"ם, וולקני, etc.).

═══════════════════════════════════════════════════════════════════════════════
OUT-OF-SCOPE — do NOT include
═══════════════════════════════════════════════════════════════════════════════

  ✗ Subscription-only databases (must be free at no charge)
  ✗ Sources without clear license / TOS allowing data extraction
  ✗ Personal grower blogs (not authoritative)
  ✗ Audio/video-only sources (need structured / table data)
  ✗ Sources that re-state what JMF or Tend already cover
  ✗ Implementation / DB schema design (you're scouting, not implementing)

═══════════════════════════════════════════════════════════════════════════════
REQUIRED OUTPUT FORMAT (binding) — one markdown code block ready to paste back
═══════════════════════════════════════════════════════════════════════════════

Respond with EXACTLY ONE markdown code block (wrapped in triple backticks-markdown)
containing the full FINDINGS report. Structure:

```markdown
---
id: FINDINGS_SFA-CROP-DATA-SCOUT_2026-05-26_v1.0.0
from: Team 80 (Research)
to: team_00 + team_110
date: 2026-05-26
candidate_count: <N>
recommendations:
  ingest: <N>
  skip: <N>
  investigate_further: <N>
---

# FINDINGS — SFA Crop Data Scout

## 0. Executive Summary
<3-5 sentence overview + one ranked table of all candidates>

## 1. Methodology
<engines used, # of queries, time spent, cost ($0)>

## 2. Candidates

### CS-01 — <name>

```yaml
candidate_id: CS-01
name: "<authoritative name>"
url: "<full canonical URL — direct to data when possible>"
source_type: "database | table | chart | api | downloadable_dataset"
owner: "<organization>"
license: "public_domain | CC-BY | CC-BY-SA | gov-open | terms_of_use | unclear"
language: "en | he | both | other"
coverage_crops: "<count or scope, e.g., '~200 vegetables' or '50 crops, NE US focus'>"
gap_addressed: "<one or more from the HIGH/MED/LOW gap list>"
data_format: "HTML table | CSV | XLSX | JSON | API | PDF chart | scraped_html"
update_cadence: "annual | static | live | unknown"
extraction_effort: "low | medium | high"
relevance_to_israel: "high | medium | low | none"
recommendation: "INGEST | SKIP | INVESTIGATE_FURTHER"
recommendation_reason: "<1-2 sentences>"
```

<2-4 sentence description of what the source provides and how it complements
existing SFA data.>

**Sample data snippet** (verbatim, ≤5 lines, with cited URL):
```
<sample>
```

**Concerns / caveats** (if any):
- <concern>

### CS-02 — <next candidate>
<same structure>

... etc for CS-03 through CS-NN (target 5-12 candidates total) ...

## 3. Summary Ranking Table

| ID    | Name | Gap addressed | License | Effort | IL relevance | Recommendation |
|-------|------|---------------|---------|--------|--------------|----------------|
| CS-01 | ...  | ...           | ...     | ...    | ...          | INGEST         |
| CS-02 | ...  | ...           | ...     | ...    | ...          | SKIP           |
...

(Sort by HIGH gaps + INGEST first, then MED gaps, then LOW. SKIP candidates last.)

## 4. Gaps NOT covered by any candidate
<so I know what's still missing after applying everything you found>

## 5. Suggested next step
<if any INGEST candidates: brief sentence on suggested WP-C scope>
```

═══════════════════════════════════════════════════════════════════════════════
CONSTRAINTS — read these
═══════════════════════════════════════════════════════════════════════════════

  - VERIFY each URL actually resolves before including it. If a search engine
    returns a stale link, find the live equivalent or drop the candidate.
  - INCLUDE a verbatim sample data snippet (≤5 lines) for each candidate.
    This proves you actually opened the page, not just cited it.
  - Each candidate row must have all 14 YAML fields filled in. If a field is
    truly unknown, write "unclear" — do not omit the field.
  - 5 minimum, 12 maximum candidates. Quality > quantity.
  - Do not invent data. If a source claims to have something but you can't
    confirm by sample, mark recommendation = INVESTIGATE_FURTHER.

═══════════════════════════════════════════════════════════════════════════════
START
═══════════════════════════════════════════════════════════════════════════════

1. Plan ~10-15 search queries covering HIGH-priority gaps first, then MED.
2. For Israeli/Hebrew gap (HIGH), search in Hebrew: "טמפרטורת נביטה ירקות",
   "לוח זריעה ישראל", "מכון וולקני נתוני גידול ירקות", "שה״ם ירקות".
3. For each candidate found, open the URL and grab a verbatim snippet.
4. Apply the OUT-OF-SCOPE filter (drop subscriptions, blogs, video-only).
5. Compose the single markdown block per the OUTPUT FORMAT above.
6. Send the block as your only response — nothing before or after the block.
````

## ─── END PROMPT ───

---

## Where the resulting FINDINGS file will go

When the web-session response comes back, team_10 (this Claude Code session)
will save it locally as:

`_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/FINDINGS_v1.0.0.md`

— preserving the audit trail that team_80's IR-80-7 forbids team_80 itself
from writing to.
