# PROGRAM BRIEF — SFA-S003-P002-WP-B
**Document version:** v1.0.0
**Author:** team_10 (sfa_build, Claude Sonnet 4.6)
**Date:** 2026-05-24
**Audience:** team_110 (LOD400 spec author)
**Status:** READY_FOR_LOD400

Multi-source crop knowledge base — JMF base → JMF PDF extraction → Tend Israeli overlay.

This brief is the **LOD200-level program scope** that defines three work packages.
team_110 expands each WP individually into a complete LOD400_spec.md.

---

## 0. Strategic Context

WP-A (LOD500_LOCKED at commit `594cbc8`) delivered the enrichment **engine**:
SOURCE_REGISTRY (7 classes), FIELD_POLICY, reconciler, `crop_field_enrichment`
table, validation harness. **But the data is sparse:**

- Only 3 fields enriched (DTM, harvest_window, documented_price)
- Only OP tier loaded (Tend, 320 rows) + 5 EX (team_00 ארוגולה)
- **No JMF data (PR tier) — directory empty when WP-A ran**
- 0 growing-task templates, 0 crop descriptions, 0 cultivar narratives

WP-B fills the engine. **Architecture: JMF is the base, Tend is the local overlay.**

```
WP-B1 (JMF Excel)    →  Validated normative base (PR tier, 0.70)
        ↓ overlay
WP-B3 (Tend overlay) →  Israeli local adaptation (OP tier, 0.55)
        ↓ enrich
WP-B2 (JMF PDF, AI)  →  Per-crop narrative knowledge (NI tier, hard override)
```

---

## 1. Asset Inventory — paths confirmed on disk

### JMF Excel (WP-B1 input):
Base path: `/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning/`

| File | Sheets used | Rows |
|------|-------------|------|
| `CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX` | `CROP CHART`, `CROP ASSOCIATED TASKS`, `DIRECT SEEDING CHART`, `NURSERY & TRANSPLANT CHART`, `CULTIVARS` | 52 / 30 / 21 / 45 / 136 |
| `../תבלאות נתונים/DIRECTSEEDINGCHART-*.XLSX` | standalone copy of seeding chart | 21 |
| `../תבלאות נתונים/NURSERYTRANSPLANTCHART-*.XLSX` | standalone copy of nursery chart | 45 |

### JMF PDF (WP-B2 input):
Base path: `/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/`

| File | Pages | Content type |
|------|-------|--------------|
| `THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF` | 240 | Per-crop chapters (narrative) |
| `THE MARKET GARDENER_*.PDF` | 209 | Same book, different edition |
| `FT_FINALE_FLAMEWEEDING*.PDF` | 3 | Flame weed timing per crop |
| `FT_FINALE_PHYTOPROTECTION*.PDF` | 3 | Biopesticide guide |
| `FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE*.PDF` | 5 | Biopesticide application table (structured) |
| `FT_FINALE_NURSERYSEEDING*.PDF` | 13 | Nursery seeding process |

### Tend Israel (WP-B3 input):
Base path: `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/`

| File | Rows | WP-B3 usage |
|------|------|-------------|
| `TASKS (from macBook Air - nimrod).CSV` | 798 | Extract recurring template patterns only |
| `GREENHOUSE_PLAN (from macBook Air - nimrod).CSV` | 287 | Populate `days_in_gh_total`, `days_to_germinate_gh` |
| `HARVESTS (from macBook Air - nimrod).CSV` | 939 | Aggregate to statistics — NOT individual records |
| `NOTES (from macBook Air - nimrod).CSV` | 27 | Skip — site-specific observations, not templates |
| `LOCATIONS`, `ORDERS_*`, `PACK`, `PICK`, `SEED_LIST` | varies | Skip — not relevant per team_00 directive |

---

## 2. WP-B1 — JMF Excel Base Layer

### Purpose
Load JMF MasterClass Excel files as the validated baseline (PR tier, 0.70).

### Deliverables

**Migration 044:**
```sql
CREATE TABLE crop_task_templates (
    id BIGSERIAL PRIMARY KEY,
    crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    trust_tier VARCHAR(20) NOT NULL,
    task_type VARCHAR(40) NOT NULL,
    timing_anchor VARCHAR(20),
    days_offset INTEGER,
    method TEXT,
    input_material TEXT,
    notes TEXT,
    display_order INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_id, source, task_type, days_offset)
);
CREATE INDEX idx_cct_crop ON crop_task_templates(crop_id);
CREATE INDEX idx_cct_type ON crop_task_templates(task_type);
```

