---
id: SFA-S003-P002-WP-B1-patch02-LOD400
wp: SFA-S003-P002-WP-B1-patch02 — JMF_CROP_MAP Hebrew terminology corrections (Q4)
gate: L-GATE_S (LOD400 — implementation spec)
status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S verdict
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch02/LOD200_spec.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
parent_wp_b1_patch01_lock_commit: "3e1f946"
builder: team_110 (Opus 4.7 — single-engine builder per §11 rationale)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B1-patch02: Hebrew Terminology Corrections (Q4)

**Read before writing a single line of code:**

1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch02/LOD200_spec.md`
2. team_00 DECISION §Q4: `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md`
3. Current `JMF_CROP_MAP` literal (post-patch01) in `organic_market_agent/crop_book/constants.py` — the 86-entry dict
4. Current `test_jmf_crop_map.py` AC-03 Counter assertion (will remain unchanged — see §6)

---

## 1. Goal

Apply exactly 2 Hebrew-value corrections to the `JMF_CROP_MAP` literal in `constants.py`, per team_00 DECISION §Q4:

| Key | Before | After |
|-----|--------|-------|
| `Parsnips` | `"גזר לבן"` | **`"שורש פטרוזילה"`** |
| `Shallots` | `"שאלוט"` | **`"בצלצלי שאלוט"`** |

Plus:
- Add 2 regression test assertions for the new values
- Append `[Unreleased]` `CHANGELOG.md` entry

Total work: ~6 lines of code touched across 3 files.

---

## 2. Architecture

### 2.1 Files modified (3 — all permitted-additive scope)

```
organic_market_agent/crop_book/constants.py    ← Two value edits in JMF_CROP_MAP
                                                 (Parsnips + Shallots). Comment
                                                 block added inline citing
                                                 DECISION file.
tests/crop_book/test_jmf_crop_map.py            ← Two new test functions
                                                 (test_parsnips_value_post_patch02,
                                                  test_shallots_value_post_patch02)
                                                 AC-03 Counter assertion UNCHANGED.
CHANGELOG.md                                     ← [Unreleased] entry
```

### 2.2 No changes to these (LOD500_LOCKED)

All WP-A + WP-B1 + patch01 + B2 + B3 deliverables remain LOD500_LOCKED. Headline files unchanged:
- `models.py`, `source_registry.py`, `field_policy.py`, `reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`
- `crop_task_templates.py`, `crop_knowledge_notes.py`, `crop_harvest_stats.py`
- `jmf_masterclass.py`, `tend_overlay.py`, all `ni/` subclasses
- `tend.py`, `jmf.py`
- `views.py`, `publisher/`, `mu-plugin/`
- All migrations 001-046
- `seed.py`

The ONLY permitted change is the 2-value edit in `constants.py::JMF_CROP_MAP` + the 2 test assertions + CHANGELOG.

---

## 3. Implementation — exact code changes

### 3.1 `constants.py` — Parsnips value change

Locate the existing line (around line 221 post-patch01):

```python
    "Parsnips":           "גזר לבן",
```

Replace with:

```python
    "Parsnips":           "שורש פטרוזילה",   # team_00 DECISION 2026-05-25 §Q4: "גזר לבן" was colloquial; replaced with botanically accurate "parsley root"
```

### 3.2 `constants.py` — Shallots value change

Locate the existing line (around line 215 post-patch01):

```python
    "Shallots":           "שאלוט",
```

Replace with:

```python
    "Shallots":           "בצלצלי שאלוט",   # team_00 DECISION 2026-05-25 §Q4: pure transliteration "שאלוט" replaced with "shallot small-onions" hybrid
