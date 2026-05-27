---
artifact: BUILD_REPORT
wp: SFA-S003-P002-WP-C2
title: "WP-C2: Hebrew Narrative NI Extraction — BUILD_COMPLETE (extraction pending)"
author: team_10 (sfa_build — Claude Sonnet 4.6)
date: 2026-05-27
status: BUILD_COMPLETE_EXTRACTION_PENDING
gate_next: L-GATE_V (team_190, after real extraction + ingestion)
---

# BUILD_REPORT — SFA-S003-P002-WP-C2

## Summary

All code construction for WP-C2 is complete. The one-time LLM extraction phase is **BLOCKED
on `ANTHROPIC_API_KEY`** (see `INQUIRY_API_KEY_v1.0.0.md`). All infrastructure is ready to run
extraction immediately once the key is provided.

## Acceptance Criteria Status

| AC | Description | Status | Note |
|----|-------------|--------|------|
| AC-C2-01 | Migration 053 applies on PG (SQLite-safe skip) | ✅ PASS | Applied: 052 → 053 |
| AC-C2-02 | L02 ≥20 crop JSONs in extracted/aosnot/ | ⏳ PENDING | Needs API key |
| AC-C2-03 | L02 per-crop coverage ≥80% (frost_tolerance, israeli_regions, flowering_date) | ⏳ PENDING | Needs API key |
| AC-C2-04 | L11 ≥5 lettuce variety_trial_score rows | ⏳ PENDING | Needs API key |
| AC-C2-05 | L09 ≥10 crops hydro_suitability | ⏳ PENDING | Needs API key |
| AC-C2-06 | L10 Zacks documented or low-yield noted | ✅ PASS | 154-char raw text; documented as low-yield |
| AC-C2-07 | L14/L16/L13 nursery_specific + growing_tip | ⏳ PENDING | Needs API key |
| AC-C2-08 | All extractions cached; runtime reads cache only | ✅ PASS | No API call at import time |
| AC-C2-09 | Hebrew preserved: no `\uXXXX` escapes | ✅ PASS | Test + spot-check verified |
| AC-C2-10 | NI hard-override semantics preserved | ✅ PASS | trust_tier=NI, reconcile_field rejects blend |
| AC-C2-11 | Tests ≥15 | ✅ PASS | 17 tests, all PASS |
| AC-C2-12 | validate_aos.sh: 29/19/0 | ✅ PASS | Verified post-build |

## Files Created / Modified

### New files
- `organic_market_agent/db/versions/053_extend_ckn_note_type.py` — migration 053
- `scripts/extract_jmf_he.py` — extraction harness (7 sources, $20 budget cap)
- `organic_market_agent/crop_book/importer/ni/aosnot_variety_info.py`
- `organic_market_agent/crop_book/importer/ni/sham_variety_trials.py`
- `organic_market_agent/crop_book/importer/ni/sham_hydro_guide.py`
- `organic_market_agent/crop_book/importer/ni/zacks_leafy_survey.py`
- `organic_market_agent/crop_book/importer/ni/jmf_ft_nurseryseeding_ext.py`
- `organic_market_agent/crop_book/importer/ni/jmf_ft_seedingincellflats.py`
- `organic_market_agent/crop_book/importer/ni/jmf_cover_crops_narrative.py`
- `tests/crop_book/test_c2_migration.py` (2 tests)
- `tests/crop_book/test_c2_aosnot_cache_schema.py` (3 tests)
- `tests/crop_book/test_c2_aosnot_importer.py` (3 tests)
- `tests/crop_book/test_c2_sham_variety_trials.py` (2 tests)
- `tests/crop_book/test_c2_sham_hydro_guide.py` (2 tests)
- `tests/crop_book/test_c2_zacks_leafy_survey.py` (1 test)
- `tests/crop_book/test_c2_jmf_ft_importers.py` (4 tests)
- `_COMMUNICATION/team_10/SFA-S003-P002-WP-C2/INQUIRY_API_KEY_v1.0.0.md`
- `_COMMUNICATION/team_10/SFA-S003-P002-WP-C2/EXTRACTION_LOG_v1.0.0.md`
- `data/external_sources/extracted/` (stub JSONs from --dry-run)

### Modified (APPEND-only)
- `organic_market_agent/crop_book/crop_knowledge_notes.py` — NOTE_TYPE_VALUES 13 → 19
- `organic_market_agent/crop_book/importer/ni/__init__.py` — added NI_C2_IMPORTER_CLASSES
- `organic_market_agent/crop_book/importer/seed.py` — _run_c2_ingestion, --c2-only, --no-c2
- `tests/crop_book/test_crop_knowledge_notes_orm.py` — updated count assertion 13 → 19

## Key Design Decisions

1. **Naming conflict resolution (jmf_ft_nurseryseeding.py):** WP-B2 already created
   `jmf_ft_nurseryseeding.py` (produces `nursery_seeding_process`). WP-C2 creates
   `jmf_ft_nurseryseeding_ext.py` (produces `nursery_specific`) — distinct source label
   `NI:jmf_ft_nurseryseeding_ext_v1`. Both coexist without conflict.

2. **NI_C2_IMPORTER_CLASSES tuple** appended to `ni/__init__.py` separately from
   `NI_IMPORTER_CLASSES` (WP-B2). No WP-B2 entries touched.

3. **Hebrew crop resolution:** `IL_CROP_MAP.get(crop_he, crop_he)` normalization + fallback
   direct `name_he` lookup for all Hebrew-keyed sources.

4. **L10 Zacks low-yield:** Raw text file is 154 chars (truncated extract). Documented as
   low-yield per AC-C2-06. Importer returns [] gracefully.

## Test Results

```
tests/crop_book/test_c2_*.py — 17 passed
Full suite: 723 passed, 1 pre-existing admin fail, 14 skipped
```

## Post-Extraction Steps (requires API key)

1. `python3 scripts/extract_jmf_he.py --source aosnot --all` (L02 — HIGHEST PRIORITY)
2. `python3 scripts/extract_jmf_he.py --source all` (remaining 6 sources)
3. `python3 -m organic_market_agent.crop_book.importer.seed --c2-only`
4. Verify crop_knowledge_notes ≥200 rows
5. Re-verify AC-C2-02 through AC-C2-07

## LOD500_LOCKED Audit

All LOD500_LOCKED files verified UNTOUCHED:
- ✅ reconciler.py (engine v1.1 FROZEN)
- ✅ enrichment_runner.py
- ✅ views.py
- ✅ publisher/wp_upload.py, upload_dispatch.py
- ✅ migrations 001–052
- ✅ crop_book/importer/tend.py
- ✅ crop_book/models.py
- ✅ mu-plugin/

team_10 / sfa_build (Claude Sonnet 4.6)
SFA-S003-P002-WP-C2 BUILD_COMPLETE
2026-05-27
