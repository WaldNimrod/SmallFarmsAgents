---
id: HANDOFF-SFA-V320-2026-04-16
from: Team 100
to: sfa_arch / Nimrod
date: 2026-04-16
type: handoff
---

# SmallFarmsAgents — V320 narrative sync

## Done

- `_aos/context/PROJECT_CONTEXT.md`, `ACTIVATION_ARCH.md`, `CLAUDE.md` — L0 **file-first** clarification + **ADR034** if/when AOS v3 DB is shared; `validate_aos` expectations.
- `AGENTS.md`, `.cursorrules` — short AOS / ADR034 pointers.
- `_aos/metadata.yaml` — provenance **c546ed4** / 2026-04-16 (aligned to hub snapshot).
- `_aos/lean-kit/.../GETTING_STARTED.md` — roadmap + validation expectation lines.
- Archive: `_aos/context/_ARCHIVE_PRE_V320_NARRATIVE_SYNC_2026-04-16.md`

## Follow-up

1. If `.cursor/rules/project-context.mdc` duplicates old “roadmap SSoT only” wording, update it to match `PROJECT_CONTEXT.md`.
2. Run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
