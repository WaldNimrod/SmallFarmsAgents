---
id: SFA-S003-P002-WP-B1-patch03-LOD400
wp: SFA-S003-P002-WP-B1-patch03 — JMF_CROP_MAP taxonomic expansion (11 value changes)
gate: L-GATE_S (LOD400 — implementation spec)
status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S verdict
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.1
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD200_spec.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md
parent_wp_patch02_lock_commit: "3d78007"
builder: team_10 (Sonnet sub-agent)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B1-patch03: Taxonomic Expansion

**Read before writing a single line of code:**

1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD200_spec.md`
2. team_00 DECISION: `_COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md` — esp. §§1-4
3. Current `JMF_CROP_MAP` (post-patch02) in `organic_market_agent/crop_book/constants.py` — 86 entries
4. Current `test_jmf_crop_map.py` — `test_jmf_crop_map_duplicate_target_allowlist` (line ~37) + `test_ac03_duplicate_group_count` (line ~142)

---

## 1. Goal

Apply 11 Hebrew-value corrections + update 2 LOCKED tests + append 11 regression tests. Net effect: 25 → 24 duplicate-target groups; 5 new baseline `crops.name_he` values introduced.

---

## 2. Architecture

### 2.1 Files modified (3)

```
organic_market_agent/crop_book/constants.py    ← 11 value edits in JMF_CROP_MAP
                                                  + 1 inline comment block citing DECISION
tests/crop_book/test_jmf_crop_map.py            ← UPDATE 2 LOCKED tests + APPEND 11 regression tests
CHANGELOG.md                                     ← [Unreleased] entry
```

### 2.2 LOD500_LOCKED scope exception

Per DECISION §4, two test functions are modifiable in this WP only:
- `test_jmf_crop_map_duplicate_target_allowlist`
- `test_ac03_duplicate_group_count`

All other locked files untouched.

---

## 3. Implementation — exact code changes

### 3.1 `constants.py` — 11 value edits

Locate each line and replace. ALL edits go inside the existing `JMF_CROP_MAP` literal. Add an inline comment block before the first edit:

```python
    # ─── BEGIN patch03 taxonomy corrections (2026-05-25) ───
    # Per team_00 DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md.
    # 11 value changes; introduces 5 new baseline crops.name_he values
    # (עלי בייבי, עגבניית שרי, עגבניות מורשת, מלפפון חממה, כרוב סיני).
    # Net effect on duplicate-target allowlist: 25 → 24 groups.
