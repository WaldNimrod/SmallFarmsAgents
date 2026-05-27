# LOD400 — SFA-S003-P002-WP-C — Deferred-Items Canonical Catalog

**Date:** 2026-05-23
**Author:** team_100 (Chief Architect, smallfarmsagents)
**WP:** SFA-S003-P002-WP-C — Deferred-Items Canonical Catalog
**Type:** LOD400_SPEC (documentation-only WP — no L-GATE_V required)
**Status:** L-GATE_S — team_00 advisory review only (no team_190 needed for doc WP)
**Builder:** team_100 (self-author + execute)
**Validator:** team_00 (Principal advisory review)
**Triggered by:** team_00 directive 2026-05-23 — "תיעוד מסודר של כל הזנבות והבעיות שנדחו... לפני פיתוח אבן הדרך הבאה והמחשבון"
**Effort:** SMALL

---

## §1 Goal

Produce a canonical, machine-readable catalog of every deferred item across the S001/S002/S003 program history so nothing is forgotten before S004 (calculator + community features) is opened.

**Single source of truth:** `documentation/KNOWN_DEBT.md` — one file, one place, all deferreds.

This is a documentation WP. No code changes. No tests. team_100 self-authors + commits + team_00 advisory accepts.

---

## §2 Scope — items to catalog

Catalog rules:
- Include items deferred via formal spec sections (`out of scope` / `deferred`)
- Include items deferred via L-GATE_V findings logged for follow-up
- Include items raised in BUILD_REPORT deviations that team_190 accepted
- Include team_00 directives that punted to "later milestone"
- Include hub V4.3 follow-ons that may impact our spoke
- Exclude items already resolved (cross-reference resolution commit/WP)

### §2.1 Inventory of known sources to scan

| Source | Path / Reference | Expected debt items |
|--------|------------------|---------------------|
| WP004 spec §15 "Out of scope" | `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` | crop images, daily cron, mobile responsive, combined shortcode, AC-06 Lighthouse, mobile smoke |
| WP004 spec §14 Risk register | same file §14 | R-WP004-02 bundle size (resolved — 15KB), R-WP004-06 sentinel fragility (mitigated by AC-17/18) |
| WP004 L-GATE_V verdict findings | `_archive/SFA-S003-P001/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` | F-190-WP004-LV-01 (prod-deploy authority — resolved via F-LV-01 decision), F-190-WP004-LV-02 (test-harness — resolved via patch02), N-190-WP004-LV-01 (pytest marker — resolved via patch02) |
| WP003 LOD500 deferreds | `_archive/SFA-S003-P001/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` (if archived) or check roadmap.yaml gate_history | placeholder care tab, market-price card placeholder, entity registry as JS (resolved by WP004 R2 Python-owned), 2 admin patch findings |
| WP002 LOD500 deferreds | similar | none identified pre-scan; verify |
| S002 WP005 RISK_REGISTER | `_archive/SFA-S002-P001/.../WP005/` | R-01 Lighthouse + cross-device smoke deferred to team_50 |
| S003 Discovery Summary | `_COMMUNICATION/TEAM_100/SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0.md` | Tend 5-year ingestion (partial — only 2022 CROP_PLAN+PRODUCT_SOLD+HARVESTS subset is in current seed), MasterClass full ingestion, EXPENSES/LOCATIONS/GREENHOUSE_PLAN/CROPAVAILABILITY etc. unused |
| Hub closure MSG-HUB-20260522-003 §5 | `_COMMUNICATION/TEAM_100/MSG-HUB-20260522-003.md` | V4.3 hub items: Cursor cloud API access, ADR034 R10 addendum (informational — not our scope but our awareness) |
| operational follow-ups | session memory + recent handoffs | team_100@smallfarmsagents API key provisioning, GCR status RESOLVED marking, entity_registry.js admin commit cleanup |
| roadmap project notes | `_aos/roadmap.yaml` lines 15-87 | S003 original definition (Tend+MasterClass) replaced by crop book; original content (WP-A1 moderated, WP-A2 calculator, M9C, M11) deferred to S004 — full backlog |
| F-LV-01 §2 closure obligation | `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` | binding policy for ALL future programs (unified end-state validation) — not a deferred item but a binding rule worth surfacing |

---

## §3 Output format — `documentation/KNOWN_DEBT.md`

