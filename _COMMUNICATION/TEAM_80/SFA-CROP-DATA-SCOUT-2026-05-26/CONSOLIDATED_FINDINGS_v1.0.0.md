---
id: CONSOLIDATED_FINDINGS_SFA-CROP-DATA-SCOUT_2026-05-26_v1.0.0
from: team_10 (consolidation by Claude Sonnet 4.7)
to: team_00 + team_110
date: 2026-05-26
engines_used: [OpenAI ChatGPT, Perplexity, Gemini]
input_findings:
  - OpenAI: 8 candidates  (5 INGEST + 1 SKIP + 2 INVESTIGATE)
  - Perplexity: 10 candidates  (8 INGEST + 0 SKIP + 2 INVESTIGATE)
  - Gemini: 7 candidates  (5 INGEST + 0 SKIP + 2 INVESTIGATE) [truncated by user]
consolidated_candidates: 11 unique groups
final_ingest: 8 groups
final_investigate: 3 groups
---

# Consolidated Findings — Web Sources Scout (Multi-Engine)

team_80 ran on 3 engines in parallel. This document merges all findings, de-duplicates
sources covering the same gap, and produces the canonical candidate list for WP-C4.

**Multi-engine value confirmed:**
- **3/3 consensus** on germination temp, frost tolerance, NPK nutrient removal, postharvest storage
- **2/3 consensus** on soil pH, ECOCROP investigate, seeds-per-gram, **Israeli MoA sources**
- **OpenAI explicitly admitted** it could not find authoritative Israeli sources;
  **Perplexity + Gemini found 2-3 Israeli candidates** — proves the multi-engine
  approach paid off precisely where it was most needed.

---

## Cross-engine consensus matrix

| Gap | OpenAI | Perplexity | Gemini | Consensus | Selected source |
|-----|:------:|:----------:|:------:|:---------:|-----------------|
| **Germination temperature** | CS-01 UC ANR HTML | CS-01 UC ANR PDF | CS-01 Purdue/UC ANR | **3/3 INGEST** | UC ANR PDF + Purdue cross-val |
| **Frost tolerance class** | CS-03 CSU + CS-04 UMN | CS-02 OSU | CS-04 OSU | **3/3 INGEST** | OSU primary + CSU/UMN cross-val |
| **Soil pH preference** | CS-02 UMD | CS-03 UMD | (not found) | **2/3 INGEST** | UMD B-1.pdf |
| **NPK nutrient removal** | CS-05 NE Veg Guide | CS-07 FAO Fertilizer | CS-02 NE Veg Guide | **3/3 INGEST** | NE Veg Guide primary + FAO supp |
| **Postharvest storage** | CS-06 UC Davis Cantwell | CS-08 UMaine | CS-07 UC Davis | **3/3 INGEST** | UC Davis Cantwell |
| **Seeds per gram** | (not found) | CS-04 Vital Seeds | CS-03 Osborne | **2/3 INGEST** | Cross-validate Vital + Osborne |
| **Companion planting** | (not found) | CS-05 UF/IFAS | (not found) | **1/3 INGEST** | UF/IFAS |
| **Israeli planting calendar** | ❌ NONE FOUND (admitted) | CS-10 MoA + CS-09 HaGina | CS-05 Shaham (MoAG) | **2/3 INGEST + 1/3 INVESTIGATE** | **CRITICAL** — multi-engine win |
| **Mediterranean varieties** | (not found) | (not found) | CS-06 Cornell Veg Varieties | **1/3 INVESTIGATE** | Cornell — secondary |
| **FAO ECOCROP** | CS-07 INVESTIGATE | CS-06 INVESTIGATE | (not found) | **2/3 INVESTIGATE** | Defer — high effort |
| **EPPO pest taxonomy** | CS-08 INVESTIGATE | (not found) | (not found) | **1/3 INVESTIGATE** | Defer — low priority |

---

## Consolidated candidate list (final, by priority)

### 🟢 TIER A — INGEST IMMEDIATELY (HIGH-gap fill, multi-engine consensus)

