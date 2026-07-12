# SFA Public Index Launch Readiness — Program Package (LOD200)

**Date:** 2026-05-07
**Author:** team_100 (sfa_arch / Claude Opus 4.7)
**Program ID:** SFA-S002-P001
**Milestone:** S002 (opened 2026-05-07)
**Type:** PROGRAM_PACKAGE
**LOD:** 200 (concept + decomposition + acceptance at program level)
**Status:** L-GATE_E PASS — team_00 directive 2026-05-07

---

## 1. Purpose

Bring the existing **OrganicMarketAgent price index** (`[sfagent_market_report]` shortcode + `public_report_body.html` + `sfagent-base.css`) to a **full publication-ready state**. This program completes work-in-flight rather than introducing new product surfaces.

team_00 directive (2026-05-07): "**יישור קו והשלמה למצב מלא ומוכן לחשיפה ופרסום**" — exhaust all sources for scraping, verify proper scraping running on production server, accurate phone rendering of the index, implement all MyPIPS stores discovered, complete M10 as part of this program.

---

## 2. Binding decisions

| ID | Topic | Decision |
|----|--------|----------|
| **D1** | M10 status | **THAWED.** Decision D4 in `SFA-PKG-POST-M9-001` LOD200 is superseded. M10 work parked on `cursor/m10-doc-mandates-spike` (commit `bb981ed`) returns to active program as WP001. |
| **D2** | WP-A1 (moderated submissions) + WP-A2 (farmer calculator) | **DEFERRED to S003 or beyond.** Advanced stage-3 features. team_00 ruling: "ברור שזה נדחה - זה לא סתם שלב 3 זה שלב 3 מתקדם." |
| **D3** | Tend exports + MasterClass PDFs (on `cursor/mypips-communication-and-handoffs`) | **RAW MATERIAL — DO NOT TOUCH.** Reserved for the next dev phase after this release. Builders MUST NOT modify, merge, or reorganize these files. |
| **D4** | MyPIPS store-discovery (on same branch) | **IN SCOPE as WP002.** Substantive store-finding research; needs audit (completed / failed / partial) before integration. |
| **D5** | DB offline | **R8 Offline Changelog Protocol** active on branch `offline/2026-05-07-smallfarmsagents-release-prep`. Spoke-native WPs use file-based SSoT (R9) — `_aos/PENDING_DB_SYNC.yaml` records pending mutations for hub-side awareness. |
| **D6** | Cross-engine validation | team_100 = Opus (orchestrator). Builders = Sonnet (Agent tool). QA = Haiku. Final validation = external (manual via `aos_mail` package to team_00 → external session). |
| **D7** | Push authority | team_100 has push authority for this session (team_00 ruling 2026-05-07). |

---

## 3. Work package decomposition

| WP | Label | Effort | Builder | QA | Validator | Depends on |
|----|-------|--------|---------|----|-----------|------------|
| **SFA-S002-P001-WP001** | M10 Thaw + Completion | LARGE | sfa_build (Sonnet, Team 10) | sfa_qa (Haiku, Team 50) | external | — |
| **SFA-S002-P001-WP002** | MyPIPS Source Integration + Branch Cleanup | LARGE | sfa_build (Sonnet, Team 10) | Team 50 | external | WP001 |
| **SFA-S002-P001-WP003** | Server Scraping Verification | NORMAL | Team 60 (Sonnet) | Team 50 | external | — |
| **SFA-S002-P001-WP004** | Mobile UI Parity | NORMAL | sfa_build (Sonnet, Team 10) | Team 50 | external | — |
| **SFA-S002-P001-WP005** | Public Launch Package | NORMAL | team_100 + Team 50 | Team 50 | external | WP001..WP004 |

**Sequencing:** WP001 → WP002 (MyPIPS depends on M10 source-handling refresh). WP003 + WP004 in parallel with WP002. WP005 final.

---

## 4. Per-WP scope summary

### WP001 — M10 Thaw + Completion
- Revive parked work from `cursor/m10-doc-mandates-spike` (commit `bb981ed`):
  - Migrations 072 (`cq_p01_alias_batch.py`), 073 (`src_wa_pending_manual.py`)
  - `organic_market_agent/normalizer/basket_tier_resolver.py` + tests (PRD025/026/027 small/medium/large basket tiers)
  - LOD400 communications v1.1, dev stack docs, SQL verification scripts
