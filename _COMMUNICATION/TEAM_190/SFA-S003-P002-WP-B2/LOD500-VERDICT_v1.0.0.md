---
id: LOD500_VERDICT_SFA-S003-P002-WP-B2_v1.0.0
from: team_190
to: team_110
date: 2026-05-25
gate: L-GATE_V
wp: SFA-S003-P002-WP-B2
spec_version: v1.1.3
spec_lock_commit: d195b75
build_head_commit: b6ecb6e
engine: GPT-5.5
result: FAIL
blockers: 1
major: 0
minor: 1
---

# LOD500 Verdict v1.0.0 — SFA-S003-P002-WP-B2

## 1. Executive Verdict

**Result: FAIL.**

Most constitutional and implementation checks pass: migration 045 is present, `ni_importer.py` is append-only, locked publisher/views paths are clean, AC-03b proves the NI registry bypass, focused B2 tests pass, and `validate_aos.sh` returns 0 FAIL.

However, the build fails AC-13 / VV-13: `--ni-only` does not run only NI ingestion. The implementation runs JMF MasterClass and Tend processing before the NI-only return, and the seed.py diff contains two NI call-site blocks despite the spec/mandate requiring one call-site block.

## 2. Scope / Independence

- Engine constraint: **PASS** — GPT-5.5, non-Claude.
- Three-engine chain: **PASS** — team_110 Opus, team_10 Sonnet, team_190 GPT-5.5.
- Independence: **PASS** — BUILD_REPORT/DISPOSITION were not read before independent VV evaluation.
- Out-of-scope acknowledgment: commits `92584ef`, `f2c6e5c`, `38a7371` are hub-sync / `aos_sync_all.sh` propagation commits touching `_aos/governance/`, `_aos/lean-kit/`, and `_aos/last_gov_sync.yaml`; they are not counted as B2 build defects.

## 3. Evidence Summary

| Check | Result | Evidence |
|---|---:|---|
| Cross-engine commit range | PASS | Build commits authored by `WaldNimrod`; mandate identifies team_10 Sonnet builder and team_110 Opus orchestrator. |
| B2 build commits protected paths | PASS | 8 in-scope build commits showed no governance/lean-kit/project_identity paths. |
| LOD500_LOCKED paths | PASS | Locked code paths clean; only migration 045 appears under db versions. |
| `ni_importer.py` append-only | PASS | `65 insertions, 0 deletions`; diff appends `_upsert_knowledge_note` after `ni_registry = _NIRegistry()`. |
| AC-03b bypass proof | PASS | `NI_IMPORTER_CLASSES: 6`; B2 labels present; `registered: []`; `overlap: []`. |
| Publisher/views isolation | PASS | Diff clean; focused isolation tests passed. |
| Focused B2 tests | PASS | 18 focused tests passed. |
| Full crop_book suite | PASS_WITH_OUT_OF_SCOPE_FAILURE | `340 passed, 1 failed`; failing test is pre-existing `test_wp_upload_crop_book_profile`. |
| `validate_aos.sh` | PASS | `29 PASS / 19 SKIP / 0 FAIL`. |
| Roadmap parse | PASS | `SFA-S003-P002-WP-B2 BUILDING LOD400_LOCKED L-GATE_B`. |
| Migration 045 sequencing | PASS | `organic_market_agent/db/versions/045_crop_knowledge_notes.py` exists. |

## 4. Findings

### BLOCKER F-LV-B2-01 — `--ni-only` is not NI-only and seed.py exceeds the one-call-site scope

**Affected VVs:** VV-12, VV-13, VV-16  
**Affected ACs:** AC-13, AC-19  
**Files:** `organic_market_agent/crop_book/importer/seed.py`, tests gap in `tests/crop_book/test_seed_ni_cli.py`

The LOD400 and mandate require `seed.py` to add `--ni-only` / `--no-ni` plus **one** NI call-site block. AC-13 says `seed.py --ni-only --dry-run` populates only NI rows, with no JMF/Tend work.

Actual implementation has two NI ingestion blocks:

- One in the dry-run in-memory branch.
- One in the real `SessionFactory` branch.

More importantly, both branches place the NI-only return **after** prior importers. Running:

