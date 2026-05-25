---
id: SFA-S003-P002-WP-B1-patch06-LOD400
wp: SFA-S003-P002-WP-B1-patch06 — JMF_CROP_MAP cleanup
gate: L-GATE_S
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-25
version: v1.0.3
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD200_spec.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md
parent_wp_patch04_lock_commit: "TBD (patch04 must lock first)"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator) ≠ team_10 Sonnet (builder) ≠ team_190 GPT-5.5 (validator) — three distinct engines"
---

# LOD400 — patch06 Cleanup

## 1. Goal

Apply the "baselines-only" policy: remove 27 entries from `JMF_CROP_MAP` (22 cultivars + 5 typos). Update LOCKED tests accordingly. Add cleanup script for any orphan `crops` rows.

**Pre-state (post-patch04):** 87 entries, 24 duplicate-target groups.
**Post-state:** **60 entries, 6 duplicate-target groups** (all pure synonyms).

## 2. Architecture

### 2.1 Files MODIFIED (6 — extended in v1.0.3 R4)
```
organic_market_agent/crop_book/constants.py        ← remove 27 lines from JMF_CROP_MAP literal
tests/crop_book/test_jmf_crop_map.py               ← UPDATE 3 LOCKED tests + APPEND 3 new + REMOVE 5 superseded patch01/patch03 tests (v1.0.2 R3 + v1.0.3 R4)
tests/crop_book/test_jmf_crop_map_aliases.py       ← UPDATE 2 LOCKED tests + REMOVE 1 LOCKED test (test_alias_entry_count_grew_by_34)
tests/crop_book/test_jmf_live_workbook_coverage.py ← REMOVE test_ac04_live_workbook_coverage_min_42_of_50 (v1.0.3 R4)
tests/crop_book/test_jmf_seed_dry_run.py           ← REMOVE test_ac07_seed_dry_run_warn_only_for_unmapped (v1.0.3 R4)
CHANGELOG.md                                        ← [Unreleased] entry
```

### 2.2 Files CREATED (1)
```
scripts/patch06_db_cleanup.py    ← idempotent orphan-crops cleanup (~80 LOC)
```

### 2.3 LOCKED scope exception (per DECISION §3 + extends patch03 R3+R4 pattern; v1.0.2 R3 expansion)
**In `test_jmf_crop_map.py`:**
- `test_jmf_crop_map_count` (asserts size)
- `test_jmf_crop_map_duplicate_target_allowlist` (24-group dict)
- `test_ac03_duplicate_group_count` (assert 24)
- **v1.0.2 R3 additions** — superseded regression tests for keys removed by patch06:
  - `test_ac04_1_eggplant_feld_literal_alias` — REMOVE (asserts `Eggplant  (Feld)` is in MAP — key removed; coverage subsumed by `test_no_typo_keys_in_map_post_patch06`)
  - `test_mesclun_value_post_patch03` — REMOVE (asserts `Mesclun → עלי בייבי` — key removed; coverage subsumed by `test_no_cultivar_keys_in_map_post_patch06`)
  - `test_salad_mix_value_post_patch03` — REMOVE (same)
  - `test_baby_kale_value_post_patch03` — REMOVE (same)
  - `test_lebanese_cucumber_value_post_patch03` — REMOVE (same)
  - (v1.0.3 R4 — moved to separate file; see below)
  - (v1.0.3 R4 — moved to separate file; see below)

**In `tests/crop_book/test_jmf_live_workbook_coverage.py` (v1.0.3 R4 addition):**
- `test_ac04_live_workbook_coverage_min_42_of_50` — REMOVE (patch01-era coverage achievement no longer holds under baselines-only policy; semantically obsolete)

**In `tests/crop_book/test_jmf_seed_dry_run.py` (v1.0.3 R4 addition):**
- `test_ac07_seed_dry_run_warn_only_for_unmapped` — REMOVE (asserts seed.py warns on unmapped — patch06's removed keys now LEGITIMATELY produce warnings; the test's pre-patch06 premise no longer holds)

**In `test_jmf_crop_map_aliases.py`:**
- `test_alias_spot_check_five_samples` (5 hardcoded keys, 4 of which are removed)
- `test_alias_entry_count_grew_by_34` (the "34 aliases" assertion no longer holds; REMOVE)
- `test_hebrew_value_collision_set_has_24_groups` (rename + value)

## 3. Implementation — exact code paths

### 3.1 `constants.py` — remove 27 lines

