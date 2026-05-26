---
id: BUILD_REPORT_SFA-S003-P002-WP-B1-patch08
wp: SFA-S003-P002-WP-B1-patch08 — variety-parser cleanup (filter noise + DELETE existing)
gate: L-GATE_BUILD
status: BUILD_COMPLETE
author: team_10 (Claude Sonnet sub-agent)
date: 2026-05-26
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md
---

# BUILD_REPORT — SFA-S003-P002-WP-B1-patch08

## 1. Summary

Build complete. All 10 ACs satisfied. 4 files modified/created per locked scope.
The variety-parser filter (`_is_valid_cultivar_name` + `KNOWN_SECTION_HEADERS`) is
integrated into `_extract_cultivar_names`. The idempotent cleanup script is authored
and verified via dry-run + SQLite fixture. 1 new regression test added — integration
suite now 16 passed (was 15).

## 2. Files changed

| File | Status | Notes |
|------|--------|-------|
| `scripts/load_masterclass_sheets.py` | MODIFIED | Added `KNOWN_SECTION_HEADERS` frozenset (10 entries) + `_is_valid_cultivar_name` function + integrated filter into `_extract_cultivar_names` |
| `scripts/patch08_cleanup_noise_varieties.py` | CREATED | Idempotent DELETE script, dry-run default, SQLite + Postgres compatible |
| `tests/integration/test_load_masterclass_sheets.py` | MODIFIED | Appended `test_extract_cultivar_filter_rejects_noise` |
| `CHANGELOG.md` | MODIFIED | patch08 entry prepended to [Unreleased] |

## 3. AC verification

| AC | Description | Result |
|----|-------------|--------|
| AC-01 | `_is_valid_cultivar_name` exists in `load_masterclass_sheets.py` | PASS |
| AC-02 | `_extract_cultivar_names` calls the filter (filtered list returned) | PASS |
| AC-03 | `test_extract_cultivar_filter_rejects_noise` PASSES | PASS |
| AC-04 | Cleanup script dry-run reports planned deletions on SQLite fixture | PASS — 3 noise rows identified, dry-run output shown, no mutation |
| AC-05 | `--apply` is idempotent (2 runs → second is no-op) | PASS — second run: "No noise rows found — already clean" |
| AC-06 | After re-running loader, no noise inserted (spec correctness via filter unit test) | PASS — filter function verified to reject all noise patterns |
| AC-07 | Real cultivars (Carmen, Ace, Sprinter, Escamillo, etc.) pass filter | PASS — test asserts Carmen, Emerite, Marnero, Sprinter, Maxifort (rootstock) all pass |
| AC-08 | `pytest tests/integration/ -q` → 16 passed (was 15, +1 new) | PASS — 16 passed in 0.12s |
| AC-09 | `pytest tests/crop_book/ -q` → 350+1 OOS unchanged | PASS — 327 passed / 23 skipped / 1 pre-existing failure (test_dispatch_upload_crop_book_profile), unchanged |
| AC-10 | `validate_aos.sh` → 0 FAIL; diff scope 4 files | PASS — 29 PASS / 19 SKIP / 0 FAIL |

## 4. Test evidence

### Integration suite (AC-08)
```
16 passed in 0.12s
```

### Crop book suite (AC-09)
```
1 failed, 327 passed, 23 skipped, 41 warnings in 6.35s
FAILED tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile
(pre-existing failure — present since before B3 build; unrelated to patch08)
```

### validate_aos.sh (AC-10)
```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

### Cleanup script fixture test (AC-04 + AC-05)
```
DRY RUN: Found 3 noise variety row(s) — Cultivars, Intensive Spacing, https://example.com
          [DRY-RUN] Would delete 3 noise variety row(s). Exit code: 0
          Rows unchanged after dry-run: 5 (Carmen, Ace, Cultivars, Intensive Spacing, https://example.com)
APPLY 1:  Deleted 3 noise variety row(s). Rows after: Carmen, Ace
APPLY 2:  No noise rows found — already clean (idempotent no-op). Rows unchanged: Carmen, Ace
ALL ASSERTIONS PASSED (AC-04 + AC-05)
```

## 5. Key implementation decisions

- **KNOWN_SECTION_HEADERS check is FIRST** in `_is_valid_cultivar_name` (before length/URL/period checks), per spec §3.1 requirement that filter checks `KNOWN_SECTION_HEADERS` FIRST.
- **SQLite + Postgres dual compatibility** in cleanup script: `ANY(:ids)` for Postgres, `IN (...)` for SQLite via exception fallback. Enables test verification on SQLite fixtures without touching production.
- **`_extract_cultivar_names` refactor** is minimal: existing extraction loop preserved unchanged; filter applied as a list comprehension on the collected `cultivar_names` list before return.
- **Pre-existing dirty files untouched**: `.env.example`, team_190 verdict, and `data/jmf/extracted/jmf_book/` JSONs from prior operational runs remain unmodified.

## 6. Deferred (operational, post-L-GATE_V)

- Running `patch08_cleanup_noise_varieties.py --apply` on production Postgres (deletes ~11 noise rows).
- Re-running OP-2 (`scripts/load_masterclass_sheets.py --load-db`) on production to restore clean variety set (idempotent via ON CONFLICT).

---
*team_10 (Claude Sonnet sub-agent) — 2026-05-26*
*BUILD_COMPLETE — ready for team_190 L-GATE_V*
