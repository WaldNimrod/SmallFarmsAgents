# MANDATE — M5 Schema Patch (Team 20)

**Mandate ID:** `MANDATE-M5-SCHEMA-TEAM20`  
**From:** Team 100 (Architecture)  
**To:** Team 20 (Infrastructure)  
**Date:** 2026-03-31  
**Milestone:** M5 — Admin UI  
**Dependency:** Gate G4 ✅ PASS  
**Template:** `_COMMUNICATION/templates/MANDATE.md`

---

## Context

M5 adds write operations to the admin UI: alias CRUD, rule CRUD, observation flag management, and a manual run trigger. All write operations must be tied to an authenticated user and logged to `audit_log`. The `users` and `audit_log` tables already exist in the schema (migration 001). This mandate covers the seed and utility migration only — no structural changes.

---

## Scope

**Team 20 owns:** Alembic migrations, DB seed data, model correctness.  
**Team 10 owns:** All application code, routes, templates.  
**No Team 20 work touches Python routes or HTML.**

---

## Task 1 — Migration `015`: Seed admin user + ensure audit_log index

File: `organic_market_agent/db/versions/015_m5_seed_admin_user.py`

```python
revision = "015"
down_revision = "014"
```

### 1a — Seed one admin user

Insert a single admin user with a bcrypt-hashed password. The password is **`admin`** (to be changed on first login — this is a local dev tool only, not internet-facing).

```python
import bcrypt
from sqlalchemy import text

ADMIN_EMAIL = "admin@local"
ADMIN_PASSWORD = "admin"
ADMIN_NAME = "Administrator"

def upgrade() -> None:
    conn = op.get_bind()
    pw_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    conn.execute(text("""
        INSERT INTO users (email, password_hash, display_name, role, is_active)
        VALUES (:email, :hash, :name, 'admin', true)
        ON CONFLICT (email) DO NOTHING
    """), {"email": ADMIN_EMAIL, "hash": pw_hash, "name": ADMIN_NAME})
```

### 1b — Add performance index on `audit_log`

```python
op.create_index(
    "ix_audit_log_entity",
    "audit_log",
    ["entity_type", "entity_id"],
    if_not_exists=True,
)
op.create_index(
    "ix_audit_log_created_at",
    "audit_log",
    ["created_at"],
    if_not_exists=True,
)
```

### 1c — Add `observation_flags` index (used in QA flags screen)

```python
op.create_index(
    "ix_observation_flags_product_id",
    "observation_flags",
    ["product_id"],
    if_not_exists=True,
)
```

> **Note:** Check the `observation_flags` table columns first. If the table has `product_id` directly, index it. If it references via `normalized_observation_id`, skip this sub-task and document the actual FK.

---

## Task 2 — Verify `users` unique constraint on `email`

Confirm that `uq_users_email` (or equivalent) exists. If not, add:

```python
op.create_unique_constraint("uq_users_email", "users", ["email"])
```

---

## Task 3 — `db.check` update

Update `organic_market_agent/db/check.py` to also verify:
- `users` table has ≥ 1 active admin row
- `audit_log` indexes exist

---

## Verification (Team 20 must confirm before filing completion report)

```bash
alembic upgrade head          # → 014 -> 015 (head)
alembic current               # → 015
python -m organic_market_agent.db.check  # → PASS

# Verify user seeded
psql $DATABASE_URL -c "SELECT email, role, is_active FROM users;"
# Expected: admin@local | admin | true

# Verify indexes
psql $DATABASE_URL -c "\di ix_audit_log_entity ix_audit_log_created_at"
```

---

## Deliverables

- [ ] `organic_market_agent/db/versions/015_m5_seed_admin_user.py`
- [ ] Updated `organic_market_agent/db/check.py` (users + audit_log checks)
- [ ] Completion report: `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_M5_SCHEMA_COMPLETE_TEAM20.md`

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31