In `JMF_CROP_MAP`, locate and DELETE the following key-value pairs (preserving the surrounding `# ── Group ──` comments):

**Type D — typos (5):**
```python
"Brussel Sprouts":              "כרוב ניצנים",
"Raddish":                      "צנונית",
"Spinach TR":                   "תרד",
"Spinarch SD":                  "תרד",
"Eggplant  (Feld)":             "חציל",
```

**Type C — cultivars (22):**
```python
"Baby kale":                    "עלי בייבי",
"Bell Pepper":                  "פלפל",
"Cauliflower / Romanesco":      "כרובית",
"Fall Cabbage":                 "כרוב",
"Fresh Carrots":                "גזר",
"Greenhouse English Cucumber":  "מלפפון",
"Greenhouse Libanese Cucumber": "מלפפון חממה",   # NOTE: also reverts patch03 §1.3 implicitly (entry removed)
"Hakurei Turnip":               "לפת",
"Leek Storage":                 "כרישה",
"Leek Summer":                  "כרישה",
"Mesclun":                      "עלי בייבי",
"Mini Celery Root":             "סלרי שורש",
"Mini Fennel":                  "שומר",
"Roma Tomato":                  "עגבנייה",
"Salad Mix":                    "עלי בייבי",
"Salanova Lettuce":             "חסה",
"Savoy Cabbage":                "כרוב",
"Storage Onion":                "בצל",
"Sucrine":                      "חסה",
"Summer Cabbage":               "כרוב",
"Winter Radish":                "צנונית",
"Zucchini":                     "קישוא",
```

Add a comment block at the patch01-alias section boundary:
```python
# ─── patch06 (2026-05-25): 22 cultivars + 5 typos removed per DECISION §3.
# Variants now live in crop_varieties (populated by patch04). The MAP is
# now baselines-only (53 baselines + 6 synonyms + 1 Ginger = 60 entries).
```

**Builder safety:** use `Edit replace_all=false` with the full line as `old_string` for each removal. DO NOT batch-delete by value (values like "כרוב" appear in multiple lines).

### 3.2 `test_jmf_crop_map.py::test_jmf_crop_map_count` — update size

```python
def test_jmf_crop_map_count(jmf_crop_map):
    """patch06: 60 entries (53 baselines + 6 synonyms + 1 Ginger from patch04)."""
    assert len(jmf_crop_map) == 60, f"Expected 60, got {len(jmf_crop_map)}"
```

### 3.3 `test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist` — 6-group dict

```python
def test_jmf_crop_map_duplicate_target_allowlist(jmf_crop_map):
    """patch06: exactly 6 synonym-pair duplicate-target groups."""
    counts = Counter(jmf_crop_map.values())
    duplicates = {
        v: sorted([k for k, mv in jmf_crop_map.items() if mv == v])
        for v, c in counts.items() if c > 1
    }
    assert duplicates == {
        "פאק צ'וי":    ["Bok Choy", "Pak Choi"],
        "מנגולד":      ["Chard", "Swiss Chard"],
        "בצל ירוק":    ["Green Onion", "Scallions"],
        "תפוח אדמה":   ["Potato", "Potatoes"],
        "אבטיח":       ["Watermelon", "Watermelons"],
        "כוסברה":      ["Cilantro", "Coriander"],
    }, f"unexpected Hebrew-value duplicates: {duplicates}"
```

### 3.4 `test_jmf_crop_map.py::test_ac03_duplicate_group_count` — count 24 → 6

```python
def test_ac03_duplicate_group_count(jmf_crop_map):
    """patch06: exactly 6 Hebrew values appear more than once (all synonyms)."""
    counts = Counter(jmf_crop_map.values())
    dup_count = sum(1 for c in counts.values() if c > 1)
    assert dup_count == 6, f"Expected 6 duplicate-target groups, got {dup_count}"
```

### 3.4c REMOVE 7 superseded tests (v1.0.2 R3 + v1.0.3 R4 amendments) — across 3 files

**`tests/crop_book/test_jmf_crop_map.py` — delete 5 function blocks:**

```python
# DELETE (full def + body):
def test_ac04_1_eggplant_feld_literal_alias(...): ...
def test_mesclun_value_post_patch03(...): ...
def test_salad_mix_value_post_patch03(...): ...
def test_baby_kale_value_post_patch03(...): ...
def test_lebanese_cucumber_value_post_patch03(...): ...
```

**`tests/crop_book/test_jmf_live_workbook_coverage.py` — delete 1 function block (v1.0.3 R4):**

