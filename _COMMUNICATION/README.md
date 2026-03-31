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

## Iron Rules (All Teams)

### 1. Spec Study Before Code Change

**Before modifying ANY code, read the relevant spec documents.**
Spec docs define WHAT the system should do and WHY. The mandate defines WHAT to implement NOW.
If a change contradicts a spec, STOP and flag to Team 100.

See each team's `ONBOARDING.md` for the categorized spec document table.

### 2. Changelog Discipline

**Every code change must be logged in `CHANGELOG.md` (project root) under `[Unreleased]`.**
At milestone end (after gate PASS), entries are moved to a versioned section with documentation update.

This is verified by Team 50 at every gate — missing changelog entries are a gate blocker.

---

## ⚠️ Canonical Templates — Mandatory

All inter-team communication **must** use the canonical templates defined in:

```
_COMMUNICATION/TEMPLATES/
  README.md             ← Template index + usage rules (READ FIRST)
  MANDATE.md            ← Work orders issued to implementing teams
  COMPLETION_REPORT.md  ← Mandate completion + next action request
  QA_REVIEW_REQUEST.md  ← Request to Team 50 to run gate QA
  QA_FINDINGS_REPORT.md ← Team 50 gate results + binding gate decision
  ARCH_DECISION.md      ← Team 100 decisions, gate open/close, amendments
```

> Documents not using these templates are informally valid but carry
> **no binding authority** for gate decisions or mandate obligations.

**Before writing any report or mandate:** read `_COMMUNICATION/TEMPLATES/README.md`.

---

## Team Structure

| Team | Name | Role | Reports to |
|------|------|------|------------|
| **Team 100** | Architecture | Owns spec, decisions, reviews | Nimrod |
| **Team 50** | QA | Validates implementation against spec | Team 100 |
| **Team 20** | Infrastructure | DB, env, migrations, seed data | Team 100 |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, admin UI | Team 100 |

Active milestone and gate status: `_COMMUNICATION/ROADMAP.md`

---

## Folder Structure

```
_COMMUNICATION/
  README.md                          ← this file
  ROADMAP.md                         ← PRIMARY REFERENCE — all milestones M1–M7
  TEMPLATES/                         ← Canonical templates (MANDATORY)
  TEAM_100/
    ONBOARDING.md
    reports/                         ← arch decisions, reviews, gate rulings
  TEAM_50/
    ONBOARDING.md
    QA_MANDATE_G*.md                 ← per-gate QA mandates
    reports/                         ← QA findings, review requests
  TEAM_20/
    ONBOARDING.md
    MANDATE_*.md                     ← active mandates
    reports/                         ← completion reports, blockers
  TEAM_10/
    ONBOARDING.md
    MANDATE_*.md                     ← active mandates
    reports/                         ← completion reports, blockers
```

---

## Standard Document Naming

```
Mandates (in TEAM_XX/):       MANDATE_{TOPIC}_{TEAM_RECIPIENT}.md
Completion Reports:           {YYYY-MM-DD}_{TOPIC}_COMPLETE_TEAM{ID}.md
QA Review Requests:           {YYYY-MM-DD}_G{N}_REVIEW_REQUEST_TEAM{ID}.md
QA Findings:                  {YYYY-MM-DD}_G{N}_QA_FINDINGS_TEAM50.md
Arch Decisions / Reviews:     {YYYY-MM-DD}_{TOPIC}_TEAM100.md
```

All filenames: `UPPERCASE_WITH_UNDERSCORES.md` — no spaces, no Hebrew.

---

## Communication Flow

```
Implementing Team           Team 100              Team 50
       │                       │                     │
       │  Read MANDATE         │                     │
       │◄──────────────────────│                     │
       │                       │                     │
       │  [implement work]     │                     │
       │                       │                     │
       │  COMPLETION_REPORT ──►│                     │
       │  + QA_REVIEW_REQUEST ─┼────────────────────►│
       │                       │                     │
       │                       │  [run QA mandate]   │
       │                       │                     │
       │◄──────────────────────┼─ QA_FINDINGS_REPORT │
       │                       │◄────────────────────│
       │                       │                     │
       │  [if PASS: next M]    │                     │
       │  [if FAIL: fix+loop]  │                     │
```

---

## Escalation Protocol

1. **Blocked on technical issue** → file `BLOCKED_{TOPIC}_TEAM{ID}.md` in your `reports/`
2. **Blocked waiting on Nimrod** → tag report with `[USER ACTION REQUIRED]`
3. **Gate disputes** → Team 100 issues an `ARCH_DECISION` doc to resolve
4. **No gate passes** without written `QA_FINDINGS_REPORT` from Team 50
5. **Gates G5 and G7** additionally require Team 100 or Nimrod written sign-off

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

Full milestone details: `_COMMUNICATION/ROADMAP.md`
