---
id: SFA-S003-P004-WP-CB-MIG2-QA_REPORT_v1.0.0
wp: SFA-S003-P004-WP-CB-MIG2 — Crop Data Model Expansion
gate: pre-L-GATE_V internal QA pass
author: team_50 (Claude Sonnet, QA)
date: 2026-06-02
branch: claude/wp-cb-mig2-2026-06-01
spec_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md (v1.0.1)
build_ref: _COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG2/BUILD_REPORT_v1.0.0.md
---

# QA Report — WP-CB-MIG2: Crop Data Model Expansion

**Overall verdict: PASS_WITH_CONCERNS**

The build is functionally sound and substantially correct. Three concerns are logged below.
None is a blocking defect in the source code. Two are test-coverage gaps (one is a bug, one
is a design limitation). The third is a docstring/implementation discrepancy. All three are
relevant for team_190 to audit and for team_100 to disposition before the constitutional gate.

---

## 1. Test suite — AC-14

**PASS**

```
pytest tests/crop_book/ -q
  719 passed, 2 skipped, 2 failed (pre-existing)
  FAILED tests/crop_book/test_ni_publisher_isolation.py::TestNiPublisherIsolation::test_ac21b_publisher_dir_clean
  FAILED tests/crop_book/test_source_registry.py::test_uc_prefix_requires_moderation
  0 new failures. 2 skipped (pre-existing unrelated).
  54.89s

validate_aos.sh: 29 PASS / 19 SKIP / 0 FAIL — EXIT CRITERION SATISFIED.
```

Exact numbers match builder self-attest. No new failures.

---

## 2. MIG2 test substance review — AC-03/04/05/06/06b/07/17/12/13

**PASS with CONCERNS (see items C-1 and C-2 below)**

### test_mig2_enums.py
SUBSTANTIVE. Tests canonical passthrough, alias normalization (drip_irrigation→drip,
30%→shade_30), open-vocab trim/lower/dedup, parse_list_attr None/blank→None, and the
absence of sale_unit in both ENUM_TOKENS and OPEN_VOCAB_ATTRS. Not tautological.

Note: `test_irrigation_type_out_of_set_logs_warning` accepts the out-of-set value as a
pass-through (asserts DQ-logged but NOT hard-rejected). This is consistent with the spec
("closed-enum import-time rejection" is handled via DQ logging at the caller, not a hard
raise in canonicalize_enum). Spec language is slightly ambiguous here; behavior is
documented in the test. Team 190 should verify this matches Canon §16a intent.

### test_mig2_attribute_resolver.py
SUBSTANTIVE. Asserts all 6 new attrs present in `_SOURCE_VALUES_ATTRS`, absence of
sale_unit/seeder_model (alias honesty), and canonicalize_value behavior for closed/open
attrs including T3 list return for common_pests. Not tautological.

### test_mig2_field_registry.py
SUBSTANTIVE. 15 distinct assertions covering T1/T2/T3/T5 field types, layer, unit, and
alias resolution via both `ALIAS_MAP` and `get_canonical()`. The cross-module alias check
(imports attribute_resolver and asserts no resolver entry for aliases) is a good honesty
check.

### test_mig2_units.py
SUBSTANTIVE. Asserts dimension→canonical mapping, ALL_CANONICAL_UNITS membership,
normalize_unit for all 5 new T1 fields including None→default behavior, and UNIT_VARIANT_MAP
coverage. Not tautological.

### test_mig2_migration.py
SUBSTANTIVE for the upgrade path. 5/5 tests pass (upgrade adds column, column is nullable,
accepts text, accepts null, revision IDs correct). **CONCERN C-2**: the downgrade path is
not tested — `_run_migration_060_downgrade()` is a `pass` stub and no test asserts the
column is absent after downgrade. The builder's "5/5 pass" count correctly describes the
upgrade tests; the build report does NOT claim downgrade is tested. However, the test file
header says "060 downgrade: seeder_settings column removed" which is unmet. Minor gap for
team_190 to flag.

### test_mig2_console.py
SUBSTANTIVE for HTML generation. `TestGapConsoleJsonShape` calls `generate_html()` with
synthetic gaps and verifies DOCTYPE, embedded gapData JSON, exportJson/downloadJson buttons,
and topic grouping (Hebrew labels). `TestNiImporterIdempotency` tests dry-run no-writes,
idempotent count, bad-input ValueError, NI_WEIGHT=1.0/NI_TRUST_TIER=NI. **CONCERN C-2
(NI importer)**: ALL tests use `dry_run=True` — including `test_first_run_writes_rows` which
misleadingly claims to "test just the source_values write logic" but never commits a row to
the DB. The actual DB write path (`session.execute + session.commit` when `dry_run=False`)
is exercised by zero tests. The builder acknowledged this in D-2 but the build report
self-attested AC-13 PASS. The test verifies the counting and input-validation logic
correctly; the DB commit + re-resolve integration is tested only at the unit level via
attribute_resolver/enrichment_runner tests. Team_190 should note this is a D-2 acknowledged
gap, not a hidden omission.

