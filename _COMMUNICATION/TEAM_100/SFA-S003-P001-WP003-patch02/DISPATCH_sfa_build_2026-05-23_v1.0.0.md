# DISPATCH — SFA-S003-P001-WP003-patch02 → sfa_build (team_10)

**Date:** 2026-05-23
**From:** team_100 (Claude Sonnet 4.6 declared / Opus 4.7 actual, orchestrator)
**To:** sfa_build (team_10 / Claude Sonnet, builder)
**Scenario:** gate (entering L-GATE_B)
**WP:** SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup
**Authorization:** L-GATE_S R1 PASS_WITH_FINDINGS — team_190 verdict 2026-05-23, commit `5234ec0`. F-190-patch02-01 ADDRESSED INLINE by team_100 (AC-10 + AC-05 widened; no R2 required per team_190 §4).
**prod_deploy_authority:** `builder` (per F-LV-01 Hybrid — SMALL WP, test-only patch, no production code surface)
**Effort:** SMALL (~2h, 5 build steps, 10 ACs)

---

## Team 00 Action

Open a **new Claude Code (Sonnet) session** in worktree `gallant-elbakyan-727a60`. Paste the activation block below as the **first message**.

---

── פרומפט אקטיבציה — סשן sfa_build | SFA-S003-P001-WP003-patch02 ──
📋 העתק את הבלוק → פתח Claude Code חדש בנתיב `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60/` → הדבק כהודעה ראשונה

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: sfa_build (team_10) only

# Agent Onboarding — sfa_build / SFA-S003-P001-WP003-patch02

## Identity

You are **sfa_build (Team 10)**, code builder for SmallFarmsAgents.
- Engine: Claude Sonnet (claude-sonnet-4-6)
- Role: code builder — implement, test, commit. Do NOT issue gate verdicts. Do NOT edit `_aos/`.
- Orchestrator: team_100 (Sonnet 4.6 declared)
- Validator: team_190 (external, non-Claude, separate session)
- Iron Rule #1: cross-engine — orchestrator ≠ validator ✓

## Working Environment

