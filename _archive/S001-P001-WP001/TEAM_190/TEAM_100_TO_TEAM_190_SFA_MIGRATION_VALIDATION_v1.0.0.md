---
id: TEAM_100_TO_TEAM_190_SFA_MIGRATION_VALIDATION_v1.0.0
from: Team 100 (sfa_arch / Claude Code)
to: Team 190 (sfa_val / OpenAI)
date: "2026-04-12"
type: VALIDATION_MANDATE
domain: smallfarmsagents
wp_id: S001-P001-WP001
subject: "L-GATE_V Constitutional Validation — SmallFarmsAgents AOS Canonization"
---

# L-GATE_V Validation Mandate — S001-P001-WP001

## Context

SmallFarmsAgents has been migrated to full AOS L0 governance.
The `_aos/` directory has been created with all canonical files, lean-kit v3.1.3 snapshot
deployed, and the project registered in the AOS hub.

**Builder:** sfa_arch (claude-code) — Team 100
**Validator:** sfa_val (openai) — Team 190
**validate_aos.sh:** 12 PASS / 0 FAIL (confirmed by builder)

## What to Validate

### 1. Run validate_aos.sh independently

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Expected: 12 PASS / 0 FAIL.

### 2. Constitutional Checks

- [ ] Cross-engine rule: builder (cursor-composer) != validator (openai) — verify in `_aos/team_assignments.yaml`
- [ ] Physical lean-kit: `_aos/lean-kit/` is a directory (not symlink), contains `LEAN_KIT_VERSION.md`
- [ ] Single-writer roadmap: `_aos/roadmap.yaml` write authority is `sfa_arch` only
- [ ] L-GATE_V independence: `_aos/governance/team_190.md` asserts exclusive L-GATE_V ownership
- [ ] Repo-internal specs: all `spec_ref` paths in `_aos/roadmap.yaml` resolve within repo
- [ ] Profile consistency: `metadata.yaml`, `project_identity.yaml`, `roadmap.yaml` all say L0
- [ ] Boundary enforcement: `project_identity.yaml` forbidden_patterns include cross-project imports

### 3. Acceptance Criteria (from LOD400)

- AC-01: `_aos/` directory contains all 15 mandatory files
- AC-02: `_aos/lean-kit/` is physical copy (not symlink)
- AC-03: `team_assignments.yaml` defines cross-engine validation
- AC-04: `project_identity.yaml` has profile L0
- AC-05: `validate_aos.sh` exits 0 (12/12 PASS)
- AC-06: Hub `_aos/projects.yaml` has SFA `enabled: true`
- AC-07: Root `CLAUDE.md` exists and references PROJECT_CONTEXT.md
- AC-08: No absolute paths in spec_ref fields
- AC-09: agents-os CLAUDE.md updated (SFA constraint removed)

### 4. Files to Review

| File | Check |
|------|-------|
| `_aos/team_assignments.yaml` | 4 teams, cross-engine |
| `_aos/roadmap.yaml` | S001 WP, gate history |
| `_aos/project_identity.yaml` | L0, forbidden_patterns |
| `_aos/metadata.yaml` | lean-kit version |
| `_aos/governance/*.md` | 4 contracts |
| `_aos/context/*.md` | 3 activation + 1 PROJECT_CONTEXT |
| `CLAUDE.md` | Root context |

## Output

Write result to: `_COMMUNICATION/team_190/S001-P001-WP001/L-GATE_V_result.md`

Format: PASS or FAIL with AC-by-AC trace and constitutional check results.
