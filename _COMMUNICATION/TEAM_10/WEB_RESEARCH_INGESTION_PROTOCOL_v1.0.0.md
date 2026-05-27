---
artifact: WEB_RESEARCH_INGESTION_PROTOCOL
version: "1.0.0"
author: team_10 (sfa_build)
date: 2026-05-27
status: ACTIVE
scope: Incoming web research from Team 80 and other teams
related: _COMMUNICATION/TEAM_80/MANDATE_CROP_EXPANSION_16_CROPS_v1.0.0.md
---

# Web Research Ingestion Protocol — Incoming Team Data

## Why this exists

Multiple teams (team_80, team_00, future teams) will deliver crop data packages
from external sources. This protocol ensures:
1. Raw data is always archived before ingestion
2. Every source value in DB traces to a citable external source
3. No duplicate or wrong-source rows are created
4. New teams' data can be ingested via the standard NI importer pipeline

---

## Current Sources Already in DB (DO NOT RE-USE THESE LABELS)

| Source label | Origin | Fields |
|---|---|---|
| `OP:Idan_2017` | Nimrod farm records 2017 | spacing, rows_per_bed, avg_yield |
| `OP:Idan_2018` | Nimrod farm records 2018 | same |
| `OP:Idan_seedlings` | Nimrod seedling order sheets | succession patterns |
| `OP:CurtisStone` | Curtis Stone Master Chart | DTM, yield/bed, CVR |
| `OP:vital_seeds_count` | Vital Seeds (UK) | seeds_per_gram |
| `OP:osborne_seed_count` | Osborne Seeds | seeds_per_gram |
| `OP:FRANCHI_catalog` | FRANCHI Italy seed catalog | variety names |
| `PR:uc_anr_germination` | UC ANR germination guide | germination_temp |
| `PR:osu_frost_tolerance` | OSU frost tolerance table | frost_tolerance_class |
| `PR:umd_soil_ph` | UMD soil pH guide | soil_ph_target, soil_ph_liming_threshold |
| `PR:ne_veg_guide` | NE Veg Guide nutrients | nutrient_removal_* |
| `NI:il_moa_garden_guide` | Israeli MoA garden guide | planting_calendar |
| `NI:sham_hydro_guide_v1` | Shaham hydro guide | hydro_suitability (knowledge_notes) |
| `NI:sham_variety_trials_v1` | Shaham 2021 trial | variety_trial_score |
| `NI:jmf_ft_nurseryseeding_ext_v1` | JMF nursery seeding | nursery_specific |
| `NI:jmf_ft_seedingincellflats_v1` | JMF seeding in flats | nursery_specific |
| `NI:aosnot_v1` | AOSNOT variety info | frost_tolerance, flowering_date (ckn) |
| `Tend` / `Tend_20XX` | Tend farm CSV exports | days_in_gh, planting plans |
| `team_00` | Manual team_00 entries | various |

---

## Incoming Data — Team 80 (Crop Expansion 16 Crops)

### Expected artifact
`_COMMUNICATION/TEAM_80/CROP_DATA_FINDINGS_16_CROPS_v1.0.0.md`

### Step 1 — Save raw file immediately

When the report arrives, save it BEFORE any processing:
```
data/external_sources/web/team80_crop_expansion_16_crops/
  session_01_correction_acknowledgment.md    ← already saved (2026-05-27)
  session_02_full_research_report.md         ← save here when received
```

### Step 2 — Create extract.json cache files

For each crop in the report, create:
```
data/external_sources/extracted/team80_crop_expansion/
  {crop_he}.json    (e.g., כרובית.json, בטטה.json, ...)
```

Cache JSON schema — fields match `crop_variety_source_values.field_name`:
```json
{
  "schema_version": "1.0",
  "source": "WR:team80_crop_expansion_v1",
  "crop_he": "כרובית",
  "provenance": {
    "report": "CROP_DATA_FINDINGS_16_CROPS_v1.0.0.md",
    "extraction_model": "team_80_manual",
    "extracted_at": "2026-XX-XX"
  },
  "fields": {
    "days_to_maturity": {"value": 65, "unit": "days", "method": "transplant",
                         "source_url": "https://...", "source_name": "Cornell Extension"},
    "in_row_spacing_cm": {"value": 45, "unit": "cm",
                          "source_url": "...", "source_name": "..."},
    "rows_per_bed": {"value": 2, "unit": null, "source_url": "...", "source_name": "..."},
    "planting_method": {"value": "transplant", "unit": null,
                        "source_url": "...", "source_name": "..."},
    "yield_per_m2_kg": {"value": 2.5, "unit": "kg/m2",
                        "source_url": "...", "source_name": "..."},
    "seeds_per_gram": {"value": 300, "unit": "seeds/g",
                       "source_url": "...", "source_name": "..."},
    "germination_temp_c_opt": {"value": "15-20", "unit": "C",
                               "source_url": "...", "source_name": "..."},
    "frost_tolerance_class": {"value": "half-hardy", "unit": null,
                              "source_url": "...", "source_name": "..."},
    "harvest_window_max_days": {"value": 14, "unit": "days",
                                "source_url": "...", "source_name": "..."},
    "succession_interval_weeks": {"value": 3, "unit": "weeks",
                                  "source_url": "...", "source_name": "..."},
    "soil_ph_target": {"value": "6.0-7.0", "unit": null,
                       "source_url": "...", "source_name": "..."}
  }
}
```

