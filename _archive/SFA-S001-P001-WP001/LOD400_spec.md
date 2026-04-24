# LOD400 — S001-P001-WP001: _aos/ Foundation

## Overview

| Field | Value |
|-------|-------|
| WP ID | S001-P001-WP001 |
| Milestone | S001 — AOS Canonization |
| Builder | sfa_arch (claude-code) |
| Validator | sfa_val (openai) |
| Profile | L0 |
| Risk | LOW |

## Scope

Create the complete `_aos/` governance directory for SmallFarmsAgents, including all mandatory
files per ARCHITECT_DIRECTIVE_AOS_IN_REPO_STANDARD_v1.0.0. Copy lean-kit v3.1.3 as physical
snapshot. Register project in AOS hub. Create root CLAUDE.md.

## Deliverables

1. `_aos/project_identity.yaml` — update from standalone to L0
2. `_aos/metadata.yaml` — lean-kit provenance
3. `_aos/README.md` — governance directory README
4. `_aos/definition.yaml` — hub team definition snapshot
5. `_aos/team_assignments.yaml` — 4-team L0 model (sfa_sd/arch/build/val)
6. `_aos/roadmap.yaml` — project-owned WP registry
7. `_aos/MILESTONE_MAP.md` — milestone history
8. `_aos/context/PROJECT_CONTEXT.md` — project overview
9. `_aos/context/ACTIVATION_ARCH.md` — architecture agent activation
10. `_aos/context/ACTIVATION_BUILDER.md` — builder agent activation
11. `_aos/context/ACTIVATION_VALIDATOR.md` — validator agent activation
12. `_aos/governance/team_00.md` — system designer contract
13. `_aos/governance/team_100.md` — architecture agent contract
14. `_aos/governance/team_110.md` — builder agent contract
15. `_aos/governance/team_190.md` — validator agent contract
16. `_aos/lean-kit/` — physical copy of agents-os/lean-kit/ v3.1.3
17. `CLAUDE.md` — root context file for Claude Code sessions
18. Hub registration: `_aos/projects.yaml` entry enabled + `projects/smallfarmsagents.yaml` updated

## Acceptance Criteria

- AC-01: `_aos/` directory contains all 15 files listed above
- AC-02: `_aos/lean-kit/` is a physical copy (not a symlink) of agents-os/lean-kit/
- AC-03: `_aos/team_assignments.yaml` defines cross-engine validation (builder != validator)
- AC-04: `_aos/project_identity.yaml` has profile L0 (not standalone)
- AC-05: `validate_aos.sh` exits 0 with all 12 checks PASS
- AC-06: Hub `_aos/projects.yaml` entry has `enabled: true`
- AC-07: Root `CLAUDE.md` exists and references `_aos/context/PROJECT_CONTEXT.md`
- AC-08: No absolute paths in any spec_ref field
- AC-09: agents-os CLAUDE.md no longer says "NOT an AOS-managed project" for SFA

## Exit Criterion

`validate_aos.sh` exits 0 + Team 190 L-GATE_V PASS.