```markdown
# Known Debt Catalog — SmallFarmsAgents

**Last refresh:** YYYY-MM-DD by team_100 / WP-XXX
**Refresh policy:** at program closure (every Phase-2-or-later P-program), team_100 sweeps
new deferred items into this file. Items are CARRIED (still deferred), RESOLVED (with
resolution-ref), or PROMOTED (became an active WP).

---

## Index

- §A Pre-S004 debt (must consider before opening S004)
- §B Operational follow-ups (admin/governance, non-product)
- §C Tend + MasterClass remaining ingestion (S003 redefinition leftover)
- §D Hub V4.3 awareness (informational; not our scope unless promoted)
- §E Resolved debt (audit trail; items closed since prior refresh)
- §F Binding policies (NOT deferred — surfaced for visibility)

---

## §A — Pre-S004 debt

### A.1 Crop book UX/UI follow-ups (deferred from WP004)
[id, severity, source-ref, current-status, S004-impact]

(populate from WP004 §15 + LV verdict findings)

### A.2 Crop book mobile parity
[id ...]

### A.3 Crop image / photo gallery
...

### A.4 Daily auto-publish cron for crop book
...

### A.5 Combined market+crop-book shortcode
...

### A.6 Lighthouse + cross-device smoke (from S002 WP005)
...

### A.7 ... (continue from source scan)

---

## §B — Operational follow-ups

### B.1 Provision team_100@smallfarmsagents API key
- Source: GCR_AOS_MESSAGING_INFRA closure MSG-HUB-20260522-003 §4
- Action: run `scripts/issue_actor_key.sh smallfarmsagents-team_100` (team_00 or team_99)
- Effect when done: canonical API path works for team_100 sends (file-fallback becomes defensive-only)
- Priority: MEDIUM

### B.2 Mark resolved GCRs in their file frontmatter
- Source: GCR_AOS_MESSAGING_INFRA + GCR_UPRESS_FTPS — both hub-resolved 2026-05-22
- Action: edit `_COMMUNICATION/TEAM_100/GCR_*.md` to add `status: CLOSED` + `hub_closure_artifact` + `resolved_at`
- Priority: LOW (housekeeping)

### B.3 entity_registry.js admin file commit
- Source: F-190-patch02-03 + F-190-WP004-01 R2 fix narrative
- Context: file EXISTS in working tree (`organic_market_agent/admin/static/crop_book/entity_registry.js`, 4009B) but its provenance never landed in a LOD500_LOCKED gate. patch02 routed around (Python-owned registry in publisher). Admin templates still reference the JS at `url_for('static', ...)`.
- Action: either (a) commit the JS as canonical for admin OR (b) refactor admin to import from publisher's Python registry data
- Priority: LOW

---

## §C — Tend + MasterClass remaining ingestion

### C.1 Tend tables not yet ingested
- Source: `_COMMUNICATION/TEAM_100/SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0.md`
- Currently ingested: 2022 CROP_PLAN + PRODUCT_SOLD + HARVESTS (subset, for crop_book seed)
- NOT ingested: CROPAVAILABILITY, EXPENSES, GREENHOUSE_PLAN, LOCATIONS, ORDERS_RAW_DATA, and 5 more tables × 5 years
- Potential consumers: WP-A enrichment (more longitudinal data), WP-A2 farmer calculator (S004)
- Priority: MEDIUM (will likely promote into WP-A scope if team_110 finds value)

### C.2 MasterClass beyond current JMF subset
- Currently ingested: JMF price/yield benchmarks per crop
- NOT ingested: full MasterClass library (other published references)
- Priority: LOW

---

## §D — Hub V4.3 awareness (informational only)

### D.1 Cursor cloud agent → hub API access gap
- Source: GCR_AOS_MESSAGING_INFRA closure MSG-HUB-20260522-003 §5
- Hub triage: `agents-os:_COMMUNICATION/team_100/TRIAGE_CURSOR_API_ACCESS_ESCALATION_2026-05-22_v1.0.0.md`
- Impact on us: if we use Cursor cloud sandbox for team_190 (instead of Mac), API access blocked. Current workaround: run team_190 on local Mac + Tailscale.
- Priority: LOW (workaround exists)

### D.2 ADR034 R10 addendum (Hub-Native WP File-SSoT Exception)
- Source: same MSG-HUB-20260522-003 §5
- Hub finding: `agents-os:_COMMUNICATION/team_100/FINDING_HUB_NATIVE_WP_DB_SYNC_NOT_APPLICABLE_2026-05-22_v1.0.0.md`
- Impact on us: governance clarification — formalizes that hub WPs (AOS-V*) are file-canonical, parallel to ADR034 R9 for our spoke roadmap. Probably zero practical impact on us; informational.
- Priority: INFO

---

## §E — Resolved debt (audit trail)

Items resolved since prior catalog refresh:

| Date | Item | Resolution-ref |
|------|------|----------------|
| 2026-05-23 | F-190-WP004-LV-02 test-harness debt | SFA-S003-P001-WP003-patch02 LOD500_LOCKED |
| 2026-05-23 | N-190-WP004-LV-01 pytest marker | same patch02 |
| 2026-05-22 | F-LV-01 prod-deploy authority gap | DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY (Hybrid policy approved) |
| 2026-05-22 | GCR_AOS_MESSAGING_INFRA (all 9 F/R pairs) | hub AOS-V4.1-WP-ACTOR-KEY-PROCEDURE + AOS-V4.2-WP-MSG-CANON-EXTENSIONS + AOS-V4.2-WP-POST-MIGRATION-HARDENING (all LOD500_LOCKED) |
| 2026-05-22 | GCR_UPRESS_FTPS_PROTOCOL | hub canon `lean-kit/modules/12-home-server-infrastructure/runbooks/UPRESS_FTPS_PROTOCOL_v1.0.0.md` propagated |

---

## §F — Binding policies (not deferred; surfaced for visibility)

### F.1 F-LV-01 §2 unified-end-state invariants
- Source: `_COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md` §2
- Binding for: ALL future programs
- Closure obligation: team_100 must validate (a) unified deployment, (b) single canonical branch (merge to main), (c) no version drift — BEFORE issuing archive mandate.
- Reminder: violations → open follow-up cleanup WP before closure artifacts.

### F.2 prod_deploy_authority field on DISPATCH (F-LV-01 Hybrid policy)
- Source: same DECISION_F-LV-01 §1
- Binding for: every DISPATCH artifact going forward
- Default tier:
  - L0 / SMALL WPs → `builder`
  - LARGE / production-critical → `team_99`
  - Security-sensitive → `amend_required`
```

