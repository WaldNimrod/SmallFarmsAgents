---
artifact_type: BUILD_REPORT
work_package: SFA-S003-P001-WP002
team: team_10 (sfa_build)
date: 2026-05-08
commit: 9b26666
branch: claude/strange-mcnulty-651551
status: COMPLETE
---

# BUILD REPORT — SFA-S003-P001-WP002
## ספר גידולים — DB Migrations + Seed Importer

**Authorization:** L-GATE_S PASS — team_190 Round 2 (2026-05-08)
**DB status:** OFFLINE (ADR034 R9 protocol active throughout)
**Commit:** `9b26666`
**Branch:** `claude/strange-mcnulty-651551`

---

## Acceptance Criteria Matrix

| AC | Description | Status | Notes |
|----|-------------|--------|-------|
| AC-01 | English enum values for category, growth_cycle, harvest_unit, planting_method, harvest_stage in DB CHECK constraints | **PASS** | LOD400 v2.0.0 §3 mandates English. Migration 036 CHECK: `'vegetables','herbs','baby','legumes','fruits','fruit_trees','grains','cover_crops'`. Migration 037 CHECK: `'direct_sow','transplant','greenhouse_transplant','cutting','purchase'` / `'full_size','baby_leaf','head','plant_sale','seed'` / `'kg','bunch','head','case','unit','seedling'`. |
| AC-02 | All 6 SQLAlchemy ORM models importable and correctly defined | **PASS** | `test_models.py` 8/8 pass. All `__tablename__` verified. CHECK constraints and relationships confirmed. |
| AC-03 | Alembic migrations 035–040 form a valid chain | **PASS** | down_revision chain: 035→034, 036→035, 037→036, 038→037, 039→038, 040→039. Circular FK (crops↔conversion_groups) resolved via deferred `op.create_foreign_key()` in migration 039. |
| AC-04 | 5 LOD300 pilot crops seeded correctly; arugula DTM=21 (team_00 override) | **PASS** | `test_seed_idempotency.py::test_seed_populates_five_pilot_crops` PASS. `test_arugula_dtm_is_21` PASS. `TEAM00_DTM_OVERRIDES = {"ארוגולה": 21}`. |
| AC-05 | JMF empty directory handled gracefully | **PASS** | `jmf.py` logs `INFO: JMF XLSX directory yielded 0 rows or no files` and returns `[]`. Not a failure per LOD400 §5. |
| AC-06 | Seed is idempotent — running twice produces no duplicate rows | **PASS** | `test_seed_idempotency.py::test_seed_twice_no_duplicates` PASS. ORM-based `_get_or_create_*` pattern (select then insert-or-update). Compatible with SQLite and PostgreSQL. |
| AC-07 | All 4 test modules green (29 tests total) | **PASS** | `pytest tests/crop_book/ -v` → **29 passed, 0 failed, 0 skipped** |
| AC-08 | AOS validation 0 FAIL | **PASS** | `validate_aos.sh` → **29 PASS / 17 SKIP / 0 FAIL**. L-GATE_BUILD EXIT CRITERION: SATISFIED. |
| AC-09 | CLI `--help` exits 0; all flags present | **PASS** | `python -m organic_market_agent.crop_book.importer.seed --help` exits 0. Flags: `--all`, `--crops`, `--dry-run`, `--year`, `--source-dir`, `--jmf-dir`, `-v`. |

**Overall: 9/9 AC — ALL PASS**

---

## Files Created

### Alembic Migrations
| File | Description |
|------|-------------|
| `organic_market_agent/db/versions/035_crop_book_families.py` | `crop_families`: id, scientific_name (UNIQUE), name_he |
| `organic_market_agent/db/versions/036_crop_book_crops.py` | `crops`: 12 cols, category/growth_cycle/harvest_unit_default CHECK, deferred FK to conversion_groups |
| `organic_market_agent/db/versions/037_crop_book_varieties.py` | `crop_varieties`: 31 cols, planting_method/harvest_stage/harvest_unit CHECK, uq_cv_crop_name_en |
| `organic_market_agent/db/versions/038_crop_book_source_values.py` | `crop_variety_source_values`: uq_cvsv_variety_field_source, CASCADE delete |
| `organic_market_agent/db/versions/039_crop_book_conversion_groups.py` | `crop_conversion_groups` + deferred FK `fk_crops_conversion_group_id` |
| `organic_market_agent/db/versions/040_crop_book_unit_conversions.py` | `crop_unit_conversions`: chk_cuc_exclusion mutual-exclusion CHECK |

