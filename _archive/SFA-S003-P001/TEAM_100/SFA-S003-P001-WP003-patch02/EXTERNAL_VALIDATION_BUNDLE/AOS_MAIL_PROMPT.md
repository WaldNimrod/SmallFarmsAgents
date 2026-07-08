# Agent Onboarding — team_190 / smallfarmsagents — SFA-S003-P001-WP003-patch02 LOD400 Spec Review

*Dispatched 2026-05-22 · team_100 → team_190 · Gate: L-GATE_SPEC · Round 1*

## Activation TL;DR

| Field | Value |
|-------|-------|
| **Identity** | team_190 · Senior Constitutional Validator |
| **Engine** | external / non-Claude (Iron Rule #1) |
| **Domain** | smallfarmsagents · profile L0 |
| **Gate** | L-GATE_SPEC, Round 1 |
| **WP** | SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup |
| **Worktree** | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60` |
| **Branch** | `claude/gallant-elbakyan-727a60` |

## Context

This is a SMALL follow-up patch to S003 closure. The patch fixes pre-existing
test-harness debt (5 hard-coded worktree paths + 1 cross-suite fixture pollution
+ 1 unregistered pytest marker) flagged in YOUR own L-GATE_V verdict on WP004
(F-190-WP004-LV-02 + N-190-WP004-LV-01).

**Binding constraint from team_00 directive (2026-05-22):**
No shortcuts. No skips. No patches-on-tests. Every failing test must be resolved
at root cause. The spec's AC-05 and AC-10 codify this — verify they leave no
escape hatch.

## Assignment

Review the LOD400 spec:
`_aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md`

Apply the 10 constitutional checks from `MANIFEST.md §3` (C1–C10). Findings
beyond C1–C10 are in scope.

## Reproducer (run before issuing verdict)

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60
python3 -m pytest tests/crop_book/ -q --tb=no
# Current state: 5 failed, 106 passed, 2 warnings, 4 errors
```

## Verdict destination

`_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md`

§0 verdict box mandatory in chat BEFORE artifact write. Commit message:
`validate(SFA-S003-P001-WP003-patch02/L-GATE_SPEC): {VERDICT} — Team 190`

---

*Activation prompt v1.0.0 — prepared 2026-05-22 by team_100.*
