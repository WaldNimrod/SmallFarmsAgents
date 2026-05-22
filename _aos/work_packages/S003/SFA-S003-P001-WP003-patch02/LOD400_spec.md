# LOD400 — SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup

**Date:** 2026-05-22
**Author:** team_100 (Claude Sonnet 4.6 declared / Opus 4.7 actual)
**WP:** SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup (post-S003 closure follow-up)
**Type:** LOD400_SPEC
**Status:** L-GATE_S ROUND_1 PASS_WITH_FINDINGS — addressed inline (no R2)
**R1 verdict:** team_190 PASS_WITH_FINDINGS 2026-05-23 (commit `5234ec0`, reviewed `394cf91`). Findings: F-190-patch02-01 LOW (AC-10 grep narrower than prose) ADDRESSED INLINE by widening AC-10 + AC-05 patterns + adding BUILD_REPORT attestation requirement (team_190 §4 explicit authorization: "Re-submit L-GATE_SPEC Round 2 only if team_100 amends AC-10; otherwise proceed directly to build"). F-190-patch02-02/03 INFO (Cluster B root cause + entity_registry.js stale-path clarification) — informational only, no spec change needed. Verdict: `_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md`
**Builder:** sfa_build (Team 10, Sonnet)
**Validator:** team_190 (external — L-GATE_SPEC + L-GATE_VALIDATE, non-Claude per IR#1)
**Depends on:** SFA-S003-P001-WP003 (LOD500_LOCKED) + SFA-S003-P001-WP004 (LOD500_LOCKED)
**Profile:** L0
**Effort:** SMALL
**Engine constraint:** sfa_build = Claude Sonnet (builder); team_190 = non-Claude (validator)
**Triggered by:** team_190 finding F-190-WP004-LV-02 (LOW/PRE-EXISTING) + N-190-WP004-LV-01 (INFO) at L-GATE_V verdict `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md`
**team_00 directive (2026-05-22):** "no shortcuts, no skips, no patches" — fix root causes; tests must pass GREEN.

**Reference documents:**
1. `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` (§3 Note 2 + §4 F-LV-02 + N-LV-01)
2. `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP003/LOD400_spec.md` (LOD500_LOCKED context — view-only)
3. `_archive/SFA-S003-P001/TEAM_10/SFA-S003-P001-WP003/BUILD_REPORT_v1.0.0.md` (WP003 build report — context)
4. This spec

---

## 1. Goal

Restore the WP003 + WP004 crop_book test suite to **100% green** under broad execution (single `pytest tests/crop_book/` invocation) by removing pre-existing test-harness debt. No production code changes. No new functional behavior. **No skips, no patches, no markers-of-convenience** — failures must be resolved at root cause per team_00 directive 2026-05-22.

After this patch, `python3 -m pytest tests/crop_book/ -q` reports **zero failures and zero errors** (collection AND execution), and `pytest` issues no `PytestUnknownMarkWarning`.

---

## 2. Pre-existing failure landscape (reproducer 2026-05-22)

Running `python3 -m pytest tests/crop_book/ -q --tb=no` on commit `8ca64e6` (archive tip) returns:

```
5 failed, 106 passed, 2 warnings, 4 errors in 3.67s
```

### 2.1 Cluster A — 5 hard-coded worktree paths in `tests/crop_book/test_views.py`

Failure pattern:

```
FileNotFoundError: [Errno 2] No such file or directory:
  '/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551/
   organic_market_agent/admin/static/crop_book/crop_book.css'
```

Each of 5 tests opens a CSS / JS / template file using an absolute path that hard-codes the historical worktree name `strange-mcnulty-651551`. That worktree was retired post-S003 Phase 1; the equivalent files now live in `gallant-elbakyan-727a60` (and in any future worktree by the same relative path).

Lines (in current `tests/crop_book/test_views.py`):

| Line | Test | File opened |
|------|------|-------------|
| 543 | `TestEntityTags::test_entity_tag_css_classes_in_css` | `…/admin/static/crop_book/crop_book.css` |
| 561 | `TestEntityTags::test_entity_macro_produces_correct_attrs` | template path |
| 657 | `TestRTLLayout::test_rtl_css_applied` | `…/crop_book.css` |
| 693 | `TestNoEditDelete::test_no_post_routes_in_blueprint` | views.py path |
| 758 | `TestViewHelpers::test_entity_registry_lookup` | `…/entity_registry.js` |

Files DO exist relative to the repo root in any worktree; the failure is purely the absolute-path constant.

### 2.2 Cluster B — 4 collection / fixture errors in `tests/crop_book/test_seed_idempotency.py`

Reproducer:
- Run **only** `pytest tests/crop_book/test_seed_idempotency.py` → 4 tests pass (in isolation).
- Run with the broader crop_book suite → 4 errors at fixture / collection time.

team_190's verdict (2026-05-13) and team_10's BUILD_REPORT D-02 attribute this to cross-suite pollution between `test_views.py` SQLite fixtures (which import market-domain models with JSONB columns) and the `test_seed_idempotency.py` SQLite session. The exact root cause needs builder investigation in this WP; the spec's AC requires the failures to be resolved at the source — **not** by skip-markers, conftest manipulation that selectively unloads, or `pytest --ignore`.

### 2.3 Cluster C — 2 unregistered `pytest.mark.integration` warnings

```
tests/crop_book/test_filter_parity.py:131  PytestUnknownMarkWarning: Unknown pytest.mark.integration
tests/crop_book/test_publisher.py:175      PytestUnknownMarkWarning: Unknown pytest.mark.integration
```

The marker is used but not declared. Fix: register `integration` in the canonical pytest config (`pyproject.toml` `[tool.pytest.ini_options]` markers list, OR `pytest.ini` markers section, OR `conftest.py` `pytest_configure`).

---

## 3. Implementation contract

### 3.1 Cluster A fix — Replace hard-coded worktree paths with relative-resolution

**Approach:** In `tests/crop_book/test_views.py`, replace every occurrence of the absolute string `"/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551"` with a worktree-agnostic root resolved via `pathlib.Path(__file__).resolve().parents[N]`, computed once at module top.

Suggested pattern (builder may adapt):

```python
from pathlib import Path

# Resolves to repo root regardless of worktree name.
REPO_ROOT = Path(__file__).resolve().parents[2]  # tests/crop_book/test_views.py → parents[2] = repo
```

Then construct each path via `REPO_ROOT / "organic_market_agent" / "admin" / "static" / "crop_book" / "crop_book.css"` etc.

### 3.2 Cluster B fix — Diagnose and resolve cross-suite pollution

The builder MUST:
1. Reproduce the failures by running the full crop_book suite (`pytest tests/crop_book/ -q`).
2. Identify which test or fixture pollutes the SQLite session for `test_seed_idempotency`.
3. Resolve at root cause. **Acceptable approaches** include:
   - Adding a proper fixture scope reset (e.g. `@pytest.fixture(scope="function", autouse=True)` to dispose the engine and recreate tables).
   - Refactoring the polluted import to avoid pulling JSONB-typed market models into the SQLite fixture path.
   - Using `with_variant(JSON, "sqlite")` or equivalent dialect-aware column declaration where the test fixture loads models.
4. **Unacceptable approaches**: `pytest.skip`, `@pytest.mark.skipif`, `pytest --ignore`, removing tests, marker-based exclusion, conftest.py that auto-skips, or any pattern that hides the failure without resolving it.

### 3.3 Cluster C fix — Register `integration` marker in canonical pytest config

Add to `pyproject.toml` (preferred, if it has a `[tool.pytest.ini_options]` section; create if absent):

```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
]
```

If `pyproject.toml` does not have a pytest config section AND `pytest.ini` exists, add to `pytest.ini` instead. If neither exists, prefer `pyproject.toml`.

### 3.4 Out of scope (NOT in this patch)

- Production code changes in `organic_market_agent/crop_book/`
- Changes to LOD500_LOCKED files from WP002, WP003, or WP004 (per AC-16 invariant from WP004 spec, still binding)
- New tests or new test coverage (this patch only restores existing tests)
- Refactoring of `test_views.py` test cases themselves (only the path constants change)
- Pytest version upgrade or test-tool dependency changes

---

## 4. Acceptance Criteria

| AC | Criterion | Evidence |
|----|-----------|----------|
| AC-01 | `python3 -m pytest tests/crop_book/ -q` returns 0 failures + 0 errors. | CI run + builder self-attestation |
| AC-02 | Same run reports 0 warnings of class `PytestUnknownMarkWarning`. | CI run |
| AC-03 | `tests/crop_book/test_views.py` contains **zero** occurrences of the literal string `strange-mcnulty-651551` (verified via `grep -c`). | `grep -c "strange-mcnulty-651551" tests/crop_book/test_views.py` → `0` |
| AC-04 | `tests/crop_book/test_views.py` contains **zero** absolute paths starting with `/Users/`. | `grep -E "['\"]\/Users\/" tests/crop_book/test_views.py` → no matches |
| AC-05 | `tests/crop_book/test_seed_idempotency.py` tests pass under broad execution (full crop_book suite); no skip-class pattern (`pytest.skip(...)`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `pytest.importorskip`, `@pytest.mark.xfail`, conftest auto-skip) added in or around this test file. **NOTE:** the pre-existing `pytest.skip("Tend source data not available…")` at the top of `_run_seed` is permitted to remain (it predates this patch — see team_190 R1 verdict §3 AC-05 row). Any NEW skip-class line in the patch diff is forbidden. | `git diff <base> HEAD -- tests/crop_book/test_seed_idempotency.py tests/crop_book/conftest.py \| grep -E "^\\+.*(pytest\.skip\|@pytest\.mark\.skip\|skipif\|importorskip\|xfail)"` → no `+` lines |
| AC-06 | The `integration` marker is registered in the canonical pytest config (`pyproject.toml` `[tool.pytest.ini_options].markers` OR `pytest.ini` `[pytest].markers`). | `python3 -c "import tomllib; ..."` OR `grep` on `pytest.ini` |
| AC-07 | LOD500_LOCKED files are untouched: `crop_book/models.py`, `crop_book/views.py`, `crop_book/templates/crop_book/{index,crop,_macros}.html`, migrations 035–040, `crop_book/publisher/` (all WP004 deliverables), `wordpress/mu-plugins/sfagent-crop-book-shortcode.php`. | `git diff <main-merge-base> HEAD -- <locked-file-list>` returns empty |
| AC-08 | `validate_aos.sh` returns 0 FAIL. | builder runs |
| AC-09 | Existing market-domain tests (`tests/test_upload_dispatch.py`, `tests/test_publisher.py`, anything outside `tests/crop_book/`) still pass. | `python3 -m pytest tests/ -q --ignore=tests/crop_book/` returns the same pre-patch result |
| AC-10 | No skip-class pattern was added anywhere in the patch's diff. Coverage MUST include: `pytest.skip(...)`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `pytest.importorskip`, `@pytest.mark.xfail`, `pytest --ignore` directives in config, and conftest auto-skip hooks (`pytest_collection_modifyitems` with skip injection). Builder BUILD_REPORT MUST include a self-attest line: "skip-class scan: no skip patterns added in patch diff (covered: skip/skipif/skip-marker/skipif-marker/importorskip/xfail-marker/--ignore/conftest auto-skip)". | `git diff <base> HEAD \| grep -E "pytest\.skip\\(\|@pytest\.mark\.skip\b\|@pytest\.mark\.skipif\|pytest\.importorskip\|@pytest\.mark\.xfail\|--ignore"` → no `+` lines. Plus BUILD_REPORT attestation line present and signed. |

---

## 5. Constitutional invariants

| Iron Rule | Application |
|-----------|-------------|
| #1 Cross-engine | sfa_build = Claude; team_190 = non-Claude. |
| #4 Single roadmap writer | team_100 (this commit set) updates `_aos/roadmap.yaml` with the new patch02 entry pre-build and the gate progression post-build. sfa_build does not touch `_aos/`. |
| #5 Final validation owned by team_190 | L-GATE_V binding. |
| #6 Artifact comms | BUILD_REPORT at `_COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md`. |
| #7 ADR034 | No DB mutations (this is test-only). |
| Directory authority (sfa_build) | Writes only to `tests/crop_book/`, `pyproject.toml` (or `pytest.ini`), `conftest.py` if needed, `_COMMUNICATION/team_10/`. NEVER `_aos/`. |
| AC-16 inheritance | LOD500_LOCKED files from WP002/WP003/WP004 remain untouched. |

---

## 6. Build sequence (5 ordered steps, total ~2h)

1. **Cluster A** — replace 5 hard-coded paths in `test_views.py` with `Path(__file__).resolve().parents[2]`-based resolution. Verify cluster A 5/5 PASS. Commit `fix(S003-WP003-patch02): replace hard-coded worktree paths in test_views`. (~30 min)
2. **Cluster C** — register `integration` marker in `pyproject.toml` (or `pytest.ini`). Verify warning suppression. Commit `fix(S003-WP003-patch02): register pytest 'integration' marker`. (~15 min)
3. **Cluster B reproduction** — run full crop_book suite, capture exact stack traces for the 4 errors. Investigate fixture order. (~20 min)
4. **Cluster B fix** — apply the chosen root-cause fix (likely a fixture-scope reset or dialect-aware variant declaration). Verify all 4 errors resolved. Commit `fix(S003-WP003-patch02): resolve test_seed_idempotency cross-suite collision`. (~30 min)
5. **Final sweep** — full `pytest tests/crop_book/ -q` + `tests/ -q --ignore=tests/crop_book/` + `validate_aos.sh`. All 10 ACs verified. BUILD_REPORT authored. Commit `gate(S003-WP003-patch02/L-GATE_B): builder self-attest PASS — 10/10 ACs`. (~15 min)

Total: ~110 min focused builder time. Effort tier: **SMALL**.

---

## 7. Risk register

| ID | Risk | Severity | Mitigation |
|----|------|----------|-----------|
| R-patch02-01 | Cluster B root cause turns out to be more complex than a fixture scope reset (e.g. requires refactoring a shared `conftest.py` that's also used by market tests). | MEDIUM | If the fix becomes invasive, escalate to team_100 at L-GATE_B — may require widening the patch scope under team_00 approval. AC-09 (existing market tests still pass) is the safety net. |
| R-patch02-02 | `pyproject.toml` does not exist in the spoke; pytest config lives elsewhere. | LOW | Builder checks for `pytest.ini`, `setup.cfg`, or creates `pyproject.toml` with minimum-needed `[tool.pytest.ini_options]` section. |
| R-patch02-03 | One of the hard-coded paths in `test_views.py` opens a file that has since been moved (not just the worktree name). | LOW | Re-verify each path's target exists at the relative location before committing the path-resolution refactor. |

---

## 8. Definition of Done (LOD500)

LOD400 → LOD500_LOCKED requires:
1. All 10 ACs PASS (sfa_build self-attestation).
2. team_190 L-GATE_V verdict = PASS (zero blocker / major findings; LOW findings only OK if non-blocking).
3. `pytest tests/crop_book/ -q` confirmed 0 failures + 0 errors + 0 warnings (PytestUnknownMarkWarning class).
4. `validate_aos.sh` = 0 FAIL.
5. roadmap.yaml updated by team_100 (single-writer rule).
6. BUILD_REPORT at `_COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md`.
7. team_00 directive 2026-05-22 honored: zero skip-patches added; zero failing tests deferred.

---

## 9. Cross-references

- F-LV-02 origin: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` §3 Note 2
- N-LV-01 origin: same verdict, §4
- team_00 directive recording: `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` §2 (same directive set instructs this patch)
- Closure obligation: after this patch's LOD500_LOCKED + GCR resolutions, team_100 will merge `claude/gallant-elbakyan-727a60` → `main` per F-LV-01 §2 "unified end-state" invariant.

---

*LOD400 spec v1.0.0 — authored 2026-05-22 by team_100.*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending.*
