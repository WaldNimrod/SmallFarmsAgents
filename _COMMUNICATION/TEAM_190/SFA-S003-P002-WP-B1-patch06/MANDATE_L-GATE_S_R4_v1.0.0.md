---
id: MANDATE_SFA-S003-P002-WP-B1-patch06_L-GATE_S_R4_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch06
round: R4
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
spec_version: v1.0.3
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_R3_v1.0.0.md
prior_round_result: FAIL (1 BLOCKER — 2 functions live in separate files)
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190 — three distinct engines"
---

# L-GATE_S R4 — patch06 (file-location correction)

## 1. R3 Disposition
FAIL on 1 BLOCKER. team_190 correctly verified that the 2 superseded tests live in separate files:
- `test_ac04_live_workbook_coverage_min_42_of_50` → `tests/crop_book/test_jmf_live_workbook_coverage.py` (NOT `test_jmf_crop_map.py`)
- `test_ac07_seed_dry_run_warn_only_for_unmapped` → `tests/crop_book/test_jmf_seed_dry_run.py` (NOT `test_jmf_crop_map.py`)

My R3 amendment listed all 7 under `test_jmf_crop_map.py` — incorrect. Verified via `grep -lE` against current source.

## 2. R3→R4 spec changes (v1.0.2 → v1.0.3)

| Section | Change |
|---------|--------|
| **§2.1** | File list 4 → 6 (added `test_jmf_live_workbook_coverage.py` + `test_jmf_seed_dry_run.py`) |
| **§2.3** | LOCKED-scope listing: 5 functions remain under `test_jmf_crop_map.py`; 1 function under `test_jmf_live_workbook_coverage.py`; 1 function under `test_jmf_seed_dry_run.py` |
| **§3.4c** | REMOVE block split into 3 file-sections; added file-emptiness rule (if a file becomes empty after removal, delete the file) |
| **§8** | LOCKED inventory extended to list both new files explicitly |
| **Footer** | v1.0.3 R4 changelog entry |

No other change. Architecture, 60/6/12 arithmetic, Hebrew values, builder identity, ACs (still 15) — all unchanged.

## 3. Validation Criteria (R4 — focused on the file-location correction)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-R4-1 | Version bumped | `version: v1.0.3` |
| VC-R4-2 | §2.1 lists 6 modified files | Explicit mention of both `test_jmf_live_workbook_coverage.py` and `test_jmf_seed_dry_run.py` |
| VC-R4-3 | §2.3 correctly attributes each test to its file | `test_ac04_live_workbook_coverage_min_42_of_50` listed under `test_jmf_live_workbook_coverage.py`; `test_ac07_seed_dry_run_warn_only_for_unmapped` listed under `test_jmf_seed_dry_run.py`; the 5 other superseded tests remain under `test_jmf_crop_map.py` |
| VC-R4-4 | §3.4c split into 3 per-file blocks | One per source file. File-emptiness rule present. |
| VC-R4-5 | §8 LOCKED inventory lists both new files | Both files explicitly enumerated in §8 |
| VC-R4-6 | Functions exist in their stated files (pre-cleanup) | `grep -lE` confirms the 2 functions live in the cited files (not in `test_jmf_crop_map.py`) |
| VC-R4-7 | No regression of R3-passing content | The 5 tests still attributed to `test_jmf_crop_map.py`; the 9 patch02/patch03 KEEP-tests still preserved; §3.1 27-removal still intact; ACs unchanged |
| VC-R4-8 | validate_aos.sh clean | 0 FAIL |

## 4. Commands

```bash
# 1. Version
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
# Expected: version: v1.0.3

# 2. Confirm file locations of the 2 corrected tests
grep -lE "test_ac04_live_workbook_coverage_min_42_of_50" tests/crop_book/*.py
# Expected: tests/crop_book/test_jmf_live_workbook_coverage.py

grep -lE "test_ac07_seed_dry_run_warn_only_for_unmapped" tests/crop_book/*.py
# Expected: tests/crop_book/test_jmf_seed_dry_run.py

# 3. Confirm §2.1 file list updated
grep -nE "test_jmf_live_workbook_coverage|test_jmf_seed_dry_run" \
  _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md | head -10

# 4. Confirm §3.4c has 3 per-file blocks
sed -n '/^### 3.4c/,/^### 3.5/p' _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md

# 5. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 5. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_R4_v1.0.0.md`

Commit: `gate(WP-B1-patch06/L-GATE_S R4): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 dispatches Sonnet for incremental cleanup commit.
FAIL → R5.

---
