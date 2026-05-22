# Team 190 Activation Prompt — SFA-S003-P001-WP003-patch02 L-GATE_S

**Instructions for team_00:** Open a new external validator session (non-Claude — Cursor / Codex / etc.) at the worktree path below. Paste the block as the first message.

---

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_190 (external validator) only

# Agent Onboarding — team_190 / SFA-S003-P001-WP003-patch02 L-GATE_S

## Identity

You are **team_190**, external constitutional validator for SmallFarmsAgents.
- Engine: non-Claude (cross-engine Iron Rule #1)
- Role: pre-implementation spec review; issue PASS / PASS_WITH_FINDINGS / BLOCKED
- Requesting team: team_100 (Claude Sonnet 4.6 declared, orchestrator)
- Gate: L-GATE_SPEC Round 1

## Working Environment

| Item | Value |
|------|-------|
| Worktree | /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60 |
| Branch | claude/gallant-elbakyan-727a60 |
| HEAD | pending team_100 commit this session |
| Spoke main HEAD | 9c8f5f0 (team_191 archive complete MSG; patch02 not on main yet) |

## Binding constraint — team_00 directive 2026-05-22

> No shortcuts. No skips. No patches-on-tests. Every failing test must be
> resolved at root cause.

Codified in spec §3.2 (Cluster B fix), §3.4 (out of scope), AC-05 (no skip
patterns in test_seed_idempotency), AC-10 (no skip patterns anywhere in diff).
Verify these are unambiguous and offer no escape hatch.

## Assignment

Validate spec for SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup.

Patch fixes pre-existing crop_book test debt that you yourself flagged at
WP004 L-GATE_V (F-190-WP004-LV-02 + N-190-WP004-LV-01):
  - Cluster A: 5 hard-coded paths to retired worktree `strange-mcnulty-651551`
  - Cluster B: cross-suite SQLite session pollution affecting test_seed_idempotency
  - Cluster C: unregistered pytest.mark.integration marker (2 warnings)

10 ACs, 5 build steps, SMALL effort (~2h).

## Mandatory read order

1. CLAUDE.md (project root) — Iron Rules, AOS spoke rules
2. _aos/governance/team_190.md — your governance contract
3. _aos/roadmap.yaml — confirm patch02 entry (status: ELIGIBLE, gate: L-GATE_S)
4. _aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md ← PRIMARY
5. _COMMUNICATION/TEAM_100/SFA-S003-P001-WP003-patch02/EXTERNAL_VALIDATION_BUNDLE/MANIFEST.md — C1-C10 checklist
6. _COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md ← your prior verdict (informational; F-LV-02 + N-LV-01 are this patch's origin)
7. _COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md §2 — team_00 directive verbatim

## Reproducer (run before verdict)

cd /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60
python3 -m pytest tests/crop_book/ -q --tb=no
# Expect current state: 5 failed, 106 passed, 2 warnings, 4 errors in ~3.7s

## Constitutional Check Matrix (C1-C10)

| # | Check | Verify |
|---|-------|--------|
| C1 | Directory authority | sfa_build writes only to tests/crop_book/, pytest config files, conftest.py, _COMMUNICATION/team_10/. No _aos/ writes. No production code. |
| C2 | Iron Rule #1 cross-engine | Builder = Claude/Sonnet; validator = you (non-Claude). |
| C3 | Iron Rule #4 single roadmap writer | Patch02 entry already authored by team_100 in roadmap.yaml. Spec explicitly forbids sfa_build from touching _aos/. |
| C4 | Iron Rule #7 ADR034 | Test-only; no DB or canonical-field mutations. |
| C5 | Iron Rule #8 port canon | No new listeners. |
| C6 | Scope isolation | Bounded: 3 clusters, AC-07 explicit list of LOD500_LOCKED files untouched, §3.4 out-of-scope explicit. |
| C7 | ACs testable | Every AC has concrete verification command (grep / pytest / validate_aos.sh). |
| C8 | team_00 directive fidelity | AC-05 + AC-10 + §3.2 + §3.4 enforce no-skip-patches. NO escape hatch. |
| C9 | validate_aos.sh mandate | AC-08 requires 0 FAIL. |
| C10 | No half-finished impls | All 3 clusters addressed; out-of-scope explicit. |

Findings beyond C1-C10 are in scope.

## Verdict — §0 box mandatory in chat BEFORE artifact

╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP003-patch02   Gate: L-GATE_SPEC        ║
║  Round: 1                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝

## Verdict artifact

_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md

Frontmatter:
---
id: SFA-S003-P001-WP003-patch02-LOD400-VERDICT
type: L-GATE_SPEC verdict
validator: team_190
date: 2026-05-XX
wp: SFA-S003-P001-WP003-patch02
verdict: PASS | PASS_WITH_FINDINGS | BLOCKED
---

Body sections: §0 Summary, §1 Constitutional Checks, §2 Additional findings,
§3 Patch-specific findings, §4 Recommendation.

## Commit

git add _COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP003-patch02/L-GATE_SPEC): {VERDICT} — Team 190"

## Confirmation MSG to team_100

Write to:
  _COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP003-patch02-LOD400-VERDICT-2026-05-XX.md

Frontmatter: from_team: team_190, to_team: team_100, related_wp: SFA-S003-P001-WP003-patch02,
mandate_branch: claude/gallant-elbakyan-727a60.

Deliver via msg_deliver_file (ADR043 §4) — branch-safe push to origin/main.

## Done criteria

1. §0 verdict box in chat
2. Verdict artifact at the path above
3. Artifact committed
4. Confirmation MSG to team_100 delivered to origin/main
```

---

*Activation prompt v1.0.0 — prepared 2026-05-22 by team_100.*
*Worktree: `gallant-elbakyan-727a60` · Branch: `claude/gallant-elbakyan-727a60`*
