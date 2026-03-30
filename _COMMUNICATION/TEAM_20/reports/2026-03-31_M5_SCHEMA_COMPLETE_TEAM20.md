# M5 Schema — completion report (Team 20)

**Date:** 2026-03-31  
**Mandate ID:** `MANDATE-M5-SCHEMA-TEAM20`  
**Reference:** `_COMMUNICATION/TEAM_20/MANDATE_M5_SCHEMA_TEAM20.md`

---

## Deliverables

| Item | Status |
|------|--------|
| `organic_market_agent/db/versions/015_m5_seed_admin_user.py` | Added |
| `organic_market_agent/db/check.py` | Updated (active admin + indexes) |
| Completion report | This file |

---

## Task 2 — `users.email` unique

No migration change. Revision **001** already defines unique index `uq_users_email` on `users.email`. Adding `create_unique_constraint` would duplicate that guarantee.

---

## Task 1b — `audit_log` indexes

Mandate names `ix_audit_log_entity` / `ix_audit_log_created_at`. Revision **001** already created **`idx_audit_log_entity`** `(entity_type, entity_id)` and **`idx_audit_log_created`** `(created_at)`. Migration **015** does **not** add second indexes on the same columns. **`db.check`** asserts those logical indexes exist (via SQLAlchemy `inspect.get_indexes`).

---

## Task 1a / 1c — Migration 015

- Seeds `admin@local` / bcrypt hash for password `admin`, display name `Administrator`, `role='admin'`, `ON CONFLICT (email) DO NOTHING`.
- `CREATE INDEX IF NOT EXISTS ix_observation_flags_product_id ON observation_flags (product_id)`.

---

## Verification commands (excerpt)

```text
$ alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade 014 -> 015, 015: M5 — seed local admin user + observation_flags index.

$ alembic current
015 (head)

$ python -m organic_market_agent.db.check
...
  OK  users (active admin): 1 rows (expected >= 1)
  OK  audit_log index on (entity_type, entity_id)
  OK  audit_log index on (created_at)
  OK  observation_flags index on (product_id)
RESULT: PASS

$ pytest tests/ -q
62 passed, 1 skipped
```

---

## Other code change (test hygiene)

`tests/test_publisher_local.py`: replaced obsolete assertion that HTML contains the string `bootstrap` (template no longer does) with a check for `dir="rtl"`, so the full suite passes after M5 work. Unrelated to schema; keeps CI green.

---

## Blockers

None.

---

*Team 20 (Infrastructure)*