`task_type` enum values (from JMF CROP ASSOCIATED TASKS columns):
`stale_seed_bed`, `flame_weeder`, `flextine_harrow_1`, `flextine_harrow_2`,
`biodisc`, `hoe`, `hand_weed`, `boron_seaweed_1`, `boron_seaweed_2`,
`straw_mulch_topdress`, `head_pinch_chop`, `mow_and_tarp`,
`at_seeding_transplanting`, `net_row_cover`

`timing_anchor` enum: `seeding`, `transplanting`, `harvest`, `field_prep`

**New importer:**
`organic_market_agent/crop_book/importer/jmf_masterclass.py`
- `parse_crop_chart(xlsx_path) -> list[dict]` — DTM, HW, days_in_cell, yield, price, unit
- `parse_associated_tasks(xlsx_path) -> list[TaskTemplate]`
- `parse_direct_seeding_chart(xlsx_path) -> list[dict]` — spacing, seeder, calibration, density
- `parse_nursery_chart(xlsx_path) -> list[dict]` — tray, days_in_cell, nursery_notes
- `parse_cultivars(xlsx_path) -> list[dict]` — provider, DTM, description, comments
- `import_jmf_masterclass(session, xlsx_path)` — orchestrator

### Crop-name mapping (critical)
JMF uses English crop names ("Arugula", "Beets", "Bell Pepper").
DB uses Hebrew (`crops.name_he`) as primary. Need explicit mapping table or join via `crops.name_en`.
**Action:** add `JMF_CROP_MAP: dict[str, str]` constant in `organic_market_agent/crop_book/constants.py`
mapping JMF English → DB Hebrew name. Decision: if no match → log warning + skip.

### New source_values populated:
| field_name | from JMF sheet | unit |
|------------|----------------|------|
| `days_to_maturity` | CROP CHART, CULTIVARS | days |
| `harvest_window_max_days` | CROP CHART | days |
| `days_in_nursery_cell` | NURSERY CHART | days |
| `avg_yield_per_bed_m` | CROP CHART (yield/100bed → convert to per-meter) | yield/m |
| `documented_price` | CROP CHART | ILS/unit |
| `in_row_spacing_cm` | DIRECT SEEDING + NURSERY (convert inches → cm) | cm |
| `rows_per_bed` | DIRECT SEEDING + NURSERY | rows |
| `direct_seed_density_g` | DIRECT SEEDING CHART | g/bed |
| `nursery_tray_type` | NURSERY CHART | text |
| `cultivar_provider` | CULTIVARS | text |
| `cultivar_description` | CULTIVARS (long text) | text |

All loaded with `source='JMF'`, `trust_tier='PR'`, `confidence_weight=0.70`.

### CLI integration
- `seed.py --jmf-only` flag to import JMF Excel alone
- `seed.py --all` should call jmf importer in addition to Tend
- `seed.py --no-jmf` opt-out for testing

### Acceptance Criteria scope
~15 ACs covering:
- Migration 044 forward/backward
- Importer parses each of 5 sheets correctly
- Crop name mapping (JMF→Hebrew) handles all 52 JMF crops
- Unit conversions (inches→cm, /100bed→/m) are accurate
- Source values upsert correctly (idempotent re-import)
- crop_task_templates populated with correct timing
- Enrichment runner picks up new PR-tier values (blending kicks in)
- Tests: ≥25 (parser tests + DB integration + idempotency)

---

## 3. WP-B2 — JMF PDF Extraction Layer (AI-assisted via NI source)

### Purpose
Extract per-crop narrative knowledge from "The Market Gardener" book and Fiche
Technique PDFs into structured fields. Uses the `NIImporter` skeleton built in WP-A.

### Deliverables

**Migration 045 (additive, only if needed):**
```sql
CREATE TABLE crop_knowledge_notes (
    id BIGSERIAL PRIMARY KEY,
    crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    trust_tier VARCHAR(20) NOT NULL,
    note_type VARCHAR(40) NOT NULL,
    body_text TEXT NOT NULL,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_id, source, note_type)
);
```

`note_type` enum:
`pest_disease`, `harvest_marker`, `storage_handling`, `rotation_companion`,
`cultivar_recommendation`, `growing_tip`, `irrigation`, `nursery_specific`