```

**The 11 edits (presented in the order they appear in the file; line numbers approximate):**

| # | Old line | New line |
|---|----------|----------|
| 1 | `"Brussels Sprouts":   "כרוב ניצנים",` (unchanged — for context) | (no change) |
| — | (the 11 edits below) | |
| 1 | `"Mesclun":            "תערובת סלט",` | `"Mesclun":            "עלי בייבי",` |
| 2 | `"Salad Mix":          "תערובת סלט",` | `"Salad Mix":          "עלי בייבי",` |
| 3 | `"Baby kale":                  "קייל",` | `"Baby kale":                  "עלי בייבי",` |
| 4 | `"Greenhouse Cherry Tomato":   "עגבנייה",` | `"Greenhouse Cherry Tomato":   "עגבניית שרי",` |
| 5 | `"Greenhouse Heirloom Tomato": "עגבנייה",` | `"Greenhouse Heirloom Tomato": "עגבניות מורשת",` |
| 6 | `"Greenhouse Libanese Cucumber":    "מלפפון",` | `"Greenhouse Libanese Cucumber":    "מלפפון חממה",` |
| 7 | `"Chinese Cabbage":             "כרוב",` | `"Chinese Cabbage":             "כרוב סיני",` |
| 8 | `"Hot Pepper":                  "פלפל",` | `"Hot Pepper":                  "פלפל חריף",` |
| 9 | `"Beans (Bush)":       "שעועית",` | `"Beans (Bush)":       "שעועית שיחית",` |
| 10 | `"Snow Peas":          "אפונת שלגים",` | `"Snow Peas":          "אפונת שלג",` |
| 11 | `"Basil":              "בזיל",` | `"Basil":              "בזיליקום",` |

**Builder safety:** use unique-substring matching (the full `"Mesclun":            "תערובת סלט",` line is unique) — don't `replace_all` the value strings, since several values appear in multiple lines (e.g., `"תערובת סלט"` is shared between Mesclun and Salad Mix).

### 3.2 `test_jmf_crop_map.py` — update LOCKED test #1

Replace the body of `test_jmf_crop_map_duplicate_target_allowlist` (line ~37) with the new 24-group dict:

```python
def test_jmf_crop_map_duplicate_target_allowlist(jmf_crop_map):
    """AC-03 (patch03): exactly 24 by-design duplicate Hebrew-target groups
    per LOD400 v1.0.0 §3.4 + DECISION_WP-B1-patch03_TAXONOMY §3."""
    counts = Counter(jmf_crop_map.values())
    duplicates = {
        v: sorted([k for k, mv in jmf_crop_map.items() if mv == v])
        for v, c in counts.items() if c > 1
    }
    assert duplicates == {
        # ── NEW patch03 group ──
        "עלי בייבי":     ["Baby kale", "Mesclun", "Salad Mix"],

        # ── Baseline pairs from WP-B1 (Mesclun/Salad Mix תערובת סלט group disappeared) ──
        "קישוא":          ["Summer Squash", "Zucchini"],

        # ── patch01 typo / synonym / qualifier groups (mostly unchanged) ──
        "כרוב ניצנים":    ["Brussel Sprouts", "Brussels Sprouts"],
        "פאק צ'וי":       ["Bok Choy", "Pak Choi"],
        "כוסברה":         ["Cilantro", "Coriander"],
        "מנגולד":         ["Chard", "Swiss Chard"],
        "אבטיח":          ["Watermelon", "Watermelons"],
        "תפוח אדמה":      ["Potato", "Potatoes"],
        "גזר":            ["Carrots", "Fresh Carrots"],
        "בצל":            ["Onions", "Storage Onion"],
        "בצל ירוק":       ["Green Onion", "Scallions"],
        "כרישה":          ["Leek Storage", "Leek Summer", "Leeks"],

        # ── Shrunk groups (patch03 splits removed members) ──
        "פלפל":           ["Bell Pepper", "Peppers"],                       # was 3; Hot Pepper left
        "עגבנייה":        ["Roma Tomato", "Tomatoes"],                       # was 4; Cherry + Heirloom left
        "מלפפון":         ["Cucumbers", "Greenhouse English Cucumber"],     # was 3; Libanese key left
        "כרוב":           ["Cabbage", "Fall Cabbage", "Savoy Cabbage",
                           "Summer Cabbage"],                                # was 5; Chinese left

        # ── Unchanged patch01 groups ──
        "חסה":            ["Lettuce", "Salanova Lettuce", "Sucrine"],
        "צנונית":         ["Raddish", "Radishes", "Winter Radish"],
        "תרד":            ["Spinach", "Spinach TR", "Spinarch SD"],
        "כרובית":         ["Cauliflower", "Cauliflower / Romanesco"],
        "לפת":            ["Hakurei Turnip", "Turnips"],
        "סלרי שורש":      ["Celery Root", "Mini Celery Root"],
        "שומר":           ["Fennel", "Mini Fennel"],
        "חציל":           ["Eggplant", "Eggplant  (Feld)"],
    }, f"unexpected Hebrew-value duplicates: {duplicates}"
```

**Disappeared groups** (no longer in the dict):
- `"תערובת סלט"` (Mesclun + Salad Mix both → "עלי בייבי")
- `"קייל"` (Baby kale → "עלי בייבי"; Kale alone)

### 3.3 `test_jmf_crop_map.py` — update LOCKED test #2

Replace `test_ac03_duplicate_group_count` (line ~142):

```python
def test_ac03_duplicate_group_count(jmf_crop_map):
    """AC-03 (patch03): exactly 24 Hebrew values appear more than once."""
    counts = Counter(jmf_crop_map.values())
    dup_count = sum(1 for c in counts.values() if c > 1)
    assert dup_count == 24, f"Expected 24 duplicate-target groups, got {dup_count}"
```

### 3.4 `test_jmf_crop_map.py` — append 11 regression tests

Append after the patch02 tests:

```python
# ─── patch03 regression tests (DECISION_WP-B1-patch03_TAXONOMY_2026-05-25) ───

def test_mesclun_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Mesclun"] == "עלי בייבי"


def test_salad_mix_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Salad Mix"] == "עלי בייבי"


def test_baby_kale_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Baby kale"] == "עלי בייבי"


def test_cherry_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Cherry Tomato"] == "עגבניית שרי"


def test_heirloom_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Heirloom Tomato"] == "עגבניות מורשת"


def test_lebanese_cucumber_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Libanese Cucumber"] == "מלפפון חממה"


def test_chinese_cabbage_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Chinese Cabbage"] == "כרוב סיני"


def test_hot_pepper_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Hot Pepper"] == "פלפל חריף"


def test_beans_bush_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Beans (Bush)"] == "שעועית שיחית"


def test_snow_peas_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Snow Peas"] == "אפונת שלג"