`python3 -m organic_market_agent.crop_book.importer.seed --all --ni-only --dry-run`

returned exit code 0 but executed JMF MasterClass and Tend processing before returning. Output included:

- `JMF MasterClass: ...`
- `Seeding crop_families...`
- `Parsed ... Tend...`
- many `[dry-run] Would process crop...` lines

That violates the user-visible meaning of `--ni-only` and the explicit AC-13 requirement to skip JMF/Tend. The tests only verify mutual exclusion/help/class labels; they do not assert that `--ni-only --dry-run` suppresses JMF/Tend.

Required remediation:

1. Move NI-only handling before JMF/Tend/Tend-overlay paths or otherwise ensure `--ni-only` executes NI ingestion only.
2. Remove duplicated NI call-site logic or factor it without adding forbidden seed.py resolver helpers.
3. Add a regression test that fails if `--ni-only --dry-run` runs JMF/Tend/Tend-overlay code.

### MINOR F-LV-B2-02 — BUILD_REPORT test-file inventory does not match actual file names

**Affected VV:** VV-17

BUILD_REPORT §3.3 lists names such as `test_ni_migration.py`, `test_ni_orm.py`, and `test_ni_seed_flags.py`, while the actual files include `test_migration_045.py`, `test_crop_knowledge_notes_orm.py`, and `test_seed_ni_cli.py`. The report still has the required sections and the test counts are directionally useful, so this is non-blocking but should be corrected with the remediation report.

## 5. VV Matrix

| VV | Status | Notes |
|---:|---|---|
| 1 | PASS | Three-engine chain confirmed by mandate and commit history. |
| 2 | PASS | `_aos/roadmap.yaml` clean in B2 build scope. |
| 3 | PASS | Independent VV evaluation formed before reading BUILD_REPORT. |
| 4 | PASS | BUILD_REPORT exists at canonical path. |
| 5 | PASS | 8 build commits did not touch governance/lean-kit/project_identity. |
| 6 | PASS | LOD500_LOCKED paths clean; migration 045 is the only db version change. |
| 7 | PASS | `ni_importer.py` append-only, +65/-0. |
| 8 | PASS | `NI_IMPORTER_CLASSES=6`; registry overlap empty. |
| 9 | PASS | Focused migration tests passed. |
| 10 | PASS | Note type CHECK covered by focused tests. |
| 11 | PASS | `_upsert_knowledge_note` hardcodes `is_internal_farm_use_only=True`. |
| 12 | FAIL | Engine reuse tests pass, but `--ni-only` flow runs earlier importers before NI. |
| 13 | FAIL | seed.py has two NI call-site blocks and `--ni-only` does not skip JMF/Tend. |
| 14 | PASS | Governance/lean-kit clean for B2 commits. |
| 15 | PASS | Publisher/views clean; isolation test passed. |
| 16 | FAIL | Full suite has only known out-of-scope publisher failure, but AC-13 behavior fails by direct command. |
| 17 | PASS_WITH_FINDING | BUILD_REPORT complete enough, but test-file names drift. |
| 18 | PASS | `validate_aos.sh` 0 FAIL. |
| 19 | PASS | Roadmap parse matches mandate expectation. |
| 20 | PASS | Migration 045 present; B3 sequencing unblocked. |

## 6. Tests / Commands Run

- `git log --format='%h %an %s' d195b75..b6ecb6e`
- Protected path and LOD500_LOCKED git diff audits
- `git diff --stat/--numstat d195b75..b6ecb6e -- organic_market_agent/crop_book/importer/ni_importer.py`
- AC-03b Python registry-bypass proof
- `pytest tests/crop_book/test_migration_045.py tests/crop_book/test_crop_knowledge_notes_orm.py tests/crop_book/test_ni_jmf_book.py tests/crop_book/test_ni_licensing_flag.py tests/crop_book/test_ni_publisher_isolation.py -q`
- `pytest tests/crop_book/ -q`
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
- `python3 -m organic_market_agent.crop_book.importer.seed --all --ni-only --dry-run`

## 7. Decision

Because there is 1 BLOCKER, WP-B2 does **not** pass L-GATE_V.

**Decision:** `FAIL` — route remediation through team_10.
