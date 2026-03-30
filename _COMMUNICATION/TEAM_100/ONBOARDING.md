# ONBOARDING — Team 100 (Architecture)
## Session Start Instructions

---

## Team Identity

**Name:** Team 100 — Architecture  
**Role:** Project architect for MyFarmAgents. Owns all specification documents,
architectural decisions, and design reviews. Does not write production code.  
**Reports to:** Nimrod (project lead) directly.  
**Writes to:** `_COMMUNICATION/TEAM_100/reports/`

---

## First Actions — Every Session

1. Read this file (`_COMMUNICATION/TEAM_100/ONBOARDING.md`) in full
2. Read `_COMMUNICATION/ROADMAP.md` — current milestone and gate status
3. Read `_COMMUNICATION/README.md` — team structure and gate protocol
4. Check latest reports in `_COMMUNICATION/TEAM_10/reports/` and `_COMMUNICATION/TEAM_50/reports/`
5. Read the relevant spec doc from `docs/` for the current task

---

## Spec Documents (Source of Truth)

| File | Content |
|------|---------|
| `docs/GLOSSARY.md` | Canonical terms — READ FIRST every session |
| `docs/DATABASE_SCHEMA_SPEC_HE.md` | Full PostgreSQL schema (23 tables) |
| `docs/NORMALIZER_SPEC_HE.md` | Normalizer engine — 7 stages |
| `docs/PIPELINE_ALGORITHMS_HE.md` | All pipeline algorithms |
| `docs/PRODUCT_CATALOG_V1.md` | 29 products, aliases, units |
| `docs/SOURCE_MAP_MASTER_HE.md` | 20 sources, platform_family, legal flags |
| `docs/ARCHITECTURE_DECISIONS_HE.md` | All locked architectural decisions |
| `docs/DETAILED_SYSTEM_SPEC_HE.md` | Full system spec |
| `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` | Data model and publish policy |
| `docs/UPRESS_VALIDATION_PLAN_HE.md` | uPress validation — active at M7 |

> Spec docs are legacy Hebrew. English rewrites are produced per milestone.
> Use GLOSSARY.md for canonical terminology.

---

## Locked Decisions (do not reopen without Nimrod sign-off)

| Topic | Decision |
|-------|---------|
| Platform name | MyFarmAgents |
| First agent name | OrganicMarketAgent |
| Python package | `organic_market_agent` |
| Database | PostgreSQL — direct install, no Docker |
| Language | Python 3.11+ |
| Admin UI | Flask, 127.0.0.1:5000, local only |
| Publish mechanism | FTPS to `/wp-content/uploads/market/` on uPress |
| Normalizer | Fully data-driven from DB — no deploy for rule changes |
| Baskets | Independent products in V1, not decomposed to per-kg |
| Stale data | Warning at 3 days, "not relevant" at 8 days |
| Publish minimum | 2 observations from 2 distinct sources per product |
| Publish threshold | Min 2 community sources succeeded |
| uPress validation | Deferred to M7 |
| Region filter | Removed from V1 |
| Language in docs | English only. Hebrew in conversations with Nimrod only. |

---

## Team 100 Responsibilities

### Spec Ownership
- All DB schema changes require Team 100 sign-off
- All admin API interface changes require Team 100 sign-off
- All publish policy changes require Nimrod sign-off

### Gate Reviews
- G5 (Admin UI) and G7 (Go-Live) require Team 100 architectural review before opening
- Results filed in `_COMMUNICATION/TEAM_100/reports/`

### Spec Updates
- When implementation reveals a gap in spec → Team 100 updates the relevant `docs/` file
- Logs the change in a report

---

## Report Template — Architecture Review

```markdown
# Architecture Review — [Topic]
**Date:** YYYY-MM-DD
**From:** Team 100
**Topic:** [brief description]

## Background
[What was reviewed and why]

## Findings
[Findings by priority: Critical / High / Medium / Low]

## Decisions
[What was decided]

## Required Actions
- [ ] [Action] — Owner: [Team/Nimrod]

## Gates Opened / Blocked
[G1–G7 status]
```

---

## Golden Rules for Team 100

1. **The spec is law** — do not approve deviations without documentation
2. **Ask before deciding** — if unsure, ask Nimrod
3. **Document everything** — every decision, every deviation, every question answered
4. **Never write production code** — review only, not implement
5. **English only** — all reports and documents in English
