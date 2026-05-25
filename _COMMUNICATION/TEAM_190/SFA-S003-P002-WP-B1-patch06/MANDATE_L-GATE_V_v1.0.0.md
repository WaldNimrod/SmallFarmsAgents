---
id: MANDATE_SFA-S003-P002-WP-B1-patch06_L-GATE_V_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B1-patch06
status: ACTIVE
verdict: PENDING
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent — 2 commits: 113b47d initial + 8920269 incremental cleanup)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190 — three distinct engines"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
spec_version: v1.0.3
build_commit_initial: 113b47d
build_commit_incremental: 8920269
build_reports: [BUILD_REPORT_v1.0.0.md (initial + STOP semantics), BUILD_REPORT_v1.0.1.md (incremental cleanup, team_110-authored stub post-Sonnet-socket-termination)]
prior_gate_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_R4_v1.0.0.md
prior_gate_result: PASS_WITH_FINDINGS (L-GATE_S R4, advisory addressed inline)
---

# L-GATE_V Mandate — patch06

## 1. Scope

Validate the executed build of patch06 (cleanup WP) against LOD400 v1.0.3.

**Two build commits** form the patch06 build:
- **`113b47d`** — initial build per v1.0.1: removed 27 keys from JMF_CROP_MAP, updated 5 LOCKED tests + removed 1, added 3 new, added cleanup script. Counter probe 60/6/12 ✓. 15/15 ACs PASS. **But 7 non-LOCKED tests failed** (consequence of cleanup).
- **`8920269`** — incremental cleanup per v1.0.3 (post-R3+R4 amendment): deleted the 7 superseded test functions across 3 files (one file deleted entirely after becoming empty). Final state: 350 pass + 1 pre-existing OOS publisher.

Combined, the patch06 build satisfies all 15 ACs cleanly.

## 2. Pre-flight
Confirm GPT-5.5. Both build commits Sonnet co-authored. Validator distinct.

## 3. Validation Criteria (16 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-V1 | **IR#1 three-engine** | Both Sonnet commits co-authored Sonnet; verdict GPT-5.5; orchestration team_110. Three distinct. |
| VC-V2 | **AC-01..AC-04 MAP shape** | `len(JMF_CROP_MAP) == 60`; 22 cultivar keys ABSENT; 5 typo keys ABSENT; 53 baselines PRESENT with correct values per DECISION §1 Cat A |
| VC-V3 | **AC-05..AC-07 duplicate-target allowlist** | `test_jmf_crop_map_duplicate_target_allowlist` passes with 6-group dict (§3.3 byte-exact); `test_ac03_duplicate_group_count` asserts 6; sum of group sizes = 12 |
| VC-V4 | **AC-08..AC-11 tests** | 3 new regression tests present (`test_no_cultivar_keys_in_map_post_patch06`, `test_no_typo_keys_in_map_post_patch06`, `test_six_synonym_groups_exact`); `test_alias_spot_check_five_samples` repurposed (5 synonym aliases per §3.6); `test_hebrew_value_collision_set_has_6_groups` renamed + asserts 6; `test_alias_entry_count_grew_by_34` ABSENT |
| VC-V5 | **AC-12..AC-13 cleanup script** | `scripts/patch06_db_cleanup.py` exists with --dry-run default + idempotent semantics |
| VC-V6 | **AC-14..AC-15 hygiene** | `pytest tests/crop_book/ -q` → **350 passed + 1 pre-existing publisher OOS** (`test_dispatch_upload_crop_book_profile` — do NOT flag); `validate_aos.sh` → 29/19/0 FAIL |
| VC-V7 | **7 superseded tests absent (across 3-4 files)** | `grep -E "^def test_ac04_1_eggplant_feld\|^def test_mesclun_value_post_patch03\|^def test_salad_mix_value_post_patch03\|^def test_baby_kale_value_post_patch03\|^def test_lebanese_cucumber_value_post_patch03\|^def test_ac04_live_workbook_coverage\|^def test_ac07_seed_dry_run_warn"` against `tests/crop_book/*.py` → **0 matches** |
| VC-V8 | **`test_jmf_live_workbook_coverage.py` deleted** | File no longer exists (per LOD400 §3.4c file-emptiness rule; was the only-test in that file) |
| VC-V9 | **`test_jmf_seed_dry_run.py` preserved** | File still exists (other tests remain after function removal) |
| VC-V10 | **9 KEEP-tests preserved** | `grep -cE "^def test_(parsnips\|shallots\|cherry_tomato\|heirloom_tomato\|chinese_cabbage\|hot_pepper\|beans_bush\|snow_peas\|basil)_value_post_patch0" tests/crop_book/test_jmf_crop_map.py` → **9** |
| VC-V11 | **Implicit patch03 §1.3 revert** | `"מלפפון חממה"` no longer appears as a VALUE in `JMF_CROP_MAP` (the `Greenhouse Libanese Cucumber` key was removed in `113b47d`) |
| VC-V12 | **IR#4 builder discipline** | Neither `113b47d` nor `8920269` touch `_aos/roadmap.yaml`. |
| VC-V13 | **Cumulative diff scope** | `git diff <patch04-lock>..HEAD` shows ONLY: `constants.py`, `test_jmf_crop_map.py`, `test_jmf_crop_map_aliases.py`, `test_jmf_live_workbook_coverage.py` (deleted), `test_jmf_seed_dry_run.py`, `CHANGELOG.md`, `scripts/patch06_db_cleanup.py`, plus team_110-authored governance artifacts (spec/mandate/verdict/report — `_aos/work_packages/`, `_COMMUNICATION/`). No other LOCKED files. |
| VC-V14 | **BUILD_REPORT integrity** | Both BUILD_REPORTs present (v1.0.0 + v1.0.1). v1.0.1 is team_110-authored stub post-Sonnet-socket-termination — explicitly noted in frontmatter; all probes re-verified independently. |
| VC-V15 | **Patch04 non-regression** | Migration 047 still applies; `crop_knowledge_notes` schema still has junction relationship; Ginger still in MAP; patch04's 13 integration tests still pass |
| VC-V16 | **Synonym group integrity** | The 6 remaining duplicate-target groups are EXACTLY: `{פאק צ'וי: [Bok Choy, Pak Choi], מנגולד: [Chard, Swiss Chard], בצל ירוק: [Green Onion, Scallions], תפוח אדמה: [Potato, Potatoes], אבטיח: [Watermelon, Watermelons], כוסברה: [Cilantro, Coriander]}` |

