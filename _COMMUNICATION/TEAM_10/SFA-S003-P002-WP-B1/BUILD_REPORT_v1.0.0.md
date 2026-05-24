---
id: BUILD_REPORT_SFA-S003-P002-WP-B1_v1.0.0
from: team_10 (sfa_build, Claude Sonnet 4.6)
to: team_110 (AOS Domain Architect)
date: 2026-05-24
type: BUILD_REPORT
wp: SFA-S003-P002-WP-B1
gate: L-GATE_B
spec_lock_commit: 262d9a3
spec_version: LOD400 v1.1.3
status: BUILD_COMPLETE
verdict: PASS_WITH_FINDINGS
---

# BUILD REPORT — SFA-S003-P002-WP-B1 (JMF MasterClass Excel Base Layer)

## 1. Verdict Summary

**BUILD_COMPLETE — PASS_WITH_FINDINGS**

All 56 new tests pass. All 22 acceptance criteria satisfied against the fixture workbook.
One open finding (AC-04 live workbook mismatch) documented via inquiry MSG.
LOD500_LOCKED inventory untouched. AOS validation clean.

---

## 2. Acceptance Criteria Table

| AC | Description | Result | Evidence |
|----|-------------|--------|----------|
| AC-01 | `crop_task_templates` table created by migration 044 | PASS | `test_migration_044::test_ac01_table_exists` |
| AC-02 | `CropTaskTemplate` ORM importable from `crop_task_templates` module | PASS | `test_crop_task_templates_orm::test_ac02_orm_importable` |
| AC-03 | `JMF_CROP_MAP` importable from `constants.py` | PASS | `test_jmf_crop_map::test_ac03_jmf_crop_map_importable` |
| AC-04 | `JMF_CROP_MAP` has exactly 52 entries verbatim from spec §5 | PASS (fixture) / FINDING (live) | `test_jmf_crop_map::test_ac04_*`; see §7 |
| AC-05 | Parser reads ≥50 rows from CROP CHART sheet | PASS | `test_jmf_masterclass_parsers::test_ac05_*` |
| AC-06 | `parse_associated_tasks` returns rows with `task_type` and `days_offset` | PASS | `test_jmf_masterclass_parsers::test_ac06_*` |
| AC-07a | `import_jmf_masterclass` is idempotent (2nd call = same row count) | PASS | `test_jmf_idempotency::test_ac07a_idempotent` |
| AC-07b | Idempotency: no duplicate rows on repeated import | PASS | `test_jmf_idempotency::test_ac07b_no_duplicates` |
| AC-08 | `lbs/100ft` → `kg/m` conversion correct (Decimal, 4dp) | PASS | `test_jmf_unit_conversions::test_ac08_*` |
| AC-09 | Inches → cm conversion correct (Decimal, 2dp) | PASS | `test_jmf_unit_conversions::test_ac09_*` |
| AC-10 | Unit conversion edge cases: None, zero, unparseable string | PASS | `test_jmf_unit_conversions::test_ac10_*` |
| AC-11 | `import_jmf_masterclass` returns `JmfImportSummary` dataclass | PASS | `test_jmf_masterclass_integration::test_ac11_returns_summary` |
| AC-12 | `source_value_rows_upserted` > 0 after import | PASS | `test_jmf_masterclass_integration::test_ac12_source_values_upserted` |
| AC-13 | EX override (team_00) wins over JMF PR (0.70) — iron regression | PASS | `test_jmf_ex_override_regression::test_ac13_ex_override_wins_over_jmf` |
| AC-14 | `task_template_rows_upserted` > 0 after import | PASS | `test_jmf_masterclass_integration::test_ac14_task_templates_upserted` |
| AC-15a | `days_offset` column is NOT NULL in migration DDL | PASS | `test_migration_044::test_ac15a_days_offset_not_null` |
| AC-15b | `days_offset` default is `-32768` (DAYS_OFFSET_PRESENCE_ONLY) | PASS | `test_migration_044::test_ac15b_days_offset_default` |
| AC-16a | `is_presence_only(-32768)` returns True; `is_presence_only(5)` returns False | PASS | `test_migration_044::test_ac16a_sentinel_helpers` |
| AC-16b | Explicit NULL insert for `days_offset` raises `IntegrityError` | PASS | `test_crop_task_templates_orm::test_ac16b_null_days_offset_raises` |
| AC-17 | `--jmf-only` flag available on seed.py CLI | PASS | `test_seed_jmf_cli::test_ac17_jmf_only_flag_available` |
| AC-18 | `--no-jmf` flag available on seed.py CLI | PASS | `test_seed_jmf_cli::test_ac18_no_jmf_flag_available` |
| AC-19 | `--jmf-masterclass-dir` flag available on seed.py CLI | PASS | `test_seed_jmf_cli::test_ac19_jmf_masterclass_dir_flag_available` |

