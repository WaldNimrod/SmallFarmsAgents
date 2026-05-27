---
artifact: EXTRACTION_LOG
wp: SFA-S003-P002-WP-C2
author: team_10 (sfa_build)
date: 2026-05-27
status: STUB_ONLY (real extraction pending API key)
---

# Extraction Log — WP-C2 Hebrew Narrative NI Extraction

## Summary

| Source | Status | Files | Token cost | Notes |
|--------|--------|-------|------------|-------|
| aosnot (L02) | STUB_DRY_RUN | 1 | $0.00 | API key missing; 1 stub crop (אוסנה) |
| sham_variety_trials (L11) | STUB_DRY_RUN | 1 | $0.00 | 1 stub crop (חסה), _table.json |
| sham_hydro_guide (L09) | STUB_DRY_RUN | 1 | $0.00 | 1 stub crop (חסה) |
| zacks_leafy_survey (L10) | STUB_DRY_RUN | 0 | $0.00 | Low-yield: raw text 154 chars, no sections detected |
| jmf_ft_nurseryseeding_ext (L14) | STUB_DRY_RUN | 1 | $0.00 | 1 stub crop (Arugula), _table.json |
| jmf_ft_seedingincellflats (L16) | STUB_DRY_RUN | 1 | $0.00 | 1 stub crop (Arugula), _table.json |
| jmf_cover_crops_narrative (L13) | STUB_DRY_RUN | 1 | $0.00 | 2 stub crops (Clover, Buckwheat), _table.json |
| **TOTAL** | — | **6** | **$0.00** | — |

## DB Row Counts (post stub ingestion)

- crop_knowledge_notes total: 58 (was 54 pre-WP-C2; +4 from stub stubs)
- WP-C2 rows: 4 (sham_variety_trials:1, sham_hydro_guide:1, jmf_ft_nurseryseeding_ext:1, jmf_ft_seedingincellflats:1)

## Hebrew Encoding

Spot-check on `data/external_sources/extracted/aosnot/אוסנה.json`:
- `\\u05` escape: NOT detected (raw UTF-8 preserved ✓)
- `crop_he`: `אוסנה` (raw UTF-8) ✓

## Pending (requires ANTHROPIC_API_KEY)

Real extraction targets per AC matrix:
- AC-C2-02: L02 AOSNOT ≥20 crop JSONs → `--source aosnot --all`
- AC-C2-03: frost_tolerance/israeli_regions/flowering_date ≥80% of crops
- AC-C2-04: L11 ≥5 lettuce variety_trial_score rows → `--source sham_variety_trials`
- AC-C2-05: L09 ≥10 hydro_suitability crops → `--source sham_hydro_guide`
- AC-C2-07: L14/L16/L13 nursery_specific + growing_tip → `--source jmf_ft_*`

See INQUIRY_API_KEY_v1.0.0.md for extraction commands and budget details.

## Budget Status

- Spent: $0.00
- Remaining: $20.00
- Log file: `data/external_sources/extracted/_extraction_log.json` (will be updated on real run)
