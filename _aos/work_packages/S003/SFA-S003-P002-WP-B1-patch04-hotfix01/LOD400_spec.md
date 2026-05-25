---
id: SFA-S003-P002-WP-B1-patch04-hotfix01-LOD400
wp: SFA-S003-P002-WP-B1-patch04-hotfix01 — Postgres int↔bool fix in load_masterclass_sheets.py
gate: L-GATE_S (LOD400 — implementation spec, LOD200 inlined for SMALL scope)
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-26
version: v1.0.0
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-hotfix01_2026-05-26_v1.0.0.md
parent_wp_patch04_lock_commit: "3dbf803"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_110 (Claude Opus 4.7 — single-engine, SMALL scope per patch02 precedent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator + single-engine builder) ≠ team_190 GPT-5.5 (validator) — IR#1 preserved via distinct validator"
---

# LOD400 — patch04-hotfix01

## 1. Goal

Fix Postgres int↔bool defect in `scripts/load_masterclass_sheets.py` that prevented operational OP-2 from inserting data. SQLite was tolerant; Postgres rejected silently. ~3 LOC + 1 regression test.

## 2. Architecture

### 2.1 File MODIFIED (1) — narrow LOD500_LOCKED exception per DECISION §3

```
scripts/load_masterclass_sheets.py    ← 3 line edits (int→bool literals)
```

### 2.2 File MODIFIED (1) — additive (LOCKED but per DECISION §3 allowed)
```
tests/integration/test_load_masterclass_sheets.py    ← +1 test asserting Postgres-compatible SQL (or skipped if no PG fixture)
```

### 2.3 File MODIFIED (1) — additive
```
CHANGELOG.md    ← [Unreleased] entry
```

## 3. Implementation

### 3.1 `_upsert_variety` boolean fix

```python
# OLD (line ~358):
session.execute(
    text(
        "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
        "VALUES (:crop_id, :name_en, 0, 0)"
    ),
    ...
)
# NEW:
session.execute(
    text(
        "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
        "VALUES (:crop_id, :name_en, FALSE, FALSE)"
    ),
    ...
)
```

### 3.2 `_upsert_knowledge_note` boolean fix

```python
# OLD (line ~337):
"VALUES (:crop_id, :source, :tier, :nt, :body, 1, :model, :now) "
# NEW:
"VALUES (:crop_id, :source, :tier, :nt, :body, TRUE, :model, :now) "
```

### 3.3 New regression test — Postgres-compatible SQL assertion

Append to `tests/integration/test_load_masterclass_sheets.py`:

```python
def test_load_masterclass_uses_postgres_compatible_booleans():
    """patch04-hotfix01: INSERT statements use FALSE/TRUE literals, not 0/1.

    Postgres rejects int→bool coercion at INSERT time (CHECK constraint enforcement).
    SQLite tolerates it. This test guards against regression to int literals.
    """
    from pathlib import Path
    script_path = Path(__file__).parents[2] / "scripts" / "load_masterclass_sheets.py"
    content = script_path.read_text(encoding="utf-8")

    # Must NOT contain int-literal patterns in INSERT VALUES for the boolean columns
    bad_patterns = [
        ", 0, 0)",       # is_default, is_grafted
        ", 1, :model",   # is_internal_farm_use_only
        "VALUES (..., 1, :model",
        "(:crop_id, :name_en, 0, 0)",
    ]
    for bp in bad_patterns:
        assert bp not in content, (
            f"patch04-hotfix01 regression: int-literal pattern {bp!r} found in "
            f"load_masterclass_sheets.py — must use FALSE/TRUE for Postgres compat"
        )

    # MUST contain the corrected patterns
    assert "(:crop_id, :name_en, FALSE, FALSE)" in content, (
        "_upsert_variety missing FALSE, FALSE in INSERT"
    )
    assert ", TRUE, :model" in content, (
        "_upsert_knowledge_note missing TRUE literal for is_internal_farm_use_only"
    )
```

### 3.4 CHANGELOG.md

```markdown
### SFA-S003-P002-WP-B1-patch04-hotfix01 — Postgres int↔bool fix (2026-05-26)
- `scripts/load_masterclass_sheets.py`: INSERT statements now use `FALSE`/`TRUE` literals instead of `0`/`1` for boolean columns (`is_default`, `is_grafted`, `is_internal_farm_use_only`). SQLite was tolerant; production Postgres rejected silently.
- `tests/integration/test_load_masterclass_sheets.py`: +1 regression test (`test_load_masterclass_uses_postgres_compatible_booleans`) that scans the script source for forbidden int-literal patterns.
- Defect surfaced during OP-2 operational run on production (commit `3dbf803`'s patch04 build). 0 rows inserted via `--load-db` against Postgres; backup taken before any operational mutation.
- Per team_00 DECISION_WP-B1-patch04-hotfix01_2026-05-26 §§1-3.
```

## 4. Acceptance Criteria (6 ACs)

- **AC-01** `_upsert_variety` INSERT uses `FALSE, FALSE`
- **AC-02** `_upsert_knowledge_note` INSERT uses `TRUE` (not `1`)
- **AC-03** `test_load_masterclass_uses_postgres_compatible_booleans` passes
- **AC-04** `pytest tests/integration/ -q` returns N+1 passing (was 13; expect 14)
- **AC-05** `pytest tests/crop_book/ -q` unchanged from post-patch06 state: 350 passed + 1 OOS publisher
- **AC-06** `validate_aos.sh` returns 0 FAIL
- **AC-07** `git diff <patch06-lock>..HEAD` shows changes ONLY in: `scripts/load_masterclass_sheets.py`, `tests/integration/test_load_masterclass_sheets.py`, `CHANGELOG.md`, and lifecycle-only fields of `_aos/roadmap.yaml`

## 5. Build sequence

1. Read this spec + DECISION
2. Apply §3.1 + §3.2 (3 line edits in script)
3. Append §3.3 regression test
4. Append §3.4 CHANGELOG entry
5. Run focused test: `pytest tests/integration/test_load_masterclass_sheets.py::test_load_masterclass_uses_postgres_compatible_booleans -v` — must pass
6. Full suite: `pytest tests/integration/ -q tests/crop_book/ -q`
7. `validate_aos.sh`
8. Single atomic commit:
```
build(WP-B1-patch04-hotfix01): Postgres int↔bool fix in load_masterclass_sheets.py

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

## 6. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | Regression test pattern-matches non-INSERT code accidentally (false negative) | Tight string matching with VALUES context; manual verification |
| R-02 | Other scripts (patch03_data_fix.py) might have same bug | Out-of-scope; this hotfix is for load_masterclass_sheets only. patch03_data_fix uses parameterized SQLAlchemy text() — needs separate audit if defect suspected |
| R-03 | SQLite tests now fail because they use the literal text 'FALSE'/'TRUE' | SQLite ACCEPTS both FALSE/TRUE and 0/1 as boolean literals (per SQLite docs). No regression. |

## 7. LOD500_LOCKED inventory

Per DECISION §3:
- `scripts/load_masterclass_sheets.py` — 3 line edits (this hotfix)
- `tests/integration/test_load_masterclass_sheets.py` — +1 test
- `CHANGELOG.md` — entry

All other LOCKED files untouched.

## 8. Builder identity rationale (single-engine)

Per DECISION §4: SMALL scope (3 LOC + 1 test), no architectural decisions, no schema changes, precedent: patch02 v1.0.0 cleanup. IR#1 preserved via team_190 distinct validator engine.

---

*LOD400 v1.0.0 — 2026-05-26 by team_110.*
*Pending: team_190 L-GATE_S.*
