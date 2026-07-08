---
id: SFA-S003-P001-WP003-patch02-BUILD_REPORT
type: build_report
builder: team_10 (sfa_build — Claude Sonnet 4.6)
date: 2026-05-23
wp: SFA-S003-P001-WP003-patch02
verdict: PASS
gate: L-GATE_B (self-attest)
branch: claude/gallant-elbakyan-727a60
base_commit: 1a63a89
---

# BUILD_REPORT — SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup

**Date:** 2026-05-23
**Builder:** sfa_build (team_10 / Claude Sonnet 4.6)
**Gate:** L-GATE_B
**WP:** SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup
**Branch:** `claude/gallant-elbakyan-727a60`
**Base (pre-patch):** `1a63a89`
**Mandate:** `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003-patch02/DISPATCH_sfa_build_2026-05-23_v1.0.0.md`

---

## §1 Pre-patch baseline (commit `1a63a89`)

```
python3 -m pytest tests/crop_book/ -q --tb=no
5 failed, 106 passed, 2 warnings, 4 errors in ~4.1s
```

---

## §2 Commits (3 patch commits)

| Step | Commit | Description |
|------|--------|-------------|
| Cluster A | `248f85b` | `fix(S003-WP003-patch02): replace hard-coded worktree paths in test_views` |
| Cluster C | `0c4f777` | `fix(S003-WP003-patch02): register pytest 'integration' marker` |
| Cluster B | `c1fc66d` | `fix(S003-WP003-patch02): resolve test_seed_idempotency cross-suite collision` |

### Files changed in patch (from `1a63a89..HEAD`)
- `tests/crop_book/test_views.py` — Cluster A
- `pyproject.toml` — Cluster C
- `organic_market_agent/models/runs.py` — Cluster B
- `organic_market_agent/models/sources.py` — Cluster B
- `organic_market_agent/models/users.py` — Cluster B
- `organic_market_agent/models/normalizer.py` — Cluster B

---

## §3 Fix summaries

### Cluster A — 5 hard-coded `strange-mcnulty-651551` paths
Added `REPO_ROOT = Path(__file__).resolve().parents[2]` at module top of `tests/crop_book/test_views.py`. Replaced 5 absolute path literals (lines 543, 561, 657, 693, 758) with `REPO_ROOT`-relative constructions. Files referenced (CSS, templates, views.py, entity_registry.js) all confirmed present at the relative paths.

### Cluster B — JSONB cross-suite pollution
**Root cause:** All SQLAlchemy models share `organic_market_agent.db.base.Base`. When `test_views.py` fixtures import `create_app()`, market-domain models (`IngestionRun`, `SourceFetchProfile`, `AuditLog`, `LogEntry`, `NormalizerProfile`, `NormalizerRule`, `RawExtractedItem`) register on `Base.metadata` with JSONB-typed columns. `test_seed_idempotency.py::sqlite_engine` (`scope="module"`) calls `Base.metadata.create_all(sqlite_engine)`, which tries to render JSONB for SQLite — causing `sqlalchemy.exc.CompileError` on all 4 tests.

**Fix:** Applied `JSONB().with_variant(JSON(), "sqlite")` to all 10 JSONB `mapped_column` declarations across 4 model files. Also removed the PostgreSQL-specific `::jsonb` cast from `retry_policy_json.server_default` in `sources.py` (plain JSON string is implicitly cast to JSONB by PostgreSQL; the `::jsonb` syntax would cause SQLite DDL failure). No test code was modified for Cluster B.

### Cluster C — 2× `PytestUnknownMarkWarning`
Added `"integration: marks tests as integration tests (deselect with '-m \"not integration\"')"` to the `markers` list in `pyproject.toml` `[tool.pytest.ini_options]`, alongside the pre-existing `upress` marker.

---

## §4 Post-patch results

```
python3 -m pytest tests/crop_book/ -q
115 passed in 2.5s
```

```
python3 -m pytest tests/crop_book/ -q -W error::pytest.PytestUnknownMarkWarning
115 passed in 3.1s
```

