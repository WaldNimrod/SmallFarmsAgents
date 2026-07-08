---
id: SFA-S003-P001-WP003-patch02-LGATES-MANIFEST
type: BUNDLE_MANIFEST
gate: L-GATE_SPEC
round: 1
from: team_100
to: team_190
date: 2026-05-22
wp: SFA-S003-P001-WP003-patch02
---

# L-GATE_SPEC Bundle Manifest — SFA-S003-P001-WP003-patch02

**Submitter:** team_100 (Sonnet 4.6 declared / Opus 4.7 actual, smallfarmsagents spoke)
**Recipient:** team_190 (external constitutional validator — non-Claude per IR#1)
**Gate:** L-GATE_SPEC, Round 1
**WP:** SFA-S003-P001-WP003-patch02 — Test-Harness Cleanup
**Triggered by:** your own L-GATE_V finding F-190-WP004-LV-02 (LOW/PRE-EXISTING) + note N-190-WP004-LV-01 (INFO)
**team_00 directive (2026-05-22):** no shortcuts, no skips, no patches — fix at root cause; tests must PASS GREEN

---

## §1 What you are validating

A short patch LOD400 spec to clear pre-existing crop_book test-harness debt that surfaced under broad pytest invocation. The patch does NOT change production code. The constraint binding the spec is team_00's "no skip-patches" directive — every failing test must be resolved at root cause.

| File | Role |
|------|------|
| `_aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md` | **PRIMARY** — full LOD400 spec, 10 ACs, 5 build steps, ~2h SMALL effort |

---

## §2 Mandatory read order

1. `CLAUDE.md` — Iron Rules, directory authority, AOS spoke rules
2. `_aos/governance/team_190.md` — your governance contract
3. `_aos/roadmap.yaml` — confirm patch02 is registered (`status: ELIGIBLE`, gate `L-GATE_S`)
4. `_aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md` ← **PRIMARY**
5. `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` ← your prior verdict origin (§3 Note 2, §4 F-LV-02, N-LV-01) — informational, do not re-litigate
6. `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` §2 — the team_00 directive constraining this patch's "no skip-patches" semantics

**Reproducer for the debt** (run before issuing verdict):
```bash
cd /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60
python3 -m pytest tests/crop_book/ -q --tb=no
# Expected current state: 5 failed, 106 passed, 2 warnings, 4 errors
```

---

## §3 Constitutional Check Matrix (L-GATE_SPEC criteria)

team_100 self-attestation; team_190 verifies adversarially.

| # | Check | What to verify |
|---|-------|---------------|
| C1 | Directory authority | sfa_build writes only to `tests/crop_book/`, `pyproject.toml` (or `pytest.ini`), `conftest.py` if needed, `_COMMUNICATION/team_10/`. No `_aos/` writes. No application source changes. |
| C2 | Iron Rule #1 — cross-engine | Builder = Claude/Sonnet; validator = you (non-Claude). |
| C3 | Iron Rule #4 — single roadmap writer | This patch02 entry was authored by team_100 in roadmap.yaml (commit pending this session). sfa_build is explicitly forbidden from touching roadmap by AC + spec §5. |
| C4 | Iron Rule #7 — ADR034 | Test-only patch; no DB mutations. |
| C5 | Iron Rule #8 — port canon | No new listeners. |
| C6 | Scope isolation | Patch is bounded: 5 hard-coded paths + 1 marker registration + 1 cross-suite fixture pollution fix. LOD500_LOCKED files (WP002/003/004 deliverables) explicitly untouched (AC-07). |
| C7 | ACs are testable | Every AC has a concrete verification command (grep / pytest run / `validate_aos.sh`). |
| C8 | team_00 directive fidelity | Spec §3 / §4 / AC-05 / AC-10 explicitly forbid `pytest.skip`, `@pytest.mark.skipif`, `conftest.py auto-skip`, marker exclusion, or test removal. Verify the spec does not give the builder an escape hatch. |
| C9 | validate_aos.sh mandate | AC-08 requires 0 FAIL. |
| C10 | No half-finished implementations | All 3 clusters (A: paths, B: fixture pollution, C: marker registration) addressed; out-of-scope explicit in §3.4. |

Findings beyond C1–C10 are also in scope.

---

## §4 Risk register (from spec §7)

| ID | Severity | Risk | Mitigation in spec |
|----|----------|------|-------------------|
| R-patch02-01 | MEDIUM | Cluster B root cause requires invasive fix (shared conftest refactor) | Escalation to team_100 at L-GATE_B; AC-09 (market tests still pass) is the safety net. |
| R-patch02-02 | LOW | `pyproject.toml` missing in spoke; pytest config lives elsewhere | Builder checks for `pytest.ini`, `setup.cfg`, or creates `pyproject.toml`. |
| R-patch02-03 | LOW | Hard-coded path target file moved (not just worktree name) | Re-verify each path's target exists before commit. |

---

## §5 Verdict format

### §0 Verdict Box (mandatory in chat BEFORE artifact)

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP003-patch02   Gate: L-GATE_SPEC        ║
║  Round: 1                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

### Verdict artifact

Write to: `_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md`

Frontmatter:
```yaml
---
id: SFA-S003-P001-WP003-patch02-LOD400-VERDICT
type: L-GATE_SPEC verdict
validator: team_190
date: 2026-05-XX
wp: SFA-S003-P001-WP003-patch02
verdict: PASS | PASS_WITH_FINDINGS | BLOCKED
---
```

Body sections:
- §0 Summary (one paragraph)
- §1 Constitutional Checks C1–C10 (table)
- §2 Additional findings (beyond C1–C10)
- §3 Patch-specific findings (e.g. AC ambiguity, scope creep risk, root-cause confidence)
- §4 Recommendation (PASS / PASS_WITH_FINDINGS / BLOCKED + actionable reason)

### Commit

```bash
git add _COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP003-patch02/L-GATE_SPEC): {VERDICT} — Team 190"
```

---

## §6 Done criteria

1. §0 verdict box shown in chat
2. Verdict artifact at `_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md`
3. Artifact committed
4. Confirmation MSG to team_100 at `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP003-patch02-LOD400-VERDICT-2026-05-XX.md` delivered to `origin/main` via `msg_deliver_file`

---

## §7 Bundle file inventory

| File | Purpose |
|------|---------|
| `MANIFEST.md` | (this file) — bundle entry point + checklist + verdict format |
| `TEAM_190_ACTIVATION_PROMPT.md` | full governance + read order activation |
| `AOS_MAIL_PROMPT.md` | compact dispatchable activation (for sessions that prefer short prompts) |

Verdict landing zone (will be created post-verdict): `_COMMUNICATION/team_190/SFA-S003-P001-WP003-patch02/`

---

*Bundle prepared 2026-05-22 by team_100 (Sonnet 4.6 declared).*
*Branch: `claude/gallant-elbakyan-727a60` · Bundle commit: pending.*
