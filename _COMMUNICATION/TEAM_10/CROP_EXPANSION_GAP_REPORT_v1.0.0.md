---
artifact: CROP_EXPANSION_GAP_REPORT
author: team_10 (sfa_build)
date: 2026-05-27
status: COMPLETE
related_mandate: _COMMUNICATION/TEAM_80/MANDATE_CROP_EXPANSION_16_CROPS_v1.0.0.md
---

# Crop Expansion Gap Report — 16 New Crops

## Background

Following WP-C2 extraction and the discovery of 4 alias gaps in IL_CROP_MAP,
team_00 directed team_10 to:
1. Add Blackberry (אוסנה) — ✅ added (id=61)
2. Verify Cherry Tomato (עגבניית שרי) — was missing; ✅ added (id=73)
3. Add all remaining crops from the IL_CROP_MAP gap list

This report documents all 16 crops added in this session and their current
data coverage.

---

## DB Changes (this session)

### New CropFamily
| id | scientific_name | name_he |
|----|----------------|---------|
| 24 | Pedaliaceae | שומשומיים |

### New Crops

| id | name_he | name_en | scientific_name | family_id | category |
|----|---------|---------|----------------|-----------|----------|
| 61 | אוסנה | Blackberry | Rubus fruticosus | 19 (ורדיים) | fruits |
| 73 | עגבניית שרי | Cherry Tomato | Solanum lycopersicum var. cerasiforme | 21 (סולניים) | fruits |
| 74 | אבטיח | Watermelon | Citrullus lanatus | 11 (דלועיים) | fruits |
| 75 | כרובית | Cauliflower | Brassica oleracea var. botrytis | 8 (מצליבים) | vegetables |
| 76 | בטטה | Sweet Potato | Ipomoea batatas | 18 (לשוניתניים) | vegetables |
| 77 | במיה | Okra | Abelmoschus esculentus | 15 (חלמיתיים) | vegetables |
| 78 | פול | Fava Bean | Vicia faba | 12 (קטניות) | vegetables |
| 79 | ציקוריה | Chicory | Cichorium intybus | 7 (מורכבים) | vegetables |
| 80 | תירס | Sweet Corn | Zea mays | 17 (דשאיים) | vegetables |
| 81 | תפוח אדמה | Potato | Solanum tuberosum | 21 (סולניים) | vegetables |
| 82 | חומוס | Chickpea | Cicer arietinum | 12 (קטניות) | vegetables |
| 83 | שומשום | Sesame | Sesamum indicum | 24 (שומשומיים) | herbs |
| 84 | חמניה | Sunflower | Helianthus annuus | 7 (מורכבים) | vegetables |
| 85 | חיטה | Wheat | Triticum aestivum | 17 (דשאיים) | vegetables |
| 86 | סויה | Soybean | Glycine max | 12 (קטניות) | vegetables |
| 87 | אדממה | Edamame | Glycine max (edamame) | 12 (קטניות) | vegetables |

**Total crops in DB: 73** (was 57 before this session)

### IL_CROP_MAP Aliases Added (constants.py)

| source key | → canonical |
|-----------|-------------|
| "אוסנה" | "אוסנה" |
| "רוקט" | "ארוגולה" |
| "פאק ציוי" / "פאק צוי" | "פאק צ'וי" |
| "קולרובי" | "קולורבי" |

---

## Data Gap Summary

All 16 new crops have **zero data** in `crop_variety_source_values`
and `crop_knowledge_notes`. Existing WP-C2 extractions produced:

- **אוסנה (id=61):** 4 knowledge_notes from aosnot (frost_tolerance,
  flowering_date, pollination_mechanism, israeli_regions). No source_values.

All others: 0 source_values, 0 knowledge_notes.

### Fields needed per crop (Priority A — critical for planner)

| field | description |
|-------|-------------|
| days_to_maturity | days transplant/seed → harvest |
| in_row_spacing_cm | plant spacing in row |
| rows_per_bed | rows on 75–90 cm bed |
| planting_method | transplant / direct |
| yield_per_m2_kg | kg per m² |
| avg_yield_per_bed_m | kg per bed metre |

### Fields needed per crop (Priority B — scheduling/seed ordering)

| field | description |
|-------|-------------|
| seeds_per_gram | seed count per gram |
| germination_temp_c_opt | optimal germination temp (°C) |
| frost_tolerance_class | hardy / half_hardy / tender |
| harvest_window_max_days | days between first and last harvest |
| succession_interval_weeks | weeks between successions |
| soil_ph_target | target soil pH |

---

## Team 80 Mandate

Mandate issued: `_COMMUNICATION/TEAM_80/MANDATE_CROP_EXPANSION_16_CROPS_v1.0.0.md`

- **SLA:** 5 working days
- **Budget:** $10
- **Priority order:** Tier 1 (Cherry Tomato, Cauliflower, Sweet Potato, Okra, Fava Bean)
  → Tier 2 → Tier 3
- **Expected response:** `CROP_DATA_FINDINGS_16_CROPS_v1.0.0.md`

---

## Next Steps (after Team 80 delivers)

1. Review team_80 findings for source credibility
2. Write WP-D (or C3-ext) to ingest findings into `crop_variety_source_values`
   via new NI importer(s) or manual seed entries
3. Re-run validate_aos.sh and route to L-GATE_V

team_10 / sfa_build
2026-05-27