#### CW-01 — Germination Temperature (UC ANR + Purdue cross-validated)
- **Primary URL**: `https://ucanr.edu/sites/default/files/2017-11/164220.pdf` (UC ANR Garden Notes 164220 — PDF chart)
- **Cross-validation URL**: `https://ag.purdue.edu/department/hla/extension/extension-publications-library/ext-pubs/ho-186-w.html` (Purdue HO-186-W)
- **Format**: PDF table → unit-convert °F to °C → upsert to `crop_variety_source_values` with field_names `germination_temp_c_min`, `germination_temp_c_opt`, `germination_temp_c_max`
- **Source label**: `PR:uc_anr_germination` (PR tier, 0.70)
- **Cross-validation strategy**: if Purdue diverges by ≥3°C from UC ANR, log + investigate
- **Coverage**: ~30 vegetable crops
- **License**: terms_of_use (educational; cite UC ANR)

#### CW-02 — Frost Tolerance Class (OSU + CSU + UMN consolidated)
- **Primary URL**: OSU frost tolerance chart (Perplexity CS-02)
- **Cross-validation**: CSU Vegetable Planting Guide (OpenAI CS-03), UMN Crop Field Planning (OpenAI CS-04)
- **Format**: HTML/PDF → derive single `frost_tolerance_class` per crop: `hardy` / `semi_hardy` / `tender` / `very_tender`
- **Field target**: `frost_tolerance_class` in `crop_variety_source_values`
- **Source label**: `PR:osu_frost_tolerance` (PR tier)
- **Cross-engine reconciliation**: if 2/3 sources agree on a class, accept; if all 3 disagree, default to `tender` + log

#### CW-03 — Soil pH Targets (UMD)
- **URL**: `https://extension.umd.edu/sites/extension.umd.edu/files/2021-03/B-1.pdf`
- **Format**: 1-page PDF table → `soil_ph_target` + `soil_ph_liming_threshold`
- **Coverage**: ~40 vegetable/fruit crops
- **Source label**: `PR:umd_soil_ph` (PR tier)

#### CW-04 — NPK Nutrient Removal (NE Veg Guide + FAO supplement)
- **Primary URL**: `https://nevegetable.org/cultural-practices/removal-nutrients-soil` (New England Vegetable Guide)
- **Supplement URL**: FAO Fertilizer use by crop bulletin (Perplexity CS-07)
- **Format**: HTML table → unit convert (lbs/A → kg/ha) → fields `nutrient_removal_n_kg_ha`, `nutrient_removal_p_kg_ha`, `nutrient_removal_k_kg_ha`, `nutrient_removal_ca_kg_ha`, `nutrient_removal_mg_kg_ha`
- **Coverage**: ~20 vegetable crops
- **Source label**: `PR:ne_veg_guide` (PR tier)
- **Note**: nutrient removal ≠ fertilizer recommendation; store with `assumed_yield_t_ha` context

### 🟢 TIER B — INGEST CRITICAL (Israeli gap-fill — multi-engine win)