## 4. Commands

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. Engine + commit attestation
git show --stat 113b47d 8920269 | head -40
git log -1 --format='%an %ae %s' 113b47d
git log -1 --format='%an %ae %s' 8920269

# 2. MAP shape
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
from collections import Counter
print(f'len: {len(JMF_CROP_MAP)}')
c = Counter(JMF_CROP_MAP.values())
groups = {v: sorted(k for k,mv in JMF_CROP_MAP.items() if mv==v) for v,n in c.items() if n>1}
print(f'groups: {len(groups)}')
print(f'sum: {sum(n for n in c.values() if n>1)}')
for v,ks in sorted(groups.items()): print(f'  {v}: {ks}')
"
# Expected: len 60 / groups 6 / sum 12 + the 6 specific synonym pairs

# 3. 7 superseded absent
grep -E "^def test_ac04_1_eggplant_feld|^def test_mesclun_value_post_patch03|^def test_salad_mix_value_post_patch03|^def test_baby_kale_value_post_patch03|^def test_lebanese_cucumber_value_post_patch03|^def test_ac04_live_workbook_coverage|^def test_ac07_seed_dry_run_warn" \
  tests/crop_book/*.py
# Expected: 0 matches

# 4. test_jmf_live_workbook_coverage.py deleted; test_jmf_seed_dry_run.py preserved
ls tests/crop_book/test_jmf_live_workbook_coverage.py 2>&1
ls tests/crop_book/test_jmf_seed_dry_run.py 2>&1

# 5. 9 KEEP-tests
grep -cE "^def test_(parsnips|shallots|cherry_tomato|heirloom_tomato|chinese_cabbage|hot_pepper|beans_bush|snow_peas|basil)_value_post_patch0" \
  tests/crop_book/test_jmf_crop_map.py
# Expected: 9

# 6. pytest + validate_aos
python3 -m pytest tests/crop_book/ -q
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 7. IR#4 check on both commits
git show --name-only 113b47d 8920269 | grep "_aos/roadmap.yaml" && echo "VIOLATION" || echo "IR#4 CLEAN (both commits)"

# 8. Migration 047 still operational (patch04 non-regression)
alembic current   # Should be 047
```

## 5. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LGATEV-VERDICT_v1.0.0.md`

Frontmatter MUST include both `build_commit_initial: 113b47d` + `build_commit_incremental: 8920269`, `spec_version: v1.0.3`, `criteria_total: 16`.

Commit: `gate(WP-B1-patch06/L-GATE_V): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF (0 blockers) → team_110 closes patch06 (Phase 7+8) → **EXECUTION_MANDATE SFA-S003-P002-WP-B NATURALLY ENDS** (7 of 7 → 8 of 8 WPs LOD500_LOCKED).
FAIL → R2.

## 6. Authorization

ADR045 R2 #2 + team_00 directive 2026-05-25 "יש לתקן את הממצאים ולהמשיך לשלב הבא".

---

*L-GATE_V mandate 2026-05-25 by team_110.*
