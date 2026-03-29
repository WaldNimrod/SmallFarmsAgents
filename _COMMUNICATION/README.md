# SmallFarms — Communication Hub

This folder is the official communication layer between all agent teams in the SmallFarms project.

## Team Structure

| Team | Name | Role |
|------|------|------|
| **Team 100** | Architecture | Project architect. Owns all spec documents and architectural decisions. |
| **Team 50** | QA | Validates implementation against spec. Issues QA reports. |
| **Team 20** | Infrastructure | Python env, PostgreSQL, Alembic, skeleton. Current: M1. |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, aggregator, admin UI. Starts at M2. |

## Folder Structure

```
_COMMUNICATION/
  README.md                  ← this file
  ROADMAP.md                 ← PRIMARY REFERENCE — all milestones M1-M7
  TEAM_100/
    ONBOARDING.md            ← architecture team session onboarding
    reports/                 ← Team 100 reports, decisions, reviews
  TEAM_50/
    ONBOARDING.md            ← QA team session onboarding
    reports/                 ← QA reports, test results, gate decisions
  TEAM_20/
    ONBOARDING.md            ← infrastructure team session onboarding
    MANDATE_M1_INFRASTRUCTURE.md  ← current active mandate
    reports/                 ← infrastructure reports, status updates
  TEAM_10/
    ONBOARDING.md            ← feature dev team session onboarding
    MANDATE_UPRESS_VALIDATION.md  ← DEFERRED to M7 (go-live)
    reports/                 ← feature dev reports, status updates
```

## Report Naming Convention

All report files must follow:
```
YYYY-MM-DD_{TOPIC}_{TEAM_ID}.md
```
Examples:
- `2026-03-29_UPRESS_TEST_RESULTS_TEAM10.md`
- `2026-03-29_ARCH_REVIEW_DB_SCHEMA_TEAM100.md`
- `2026-03-29_QA_NORMALIZER_GATE_TEAM50.md`

## Escalation Protocol

1. If a team is blocked by a technical issue → write blocker in report, ping Team 100 via their reports/ folder
2. If a team needs user (Nimrod) action → mark with `[USER ACTION REQUIRED]` at the top of the report
3. No gate may be passed without written sign-off in the reports/ folder

## Gate System

| Gate | Milestone | Description | Approver |
|------|-----------|-------------|----------|
| G1 | M1 | PostgreSQL schema + seed data + models | Team 50 |
| G2 | M2 | Collector + parser pipeline, 3+ sources | Team 50 |
| G3 | M3 | Normalizer engine with DB-driven rules | Team 50 |
| G4 | M4 | Aggregator + local viewer | Team 50 |
| G5 | M5 | Admin UI functional | Team 100 + Team 50 |
| G6 | M6 | 7-day automated run + alerting | Team 50 |
| G7 | M7 | Public publishing (uPress) — Go-Live | User (Nimrod) |

**Current active gate: G1 (M1)**

Full milestone details: `_COMMUNICATION/ROADMAP.md`
