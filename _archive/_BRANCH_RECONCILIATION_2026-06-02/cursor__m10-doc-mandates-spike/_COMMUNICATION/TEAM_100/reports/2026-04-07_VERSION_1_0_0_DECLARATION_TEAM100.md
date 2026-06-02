# Team 100 — Version 1.0.0 Declaration

**Document ID:** ARCH-20260407-V1-0-0  
**Date:** 2026-04-07  
**Author:** Team 100 (Architecture)  
**Status:** DECLARED

---

## 1. Declaration

Team 100 hereby declares the current state of the OrganicMarketAgent system as **version 1.0.0** — the first official production release.

**Git tag:** `v1.0.0`

---

## 2. Scope of v1.0.0

Version 1.0.0 encompasses all work from project inception through M13 completion:

| Milestone | Description | Gate |
|-----------|-------------|------|
| M1 | Local Foundation (DB, models, migrations) | G1 PASS |
| M2 | Collection Layer (collectors, parsers, ingestion) | G2 PASS |
| M3 | Normalizer Engine (alias, unit, price, basket, confidence) | G3 PASS |
| M4 | Aggregation + Local Viewer + Admin Dashboard | G4 PASS |
| M5 | Admin UI (CRUD, auth, blueprints) | G5 PASS |
| M6 | Automation + Resilience (scheduler, alerts, charts) | G6 PASS |
| M7 | Public Publishing / Go-Live (FTPS, WordPress) | G7 PASS |
| M8 | UX Polish + Policy Formalization | G8 PASS |
| M9 | Site Optimization and Maintenance | G9 PASS |
| M10 | Source Expansion & Data Quality (M10.1-M10.3 complete; M10.4/M10.5 frozen) | G10 CONDITIONAL |
| M13 | Public Product Details + CSA + Channel Variants | G11 CONDITIONAL PASS |

### System Metrics at v1.0.0

| Metric | Value |
|--------|-------|
| Published products | 77 |
| Active sources | 14+ community sources |
| Alembic head revision | 071 |
| Test suite | 183 passed, 5 skipped |
| Public index | Live at nimrod.bio/smallfarmsagent/ |
| Schema version | 3.0 (manifest + report) |
| Admin dashboard | Operational at localhost:5000 |
| Automated pipeline | Cron-based, FTPS upload to uPress |

---

## 3. Known Limitations (carried forward to v1.1.0)

- M10.4 (mypips) and M10.5 (CSA/retail) are FROZEN — capability in codebase but QA targets not met
- 92 distinct unresolvable alias names (backlog)
- PRD027 duplicate in published output (investigation pending)
- PRD072 (passion fruit) unit inconsistency across sources
- G11 keyboard accessibility (focus-trap) is CONDITIONAL
- M9C content not yet published (blog post pending Nimrod briefing)

These items are scoped for resolution in v1.1.0.

---

## 4. Version Scheme Going Forward

| Version | Scope | Gate |
|---------|-------|------|
| **v1.0.0** | M1-M13 complete (this declaration) | -- |
| **v1.1.0** | Consolidated CQ + M10.x + M9C | G-V1.1 |
| **v1.2.0** | M11 specs (farmer roles, FarmCostAgent, submission form) | -- |
| v2.x | M12 vision features (out of current scope) | TBD |

---

## 5. CHANGELOG Freeze

All entries currently under `[Unreleased]` in `CHANGELOG.md` are moved to `[1.0.0] - 2026-04-07` as part of this declaration. Future changes target `[Unreleased]` for the v1.1.0 cycle.

---

## 6. Signature

**Declared by:** Team 100 (Architecture)  
**Document ID:** ARCH-20260407-V1-0-0  
**Effective:** Immediately
