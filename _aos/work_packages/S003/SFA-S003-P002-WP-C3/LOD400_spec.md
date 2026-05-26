---
id: SFA-S003-P002-WP-C3-LOD400
wp: SFA-S003-P002-WP-C3
gate: L-GATE_S (LOD400 — build-precise spec, compact)
status: LOD400_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD200_spec.md
---

# LOD400 — WP-C3: Secondary + OCR + Backlog Sweep

## 1. Mission
(See LOD200 §1.) Ingest 5-6 secondary sources; reconcile L49 vs L03/L04;
decide Tend 2018 inclusion. OCR Curtis Stone images. No new DB tables.

## 2. File-by-file delta

| Action | Path |
|--------|------|
| NEW | `organic_market_agent/crop_book/importer/urban_farmer/__init__.py` |
| NEW | `organic_market_agent/crop_book/importer/urban_farmer/curtis_profiles_importer.py` (L40) |
| NEW | `organic_market_agent/crop_book/importer/urban_farmer/curtis_ocr_importer.py` (L41 — reads cached OCR JSON) |
| NEW | `organic_market_agent/crop_book/importer/israeli/idan_seedlings_importer.py` (L05a+L05b) |
| NEW | `organic_market_agent/crop_book/importer/israeli/franchi_catalog_importer.py` (L06 sheet 2) |
| NEW | `organic_market_agent/crop_book/importer/israeli/idan_2018_diff.py` (L49 — supersede L03/L04 only where newer) |
| NEW | `scripts/ocr_curtis_images.py` (one-time prepare: tesseract OR vision API → JSON cache per image) |
| OPTIONAL | `organic_market_agent/crop_book/importer/tend_overlay.py` (extend for 2018 if decision = include) |
| MODIFY | `organic_market_agent/crop_book/importer/seed.py` (`--c3-only`, `--no-c3`) |
| NEW | `data/external_sources/extracted/curtis_ocr/<image_id>.json` (cache) |
| NEW | `tests/crop_book/test_c3_*.py` (≥12 tests) |
| NEW | `_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/TEND_2018_INVESTIGATION.md` (decision artifact) |

## 3. Data model — NO NEW TABLES

All upserts hit existing tables:
- `crop_variety_source_values` (Curtis L40, L05a/b derived, L06, L49 diff, optional Tend 2018)
- `crop_knowledge_notes` (Curtis L41 OCR narrative — NI tier)

`succession_interval_weeks` source_value field: builder verifies it's a known
field; if not, document in spec discrepancy + skip the L05a/b derivation (downgrade scope).

## 4. Importer architecture

### 4.1 Curtis master chart (L40) — `curtis_profiles_importer.py`

```python
def parse_curtis_master_chart(xlsx_path: Path) -> list[dict]:
    """Sheet 'Sheet 1 - Master Chart-1', 23 rows × 29 cols.
    Fields:
      Crop, Avg DTM from seed date, Available for harvest, Crop Type,
      CVR5/5, Quick or Steady, DS/TR, Bed Size, Walkway width,
      When to DS, When to TRN, Last Field Plant Date, Last GH Plant Date,
      Jang Roller, EW Plate, ...
    Map to source_values:
      - Avg DTM → days_to_maturity (OP:CurtisStone)
      - CVR5/5 → derive curtis_value_rating (new field name; if not in current
        schema, store in `note` column with prefix)
      - DS/TR → planting_method
      - Jang Roller, EW Plate → seeder calibration notes
    """
```

### 4.2 OCR pipeline (L41) — `scripts/ocr_curtis_images.py`

**Decision rubric (LOD400 lock):**
- **Engine choice: Anthropic Vision API one-time call.**
- Rationale: 34 images × ~$0.05/image = ~$1.70 (well within $5 cap). Quality
  significantly higher than tesseract for handwriting/printed-mix book pages.
- Output: `data/external_sources/extracted/curtis_ocr/L41_curtis_chart_NN.json`
  with structured fields per crop: `{crop, planting_specs, varieties, dtm,
  avg_yield_per_bed, avg_gross_profit_per_bed, narrative_text}`.
- Idempotency: skip OCR if cache exists.

Fallback: if Anthropic API unavailable, tesseract → manual review.

### 4.3 Idan seedlings (L05a/b) — `idan_seedlings_importer.py`