```python
# DELETE (full def + body):
def test_ac04_live_workbook_coverage_min_42_of_50(...): ...
```

If this is the ONLY test in the file, also delete the file entirely (clean up the empty test module). If other tests remain in the file, leave it.

**`tests/crop_book/test_jmf_seed_dry_run.py` — delete 1 function block (v1.0.3 R4):**

```python
# DELETE (full def + body):
def test_ac07_seed_dry_run_warn_only_for_unmapped(...): ...
```

Same file-emptiness rule as above.

**Do NOT delete** the other patch02/patch03 regression tests in `test_jmf_crop_map.py` (Parsnips, Shallots, Cherry Tomato, Heirloom Tomato, Chinese Cabbage, Hot Pepper, Beans Bush, Snow Peas, Basil — keys remain baselines).

### 3.5 `test_jmf_crop_map.py` — APPEND 3 new regression tests

```python
# ─── patch06 regression tests (DECISION 2026-05-25 §3) ───

def test_no_cultivar_keys_in_map_post_patch06():
    """patch06: 22 cultivar keys removed from JMF_CROP_MAP (now in crop_varieties)."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    removed_cultivars = {
        "Baby kale", "Bell Pepper", "Cauliflower / Romanesco", "Fall Cabbage",
        "Fresh Carrots", "Greenhouse English Cucumber", "Greenhouse Libanese Cucumber",
        "Hakurei Turnip", "Leek Storage", "Leek Summer", "Mesclun",
        "Mini Celery Root", "Mini Fennel", "Roma Tomato", "Salad Mix",
        "Salanova Lettuce", "Savoy Cabbage", "Storage Onion", "Sucrine",
        "Summer Cabbage", "Winter Radish", "Zucchini",
    }
    for k in removed_cultivars:
        assert k not in JMF_CROP_MAP, f"Cultivar key {k!r} still in MAP — patch06 incomplete"


def test_no_typo_keys_in_map_post_patch06():
    """patch06: 5 workbook typo keys removed from JMF_CROP_MAP."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    removed_typos = {"Brussel Sprouts", "Eggplant  (Feld)", "Raddish", "Spinach TR", "Spinarch SD"}
    for k in removed_typos:
        assert k not in JMF_CROP_MAP, f"Typo key {k!r} still in MAP — patch06 incomplete"


def test_six_synonym_groups_exact():
    """patch06: the 6 remaining duplicate-target groups are all pure synonym pairs."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    from collections import Counter
    counts = Counter(JMF_CROP_MAP.values())
    duplicates = {v for v, c in counts.items() if c > 1}
    assert duplicates == {"פאק צ'וי", "מנגולד", "בצל ירוק", "תפוח אדמה", "אבטיח", "כוסברה"}
```

### 3.6 `test_jmf_crop_map_aliases.py` — full restructure of LOCKED tests

```python
# REPURPOSE test_alias_spot_check_five_samples — was 5 hardcoded; now 5 synonym aliases
def test_alias_spot_check_five_samples(jmf_crop_map):
    """patch06: 5 sample synonym aliases resolve to the correct baseline Hebrew."""
    expected = {
        "Coriander":   "כוסברה",
        "Green Onion": "בצל ירוק",
        "Pak Choi":    "פאק צ'וי",
        "Potato":      "תפוח אדמה",
        "Swiss Chard": "מנגולד",
    }
    for key, expected_value in expected.items():
        assert key in jmf_crop_map
        assert jmf_crop_map[key] == expected_value

# REMOVE test_alias_entry_count_grew_by_34 entirely (no longer holds — 34 aliases removed/refactored)

# RENAME + UPDATE test_hebrew_value_collision_set_has_24_groups → test_hebrew_value_collision_set_has_6_groups
def test_hebrew_value_collision_set_has_6_groups(jmf_crop_map):
    """patch06: Hebrew-value collision set = 6 synonym groups."""
    counts = Counter(jmf_crop_map.values())
    duplicate_targets = {v for v, c in counts.items() if c > 1}
    assert len(duplicate_targets) == 6, (
        f"Expected 6 synonym groups, found {len(duplicate_targets)}: {sorted(duplicate_targets)}"
    )
```

### 3.7 `scripts/patch06_db_cleanup.py` — orphan cleanup

