---
id: DECISION_WP-B1-patch04-hotfix02_2026-05-26_v1.0.0
from: team_00 (Principal — in-session)
to: [team_110, team_190, team_100]
date: 2026-05-26
type: DECISION
scope: SFA-S003-P002-WP-B1-patch04-hotfix02 — Postgres transaction-poisoning fix in _upsert_variety
status: AUTHORIZED
trigger: "OP-2 re-run on production Postgres post-hotfix01 surfaced a second defect: _upsert_variety uses Python try/except: pass to swallow UNIQUE conflicts, but Postgres still poisons the transaction → all subsequent INSERTs fail with InFailedSqlTransaction. SQLite did not poison; tests passed. patch04 build never tested concurrent-variety inserts against Postgres."
parent_wp: SFA-S003-P002-WP-B1-patch04 (LOD500_LOCKED at 3dbf803)
sibling_wp: SFA-S003-P002-WP-B1-patch04-hotfix01 (LOD500_LOCKED at a7493a4 — addressed int↔bool only)
---

# DECISION — patch04-hotfix02

## §1. Defect

`scripts/load_masterclass_sheets.py::_upsert_variety` (line ~352):

```python
try:
    session.execute(text(
        "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
        "VALUES (:crop_id, :name_en, FALSE, FALSE)"  # post-hotfix01
    ), {"crop_id": crop_id, "name_en": variety_name})
except Exception:
    pass  # UNIQUE conflict — variety already exists
```

The Python `except: pass` catches the SQLAlchemy IntegrityError but **does NOT rollback the Postgres transaction**. Postgres marks the transaction as aborted; all subsequent `session.execute()` calls fail with `InFailedSqlTransaction`. SQLite does not poison transactions on constraint conflicts → tests passed.

`_upsert_knowledge_note` (line ~328) already uses `ON CONFLICT (crop_id, source, note_type) DO NOTHING` correctly. The fix is to mirror that pattern in `_upsert_variety`.

## §2. Scope

**Single file:** `scripts/load_masterclass_sheets.py`

**One change:** replace `try/except` swallow pattern with `ON CONFLICT (crop_id, name_en) DO NOTHING` SQL clause.

**One test:** add Postgres-pattern regression check to ensure no remaining `try/except: pass` around `session.execute` in the script.

## §3. LOD500_LOCKED scope exception

Single-file narrow exception (`scripts/load_masterclass_sheets.py`) — already authorized as a follow-up by hotfix01's precedent. Same operational rationale.

## §4. Builder + Validator

- **Builder:** single-engine team_110 (Opus 4.7) — SMALL scope (1 line edit + 1 test), patch02 + hotfix01 precedent
- **Validator:** team_190 (GPT-5.5) — IR#1 preserved

## §5. Out-of-scope

- Other scripts (patch03_data_fix, patch06_db_cleanup) — verified separately
- `_get_or_create_crop` SELECT-then-INSERT pattern — works correctly in OP-2 because all 27 cache records have existing `name_he` in crops table (lazy-creation branch never reached)
- Re-architecting `load_to_db` — out-of-scope
- Reopening patch04 itself

## §6. Operational continuation

After hotfix02 LOD500_LOCKED → resume OP-2 → OP-3 → patch07 (OP-4).

---

*DECISION 2026-05-26 — second hotfix in the patch04 lineage. team_00 in-session "hotfix02 מלא" directive.*
