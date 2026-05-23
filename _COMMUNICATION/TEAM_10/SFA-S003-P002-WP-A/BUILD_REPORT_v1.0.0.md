# BUILD_REPORT — SFA-S003-P002-WP-A
**Work Package:** Data Enrichment Architecture (WP-A)
**Report version:** v1.0.0
**Builder engine:** team_10 (Claude Sonnet 4.5)
**Date:** 2026-05-24
**Spec reference:** `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` (v1.1.0, LOD400_LOCKED)

---

## 1. Build Outcome

**Status: BUILD COMPLETE — all 10 LOD400 steps implemented and verified.**

---

## 2. Deliverables Summary

### Step 1 — Spec Lock
- LOD200 spec: `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md` (v1.1.0, pre-existing)
- LOD400 spec: `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` (v1.1.0, pre-existing)
- team_190 verdict: L-GATE_B EXIT CRITERION SATISFIED (29 PASS / 17 SKIP / 0 FAIL)

### Step 2 — Source Registry + Field Policy
| File | Status |
|------|--------|
| `organic_market_agent/crop_book/source_registry.py` | CREATED |
| `organic_market_agent/crop_book/field_policy.py` | CREATED |

7-class source taxonomy (EX/NI/PR/OP/MK/WB/UC) with weights, hard-override flags, moderation gate.
Per-field blend strategy table (weighted_mean / hard_winner / latest_op) for 9 named fields + default.

### Step 3 — Models (GCR_1)
| File | Change |
|------|--------|
| `organic_market_agent/crop_book/enrichment_models.py` | CREATED — `CropFieldEnrichment` ORM |
| `organic_market_agent/crop_book/models.py` | MODIFIED (GCR_1 scope) — 3 columns on `CropVarietySourceValue`; `enrichments` relationship on `CropVariety` |

GCR_1 columns: `trust_tier VARCHAR(20)`, `confidence_weight NUMERIC(5,4)`, `is_outlier_rejected BOOLEAN`.
Circular import avoided via `TYPE_CHECKING` guard.

### Step 4 — Migrations
| Migration | Table | Type |
|-----------|-------|------|
| `041_crop_field_enrichment.py` | `crop_field_enrichment` | NEW TABLE (additive, no GCR) |
| `042_source_values_enrich.py` | `crop_variety_source_values` | ADD 3 COLUMNS (GCR_1) |

Both applied: `alembic upgrade head` → 041→042 PASS. Schema verified against live PostgreSQL.
Unique constraint `uq_cfe_variety_field` on `(variety_id, field_name)`.

### Step 5 — Reconciler Rewrite
**File:** `organic_market_agent/crop_book/importer/reconciler.py`

Pluggable engine replacing hardcoded priority logic:
- `Candidate` + `FieldConsensus` dataclasses
- `_outlier_mask()`: modified Z-score / MAD gate with F-190-WP-A-02 fix:
  - MAD=0 + all identical → no outliers
  - MAD=0 + not identical → IQR fallback; IQR=0 → flag non-median
- `reconcile_field()`: classify → hard_override → outlier gate → blend strategy → confidence
- `reconcile_dtm()` backward-compat wrapper: (source, value) tuple matching for per-row outlier flag
- `reconcile_variety()` backward-compat wrapper: field-by-field delegation to reconcile_field
- `_winning_source_label()`: mirrors `multi_year_op_mean` collapse logic

Bug found + fixed during build: `reconcile_dtm` previously used set membership on source labels, causing all Tend rows to be flagged when any Tend value was an outlier. Fixed by matching on `(source_label, value)` tuples.

### Step 6 — Enrichment Runner + seed --enrich
| File | Change |
|------|--------|
| `organic_market_agent/crop_book/importer/enrichment_runner.py` | CREATED |
| `organic_market_agent/crop_book/importer/seed.py` | MODIFIED — GCR_1 field passthrough + `--enrich` flag |

`run_enrichment(session, variety_ids=None, dry_run=False) → EnrichmentSummary`
- Loads CropVarietySourceValue rows per variety
- Back-populates `trust_tier` where NULL (idempotent)
- UC moderation gate: skip if `confidence_weight IS NULL OR = 0`
- Calls `reconcile_field()` per (variety, field)
- Upserts into `crop_field_enrichment` (INSERT or UPDATE by unique constraint)
- Returns `EnrichmentSummary(variety_count, field_count, outlier_count, high_confidence_count)`

### Step 7 — NI Importer Skeleton
**File:** `organic_market_agent/crop_book/importer/ni_importer.py`

Abstract `NIImporter` base class with `load()` + `validate()` hooks.
`_NIRegistry` singleton with `register()` and `load_all()`.
Source label convention: `"NI:<name>"` (detected by `source_registry.get_source_spec`).

### Step 8 — Validation Harness
**File:** `scripts/validate_enrichment.py`