```python
"""Idempotent cleanup of crops rows whose name_he is no longer reachable from
the cleaned JMF_CROP_MAP. Specifically targets the patch03 §1.3 anomaly row
(name_he = 'מלפפון חממה').

Usage:
  python scripts/patch06_db_cleanup.py --dry-run
  python scripts/patch06_db_cleanup.py --apply

Per DECISION_WP-B1-patch04-patch06 §3.5.
"""
ORPHAN_NAME_HE = {'מלפפון חממה'}  # patch03 anomaly being collapsed back to מלפפון

def main(dry_run: bool):
    """For each orphan name_he:
       1. Find the canonical baseline crop (e.g., מלפפון חממה → מלפפון)
       2. Re-point all FK references (crop_varieties.crop_id, crop_knowledge_notes.crop_id)
       3. Delete the orphan crops row
       Logs every row touched.
    """
```

### 3.8 CHANGELOG.md

```markdown
### SFA-S003-P002-WP-B1-patch06 — JMF_CROP_MAP cleanup (2026-05-25)
- **REMOVED 27 entries** from JMF_CROP_MAP per DECISION §3:
  - 22 cultivars moved to crop_varieties (populated by patch04)
  - 5 workbook typos / edition suffixes deleted as artifact noise
- **Net:** 87 → 60 entries; duplicate-target groups 24 → 6 (all pure synonyms)
- Implicitly reverts patch03 §1.3 (Greenhouse Libanese Cucumber removed from MAP — variety now in crop_varieties with "Greenhouse" + "Libanese" attributes)
- LOD500_LOCKED scope exception: 13 LOCKED test touches across 4 test files (per DECISION §3 + v1.0.2 R3 + v1.0.3 R4 amendments) — 5 updates + 8 removals
- `scripts/patch06_db_cleanup.py` automates orphan crops row cleanup
```

## 4. Acceptance Criteria (15 ACs)

### 4.1 MAP shape (AC-01..AC-04)
- **AC-01** `len(JMF_CROP_MAP) == 60`
- **AC-02** All 22 cultivar keys (§2.1 type C) ABSENT from MAP
- **AC-03** All 5 typo keys (§2.1 type D) ABSENT from MAP
- **AC-04** The 53 baselines (per DECISION §1.3 Cat A) PRESENT with correct values

### 4.2 Duplicate-target allowlist (AC-05..AC-07)
- **AC-05** `test_jmf_crop_map_duplicate_target_allowlist` passes with new 6-group dict (per §3.3)
- **AC-06** `test_ac03_duplicate_group_count` asserts 6
- **AC-07** Sum of group sizes = 12 (6 groups × 2 keys each)

### 4.3 Tests (AC-08..AC-11)
- **AC-08** The 3 new regression tests (`test_no_cultivar_keys_in_map_post_patch06`, etc.) pass
- **AC-09** `test_alias_spot_check_five_samples` repurposed to 5 synonym aliases, passes
- **AC-10** `test_hebrew_value_collision_set_has_6_groups` (renamed) passes
- **AC-11** `test_alias_entry_count_grew_by_34` no longer exists in the file

### 4.4 Cleanup script (AC-12..AC-13)
- **AC-12** `python scripts/patch06_db_cleanup.py --dry-run` reports planned orphan removals
- **AC-13** Script is idempotent (running twice yields 0 changes on second run)

