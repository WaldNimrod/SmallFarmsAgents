---
id: VERDICT_SFA-S003-P004-WP-CB-MIG_L-GATE_V_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-31
type: validation_verdict
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_V
artifact: _COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG/BUILD_REPORT_v1.0.0.md
coverage_snapshot: _COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG/COVERAGE_SNAPSHOT_CB1_v1.0.0.md
canon: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
lod400: _aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md
validator_engine: Codex / GPT-5 (non-Claude)
phase_owner: team_190
correction_cycle: R1
result: PASS_WITH_FINDINGS
---

# WP-CB-MIG L-GATE_V Verdict

```yaml
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_V
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS_WITH_FINDINGS
constitutional_checks: 4/4
ac_checks: 12/12
findings:
  - id: F-190-MIG-LV-01
    severity: MINOR
    summary: "Two test files named in the build report are present in the workspace but are not tracked by git."
    evidence: "git ls-files omits tests/crop_book/test_derive.py and tests/crop_book/test_field_registry.py; git ls-files --others --exclude-standard lists both files. The escalated pytest run included them from the working tree, but HEAD would not contain those tests."
notes:
  - "season_window data gap: crop_attribute has 0 season_window rows because planting_season was NULL for all varieties."
  - "nursery-trio violations: 50 rows where nursery_days_to_potting > days_in_nursery; logged as data/source semantic mismatch, not migration code failure."
summary: "Live DB and source validation passes the WP-CB-MIG L-GATE_V substance: canonical units/enums are clean, forbidden derived fields are absent from both source_values and enrichment after re-enrichment, crop_attribute is populated for available canonical attributes with season_window only absent as a data gap, old field names and dropped columns are gone, Alembic is at 059, the corrected views.py/engine.py dropped-column greps are empty, reconciler/enrichment_runner and roadmap constraints hold, pytest has only the two mandated pre-existing failures, and validate_aos has 0 FAIL. The only finding is a packaging/test-tracking issue: two tests listed by the build report are untracked and should be added or the report amended before treating the commit as fully self-contained."
```

## Evidence

### DB State

| Check | Result | Evidence |
|-------|--------|----------|
| AC-02 unit canonicality | PASS | Non-canonical query returned only `(NULL)|245`; grouped NULL-unit fields were categorical/list/open-vocab fields only, each with `count(value_numeric)=0`. No residual `celsius`/`C`/bare yield `kg`/`%`/`seeds/g`. |
| AC-03 enum canonicality | PASS | Both out-of-set queries for `frost_tolerance_class` and `planting_method` returned empty. |
| AC-05 derived fields eliminated | PASS | Both `crop_field_enrichment` and `crop_variety_source_values` returned empty for forbidden derived fields. This confirms the AC-05 corrective held after re-enrichment. |
| AC-04 crop_attribute populated | PASS with data-gap note | Present counts: `frost_tolerance_class` 41, `harvest_stage` 158, `harvest_unit` 157, `planting_method` 31, `rootstock_variety` 4, `sowing_months` 39, `storage_ethylene_sensitivity` 34, `transplant_months` 35, `variety_provider` 9. `season_window` has 0 rows due source-column NULLs. `storage_life_text` is correctly DERIVE/DROP, not a crop_attribute output. |
| AC-06 old names gone | PASS | Old-name query in `crop_field_enrichment` returned empty. |
| Alembic head | PASS | `python3 -m alembic current` returned `059 (head)`. |
| AC-08 dropped columns | PASS | Dropped-column query returned empty; `nursery_days_to_germinate` query returned one row. |
| AC-09 DQ storage_life_text | PASS | `SELECT count(*) ... field_name='storage_life_text'` returned `0`. |

### Consumer Code

| Check | Result | Evidence |
|-------|--------|----------|
| `views.py` dropped-column grep | PASS | Mandated grep returned empty. |
| `publisher/engine.py` dropped-column grep | PASS | Mandated grep returned empty. |

### Constitutional Checks

| Check | Result | Evidence |
|-------|--------|----------|
| `reconciler.py` untouched | PASS | `git diff a6df5f4 -- organic_market_agent/crop_book/importer/reconciler.py \| wc -l` returned `0`. |
| `enrichment_runner.py` untouched | PASS | `git diff a6df5f4 -- organic_market_agent/crop_book/importer/enrichment_runner.py \| wc -l` returned `0`. |
| IR#4 no roadmap edit in builder commit | PASS | `git show 0247a95 -- _aos/roadmap.yaml \| wc -l` returned `0`. |
| No production push in migration runner | PASS | `grep -rn "POST.*ingest" organic_market_agent/crop_book/canon/migrate.py` returned empty. |

### Tests

`python3 -m pytest tests/crop_book/ -q` was rerun outside the sandbox so the live DB integration test could connect to `127.0.0.1:5433`.

Result: `631 passed, 2 failed, 1 skipped`.

The two failures are the expected pre-existing failures named in the mandate:
- `tests/crop_book/test_source_registry.py::test_uc_prefix_requires_moderation`
- `tests/crop_book/test_ni_publisher_isolation.py::TestNiPublisherIsolation::test_ac21b_publisher_dir_clean`

`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returned `29 PASS / 19 SKIP / 0 FAIL`.

## Verdict

`PASS_WITH_FINDINGS`.

The runtime/data migration gate is satisfied, including the two team_100-caught corrective areas. Before LOD500 lock, team_100 should either add `tests/crop_book/test_derive.py` and `tests/crop_book/test_field_registry.py` to the commit or amend the build report/test-evidence claims so the locked artifact is self-contained.

-- team_190