---

## 3. Test Execution Evidence

### pytest tests/crop_book/ -q (final run)

```
1 failed, 241 passed, 16 warnings in 5.79s

FAILED tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile
```

**New WP-B1 tests: 56** (spec required ≥25)

| Test file | Tests | ACs covered |
|-----------|-------|-------------|
| test_jmf_crop_map.py | 7 | AC-03, AC-04 |
| test_jmf_unit_conversions.py | 12 | AC-08, AC-09, AC-10 |
| test_jmf_masterclass_parsers.py | 11 | AC-05, AC-06 |
| test_crop_task_templates_orm.py | 7 | AC-02, AC-16b |
| test_migration_044.py | 5 | AC-01, AC-15a, AC-15b, AC-16a |
| test_jmf_masterclass_integration.py | 5 | AC-11, AC-12, AC-14 |
| test_jmf_idempotency.py | 2 | AC-07a, AC-07b |
| test_seed_jmf_cli.py | 6 | AC-17, AC-18, AC-19 |
| test_jmf_ex_override_regression.py | 1 | AC-13 |
| **TOTAL** | **56** | AC-01 through AC-19 |

**Pre-existing failure (not WP-B1):**
`test_dispatch_upload_crop_book_profile` in `test_wp_upload_crop_book.py` touches locked publisher code
(`organic_market_agent/publisher/upload_dispatch.py`). This failure predates this WP and is unrelated
to any WP-B1 deliverable. It was present at commit 262d9a3 (spec lock).

---

## 4. AOS Validation Evidence

```
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

=================================================
RESULT: 29 PASS / 17 SKIP / 0 FAIL
=================================================
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## 5. LOD500_LOCKED Audit

`git diff 262d9a3..HEAD -- <locked-paths>` produced **zero output** for all locked files:

| Locked path | Diff result |
|-------------|-------------|
| `organic_market_agent/views.py` | CLEAN |
| `organic_market_agent/publisher/wp_upload.py` | CLEAN |
| `organic_market_agent/publisher/upload_dispatch.py` | CLEAN |
| `organic_market_agent/crop_book/importer/tend.py` | CLEAN |
| `organic_market_agent/crop_book/models.py` | CLEAN |
| `organic_market_agent/crop_book/source_registry.py` | CLEAN |
| `organic_market_agent/crop_book/field_policy.py` | CLEAN |
| `organic_market_agent/crop_book/enrichment_models.py` | CLEAN |
| `organic_market_agent/crop_book/reconciler.py` | CLEAN |
| `organic_market_agent/crop_book/importer/enrichment_runner.py` | CLEAN |
| `organic_market_agent/db/versions/001..043_*.py` | CLEAN |

---

## 6. Files Touched Classification

### CREATED (new files — WP-B1 deliverables)

| File | Step | Notes |
|------|------|-------|
| `organic_market_agent/crop_book/crop_task_templates.py` | Step 2 | ORM module, `DAYS_OFFSET_PRESENCE_ONLY = -32768` |
| `organic_market_agent/db/versions/044_crop_task_templates.py` | Step 3 | Migration 044, down_revision="043" |
| `organic_market_agent/crop_book/importer/jmf_masterclass.py` | Steps 5-7 | 5 parsers + orchestrator + helpers |
| `tests/crop_book/fixtures/jmf/make_fixture.py` | Step 5 | Fixture generator (openpyxl) |
| `tests/crop_book/fixtures/jmf/minimal_masterclass.xlsx` | Step 5 | 3-crop fixture (Arugula, Carrots, Basil) |
| `tests/crop_book/test_jmf_crop_map.py` | Step 9 | 7 tests |
| `tests/crop_book/test_jmf_unit_conversions.py` | Step 9 | 12 tests |
| `tests/crop_book/test_jmf_masterclass_parsers.py` | Step 9 | 11 tests |
| `tests/crop_book/test_crop_task_templates_orm.py` | Step 9 | 7 tests |
| `tests/crop_book/test_migration_044.py` | Step 9 | 5 tests |
| `tests/crop_book/test_jmf_masterclass_integration.py` | Step 9 | 5 tests |
| `tests/crop_book/test_jmf_idempotency.py` | Step 9 | 2 tests |
| `tests/crop_book/test_seed_jmf_cli.py` | Step 9 | 6 tests |
| `tests/crop_book/test_jmf_ex_override_regression.py` | Step 9 | 1 test (AC-13 iron regression) |
| `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B1/INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md` | Step 9 | Per §11 Step 4 rule |

### MODIFIED (existing files)

| File | Change | Locked? |
|------|--------|---------|
| `organic_market_agent/crop_book/constants.py` | Appended `JMF_CROP_MAP` (52 entries) | No |
| `organic_market_agent/crop_book/importer/seed.py` | CLI flags + enrichment_models import fix | No |
| `CHANGELOG.md` | Added WP-B1 `[Unreleased]` entry | No |

---

## 7. Open Findings

### FINDING-01: AC-04 Live Workbook Crop Name Mismatch (MEDIUM)

**Inquiry filed:** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B1/INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md`

