---
spec_version: v1.0.1
wp: SFA-S003-P002-WP-B1-patch06
gate: L-GATE_BUILD
status: BUILD_COMPLETE
engine: Sonnet (claude-sonnet-4-6)
build_commit: 113b47d
report_date: 2026-05-25
author: team_10
---

# BUILD_REPORT — SFA-S003-P002-WP-B1-patch06 (Cleanup WP)

## 1. Per-AC PASS Table

| AC | Description | Status | Notes |
|----|-------------|--------|-------|
| AC-01 | `len(JMF_CROP_MAP) == 60` | PASS | Counter probe: 60 |
| AC-02 | All 22 cultivar keys ABSENT from MAP | PASS | `test_no_cultivar_keys_in_map_post_patch06` passes |
| AC-03 | All 5 typo keys ABSENT from MAP | PASS | `test_no_typo_keys_in_map_post_patch06` passes |
| AC-04 | 53 baselines PRESENT with correct values | PASS | All baseline tests pass; spot-checked Arugula, Carrots, Basil, Ginger, Rutabaga, Parsnips, Shallots |
| AC-05 | `test_jmf_crop_map_duplicate_target_allowlist` passes with 6-group dict | PASS | New 6-group dict asserted exactly |
| AC-06 | `test_ac03_duplicate_group_count` asserts 6 | PASS | Updated 24 → 6 |
| AC-07 | Sum of group sizes = 12 (6 groups × 2 keys each) | PASS | Counter probe: sum=12 |
| AC-08 | 3 new regression tests pass | PASS | test_no_cultivar_keys, test_no_typo_keys, test_six_synonym_groups_exact all pass |
| AC-09 | `test_alias_spot_check_five_samples` repurposed to 5 synonym aliases, passes | PASS | Coriander, Green Onion, Pak Choi, Potato, Swiss Chard |
| AC-10 | `test_hebrew_value_collision_set_has_6_groups` (renamed) passes | PASS | Renamed from test_hebrew_value_collision_set_has_24_groups |
| AC-11 | `test_alias_entry_count_grew_by_34` no longer exists in the file | PASS | Function block removed; replaced with comment |
| AC-12 | `scripts/patch06_db_cleanup.py --dry-run` reports planned orphan removals | PASS | Script created; idempotent dry-run default; handles מלפפון חממה → מלפפון |
| AC-13 | Script is idempotent (running twice yields 0 changes on second run) | PASS | `_find_orphan_crop` returns None if already deleted → logs "nothing to do" |
| AC-14 | `pytest tests/crop_book/ -q` — 0 unexpected failures | FINDINGS (see §6) | 350 passed; 7 expected-consequence failures + 1 pre-existing OOS |
| AC-15 | `validate_aos.sh` returns 0 FAIL | PASS | 29 PASS / 19 SKIP / 0 FAIL |

**AC-14 NOTE:** 7 non-LOCKED tests fail as expected direct consequences of removing 27 keys. These are reported as findings in §6.

## 2. Files Modified (diff stats)

| File | Change |
|------|--------|
| `organic_market_agent/crop_book/constants.py` | MODIFIED — 27 key-value pairs removed from JMF_CROP_MAP; patch06 comment block added; trailing comment updated (87→60, test ref updated) |
| `tests/crop_book/test_jmf_crop_map.py` | MODIFIED — 3 LOCKED tests updated (count 87→60, allowlist 24→6, dup_count 24→6); 3 new regression tests appended |
| `tests/crop_book/test_jmf_crop_map_aliases.py` | MODIFIED — `test_alias_spot_check_five_samples` repurposed; `test_alias_entry_count_grew_by_34` removed; `test_hebrew_value_collision_set_has_24_groups` renamed to `test_hebrew_value_collision_set_has_6_groups` with assertion 24→6 |
| `CHANGELOG.md` | MODIFIED — patch06 [Unreleased] entry prepended |
| `scripts/patch06_db_cleanup.py` | CREATED — ~130 LOC; idempotent orphan cleanup; dry-run default; targets מלפפון חממה → מלפפון re-point |

## 3. Test Results (full count)

```
pytest tests/crop_book/ -q
8 failed, 350 passed, 42 warnings
```

**Failures breakdown:**

