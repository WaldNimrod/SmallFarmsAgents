# Wave Plan — External Sources Ingestion (3 Waves)

**Companion to:** `INDEX.md`
**Generated:** 2026-05-26
**Author:** team_10 (preparation; team_110 owns execution per ADR045)

This plan converts the 20+ external source candidates into 3 WP-scoped waves.
Each wave is sized to be a single WP (LOD200 → LOD400 → build → validate →
close). Waves are sequenced by dependency + risk profile.

---

## 🌊 WAVE 1 — Structured Tabular Ingestion (LOW risk, HIGH yield)

**Proposed WP id:** `SFA-S003-P002-WP-C1`
**Name:** "Israeli structured data + Tend multi-year backfill"
**Effort:** MEDIUM
**Risk:** LOW (XLSX/CSV with clear schemas; no LLM extraction; no PDF parsing)
**Trust tiers added:** PR (Israeli MoA-published), OP (Israeli growers), OP (Tend)

### Scope

Ingest the 8 Tier-1 files — all already in well-known tabular format:

| File | New importer | Trust tier | Target table |
|------|--------------|:---:|--------------|
| L01 GROWORGANIC sowing dates | `israeli/groworganic_importer.py` | PR (0.70) | `crop_planting_calendar` (NEW) |
| L36 BUSTAN calendar | `israeli/bustan_importer.py` (PDF-table) | PR | `crop_planting_calendar` |
| L12 JMF cover crop chart | `jmf/cover_crops_importer.py` | PR | `crop_cover_crops` (NEW) |
| L03 IDAN winter planning | `israeli/idan_planning_importer.py` | OP (0.55) | `crop_variety_source_values` (existing) + `crop_seasonal_plan` (NEW) |
| L04 IDAN summer planning | same | OP | same |
| Tend 2019, 2020, 2021 (3 years) | extend `tend_overlay.py` from WP-B3 | OP | existing tables |

### New schemas (2 migrations)

**Migration 047** — `crop_planting_calendar`
```sql
CREATE TABLE crop_planting_calendar (
  id BIGSERIAL PRIMARY KEY,
  crop_id BIGINT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
  source VARCHAR(50) NOT NULL,        -- 'NI:groworganic', 'NI:bustan'
  trust_tier VARCHAR(20) NOT NULL,
  region VARCHAR(40),                  -- 'IL_general', 'IL_north', etc.
  month_jan BOOLEAN, month_feb BOOLEAN, ..., month_dec BOOLEAN,  -- 12 cols
  activity_type VARCHAR(20),           -- 'seed' / 'transplant' / 'both'
  season VARCHAR(20),                  -- 'spring'/'summer'/'fall'/'winter'/'all'
  notes TEXT,
  UNIQUE(crop_id, source, activity_type)
);
```

**Migration 048** — `crop_cover_crops` (small standalone table — possibly fold into NI tier)
```sql
CREATE TABLE crop_cover_crops (
  id BIGSERIAL PRIMARY KEY,
  name_en VARCHAR(60), name_he VARCHAR(60),
  category VARCHAR(40),                -- 'legume' / 'cereal' / 'brassica' / 'other'
  total_days_garden INTEGER,
  germination_temp_c_min INTEGER,
  hardiness_zone INTEGER,
  sow_window TEXT,
  inoculum VARCHAR(40),
  survives_winter BOOLEAN,
  notes TEXT
);
```

### Tend multi-year backfill
- Re-use `tend_overlay.py` (WP-B3). Add `--year` CLI flag (already exists in seed.py).
- Run for 2019, 2020, 2021 → upserts to `crop_task_templates` + `crop_harvest_stats`
- 2018 deferred (LOW volume — flag with INVESTIGATE).
- Expected DB delta: ~3,000 new harvest aggregates, ~2,500 new task templates → OP-tier statistical power × 4

### Acceptance criteria target (~15 ACs)
- AC-W1-01 — `crop_planting_calendar` migration applies cleanly + backward
- AC-W1-02 — `crop_cover_crops` migration applies cleanly + backward
- AC-W1-03 — `groworganic_importer.py` parses 86 rows correctly with seasonal markers
- AC-W1-04 — `bustan_importer.py` extracts monthly planting matrix from PDF (table parse)
- AC-W1-05 — `idan_planning_importer.py` round-trips both winter (L03) and summer (L04)
- AC-W1-06 — JMF cover-crop chart populates `crop_cover_crops` with all rows
- AC-W1-07 — Tend 2019 ingestion: 442 CROP_PLAN rows + 1,884 HARVESTS aggregated
- AC-W1-08 — Tend 2020 ingestion: 724 CROP_PLAN + 3,720 HARVESTS aggregated
- AC-W1-09 — Tend 2021 ingestion: 552 CROP_PLAN + 1,723 HARVESTS aggregated
- AC-W1-10 — Idan + GROWORGANIC + Bustan crop-name maps: ≥90% coverage of existing 52 crops
- AC-W1-11 — Reconciler picks up new sources in `reconcile_field()` without changes
- AC-W1-12 — `validate_enrichment.py` shadow-run shows ≥3 new (variety, field) pairs reaching CALIBRATED
- AC-W1-13 — `seed.py --all` invokes all 3 new importers; `--no-{groworganic|bustan|idan|tend-multi}` opt-outs
- AC-W1-14 — Tests ≥25
- AC-W1-15 — validate_aos.sh 29/19/0