**Decision point for team_110**: should this be a new table OR enrich existing
`crop_varieties.notes` column? Recommendation: NEW table because notes are
crop-level (not variety-level) and structured by type.

**New importers** (concrete `NIImporter` subclasses):
- `organic_market_agent/crop_book/importer/ni/jmf_book.py`
  - Reads `THEMARKETGARDENEREBOOK.PDF` via `pdftotext`
  - For each known crop, locates the chapter section (heuristic + heading match)
  - Extracts: pest_disease, harvest_marker, storage_handling, rotation, cultivars
  - Source label: `NI:jmf_book_v1`
- `organic_market_agent/crop_book/importer/ni/jmf_ft_flameweed.py`
  - Parses FT_FLAMEWEEDING PDF (3pp, structured)
  - Adds `flame_weeder` task templates with refined timing
  - Source label: `NI:jmf_ft_flameweed`
- `organic_market_agent/crop_book/importer/ni/jmf_ft_biopesticide.py`
  - Parses FT_TABLEAUAPPLICATIONBIOPESTICIPE table (5pp)
  - Adds pest/disease notes per crop + spray schedule
  - Source label: `NI:jmf_ft_biopesticide`

### LLM-assisted extraction architecture
- The PDF extraction is **NOT** done at runtime. It's a one-time `prepare` step:
  1. `pdftotext` extracts raw text per PDF
  2. A Python script using Anthropic API (Claude) chunks the text by crop chapter
  3. For each chunk, Claude extracts structured fields → JSON
  4. JSON cached to `data/jmf/extracted/<crop>_<source>.json`
  5. The importer reads cached JSON and upserts to DB
- Reasoning: avoid LLM calls at deploy time; allow team review of extractions before commit.

**Caching contract:** All extractions cached under `data/jmf/extracted/` (gitignored or committed — team_110 decides).

### Trust tier
NI (hard override, weight=NULL, `is_hard_override=True`). Falls back to NULL weight in `confidence_weight`. NI values win over JMF (PR) and Tend (OP) for the same field.

### Acceptance Criteria scope
~10 ACs covering:
- PDF text extraction works (no encoding loss for crop names)
- Per-crop chapter detection is correct (manual spot-check 5 crops)
- JSON cache schema is stable
- DB upsert is idempotent
- Enrichment runner respects NI hard override
- Tests: ≥15 (parser tests + LLM stub tests + DB integration)

---

## 4. WP-B3 — Tend Israel Adaptation Overlay

### Purpose
Layer Israeli local adaptation on top of JMF base. Only **recurring template
patterns** — NOT individual one-off records.

### Deliverables

**Migration 046:**
```sql
CREATE TABLE crop_harvest_stats (
    id BIGSERIAL PRIMARY KEY,
    crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    season VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL,
    cycles_count INTEGER,
    first_harvest_week INTEGER,
    peak_harvest_week INTEGER,
    last_harvest_week INTEGER,
    yield_total NUMERIC(12,2),
    yield_unit VARCHAR(20),
    yield_per_bed_min NUMERIC(10,3),
    yield_per_bed_max NUMERIC(10,3),
    yield_per_bed_median NUMERIC(10,3),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_id, season, year, source)
);
```

**New importer:**
`organic_market_agent/crop_book/importer/tend_overlay.py`

Sub-modules:
- `parse_tasks_templates(csv_path) -> list[TaskTemplate]`
  - Whitelist: `Transplant`, `Direct Sow`, `Greenhouse Sow`, `Weed`,
    `Row Cover & Mulch`, `Stale Bed`, `Pest & Disease`, `Potting up`, `Thin`
  - Blacklist: `Maintenance`, `Irrigate`, `Trellis` (when planting=blank),
    `Seed Cleaning`, `Drill Sow`, `השלמות שתילה`, `ריכוז שעות`, `הידרופוניקה`
  - For each whitelisted task: derive `(crop_id, task_type, days_offset_from_sow)`
  - Aggregate timing across plantings → median + range
  - Upsert to `crop_task_templates` with `source='Tend_2022'`, `trust_tier='OP'`
- `parse_greenhouse_plan(csv_path) -> list[dict]`
  - Extract `Days In Greenhouse`, `Days to 1st potting up` per crop
  - Upsert to `crop_variety_source_values` (fields: `days_in_gh_total`, `days_to_first_potting`)
