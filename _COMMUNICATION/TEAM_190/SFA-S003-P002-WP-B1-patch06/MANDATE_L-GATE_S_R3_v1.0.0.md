---
id: MANDATE_SFA-S003-P002-WP-B1-patch06_L-GATE_S_R3_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch06
round: R3
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
spec_version: v1.0.2
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_R2_v1.0.0.md
prior_round_result: PASS clean (R2)
trigger: "Sonnet build (113b47d) ran successfully under v1.0.1 spec — 15/15 ACs PASS, Counter probe 60/6/12 — but reported 7 non-LOCKED consequence-failures (BUILD_REPORT v1.0.0 at commit 6801e64). Sonnet correctly did NOT extend scope. Same pattern as patch03 R3+R4."
build_commit: 113b47d
report_commit: 6801e64
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 ≠ team_10 Sonnet ≠ team_190 GPT-5.5 — three distinct engines"
---

# L-GATE_S R3 — patch06 (spec amendment for 7 superseded tests)

## 1. Why R3 (not just dispatch / not L-GATE_V)

R2 was PASS clean. Sonnet built per v1.0.1 (commit `113b47d`) and reported 7 non-LOCKED test failures as **expected consequences** of the cleanup — tests that hardcoded values for removed keys (5 patch02/patch03 regression tests + 1 patch01 typo-alias test + 1 patch01 workbook-coverage achievement test). Sonnet correctly STOPPED at scope boundary — the failing tests were NOT in the v1.0.1 §2.2 LOCKED scope exception.

The fix is the same pattern as patch03 R3+R4: extend the LOCKED scope exception to cover the 7 superseded tests with REMOVE directive, then Sonnet does an incremental cleanup commit.

## 2. R2→R3 spec changes (v1.0.1 → v1.0.2)

| Section | Change |
|---------|--------|
| **§2.3** | Extended LOCKED scope exception to enumerate 7 additional functions in `test_jmf_crop_map.py` (all REMOVE) |
| **§3.4c NEW** | Specifies the 7 function-block removals byte-exactly |
| **Footer changelog** | v1.0.2 R3 entry appended |

The 7 tests (all `tests/crop_book/test_jmf_crop_map.py`):
1. `test_ac04_1_eggplant_feld_literal_alias` — REMOVE (asserts removed key `"Eggplant  (Feld)"` in MAP)
2. `test_mesclun_value_post_patch03` — REMOVE (asserts removed `Mesclun → עלי בייבי`)
3. `test_salad_mix_value_post_patch03` — REMOVE (same)
4. `test_baby_kale_value_post_patch03` — REMOVE (same)
5. `test_lebanese_cucumber_value_post_patch03` — REMOVE (asserts removed `Greenhouse Libanese Cucumber`)
6. `test_ac04_live_workbook_coverage_min_42_of_50` — REMOVE (patch01 coverage achievement semantically obsolete under baselines-only policy)
7. `test_ac07_seed_dry_run_warn_only_for_unmapped` — REMOVE (premise inverted: post-patch06 the removed keys LEGITIMATELY produce WARN; the pre-patch06 "should pass without warn" assertion no longer holds)

All 7 removals are subsumed by patch06's existing new tests (§3.5):
- `test_no_cultivar_keys_in_map_post_patch06` covers #1-5 (asserts removed keys ABSENT)
- `test_no_typo_keys_in_map_post_patch06` covers #1 (specifically)
- `test_six_synonym_groups_exact` covers structural integrity

For #6-7 (workbook coverage + seed-warn): these test PRE-patch06 importer behavior that has changed deliberately. Coverage is now baselines-only (no aliases to inflate). seed.py warning on unmapped workbook strings is now CORRECT behavior. The tests themselves no longer reflect intent → REMOVE.

NO other change. Architecture, Hebrew values, 6-group dict, builder identity, ACs (still 15), risk register — all preserved.

## 3. Validation Criteria (R3 — focused)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-R3-1 | Version bumped | `version: v1.0.2` |
| VC-R3-2 | §2.3 lists 7 NEW LOCKED-scope tests | Verify all 7 function names present in §2.3 with REMOVE directive |
| VC-R3-3 | §3.4c NEW exists | §3.4c block specifies the 7 removals byte-exact + clarification that other patch02/patch03 regression tests (Parsnips, Shallots, Cherry, Heirloom, Chinese Cabbage, Hot Pepper, Beans Bush, Snow Peas, Basil) STAY UNCHANGED (their keys are baselines, not removed) |
| VC-R3-4 | Sonnet build commit identified | Frontmatter cites `build_commit: 113b47d` + BUILD_REPORT at `6801e64` |
| VC-R3-5 | Removal coverage subsumed | The 5 cultivar-value tests are covered by `test_no_cultivar_keys_in_map_post_patch06`; the 1 typo test by `test_no_typo_keys_in_map_post_patch06`; the 2 workbook-coverage/seed-warn tests are SEMANTICALLY obsolete (no replacement needed) |
| VC-R3-6 | No regression on R2 PASS content | §3.1 (27 removals), §3.2-3.4b (LOCKED test updates), §3.5 (3 new regression tests), §3.6 (alias-file 2 updates + 1 removal), §3.7 (cleanup script), §3.8 (CHANGELOG), §4 ACs all unchanged from v1.0.1 |
| VC-R3-7 | Footer changelog | v1.0.2 R3 entry present, references BUILD_REPORT + commit hash |
| VC-R3-8 | validate_aos.sh | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL |

## 4. Required Commands

```bash
# 1. Version + scope
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
grep -nE "test_ac04_1_eggplant_feld|test_mesclun_value_post_patch03|test_salad_mix_value_post_patch03|test_baby_kale_value_post_patch03|test_lebanese_cucumber_value_post_patch03|test_ac04_live_workbook_coverage|test_ac07_seed_dry_run_warn" \
  _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md | head -20
# Expected: each test name appears ≥1 in §2.3 LOCKED-scope listing + §3.4c removals listing

# 2. Confirm the 7 functions EXIST in current source (pre-cleanup state)
grep -nE "^def test_ac04_1_eggplant_feld|^def test_mesclun_value_post_patch03|^def test_salad_mix_value_post_patch03|^def test_baby_kale_value_post_patch03|^def test_lebanese_cucumber_value_post_patch03|^def test_ac04_live_workbook_coverage|^def test_ac07_seed_dry_run_warn" \
  tests/crop_book/test_jmf_crop_map.py | head -10

# 3. Sanity: the 9 patch02/patch03 tests that SHOULD NOT be removed still exist
grep -cE "^def test_(parsnips|shallots|cherry_tomato|heirloom_tomato|chinese_cabbage|hot_pepper|beans_bush|snow_peas|basil)_value_post_patch0" \
  tests/crop_book/test_jmf_crop_map.py
# Expected: 9 (Parsnips + Shallots + Cherry + Heirloom + Chinese Cabbage + Hot Pepper + Beans Bush + Snow Peas + Basil)

# 4. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 5. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_R3_v1.0.0.md`

Commit: `gate(WP-B1-patch06/L-GATE_S R3): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

- PASS/PWF → team_110 dispatches Sonnet for incremental cleanup commit
- FAIL → R4

## 6. Authorization

ADR045 R2 #2 + team_00 sequencing directive "יש לתקן את הממצאים ולהמשיך לשלב הבא" (fix findings and proceed). Same pattern as patch03 R3+R4 amendments.

---

*L-GATE_S R3 mandate 2026-05-25 by team_110.*