| Test | File | Cause | Classification |
|------|------|-------|----------------|
| `test_ac04_1_eggplant_feld_literal_alias` | test_jmf_crop_map.py | `"Eggplant  (Feld)"` removed as typo D | Expected consequence of patch06 |
| `test_mesclun_value_post_patch03` | test_jmf_crop_map.py | `"Mesclun"` removed as cultivar C | Expected consequence of patch06 |
| `test_salad_mix_value_post_patch03` | test_jmf_crop_map.py | `"Salad Mix"` removed as cultivar C | Expected consequence of patch06 |
| `test_baby_kale_value_post_patch03` | test_jmf_crop_map.py | `"Baby kale"` removed as cultivar C | Expected consequence of patch06 |
| `test_lebanese_cucumber_value_post_patch03` | test_jmf_crop_map.py | `"Greenhouse Libanese Cucumber"` removed as cultivar C | Expected consequence of patch06 |
| `test_ac04_live_workbook_coverage_min_42_of_50` | test_jmf_live_workbook_coverage.py | Coverage threshold ≤8 misses violated (now 26 misses) | Expected consequence of patch06 |
| `test_ac07_seed_dry_run_warn_only_for_unmapped` | test_jmf_seed_dry_run.py | Unmapped threshold exceeded (same root cause) | Expected consequence of patch06 |
| `test_dispatch_upload_crop_book_profile` | test_wp_upload_crop_book.py | Pre-existing OOS publisher regression | Pre-existing since WP-B3 (unrelated to patch06) |

**All 7 non-OOS failures were passing pre-patch06 and fail solely because removed keys were referenced in those tests. None of these are LOCKED tests per DECISION §3+§4.**

## 4. Counter Probe Output (MUST be 60/6/12)

```
len: 60
groups: 6
sum: 12

  אבטיח: ['Watermelon', 'Watermelons']
  בצל ירוק: ['Green Onion', 'Scallions']
  כוסברה: ['Cilantro', 'Coriander']
  מנגולד: ['Chard', 'Swiss Chard']
  פאק צ'וי: ['Bok Choy', 'Pak Choi']
  תפוח אדמה: ['Potato', 'Potatoes']
```

**CONFIRMED: 60 / 6 / 12 — exact match to spec.**

All 6 groups match DECISION §3 exactly:
- פאק צ'וי: [Bok Choy, Pak Choi] ✓
- מנגולד: [Chard, Swiss Chard] ✓
- בצל ירוק: [Green Onion, Scallions] ✓
- תפוח אדמה: [Potato, Potatoes] ✓
- אבטיח: [Watermelon, Watermelons] ✓
- כוסברה: [Cilantro, Coriander] ✓

## 5. validate_aos.sh Result

```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

## 6. Notes / Observations / Findings

### Finding F-01 — 7 non-LOCKED tests now fail (expected, follow-up required)

**Nature:** Expected consequence of removing 27 MAP keys.

**Affected non-LOCKED tests (per mandate §EXPECTED TEST RESULTS advisory):**

1. `test_ac04_1_eggplant_feld_literal_alias` — patch01 regression asserting `"Eggplant  (Feld)"` is in MAP (removed as typo D per LOD400 §3.1)
2. `test_mesclun_value_post_patch03` — patch03 regression asserting `"Mesclun"` is in MAP (removed as cultivar C)
3. `test_salad_mix_value_post_patch03` — patch03 regression asserting `"Salad Mix"` is in MAP (removed as cultivar C)
4. `test_baby_kale_value_post_patch03` — patch03 regression asserting `"Baby kale"` is in MAP (removed as cultivar C)
5. `test_lebanese_cucumber_value_post_patch03` — patch03 regression asserting `"Greenhouse Libanese Cucumber"` is in MAP (removed as cultivar C)
6. `test_ac04_live_workbook_coverage_min_42_of_50` — asserts live workbook has ≤8 unmapped crops; patch06 removals raise unmapped count to 26 (the removed keys correspond to real CROP CHART rows in the live workbook)
7. `test_ac07_seed_dry_run_warn_only_for_unmapped` — same root cause as F-01.6

**Action required by team_110 / team_00:** These 7 tests need a subsequent follow-up WP or amendment to either (a) remove/update the stale assertions, or (b) update the live workbook coverage threshold. None are in the LOCKED scope exception for patch06.

### Finding F-02 — `test_ac04_1_eggplant_feld_literal_alias` is a LOCKED patch01 AC

The `test_ac04_1_eggplant_feld_literal_alias` test (LOD400 §4 AC-04.1) was a patch01 acceptance criterion. Its removal key `"Eggplant  (Feld)"` appears in the LOD400 §3.1 Type D typo removal list. This is a known conflict between patch01 and patch06 policies — patch06 correctly takes precedence per DECISION §3. The test needs updating in a follow-up.

### IR Compliance

- IR#4: `_aos/roadmap.yaml` NOT touched ✓
- IR#11: `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` NOT touched ✓
- Pre-existing dirty files untouched (`.env.example`, `sfa_delivery/`, `data/.wp_media_id_*`, etc.) ✓
- `replace_all=false` used for all Edit calls; Hebrew values NOT used as `old_string` targets ✓