### Step 3 — Create NI importer

New file: `organic_market_agent/crop_book/importer/ni/team80_crop_expansion.py`

```python
"""WP-D: Team 80 web research — 16 crop expansion data."""
from pathlib import Path
from organic_market_agent.crop_book.importer.ni_importer import BaseNIImporter

SOURCE = "WR:team80_crop_expansion_v1"
CACHE_DIR = Path("data/external_sources/extracted/team80_crop_expansion")

class Team80CropExpansionImporter(BaseNIImporter):
    name = "team80_crop_expansion_v1"
    cache_dir = CACHE_DIR
    # load() → source_values for numeric fields
    # load_knowledge_notes() → empty (web research → source_values, not ckn)
```

Source label prefix: **`WR:`** (Web Research) — distinct from `OP:` (Operator), `PR:` (Peer Research), `NI:` (Narrative Intelligence).

### Step 4 — Deduplication check

**CRITICAL:** Before ingesting, check which fields are already covered for each crop.
The current coverage map (2026-05-27) is:

| Crop | Fields already in DB | Sources |
|---|---|---|
| עגבניית שרי | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, days_in_gh_total | OP:Idan_2017, Tend_20XX |
| אבטיח | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, soil_ph_target | OP:Idan_2017, PR:umd_soil_ph |
| כרובית | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, seeds_per_gram, soil_ph_target | OP:Idan_2017, OP:vital_seeds_count, PR:umd_soil_ph |
| במיה | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, soil_ph_target | OP:Idan_2017, PR:umd_soil_ph |
| תירס | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, germination_temp, frost_tolerance_class, soil_ph_target, nutrient_removal | OP:Idan_2017, PR:uc_anr, PR:osu_frost, PR:umd_soil_ph, PR:ne_veg_guide |
| תפוח אדמה | in_row_spacing_cm, rows_per_bed, avg_yield_per_bed_m, frost_tolerance_class, nutrient_removal | OP:Idan_2017, PR:osu_frost, PR:ne_veg_guide |
| אדממה | in_row_spacing_cm | OP:Idan_2017 |
| חמניה | seeds_per_gram | OP:vital_seeds_count |

Team 80 data for a field already in DB → still write it (adds a second source = increases ≥2 source coverage). The reconciler blends by confidence_weight; `WR:` sources default to `confidence_weight=0.7`.

Do NOT write to fields where we already have ≥3 sources — check reconciled view first.

### Step 5 — Ingest

```bash
# After importer created and cache files in place:
python3 -m organic_market_agent.crop_book.importer.seed --wp-d-only   # (add flag in seed.py)
# OR run directly during WP-D session
```

---

## Incoming Data — Other Teams

When additional packages arrive:

| Source type | Label prefix | Notes |
|---|---|---|
| Web research (scraping, extension sites) | `WR:` | |
| Operator / grower field records | `OP:` | Nimrod's data, partner farms |
| Peer research (academic, gov extension) | `PR:` | Cited publications |
| Narrative Intelligence (LLM extraction) | `NI:` | PDF/DOCX extraction |
| Direct team_00 entry | `team_00` | Manual trusted override |

Each new source needs:
1. Raw file saved to `data/external_sources/web/<source_slug>/`
2. Extract JSON in `data/external_sources/extracted/<source_slug>/`
3. NI importer in `organic_market_agent/crop_book/importer/ni/<source_slug>.py`
4. Registration in `seed.py` under appropriate wave flag

---

## Pending Local Sources Still to Ingest (from WAVE_PLAN)

The following local files exist in `data/external_sources/` but are NOT yet in DB:

| Source | File | Fields | Priority |
|---|---|---|---|
| L03/L04 Idan winter/summer | `israeli/L03_IDAN_winter_planning.xlsx` | DTM, spacing, harvest window, succession | HIGH |
| L49 Idan 2018 update | `israeli/L49_IDAN_market_gardening_tech.xlsx` | same as L03/L04 | HIGH |
| L01 GrowOrganic calendar | `israeli/L01_GROWORGANIC_sowing_dates_base.xlsx` | Israeli planting calendar | HIGH |
| L36 Bustan calendar | `israeli/L36_BUSTAN_sowing_calendar.pdf` | Israeli monthly calendar | HIGH |
| L40 Curtis chart | `urban_farmer/L40_curtis_crop_profiles.xlsx` | DTM, yield/bed, CVR | MEDIUM |
| L41 Curtis images | `urban_farmer/L41_curtis_chart_*.jpg` (34) | Per-crop profiles | LOW (OCR needed) |

These represent the highest-value remaining gap-fill for core planner fields (especially DTM).

---

team_10 / sfa_build
2026-05-27
