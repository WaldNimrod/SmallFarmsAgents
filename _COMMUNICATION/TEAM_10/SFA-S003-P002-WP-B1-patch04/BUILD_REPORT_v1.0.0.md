---
spec_version: v1.0.1
build_commit: a0397cd
status: BUILD_COMPLETE
engine: Sonnet (claude-sonnet-4-6)
team: team_10
date: 2026-05-25
wp: SFA-S003-P002-WP-B1-patch04
lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04/LOD400_spec.md
---

# BUILD_REPORT — SFA-S003-P002-WP-B1-patch04

## 1. Per-AC PASS Table (all 22)

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-01 | `JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"` | PASS | `test_ginger_baseline_post_patch04` |
| AC-02 | `"ג'ינג'ר" in JMF_CROP_MAP.values()` | PASS | `test_ginger_baseline_post_patch04` |
| AC-03 | `len(JMF_CROP_MAP) == 87` | PASS | `test_jmf_crop_map_count` (updated 86→87) |
| AC-04 | Migration 047 upgrade returns success | PASS | `TestMigration047Upgrade.test_migration_047_upgrade_creates_table` |
| AC-05 | Table `crop_knowledge_notes_crops` with (note_id, crop_id) | PASS | `TestMigration047Upgrade.test_migration_047_upgrade_creates_table` |
| AC-06 | Index `ix_ckn_crops_crop_id` exists | PASS | `TestMigration047Upgrade.test_migration_047_index_exists` |
| AC-07 | `alembic downgrade 046` cleanly reverses | PASS | `TestMigration047Downgrade.test_migration_047_downgrade_reverses` |
| AC-08 | ORM `crops_linked` relationship defined; SQL semantics verified | PASS | `TestJunctionORM.test_junction_orm_relationship_returns_crops` |
| AC-09 | Cascade delete: note deletion cascades to junction rows | PASS | `TestJunctionCascade.test_junction_cascade_delete_on_crop` |
| AC-10 | `--dry-run` parses all processable MDs without error | PASS | `TestLoaderDryRun.test_load_masterclass_dryrun_parses_all_37` |
| AC-11 | `--load-db` produces 24 JSON files at `data/jmf/extracted/jmf_book/` | PASS | 24 files present post-commit |
| AC-12 | Each JSON conforms to WP-B2 schema | PASS | `TestJSONSchemaValid.test_load_masterclass_produces_valid_json_schema` |
| AC-13 | Every `body_text` ≤ 2000 chars | PASS | `TestBodyTextTruncation.*` (2 tests) |
| AC-14 | `is_internal_farm_use_only` = true on every record | PASS | `TestInternalFlagOnAllRecords.test_load_masterclass_all_records_internal_flag` |
| AC-15 | `--dry-run` reports per-row impact without mutation | PASS | `TestPatch03DataFixDryRun.test_patch03_data_fix_dryrun_reports_correctly` |
| AC-16 | Script idempotent (second run → 0 row changes) | PASS | `TestPatch03DataFixIdempotent.test_patch03_data_fix_idempotent` |
| AC-17 | Missing-row-set handled gracefully (0 rows, no error) | PASS | `TestPatch03DataFixIdempotent.test_patch03_data_fix_missing_row_tolerance` |
| AC-18 | `pytest tests/crop_book/ -q` → 355 passed + 1 pre-existing failure | PASS | 355 passed, 1 FAILED (wp_upload OOS) |
| AC-19 | `pytest tests/integration/ -q` → all 13 new tests pass | PASS | 13 passed |
| AC-20 | `validate_aos.sh` → 0 FAIL | PASS | 29 PASS / 19 SKIP / 0 FAIL |
| AC-21 | Diff scope — changes only in §2.1+§2.2 + data files + index.json | PASS | See §2 below |
| AC-22 | 24-group duplicate-target allowlist UNCHANGED | PASS | `test_jmf_crop_map_duplicate_target_allowlist` unchanged |