Shadow-run calibration: compares `crop_field_enrichment` against `TEAM00_DTM_OVERRIDES` (ground truth).
Checks: row existence, `winning_source_class == "EX"`, `confidence_score == 1.0000`, `value_best` within ±0.5.
Exit code: 0=pass, 1=fail.

### Step 9 — Enrichment Publisher
**File:** `organic_market_agent/crop_book/publisher/enrichment_publisher.py`

**F-01 compliant: NO `dispatch_upload()` call. JSON file only.**
`publish_enrichment(session, output_path=None) → Path`
- Output: `output/sfagent-crop-book-enrichment.json`
- Schema: `{generated_at, variety_count, fields: [{variety_id, crop_name_he, ...}]}`
- `ensure_ascii=False` preserves Hebrew characters

### Step 10 — Test Suite
**56 tests across 5 new files + updated `test_reconciler.py`:**

| File | Tests | Result |
|------|-------|--------|
| `test_source_registry.py` | 10 | 10/10 PASS |
| `test_field_policy.py` | 8 | 8/8 PASS |
| `test_reconciler.py` (updated) | 10 | 10/10 PASS |
| `test_reconciler_engine.py` | 18 | 18/18 PASS |
| `test_enrichment_runner.py` | 5 | 5/5 PASS |
| `test_enrichment_publisher.py` | 5 | 5/5 PASS |

Full suite (minus 2 pre-existing failures in LOD500_LOCKED files): **433 PASS, 14 SKIP, 0 new failures**.

---

## 3. LOD400 Acceptance Criteria — Verification

| AC | Description | Status |
|----|-------------|--------|
| AC-01 | SOURCE_REGISTRY with 7-class taxonomy, class codes, weights, hard-override flags | ✅ PASS |
| AC-02 | FIELD_POLICY for 9 named fields + default | ✅ PASS |
| AC-03 | `CropFieldEnrichment` ORM + migration 041 | ✅ PASS |
| AC-04 | `CropVarietySourceValue` GCR_1 columns + migration 042 | ✅ PASS |
| AC-05 | EX/NI hard override: always wins, confidence=1.0000 | ✅ PASS |
| AC-06 | UC moderation gate: excluded unless confidence_weight > 0 | ✅ PASS |
| AC-07 | Outlier gate: modified Z-score + MAD=0 branch (F-190-WP-A-02) | ✅ PASS |
| AC-08 | Blend strategies: weighted_mean / hard_winner / latest_op | ✅ PASS |
| AC-09 | multi_year_op_mean collapses OP observations before blending | ✅ PASS |
| AC-10 | validate_enrichment.py calibrates against team_00 EX overrides | ✅ PASS |
| AC-11 | enrichment_publisher.py generates JSON only — NO dispatch_upload (F-01) | ✅ PASS |
| AC-12 | GCR_1 fields back-populated in reconcile_dtm wrapper | ✅ PASS |
| AC-13 | seed.py --enrich flag calls run_enrichment after seed | ✅ PASS |
| AC-14 | Migration 041 unique constraint uq_cfe_variety_field | ✅ PASS |
| AC-15 | ni_importer.py abstract skeleton with registry | ✅ PASS |
| AC-16 | run_enrichment idempotent (upsert semantics) | ✅ PASS |
| AC-17 | Backward-compat: reconcile_dtm / reconcile_variety unchanged signatures | ✅ PASS |
| AC-18 | TYPE_CHECKING guard avoids circular import | ✅ PASS |
| AC-19 | validate_aos.sh: 0 FAIL | ✅ PASS (29/17/0) |
| AC-20 | 20+ new tests covering enrichment pipeline | ✅ PASS (56 new tests) |

---

## 4. LOD500_LOCKED Compliance

No LOD500_LOCKED files were modified. Verified:
- `views.py` — UNTOUCHED ✅
- `publisher/*.py` (existing files) — UNTOUCHED ✅
- `migrations/001–040` — UNTOUCHED ✅
- `mu-plugin` — UNTOUCHED ✅
- `tend.py`, `jmf.py` — UNTOUCHED ✅

`models.py` modified ONLY under GCR_1 pre-authorization (Decision A-3):
- 3 columns on `CropVarietySourceValue` ✅
- `enrichments` relationship on `CropVariety` ✅
- No other changes ✅

---

## 5. Pre-existing Test Failures (Not Introduced by WP-A)

| Test | Root cause | Our fault? |
|------|-----------|------------|
| `test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile` | `UploadResult.__init__()` unexpected kwarg `wp_artifacts` in LOD500_LOCKED publisher | NO |
| `test_admin_routes.py::test_t09_runs_trigger_creates_ingestion_run` | Timing/state assertion (54>54) in admin route | NO |

---

## 6. Gate Readiness

**L-GATE_B (Builder):** SATISFIED
- validate_aos.sh: 29 PASS / 17 SKIP / 0 FAIL
- All 20 ACs verified
- 56 tests pass

**Ready for L-GATE_V (Validator / team_190):** YES

---

_Authored by: team_10 (sfa_build role) | SFA-S003-P002-WP-A LOD400 §17 Step 10_
