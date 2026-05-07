# LOD400 — SFA-S002-P001-WP008 — Wire WP REST Primary into Scheduler + Admin (F-190-01 remediation)

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP008
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_BUILD
**Builder:** sfa_build (Sonnet, Team 10)
**Production validator:** team_99
**QA:** Team 50
**Validator:** external (re-validation cycle of WP005 bundle if scope warrants)
**Priority:** P0 — daily cron currently broken (will fail at next 06:00 UTC scheduled run)

---

## 1. Goal

Extend WP007's WP REST primary upload path from CLI-only (`organic_market_agent/__main__.py::_do_upload`) to **all upload entrypoints** so that the daily cron + Admin UI button + any future caller use the same `WP REST primary, FTPS fallback` policy. Without this, the daily cron at 06:00 UTC silently fails (FTPS over Bezeq-blocked port 21), even though Phase 1 manual smoke succeeded.

team_190 verdict `ccb5939` finding F-190-01 MEDIUM. Team 100 wires WP REST primary into the missing entrypoints.

---

## 2. Hard binding facts (from team_190 verdict)

- `organic_market_agent/scheduler/pipeline.py` lines ~285–338 still call FTPS-only `upload_artifacts` from `ftps_upload.py`.
- `organic_market_agent/admin/routes/runs.py::runs_upload_now` still FTPS-only.
- `organic_market_agent/utils/config.py::upress_configured()` keys off FTPS env vars only — does not recognize WP REST configuration as "upload-capable".
- The CLI path through `__main__.py::_do_upload` correctly prefers WP REST and is the only currently-working production path.

---

## 3. Acceptance Criteria

### AC-01 — Shared upload helper
Extract `_do_upload`'s WP-REST-primary + FTPS-fallback policy into a shared helper module callable from any entrypoint. Suggested location: `organic_market_agent/publisher/upload_dispatch.py` (new) with a single public function `dispatch_upload(output_dir, *, allow_fallback_ftps_env="UPRESS_FALLBACK_FTPS")` returning a structured result `(protocol_used, success_count, total_count, errors)`.

The function MUST:
- Prefer `wp_upload.upload_all_artifacts(output_dir)` when WP REST is configured.
- Optionally fall back to `ftps_upload.upload_artifacts(output_dir)` if `UPRESS_FALLBACK_FTPS=1` AND WP REST attempt fails.
- Default behavior: WP REST primary, no FTPS attempt unless flag is set.
- Log clearly which protocol was used (so `pipeline_alerts` can record it).

### AC-02 — `__main__.py::_do_upload` uses the shared helper
Refactor (without behavior change) so `_do_upload` is a thin wrapper around `dispatch_upload`. Existing CLI tests must continue to pass.

### AC-03 — `scheduler/pipeline.py` uses the shared helper
The upload phase block at L285–338 (the FTPS-only call site) is replaced with `dispatch_upload(...)`. Any error handling specific to the scheduler context (logging, `pipeline_alerts` insertion) is preserved.

### AC-04 — `admin/routes/runs.py::runs_upload_now` uses the shared helper
Same: existing FTPS-only call replaced with `dispatch_upload(...)`. Admin UI behavior unchanged from the user's perspective (success/failure UI same).

### AC-05 — `config.upress_configured()` recognizes WP REST
Update the function (or add `wp_rest_configured()` companion as already exists per WP007) so that callers checking "is upload configured" return True when WP REST keys are set, even without FTPS keys.

If WP007 already added `wp_rest_configured()`: update `upress_configured()` to OR the two checks: `return wp_rest_configured() or ftps_configured()`.

### AC-06 — Tests
- `tests/test_upload_dispatch.py` — unit tests for the new shared helper:
  - WP REST configured → calls wp_upload, returns success
  - WP REST configured but call raises → if `UPRESS_FALLBACK_FTPS=1` falls back; otherwise propagates error
  - Neither configured → raises clearly
- `tests/test_scheduler_upload_path.py` (new) OR extension of existing scheduler tests — assertion that the scheduler's upload phase routes through the shared helper, NOT directly through `ftps_upload.upload_artifacts`.
- All existing tests continue to pass.

