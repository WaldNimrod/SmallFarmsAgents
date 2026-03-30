# ARCH_DECISION — M5 Admin UI Review

**Document ID:** `ARCH-20260331-M5-REVIEW-TEAM100`  
**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev) · Team 20 (Infrastructure) · Team 50 (QA)  
**Date:** 2026-03-31  
**Milestone:** M5 — Admin UI  
**Template:** `_COMMUNICATION/templates/ARCH_DECISION.md`

---

## Summary

Team 100 has reviewed the M5 completion reports from Team 10 and Team 20.

| Team | Verdict | Notes |
|------|---------|-------|
| Team 20 — migration 015 | ✅ **ACCEPTED** | Clean, correct. Audit_log index note is well-reasoned. |
| Team 10 — Admin UI | ⚠️ **CONDITIONAL ACCEPT** | Two critical bugs in `run_ingestion.py` patched by Team 100 in this document. All other findings advisory. |

G5 QA may proceed immediately after this patch is applied.

---

## Team 20 — Accepted as Filed

Migration `015_m5_seed_admin_user.py` is correct:
- `admin@local` user seeded with bcrypt hash, `ON CONFLICT DO NOTHING`.
- `ix_observation_flags_product_id` added.
- No duplicate `audit_log` indexes created (correct: `idx_audit_log_entity` and `idx_audit_log_created` already exist from migration 001). The docstring explains this clearly.
- `db.check` extended to verify admin user presence and all three indexes.
- `downgrade()` correctly reverses both the user seed and the new index.

---

## Team 10 — Critical Bugs Found and Patched

### Bug 1 — `@click.command()` decorator on a shared Python helper

**File:** `organic_market_agent/scheduler/run_ingestion.py`

`execute_ingestion_for_run()` was decorated with `@click.command()` and three `@click.option()` decorators. Click wraps the function in a `BaseCommand` object at import time. When `scheduler/pipeline.py` imports and calls it as a plain Python callable:

```python
execute_ingestion_for_run(session, ingestion_run, pairs)
```

Click intercepts the call, reads `sys.argv`, and attempts CLI parsing — the three Python arguments are silently discarded and the function body never executes. The background pipeline triggered from the Admin UI (`/runs/trigger`) would complete the HTTP response, create the `IngestionRun` row, and then do nothing in the background thread.

**Fix:** Decorators removed from `execute_ingestion_for_run`. A thin `run_ingestion_cli` Click command now wraps the `run_ingestion()` helper. `if __name__ == "__main__"` now calls `run_ingestion_cli(standalone_mode=True)`.

### Bug 2 — `NameError` for counter variables in `run_ingestion()`

**File:** `organic_market_agent/scheduler/run_ingestion.py`

After calling `execute_ingestion_for_run(session, ingestion_run, pairs)`, `run_ingestion()` referenced `succeeded`, `failed`, `skipped`, `community_succeeded` — local variables of `execute_ingestion_for_run`, not visible in the caller. Any CLI invocation would raise `NameError` at the `click.echo` line.

**Fix:** Counters now read from `ingestion_run` model fields (`ingestion_run.sources_succeeded`, `ingestion_run.sources_failed`, `ingestion_run.community_sources_succeeded`), which `execute_ingestion_for_run` populates before returning.

---

## Advisory Items (non-blocking for G5)

| ID | Location | Finding | Action |
|----|----------|---------|--------|
| A1 | `pipeline.py` L4 | `from datetime import date` unused | Removed by Team 100 in this patch |
| A2 | `routes/runs.py` | T09 mock patches correct path `...runs.run_pipeline` — verified matches runtime import | No action needed |
| A3 | `run_ingestion.py` | `status='completed'` — DB CHECK allows `running/completed/partial/failed` | Confirmed correct. No action. |
| A4 | UI strings | Hebrew `flash()` and `login_message` strings — acceptable for Hebrew UI | No action needed |

---

## Status Constraint Verification (A3)

```sql
SELECT pg_get_constraintdef(c.oid)
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
WHERE t.relname = 'ingestion_runs' AND c.contype = 'c';
```

Result:
```
CHECK (status IN ('running', 'completed', 'partial', 'failed'))
```

`'completed'` is a valid value. No schema change needed.

---

## Files Patched by Team 100

- `organic_market_agent/scheduler/run_ingestion.py` — Bug 1, Bug 2
- `organic_market_agent/scheduler/pipeline.py` — A1 (unused import)

---

## QA Handoff Instruction (Team 50)

Gate G5 QA may now proceed using `QA_MANDATE_G5.md`. No mandate changes are required. The run trigger (`POST /runs/trigger`) is now functionally correct — `execute_ingestion_for_run` is a plain Python function with no Click decoration, and the pipeline background thread will execute correctly.

Pre-condition for T07 (run trigger test): ensure alembic is at `015` and the admin server is restarted after this patch.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Sign-off ID:** `ARCH-20260331-M5-REVIEW-TEAM100`
