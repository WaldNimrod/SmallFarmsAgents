---
id: SFA-S003-P002-WP-C3-LOD200
wp: SFA-S003-P002-WP-C3 — Secondary Sources + OCR + Backlog Sweep
gate: L-GATE_S (LOD200)
status: LOD200_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-A
  - SFA-S003-P002-WP-B (LOD500_LOCKED)
  - SFA-S003-P002-WP-C1 (depends on Tend baseline + Idan baseline)
depends_on: [SFA-S003-P002-WP-C1]
brief_ref: data/external_sources/WAVE_PLAN_v1.0.0.md
---

# LOD200 — WP-C3: Secondary Sources + OCR + Backlog Sweep

## 1. Mission

Ingest secondary sources that need image-OCR or comparative analysis:
Curtis Stone (Urban Farmer) data, Idan's seedling succession patterns, FRANCHI
Italian variety catalog. Settle the Tend 2018 + Idan 2018 update questions.

## 2. In-scope

- **L40 Curtis Stone master chart** (XLSX, 23 crops × 29 cols) — `urban_farmer/curtis_profiles_importer.py`
- **L41 Curtis 34 scanned book pages** — OCR pipeline (tesseract OR Anthropic vision API one-time) → cached JSON → NI-tier narrative
- **L05a/L05b Idan seedling trackers** — `israeli/idan_seedlings_importer.py` → derive `succession_interval_weeks` per crop
- **L06 covers & tunnels XLSX** — extract sheet 2 (FRANCHI seed catalog, 29 rows) → variety reference data
- **L49 Idan 2018 update** — diff vs L03/L04 (2017); supersede only where newer; document deltas
- **Tend 2018 decision** — investigate (CROP_PLAN=60, TASKS=97, HARVESTS=0); if just initial setup, ingest CROP_PLAN+SEED_LIST only with disclaimer; if richer than appears, full ingestion
- **L45 Nimrod's 2017 data** — assess if it complements gaps left after C1+C2; if yes, light ingestion
- **L43 customer leafy greens** — final SKIP confirmation after C1+C2 (likely no incremental value)

## 3. Out-of-scope

- L38 Italian Libretto Orto — DEFER to Wave 4 (Mediterranean adaptation TBD)
- L26 (bank receipt — confirmed SKIP)
- L44 (wiring diagram — confirmed SKIP)
- L39 mesclun guide — confirmed SKIP

## 4. Data sources (all in `data/external_sources/`)

| Code | Path | Type |
|------|------|------|
| L40 | `urban_farmer/L40_curtis_crop_profiles.xlsx` | XLSX (23×29) |
| L41 | `urban_farmer/L41_curtis_chart_*.jpg` (34 files) | scanned book pages |
| L05a | `israeli/L05a_IDAN_seedlings_winter_18-19.xlsx` | XLSX |
| L05b | `israeli/L05b_IDAN_seedlings_summer_18-19.xlsx` | XLSX |
| L06 | `israeli/L06_covers_and_tunnels.xlsx` | XLSX (sheet 2 only) |
| L49 | `israeli/L49_IDAN_market_gardening_tech.xlsx` | XLSX |
| L45 | `israeli/L45_2017_data_summary.xlsx` | XLSX |
| Tend 2018 | `tend_multi_year/Tend_2018_*.csv` | 6 CSVs |

## 5. Data model summary

- **No new tables.** All data goes into existing tables:
  - Curtis L40 → `crop_variety_source_values` (OP tier, `source='OP:CurtisStone'`, weight=0.55)
  - Curtis L41 OCR → `crop_knowledge_notes` (NI tier, `source='NI:curtis_stone_book'`)
  - L05a/b → derived field `succession_interval_weeks` added to `crop_varieties` table via spec_value or new source_values row (decision in LOD400)
  - L06 sheet 2 → variety reference into `crop_varieties` updates (where match exists) OR `crop_variety_source_values` for variety_name + provider
  - L49 diff → upsert OP rows with `source='OP:Idan_2018'`
  - Tend 2018 → optional CROP_PLAN ingestion only

## 6. Trust-layer placement

| Source | Tier | Weight |
|--------|------|--------|
| L40 Curtis master chart | OP | 0.55 (BC Canada climate caveat) |
| L41 Curtis OCR narrative | NI | NULL (hard override on narrative only) |
| L05a/b Idan seedlings | OP | 0.55 |
| L06 FRANCHI catalog | OP | 0.55 (variety reference; not blendable scalar) |
| L49 Idan 2018 | OP | 0.55 |
| Tend 2018 | OP | 0.55 |

## 7. Dependencies

- Hard: WP-C1 (Tend baseline + Idan 2017 baseline must exist before C3 can diff/extend)
- Soft: WP-C2 (Hebrew narrative complements Curtis OCR)

## 8. LOD500_LOCKED untouched — same as C1/C2

## 9. GCR requirements

**Possibly:** `succession_interval_weeks` already exists on `crop_varieties` table
(see WP-B1 LOD400 reference). If yes, NO GCR. If field doesn't exist, file
GCR-C3-1 for that field addition. Builder to verify in LOD400 phase.

## 10. AC count target: 10
## 11. Test count target: 12

## 12. Open questions

1. **OCR engine choice** — Tesseract (free, lower quality) vs. Anthropic Vision
   API one-time call (paid, higher quality). Decision in LOD400 based on cost
   ($5 budget cap).
2. **Curtis L40 vs L41 redundancy** — L40 XLSX has structured data; L41 images
   add narrative. After OCR, dedupe content overlap.
3. **L45 value** — peek after C1+C2 reveal which gaps remain.

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.*
