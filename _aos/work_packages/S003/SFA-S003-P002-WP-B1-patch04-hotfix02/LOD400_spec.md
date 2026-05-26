---
id: SFA-S003-P002-WP-B1-patch04-hotfix02-LOD400
wp: SFA-S003-P002-WP-B1-patch04-hotfix02 — Postgres transaction-poisoning fix in _upsert_variety
gate: L-GATE_S (LOD400 — LOD200 inlined for SMALL scope)
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-26
version: v1.0.0
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-hotfix02_2026-05-26_v1.0.0.md
parent_wp_hotfix01_lock_commit: "a7493a4"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_110 (Claude Opus 4.7 — single-engine, SMALL scope per hotfix01/patch02 precedent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator + single-engine builder) ≠ team_190 GPT-5.5 (validator) — IR#1 preserved via distinct validator engine"
---

# LOD400 — patch04-hotfix02

## 1. Goal

Replace transaction-poisoning `try/except: pass` swallow pattern with `ON CONFLICT (crop_id, name_en) DO NOTHING` SQL clause in `_upsert_variety`. Mirror the correct pattern already used by `_upsert_knowledge_note`.

## 2. Architecture

### 2.1 Files modified (3)
```
scripts/load_masterclass_sheets.py                    ← 1 function rewrite (_upsert_variety, ~10 LOC)
tests/integration/test_load_masterclass_sheets.py     ← +1 regression test
CHANGELOG.md                                           ← entry
```

## 3. Implementation

### 3.1 `_upsert_variety` rewrite

```python
# OLD (post-hotfix01):
def _upsert_variety(session, crop_id: int, variety_name: str):
    """Insert a crop_varieties row if not exists."""
    from sqlalchemy import text
    try:
        session.execute(
            text(
                "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
                "VALUES (:crop_id, :name_en, FALSE, FALSE)"
            ),
            {"crop_id": crop_id, "name_en": variety_name},
        )
    except Exception:
        pass  # UNIQUE conflict — variety already exists


# NEW:
def _upsert_variety(session, crop_id: int, variety_name: str):
    """Insert a crop_varieties row if not exists.

    Uses Postgres ON CONFLICT clause so a UNIQUE-constraint conflict does NOT
    poison the transaction. The previous try/except: pass pattern caught the
    Python exception but left Postgres in an aborted-transaction state →
    all subsequent INSERTs failed with InFailedSqlTransaction. SQLite did not
    exhibit this behavior; defect surfaced operationally on production (2026-05-26).
    """
    from sqlalchemy import text
    session.execute(
        text(
            "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
            "VALUES (:crop_id, :name_en, FALSE, FALSE) "
            "ON CONFLICT (crop_id, name_en) DO NOTHING"
        ),
        {"crop_id": crop_id, "name_en": variety_name},
    )
```

The unique constraint `uq_cv_crop_name_en` is on `(crop_id, name_en)`. SQLite supports `ON CONFLICT DO NOTHING` since 3.24+ — no SQLite regression expected.

### 3.2 Regression test

Append to `tests/integration/test_load_masterclass_sheets.py`:

```python
def test_load_masterclass_no_silent_try_except_around_execute():
    """patch04-hotfix02: _upsert_variety must use ON CONFLICT, not try/except: pass.

    Python try/except around session.execute catches the IntegrityError but
    does NOT rollback the Postgres transaction. All subsequent INSERTs fail
    with InFailedSqlTransaction. Defect surfaced 2026-05-26 during OP-2 prod
    run. This test guards against regression to the silent-swallow pattern.
    """
    from pathlib import Path
    script_path = Path(__file__).parents[2] / "scripts" / "load_masterclass_sheets.py"
    content = script_path.read_text(encoding="utf-8")

    # The fixed _upsert_variety must use ON CONFLICT (crop_id, name_en) DO NOTHING
    assert "ON CONFLICT (crop_id, name_en) DO NOTHING" in content, (
        "_upsert_variety must use ON CONFLICT clause to avoid Postgres "
        "transaction-poisoning on UNIQUE conflict"
    )

    # The forbidden pattern: bare try/except: pass around session.execute
    # We check the specific old-pattern snippet
    forbidden = "except Exception:\n        pass  # UNIQUE conflict"
    assert forbidden not in content, (
        "patch04-hotfix02 regression: silent try/except: pass around "
        "session.execute found in load_masterclass_sheets.py — must use "
        "ON CONFLICT DO NOTHING instead"
    )
```