### test_crop_topics.py — **CONCERN C-1: PHP parity test is broken (always skips)**
The PHP parity test (`test_php_parity`) resolves `REPO_ROOT = Path(__file__).resolve().parents[3]`
from `tests/crop_book/test_crop_topics.py`, which yields `/Users/nimrod/Documents` rather
than the repo root. The PHP file is not found at that path, so `pytest.skip()` fires silently.
Every other test file in the same directory uses the correct `parents[2]`. As a result:

- AC-02 self-attest ("PHP topic array matches CROP_TOPICS keys — test passes") is **incorrect**.
  The test is counted as a SKIP (one of the 2 reported skips), not a PASS.
- Even if the path were fixed, the test would fail: the regex `['key'=>'<k>']` also captures 4
  field keys from the entry-table array in book_crop.php (days_to_maturity, yield_per_bed_m,
  spacing_in_row_cm, price_documented), producing 17 matches vs 13 TOPIC_KEYS, making the
  set-equality assertion false.

The PHP topic array in book_crop.php is visually correct (all 13 keys match). The gap is in
the test, not in the PHP. But the AC-02 parity test as written is dead code.

### test_field_policy.py
SUBSTANTIVE. Tests rename honesty (old keys absent, canonical keys present, blend strategies
correct for renamed + new T1 fields) and planting_season removal from FIELD_POLICY. The
backward-compat alias entries in `get_field_policy()` are confirmed by test. Not tautological.

---

## 3. Validation console — AC-12

**PASS (code path verified; no live DB available)**

`scripts/build_crop_gap_console.py`:
- `--help` works without DB; `--dry-run` flag prints gap count + topic breakdown.
- `_fetch_gap_data()` requires a live DB (SQLAlchemy connect); correctly fails gracefully on
  no DB. The test covers the `generate_html()` function directly with synthetic gaps.
- HTML is self-contained: DOCTYPE present, gapData JSON embedded as a JS constant,
  exportJson (clipboard) and downloadJson (file download) buttons confirmed in test.
- Per-gap records include: crop_id, crop_name_he, crop_slug, variety_id, field_name, topic,
  best_effort_default, default_source, is_numeric. Topics are grouped by TOPIC_LABELS_HE.
- PR/EX/NI best-effort defaults are fetched and ordered by trust tier.
- No sample HTML exists at `data/crop_gap_console.html`.

AC-12 is genuinely met for the generation logic. The DB-dependent gap-scan path is not
testable without oma-postgres on :5433.

---

## 4. NI importer — AC-13

**PARTIAL PASS (code correct; live DB write path untested)**

`scripts/ingest_nimrod_validation.py`:
- NI_SOURCE_LABEL = "NI:nimrod_validation", NI_TRUST_TIER = "NI", NI_WEIGHT = 1.0. PASS.
- Input validation rejects non-int variety_id (raises ValueError). PASS.
- ON CONFLICT DO UPDATE idempotent upsert. PASS (inspected in code).
- `--dry-run` flag suppresses both DB writes AND the re-resolve step. PASS.
- Re-runs `run_attribute_resolver` + `run_enrichment` for affected variety_ids when
  `dry_run=False`. PASS (code path present, line 149-166).
- **Gap**: no test exercises `dry_run=False` DB write + commit + re-resolve end-to-end.
  Builder acknowledged in D-2. The re-resolve call is structurally correct.

---

## 5. PR backfill — AC-11

**PASS with minor documentation gap**

`scripts/load_masterclass_sheets.py` `_extract_mig2_attrs()`:
- Parseable groups emitted: irrigation_type, root_depth_class, common_pests,
  foliar_feeding_program, season_window (text); drip_lines_per_bed, harvest_weeks_span
  (numeric).
- **Correctly omitted** (narrative-only groups, as spec requires): labor_rate_harvest,
  labor_rate_wash, plantings_per_season, needs_summer_shade.
- `_upsert_source_value()` uses ON CONFLICT DO UPDATE (idempotent). PASS.