def test_basil_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Basil"] == "בזיליקום"
```

### 3.5 `CHANGELOG.md` — `[Unreleased]` entry

Append under `[Unreleased]`:

```markdown
### SFA-S003-P002-WP-B1-patch03 — JMF_CROP_MAP taxonomic expansion (2026-05-25)
- **NEW baseline crops** (5 name_he values introduced): עלי בייבי, עגבניית שרי, עגבניות מורשת, מלפפון חממה, כרוב סיני
- **Remapped to עלי בייבי** (3 keys): Mesclun, Salad Mix, Baby kale
- **Split off umbrella categories** (5 keys): Greenhouse Cherry Tomato (→ עגבניית שרי), Greenhouse Heirloom Tomato (→ עגבניות מורשת), Greenhouse Libanese Cucumber (→ מלפפון חממה), Chinese Cabbage (→ כרוב סיני), Hot Pepper (→ פלפל חריף)
- **Hebrew refinements** (3 keys): Beans (Bush) → שעועית שיחית; Snow Peas → אפונת שלג; Basil → בזיליקום
- Duplicate-target allowlist: 25 → 24 groups (תערובת סלט + קייל groups disappear; עלי בייבי group of 3 appears; 4 groups shrink)
- LOD500_LOCKED scope exception: 2 test functions updated per DECISION_WP-B1-patch03_TAXONOMY §4
- Per team_00 DECISION_WP-B1-patch03_TAXONOMY_2026-05-25 §§1-4
```

---

## 4. Acceptance Criteria (18 ACs)

### 4.1 Per-value assertions (AC-01..AC-11)

For each of the 11 keys, `JMF_CROP_MAP[<key>] == <new value>`:

- **AC-01** Mesclun → `"עלי בייבי"`
- **AC-02** Salad Mix → `"עלי בייבי"`
- **AC-03** Baby kale → `"עלי בייבי"`
- **AC-04** Greenhouse Cherry Tomato → `"עגבניית שרי"`
- **AC-05** Greenhouse Heirloom Tomato → `"עגבניות מורשת"`
- **AC-06** Greenhouse Libanese Cucumber → `"מלפפון חממה"`
- **AC-07** Chinese Cabbage → `"כרוב סיני"`
- **AC-08** Hot Pepper → `"פלפל חריף"`
- **AC-09** Beans (Bush) → `"שעועית שיחית"`
- **AC-10** Snow Peas → `"אפונת שלג"`
- **AC-11** Basil → `"בזיליקום"`

### 4.2 Structural assertions (AC-12..AC-15)

- **AC-12** `len(JMF_CROP_MAP) == 86` (unchanged)
- **AC-13** Duplicate-target allowlist = 24 groups exactly, matching §3.2 dict literal.
- **AC-14** `test_ac03_duplicate_group_count` asserts `dup_count == 24`.
- **AC-15** Five new Hebrew strings appear at least once each in `JMF_CROP_MAP.values()`: עלי בייבי, עגבניית שרי, עגבניות מורשת, מלפפון חממה, כרוב סיני.

### 4.3 Hygiene (AC-16..AC-18)

- **AC-16** `pytest tests/crop_book/ -q` returns 354 passed (343 baseline + 11 new patch03 tests; 2 LOCKED test updates absorb in place) + 1 pre-existing publisher failure (out-of-scope per team_00).
- **AC-17** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns exit code 0.
- **AC-18** `git diff <patch02-lock>..HEAD` shows changes ONLY in: `constants.py`, `test_jmf_crop_map.py`, `CHANGELOG.md`, and lifecycle-only fields of `_aos/roadmap.yaml`. All other locked paths empty.

---

## 5. Test requirements

**Minimum 13 tests touched:**
- 2 LOCKED tests updated in place (per DECISION §4 exception)
- 11 new regression tests appended

Existing patch02 tests (`test_parsnips_value_post_patch02`, `test_shallots_value_post_patch02`) and all WP-B1/patch01 tests remain unchanged.

---

## 6. Build sequence

**Step 1** — Read this LOD400 + DECISION + LOD200 + verify current constants.py state (must match the "Old line" column of §3.1 for all 11 keys).

**Step 2** — Apply the 11 value edits to `constants.py` (one Edit per line; use unique-substring matching since some values appear in multiple lines).

**Step 3** — Update the 2 LOCKED tests in `test_jmf_crop_map.py` per §3.2 + §3.3.

**Step 4** — Append the 11 regression tests per §3.4.

**Step 5** — Append CHANGELOG entry per §3.5.

**Step 6** — Run focused tests:
```bash
pytest tests/crop_book/test_jmf_crop_map.py -v
```
Then full suite:
```bash
pytest tests/crop_book/ -q
```
Then validate_aos.sh — must return 0 FAIL.

**Step 7** — Single atomic commit:
```
build(WP-B1-patch03): JMF_CROP_MAP taxonomic expansion per team_00 DECISION
```

**Builder safety:** verify the duplicate-target dict in §3.2 BYTE-EXACTLY by counting groups (24) and total keys-with-duplicates (**55** keys total in the dict — sum of group sizes; verifiable via `python3 -c "from organic_market_agent.crop_book.constants import JMF_CROP_MAP; from collections import Counter; c=Counter(JMF_CROP_MAP.values()); print(sum(n for n in c.values() if n>1))"` after applying value edits) BEFORE committing. Mismatch indicates an edit slipped.

---

## 7. PRE_HANDOFF advisory disposition

| # | Advisory | patch03 disposition |
|---|---|---|
| 1 | JMF PDF licensing | **N/A** (no PDF content; constants.py edits) |
| 2 | LLM extraction cache | **N/A** (no LLM) |
| 3 | Tend whitelist | **N/A** (WP-B3 closed) |
| 4 | Transitive WP-A dependency | **N/A** (no engine surfaces touched) |

---

## 8. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | Production DB seeded BEFORE patch03 has rows with old Hebrew values for the 11 affected crops | UNKNOWN | LOW | Out-of-scope at spec level per DECISION §8. team_00 to run data-fix SQL post-merge if needed. |
| R-02 | Five new baseline `crops` rows must be created lazily by next import — if any importer code path assumes specific `crops.name_he` rows exist at startup, it would fail | LOW | LOW | Importer code (`jmf_masterclass.py`, etc.) uses lazy `crops.upsert(name_he=X)` pattern (verified in WP-B1 build). No startup assumption. |
| R-03 | Builder accidentally `replace_all` a shared value string (e.g., `"תערובת סלט"` appears in Mesclun + Salad Mix lines) instead of unique-substring matching | MEDIUM | LOW | Spec §3.1 explicitly warns. Use full-line matching with key prefix. AC-13 catches via the 24-group structural assertion. |
| R-04 | The updated 24-group dict in §3.2 has a typo or wrong group membership | MEDIUM | MEDIUM | Builder MUST run `pytest tests/crop_book/test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist -v` after edits and BEFORE commit. The assertion error message includes the actual diff. |
| R-05 | "עלי בייבי" string interpreted differently in different fonts / spaces (RTL spacing) | LOW | LOW | Use copy-paste from DECISION §1.1 verbatim. Hebrew roundtrip test (`test_jmf_crop_map_hebrew_roundtrip`) provides encoding-integrity coverage. |

---

## 9. LOD500_LOCKED file inventory (patch03 narrow exception)

Same as patch02 + cumulative. The narrow scope exception authorized in DECISION §4 is limited to:
- `tests/crop_book/test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist` (single function body)
- `tests/crop_book/test_jmf_crop_map.py::test_ac03_duplicate_group_count` (single constant `25` → `24`)

All OTHER locked files (models, importers, migrations, governance) untouched.

---

## 10. File-level deliverables summary

### CREATE (new files)

```
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch03/BUILD_REPORT_v1.0.0.md   (sub-agent writes after build)
```

### MODIFY (3 existing files — additive scope + 2-function LOCKED exception)

```
organic_market_agent/crop_book/constants.py     ← 11 value edits + 1 comment block in JMF_CROP_MAP
tests/crop_book/test_jmf_crop_map.py            ← 2 LOCKED tests updated + 11 regression tests appended
CHANGELOG.md                                     ← [Unreleased] entry
```

### DO NOT TOUCH

Everything else. Explicit no-touch list:
- `models.py`, `source_registry.py`, `field_policy.py`, `reconciler.py`, `enrichment_runner.py`
- `crop_task_templates.py`, `crop_knowledge_notes.py`, `crop_harvest_stats.py`
- `jmf_masterclass.py`, `tend_overlay.py`, `ni_importer.py`, all `ni/` subclasses
- `tend.py`, `jmf.py`, `seed.py`
- `views.py`, `publisher/`, `mu-plugin/`
- All migrations 001-046
- `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`
- `_aos/roadmap.yaml` — lifecycle fields only (team_110 transitions, NOT the builder)

---

## 11. Builder identity

Sonnet sub-agent (team_10), spawned by team_110 per the standard IR#1 orchestrator-vs-builder pattern. NOT a single-engine build (contrast patch02 §11 — that scope was 4 LOC; this is ~70 LOC + LOCKED test edits, exceeding the single-engine threshold).

---

*LOD400 v1.0.0 — authored 2026-05-25 by team_110 (Claude Opus 4.7) under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*v1.0.1 (2026-05-25) — R2 correction per team_190 L-GATE_S R1 verdict F-S-PATCH03-01: §6 builder-safety line corrected to state "55 keys total" (sum of group sizes for the 24-group dict — prior wording had incorrect arithmetic). Added verification command. No change to ACs, values, scope, or builder identity.*
*Pending: team_190 L-GATE_S R2 validation.*