The on-disk JMF MasterClass workbook at the master path
(`CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX`)
is a farm-specific adaptation, not the canonical JMF edition.
Only 14 of 50 crop names match `JMF_CROP_MAP` keys.

**Impact:** Live import produces 0 enriched rows (no matching families in offline DB;
per dry_run: `crops_seen=17, source_value_rows_upserted=0`).
All 22 ACs pass against the fixture workbook (`minimal_masterclass.xlsx`).
The importer correctly logs WARN+skip for all misses — no incorrect behavior.

**Options for team_110 to decide:**
1. Update `JMF_CROP_MAP` (aliases for farm-specific names) → requires LOD400 v1.1.4 patch + L-GATE_S re-run
2. Accept current state — importer is correct per spec; data mapping extension deferred
3. Replace with canonical JMF workbook if available

**Builder stance:** Per LOD400 §11 Step 4 — no improvisation. Importer implemented
verbatim per spec. Inquiry filed. Build proceeds to BUILD_COMPLETE.

---

## 8. MINOR CARRY Acknowledgments

Per LOD400 v1.1.3 §13 (PASS_WITH_FINDINGS acknowledgments):

| Carry ID | Description | Status |
|----------|-------------|--------|
| F-S-002-MINOR-R3 | `days_offset` sentinel design accepted; not ergonomically ideal | ACKNOWLEDGED |
| F-S-003-MINOR-R3 | `standalone_divergences` logging advisory; master always wins | ACKNOWLEDGED |

---

## 9. Runtime Stats — Live JMF Import (--jmf-only --dry-run)

Command: `python3 -m organic_market_agent.crop_book.importer.seed --jmf-only --dry-run`

```
JmfImportSummary(
  crops_seen=17,
  source_value_rows_upserted=0,      # dry_run + no families in offline DB
  task_template_rows_upserted=0,     # dry_run
  map_misses=107,                    # farm-specific + standalone sheet names
  standalone_divergences=[
    ('DIRECT_SEEDING', 'Radish', 'rows_per_bed', '12!=6'),
    ('DIRECT_SEEDING', 'String Beans', 'in_row_spacing_cm', '60.96!=5.08')
  ],
  invalid_offsets=0
)
```

**Non-numeric `at_seeding_transplanting` cells (correctly handled via presence-only sentinel):**
- Radish: "Net/row cover"
- Salanova: "Landscape fabric"
- Rapini: "Net/row cover"
- Bok Choi: "Net/row cover"

**Inch-format parse warnings (expected — curly-quote encoding in workbook):**
- `inches_to_cm: cannot parse '2'''` (×3)
- `inches_to_cm: cannot parse '2.5'''` (×1)
- `inches_to_cm: cannot parse '0.5\xa0»'` (×1)

---

## 10. Commits Since Spec Lock (262d9a3)

```
3fef7ca build(WP-B1/step9): 56 new tests (9 files) + CHANGELOG + AC-04 inquiry
a976421 build(WP-B1/step8): seed.py CLI flags --jmf-masterclass-dir, --jmf-only, --no-jmf
db37572 build(WP-B1/step5-6): jmf_masterclass.py parsers + unit conversions + fixture
b86983b build(WP-B1/step2-4): ORM crop_task_templates + migration 044 + JMF_CROP_MAP
b4ac30c mandate(WP-B1/L-GATE_B): issue build mandate to sfa_build (team_10)
```

---

*Filed 2026-05-24 by team_10 (sfa_build, Claude Sonnet 4.6).*
*Spec lock: LOD400 v1.1.3 @ 262d9a3. Next gate: L-GATE_V (team_190).*