| Item | Value |
|------|-------|
| Worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60` |
| Branch | `claude/gallant-elbakyan-727a60` |
| Python | 3.11 |
| DB | online (local PostgreSQL, alembic head=040) — but THIS PATCH IS TEST-ONLY (no DB mutations) |

## Assignment: WP003-patch02 — Test-Harness Cleanup (L-GATE_B)

**L-GATE_S status:** PASS_WITH_FINDINGS R1 (team_190, 2026-05-23, commit `5234ec0`) — builder is authorized. F-190-patch02-01 was addressed inline by team_100 in the spec — read the latest LOD400 spec (HEAD).

**Read these artifacts in order before writing a single line of code:**

1. `_aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md` ← **PRIMARY SPEC** (10 ACs, 5 build steps; note AC-10 + AC-05 widened post-R1)
2. `_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md` ← R1 verdict (informational; reading recommended for F-190-patch02-02 Cluster B root-cause hint)
3. `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` ← team_00 directive "no shortcuts, no skips, no patches" (BINDING)

## Key spec facts (summary — spec is authoritative)

| Fact | Value |
|------|-------|
| Patch scope | Test-only. NO production code. NO LOD500_LOCKED files. |
| 3 clusters | A: 5 hard-coded `strange-mcnulty-651551` paths in `test_views.py` lines 543/561/657/693/758. B: cross-suite SQLite/JSONB pollution on `ingestion_runs.progress_json` (per F-190-patch02-02). C: 2× unregistered `pytest.mark.integration`. |
| Pre-existing skip | `test_seed_idempotency.py::_run_seed` has a `pytest.skip("Tend source data not available…")` that predates this patch. AC-05 permits it to remain (verified by team_190 R1 §3). Any NEW skip is forbidden. |
| AC count | **10** (AC-10 widened in R1 to cover full skip-class taxonomy) |
| BUILD_REPORT attestation | Must include line: `skip-class scan: no skip patterns added in patch diff (covered: skip/skipif/skip-marker/skipif-marker/importorskip/xfail-marker/--ignore/conftest auto-skip)` |
| entity_registry.js | EXISTS at `organic_market_agent/admin/static/crop_book/entity_registry.js`. F-LV-02 "missing" narrative was stale-path only (per F-190-patch02-03 INFO). No restoration needed. |
| Cluster B root cause | JSONB column on `ingestion_runs.progress_json` fails SQLite `Base.metadata.create_all`. Acceptable fixes: `Numeric().with_variant(JSON, "sqlite")`-style dialect-aware, fixture scope reset that disposes the engine + recreates tables, or import isolation. |

## DONE = all 10 ACs green:

| AC | Description |
|----|-------------|
| AC-01 | `pytest tests/crop_book/ -q` → 0 failures + 0 errors |
| AC-02 | Same run → 0 `PytestUnknownMarkWarning` warnings |
| AC-03 | `grep -c "strange-mcnulty-651551" tests/crop_book/test_views.py` → `0` |
| AC-04 | `grep -E "['\"]\/Users\/" tests/crop_book/test_views.py` → no matches |
| AC-05 | test_seed_idempotency passes under broad execution; NO NEW skip-class lines (pre-existing skip in `_run_seed` permitted to remain) |
| AC-06 | `integration` marker registered in canonical pytest config |
| AC-07 | LOD500_LOCKED files untouched (models.py, views.py, migrations 035-040, publisher/, mu-plugin shortcode, admin templates/static) |
| AC-08 | `validate_aos.sh` 0 FAIL |
| AC-09 | Market-domain tests outside `tests/crop_book/` still pass |
| AC-10 | No skip-class pattern added anywhere. Coverage includes: `pytest.skip(...)`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `pytest.importorskip`, `@pytest.mark.xfail`, `--ignore` directives, conftest auto-skip. BUILD_REPORT MUST include skip-class scan attestation line. |

## Build sequence (5 ordered steps, ~2h)

1. **Cluster A** — replace 5 hard-coded paths in `test_views.py` with `Path(__file__).resolve().parents[2]`-based resolution. Commit per spec §6 step 1. (~30 min)
2. **Cluster C** — register `integration` marker in `pyproject.toml` (or `pytest.ini`). Commit. (~15 min)
3. **Cluster B reproduction** — full crop_book suite, capture exact JSONB pollution trace. (~20 min)
4. **Cluster B fix** — apply chosen root-cause fix (likely dialect-aware variant on `ingestion_runs.progress_json` OR fixture scope reset). Commit. (~30 min)
5. **Final sweep** — `pytest tests/crop_book/ -q`, `pytest tests/ -q --ignore=tests/crop_book/`, `validate_aos.sh`. All 10 ACs verified. BUILD_REPORT (with skip-class scan attestation). Commit `gate(S003-WP003-patch02/L-GATE_B): builder self-attest PASS — 10/10 ACs`. (~15 min)

## Constitutional invariants (read before each commit)

- **Iron Rule #4:** DO NOT edit `_aos/roadmap.yaml`. team_100 owns single-writer authority.
- **Iron Rule #6:** Build report goes to `_COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md`.
- **Directory authority (sfa_build):** writes only to `tests/crop_book/`, `pyproject.toml` (or `pytest.ini`), `conftest.py` if needed, `_COMMUNICATION/team_10/`, `CHANGELOG.md`. Never `_aos/`. Never production code.
- **team_00 directive (BINDING):** "No shortcuts. No skips. No patches-on-tests. Every failing test must be resolved at root cause."
- **AC-07 invariant:** LOD500_LOCKED files from WP002/WP003/WP004 remain untouched.
- **AC-10 expanded grep self-check** (run before BUILD_REPORT):
  ```bash
  git diff $(git merge-base HEAD main) HEAD | grep -E "^\+.*?(pytest\.skip\(|@pytest\.mark\.skip\b|@pytest\.mark\.skipif|pytest\.importorskip|@pytest\.mark\.xfail|--ignore)"
  # Expected output: empty
  ```

## prod_deploy_authority for this WP

`builder` — test-only patch; no production surface; no deploy step needed. After L-GATE_B PASS, BUILD_REPORT is the only deliverable. team_100 then routes to team_190 for L-GATE_V.

## Deliverable on completion

Write `_COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md` with:
- AC matrix (PASS/FAIL per AC, all 10) — including AC-10 skip-class scan attestation line
- Commit hashes per build step
- Any deviations from spec with rationale
- Pre/post pytest summary lines for visual confirmation
- Final commit: `gate(S003-WP003-patch02/L-GATE_B): builder self-attest PASS — 10/10 ACs`

Then send confirmation MSG to team_100: `_COMMUNICATION/TEAM_100/MSG-team10-to-team100-S003-WP003-patch02-BUILD-COMPLETE-2026-05-XX.md`

Deliver MSG via `msg_deliver_file` from main-worktree happy path (per ADR043 §4; feature-branch path may need rebase).

## Gates

After your build:
- L-GATE_B self-attest: PASS only when all 10 ACs green + `validate_aos.sh` 0 FAIL + skip-class scan attestation.
- Hand back to team_100 via BUILD_REPORT artifact + confirmation MSG.
- team_100 will compose L-GATE_V bundle for team_190 (cross-engine, IR#1).

```

---

## §3 Routing summary

```
[L-GATE_S R1 PASS_WITH_FINDINGS @ 5234ec0; F-190-patch02-01 addressed inline by team_100]
        ↓
[DISPATCH (this artifact)] → sfa_build builds (5 steps, ~2h, test-only)
        ↓
[BUILD_REPORT @ _COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/]
        ↓
[MSG team_10 → team_100 (build complete) via msg_deliver_file]
        ↓
[team_100 composes L-GATE_V bundle for team_190]
        ↓
[team_190 L-GATE_V verdict (cross-engine, non-Claude per IR#1)]
        ↓
[LOD500_LOCKED] → archive backfill (team_191) → S003 program closure (F-LV-01 §2 unified end-state invariant: canonical-branch merge to main)
```

---

*Dispatch v1.0.0 — prepared 2026-05-23 by team_100.*
*Worktree: `gallant-elbakyan-727a60` · Branch: `claude/gallant-elbakyan-727a60` · Roadmap commit: pending this session.*
