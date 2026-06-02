# Session 0 — v1.1.0 startup checklist (Team 10)

**Date:** 2026-03-30  
**Reference:** `HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` §4 Session 0, §8

| Step | Result |
|------|--------|
| Pull latest / working tree | Agent session on current workspace |
| `docker-compose up -d` / `docker compose up -d` | **Not running** at check time (`docker compose ps` showed no services). Nimrod: start `oma-g2-ev` (or project compose service) before Phase B ingestion. |
| `alembic current` | `071 (head)` — confirmed 2026-03-30 |
| Pending Team 20 migration reports | None found under `_COMMUNICATION/TEAM_20/reports/` |
| Team 100 approval responses | No blocker files reviewed |
| `CHANGELOG.md [Unreleased]` | Active; v1.1.0 entries present |
| LOD400 spec §0 corrections | Read as part of implementation |

**Next:** File migration 072 request (SRC_WA); proceed with code/docs deliverables; Phase B blocked on Docker + Team 20 confirmation per HANDOFF.