#### CW-05 — Israeli Ministry of Agriculture sources (Perplexity + Gemini)
- **Primary URL**: Israeli MoA home vegetable garden guide (Perplexity CS-10) — confirms Israel planting calendar + basic crop requirements
- **Supplement URL**: Shaham (שה"ם, MoAG Extension Service — Gemini CS-05) — government-authoritative
- **Format**: Likely PDF/HTML hybrid; need pdfplumber + scraping
- **Field target**: Extend `crop_planting_calendar` (from C1) with `region='IL_general'`; add `israeli_regions` notes to `crop_knowledge_notes` (NI tier)
- **Source labels**: `NI:il_moa_garden_guide`, `NI:shaham_extension`
- **Hebrew handling**: same RTL/UTF-8 preservation as WP-C2 pattern
- **HIGH PRIORITY** — this is the gap OpenAI explicitly failed to fill but two other engines succeeded on. Validates the multi-engine investment.

### 🟡 TIER C — INGEST SECONDARY (single-engine but valuable)

#### CW-06 — Seeds per Gram (Vital Seeds + Osborne)
- **Vital Seeds URL** (Perplexity CS-04): seeds-per-gram table
- **Osborne URL** (Gemini CS-03): seed count reference
- **Cross-validation**: if both sources cover same crop, use median; if only one, use as-is
- **Format**: HTML tables (likely commercial — confirm license before commit)
- **Field target**: `seeds_per_gram` in `crop_variety_source_values`
- **Source label**: `OP:vital_seeds_count` / `OP:osborne_seed_count` (OP tier — commercial)

#### CW-07 — Companion Planting Matrix (UF/IFAS)
- **URL**: UF/IFAS vegetable companion planting chart (Perplexity CS-05)
- **Format**: HTML/PDF chart → NEW table `crop_companion_matrix` (crop_id × companion_crop_id × `compatibility` enum: `beneficial` / `neutral` / `antagonistic`)
- **Source label**: `PR:uf_ifas_companion` (PR tier)
- **Note**: companion planting evidence is weak in academic literature; flag as advisory not normative

### 🟡 TIER D — INGEST POSTHARVEST (lower priority but well-structured)

#### CW-08 — Postharvest Storage Conditions (UC Davis Cantwell)
- **URL**: `https://extension.k-state.edu/foodsafety/produce/resources/docs/storage-guidelines-UCDavis.pdf`
- **Cross-validation**: UMaine storage tables (Perplexity CS-08)
- **Format**: PDF table → NEW table `crop_postharvest_storage` with: `storage_temp_c_min`, `storage_temp_c_max`, `rh_pct_min`, `rh_pct_max`, `freezing_point_c`, `ethylene_production`, `ethylene_sensitivity`, `storage_life_days`
- **Coverage**: 100+ commodities
- **Source label**: `PR:uc_davis_postharvest` (PR tier)

### 🟠 TIER E — INVESTIGATE_FURTHER (defer to a follow-up WP if/when needed)

| ID | Source | Why defer | When to revisit |
|----|--------|-----------|-----------------|
| CW-09 | FAO ECOCROP / GAEZ | High extraction effort; bulk export not confirmed; 403 errors on catalog endpoints in scout session | If CW-01..CW-08 leave HIGH gaps unresolved |
| CW-10 | EPPO Global Database API | API registration + TOS review needed; LOW-priority pest taxonomy | After UI surfaces pest browsing |
| CW-11 | Cornell Vegetable Varieties (Mediterranean focus) | Single-engine find; structure unconfirmed | After WP-C2 reveals what variety data is still missing |
| CW-12 | "HaGina HaOrganit" Israel sowing calendar (Perplexity CS-09) | Non-official source; cross-engine uncertainty | After CW-05 (official Israeli sources) prove insufficient |

---

## Gaps NOT covered by any candidate

Confirmed by all 3 engines:
1. **Variety-level Mediterranean trial data** — beyond Quebec-biased JMF and beyond CW-05 narrative
2. **Crop-disease forecasting models** (degree-day based) for IL conditions
3. **Companion planting evidence rating** (academic vs. anecdotal classification)
4. **Per-variety nutrient demand** (only aggregate-crop-level removal available)
5. **Crop water requirements** (Kc coefficients per crop stage) — surprising omission

These remain open for future scouting waves.

---

## Suggested WP-C4 scope (recommendation to team_00)

**Author WP-C4 LOD400 covering all 8 INGEST candidates (CW-01..CW-08).**

Phases:
- **Phase 1 (HIGH-gap fills)**: CW-01 germination temp, CW-02 frost tolerance,
  CW-03 soil pH, CW-05 Israeli sources (CRITICAL)
- **Phase 2 (MED-gap fills)**: CW-04 NPK removal, CW-06 seeds per gram,
  CW-07 companion planting
- **Phase 3 (LOW-gap fill)**: CW-08 postharvest storage

INVESTIGATE_FURTHER items (CW-09..CW-12) → defer to WP-D (future) or
absorb into WP-C4 R2 if scope budget allows.

Estimated build: 5-6 sessions for full WP-C4 (more sources than C1 and similar
complexity to C2).

---

## Critical observation — multi-engine validates the approach

| Question | Answer |
|----------|--------|
| Did multi-engine help vs single-engine? | **YES — definitively.** OpenAI explicitly admitted it could not find Israeli sources. Perplexity + Gemini both did. Without the multi-engine approach, the HIGH-priority Israeli gap would remain. |
| What's the engine specialization pattern? | OpenAI was conservative + thorough on US extension sources; Perplexity was broadest (10 candidates including the most Israeli + commercial seed sources); Gemini was most focused on government-authoritative sources (Shaham/MoAG explicit) |
| Should we run multi-engine for future scouts? | **YES** — especially when the topic has both English-language abundance and non-English authoritative gaps |

---

*Consolidated by team_10 (Claude Sonnet 4.7) 2026-05-26 from 3 team_80 engine outputs.
Pre-handoff package complete. WP-C4 LOD400 authoring follows immediately.*