```

### 3.3 `test_jmf_crop_map.py` — 2 regression tests appended

Append after existing tests (do NOT modify any existing test, especially AC-03 Counter assertion):

```python
def test_parsnips_value_post_patch02():
    """patch02 (DECISION 2026-05-25 §Q4): Parsnips Hebrew is 'שורש פטרוזילה'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Parsnips"] == "שורש פטרוזילה", (
        f"Parsnips Hebrew value drifted from DECISION §Q4. "
        f"Got: {JMF_CROP_MAP['Parsnips']!r}"
    )
    # Negative — the old colloquial value must NOT be present
    assert "גזר לבן" not in JMF_CROP_MAP.values(), (
        "Stale 'גזר לבן' value found in JMF_CROP_MAP — patch02 not applied?"
    )


def test_shallots_value_post_patch02():
    """patch02 (DECISION 2026-05-25 §Q4): Shallots Hebrew is 'בצלצלי שאלוט'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Shallots"] == "בצלצלי שאלוט", (
        f"Shallots Hebrew value drifted from DECISION §Q4. "
        f"Got: {JMF_CROP_MAP['Shallots']!r}"
    )
    # Negative — the pure-transliteration value must NOT be the lone match anymore
    assert JMF_CROP_MAP["Shallots"] != "שאלוט", (
        "Shallots still uses pure transliteration; patch02 not applied"
    )
```

### 3.4 AC-03 Counter assertion — UNCHANGED

The existing AC-03 Counter assertion (test_ac03_*) in `test_jmf_crop_map.py` checks the 2 by-design duplicate pairs:
- `"תערובת סלט": ["Mesclun", "Salad Mix"]`
- `"קישוא": ["Summer Squash", "Zucchini"]`

Parsnips and Shallots are NOT in any duplicate-target group (each has a unique Hebrew value before AND after this patch). The Counter assertion remains correct without modification. AC-04 in §4 of this spec verifies this.

### 3.5 CHANGELOG.md — `[Unreleased]` entry

Append under `[Unreleased]` section:

```markdown
### SFA-S003-P002-WP-B1-patch02 — JMF_CROP_MAP Hebrew terminology corrections (2026-05-25)
- `Parsnips`: Hebrew value changed from "גזר לבן" (colloquial) to "שורש פטרוזילה" (botanically accurate parsley root)
- `Shallots`: Hebrew value changed from "שאלוט" (pure transliteration) to "בצלצלי שאלוט" (Hebrew + transliteration hybrid)
- Per team_00 DECISION 2026-05-25 §Q4
- Closes the WP-B program (5/5 WPs + this patch LOD500_LOCKED)
```

---

## 4. Acceptance Criteria

**AC-01 — Parsnips Hebrew value updated.**
`JMF_CROP_MAP["Parsnips"] == "שורש פטרוזילה"`. The old value `"גזר לבן"` does NOT appear anywhere in `JMF_CROP_MAP.values()` (assert via `assert "גזר לבן" not in JMF_CROP_MAP.values()`).

**AC-02 — Shallots Hebrew value updated.**
`JMF_CROP_MAP["Shallots"] == "בצלצלי שאלוט"`. The old pure-transliteration value `"שאלוט"` does NOT remain as the Shallots value.

**AC-03 — Tomatillos unchanged (confirmed as-is).**
`JMF_CROP_MAP["Tomatillos"] == "תומאטיו"` (the patch01 value). No change introduced by this patch.

**AC-04 — AC-03 Counter assertion regression — STILL PASSES unchanged.**
Running the existing `test_ac03_*` test (from patch01) yields the same duplicate-target dict as before:
```python
{"תערובת סלט": ["Mesclun", "Salad Mix"],
 "קישוא": ["Summer Squash", "Zucchini"]}