---

## §4 Acceptance Criteria

| AC | Criterion | Evidence |
|----|-----------|----------|
| AC-01 | `documentation/KNOWN_DEBT.md` exists and parses as valid markdown | manual inspection |
| AC-02 | KNOWN_DEBT.md covers all 10 sources listed in §2.1 (each source scanned, items extracted or noted as "none found") | sweep verification |
| AC-03 | Each debt item has: id, severity, source-ref (with path), current-status, S004-impact note | structured entries |
| AC-04 | Each resolved item in §E has resolution-ref pointing to commit/WP/decision | cross-reference |
| AC-05 | Roadmap project notes acknowledge KNOWN_DEBT.md as canonical backlog source | roadmap.yaml updated |
| AC-06 | Refresh policy stated in KNOWN_DEBT.md header (when + by whom + trigger) | header text |
| AC-07 | team_00 advisory review acknowledges the catalog covers what they think it should | in-session ack |
| AC-08 | `validate_aos.sh` 0 FAIL post-commit | CI |

---

## §5 Build sequence (5 steps, ~1h)

1. **Sweep** — scan all 10 sources in §2.1, extract candidate items. (~20 min)
2. **Author** — write `documentation/KNOWN_DEBT.md` per the §3 template. (~20 min)
3. **Cross-link** — add a roadmap.yaml notes mention pointing to KNOWN_DEBT.md as canonical backlog. Update SFA-S003-P002-WP-C entry status → COMPLETE. (~5 min)
4. **Validate** — `validate_aos.sh` 0 FAIL. (~5 min)
5. **Commit** — `feat(S003-WP-C): canonical deferred-items catalog → documentation/KNOWN_DEBT.md`. Display to team_00 for advisory review. (~10 min)

---

## §6 Constitutional invariants

| Iron Rule | Application |
|-----------|-------------|
| #4 Single roadmap writer | team_100 is sole writer of `_aos/roadmap.yaml`. Self-WP — no conflict. |
| #6 Artifact comms | KNOWN_DEBT.md is the canonical inter-program artifact. |
| Directory authority (team_100) | `documentation/`, `_aos/roadmap.yaml`, `_COMMUNICATION/TEAM_100/`. No code surface. |
| Doc WP exemption | No L-GATE_B / L-GATE_V required (no implementation). team_00 advisory accept = closure. |

---

## §7 Definition of Done

1. AC-01..AC-08 all PASS
2. team_00 acknowledges catalog in-session
3. Roadmap WP-C gate_history extended with L-GATE_DONE (CONTENT-track-style — no L-GATE_V)
4. Commit on `claude/gallant-elbakyan-727a60`
5. KNOWN_DEBT.md visible to anyone opening S004 planning ("read KNOWN_DEBT.md before scoping S004" becomes a startup line in S004's eligibility brief)

---

*LOD400 spec v1.0.0 — authored 2026-05-23 by team_100.*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending.*