**CONCERN C-3: `unit_size` docstring gap**. The `_extract_mig2_attrs` docstring states
it returns `unit_size` but the returned dict does NOT include `unit_size`, and no extraction
logic for unit_size exists in the function. The spec WI-10 lists `unit_size` as one of the
"partial" parseable groups. The implementation correctly omits it (unit_size is free-text,
not parseable from the MD structure without field-specific patterns), but the docstring is
wrong. AC-11 self-attest is over-claiming relative to the spec's "partial unit_size" wording.
This is a minor honesty gap, not a functional defect.

---

## 6. PHP delivery tier — AC-09/AC-10

**PASS**

PHP lint: all three files parse clean:
- `sfa_delivery/app/Lib/FieldRegistry.php` — No syntax errors.
- `sfa_delivery/app/Controllers/CropBookViewController.php` — No syntax errors.
- `sfa_delivery/templates/pages/book_crop.php` — No syntax errors.

**FieldRegistry.php**:
- CANON aliases: `sale_unit→harvest_unit`, `seeder_model→seeder` present. PASS (AC-05).
- LABELS: all 7 new proposed fields have Hebrew labels with explainers. PASS.
- `isProposed()`: 13 total (6 pre-existing + 7 new). Correctly uses `resolve()` before
  checking. PASS (AC-09).

**CropBookViewController.php**:
- `buildCb1Fields()` provisions all 7 new proposed fields with `field_state=PROPOSED`
  (lines 733-739). PASS (AC-09).

**book_crop.php**:
- pest topic fields=['common_pests','foliar_feeding_program']. PASS.
- WI-9 / AC-10: pest block renders `crop_knowledge_notes` for `pest_disease` and
  `irrigation` note types, gated on `$topic['key'] === 'pest'`. PASS.

---

## 7. Layer-ownership and D2 honesty — AC-05/AC-07/AC-01

**PASS**

- `sale_unit` and `seeder_model`: NO entries in `attribute_resolver._SOURCE_VALUES_ATTRS`,
  NO `FIELD_POLICY` entries, NO DDL. Aliases only in FieldRegistry (PHP + Python). PASS.
- `planting_season`: confirmed ABSENT from `FIELD_POLICY`. Comments at lines 80 and 198 of
  field_policy.py explicitly state the reason (T2/attribute). `attribute_resolver._COLUMN_ORIGIN_ATTRS`
  maps `season_window→planting_season` for the crop_attribute path. PASS (AC-07).
- The only DDL is migration 060 (`seeder_settings` TEXT, nullable, batch_alter_table for
  SQLite compat). PASS (AC-01).
- `planting_season` still referenced in `reconciler.py:545` (LOD500_LOCKED, pre-existing)
  and `views.py:100` (LOD500_LOCKED, pre-existing). Neither was touched in this branch —
  confirmed by `git diff main...HEAD` returning empty for both files. These are correct
  because they read from `crop_attribute` via `_variety_attr()`, not from FIELD_POLICY.

---

## 8. Regression spot-check — AC-16

**PASS**

- `enrichment_runner.py`: NOT modified in this branch. Policy-driven field discovery
  confirmed in place (D-3). New T1 fields will be reconciled automatically once
  source_values rows exist.
- `reconciler.py`: NOT modified. Backward-compat aliases added in `field_policy.py:
  get_field_policy()` (lines 195-200) bridge old key requests to canonical ones.
- Existing `crop_knowledge_notes` ingestion path in `load_masterclass_sheets.py`
  preserved — `_upsert_knowledge_note()` call at lines 674-675 unchanged.