### AC-07 — Documentation
- `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md` — §1 architecture summary updated to note the shared helper.
- `CHANGELOG.md` `[Unreleased] ### Fixed` entry referencing F-190-01.

---

## 4. Files in scope

### CREATE
- `organic_market_agent/publisher/upload_dispatch.py` — shared helper (~50-80 lines)
- `tests/test_upload_dispatch.py`

### UPDATE
- `organic_market_agent/__main__.py` — `_do_upload` becomes thin wrapper
- `organic_market_agent/scheduler/pipeline.py` — replace upload phase
- `organic_market_agent/admin/routes/runs.py` — replace `runs_upload_now`
- `organic_market_agent/utils/config.py` — `upress_configured()` recognizes WP REST
- `tests/test_scheduler_upload_path.py` (new file or update existing test_scheduler*)
- `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`
- `CHANGELOG.md`

### DO NOT TOUCH
- `wp_upload.py` itself (already correct from WP007)
- `ftps_upload.py` itself (defensive code preserved)
- DB schema, migrations, collectors, templates
- `_aos/governance/`, `_aos/roadmap.yaml`, `_aos/PENDING_DB_SYNC.yaml`
- shaked-wg-agent codebase (reference only)

---

## 5. Implementation notes

- The refactor should be **mechanical**: the existing `_do_upload` body is moved/extracted, then called from each entrypoint. No behavioral change for the CLI path.
- Be careful with imports — `scheduler/pipeline.py` should NOT import `__main__` (circular). Hence the new `publisher/upload_dispatch.py` location.
- `pipeline_alerts` insertion: preserve the scheduler's existing logic for alerting on failure; just feed it the new helper's structured result.
- Admin UI: the `runs_upload_now` endpoint returns JSON to the browser. Preserve the response shape so the UI doesn't break.

---

## 6. Test plan

### Unit
- `dispatch_upload` happy path (WP REST configured) — calls wp_upload, returns success tuple.
- Fallback gate (UPRESS_FALLBACK_FTPS=1 + WP REST raises) — falls back; result tuple shows `protocol_used: ftps`.
- No upload configured — raises explicit error.

### Integration
- Run `python -m organic_market_agent run_publisher --upload` (CLI) — must continue to upload via WP REST. Same as Phase 1.
- Run scheduler via `python -m organic_market_agent.scheduler.runner` (or whatever cron invokes) on a test fixture — must call WP REST.
- Hit Admin "Upload Now" via test client — must call WP REST.

### Production smoke (team_99 domain)
After deploy:
- Manually trigger `runs_upload_now` from Admin UI — confirm artifact_version advances.
- Wait for next scheduled cron run (06:00 UTC) OR force-trigger via `systemctl start sfa-pipeline.service` — confirm WP REST used (check logs for protocol).
- Public manifest fresh.

---

## 7. Risks

| Risk | Mitigation |
|------|-----------|
| Refactor breaks existing CLI behavior | Existing tests must pass unchanged; CI gate |
| Scheduler error-handling subtleties differ from CLI | Preserve scheduler-specific `pipeline_alerts` + try/except blocks; only swap the upload call |
| Admin UI response shape changes | Preserve JSON contract; add a smoke test for the route |
| Circular import (scheduler ↔ __main__) | Place shared helper in `publisher/upload_dispatch.py` (already separate package) |

---

## 8. Sprint estimate

**SMALL (<1 day)** — mechanical refactor + 3 entrypoints + tests + docs.

---

## 9. Out of scope

- WP001 (M10) — Phase 2 deferred.
- WP002 (MyPIPS) — Phase 2 deferred.
- LOD500 file authoring (F-190-03) — defer per Phase 1 L0 acceptance.

---

## 10. References

- team_190 verdict (commit `ccb5939`): `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md` §4 F-190-01
- WP007 LOD400: `_aos/work_packages/S002/SFA-S002-P001-WP007/LOD400_spec.md`
- WP007 build: `organic_market_agent/__main__.py::_do_upload` (the working pattern)
- Runbook: `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`

---

*LOD400 ready. Mechanical refactor — fast turnaround expected.*
