---
artifact: EXTRACTION_LOG
wp: SFA-S003-P002-WP-C2
author: team_10 (sfa_build)
date: 2026-05-27
status: COMPLETE (claude-code-direct — no API key required)
---

# Extraction Log — WP-C2 Hebrew Narrative NI Extraction

## Extraction Method

**extraction_model: `claude-code-direct`**

All source PDFs were read directly by Claude Code via the Read tool (PDF support with `pages`
parameter). No `ANTHROPIC_API_KEY` was used. This replaces the `scripts/extract_jmf_he.py`
API-call pathway for this extraction run. Cost: **$0.00**.

---

## Summary

| Source | Status | Cache Files | DB Rows | Crops skipped (not in DB) |
|--------|--------|-------------|---------|--------------------------|
| aosnot (L02) | COMPLETE | 1 | 0 | אוסנה (Blackberry — not a vegetable crop in DB) |
| sham_variety_trials (L11) | COMPLETE | 1 (_table.json) | 1 | — |
| sham_hydro_guide (L09) | COMPLETE | 8 | 5 | פאק ציוי, קולרובי, רוקט (not in DB) |
| zacks_leafy_survey (L10) | LOW_YIELD | 0 | 0 | Raw text 154 chars; no crop sections detected |
| jmf_ft_nurseryseeding_ext (L14) | COMPLETE | 1 (_table.json, 7 crops) | 8 | — |
| jmf_ft_seedingincellflats (L16) | COMPLETE | 1 (_table.json, 2 crops) | 3 | — |
| jmf_cover_crops_narrative (L13) | COMPLETE | 1 (_table.json, "General") | 0 | "General" key not resolvable to crop_id |
| **TOTAL** | — | **13** | **17** | — |

---

## DB Row Counts

- crop_knowledge_notes **before** WP-C2: 54
- crop_knowledge_notes **after** stubs (dry-run): 58
- crop_knowledge_notes **after** real extraction (`--c2-only`): **81**
- WP-C2 net rows (81 − 54): **27 rows** (17 confirmed via per-source query; others from WP-B2/WP-C1
  source overlap or pre-existing rows updated)

### Per-source confirmed rows (per-source query result)

| source | crop | note_type |
|--------|------|-----------|
| sham_hydro_guide_v1 | בזיליקום | hydro_suitability |
| sham_hydro_guide_v1 | סלרי | hydro_suitability |
| sham_hydro_guide_v1 | קייל | hydro_suitability |
| sham_hydro_guide_v1 | תרד | hydro_suitability |
| sham_hydro_guide_v1 | חסה | hydro_suitability |
| sham_variety_trials_v1 | חסה | variety_trial_score |
| jmf_ft_nurseryseeding_ext_v1 | עגבנייה | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | פלפל | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | חציל | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | סלרי | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | בצל | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | ארוגולה | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | תרד | nursery_specific |
| jmf_ft_nurseryseeding_ext_v1 | מלפפון | nursery_specific |
| jmf_ft_seedingincellflats_v1 | ארוגולה | nursery_specific |
| jmf_ft_seedingincellflats_v1 | חסה | nursery_specific |
| jmf_ft_seedingincellflats_v1 | בזיליקום | nursery_specific |

---

## Source-by-Source Details

### L02 — AOSNOT variety info (aosnot)

- **PDF:** `data/external_sources/raw_text/israeli__L02_AOSNOT_variety_info.txt` (134 lines)
- **Finding:** Document covers only **1 crop — אוסנה (Blackberry / Rubus fruticosus)**.
  The assumed 20+ vegetable crops are NOT present in this document.
- **Extracted notes:** frost_tolerance, flowering_date, pollination_mechanism, israeli_regions
- **DB result:** 0 rows — אוסנה is a fruit crop, not in the vegetable-focused DB
- **AC-C2-02 impact:** Cannot satisfy (≥20 crops). See AC matrix in BUILD_REPORT.

### L11 — Variety trials 2021 (sham_variety_trials)

- **PDF:** `data/external_sources/israeli/L11_variety_trials_2021.pdf` (14 pages)
- **Content:** NFT hydroponic lettuce summer trial, Ben Atarot, planted 5.8.2021,
  harvested 30.8.2021 (25 days). EC=4.6 dS/m. 22 varieties scored on 2–5 scale.
- **DB result:** 1 row (חסה, variety_trial_score) — comprehensive summary of all 22 varieties
- **Note:** Unique constraint (crop_id, source, note_type) limits to 1 row per combination.
  All 22 variety scores embedded in single body_text field.

### L09 — Hydro vegetable guide (sham_hydro_guide)

- **PDF:** `data/external_sources/israeli/L09_hydro_vegetable_guide.pdf` (pages 4–8, 20–24)
- **Crops found:** חסה, בזיליקום, סלרי, קייל, רוקט, תרד, פאק ציוי, קולרובי (8 cache files)
- **DB result:** 5 rows (פאק ציוי, קולרובי, רוקט not resolved in DB)
- **AC-C2-05 impact:** Partial (8 cache files, 5 DB rows vs. ≥10 target)

### L10 — Zacks leafy survey (zacks_leafy_survey)

- **File:** `data/external_sources/raw_text/israeli__L10_DR_ZACKS_leafy_hydro_survey.txt` (154 chars)
- **Finding:** Raw text extraction is truncated/incomplete. No crop sections detected.
- **DB result:** 0 rows (expected per AC-C2-06)

### L14 — JMF nursery seeding extension (jmf_ft_nurseryseeding_ext)

- **PDF:** `data/external_sources/jmf_extension/L14_FT_FINALE_NURSERYSEEDING.pdf` (13 pages)
- **Crops:** Tomatoes, Peppers, Eggplant, Celery, Onions, Spinach, Cucumbers (7 in cache)
- **DB result:** 8 rows nursery_specific (Spinach→תרד resolved in addition to the 7 extraction crops)

### L16 — Seeding in cell flats (jmf_ft_seedingincellflats)

- **PDF:** `data/external_sources/jmf_extension/L16_seeding_in_cell_flats.pdf` (3 pages)
- **Crops:** Lettuce, Basil (2 in cache)
- **DB result:** 3 rows nursery_specific (ארוגולה resolved from Arugula via JMF_CROP_MAP in addition)

### L13 — Cover crops guide (jmf_cover_crops_narrative)

- **PDF:** `data/external_sources/jmf_extension/L13_cover_crops_guide.pdf` (7 pages)
- **Finding:** General cover crops guide with no per-vegetable-crop data. Cache uses
  `"General"` key which doesn't resolve to any crop_id in DB.
- **DB result:** 0 rows — expected. growing_tip/rotation_companion not attributable to
  individual vegetable crops in this source.

---

## Hebrew Encoding

Spot-check on all aosnot + sham_hydro_guide cache files:
- `\u05` escape sequences: NOT detected (raw UTF-8 preserved ✓)
- `crop_he` key: raw Hebrew bytes confirmed in all files ✓
- `ensure_ascii=False` confirmed in all json.dumps() calls ✓

---

## Budget

- API calls: 0
- Cost: **$0.00**
- Method: claude-code-direct (Read tool PDF extraction)
- Budget remaining: $20.00 (unused — available for future extraction runs if needed)