```
Parsnips and Shallots do NOT introduce new duplicates (each Hebrew value remains unique across the dict).

**AC-05 — `JMF_CROP_MAP` size unchanged.**
`len(JMF_CROP_MAP) == 86` (same as post-patch01).

**AC-06 — `validate_aos.sh` 0 FAIL.**
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns exit code 0.

**AC-07 — All existing tests still PASS (zero regression).**
`pytest tests/crop_book/ -q` returns 343 passed (341 baseline + 2 new patch02 tests) + 1 pre-existing publisher failure (out-of-scope; predates WP-B).

**AC-08 — No LOD500_LOCKED file modified beyond §2.1 scope.**
`git diff <patch01-lock>..HEAD` shows changes ONLY in: `constants.py` (JMF_CROP_MAP 2 values + comment), `test_jmf_crop_map.py` (2 new test functions appended), `CHANGELOG.md` (entry appended). All other locked paths empty.

---

## 5. Test requirements

**Minimum 2 new tests** appended to `tests/crop_book/test_jmf_crop_map.py`:

1. `test_parsnips_value_post_patch02` — covers AC-01
2. `test_shallots_value_post_patch02` — covers AC-02

Existing tests untouched. AC-03 Counter assertion test from patch01 remains the regression coverage for AC-04 + AC-05.

---

## 6. Build sequence (3 steps — minimal patch)

**Step 1** — Read this LOD400 + DECISION file + verify current constants.py state (Parsnips line ~221; Shallots line ~215).

**Step 2** — Apply the 2 value edits to `constants.py` + append 2 test functions to `test_jmf_crop_map.py` + append CHANGELOG entry.

**Step 3** — Run focused tests:
```bash
pytest tests/crop_book/test_jmf_crop_map.py -v
```
Then run the full suite:
```bash
pytest tests/crop_book/ -q
```
Run `validate_aos.sh` — must return 0 FAIL.

**Step 4** — Commit as a single atomic commit (small enough to be atomic):
```
build(WP-B1-patch02): Hebrew terminology corrections per team_00 DECISION §Q4
```

---

## 7. PRE_HANDOFF advisory disposition

| # | Advisory | patch02 disposition |
|---|---|---|
| 1 | JMF PDF licensing | **N/A** (no PDF/NI content; pure constants.py edit) |
| 2 | LLM extraction cache | **N/A** (no LLM) |
| 3 | Tend whitelist | **N/A** (WP-B3 closed) |
| 4 | Transitive WP-A dependency | **N/A** (no engine surfaces touched) |

---

## 8. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | A production DB seeded BEFORE patch02 has rows with old Hebrew values for Parsnips / Shallots | UNKNOWN | LOW | Out-of-scope for this WP at the SPEC level. If team_00's production import runs surface bad data, a separate data-fix SQL is needed (UPDATE crops SET name_he = '...' WHERE name_he IN ('גזר לבן', 'שאלוט') AND ... — verify scope before running). Document in COMPLETION_REPORT §9 as an open operational item if relevant. |
| R-02 | Re-running `seed.py --all` with the new map values may create duplicate `crops` rows (one for the old name_he, one for the new) | LOW | LOW | The crop_id resolution flows from `JMF_CROP_MAP[crop_jmf_en] → crops.name_he → crops.id`. Changing the Hebrew value redirects the lookup. If production has an old-value crop row, a fresh import would either: (a) match the new Hebrew row if it exists, (b) create a new row leaving the old one orphaned. R-01's data-fix handles this. |
| R-03 | Builder is single-engine (team_110 Opus 4.7 acts as both orchestrator and builder) | LOW | LOW | Per LOD200 §10 + AC-08 enforcement: scope is 6 lines of code. IR#1 preserved via team_190 validator (GPT-5.5). Precedent: patch01 v1.1.3 cleanup. L-GATE_S R1 mandate explicitly notes this choice for team_190 transparency. |

---

## 9. LOD500_LOCKED file inventory (this patch must not modify any)

Same as B2 + B3 inventories cumulative. Headline:
- All WP-A + B1 + patch01 + B2 + B3 deliverables (ORM modules, importers, migrations 001-046)
- `tend.py`, `jmf.py`
- `views.py`, `publisher/`, `mu-plugin/`
- `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`

**ONLY permitted edits:**
- `constants.py` — 2 value edits in `JMF_CROP_MAP` (Parsnips + Shallots) + 2 inline comments
- `test_jmf_crop_map.py` — 2 appended test functions
- `CHANGELOG.md` — [Unreleased] entry

---

## 10. File-level deliverables summary

### CREATE (new files)

```
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch02/BUILD_REPORT_v1.0.0.md   (team_110 writes after L-GATE_B since team_110 is single-engine builder per §11 of LOD200)
```

### MODIFY (3 existing files — additive scope only)

```
organic_market_agent/crop_book/constants.py        ← 2 value edits in JMF_CROP_MAP literal
tests/crop_book/test_jmf_crop_map.py               ← 2 new test functions appended
CHANGELOG.md                                        ← [Unreleased] entry
```

### DO NOT TOUCH

See §2.2 + §9. Effectively ALL files except the 3 in MODIFY.

---

*LOD400 v1.0.0 — authored 2026-05-25 by team_110 (Claude Opus 4.7) under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*Pending: team_190 L-GATE_S validation.*