### 3.3 CHANGELOG entry

```markdown
### SFA-S003-P002-WP-B1-patch04-hotfix02 — Postgres transaction-poisoning fix (2026-05-26)
- `scripts/load_masterclass_sheets.py::_upsert_variety`: replaced Python `try/except: pass` UNIQUE-conflict swallow with `ON CONFLICT (crop_id, name_en) DO NOTHING` SQL clause. Python `except` caught the IntegrityError but didn't rollback the Postgres transaction, causing all subsequent INSERTs to fail with `InFailedSqlTransaction`. SQLite tolerated; production Postgres poisoned.
- `tests/integration/test_load_masterclass_sheets.py`: +1 regression test (`test_load_masterclass_no_silent_try_except_around_execute`).
- Defect surfaced during OP-2 re-run post-hotfix01 (2026-05-26).
- Per team_00 DECISION_WP-B1-patch04-hotfix02_2026-05-26 §§1-3.
```

## 4. Acceptance Criteria (7 ACs)

- **AC-01** `_upsert_variety` body contains `ON CONFLICT (crop_id, name_en) DO NOTHING`
- **AC-02** `except Exception: pass` pattern around `session.execute` ABSENT from `_upsert_variety`
- **AC-03** `test_load_masterclass_no_silent_try_except_around_execute` passes
- **AC-04** `pytest tests/integration/ -q` → 15 passed (was 14; +1 new regression test)
- **AC-05** `pytest tests/crop_book/ -q` → 350 + 1 OOS publisher (unchanged from post-hotfix01)
- **AC-06** `validate_aos.sh` → 0 FAIL
- **AC-07** Diff scope: only `scripts/load_masterclass_sheets.py`, `tests/integration/test_load_masterclass_sheets.py`, `CHANGELOG.md`, `_aos/roadmap.yaml` (lifecycle), `_aos/work_packages/.../LOD400_spec.md`

## 5. Build sequence

1. Read this spec + DECISION
2. Apply §3.1 rewrite (`_upsert_variety`)
3. Append §3.2 regression test
4. Append §3.3 CHANGELOG
5. Run focused test → must pass
6. Full suites — counts per AC-04 + AC-05
7. validate_aos.sh — 0 FAIL
8. Single atomic commit:
```
build(WP-B1-patch04-hotfix02): Postgres transaction-poisoning fix in _upsert_variety

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

## 6. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | SQLite < 3.24 doesn't support `ON CONFLICT DO NOTHING` | Project requires Python 3.11+ which ships SQLite 3.40+. Verified compatible. |
| R-02 | More latent Postgres-only defects in load_to_db | Out-of-scope. If surfaced post-hotfix02, hotfix03 follows same pattern. |
| R-03 | Builder accidentally removes the docstring | LOD400 §3.1 shows full function body byte-exact. |

## 7. LOD500_LOCKED inventory

Per DECISION §3:
- `scripts/load_masterclass_sheets.py` — 1 function rewrite
- `tests/integration/test_load_masterclass_sheets.py` — +1 test
- `CHANGELOG.md` — entry

All other LOCKED files untouched.

## 8. Builder identity rationale (single-engine)

Per DECISION §4: SMALL scope (1 function ~10 LOC + 1 test), no architectural decisions. Precedent: hotfix01 same shape, also single-engine. IR#1 preserved via team_190 GPT-5.5 distinct validator engine.

---

*LOD400 v1.0.0 — 2026-05-26.*
*Pending: team_190 L-GATE_S.*