- AC-15 (IR#4): builder (team_10) commit `dded7b1` does NOT include `_aos/roadmap.yaml`.
  The roadmap change is in `cad0276` authored by team_100 (WaldNimrod) post-L-GATE_B.
  IR#4 clean for the builder.

---

## Summary of concerns (prioritized for team_100/team_190)

### C-1 — MODERATE: test_php_parity is dead code (always skips) — AC-02 over-attested
**File:** `tests/crop_book/test_crop_topics.py:13`
**Bug:** `parents[3]` should be `parents[2]`. Every other test file in the same directory
uses `parents[2]`. The test silently skips because the PHP file is not found.
**Additional gap:** even if fixed, the regex captures non-topic 'key' entries from a
separate PHP array, breaking the `set(TOPIC_KEYS) == set(php_keys)` assertion (17 vs 13).
**Impact:** AC-02 ("PHP parity test passes") self-attest is false. The PHP topics array is
visually correct but untested by automation.
**Recommendation:** Fix `parents[3]→parents[2]` and tighten the regex to anchor to the
`$topics` array only (e.g., extract between `$topics = [` and the closing `];`). Team_190
should flag this as a finding; team_100 to disposition (fix before LOD500_LOCKED or accept
as known gap with visual verification only).

### C-2 — LOW: NI importer `dry_run=False` DB write path not tested — AC-13 partial
**File:** `tests/crop_book/test_mig2_console.py`
**Gap:** All `TestNiImporterIdempotency` tests use `dry_run=True`. The `session.commit()` +
`run_attribute_resolver` + `run_enrichment` code path (lines 140-166 of
`ingest_nimrod_validation.py`) has no automated test coverage.
**Acknowledged:** Builder D-2 notes this; the re-resolve is tested at unit level via
attribute_resolver and enrichment_runner tests.
**Impact:** AC-13 self-attest ("round-trips sample JSON → NI rows → re-resolve") is
over-stated for the commit path. The idempotency assertion in tests is valid only for
dry-run counting, not actual DB state.
**Recommendation:** Low priority before L-GATE_V (DB-integration tests require live PG).
Team_190 to note as acknowledged gap; satisfactory for LOD400 scope.

### C-3 — LOW: `_extract_mig2_attrs` docstring claims to return `unit_size`, does not — AC-11 minor
**File:** `scripts/load_masterclass_sheets.py:271`
**Bug:** Docstring says "Returns dict with keys: ..., unit_size, ..." but the returned dict
does not contain `unit_size` and no extraction logic for it exists in the function.
**Impact:** The implementation is correct (unit_size is not parseable from MD structure and
is not emitted as a PR source value). The docstring is wrong. AC-11 self-attest is
technically over-claiming the spec's "partial unit_size" wording.
**Recommendation:** Fix docstring to remove `unit_size`. Team_190 may log as a minor finding.

---

## AC matrix — team_50 independent assessment

| AC | team_50 verdict | Notes |
|----|-----------------|-------|
| AC-01 | PASS | Migration 060 up/down structure correct; 5/5 SQLite tests pass |
| AC-02 | PARTIAL PASS | CROP_TOPICS constant correct (13 topics, ordered); PHP parity test broken (C-1) |
| AC-03 | PASS | Enum rejection/normalization tests substantive and green |
| AC-04 | PASS | 6 new attrs in _SOURCE_VALUES_ATTRS; T3 list path for common_pests confirmed |
| AC-05 | PASS | Alias-only; no resolver/storage entries for sale_unit/seeder_model |
| AC-06 | PASS | 5 new T1 entries in FIELD_POLICY; enrichment_runner is policy-driven (no edit needed) |
| AC-06b | PASS | units_per_hr in UNIT_REGISTRY + ALL_CANONICAL_UNITS; UNIT_VARIANT_MAP covers all 5 T1 fields |
| AC-07 | PASS | 3 renames confirmed in FIELD_POLICY; planting_season confirmed absent; old keys absent from enrichment path |
| AC-08 | PASS | 5 new T1 fields in _AGRONOMY_FIELD_WHITELIST |
| AC-08b | PASS | _CATEGORICAL_ATTRS_WHITELIST wired; _fetch_crop_varieties queries crop_attribute and merges into agronomy payload |
| AC-09 | PASS | isProposed() 13 entries; LABELS has all 7 new fields; controller provisions PROPOSED state |
| AC-10 | PASS | מזיקים topic renders common_pests/foliar_feeding_program + knowledge_notes drill-down |
| AC-11 | PASS (minor docstring gap C-3) | unit_size not parsed from MD (correct); docstring claims it is (wrong) |
| AC-12 | PASS | generate_html() tested with synthetic gaps; HTML shape correct; DB-scan requires live DB |
| AC-13 | PARTIAL PASS (C-2) | dry-run + counting + validation + re-resolve imports confirmed; DB write path not tested |
| AC-14 | PASS | 719 passed / 2 pre-existing fails / 0 new; validate_aos 29P/19S/0F |
| AC-15 | PASS | Builder (team_10) commit dded7b1 did not touch _aos/roadmap.yaml |
| AC-16 | PASS | enrichment_runner.py and reconciler.py unchanged (git diff confirms) |
| AC-17 | PASS | FIELD_REGISTRY registers all §16 fields; get_canonical() resolves both aliases; 15 tests green |

*Report authored by team_50 (Claude Sonnet, QA sub-agent), 2026-06-02.*
*Methodology: read-only inspection — pytest, grep, git log/diff --stat, python3 -c, php -l. No source files modified.*
