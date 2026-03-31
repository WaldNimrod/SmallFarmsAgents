# OrganicMarketAgent — Documentation Hub

**Single entry point** for humans and AI agents working on this repository.  
All files under `documentation/` are **English only** (project language policy).  
**Canonical terminology:** [`docs/GLOSSARY.md`](../docs/GLOSSARY.md) (read first).

---

## Quick map

| Area | Path | Purpose |
|------|------|---------|
| Overview & scope | [`01-overview/`](01-overview/) | What the system is, milestones, boundaries |
| Architecture | [`02-architecture/`](02-architecture/) | Modules, boundaries, key code locations |
| Data & schema | [`03-data-and-schema/`](03-data-and-schema/) | PostgreSQL, Alembic, ORM models, important tables |
| Pipelines & runtime | [`04-pipelines-and-runtime/`](04-pipelines-and-runtime/) | Collect → parse → normalize → aggregate → publish |
| Admin & operations | [`05-admin-and-operations/`](05-admin-and-operations/) | Local Flask admin, maintenance, alerts, env |
| Scripts & CLI | [`06-scripts-and-cli/`](06-scripts-and-cli/) | Shell scripts and `python -m organic_market_agent` |
| Testing | [`07-testing/`](07-testing/) | Pytest layout and commands |
| Troubleshooting | [`08-troubleshooting/`](08-troubleshooting/) | Debugging, alert tags, DB sanity checks |
| **Archive** | [`archive/`](archive/) | **Completed** time-bound specs and handoff notes |
| External references | [`external-references/`](external-references/) | Where `docs/`, `_COMMUNICATION/`, and legacy specs live |

---

## For AI agents (continuation / incident response)

1. Read [`docs/GLOSSARY.md`](../docs/GLOSSARY.md).
2. Open the section above that matches the task (schema change → `03`, pipeline bug → `04`, etc.).
3. **Read the relevant spec document** before making any change (see categorized table in `project-context.mdc` or team onboarding files).
4. Prefer **code** under `organic_market_agent/` as source of truth; this tree summarizes and links.
5. **Log every code change** in [`CHANGELOG.md`](../CHANGELOG.md) under `[Unreleased]` before the session ends.
4. For team process and gates, see [`external-references/`](external-references/) → `_COMMUNICATION/ROADMAP.md`.
5. When a temporary spec or work package is **finished**, move or copy it into [`archive/`](archive/) per [`archive/README.md`](archive/README.md).

---

## Repository roots (not duplicated here)

| Path | Role |
|------|------|
| `organic_market_agent/` | Application code (Python package) |
| `organic_market_agent/db/versions/` | Alembic migrations (schema history) |
| `tests/` | Automated tests |
| `scripts/` | Operational shell scripts |
| `tools/` | Ad-hoc Python helpers (reviews, HTML generators) |
| `docs/` | Glossary + legacy / bilingual specs (see external-references) |
| `_COMMUNICATION/` | Team reports, mandates, roadmap (human process) |

---

*Last updated: 2026-03-31 (post-M6 pipeline resolution improvements, full documentation refresh).*
