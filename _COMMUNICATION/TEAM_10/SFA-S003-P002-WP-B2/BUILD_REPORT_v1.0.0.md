# BUILD_REPORT — WP-B2: JMF NI Extraction Layer
**Version:** v1.0.0
**Date:** 2026-05-25
**Builder:** team_10 (Claude Sonnet 4.6)
**Spec:** SFA-S003-P002-WP-B2 LOD400 v1.1.3 LOCKED
**Status:** BUILD_COMPLETE

---

## 1. Authorization

- **L-GATE_B Mandate:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/MANDATE_L-GATE_B_v1.0.0.md`
- **Issuer:** team_110 (Claude Opus 4.7)
- **Spec lock:** LOD400 v1.1.3 — L-GATE_S R4 PASS_WITH_FINDINGS
- **IR#1 compliance:** Builder (Claude Sonnet 4.6) ≠ Spec author (team_110/Opus 4.7) ≠ Validator (team_190/GPT-5.5)

---

## 2. Commit Range

| Step | Hash | Description |
|------|------|-------------|
| Step 2-3 | `6e9d92d` | CropKnowledgeNote ORM + migration 045 |
| Step 4   | `808eb47` | ni/ directory + 6 NIImporter subclasses |
| Step 5   | `de38372` | APPEND _upsert_knowledge_note to ni_importer.py |
| Step 6   | `ae8a3c0` | fixture JSONs + data/ gitkeep + .gitattributes |
| Step 7   | `91f2081` | scripts/extract_jmf_ni.py |
| Step 8   | `f0ce180` | seed.py --ni-only / --no-ni + NI call-site block |
| Step 9   | `e95dce4` | 37 new tests across 14 test files (all ACs covered) |
| Step 10  | *(this commit)* | CHANGELOG.md update + BUILD_REPORT |

**Full range from patch01 lock:** `6e9d92d..HEAD`

---

## 3. Deliverables Checklist

### 3.1 New Files

| File | Purpose |
|------|---------|
| `organic_market_agent/crop_book/crop_knowledge_notes.py` | CropKnowledgeNote ORM, 13 NOTE_TYPE_VALUES, BODY_TEXT_MAX_LENGTH=2000 |
| `organic_market_agent/db/versions/045_crop_knowledge_notes.py` | Migration 045 (down_revision="044") |
| `organic_market_agent/crop_book/importer/ni/__init__.py` | NI_IMPORTER_CLASSES tuple (6 subclasses, registry bypass) |
| `organic_market_agent/crop_book/importer/ni/jmf_book.py` | JmfBookImporter (NI:jmf_book_v1) |
| `organic_market_agent/crop_book/importer/ni/jmf_book_alt.py` | JmfBookAltImporter (NI:jmf_book_alt_v1) |
| `organic_market_agent/crop_book/importer/ni/jmf_ft_flameweed.py` | JmfFtFlameweedImporter (NI:jmf_ft_flameweed_v1) |
| `organic_market_agent/crop_book/importer/ni/jmf_ft_biopesticide.py` | JmfFtBiopesticideImporter (NI:jmf_ft_biopesticide_v1) |
| `organic_market_agent/crop_book/importer/ni/jmf_ft_phytoprotection.py` | JmfFtPhytoprotectionImporter (NI:jmf_ft_phytoprotection_v1) |
| `organic_market_agent/crop_book/importer/ni/jmf_ft_nurseryseeding.py` | JmfFtNurseryseedingImporter (NI:jmf_ft_nurseryseeding_v1) |
| `scripts/extract_jmf_ni.py` | Standalone extraction CLI (text files, not PDFs) |
| `.gitattributes` | data/jmf/extracted/** linguist-vendored |
| `data/jmf/raw_text/<6 sources>/.gitkeep` | Input text dirs (team_00 populates post-merge) |
| `data/jmf/extracted/<6 sources>/.gitkeep` | Output JSON cache dirs |
| `tests/crop_book/fixtures/ni/<source>/<crop>.json` (13 files) | Fixture JSONs for all 6 sources |

### 3.2 Modified Files

| File | Change |
|------|--------|
| `organic_market_agent/crop_book/importer/ni_importer.py` | APPEND ONLY: `_upsert_knowledge_note()` after ni_registry line |
| `organic_market_agent/crop_book/importer/seed.py` | --ni-only / --no-ni flags + NI call-site block |
| `CHANGELOG.md` | WP-B2 [Unreleased] entry |

### 3.3 Test Files (14 files, 37 tests)

| File | ACs covered |
|------|------------|
| `test_ni_migration.py` | AC-01 (migration upgrade/downgrade) |
| `test_ni_orm.py` | AC-02 (ORM model, 13 note_type values) |
| `test_ni_upsert_helper.py` | AC-03 (helper exists, always NI trust_tier) |
| `test_ni_jmf_book_importer.py` | AC-06, AC-07, AC-08 (jmf_book load methods) |
| `test_ni_jmf_book_alt_importer.py` | AC-08 (jmf_book_alt) |
| `test_ni_jmf_ft_flameweed.py` | AC-09 (flame_weed_timing) |
| `test_ni_jmf_ft_biopesticide.py` | AC-09 (biopesticide_spray) |
| `test_ni_jmf_ft_phytoprotection.py` | AC-09 (phytoprotection_substance + _application) |
| `test_ni_jmf_ft_nurseryseeding.py` | AC-09 (nursery_seeding_process) |
| `test_ni_licensing_flag.py` | AC-05 (is_internal_farm_use_only always True) |
| `test_ni_idempotency.py` | AC-11 (upsert idempotency) |
| `test_ni_dedup_alt_edition.py` | AC-16 (jmf_book + jmf_book_alt coexist) |
| `test_ni_publisher_isolation.py` | AC-19, AC-20, AC-21a (LOD500_LOCKED audit) |
| `test_ni_seed_flags.py` | AC-17, AC-18 (seed.py CLI flags) |

---

## 4. Test Results

```
pytest tests/crop_book/ -q
288 passed, 1 failed (pre-existing: test_wp_upload_crop_book — out of scope)
37 new tests: ALL GREEN
```

**Suite delta from patch01 baseline (251 passed):** +37 new tests.

---

## 5. validate_aos.sh Result

```
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
29 PASS / 19 SKIP / 0 FAIL
```

Confirmed clean after each commit (Step 2-3 through Step 9).

---

## 6. LOD500_LOCKED Audit (AC-19 / AC-20 / AC-21a)

All locked paths verified CLEAN — zero modifications in WP-B2 commit range:

| Path | Status |
|------|--------|
| `publisher/` (all files) | CLEAN |
| `organic_market_agent/crop_book/views.py` | CLEAN |
| `organic_market_agent/crop_book/models.py` | CLEAN |
| `organic_market_agent/crop_book/importer/source_registry.py` | CLEAN |
| `organic_market_agent/crop_book/importer/field_policy.py` | CLEAN |
| `organic_market_agent/crop_book/importer/reconciler.py` | CLEAN |
| `organic_market_agent/crop_book/importer/enrichment_runner.py` | CLEAN |
| `organic_market_agent/crop_book/enrichment_models.py` | CLEAN |
| `organic_market_agent/crop_book/importer/tend.py` | CLEAN |
| `organic_market_agent/crop_book/importer/jmf.py` | CLEAN |
| `organic_market_agent/db/versions/001_*.py` through `044_*.py` | CLEAN |
| `organic_market_agent/crop_book/constants.py` | CLEAN |
| `organic_market_agent/crop_book/crop_task_templates.py` | CLEAN |
| `organic_market_agent/crop_book/importer/jmf_masterclass.py` | CLEAN |
| `organic_market_agent/crop_book/importer/ni_importer.py` (body) | APPEND ONLY — NIImporter class, _NIRegistry class, ni_registry singleton unchanged |

**§3.1 OPERATIVE LICENSING INVARIANT:** `is_internal_farm_use_only=True` hardcoded in `_upsert_knowledge_note()` regardless of caller args. No publisher/ or views.py modifications. CONFIRMED.

---

## 7. Architectural Notes

- **Registry bypass (§7.1):** B2 subclasses are NOT registered in ni_registry singleton. `NI_IMPORTER_CLASSES` tuple enables session-aware resolution (crop_id, variety_id) inside `load()` / `load_knowledge_notes()`.
- **Dual format support:** FT importers accept both `_table.json` (production: crops dict) and per-crop JSON files (test fixtures).
- **Q1 compliance:** `extract_jmf_ni.py` reads text files, not PDFs. team_00 provides text files post-merge.
- **Q5 compliance:** 6 sources implemented (3 baseline + 3 additional: phytoprotection, nurseryseeding, biopesticide). 13 note_type values (3 added: phytoprotection_substance, phytoprotection_application, nursery_seeding_process).
- **AC-16 dedup:** `UNIQUE(crop_id, source, note_type)` — jmf_book and jmf_book_alt have different source labels, so both rows coexist for same crop + note_type.

---

## 8. Pending / Out of Scope

- **Q1 text files:** team_00 to provide JMF raw text files to `data/jmf/raw_text/` after merge. Extraction via `python scripts/extract_jmf_ni.py --all`.
- **DB online mutations:** DB is ONLINE (ADR034). Live production seed runs go via `python -m organic_market_agent.crop_book.importer.seed --ni-only` through established API pipeline.
- **pre-existing failure:** `test_wp_upload_crop_book` — WP REST API upload test, unrelated to WP-B2 scope, remains 1 failure throughout.

---

*BUILD_REPORT filed by team_10 (Claude Sonnet 4.6) — 2026-05-25*
*Routed to: team_110 (L-GATE_V handoff), team_190 (validator)*