### ORM Models
| File | Contents |
|------|----------|
| `organic_market_agent/crop_book/models.py` | 6 classes: CropFamily, CropConversionGroup, Crop, CropVariety, CropVarietySourceValue, CropUnitConversion. BigInteger().with_variant(Integer(), "sqlite") PKs for SQLite test compatibility. |

### Importer Package
| File | Contents |
|------|----------|
| `organic_market_agent/crop_book/constants.py` | TEND_CROP_MAP (52 entries), TEND_FAMILY_MAP, CATEGORY_MAP, HARVEST_UNIT_MAP, GROWTH_CYCLE_MAP, PLANTING_METHOD_MAP, HARVEST_STAGE_MAP, TEAM00_DTM_OVERRIDES, OUTLIER_CROPS |
| `organic_market_agent/crop_book/importer/tend.py` | `parse_crop_plan()`, `parse_product_sold()`, `discover_tend_years()` |
| `organic_market_agent/crop_book/importer/jmf.py` | JMF XLSX parser; graceful empty-directory handling |
| `organic_market_agent/crop_book/importer/reconciler.py` | `reconcile_dtm()` (team_00 > JMF > Tend; OUTLIER_REJECTED), `reconcile_variety()` |
| `organic_market_agent/crop_book/importer/seed.py` | CLI orchestrator; seeds 23 families, 7 conversion groups, carrot overrides |

### Tests
| File | Tests | Result |
|------|-------|--------|
| `tests/crop_book/test_models.py` | 8 | PASS |
| `tests/crop_book/test_reconciler.py` | 9 | PASS |
| `tests/crop_book/test_tend_importer.py` | 8 | PASS |
| `tests/crop_book/test_seed_idempotency.py` | 4 | PASS |
| **Total** | **29** | **29 PASS / 0 FAIL** |

### Modified Files
| File | Change |
|------|--------|
| `organic_market_agent/models/__init__.py` | Added 6 crop_book model imports + `__all__` entries for Alembic autogenerate |
| `CHANGELOG.md` | Added S003 WP002 entry under [Unreleased] |

---

## Design Decisions and Deviations

| Decision | Rationale |
|----------|-----------|
| BigInteger().with_variant(Integer(), "sqlite") for PKs | SQLite only auto-increments INTEGER PRIMARY KEY (not BIGINT PRIMARY KEY). Migrations still use `sa.BigInteger()` for correct PostgreSQL DDL. |
| ORM-based upsert (select then insert/update) | Avoids PostgreSQL-only `ON CONFLICT` syntax; works in SQLite for idempotency tests (AC-06). |
| English enum values for all CHECK constraints | LOD400 v2.0.0 AC-01 is PRIMARY SPEC; LOD200 Hebrew labels are UI display only. |
| Deferred FK crops→crop_conversion_groups | Circular dependency: crops created in 036, conversion_groups in 039. FK added via `op.create_foreign_key()` at end of 039. |
| ללא_קבוצה group seeded with no CropUnitConversion row | LOD200 §4.7 defines no conversion for this group; carrot uses crop-specific overrides instead. |
| JMF directory empty — not a failure | LOD400 §5 explicitly permits; INFO log, return []. |

---

## Regression Verification

Pre-existing PostgreSQL failures (23 tests) due to offline DB schema mismatch (`sources.display_bucket` not in local DB) — confirmed pre-existing by `git stash` test. These failures exist on the base branch and are unrelated to WP002.

Non-DB tests: **237 passed**, 14 skipped — no regressions introduced.

---

## Routing

- **To:** team_00, team_100
- **Cc:** team_190 (for L-GATE_V scheduling)
- **Next step:** team_190 L-GATE_V (validator) — constitutional review of WP002 deliverables