- Reconcile against current main (58 commits ahead).
- Deliverable: clean rebase or extracted-and-reapplied changes, all tests green.

### WP002 — MyPIPS Source Integration + Branch Cleanup
- Audit `cursor/mypips-communication-and-handoffs` MyPIPS portion: classify each store discovery as COMPLETED / FAILED / PARTIAL.
- Integrate COMPLETED sources into `organic_market_agent/sources/` (collectors).
- Document FAILED experiments in `_COMMUNICATION/TEAM_100/SFA-S002-P001/MYPIPS_AUDIT.md`.
- Complete PARTIAL sources where feasible.
- Final state: branch `cursor/mypips-communication-and-handoffs` is empty of in-scope work (raw material preserved).

### WP003 — Server Scraping Verification (waldhomeserver)
- Confirm production scraping schedule on `waldhomeserver`: cron jobs / systemd timers, log integrity, freshness SLA.
- Verify FTPS publish pipeline parity (referenced in 2026-04 sign-offs).
- Output: `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.md`.

### WP004 — Mobile UI Parity
- Audit `[sfagent_market_report]` rendering on iOS/Android viewports.
- Fix responsive issues in `public_report_body.html` + `sfagent-base.css`.
- Lighthouse mobile score target ≥ 85.
- Smoke evidence: screenshots at 375px / 414px / 768px.

### WP005 — Public Launch Package
- Run `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`.
- Compose external QA bundle: scope summary, test results, parity sign-offs, rollback plan.
- Generate `aos_mail` package for team_00 → external validator dispatch.

---

## 5. Program-level acceptance (Team 190 / external validator)

| PAC | Criterion |
|-----|-----------|
| **PAC-01** | All 5 WPs reach L-GATE_V PASS (or PASS_WITH_REMEDIATION). |
| **PAC-02** | `validate_aos.sh` 0 FAIL on the offline branch before close. |
| **PAC-03** | Full test suite green on the integrated branch. |
| **PAC-04** | MyPIPS branch processed: in-scope work merged or filed; raw material untouched. |
| **PAC-05** | Mobile parity smoke evidence captured. |
| **PAC-06** | Server scraping freshness verified within last 24h before launch. |
| **PAC-07** | External validation feedback ingested (or formally waived). |

---

## 6. Out of scope

- **Tend farm exports (CSV/ZIP)** + **Team 80 MasterClass PDFs** — raw material reserved for next-phase dev (D3).
- **WP-A1 (moderated submissions)** — deferred to S003+ (D2).
- **WP-A2 (farmer economics calculator)** — deferred to S003+ (D2).
- **AOS hub governance edits** — this session writes to spoke only.

---

## 7. Cross-engine map (Iron Rule #1)

| Role | Engine | Source |
|------|--------|--------|
| **Orchestrator (team_100)** | Claude Opus 4.7 | This session |
| **Builder (sfa_build)** | Claude Sonnet 4.6 | Spawned via Agent tool, subagent_type=general-purpose |
| **QA (sfa_qa, Team 50)** | Claude Haiku 4.5 | Spawned via Agent tool |
| **Cross-engine validator** | External (Cursor/manual) | aos_mail package to team_00 → external session |

team_100 (Opus) does NOT validate code it caused to be built. External step is the constitutional validator.

---

## 8. References

| Document | Role |
|----------|------|
| [`_aos/PENDING_DB_SYNC.yaml`](../../../_aos/PENDING_DB_SYNC.yaml) | Offline mutations log (this session) |
| [`_aos/roadmap.yaml`](../../../_aos/roadmap.yaml) | WP state registry (file-based SSoT, ADR034 R9) |
| [`_COMMUNICATION/ROADMAP.md`](../../ROADMAP.md) | Narrative roadmap (to be updated post-launch) |
| `cursor/m10-doc-mandates-spike@bb981ed` | M10 parked work source |
| `cursor/mypips-communication-and-handoffs@732121e` | MyPIPS work + raw material (do not touch raw) |
| [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) | Publish runbook |

---

*End of LOD200 program package. L-GATE_E PASS recorded 2026-05-07 by team_00 in-session approval. Next: per-WP LOD400 specs.*
