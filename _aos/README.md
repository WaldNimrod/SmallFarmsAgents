# _aos/ — AOS Governance Layer

This directory is the **AOS governance container** for the SmallFarmsAgents project.

It enables this project to function as a canonical **L0 spoke project** in the AOS framework,
independently of hub access (Iron Rule #8).

## Contents

| File / Dir | Purpose |
|------------|---------|
| `metadata.yaml` | Lean-kit version + profile (L0) |
| `project_identity.yaml` | Project boundaries + forbidden patterns |
| `definition.yaml` | Team definitions snapshot from hub |
| `team_assignments.yaml` | Who executes, which engine (cross-engine enforced) |
| `roadmap.yaml` | WP state registry — SSoT for WHAT/WHEN |
| `MILESTONE_MAP.md` | Milestone descriptions |
| `governance/` | Per-team operational contracts |
| `context/` | Agent activation files (startup reads) |
| `work_packages/` | LOD spec chain per WP |
| `lean-kit/` | Physical methodology snapshot v3.1.3 (NEVER symlink) |

## Key Iron Rules

1. **Cross-engine validation** — builder engine != validator engine (cursor-composer != openai)
2. **Physical lean-kit** — `lean-kit/` is always a physical copy, never a symlink
3. **Repo-internal specs** — `spec_ref` paths never leave the repository
4. **Single-writer roadmap** — one agent holds write authority at a time
5. **L-GATE_V independence** — always sfa_val (openai), immutable

## Validation

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Exit 0 = all checks pass.

## Profile

**L0 — Lean/Manual.** No engine infrastructure. Governance-only.
Manual orchestration by Team 00 (Nimrod).
