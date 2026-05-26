---
id: SFA-S003-P002-WP-C2-LOD200
wp: SFA-S003-P002-WP-C2 — Hebrew Narrative Extraction (NI tier)
gate: L-GATE_S (LOD200 — architecture spec)
status: LOD200_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-A
  - SFA-S003-P002-WP-B (LOD500_LOCKED)
depends_on: [SFA-S003-P002-WP-B]
parallel_eligible_with: SFA-S003-P002-WP-C1
brief_ref: data/external_sources/WAVE_PLAN_v1.0.0.md
---

# LOD200 — WP-C2: Hebrew Narrative Extraction (NI tier)

## 1. Mission

Apply the WP-B2 NIImporter pattern to Hebrew authoritative sources. LLM-assisted
extraction (Anthropic API, one-time prepare step with caching) of per-crop
narrative knowledge from 7 sources into the existing `crop_knowledge_notes`
table (+ extended `note_type` enum).

## 2. In-scope

- **Migration 049** — extend `crop_knowledge_notes.note_type` CHECK with 6 new enum values: `frost_tolerance`, `flowering_date`, `pollination_mechanism`, `israeli_regions`, `variety_trial_score`, `hydro_suitability`
- **New concrete NIImporter subclasses** under `organic_market_agent/crop_book/importer/ni/`:
  - `aosnot_variety_info.py` (L02 — 1.3MB DOCX Hebrew encyclopedia)
  - `sham_variety_trials.py` (L11 — שה"מ official variety trial)
  - `sham_hydro_guide.py` (L09 — שה"מ hydro manual)
  - `zacks_leafy_survey.py` (L10 — Dr. Zacks IL leafy survey)
  - `jmf_ft_nurseryseeding.py` (L14 — extends WP-B2)
  - `jmf_ft_seedingincellflats.py` (L16)
  - `jmf_cover_crops_narrative.py` (L13 — companion narrative to L12 chart from C1)
- **Extraction harness** at `scripts/extract_jmf_he.py` (multi-source dispatcher) — outputs to `data/external_sources/extracted/<source>/<crop>.json`
- **Hebrew prompt tuning** for Anthropic API (RTL handling, encoding preservation)
- **CLI**: `seed.py --c2-only`, `--no-c2`; integrate into `--all` (NI runs LAST = hard-override winner)
- **Tests** ≥15

## 3. Out-of-scope

- Re-extraction at runtime (cache-only path)
- Italian Libretto Orto (L38, deferred — wave 4 / never)
- L26 (already determined to be a bank receipt, not Hebrew JMF)
- Modifying WP-B2 cache structure (extend, not replace)
- Publication of extracted prose (internal farm-use only per WP-B2 advisory #1)

## 4. Data sources (all in `data/external_sources/`)

| Code | Path | Type | Pages |
|------|------|------|------|
| L02 | `israeli/L02_AOSNOT_variety_info.docx` | DOCX | 1.3MB (~30-50 crops) |
| L11 | `israeli/L11_variety_trials_2021.pdf` | PDF | 14 |
| L09 | `israeli/L09_hydro_vegetable_guide.pdf` | PDF | 24 |
| L10 | `israeli/L10_DR_ZACKS_leafy_hydro_survey.pdf` | PDF | 52 |
| L14 | `jmf_extension/L14_FT_FINALE_NURSERYSEEDING.pdf` | PDF | 13 |
| L16 | `jmf_extension/L16_seeding_in_cell_flats.pdf` | PDF | 3 |
| L13 | `jmf_extension/L13_cover_crops_guide.pdf` | PDF | 7 |

## 5. Data model summary

### 5.1 Migration 049 — extend `crop_knowledge_notes.note_type` enum

```sql
ALTER TABLE crop_knowledge_notes DROP CONSTRAINT ck_ckn_note_type;
ALTER TABLE crop_knowledge_notes ADD CONSTRAINT ck_ckn_note_type
  CHECK (note_type IN (
    -- original 10 from WP-B2
    'pest_disease', 'harvest_marker', 'storage_handling',
    'rotation_companion', 'cultivar_recommendation', 'growing_tip',
    'irrigation', 'nursery_specific', 'flame_weed_timing',
    'biopesticide_spray',
    -- NEW 6 from C2
    'frost_tolerance', 'flowering_date', 'pollination_mechanism',
    'israeli_regions', 'variety_trial_score', 'hydro_suitability'
  ));
```

### 5.2 Extracted JSON cache schema

`data/external_sources/extracted/aosnot/<crop_he>.json`:
```json
{
  "source": "NI:aosnot",
  "crop_he": "אוסנה",
  "crop_en": "Blackberry",
  "extracted_at": "2026-05-27T...",
  "extraction_model": "claude-sonnet-4.7",
  "notes": [
    {"note_type": "frost_tolerance", "body": "עמיד לקור"},
    {"note_type": "israeli_regions", "body": "כל האזורים"},
    {"note_type": "flowering_date", "body": "אביב אפריל-יוני"},
    {"note_type": "pollination_mechanism", "body": "דבורים"},
    {"note_type": "pest_disease", "body": "ציפורים, חתולים"},
    {"note_type": "growing_tip", "body": "..."}
  ]
}
```

## 6. Trust-layer placement

All sources: `trust_tier='NI'`, `confidence_weight=NULL`, `is_hard_override=True`.
Source labels: `NI:aosnot`, `NI:sham_variety_trials_2021`, `NI:sham_hydro_guide`,
`NI:zacks_leafy_survey`, `NI:jmf_ft_nurseryseeding`, `NI:jmf_ft_seedingincellflats`,
`NI:jmf_cover_crops_narrative`.

## 7. Dependencies

- Hard: WP-A engine, WP-B2 (existing `crop_knowledge_notes` table + NIImporter skeleton)
- Soft: WP-C1 (Israeli structured data helps cross-validate Hebrew narrative claims)

## 8. LOD500_LOCKED untouched

Same as C1 LOD200 §8. Additionally: WP-B2's `crop_knowledge_notes` table is
LOD500_LOCKED — but the migration 049 `ALTER` to add CHECK enum values is an
explicit additive extension permitted under the WP-B2 spec amendment pattern
(team_00 to confirm in BUILD).

## 9. GCR requirements

**NONE.** Migration 049 is additive (extends CHECK enum); no relationship
changes to `Crop` model. Same path as WP-B2.

## 10. AC count target: 12

## 11. Test count target: 15

## 12. Open questions

1. **L10 Zacks survey (52pp)** — needs first deep peek; may be hydro-only and add
   limited value. team_10 to report after pdftotext full extraction.
2. **Hebrew RTL in LLM extraction** — confirm Anthropic API correctly preserves
   Hebrew without encoding drift. Use ASCII-safe `body_text` storage.
3. **L02 AOSNOT crop count** — file is 1.3MB; estimate ~30-50 crops. Confirm
   by section count before mandate dispatch.

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.
LOD400 to be authored before activation OR by team_110 in execution mode.*
