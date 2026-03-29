# SmallFarms — Communication Hub

This folder is the official communication layer between all agent teams in the SmallFarms project.

## Team Structure

| Team | Name | Role |
|------|------|------|
| **Team 100** | Architecture | Project architect. Owns all spec documents and architectural decisions. |
| **Team 50** | QA | Validates implementation against spec. Issues QA reports. |
| **Team 10** | Implementation | Writes all production code. First task: uPress validation. |

## Folder Structure

```
_COMMUNICATION/
  README.md                  ← this file
  TEAM_100/
    ONBOARDING.md            ← architecture team session onboarding
    reports/                 ← Team 100 reports, decisions, reviews
  TEAM_50/
    ONBOARDING.md            ← QA team session onboarding
    reports/                 ← QA reports, test results, gate decisions
  TEAM_10/
    ONBOARDING.md            ← implementation team session onboarding
    MANDATE_UPRESS_VALIDATION.md  ← first mandate: uPress FTP testing
    reports/                 ← implementation reports, status updates, blockers
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

| Gate | Description | Approver |
|------|-------------|----------|
| G0 | uPress FTP access validated | User (Nimrod) |
| G1 | PostgreSQL schema deployed + tested | Team 50 |
| G2 | Collector + parser pipeline end-to-end | Team 50 |
| G3 | Normalizer engine with DB-driven rules | Team 50 |
| G4 | Aggregator + publish to FTPS | Team 50 |
| G5 | Admin UI functional | Team 100 review |
| G6 | Full integration test | Team 50 sign-off |
