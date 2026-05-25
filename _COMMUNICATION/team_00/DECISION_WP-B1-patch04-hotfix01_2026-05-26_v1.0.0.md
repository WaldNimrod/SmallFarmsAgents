---
id: DECISION_WP-B1-patch04-hotfix01_2026-05-26_v1.0.0
from: team_00 (Principal — in-session)
to: [team_110, team_190, team_100]
date: 2026-05-26
type: DECISION
scope: SFA-S003-P002-WP-B1-patch04-hotfix01 — fix Postgres int↔bool defect in load_masterclass_sheets.py
status: AUTHORIZED
trigger: "Operational OP-2 run on production Postgres surfaced silent INSERT failures. load_masterclass_sheets.py uses int literals (0/1) for boolean columns; SQLite (used in patch04 tests) coerces these silently, but production Postgres rejects with type-mismatch. 0 rows inserted across all 24 cache JSONs. Bug confirmed via docker exec INSERT probe."
parent_wp: SFA-S003-P002-WP-B1-patch04 (LOD500_LOCKED at commit 3dbf803)
---

# DECISION — patch04-hotfix01

## §1. The defect

In `scripts/load_masterclass_sheets.py`:

- `_upsert_variety()` line ~358: `INSERT ... is_default, is_grafted) VALUES (..., 0, 0)`
- `_upsert_knowledge_note()` line ~337: `INSERT ... is_internal_farm_use_only, ...) VALUES (..., 1, ...)`

Postgres CHECK constraints + boolean column types reject integer literals. SQLite is tolerant; patch04's integration tests ran on SQLite only.

## §2. Scope of hotfix

**Single file:** `scripts/load_masterclass_sheets.py`

**Three changes:**
1. `_upsert_variety` — `VALUES (:crop_id, :name_en, 0, 0)` → `VALUES (:crop_id, :name_en, FALSE, FALSE)`
2. `_upsert_knowledge_note` — `VALUES (..., 1, :model, :now)` → `VALUES (..., TRUE, :model, :now)`
3. Add integration test using **Postgres test fixture** (not SQLite) to prevent regression. If no Postgres test fixture exists, document as deferred and add a SQL syntax linting test.

## §3. LOD500_LOCKED scope exception

`scripts/load_masterclass_sheets.py` was authored in patch04 and locked at `3dbf803`. team_00 authorizes a **narrow exception** for this file (3 line changes + 1 test) to fix the production defect.

The `tests/integration/test_load_masterclass_sheets.py` file (also patch04) may be extended with 1 new Postgres-specific test if a fixture is available.

## §4. Builder + Validator

- **Builder:** single-engine team_110 (Opus 4.7). The fix is mechanical (3 line edits + 1 test); precedent: patch02 single-engine builder for SMALL scope.
- **Validator:** team_190 (GPT-5.5) — IR#1 preserved via distinct validator engine.

## §5. Out-of-scope

- Refactoring `load_to_db` architecture
- Adding Postgres-Docker test infrastructure if not already present
- Re-validating the 24 JSON cache files (those are correct; the bug is purely in the DB INSERT step)
- Reopening patch04 itself — patch04 stays LOD500_LOCKED with this hotfix as a follow-up

## §6. Operational continuation

After patch04-hotfix01 LOD500_LOCKED:
- Resume OP-2: `python scripts/load_masterclass_sheets.py --load-db ...` against production Postgres
- Then OP-3: `python scripts/patch06_db_cleanup.py --apply`
- Then OP-4: open patch07 WP for sheet 056

---

*DECISION recorded 2026-05-26 by team_110 transcribing team_00 in-session "patch04-hotfix WP מלא" directive.*