---

## 2. Files Modified / Created (diff stats)

**NEW files (5 code + 24 data + 2 test infra = 31):**
```
organic_market_agent/crop_book/crop_knowledge_notes_crops.py   (+26 lines)
organic_market_agent/db/versions/047_create_crop_knowledge_notes_crops_junction.py  (+54 lines)
scripts/load_masterclass_sheets.py                              (+330 lines)
scripts/patch03_data_fix.py                                     (+145 lines)
tests/integration/__init__.py                                   (empty)
tests/integration/test_load_masterclass_sheets.py               (+390 lines)
data/jmf/extracted/jmf_book/[24 JSON files]                    (data)
```

**MODIFIED files (6):**
```
organic_market_agent/crop_book/__init__.py                      (+5 lines, was empty)
organic_market_agent/crop_book/constants.py                     (+4 lines: Ginger + comment)
organic_market_agent/crop_book/crop_knowledge_notes.py          (+8 lines: relationship + import)
organic_market_agent/crop_book/models.py                        (+6 lines: knowledge_notes_linked)
tests/crop_book/test_jmf_crop_map.py                            (+9 lines: Ginger regression test)
tests/crop_book/test_jmf_crop_map_aliases.py                    (+2 lines: count 86→87)
CHANGELOG.md                                                     (+8 lines: patch04 entry)
documentation/jmf_masterclass_crop_sheets/_index.json           (Ginger entry: english_keys + status)
```

**Total build commit:** 38 files changed, 2403 insertions(+), 9 deletions(-)

**Note on `test_jmf_crop_map_aliases.py`:** Updated `test_alias_entry_count_grew_by_34` from 86→87 to satisfy AC-03 (`len(JMF_CROP_MAP) == 87`). This is a count test, not one of the locked 24-group semantic tests. The 24-group tests (`test_jmf_crop_map_duplicate_target_allowlist`, `test_ac03_duplicate_group_count`) are UNCHANGED — Ginger creates a new unique Hebrew value so it does not affect duplicate target groups.

---

## 3. Test Results

### crop_book suite (AC-18):
```
pytest tests/crop_book/ -q
1 failed, 355 passed, 42 warnings
FAILED: tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile
  → pre-existing publisher failure (OOS — do not fix)
```

### integration suite (AC-19):
```
pytest tests/integration/ -q
13 passed
```

### Combined:
```
pytest tests/crop_book/ tests/integration/ -q
1 failed, 368 passed
```

---

## 4. Data Delivered

| Item | Count | Notes |
|------|-------|-------|
| JSON cache files | 24 | at `data/jmf/extracted/jmf_book/` |
| Sheets processed | 28 | from 37 total MDs (28 have JMF_CROP_MAP keys) |
| Sheets skipped | 9 | NEW_CROP_OR_VARIANT status: hot pepper / tomato variants (patch06 scope), מיזונה וחרדל, מלפפון חממה sub-variant, etc. |
| DB notes rows (SQLite test) | ~55–70 | (notes_count varies by sheet; each sheet produces 2-4 notes) |
| DB variety rows (SQLite test) | ~20 | extracted from CULTIVARS sections (Ginger: 2, Peppers-greenhouse: 8, Beans-Pole: 10) |

**JSON schema:** All 24 files conform to WP-B2 schema (`schema_version: "1.0"`, `is_internal_farm_use_only: true`, all `body_text` ≤ 2000 chars).

**Why 24 JSON files instead of ~37:** 28 processable sheets map to 24 unique `crop_jmf_en` keys (e.g., Carrots has 2 sheets: "גזר איחסון" + "גזר טרי"; both PARTIAL_MATCH to Carrots → same `Carrots.json`). The last-processed sheet wins for duplicate crops. This is correct behavior per the caching design.

---

## 5. Script Execution Probes