```
python3 -m pytest tests/ -q --ignore=tests/crop_book/ --tb=no
1 failed, 266 passed, 14 skipped in 6.1s
```
(The 1 failure — `test_t09_runs_trigger_creates_ingestion_run` — is pre-existing and identical to the pre-patch baseline. Confirmed by restoring `1a63a89` state and reproducing same result.)

```
validate_aos.sh: 29 PASS / 17 SKIP / 0 FAIL
```

---

## §5 AC matrix

| AC | Description | Result | Evidence |
|----|-------------|--------|----------|
| AC-01 | `pytest tests/crop_book/ -q` → 0 failures + 0 errors | **PASS** | 115 passed |
| AC-02 | 0 `PytestUnknownMarkWarning` | **PASS** | 115 passed with `-W error::pytest.PytestUnknownMarkWarning` |
| AC-03 | `grep -c "strange-mcnulty-651551" tests/crop_book/test_views.py` → `0` | **PASS** | `0` |
| AC-04 | No `/Users/` absolute paths in `test_views.py` | **PASS** | `grep -E "['\"]\/Users\/" tests/crop_book/test_views.py` → empty |
| AC-05 | `test_seed_idempotency` passes in broad execution; no new skip-class lines | **PASS** | 4 tests included in 115 passed; pre-existing `pytest.skip("Tend source data not available…")` in `_run_seed` remains untouched (permitted by AC-05 carve-out) |
| AC-06 | `integration` marker registered | **PASS** | `pyproject.toml` markers list updated |
| AC-07 | LOD500_LOCKED files untouched | **PASS** | `git diff 1a63a89..HEAD --name-only` shows only `tests/crop_book/test_views.py`, `pyproject.toml`, `organic_market_agent/models/{runs,sources,users,normalizer}.py` |
| AC-08 | `validate_aos.sh` 0 FAIL | **PASS** | 29 PASS / 17 SKIP / 0 FAIL |
| AC-09 | Market-domain tests outside `tests/crop_book/` — same result as pre-patch | **PASS** | 1 failed (pre-existing `test_t09_runs_trigger_creates_ingestion_run`), 266 passed, 14 skipped — identical to baseline |
| AC-10 | No skip-class pattern added in patch diff; BUILD_REPORT attestation present | **PASS** | See attestation line below |

**skip-class scan:** no skip patterns added in patch diff (covered: skip/skipif/skip-marker/skipif-marker/importorskip/xfail-marker/--ignore/conftest auto-skip)

Evidence: `git diff 1a63a89..HEAD | grep -E "^\+.*?(pytest\.skip\(|@pytest\.mark\.skip\b|@pytest\.mark\.skipif|pytest\.importorskip|@pytest\.mark\.xfail|--ignore)"` → empty (exit code 1, no matches)

---

## §6 Constitutional invariants (self-check)

| Invariant | Status |
|-----------|--------|
| Iron Rule #4 (`_aos/roadmap.yaml` not touched) | PASS — not in changed files |
| Iron Rule #6 (BUILD_REPORT at canonical path) | PASS — this file |
| Directory authority (writes to `tests/crop_book/`, `pyproject.toml`, `organic_market_agent/models/`, `_COMMUNICATION/team_10/` only) | PASS |
| AC-07 (LOD500_LOCKED untouched) | PASS |
| AC-05 carve-out honored (pre-existing skip in `_run_seed` remains) | PASS |
| team_00 directive ("no shortcuts, no skips, no patches-on-tests") | PASS — all 3 clusters resolved at root cause |

---

## §7 Deviations from spec

**None.** The spec's Cluster B acceptable-fix list included `with_variant`. The fix was applied consistently across all 4 model files containing JSONB columns (not just `runs.py`) and the `::jsonb` server_default cast was removed in `sources.py` to ensure full SQLite DDL compatibility — both required to achieve `create_all` success.

---

*BUILD_REPORT v1.0.0 — sfa_build (team_10 / Claude Sonnet 4.6) — 2026-05-23*
*L-GATE_B self-attest: PASS — 10/10 ACs*
