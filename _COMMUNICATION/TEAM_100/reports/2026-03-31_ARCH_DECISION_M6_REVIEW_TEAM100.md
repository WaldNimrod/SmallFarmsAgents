# ARCH_DECISION — M6 Implementation Review

**Document ID:** `ARCH-20260331-M6-REVIEW-TEAM100`  
**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev) · Team 20 (Infrastructure) · Team 50 (QA)  
**Date:** 2026-03-31  
**Milestone:** M6 — Automation + Resilience  
**Template:** `_COMMUNICATION/templates/ARCH_DECISION.md`

---

## Decision

**Team 20 (migration 016):** ✅ ACCEPTED  
**Team 10 (M6 features):** ✅ ACCEPTED  

No critical bugs found. Two advisory items noted (non-blocking for G6). Gate G6 QA may proceed immediately.

---

## Team 20 — Accepted as Filed

Migration `016_m6_scheduler_and_alerts.py` is correct and well-documented.

**Deviations from mandate — all accepted:**

| # | Mandate text | Implementation | Assessment |
|---|-------------|----------------|------------|
| D1 | `ON CONFLICT DO NOTHING` for seed | `INSERT ... WHERE NOT EXISTS (SELECT 1 FROM scheduler_config)` | **Correct.** `ON CONFLICT DO NOTHING` requires a UNIQUE constraint with an explicit target; without one, PostgreSQL rejects the syntax. `WHERE NOT EXISTS` achieves the same semantic safely. |
| D2 | `INTEGER` FK for `pipeline_alerts.ingestion_run_id` | `BigInteger` | **Correct.** `ingestion_runs.id` is `BigInteger` in migration 001. Matching type is required to satisfy the FK constraint. Mandate text had a type mismatch. |
| D3 | `SERIAL` PK | `Integer() + Identity(always=False)` | **Accepted.** PostgreSQL-native equivalent; SQLAlchemy 2.x preferred idiom over `SERIAL`. |

All required CHECK constraints, indexes, `downgrade()`, models, `__init__.py` exports, and `db.check` extensions are present and correct. `pytest tests/` — 73 passed, 1 skipped.

---

## Team 10 — Accepted

All nine tasks from the mandate have been implemented. Full review:

### `scheduler/runner.py`
- Self-gating logic correct: `is_enabled` guard → time guard (±1 min) → overlap guard → create run → `run_pipeline` → write alert.
- `scheduled_time_matches` and `alert_for_run_outcome` are correctly factored as testable pure helpers.
- `if __name__ == "__main__": main()` block confirmed present — cron invocation via `python -m organic_market_agent.scheduler.runner` will work.
- Alert levels correct: `failed` → `error`; `sources_failed > 0` → `warning`; clean → `info`.

### `scheduler/pipeline.py`
- `source_code`, `skip_normalize`, `skip_publish`, `retry_attempts` kwargs added correctly.
- Empty `pairs` after `source_code` filter writes a `PipelineAlert(level='error')` and marks run `failed` — correct fail-fast behaviour.
- Unhandled exception catch marks run `failed` if still in `running` state — correct resilience.

### `scheduler/run_ingestion.py`
- `retry_attempts` parameter added to `execute_ingestion_for_run`. Retry loop: `max_tries = 1 + max(0, retry_attempts)` — correct (0 retries = 1 attempt, 2 retries = 3 attempts). 1s sleep between attempts.

### `admin/routes/runs.py`
- Trigger accepts `source_code`, `skip_normalize`, `skip_publish`. Reads `retry_attempts` from `scheduler_config`.
- `sources_total` pre-set to filtered `len(pairs)` before background thread.
- `functools.partial` used correctly to pass kwargs to background thread.
- List shows last 50 rows with `duration_secs` and `alert_count` subquery.
- `any_running` flag drives `<meta http-equiv="refresh" content="5">` in template.

### `admin/routes/scheduler.py`
- All four routes implemented: `scheduler_page`, `scheduler_update`, `scheduler_toggle`, `scheduler_run_cleanup`.
- Server-side validation for all fields (ranges enforced).
- `audit_write` called on all mutations.
- Cleanup SQL matches mandate exactly (CTE with `RETURNING`, cascades via FK).
- `cleanup_last_run` updated after cleanup.

### `admin/routes/alerts.py`
- `alert_mark_read` and `alerts_mark_all_read` implemented.
- `request.referrer` fallback to dashboard on mark-read redirect — good UX.

### `admin/__init__.py`
- `g.unread_alert_count` injected in `before_request` with `try/except` guard (safe if table missing before migration).
- `scheduler` and `alerts` blueprints registered in correct order.

### `tests/test_runner.py`
- 6 tests covering: `scheduled_time_matches` edge cases, disabled guard, wrong-time guard, successful run (run_pipeline called with correct args + info alert), partial run (warning alert), `alert_for_run_outcome` unit tests.
- Mock strategy (single `MagicMock` context manager reused across both `SessionFactory()` calls in `main()`) is valid — MagicMock is reentrant.

### `tests/test_scheduler_routes.py`
- 4 tests; correctly uses `db_session.expire_all()` before re-reading config after toggle POST (required because the route uses a different session).
- Cleanup test uses byte-string match for Hebrew flash message OR `b"0"` — pragmatic and correct.

### `docs/OPERATIONS.md`
- English, concise, correct cron line with `logs/` directory note.

---

## Advisory Items (non-blocking for G6)

| ID | Location | Finding | Recommendation |
|----|----------|---------|----------------|
| A1 | `runs.py` L15 | `_get_active_sources_with_profiles` imported (underscore = module-private). Works correctly; follows existing pattern in `pipeline.py`. | No change required for G6. Consider exporting as public function in M7 cleanup. |
| A2 | `test_scheduler_routes.py` T3 | Cleanup test asserts `b"0" in r.data` as fallback. In a fresh test DB this will always be the fallback path. | Acceptable for G6. Team 50 must run T07 manually on the live DB where old rows may exist. |

---

## Test Suite

`pytest tests/ -q` → **85 passed, 1 skipped** (QA001 skip — G4 waiver in force). No regressions.

---

## Completion Reports Required

Before G6 QA begins, Team 10 must file:
- `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M6_IMPLEMENTATION_COMPLETE_TEAM10.md` (using `COMPLETION_REPORT.md` template)
- `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_M6_REVIEW_REQUEST_TEAM50.md` (using `QA_REVIEW_REQUEST.md` template)

These were not delivered with the implementation report. **File before Team 50 begins G6 QA.**

---

## G6 QA Instruction (Team 50)

Proceed with `QA_MANDATE_G6.md`. No mandate amendments required.

Pre-condition note: cron line must be installed on host (Team 20 responsibility per `docs/OPERATIONS.md`) before T-cron evidence can be collected. T09 (`test_runner.py`) covers the gating logic without needing the cron installed.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Sign-off ID:** `ARCH-20260331-M6-REVIEW-TEAM100`