### load_masterclass_sheets.py --dry-run:
```
SUMMARY: 28 processable, 9 skipped
  79 truncation warning(s)
  SKIP: 038-ft-finale-pimentfort-eng-220613-142647.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 041-document-041.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 046-ooy.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 056-eouio-oyono.md — ...NEW_CROP_OR_VARIANT... (storage/washing — cross-crop sheet)
  SKIP: 060-nouo.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 061-oaoo-oo.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 062-oaoo-uo.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 063-oaoo-yu-nou.md — ...NEW_CROP_OR_VARIANT...
  SKIP: 070-ouoao-ouo.md — ...NEW_CROP_OR_VARIANT...
Dry-run complete — no files written.
```
Exit code: 0.

### patch03_data_fix.py --dry-run (SQLite fixture):
Tested via `TestPatch03DataFixDryRun.test_patch03_data_fix_dryrun_reports_correctly`:
- Reports "[DRY-RUN] 'גזר לבן' → 'שורש פטרוזילה': 1 row(s) would be updated"
- No mutation confirmed (row verified present after dry-run)
- Exit code: 0

(Direct CLI invocation against live Postgres omitted — production DB mutation is out of build scope per LOD400 §6. Integration test against SQLite fixture confirms behavior.)

---

## 6. Migration 047 Upgrade + Downgrade Test Results

```
pytest tests/integration/test_load_masterclass_sheets.py::TestMigration047Upgrade \
       tests/integration/test_load_masterclass_sheets.py::TestMigration047Downgrade -v

PASSED TestMigration047Upgrade::test_migration_047_upgrade_creates_table
PASSED TestMigration047Upgrade::test_migration_047_index_exists
PASSED TestMigration047Downgrade::test_migration_047_downgrade_reverses
```

All SQLite in-memory, no live Postgres touched per IR discipline.

---

## 7. validate_aos.sh Result

```
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## 8. Notes / Observations / Deferred Items

### 8.1 JSON file count (24 vs "~37")
The LOD400 estimates ~37 JSON files. Actual: 24 unique files from 28 processable sheets. Reason: multiple MDs share the same `crop_jmf_en` primary key (Carrots: 2 sheets, Lettuce: 3 sheets, Peppers: 2 sheets, Fennel: 2 sheets). The last-processed sheet's data overwrites earlier entries in the JSON file. This is expected behavior per the caching schema design.

### 8.2 Ginger in _index.json
Sheet 050 had `english_keys: []` and `status: NEW_CROP_OR_VARIANT` in `_index.json` because it was generated before Ginger was added to JMF_CROP_MAP. Updated `_index.json` to add `"Ginger"` as english_key and status `MATCHED_PATCH04`.

### 8.3 crop_book/__init__.py
Was empty before patch04. Now exports `CropKnowledgeNote` + `crop_knowledge_notes_crops` to ensure both tables are registered in `Base.metadata` when the crop_book package is imported. This prevented `NoReferencedTableError` in `seed.py --dry-run` tests (which call `Base.metadata.create_all()`).

### 8.4 test_jmf_crop_map_aliases.py update
`test_alias_entry_count_grew_by_34` updated from 86→87. This is a count test (not the locked 24-group semantic test). AC-22 (24-group dict unchanged) confirmed passing.

### 8.5 Deferred to patch06
- 27 entries to remove from JMF_CROP_MAP (22 cultivars + 5 typos)
- Revert patch03 `מלפפון חממה` to `מלפפון`
- Update 24-group tests to 3-group
- DB production data-fix (patch03_data_fix.py --apply): safe to run post-patch04 LOD500_LOCKED against production Postgres

### 8.6 sheet 056 (storage/washing cross-crop note)
Skipped in this build because it has no `english_keys` in `_index.json`. The DECISION §2.4 OP-04 schema (junction table) is implemented but sheet 056 loading is deferred — would require adding cross-crop logic to the loader or manually mapping it. The junction infrastructure (Migration 047 + ORM) is ready.