### 4.5 Hygiene (AC-14..AC-15)
- **AC-14** `pytest tests/crop_book/ -q` returns N passing (count to be computed at build time based on patch04's actual count); 0 unexpected failures
- **AC-15** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL

## 5. Test requirements

**LOCKED updates (5 functions):**
- 3 in `test_jmf_crop_map.py` (count + allowlist + ac03_count)
- 2 in `test_jmf_crop_map_aliases.py` (spot_check + collision rename)

**LOCKED removals (8 functions across 4 files; v1.0.2 R3 + v1.0.3 R4):**
- 5 in `test_jmf_crop_map.py` (test_ac04_1_eggplant_feld_literal_alias + 4 patch03 cultivar-value tests)
- 1 in `test_jmf_crop_map_aliases.py` (test_alias_entry_count_grew_by_34)
- 1 in `test_jmf_live_workbook_coverage.py` (test_ac04_live_workbook_coverage_min_42_of_50; delete file if empty)
- 1 in `test_jmf_seed_dry_run.py` (test_ac07_seed_dry_run_warn_only_for_unmapped; delete file if empty)

**New regression tests (3 appended to `test_jmf_crop_map.py`):**
- test_no_cultivar_keys_in_map_post_patch06
- test_no_typo_keys_in_map_post_patch06
- test_six_synonym_groups_exact

**Total:** 5 LOCKED updates + 8 LOCKED removals + 3 new = **16 test functions touched** across 4 files.

## 6. Build sequence

1. **Pre-flight:** verify patch04 LOD500_LOCKED + `crop_varieties` table populated by patch04 (sample queries: at least 100 variety rows linked to baseline crops covering all 22 removed cultivar concepts).
2. Apply 27 removals in `constants.py` (§3.1)
3. Update 3 LOCKED tests in `test_jmf_crop_map.py` (§3.2-3.4)
4. Append 3 new regression tests (§3.5)
5. Update 2 + remove 1 LOCKED tests in `test_jmf_crop_map_aliases.py` (§3.6)
6. Author `scripts/patch06_db_cleanup.py` (§3.7)
7. Append CHANGELOG (§3.8)
8. Run focused tests: `pytest tests/crop_book/test_jmf_crop_map.py tests/crop_book/test_jmf_crop_map_aliases.py -v` — all PASS
9. Run full suite — confirm count matches AC-14
10. Run `validate_aos.sh` — 0 FAIL
11. Single atomic commit:
```
build(WP-B1-patch06): JMF_CROP_MAP cleanup — 22 cultivars + 5 typos removed

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>
```

**Builder safety:** before commit, run the Counter probe — must show exactly 6 groups / 12 keys-with-duplicates / 60 total.

## 7. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | Removing keys breaks downstream lookup (importer hits removed key in workbook) | patch04 populated `crop_varieties` first; importer can fall back to variety lookup. AC-09 + AC-14 catch. |
| R-02 | Builder uses `replace_all` on a value string (e.g., "כרוב" appears in multiple removed lines) | §3.1 explicitly warns; use full-line matching with key prefix. |
| R-03 | `test_alias_entry_count_grew_by_34` removal pattern not understood by Sonnet | §3.6 shows exact "REMOVE this test" instruction. Builder should DELETE the function block entirely, not modify. |
| R-04 | Orphan cleanup script touches wrong rows | dry-run mode default; --apply required; logs every row. |

## 8. LOD500_LOCKED file inventory (extended in v1.0.3 R4)
Same as patch04 + cumulative. Permitted modifications:
- `constants.py` — 27-line removal block in JMF_CROP_MAP literal
- `test_jmf_crop_map.py` — 3 LOCKED tests updated + 3 new appended + 5 superseded tests REMOVED (per DECISION §3 + v1.0.2 R3 + v1.0.3 R4 scope exceptions)
- `test_jmf_crop_map_aliases.py` — 2 LOCKED tests updated + 1 removed
- `test_jmf_live_workbook_coverage.py` — 1 superseded test REMOVED (v1.0.3 R4; if file becomes empty, delete file)
- `test_jmf_seed_dry_run.py` — 1 superseded test REMOVED (v1.0.3 R4; if file becomes empty, delete file)
- `CHANGELOG.md` — entry

All other LOCKED files untouched.

## 9. Out-of-scope
- New entries to JMF_CROP_MAP (none — Ginger is patch04's job)
- Schema changes (Migration 047 is patch04)
- `crop_varieties` / `crops` / `crop_knowledge_notes` row mutations beyond §3.7's automated orphan cleanup

## 10. Builder
team_10 (Sonnet sub-agent). MEDIUM scope, high LOCKED-touch surface.

---

*LOD400 v1.0.0 — 2026-05-25.*
*v1.0.1 (2026-05-25) — R2 correction per team_190 L-GATE_S R1 VC-1 BLOCKER: frontmatter now explicitly records the full three-engine chain (orchestrator + builder + validator + engine_chain summary). No other change.*
*v1.0.2 (2026-05-25) — R3 amendment after Sonnet builder reported 7 non-LOCKED test failures as expected-consequence of the cleanup (BUILD_REPORT v1.0.0 at commit 6801e64; build commit 113b47d). 7 superseded tests added to LOCKED scope exception with REMOVE directive.*
*v1.0.3 (2026-05-25) — R4 correction per team_190 L-GATE_S R3 BLOCKER: 2 of the 7 superseded tests actually live in separate files (`test_jmf_live_workbook_coverage.py` and `test_jmf_seed_dry_run.py`), not in `test_jmf_crop_map.py`. §2.1 file list extended (4→6 files); §2.3 LOCKED-scope listing updated to enumerate the correct file for each test; §3.4c REMOVE block split per-file; §8 LOD500_LOCKED inventory extended; if either of the two new files becomes empty after the single-function removal, builder deletes the file.*
*Pending: team_190 L-GATE_S R4.*
