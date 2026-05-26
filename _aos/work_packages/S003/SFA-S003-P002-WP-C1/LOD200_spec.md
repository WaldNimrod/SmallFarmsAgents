---
id: SFA-S003-P002-WP-C1-LOD200
wp: SFA-S003-P002-WP-C1 — Israeli Structured Data + Tend Multi-Year Backfill
gate: L-GATE_S (LOD200 — architecture spec)
status: LOD200_LOCKED
author: team_10 (acting under team_00 grant for canonical registration)
date: 2026-05-26
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-A (engine SSoT — LOD500_LOCKED at 594cbc8)
  - SFA-S003-P002-WP-B (program — LOD500_LOCKED, tag S003-P002-WP-B-v1.0.0)
depends_on: [SFA-S003-P002-WP-B]
brief_ref: data/external_sources/WAVE_PLAN_v1.0.0.md
sources_index: data/external_sources/INDEX.md
validator: team_190 (non-Claude, Iron Rule #1)
builder: sfa_build (team_10, separate session)
parallel_eligible_with: SFA-S003-P002-WP-C2
---

# LOD200 — WP-C1: Israeli Structured Data + Tend Multi-Year Backfill

## 1. Mission

Ingest 8 Tier-1 tabular sources (already scouted in
`data/external_sources/INDEX.md`) into the SFA crop book. Pure structured
tabular work — **no LLM, no OCR, no PDF narrative parsing.** Fills HIGH-priority
gaps: Israeli planting calendar, cover-crop germination temps, 2nd Israeli
farmer benchmarks, and 4× multiplication of Tend OP-tier statistical base.

## 2. In-scope

- **Migration 047** — new `crop_planting_calendar` table (PR+NI tier monthly matrix)
- **Migration 048** — new `crop_cover_crops` table (JMF cover-crop chart)
- **New importer modules**:
  - `israeli/groworganic_importer.py` (L01)
  - `israeli/bustan_importer.py` (L36 — 1-page PDF table parse with pdfplumber)
  - `israeli/idan_planning_importer.py` (L03, L04)
  - `jmf/cover_crops_importer.py` (L12 — 1-page PDF table)
  - extend `tend_overlay.py` (WP-B3) for years 2019, 2020, 2021
- **Crop-name map extension**: add `IL_CROP_MAP` constant in `constants.py` for Hebrew→DB mapping
- **CLI**: `seed.py --c1-only`, `--no-c1`; integrate into `--all` flow
- **Tests** ≥25 (parser + importer + idempotency + reconciler integration)

## 3. Out-of-scope

- Hebrew narrative DOCX/PDF extraction (deferred to WP-C2)
- Curtis Stone OCR (deferred to WP-C3)
- Web-sourced data (deferred to WP-C4 pending team_80 multi-engine scout)
- Modifying existing `organic_market_agent/crop_book/importer/tend.py` (raw-material guard)
- Tend 2018 (LOW volume — investigate decision deferred to remediation if needed)
- No edits to LOD500_LOCKED files

## 4. Data sources (all in `data/external_sources/`)

| Code | Path | Type | Rows |
|------|------|------|------|
| L01 | `israeli/L01_GROWORGANIC_sowing_dates_base.xlsx` | XLSX | 86×26 |
| L03 | `israeli/L03_IDAN_winter_planning.xlsx` | XLSX | 203×19 |
| L04 | `israeli/L04_IDAN_summer_planning.xlsx` | XLSX | 150×17 |
| L12 | `jmf_extension/L12_cover_crop_chart.pdf` | PDF (1pg) | ~15 rows |
| L36 | `israeli/L36_BUSTAN_sowing_calendar.pdf` | PDF (1pg) | ~30 crops |
| Tend 2019 | `tend_multi_year/Tend_2019_*.csv` | 6 CSVs | 3,560 rows |
| Tend 2020 | `tend_multi_year/Tend_2020_*.csv` | 6 CSVs | 6,685 rows |
| Tend 2021 | `tend_multi_year/Tend_2021_*.csv` | 6 CSVs | 3,865 rows |

## 5. Data model summary

### 5.1 `crop_planting_calendar` (migration 047) — NEW

Monthly planting matrix per crop, per source (Israeli sources primary).
Stores 12 boolean month-columns + activity_type + region.

### 5.2 `crop_cover_crops` (migration 048) — NEW

Cover-crop reference table with germination temperature + hardiness zone.
Standalone (not joined to `crops` because cover crops are a separate set).

### 5.3 Extensions to existing tables (NO GCR — additive only)
- `crop_variety_source_values`: new sources `'NI:groworganic'`, `'NI:bustan'`,
  `'OP:Idan_2017'`, `'OP:Tend_2019'`, `'OP:Tend_2020'`, `'OP:Tend_2021'`
- `crop_task_templates` (from WP-B1): new source labels for 3 Tend years
- `crop_harvest_stats` (from WP-B3): new (crop, year, season) aggregates for 3 years

## 6. Trust-layer placement

| Source | Tier | Weight | Rationale |
|--------|------|--------|-----------|
| L01 GROWORGANIC | NI | NULL (hard override) | Curated Israeli reference (groworganic.info) |
| L36 BUSTAN | NI | NULL (hard override) | Curated Israeli reference (ginatbustan.com) |
| L12 JMF cover crops | PR | 0.70 | JMF reference, same as JMF base |
| L03/L04 Idan | OP | 0.55 | 2nd Israeli grower (Eliakim farm) |
| Tend 2019/20/21 | OP | 0.55 | Same as Tend_2022 already loaded |

## 7. Dependencies

- Hard: WP-A (enrichment engine), WP-B (PR/OP/NI tier infrastructure)
- Soft: WP-C2 (Wave 2 narrative) can run parallel

## 8. LOD500_LOCKED untouched

| File | Why untouched |
|------|---------------|
| `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py` | LOD500_LOCKED |
| `db/versions/001..046_*.py` | LOD500_LOCKED |
| `mu-plugin/`, `tend.py` (importer) | LOD500_LOCKED (raw-material guard) |
| `crop_book/models.py` | LOD500_LOCKED (no GCR needed; new tables are standalone) |

## 9. GCR requirements

**NONE.** Both new tables (`crop_planting_calendar`, `crop_cover_crops`) are
standalone — no relationship added to `Crop` model. Queried via explicit
`session.query(...)`.

## 10. Acceptance criteria count target

**15 ACs minimum.** See LOD400 §10 for full matrix.

## 11. Test count target

**25 tests minimum.** Breakdown:
- 5 migration tests (047, 048 forward/backward + SQLite-safe)
- 8 importer-unit tests (parser per source)
- 8 DB-integration tests (upsert + idempotency)
- 4 reconciler integration tests (new sources blend correctly)

## 12. Open questions

1. **Tend 2018 inclusion** — defer or include with CROP_PLAN+SEED_LIST only?
   Recommendation: defer (separate INVESTIGATE artifact, not blocker for C1).
2. **L01 GROWORGANIC seasonal markers** (EQX, S22, EFS, ECS) — confirm encoding:
   EQX=equinox, S22=summer solstice (June 22), EFS=early fall start, ECS=early
   cold start? team_10 to verify by reading source XLSX and confirming with
   team_00 if ambiguous.
3. **Bustan PDF parse method** — try `pdfplumber` first; fall back to manual
   text+regex if column extraction fails. 1-page only, low risk.

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.*
