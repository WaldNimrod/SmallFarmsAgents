# MILESTONE_MAP.md — SmallFarmsAgents AOS Milestone Descriptions

## Pre-AOS History (completed before canonization)

| Phase | Period | Outcome |
|-------|--------|---------|
| M1 — Foundation | 2026-03 | Project setup, initial scraping infrastructure |
| M2 — Data Pipeline | 2026-03 | PostgreSQL schema, Alembic migrations, scraper agents |
| M3 — Market Intelligence | 2026-03 | Price normalization, Hebrew NLP, unit standardization |
| M4 — Multi-Source | 2026-03 | Shufersal, Rami Levy, organic farms integration |
| M5 — Quality Assurance | 2026-03 | Test suite (127+ tests), G1-G6 gates, CI pipeline |
| M6 — Hub Integration | 2026-03 – 04 | Data hub connector, JSON export, nimrod.bio publish path |
| M7 — Reporting | 2026-04 | Price index reports, community dashboard data |
| M8 — Documentation | 2026-04 | English docs hub, bilingual glossary, SSOT |
| M9 — Resolution | 2026-04 | 100% extraction resolution rate achieved |

## AOS Stages

### S001 — AOS Canonization (ACTIVE)

**Goal:** Wrap the existing project in AOS governance structure.
Adds `_aos/`, `CLAUDE.md`, lean-kit snapshot, and registers in hub.
No changes to project code, scripts, or data pipeline.

**WPs:**
- S001-P001-WP001: `_aos/` Foundation (governance + lean-kit + hub registration)

**Exit criterion:** `validate_aos.sh` exits 0 + Team 190 L-GATE_V PASS.

### M10 — UX & Publish (BACKLOG)

**Goal:** Community-facing UX for the organic price index.
Pending: nimrod.bio integration, public dashboard, user-facing reports.

### M11 — Community Features (BACKLOG)

**Goal:** Community contribution pipeline — farmers submit prices, community validation.
Pending: user auth, submission flow, validation protocol.
