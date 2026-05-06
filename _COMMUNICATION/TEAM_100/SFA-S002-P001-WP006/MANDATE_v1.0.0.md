# MANDATE — SFA-S002-P001-WP006 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (Opus, orchestrator)
**To:** sfa_build (Sonnet, Team 10 builder)
**WP:** SFA-S002-P001-WP006 — FTPS Upload Remediation (F-01 fix)
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)
**Priority:** P0 — blocking launch + active public regression (site stuck on 19-day-old data)

---

## 1. Identity

You are **sfa_build (Team 10)** running on Claude Sonnet. Cross-engine: orchestrator team_100 = Opus, you = Sonnet, validator = external. Stay distinct.

---

## 2. The problem

Production FTPS upload to uPress has been broken since at least 2026-04-17 (last successful upload). team_99's verification (Pass-1, 2026-05-06) confirmed root cause:

> Standard Python `ftplib.FTP_TLS` does not perform TLS session reuse on data connections. uPress requires it. Result: 425 / timeout / no STOR success.

**Site is showing 19-day-old data publicly. This is the launch blocker.**

---

## 3. The fix (already known — restore lost pattern)

Restore the `ReusedSessionFTP_TLS` subclass in `organic_market_agent/publisher/ftps_upload.py`. This pattern was historically present in SFA but appears to have regressed.

### Authoritative reference (read first, do NOT modify)

```
/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/ftps_upload.py
/Users/nimrod/Documents/shaked-wg-agent/tests/test_ftps_upload.py
```

The shaked-wg-agent docstring confirms: *"Pattern copied from SmallFarmsAgents/organic_market_agent/publisher/ftps_upload.py"*. shaked-wg-agent uploads to the same uPress server successfully — its implementation works. Adapt back into SFA.

---

## 4. Binding spec

`_aos/work_packages/S002/SFA-S002-P001-WP006/LOD400_spec.md` — 7 ACs (AC-01..AC-07). Read fully.

---

## 5. Working environment

| Item | Value |
|------|-------|
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` (already checked out) |
| Repo root | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Python | 3.11 |
| DB | offline (not needed for this WP) |
| Env | `.env.example` shows `UPRESS_SFTP_*` keys — actual credentials only on production server, not in dev |

---

## 6. Process

1. Read this mandate + LOD400 spec end-to-end.
2. Read `organic_market_agent/publisher/ftps_upload.py` — current SFA state. Note what's there and what's missing.
3. Read the **shaked-wg-agent reference**: `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/ftps_upload.py` — full file.
4. Read the shaked-wg-agent test: `/Users/nimrod/Documents/shaked-wg-agent/tests/test_ftps_upload.py`.
5. Restore the `ReusedSessionFTP_TLS` subclass in SFA's `ftps_upload.py`. Adapt namespacing/logging/constants to SFA conventions, but keep the TLS behavior identical to the reference.
6. Route the upload entry point through the new subclass (replace `FTP_TLS()` with `ReusedSessionFTP_TLS()`).
7. Add/update `tests/test_ftps_upload.py` — mirror the shaked-wg-agent test where applicable.
8. Run `pytest tests/test_ftps_upload.py -v` — green.
9. Run full pytest suite — no regressions (DB-dependent tests may skip, that's fine).
10. Run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — 0 FAIL.
11. Update `CHANGELOG.md` `[Unreleased]` `### Fixed` with one line about F-01.
12. Commit with message starting `build(S002-WP006): restore ReusedSessionFTP_TLS subclass — F-01 fix`.
13. Do NOT push (team_100 will push after review).

---

## 7. Hard constraints

1. No DB schema changes, no migrations.
2. No collector changes.
3. No template/CSS changes (those are WP004's territory).
4. No `_aos/` writes (governance read-only).
5. No `_aos/roadmap.yaml` writes (team_100 single-writer).
6. **Do NOT modify the shaked-wg-agent codebase** — it is reference-only.
7. **Do NOT commit credentials** — `.env` values stay off the branch (only `.env.example`).
8. No git push — commits only.

---

## 8. Reporting back

Final message format:

```markdown
## WP006 Build Report

### Status
PASS | PASS_WITH_FINDINGS | BLOCKED

### Acceptance Criteria status
| AC | Status | Evidence |
| AC-01 ReusedSessionFTP_TLS subclass | ... | ... |
| AC-02 Code path uses subclass | ... | ... |
| AC-03 Unit + integration tests | ... | ... |
| AC-04 Local smoke (if creds available, optional) | ... | ... |
| AC-05/06/07 (deferred to deploy + WP003 Pass-2) | DEFERRED | Handed to team_99 |

### Files changed
<list>

### Tests
<count + result>

### validate_aos.sh
<result line>

### Commit SHA(s)
<sha>

### Deploy hand-off note for team_99
- Branch tip after build: <sha>
- Manual deploy command: `python -m organic_market_agent run_publisher --upload`
- Smoke target: artifact_version on https://www.nimrod.bio/wp-content/uploads/market/manifest.json should advance within 60s of run

### Blockers / open questions
<list or none>
```

---

## 9. Authority limits

- MAY commit to offline branch.
- MAY NOT push, merge, tag, or issue gate verdicts.
- MAY NOT touch shaked-wg-agent code.
- MAY NOT touch credentials.

---

*Mandate issued. Cross-engine: Sonnet builder. Final validator external. Production deploy by team_99 after this build completes.*