```python
def derive_succession_intervals(xlsx_paths: list[Path]) -> dict[str, int]:
    """For each crop, count distinct seedling-order dates within the season
    and derive median interval (weeks). Output: {crop_he: succession_weeks}.

    Example: ברוקולי has orders on 18/9, 2/10, 16/10, 27/11, 11/12, 22/1, 5/2, 19/2
    → 8 orders over ~5 months → median interval ~3 weeks.
    """
```

Upsert to `crop_variety_source_values` with `field_name='succession_interval_weeks'`,
`source='OP:Idan_seedlings'`, `trust_tier='OP'`.

### 4.4 FRANCHI catalog (L06 sheet 2) — `franchi_catalog_importer.py`

```python
def parse_franchi_catalog(xlsx_path: Path) -> list[dict]:
    """Sheet 'גיליון2', 29 rows × 5 cols.
    Columns: מין (crop), זן (variety EN+code), קוד, אריזה (package), כמות.
    Upsert variety references to crop_variety_source_values with
    field_name='variety_provider', source='OP:FRANCHI_catalog'.
    """
```

### 4.5 L49 diff vs L03/L04 — `idan_2018_diff.py`

```python
def diff_and_upsert(l49_path, l03_path, l04_path, session):
    """Read all three Idan files. For each (crop, field) in L49:
        - If L03/L04 has same (crop, field) with different value:
            → upsert L49 row with source='OP:Idan_2018' (separate row;
              reconciler will blend per FIELD_POLICY)
        - If L49 has new (crop, field) not in L03/L04:
            → upsert as new OP row
        - If identical → skip (idempotency)
    Log diff to _COMMUNICATION/team_10/SFA-S003-P002-WP-C3/L49_DIFF_REPORT.md
    """
```

### 4.6 Tend 2018 decision

Pre-flight investigation:
1. Read Tend_2018_CROP_PLAN.csv full content
2. If it has structurally different schema → SKIP (document in TEND_2018_INVESTIGATION.md)
3. If schema matches 2019+ → INGEST CROP_PLAN + SEED_LIST only (since HARVESTS=0, NOTES=0)
4. Update TEND_2018_INVESTIGATION.md with decision + rationale

## 5. AC matrix (10 ACs)

| AC | Description |
|----|-------------|
| AC-C3-01 | L40 Curtis master chart parses → ≥20 source_value rows with `source='OP:CurtisStone'` |
| AC-C3-02 | L41 OCR pipeline produces ≥30 cached JSONs (out of 34 images; ≥88% success) |
| AC-C3-03 | Curtis OCR narrative populated in `crop_knowledge_notes` (NI tier) for ≥10 crops |
| AC-C3-04 | L05a+L05b succession intervals derived for ≥8 crops |
| AC-C3-05 | L06 FRANCHI catalog: 29 variety references inserted |
| AC-C3-06 | L49 diff report generated; differential rows upserted with `source='OP:Idan_2018'`; no duplicates |
| AC-C3-07 | Tend 2018 decision documented; if INGEST → CROP_PLAN + SEED_LIST only |
| AC-C3-08 | Reconciler blend stability: no regression in `validate_enrichment.py` CALIBRATED count vs C1+C2 baseline |
| AC-C3-09 | Tests ≥12 |
| AC-C3-10 | validate_aos.sh: 29/19/0 |

## 6. Verification

```bash
# OCR (one-time)
python3 scripts/ocr_curtis_images.py

# Importers
python3 -m organic_market_agent.crop_book.importer.seed --c3-only

# Tests
python3 -m pytest tests/crop_book/test_c3_*.py

# Diff sanity
cat _COMMUNICATION/team_10/SFA-S003-P002-WP-C3/L49_DIFF_REPORT.md
cat _COMMUNICATION/team_10/SFA-S003-P002-WP-C3/TEND_2018_INVESTIGATION.md

bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 7. Risk register
| Risk | Mitigation |
|------|------------|
| Tesseract+vision both fail on Curtis pages (poor scan quality) | Document failure per image; manually transcribe ≥10 highest-priority pages |
| L49 vs L03/L04 reveals massive divergence → unclear how to reconcile | Defer L49 ingestion; flag for team_00 decision |
| L05a/b succession intervals depend on undefined `succession_interval_weeks` field | If field absent, skip L05a/b derivation; document downgrade |

---
*LOD400 authored by team_10 2026-05-26 under team_00 grant.*
