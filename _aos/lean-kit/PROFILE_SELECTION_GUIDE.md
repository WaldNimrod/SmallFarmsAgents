# AOS Profile Selection Guide
# Version: 1.0.0 | Updated: 2026-04-11

---

## Which profile should this WP use?

**Profile is declared in LOD100 by Team 00 at WP creation. It is immutable once set.**

---

## Quick decision

```
Is this WP bounded (1 team, well-understood pattern, low risk)?
  → L2 (or L0 if no engine needed)

Does this WP have any of these?
  - ≥2 teams with integration contracts between them
  - New state machine with ≥5 states
  - MEDIUM or HIGH implementation risk
  - New data model or API surface
  - Team 00 wants explicit LOD300 before implementation starts
  → L2.5
```

---

## Comparison table

| Aspect | L0 | L2 | L2.5 |
|--------|----|----|------|
| **Best for** | Minimal governance, no engine | Standard projects with engine | Complex WPs, ≥2 teams, integration contracts |
| **LOD track** | Track A or B (optional) | Track A or B (optional) | Always Track B |
| **Research rounds** | Not required | Not required | R1/R2/R3 mandatory before each LOD step |
| **LOD300 required?** | Optional | Optional | Always |
| **Human gates** | 0 (automated) | 0 (automated) | 2 mandatory (Team 00 only, non-delegatable) |
| **Cross-engine validation** | Optional | Optional | Mandatory at every LOD step |
| **Engine required?** | No | Yes | Yes (extends L2) |
| **Gate sequence** | L-GATE_E/S/B/V | L-GATE_E/S/B/V | L25-PH1 through L25-PH6 (11 sub-phases) |
| **Mockup** | Optional | Optional | Mandatory (produced in PH2B) |
| **FCP protocol** | Not defined | Not defined | FCP-1/2/3/4 + circuit breaker |
| **Canonicalized** | v3.1.1 | v3.1.1 | v3.1.3 (2026-04-11) |

---

## L0 — Lean / Manual

**Use when:**
- Project needs AOS governance structure without an automation engine
- Single person or single team, stable well-understood patterns
- No CI/CD, no dashboard, no API backend required
- Governance-only: roadmap.yaml + team contracts + LOD documents

**Examples:** AOS-Sandbox-Lean (proof-of-concept governance only)

**How to activate:**
1. Copy lean-kit snapshot to project `_aos/lean-kit/`
2. Create `_aos/roadmap.yaml` from template
3. Use LOD100 → LOD400 cycle manually (Track A: skip LOD300)
4. No orchestrator needed — Team 00 manages directly

**Profile file:** `lean-kit/profiles/L0.yaml`

---

## L2 — AOS v3 / Dashboard

**Use when:**
- Full governance with automated engine integration
- Dashboard observability desired
- Moderate complexity WPs (1-2 teams, understood patterns)
- Track A viable (LOD300 optional)

**Examples:** TikTrack, AOS-Sandbox-Full

**How to activate:**
1. Copy lean-kit snapshot
2. Deploy `core/` engine (FastAPI + DB)
3. Seed via `core/seed.py`
4. WPs flow through L-GATE_E → L-GATE_S → L-GATE_B → L-GATE_V
5. Agents activated manually per gate

**Profile file:** `lean-kit/profiles/L2.yaml`

---

## L2.5 — Managed Agent Pipeline

**Use when:**
- WP touches ≥2 teams with integration contracts
- State machine has ≥5 states (LOD300 non-trivial)
- Implementation risk is MEDIUM or HIGH
- New data model or API surface being introduced
- Team 00 wants explicit LOD300 before any implementation begins

**Examples:** `SBXF-P001-WP-L25-001` (canary, 2026-04-11, COMPLETE)

**How to activate (as Orchestrator):**

Step 1 — Read in order:
```
1. core/operator_dna.yaml
2. core/definition.yaml
3. lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md
4. {project}/_aos/work_packages/{WP-ID}/LOD100_{WP-ID}.md
```

Step 2 — Paste this activation block to Claude Code:
```
You are the L2.5 Pipeline Orchestrator (Team 100).
Read: lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md
Then validate LOD100 at: {path/to/LOD100}.md
Profile: L2.5. WP-ID: {WP-ID}. Project: {project-id}.
Start Phase 1.
```

**Profile file:** `lean-kit/profiles/L2.5.yaml`
**Execution guide:** `lean-kit/modules/managed-pipeline/L25_QUICK_REFERENCE.md`
**Full runbook:** `lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md`

---

## L3 — CLI-Driven (Future)

Not yet built. Target: L2.5 with both human gates automated via quality thresholds.
- Phase 3 gate → automated LOD300 quality check
- Phase 5 gate → automated AC coverage verification

L2.5 is the training ground for L3: every run produces quality data toward L3 trust thresholds.

**Profile file:** `lean-kit/profiles/L3.yaml` (stub only)

---

## LOD100 profile declaration

When writing a LOD100, declare the profile explicitly:

```markdown
---
wp_id: {PROJECT}-P{N}-WP-{N}
profile: L0 | L2 | L2.5          ← required for L2.5
operator_dna_version: "0.1.0"    ← required for L2.5 only
...
---
```

Profile is **immutable** once set. If complexity changes mid-WP, create a new LOD100.

---

## Files index

| What | Where |
|------|-------|
| L0 profile | `lean-kit/profiles/L0.yaml` |
| L2 profile | `lean-kit/profiles/L2.yaml` |
| L2.5 profile | `lean-kit/profiles/L2.5.yaml` |
| L2.5 quick reference | `lean-kit/modules/managed-pipeline/L25_QUICK_REFERENCE.md` |
| L2.5 orchestrator runbook | `lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md` |
| L2.5 LOD100 form | `lean-kit/modules/managed-pipeline/artifacts/LOD100_L25_FORM.md` |
| Getting started (L0/L2) | `lean-kit/modules/project-governance/GETTING_STARTED.md` |
| Module index | `lean-kit/MODULE_INDEX.md` |
