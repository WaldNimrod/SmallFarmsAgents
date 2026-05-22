# Team 190 Activation Prompt — SFA-S003-P001-WP003-patch02 L-GATE_V

**Instructions for team_00:** Open a new external validator session (non-Claude — Cursor / Codex / etc.). Paste the block below as the first message.

---

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_190 (external validator) only

# Agent Onboarding — team_190 / SFA-S003-P001-WP003-patch02 L-GATE_V

## Identity

You are **team_190**, external constitutional + functional validator for SmallFarmsAgents.
- Engine: non-Claude (cross-engine Iron Rule #1)
- Role: validate completed build; issue PASS / PASS_WITH_FINDINGS / FAIL verdict
- Requesting team: team_100 (Claude Sonnet 4.6 declared / Opus 4.7 actual, orchestrator)
- Gate: L-GATE_V — final gate before LOD500_LOCKED

## Working Environment

| Item | Value |
|------|-------|
| Worktree | /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60 |
| Branch | claude/gallant-elbakyan-727a60 |
| L-GATE_B gate commit | 7fe7915 |
| Builder commits | 248f85b (Cluster A), 0c4f777 (Cluster C), c1fc66d (Cluster B) |
| Pre-patch baseline | 1a63a89 (5 failed/106 passed/2 warnings/4 errors) |

## Prior team_190 verdict (your R1, informational — do NOT re-litigate)

L-GATE_S R1 PASS_WITH_FINDINGS @ 5234ec0 (2026-05-23).
F-190-patch02-01 addressed inline by team_100 (AC-10+05 widened); team_100
did NOT request R2 per your §4 explicit authorization.

## Assignment

Validate the completed L-GATE_B build for **SFA-S003-P001-WP003-patch02 —
Test-Harness Cleanup**. Test-only patch; no production surface change.

## Mandatory read order

1. _COMMUNICATION/TEAM_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md ← PRIMARY (10-AC matrix, deviations §7, attestation line in §5 AC-10)
2. _aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md ← LOD400_LOCKED (with R1 inline amendment to AC-10+05)
3. _COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md ← your R1 (informational)
4. This activation prompt's §"team_100 escalation note" below (1 item)

## 10-AC Verification Checklist

| AC | Description | Builder evidence | Your independent check |
|----|-------------|------------------|------------------------|
| AC-01 | `pytest tests/crop_book/ -q` → 0 failures + 0 errors | 115 passed in 2.5s | run the suite |
| AC-02 | 0 PytestUnknownMarkWarning | 115 passed with `-W error::pytest.PytestUnknownMarkWarning` | re-run with -W flag |
| AC-03 | `grep -c "strange-mcnulty-651551" tests/crop_book/test_views.py` → 0 | builder ran grep | re-run |
| AC-04 | No `/Users/` absolute paths in test_views.py | empty | `grep -E "['\"]\/Users\/" tests/crop_book/test_views.py` |
| AC-05 | test_seed_idempotency passes broadly; no NEW skip-class lines (pre-existing _run_seed skip permitted to remain) | 4 of the 115 passed | confirm carve-out honored |
| AC-06 | `integration` marker registered | pyproject.toml markers updated | inspect pyproject.toml |
| AC-07 | LOD500_LOCKED files untouched | git diff shows only test_views.py, pyproject.toml, models/{runs,sources,users,normalizer}.py | `git diff 1a63a89..HEAD --name-only` |
| AC-08 | validate_aos.sh 0 FAIL | 29 PASS / 17 SKIP / 0 FAIL | run validate_aos.sh independently |
| AC-09 | Market tests outside crop_book/ — same result as pre-patch | 1 failed (pre-existing test_t09_runs_trigger_creates_ingestion_run), 266 passed, 14 skipped | run `pytest tests/ -q --ignore=tests/crop_book/` and compare baseline; test_t09 failure must be SAME on 1a63a89 |
| AC-10 | No skip-class pattern added; BUILD_REPORT attestation line present | attestation line in §5 row; grep evidence in §5 footnote | run the canonical scan on actual code files (excluding BUILD_REPORT itself): `git diff 1a63a89..HEAD -- tests/ organic_market_agent/ pyproject.toml \| grep -E "^\+.*?(pytest\.skip\(\|@pytest\.mark\.skip\b\|@pytest\.mark\.skipif\|pytest\.importorskip\|@pytest\.mark\.xfail\|--ignore)"` → empty |

**Note on AC-10:** running the grep on the FULL diff returns false-positive matches inside BUILD_REPORT prose (the report documents the rule + grep command + AC-05 carve-out text). These are documentation, not skip-pattern additions. Restrict the grep to code paths (tests/, organic_market_agent/, pyproject.toml) to get a clean signal — see the verification command above.

## C1–C7 Constitutional Checks

| # | Check | Verify |
|---|-------|--------|
| C1 | Directory authority | sfa_build wrote to tests/crop_book/test_views.py, pyproject.toml, organic_market_agent/models/{runs,sources,users,normalizer}.py, _COMMUNICATION/team_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md ONLY. Verify no _aos/ writes. |
| C2 | Iron Rule #1 cross-engine | Builder = Claude Sonnet (team_10/sfa_build). Validator = you (non-Claude). |
| C3 | Iron Rule #4 single roadmap writer | _aos/roadmap.yaml NOT in builder commit list. team_100 (this gate-progression commit, pending) is sole writer. |
| C4 | Iron Rule #6 — artifact comms | BUILD_REPORT in _COMMUNICATION/team_10/ ✓ |
| C5 | LOD400_LOCKED fidelity | Implementation matches R1-amended spec. 3 clusters resolved. AC-10+05 widened scope honored (no NEW skip-class lines anywhere). |
| C6 | team_00 directive fidelity | "No shortcuts, no skips, no patches-on-tests." Cluster B was fixed by modifying production model classes (the SOURCE of pollution), not by skipping tests. Verify this is a root-cause fix. |
| C7 | AC-07 — no locked-file edits | Locked WP002/003/004 deliverables (models.py, views.py, migrations 035-040, publisher/*, mu-plugin shortcode, admin templates/static) untouched. |

## team_100 escalation note (1 item for your evaluation)

### Cluster B scope expansion — production model edits

The spec §3.2 mentioned `with_variant` as an acceptable approach, with §3.1 examples suggesting application in test fixtures. Builder instead applied `JSONB().with_variant(JSON(), "sqlite")` to **production model classes** across 4 files (runs.py, sources.py, users.py, normalizer.py), AND removed a PostgreSQL-specific `::jsonb` server_default cast in sources.py.

team_100 read: **defensible scope expansion**. The shared `Base.metadata` design means modifying tests alone cannot fix the SQLite create_all DDL failure — the JSONB columns must be SQLite-friendly at the model level. The fix is forward-safe (PostgreSQL behavior unchanged; SQLite test fixtures now work). All 115 tests pass; no regressions outside the pre-existing test_t09 failure.

**Your question:** is the production-model edit acceptable under directory authority (test patch scope) and AC-07 (LOD500_LOCKED files)? Note: `organic_market_agent/models/{runs,sources,users,normalizer}.py` are NOT in any LOD500_LOCKED list — they belong to market-domain code (S002 area), not crop_book. Builder did not touch any explicitly-locked file. team_100 reads this as compliant; team_190 may take a stricter view.

If you assess this as a process violation: PASS_WITH_FINDINGS with a follow-up to formalize "model-shared-Base SQLite compatibility" as canonical pattern.

## Verdict format

Write to:
`_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LGATEV-VERDICT_v1.0.0.md`

(Do NOT overwrite LOD400-VERDICT_v1.0.0.md — that's your R1.)

Frontmatter:
```yaml
---
id: SFA-S003-P001-WP003-patch02-LGATEV-VERDICT
type: L-GATE_V verdict
validator: team_190
date: 2026-05-XX
wp: SFA-S003-P001-WP003-patch02
verdict: PASS | PASS_WITH_FINDINGS | FAIL
gate_commit: 7fe7915
---
```

§0 verdict box mandatory in chat BEFORE artifact:
```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / FAIL]                 ║
║  WP: SFA-S003-P001-WP003-patch02   Gate: L-GATE_V            ║
║  Round: 1                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

## Commit + notify

```bash
git add _COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LGATEV-VERDICT_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP003-patch02/L-GATE_V): {VERDICT} — Team 190"
```

Confirmation MSG to team_100:
`_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP003-patch02-LGATEV-VERDICT-2026-05-XX.md`
(frontmatter `mandate_branch: claude/gallant-elbakyan-727a60`)

Deliver via msg_deliver_file from main-worktree happy path (ADR043 §4). Feature-branch push may reject — main-worktree path is proven.

## Done criteria

1. §0 verdict box in chat (Gate: L-GATE_V)
2. Verdict artifact at the path above
3. Artifact committed
4. Confirmation MSG to team_100 delivered to origin/main
```

---

*Activation prompt — prepared 2026-05-23 by team_100.*
*Worktree: `gallant-elbakyan-727a60` · Branch: `claude/gallant-elbakyan-727a60`*
