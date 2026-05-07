# MANDATE — SFA-S002-P001-WP008 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (Opus, orchestrator)
**To:** sfa_build (Sonnet, Team 10 builder)
**WP:** SFA-S002-P001-WP008 — Wire WP REST primary into scheduler + admin (F-190-01 remediation)
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)
**Priority:** P0 — daily cron currently broken (will fail tomorrow at 06:00 UTC)
**Triggered by:** team_190 verdict `ccb5939` finding F-190-01

---

## 1. Identity

You are **sfa_build (Team 10)** running on Claude Sonnet under cross-engine governance. team_100 (Opus) orchestrates; you build; team_190 (Cursor Composer) just delivered the verdict pointing to this gap; team_99 will deploy. Stay distinct (Iron Rule #1).

---

## 2. Why this exists

You completed WP007 (commit `73eaf3e`) and wired WP REST primary into `__main__.py::_do_upload` (CLI). That path works in production — team_99 verified. **However, you missed two other entrypoints:**

1. `organic_market_agent/scheduler/pipeline.py` (lines ~285–338) — the daily cron entrypoint
2. `organic_market_agent/admin/routes/runs.py::runs_upload_now` — the Admin UI button

Both still call FTPS-only `ftps_upload.upload_artifacts`. team_190's external review (verdict `ccb5939`, finding F-190-01) flagged this. **Tomorrow's 06:00 UTC cron will fail** unless this is fixed.

This is a mechanical refactor. Extract `_do_upload`'s policy into a shared helper, call it from all three entrypoints.

---

## 3. Binding spec

`_aos/work_packages/S002/SFA-S002-P001-WP008/LOD400_spec.md` — 7 ACs (AC-01..AC-07). Read fully.

---

## 4. Reference

The working pattern is already in your own commit `73eaf3e`:
- `organic_market_agent/__main__.py::_do_upload` — primary pattern
- `organic_market_agent/utils/config.py::wp_rest_configured()` — gate check helper

team_190 verdict (read for context): `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md` (commit `ccb5939`).

---

## 5. Working environment

| Item | Value |
|------|-------|
| Branch (already checked out) | `offline/2026-05-07-smallfarmsagents-release-prep` (now merged to main; offline branch tip ~`d7731cf`, main tip `92c84e2`) |
| Repo root | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Python | 3.11 |
| DB | offline (not needed for this WP) |
| Network | port 21 blocked (so any FTPS smoke locally is meaningless — skip) |

Note: main and offline are now synchronized. Continue work on the offline branch.

---

## 6. Architectural target

Create `organic_market_agent/publisher/upload_dispatch.py` with:

```python
def dispatch_upload(
    output_dir: Path,
    *,
    allow_fallback_ftps_env: str = "UPRESS_FALLBACK_FTPS",
) -> UploadResult:
    """WP REST primary, optional FTPS fallback. Single source of truth for all upload entrypoints."""
    # 1. If wp_rest_configured() → call wp_upload.upload_all_artifacts(output_dir)
    # 2. If WP REST attempt raises AND os.environ.get(allow_fallback_ftps_env) == "1" → call ftps_upload.upload_artifacts(output_dir)
    # 3. If neither configured → raise NoUploadConfigured
```

Then 3 entrypoint refactors:
- `__main__.py::_do_upload` — call `dispatch_upload(output_dir)` (preserve existing CLI surface)
- `scheduler/pipeline.py` L285-338 — call `dispatch_upload(output_dir)` (preserve `pipeline_alerts` insertion)
- `admin/routes/runs.py::runs_upload_now` — call `dispatch_upload(output_dir)` (preserve JSON response shape)

Plus `config.py::upress_configured()` returns `wp_rest_configured() or ftps_configured()`.

Plus tests.

---

## 7. Hard constraints

1. **Mechanical refactor only** — no behavior change for the CLI path.
2. **Preserve scheduler error handling** — `pipeline_alerts` insertion, try/except, retry policy stay intact.
3. **Preserve admin response shape** — Admin UI doesn't break.
4. **No DB schema, migrations, collectors, templates touched.**
5. **No `_aos/` writes** (governance, roadmap, PENDING_DB_SYNC).
6. **No git push** — commits only.
7. **Do NOT remove `ftps_upload.py`** — defensive code retained.
8. **Do NOT modify `wp_upload.py`** — already correct from WP007.

---

## 8. Process

1. Read MANDATE + LOD400 + team_190 verdict §4 (F-190-01) end-to-end.
2. Read current state of `__main__.py`, `scheduler/pipeline.py`, `admin/routes/runs.py`, `utils/config.py`.
3. Create `publisher/upload_dispatch.py` with the policy extracted.
4. Refactor `__main__.py::_do_upload` → thin wrapper. Run existing tests; must pass unchanged.
5. Refactor `scheduler/pipeline.py` upload phase. Add scheduler-specific test (`tests/test_scheduler_upload_path.py` or extension).
6. Refactor `admin/routes/runs.py::runs_upload_now`. Add admin route test.
7. Update `config.py::upress_configured()`.
8. Add `tests/test_upload_dispatch.py` (unit tests per AC-06).
9. Run `pytest tests/` — green (some DB tests skip — fine).
10. Run `validate_aos.sh` — 0 FAIL.
11. Update runbook §1 architecture summary + `CHANGELOG.md` `[Unreleased] ### Fixed` (F-190-01).
12. Commit with message starting `build(S002-WP008): wire WP REST primary into scheduler + admin — F-190-01 fix`.
13. Do NOT push.

---

## 9. Reporting back

Final report per the standard build report format. Include AC table, files changed, test results, validate_aos result, commit SHA, deploy hand-off note for team_99 (since this needs to land on production before tomorrow's 06:00 UTC cron).

---

## 10. Authority limits

- MAY commit to offline branch.
- MAY NOT push, merge, tag, or issue gate verdicts.
- MAY NOT modify governance, roadmap, FTPS code, wp_upload.py, shaked-wg-agent.

---

*Mandate issued. P0 — daily cron must work via WP REST before tomorrow 06:00 UTC.*
