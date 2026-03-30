# MyFarmAgents — Communication Hub

> **MyFarmAgents** is a volunteer community initiative building collaborative AI
> agents for Israel's small organic farming community.
>
> **OrganicMarketAgent** is the first agent — a community price index for
> organic vegetables.

---

## Language Policy

All documents and reports in this folder are written in English.
Hebrew is used only in direct conversation with project lead Nimrod.
Canonical terminology: `docs/GLOSSARY.md`

---

## Team Structure

| Team | Name | Role | Active Mandate |
|------|------|------|----------------|
| **Team 100** | Architecture | Owns spec and architectural decisions | Ongoing review |
| **Team 50** | QA | Validates implementation against spec | Gate G1 review pending |
| **Team 20** | Infrastructure | DB, env, skeleton | **M1 — active** |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, admin UI | Waiting for G1 |

---

## Folder Structure

```
_COMMUNICATION/
  README.md                          ← this file
  ROADMAP.md                         ← PRIMARY REFERENCE — all milestones M1–M7
  TEAM_100/
    ONBOARDING.md                    ← architecture team session onboarding
    reports/
  TEAM_50/
    ONBOARDING.md                    ← QA team session onboarding
    reports/
  TEAM_20/
    ONBOARDING.md                    ← infrastructure team session onboarding
    MANDATE_M1_INFRASTRUCTURE.md     ← current active mandate
    reports/
  TEAM_10/
    ONBOARDING.md                    ← feature dev team session onboarding
    MANDATE_UPRESS_VALIDATION.md     ← DEFERRED to M7 (go-live)
    reports/
```

---

## Report Naming Convention

```
YYYY-MM-DD_{TOPIC}_{TEAM_ID}.md
```

Examples:
- `2026-03-29_M1_COMPLETE_TEAM20.md`
- `2026-03-29_G1_QA_PASS_TEAM50.md`
- `2026-03-29_ARCH_REVIEW_DB_SCHEMA_TEAM100.md`

---

## Escalation Protocol

1. Blocked by technical issue → write blocker in report, notify Team 100 via their reports/
2. Blocked waiting on Nimrod → mark report with `[USER ACTION REQUIRED]`
3. No gate passes without written Team 50 sign-off
4. Gates G5 and G7 additionally require Team 100 or Nimrod sign-off

---

## Gate System

| Gate | Milestone | Description | Required Sign-off |
|------|-----------|-------------|-------------------|
| G1 | M1 | PostgreSQL schema + seed data + models | Team 50 |
| G2 | M2 | Collector + parser pipeline, 3+ sources | Team 50 |
| G3 | M3 | Normalizer engine, DB-driven rules | Team 50 |
| G4 | M4 | Aggregator + local viewer | Team 50 |
| G5 | M5 | Admin UI functional | Team 100 + Team 50 |
| G6 | M6 | 7-day automated run + alerting | Team 50 |
| G7 | M7 | Public publishing (uPress) — Go-Live | Nimrod |

**Current active gate: G1 (M1)**

Full milestone details: `_COMMUNICATION/ROADMAP.md`
