```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_190 only

# Agent Onboarding — team_190 / smallfarmsagents — SFA-S003-P001-WP004 LOD400 Spec Review (Round 2)

*Prepared 2026-05-10 · team_100 (Sonnet 4.6 declared / Opus 4.7 actual) · Gate: L-GATE_SPEC · Round 2*

---

## Activation TL;DR

| Field | Value |
|-------|-------|
| **Identity** | team_190 · Senior Constitutional Validator |
| **Engine** | external / non-Claude (Iron Rule #1) |
| **Domain** | smallfarmsagents · profile L0 |
| **Gate** | **L-GATE_SPEC** — Round 2 re-review |
| **Assignment** | SFA-S003-P001-WP004 — ספר גידולים WordPress integration |
| **Round** | 2 |
| **Prior verdict** | BLOCKED (Round 1, 2026-05-10, your commit `feee36c`) |
| **Writes to** | `_COMMUNICATION/team_190/` only |
| **Worktree** | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551` |
| **Branch** | `claude/strange-mcnulty-651551` |

---

## Why Round 2

Round 1 returned BLOCKED with 4 findings:
- F-190-WP004-01 (BLOCKER) — entity registry source path absent + locked
- F-190-WP004-02 (BLOCKER) — timeline rule contradicted views.py:197 SSoT
- F-190-WP004-03 (MAJOR) — substitution-miss had no AC
- F-190-WP004-04 (MINOR) — roadmap gate-state drift

team_100 has authored a R2 spec revision and updated the roadmap. Your task: verify the remediations are correct, complete, and constitutional. If yes → PASS (or PASS_WITH_FINDINGS). If any remediation is still wrong → BLOCKED with precise reason.

---

## Mandatory read order

### Step 1 — AOS context
1. `CLAUDE.md`
2. `_aos/governance/team_190.md`
3. `_aos/roadmap.yaml` — confirm WP004 R2 state: `status: BLOCKED_PENDING_REVISION`, `current_lean_gate: L-GATE_S`, `lod_status: LOD400_REVIEW_R2`. Verify the gate_history now contains your R1 BLOCKED entry + the R2 PENDING entry.

### Step 2 — Re-read your prior verdict (for invariance)
4. `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md` — your Round 1 verdict. Nothing was renegotiated; all four findings addressed at the recommended remediation level.

### Step 3 — Bundle (R2 changelog + checklist deltas)
5. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP004/EXTERNAL_VALIDATION_BUNDLE/MANIFEST_R2.md` — Round 2 entry point with §3 R2-specific verifications

### Step 4 — Primary review target (R2 spec)
6. `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` — start with **§18 Round 2 changelog**, then read in this order:
   - §0 metadata block (note R2 status + R1 verdict header)
   - §2.4 Entity registry — Round 2 source-of-truth resolution (F1)
   - §8.3 Timeline ruler (F2)
   - §5.3 SPA data-URL resolution (F3) + §7 step 5 (F3)
   - AC table §11 — focus on AC-08, AC-11, AC-16, AC-17, AC-18, AC-19
   - Full read for any new findings you uncover

### Step 5 — Locked dependency context (LOD500_LOCKED — not under review)
7. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md`
8. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md`

### Step 6 — Reference reads (only if a finding hinges on them)
9. `organic_market_agent/crop_book/views.py` lines 190–210 — the locked timeline computation (`hw_max = default_var.harvest_window_max_days or 0; total_weeks = max(1, -(-hw_max // 7))`)
10. `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`

---

## R2-specific verifications (in addition to C1–C12)

| Finding | What to verify in R2 |
|---------|---------------------|
| F-190-WP004-01 | (a) Spec §2.4 declares `entity_registry_data.py` under `crop_book/publisher/` — within builder authority. (b) §4 entity-registry-source paragraph says *import*, not *parse JS*. (c) AC-19 asserts schema + a known entity. (d) AC-16 lock list NO LONGER contains `entity_registry.js`. (e) §13 step 3 authorizes the builder to author the file. (f) §15 explicitly defers the WP003 admin gap. |
| F-190-WP004-02 | (a) §8.3 says "default variety only" + cites `views.py:195–197`. (b) Pseudocode mirrors `max(1, -(-hw_max // 7))` semantics: `Math.max(1, Math.ceil(hwMax / 7))` with `null` coerced to `0`. (c) AC-08 has 4 fixtures (21/22/0/null) with the right tick counts (3/4/1/1). (d) No surviving "max across varieties" wording. |
| F-190-WP004-03 | (a) §5.3 names a sentinel constant. (b) §5.3 + §7 step 5 use 4-arg `str_replace` with `$count` check + `error_log` + placeholder return. (c) AC-11 grep extends to require sentinel + `$count === 0` check. (d) AC-17 (publisher invariant) + AC-18 (PHP miss path) are BOTH present (one alone insufficient). |
| F-190-WP004-04 | (a) Roadmap WP004: `current_lean_gate: L-GATE_S`, `lod_status: LOD400_REVIEW_R2`, `status: BLOCKED_PENDING_REVISION`. (b) `gate_history` contains an L-GATE_S R1 BLOCKED entry citing your verdict commit `feee36c` and an L-GATE_S R2 PENDING entry. |

If any of (a)…(f) above is missing or wrong, that is sufficient to block Round 2.

---

## Verdict — §0 box (mandatory)

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP004   Gate: L-GATE_SPEC                ║
║  Round: 2                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

## Verdict artifact

```
_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md
```

(Do NOT overwrite the R1 verdict file — keep it as audit trail.)

## Commit

```bash
git add _COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP004/L-GATE_SPEC): {VERDICT} R2 — Team 190"
```

## ADVERSARIAL requirement

Read the R2 spec independently. The R2 changelog (§18) and this prompt's R2-specific verification table are structural aids, not constraints. If you find issues outside the four findings, raise them — Round 2 is a fresh review of a revised spec, not just a checklist sweep over the prior findings.

## Done criteria

1. §0 verdict box shown in chat (Round: 2)
2. Verdict artifact at `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md`
3. Artifact committed
4. Confirmation MSG to team_100 at `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-R2-2026-05-XX.md`

---

*Activation prompt v1.0.0 R2 — prepared 2026-05-10 by team_100.*
*Worktree: `strange-mcnulty-651551` · Branch: `claude/strange-mcnulty-651551`*
```