### Estimated build effort
- Spec authoring (LOD200+LOD400): 1 session
- Build: 1-2 sessions
- Validate: 1 session
- Total: ~4 sessions

---

## 🌊 WAVE 2 — Narrative Extraction Layer (MEDIUM risk, HIGH yield)

**Proposed WP id:** `SFA-S003-P002-WP-C2`
**Name:** "Hebrew narrative extraction (per-crop encyclopedia + variety trials)"
**Effort:** LARGE
**Risk:** MEDIUM (LLM extraction with caching, similar to WP-B2; Hebrew adds complexity)
**Trust tier added:** NI (hard override)

### Scope

Apply the WP-B2 NIImporter pattern to Hebrew sources:

| File | Concrete NIImporter | Per-crop yield |
|------|---------------------|----------------|
| **L02** AOSNOT (1.3MB DOCX, per-crop Hebrew encyclopedia) | `ni/aosnot_variety_info.py` | ~10 fields per crop (frost-tol, regions, flowering, yield date, pests, pollination, latin) |
| **L11** Variety trials 2021 (שה"מ, official) | `ni/sham_variety_trials.py` | per-variety lettuce scores (color, taste, bolting, overall) |
| **L09** Hydro vegetable guide (שה"מ) | `ni/sham_hydro_guide.py` | per-crop hydro suitability notes |
| **L10** Dr. Zacks leafy survey (52pp) | `ni/zacks_leafy_survey.py` | per-crop production benchmarks IL |
| **L14** FT_NURSERYSEEDING (JMF) | extends WP-B2 `ni/jmf_ft_nurseryseeding.py` | per-crop nursery protocol detail |
| **L13** + **L12** cover crops (already in Wave 1 for chart) | LLM-extract narrative | crop_cover_crops.notes enrichment |
| **L16** seeding in cell flats | extends nursery NIImporter | per-crop cell-flat protocol |

### Pipeline (mirrors WP-B2 architecture)

```
PDF/DOCX  →  pdftotext / textutil  →  raw_text/
                                            │
                                            ▼
                            extraction_runner.py (one-time, manual)
                            calls Anthropic API: chunk per crop chapter
                                            │
                                            ▼
                            data/jmf/extracted/<source>/<crop>.json (cache)
                                            │
                                            ▼
                            ni/<source>_importer.py reads cache, upserts to:
                              - crop_knowledge_notes (existing from WP-B2)
                              - crop_variety_source_values (for blendable scalars
                                like frost_tolerance_class)
```

### New schemas (1 migration)

**Migration 049** — extend `crop_knowledge_notes.note_type` CHECK constraint
Add 4 new enum values:
- `frost_tolerance` (from L02)
- `flowering_date` (from L02)
- `pollination_mechanism` (from L02)
- `israeli_regions` (from L02)
- `variety_trial_score` (from L11)
- `hydro_suitability` (from L09)

### Acceptance criteria target (~12 ACs)
- AC-W2-01 — Migration 049 applies cleanly + backward
- AC-W2-02 — L02 AOSNOT extraction produces ≥20 crop JSON files
- AC-W2-03 — L02 per-crop fields populated for: frost_tolerance, israeli_regions, latin_name, flowering_date, yield_date
- AC-W2-04 — L11 variety-trial data per lettuce variety populated
- AC-W2-05 — L09 hydro guide: per-crop hydroponic suitability classified
- AC-W2-06 — L10 Zacks survey: production benchmarks extracted (where applicable)
- AC-W2-07 — L14 FT_NURSERYSEEDING per-crop nursery protocol extracted
- AC-W2-08 — All extractions cached to `data/external_sources/extracted/`
- AC-W2-09 — Hebrew text preserved (no encoding loss)
- AC-W2-10 — NI tier hard-override semantics preserved (no blending of NI rows)
- AC-W2-11 — Tests ≥15 (parser + LLM-stub + DB integration)
- AC-W2-12 — validate_aos.sh remains clean

### Estimated build effort
- Spec authoring: 1-2 sessions
- Build: 2-3 sessions (LLM extraction takes time; Hebrew prompting tuning)
- Validate: 1 session
- Total: ~5 sessions

---

## 🌊 WAVE 3 — Secondary Sources + OCR + Backlog Sweep (LOWER priority)

**Proposed WP id:** `SFA-S003-P002-WP-C3`
**Name:** "Curtis Stone OCR + Idan 2018 update + secondary backlog"
**Effort:** MEDIUM
**Risk:** MEDIUM (OCR quality variable; some files may not yield clean data)

### Scope

| File | Action | Target |
|------|--------|--------|
| **L40** Curtis Stone master chart XLSX | `urban_farmer/curtis_profiles_importer.py` | OP tier (single source — Curtis's farm, BC Canada — climate caveat) |
| **L41** Curtis 34 scanned book pages | OCR via `tesseract` or vision-LLM → `curtis_book_pages/<crop>.txt` → manual review → NI tier per-crop narrative | NI for non-overlap with L40 XLSX |
| **L05a, L05b** Idan seedling trackers | `idan_seedlings_importer.py` | OP tier — **succession planting templates** (bi-weekly tray orders) → new derived field `succession_interval_weeks` per crop |
| **L06** Covers & tunnels | sheet 1 (plot×month) → SKIP (site-specific). Sheet 2 (FRANCHI seed catalog) → variety reference data → OP tier | Variety enrichment for tomato/zucchini/pepper |
| **L49** Idan 2018 update | Compare against L03/L04 (2017 data). If newer values → supersede; else SKIP duplicates | OP tier patch |
| **L45** Nimrod's 2017 farm data | INVESTIGATE — likely operational not knowledge | Defer unless wave 2 reveals gaps |
| **L43** Customer leafy greens | Confirm SKIP after Wave 1+2 reveal what's missing | SKIP |
| **L38** Italian Libretto Orto | **PARK** — needs OCR + Italian translation; only revisit if Mediterranean adaptation becomes high priority | DEFER |
| **Tend 2018** (the year with 0 HARVESTS) | INVESTIGATE — if just setup data, ingest only CROP_PLAN + SEED_LIST as background | Decision pending |

### Acceptance criteria target (~10 ACs)
- AC-W3-01 — Curtis master chart imported (23 crops × 29 fields)
- AC-W3-02 — Curtis OCR pipeline ≥80% legibility on 34 images; cached as JSON
- AC-W3-03 — Idan seedlings extracted as succession-interval templates per crop
- AC-W3-04 — FRANCHI seed catalog (L06 sheet 2) populates 29 variety rows
- AC-W3-05 — L49 vs L03/L04 diff resolved (no duplicate insertions)
- AC-W3-06 — Tend 2018 decision documented in REMEDIATION_REPORT
- AC-W3-07 — Reconciler blend stability after all sources loaded
- AC-W3-08 — Multi-source CALIBRATED count grows by ≥10
- AC-W3-09 — Tests ≥12
- AC-W3-10 — validate_aos.sh remains clean

### Estimated build effort
- Spec authoring: 1 session
- Build: 2 sessions (OCR setup + per-source variation)
- Validate: 1 session
- Total: ~4 sessions

---

## Cross-wave dependency diagram

```
WP-B program (DONE — LOD500_LOCKED at tag S003-P002-WP-B-v1.0.0)
        │
        ▼
   Wave 1 (C1) — tabular ingestion         ◀── HIGH priority, LOW risk
   ├─ planting calendar (L01, L36)
   ├─ Idan planning (L03, L04)
   ├─ Cover crops chart (L12)
   └─ Tend 2019, 2020, 2021 backfill
        │
        ▼
   Wave 2 (C2) — Hebrew narrative NI       ◀── HIGH priority, MEDIUM risk
   ├─ AOSNOT encyclopedia (L02)
   ├─ Variety trials (L11)
   ├─ Hydro guides (L09, L10)
   └─ JMF FT extensions (L13, L14, L16)
        │
        ▼
   Wave 3 (C3) — Secondary + OCR           ◀── LOWER priority
   ├─ Curtis Stone (L40, L41 OCR)
   ├─ Idan seedlings (L05ab) + 2018 (L49)
   ├─ FRANCHI catalog (L06 sheet 2)
   └─ Investigate-or-defer items
```

Waves can be **parallelized** between WP-C1 (tabular) and WP-C2 (narrative LLM)
since they touch different layers (relational vs. text). WP-C3 must wait for
WP-C1 (needs Tend baseline) and benefits from WP-C2 (Curtis cross-validates).

---

## Per-wave deliverable timeline

| Wave | Spec | Build | Validate | Close | Total (sessions) |
|------|:---:|:---:|:---:|:---:|:---:|
| C1 (tabular) | 1 | 1-2 | 1 | 0.5 | **~4** |
| C2 (Hebrew NI) | 1-2 | 2-3 | 1 | 0.5 | **~5** |
| C3 (OCR + backlog) | 1 | 2 | 1 | 0.5 | **~4** |
| **Total program** | 3-4 | 5-7 | 3 | 1.5 | **~13 sessions** |

If C1 and C2 run in parallel (different team_110 sessions): timeline ~8 sessions total.

---

## Recommendation

**Proceed with Wave 1 (WP-C1) first.** Reasons:
1. Lowest risk (no LLM, no OCR, no PDF parsing of narrative)
2. Largest immediate DB delta (4× Tend years; 2 new structured Israeli sources)
3. Unblocks calibration: more OP/PR data means `validate_enrichment.py` shadow
   run yields more CALIBRATED rows = visible improvement
4. Builds importer patterns that Waves 2/3 can extend

After Wave 1 LOD500_LOCKED → assess gap residue → launch Wave 2 + 3 in parallel.

---

*Generated by team_10 / Claude Sonnet 4.7 — 2026-05-26.
Execution delegated to team_110 (separate session under future EXECUTION_MANDATE).*