- `parse_harvests_aggregate(csv_path) -> list[HarvestStat]`
  - Aggregate by (crop, year, season) → cycles_count, peak_week, yield range
  - Upsert to `crop_harvest_stats`
  - **NEVER** insert individual harvest records

### Task-type mapping (Tend → JMF taxonomy)
| Tend Task Type | JMF task_type | Notes |
|----------------|---------------|-------|
| `Direct Sow` | `at_seeding_transplanting` | timing_anchor=seeding |
| `Transplant` | `at_seeding_transplanting` | timing_anchor=transplanting |
| `Greenhouse Sow` | `nursery_seed` | new task_type, anchor=seeding |
| `Weed` (Method=Hand weed) | `hand_weed` | days_offset from planting |
| `Stale Bed` | `stale_seed_bed` | days_offset negative (pre-planting) |
| `Row Cover & Mulch` (Method=Tarp) | `net_row_cover` | |
| `Pest & Disease` | `pest_spray` | new task_type, captures method |
| `Potting up` | `potting_up` | new task_type |
| `Thin` | `thinning` | new task_type |

### Acceptance Criteria scope
~12 ACs covering:
- Task whitelist filter applied correctly
- Task type mapping (Tend→JMF) is correct
- Timing aggregation (median + range) is accurate
- Harvest aggregation does NOT create per-record rows
- Crop name mapping (Tend → DB Hebrew) handles all crops
- Idempotent re-import
- Enrichment runner blends Tend (OP) with JMF (PR) correctly
- Tests: ≥20 (parser tests + aggregation tests + DB integration)

---

## 5. Cross-WP Invariants (apply to all 3 WPs)

### LOD500_LOCKED protections (untouched)
- `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py`
- Migrations `001`-`043`
- `tend.py`, `jmf.py` (the empty stub from WP-A — but may be replaced/extended)
- mu-plugin

### GCR requirements
- WP-B1: **No `models.py` GCR needed** (new table + ORM is additive)
- WP-B2: **GCR_2 needed if** `crop_knowledge_notes` requires `Crop.knowledge_notes` relationship on existing `Crop` model. Otherwise additive.
- WP-B3: **No `models.py` GCR needed** (new `crop_harvest_stats` table is additive)

team_110 must request GCRs from team_00 BEFORE LOD400 lock if any model.py mutations are required.

### Iron Rule #4 compliance
- All builder commits must NOT include `_aos/roadmap.yaml`
- Roadmap transitions only via MSG to team_100

### Engine reuse
- All new source values go through the WP-A enrichment engine
- All importers must populate `trust_tier` and `confidence_weight` on insert
- No bypassing of `reconcile_field` for blendable fields

### Dependencies
```
WP-B1 (JMF Excel) ────┬───→ WP-B2 (JMF PDF NI)   [B2 reuses crop_id mappings]
                      └───→ WP-B3 (Tend overlay)  [B3 layers OP on PR baseline]
```

WP-B1 must complete first. B2 and B3 can proceed in parallel.

---

## 6. Deliverables Summary

| Artifact | WP-B1 | WP-B2 | WP-B3 |
|----------|-------|-------|-------|
| LOD400 spec | required | required | required |
| Migration | 044 | 045 (optional) | 046 |
| New importer | jmf_masterclass.py | ni/jmf_book.py + 2 FT | tend_overlay.py |
| New tables | crop_task_templates | crop_knowledge_notes? | crop_harvest_stats |
| Min tests | 25 | 15 | 20 |
| Min ACs | 15 | 10 | 12 |
| Estimated effort | LARGE | LARGE (LLM work) | MEDIUM |

---

## 7. Open Questions for team_110 to Resolve in LOD400

1. **JMF crop name map** — propose canonical mapping table location and content
2. **WP-B2 storage** — new table OR enrich `crop_varieties.notes`? (recommend new table)
3. **LLM extraction caching** — `data/jmf/extracted/` committed or gitignored?
4. **Tend task whitelist** — confirm final list with team_00 before LOD400 lock
5. **Harvest aggregation grain** — by (crop, year, season) — confirm season enum: spring/summer/fall/winter?
6. **JMF PDF unicode handling** — Hebrew crop names in JMF? (likely English-only — confirm)

---

_Authored by team_10 (Claude Sonnet 4.6) 2026-05-24. Handoff to team_110 for LOD400._
