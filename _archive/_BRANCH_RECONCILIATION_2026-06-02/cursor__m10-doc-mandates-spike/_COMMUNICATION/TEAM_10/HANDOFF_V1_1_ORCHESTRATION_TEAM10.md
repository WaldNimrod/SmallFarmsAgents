# Team 10 — v1.1.0 Phase A Orchestration Handoff

**Document ID:** HANDOFF-20260408-V1-1-ORCH-TEAM10  
**Date:** 2026-04-08  
**Issued by:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev — primary executor and orchestrator)  
**Status:** ACTIVE  
**Mandate reference:** `MANDATE-20260408-V1-1-LOD400-EXEC` (`_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md`)  
**Spec reference:** `SPEC-20260408-PHASE-A-LOD400` (`_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`)

---

## Purpose

This document is the practical field guide for executing v1.1.0 Phase A across all participating teams. The mandate tells you **what** to build. This document tells you **how to coordinate**, **who to hand off to**, **when**, and **through which artifacts**.

**Team 10's role in this release is dual:**
1. **Implementer** — write the code, run the queries, produce the artifacts
2. **Orchestrator** — manage the coordination flow between Team 20, Team 50, Team 100, and Nimrod

No gate will open without the correct artifacts in the correct places. No team will act without a properly filed request. Read this document once before starting, and refer back to the relevant section at each phase transition.

---

## 1. Governing Document Hierarchy

When anything conflicts, this is the precedence order:

```
SPEC-20260408-PHASE-A-LOD400       ← binding for all implementation details
    │  (adds precision to ↓)
MANDATE-20260408-V1-1-LOD400-EXEC  ← binding execution order
    │  (supersedes ↓ at LOD400 level)
MANDATE-20260407-V1-1-CONSOLIDATED ← retain for context only
    │  (policy decisions still binding from ↓)
ARCH-20260406-CQ-MASTER            ← LOD200 policy (alias rules, tier ranges, cherry tokens)
```

If code, plan, or policy conflict: stop, file a delta report to Team 100, wait for resolution. **Do not proceed on assumption.**

---

## 2. Team Coordination Map

| Team | Role in this release | When to involve | How to reach |
|------|---------------------|-----------------|--------------|
| **Team 10** (you) | Primary implementer + orchestrator | All phases | — |
| **Infrastructure team** | Apply Alembic migrations you cannot touch | Any time A2 triage produces new aliases/rules that need a migration (migration 072+) | File request with SQL spec; wait for confirmation before running (**Note:** Nimrod has indicated Team 60 may own this role — pending formal registration; treat as Team 20 / infrastructure team until clarified) |
| **Team 100** | Architecture decisions, new product approvals, Pantry ADR sign-off | Escalation only — do not consult for routine work | File report in `_COMMUNICATION/TEAM_100/reports/` — tag `[USER ACTION REQUIRED]` if Nimrod must decide |
| **Team 50** | QA gate G-V1.1 validation | After completion report is filed; after Team 190 preflight passes | File `QA_REVIEW_REQUEST.md` in `_COMMUNICATION/TEAM_50/reports/` |
| **Team 190** | Constitutional preflight of completion package | After all phases complete; before Team 50 gate | File in `_COMMUNICATION/TEAM_190/` — see §7 |
| **Nimrod (Operator)** | Full pipeline runs on local machine; FTPS upload; WP blog page if REST unavailable | Phase B (ingestion run), Phase E (FTPS), A4 (WP page) | Tag `[USER ACTION REQUIRED]` in any report; Nimrod reads reports directly |

**Rule:** Every cross-team request produces a written artifact. Verbal/informal requests carry no binding obligation.

---

## 3. Decision Authority Boundaries

Before escalating, check whether Team 10 can decide autonomously:

| Decision | Team 10 autonomous | Must escalate |
|---|---|---|
| Add alias for existing product | ✅ Yes — per alias policy (global, confidence 0.90) | Only if source-scoped with ambiguity |
| Add scope-skip rule for clearly out-of-scope raw name | ✅ Yes — per CQ-P01 decision matrix (spec §A2) | If ambiguous — escalate to Team 100 |
| Fix source selector/config in `source_fetch_profiles` | ✅ Yes — A3 scope | Document before/after observation count |
| Deactivate a failing source | ✅ Yes — if no data in 30+ days and quick-fix failed | Document reason |
| Add normalizer rule (`normalizer_rules` table) | ✅ Yes — standard rules | None |
| Apply a migration file | ❌ No — Team 20 owns `db/versions/` | Always coordinate with Team 20 |
| Add a new product code | ❌ No — Team 100 approval required | Submit proposed code/name/category/unit |
| Modify tier ranges (PRD025/026/027 item counts or prices) | ❌ No — policy decision | Submit audit data to Team 100 |
| Change the `basket_tier_resolver.py` public API signature | ❌ No — spec §C4.2 is binding | Escalate to Team 100 if blockers arise |
| Modify `organic_market_agent/models/` or `db/` | ❌ No — Team 20 domain | Never touch |

---

## 4. Session-by-Session Execution Workflow

### Session 0 (start here — 30 min)

Before any code:

- [ ] Read `_COMMUNICATION/ROADMAP.md` — confirm v1.1.0 is the active cycle and G-V1.1 is pending
- [ ] Read this document in full
- [ ] Read the LOD400 spec (§0 code-vs-plan corrections first — there are 6 binding corrections to internalize)
- [ ] Read `docs/GLOSSARY.md` — canonical terminology for this codebase
- [ ] Verify `CHANGELOG.md` `[Unreleased]` is the active log section
- [ ] Start local environment: Docker (`docker-compose up -d`), admin server, confirm `DATABASE_URL` resolves

**Deliverable:** None. Proceed to Phase A only when all checklist items are confirmed.

---

### Session 1 — Phase A (parallel tasks A1–A4)

**All four A-tasks can run in the same session or across parallel sessions.**

#### A1 — DB Audits

Run both SQL audit queries from spec §A1:

```sql
-- Cherry guard (expected: 0 rows)
-- Note: DB column is `products.code` (not product_code).
SELECT pa.id, pa.alias_text, p.code AS product_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001'
  AND pa.is_active = TRUE
  AND (pa.alias_text ILIKE '%שרי%' OR pa.alias_text ILIKE '%cherry%' OR pa.alias_text ILIKE '%צ''רי%');

-- Basket code guard (expected: 0 rows)
SELECT pa.id, pa.alias_text, p.code AS product_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029')
  AND pa.is_active = TRUE;
```

**If 0 rows:** Document "clean audit" in completion report. No migration needed. ✓  
**If rows found:** Prepare SQL fix. → **Handoff to Team 20** (see §5.1).

#### A2 — Alias Backlog Clearance

Source: `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_EXCEPTIONS_REGISTER_TEAM10.md` — 92 names.

Classify each name using the decision matrix in spec §A2:

| Bucket | Action | Who |
|--------|--------|-----|
| (a) Maps to existing product | Prepare `INSERT INTO product_aliases` | → Team 20 migration 072 |
| (b) Scope-skip (clearly out of scope) | Prepare `INSERT INTO catalog_scope_skip_rules` | → Team 20 migration 072 |
| (c) New product needed | Escalate to Team 100 with proposed code/name/unit | → Team 100, WAIT for approval |
| (d) Invalid / noise | Mark as `ignored` in triage table, no action | Team 10 autonomous |

Collect all (a) and (b) SQL. → **Handoff to Team 20** for migration 072 (see §5.1). Do not run `alembic upgrade head` yourself.

#### A3 — M10.x Pragmatic Optimization

Time-boxed to one session. For each active source (SRC041–SRC070 mypips; SRC033–SRC036 CSA/retail):

1. Check last fetch run status in admin UI `/sources`
2. For stalled sources: attempt quick-fix (selector update, URL cache-bust, deactivation if no data in 30+ days)
3. Document each change: `source_code | before obs count | after obs count | action taken`

This is autonomous — no Team 20 or Team 100 involvement unless a schema change is needed.

#### A4 — WhatsApp Protocol + M9C Blog Placeholder

Create `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` with all 7 sections (spec §A4.2). Section 5 must include the `psql INSERT` example from spec §A4.3 verbatim.

For the WordPress blog draft: attempt WP REST API call (spec §A4.4 curl command). If Application Password is not configured:
- Document as **`[USER ACTION REQUIRED]`** in Phase A completion note
- Nimrod creates the page manually

**Phase A is complete when:** A1 audit documented, A2 triage table complete and migration 072 submitted to Team 20, A3 changes documented, A4 protocol document created.

---

### Handoff Point H1 — Team 20 Migration Request

After A1/A2 SQL is prepared, file a migration request:

**File:** `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_072_REQUEST_TEAM10.md`

Must include:
- Full SQL for each alias/scope-skip rule to insert
- Any fix-forward SQL from A1 (if drift was found)
- Confirmation that you have NOT run `alembic upgrade head` yet
- Request: "Please create migration 072, apply, and confirm `alembic current` = head"

**Wait for Team 20 confirmation before Phase B.**

---

### Session 2 — Phase B: Full Ingestion Run + PRD027 Confirmation

**Prerequisite:** Team 20 confirms `alembic current` = head (migration 072 applied).

**This phase requires Nimrod's local machine for the full ingestion run** — the production database and source credentials are on the operator's machine. Tag Nimrod in a report before starting.

**File:** `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_PHASE_B_REQUEST_TEAM10.md`  
Content: "Phase A complete. Migration 072 applied. Requesting Nimrod to run full pipeline (commands below). [USER ACTION REQUIRED]"

Include the exact commands from the mandate §Task 2:

```bash
alembic current
# All active sources: omit --source-code. Normalize after ingestion per CLI.
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_normalizer
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

After the run, verify PRD027 and product count. Record results. **Phase B is complete when published product count ≥ 77 and PRD027 appears ≤ 1 time.**

---

### Session 3 — Phase C (parallel tasks C1–C4)

**Prerequisite:** Phase B complete (post-ingestion metrics available).

C1–C4 are all parallel. C4 is the primary code deliverable. C1–C3 are audit/research tasks producing mandatory matrices for the completion report and QA gate.

#### C1 — Eggs Unit Audit (CQ-P03)

Build the source × unit matrix for PRD067 across all active sources. Classify each source: 12-pack → `egg_carton_12`, loose/unit → `unit`, 6-pack → `unit` (flag for Team 100 if `egg_carton_6` is needed). Add source-scoped `normalizer_rules` unit_map entries where needed. Target ≥ 90% correctly mapped.

#### C2 — Passion Fruit Disambiguation (CQ-P04)

Build the source × unit matrix for PRD072. For each active source: check `raw_unit_text`, inspect `raw_payload_json` if needed, classify as (a) genuine per-fruit (correct — keep `unit`) or (b) mislabeled kg (add source-scoped `normalizer_rules` override). Price heuristic: per-fruit = ₪3–8/unit; if ₪20–40 with `יחידה`, it is per-kg mislabeled. Policy binding: PRD072 default stays `kg`; override only where demonstrably wrong.

#### C3 — Blueberries Pack Research (CQ-P05)

Research-only — **no code change.** Build the `source × pack_description × grams_if_known × price_per_100g_calc` table for PRD086. Use `raw_product_name` regex `\d+\s*(?:גרם|gr|g)` to detect gram values; fall back to source website inspection or flag "requires Team 80 field research." Target ≥ 50% of sources with grams determined.

When C3 is complete: **file the notification report to Team 100** (`_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md`) with the full table. This triggers the Phase D Pantry ADR by Team 100 — you do not author the ADR.

#### C4 — basket_tier_resolver.py (CQ-P07)

Read spec §C4 in full before writing a single line. The **canonical API** (BINDING — do not deviate):

```python
def resolve_basket_tier(
    csa_context_json: Optional[str],   # JSON string from DB, NOT a dict
    price_amount: Optional[Decimal],   # Decimal — never float
    session: Session,
) -> tuple[Optional[str], str]:        # (product_code, resolution_note)
```

`basket_handler.py` modification: call `basket_tier_resolver.run(ctx, session)` AFTER nullifying `ctx.normalized_price_value = None`. Tests: `tests/test_basket_tier_resolver.py` with exactly the 8 named cases from spec §C4.8, all using `Decimal` for price arguments.

If tier ranges in the real CSA data don't match the spec's bands: **do not modify ranges autonomously** — file a report to Team 100 with the actual distribution and wait for sign-off.

---

### Session 4 — Phase D: C3 Delivery + Team 100 ADR trigger

**Prerequisite:** Phase C complete — specifically C3 blueberries research table.

**Team 10 action:** File the C3 notification report to Team 100:
```
_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md
```
Include: the completed C3 table, any pack-size patterns observed for PRD087–PRD100 (dry goods), confirmation that no code change was made.

**Team 100 action (D1):** Upon receipt of C3 notification, Team 100 independently authors the Pantry ADR at `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md`. Team 10 does NOT write the ADR. Team 10's Phase D is complete when the C3 notification report is filed.

**In the completion report:** Reference the D1 ADR path (or note "pending Team 100 authorship" if not yet filed).

---

### Session 5 — Phase E: Final Publish + Gate Evidence Package

**Prerequisite:** Phases A–D all complete.

Run the final pipeline, both privacy audit commands (Python + grep), and full test suite. Then tag Nimrod for FTPS upload.

Verify all E1 exit criteria from mandate §Task 5 before filing the completion report.

---

## 5. Cross-Team Handoff Protocols

### 5.1 Handing off to Team 20 (migrations)

1. Prepare the complete SQL for migration 072 (aliases, scope-skip rules, any drift fixes)
2. File `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_072_REQUEST_TEAM10.md`
3. Do NOT run `alembic upgrade head` yourself
4. Wait for Team 20 confirmation (report in `_COMMUNICATION/TEAM_20/reports/`)
5. Once confirmed, run `alembic current` to verify head, then proceed

**If Team 20 is unavailable:** escalate to Team 100 via `_COMMUNICATION/TEAM_100/reports/BLOCKED_...` report.

---

### 5.2 Requesting Nimrod (operator actions)

Tag `[USER ACTION REQUIRED]` in any report when:
- Full pipeline run is needed (Phase B, Phase E)
- FTPS upload is needed (Phase E)
- WP blog page creation if REST unavailable (Phase A4)
- Any production database operation on the operator machine

File the report first. Include exact commands for Nimrod to run. Nimrod will execute and reply — do not proceed past that step until confirmed.

---

### 5.3 Escalating to Team 100

File in `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_[TOPIC]_ESCALATION_TEAM10.md`.

Required when:
- A new product code is needed (bucket (c) in alias triage)
- Tier range data doesn't match spec
- Any deviation from the LOD400 spec is required
- Mandate and current code are incompatible in an unexpected way
- Blueberry pack-size findings ready for Pantry ADR sign-off (C3)

Include: exact finding, current code/data state, proposed resolution options, and which option you recommend.

---

### 5.4 Handing off to Team 190 (pre-QA preflight)

After all phases are complete and the completion report is drafted, submit to Team 190 before Team 50:

**File:** `_COMMUNICATION/TEAM_190/PREFLIGHT_REQUEST_V1_1_TEAM10.md`

Include:
- Link to completion report
- Link to mandate `MANDATE-20260408-V1-1-LOD400-EXEC`
- Link to LOD400 spec `SPEC-20260408-PHASE-A-LOD400`
- Summary of any deviations and their Team 100 approvals
- Confirmation that all 11 completion report items are present

Wait for Team 190 PASS before filing the Team 50 QA review request.

---

### 5.5 Requesting Team 50 QA Gate G-V1.1

Only after Team 190 PASS:

**File:** `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_V1_1_QA_REQUEST_TEAM10.md`  
Use template: `_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md`

Include mandate ID, completion report path, Team 190 PASS report path, and all evidence items from the verification checklist.

---

## 6. Artifacts Checklist

Track these as you go. The completion report cannot be filed until all are present.

### Phase A
- [ ] A1: SQL audit query output (0 rows confirmed or drift fix applied)
- [ ] A2: Full 92-name triage table (bucket a/b/c/d for each name)
- [ ] A2: Migration 072 SQL submitted to Team 20
- [ ] A3: Before/after observation count per optimized source
- [ ] A4: `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` (7 sections)
- [ ] A4: Blog page created or `[USER ACTION REQUIRED]` documented
- [ ] CHANGELOG: all A-phase changes under `[Unreleased]`

### Phase B
- [ ] B1: Full ingestion run output (source success/fail table)
- [ ] B1: PRD027 verification output (`count ≤ 1: PASS`)
- [ ] B1: Published product count ≥ 77 confirmed

### Phase C
- [ ] C1: Source × unit matrix for eggs (all active PRD067 sources, ≥ 90% correctly mapped)
- [ ] C2: Source × unit matrix for passion fruit (all active PRD072 sources, per-source classification)
- [ ] C3: Blueberries research table (source × pack_description × grams_if_known × price_per_100g_calc)
- [ ] C3 notification report to Team 100 filed (`_COMMUNICATION/TEAM_100/reports/...C3_BLUEBERRY_FINDINGS...`)
- [ ] C4: `organic_market_agent/normalizer/basket_tier_resolver.py` exists with canonical API signature
- [ ] C4: `organic_market_agent/normalizer/basket_handler.py` modified (calls tier resolver after price nullification)
- [ ] C4: `tests/test_basket_tier_resolver.py` — ≥ 8 named test cases, all PASS (all use `Decimal`)

### Phase D
- [ ] D1: Team 100 Pantry ADR path referenced in completion report (or "pending Team 100 authorship" noted)

### Phase D
- [ ] D1: Unit normalization summary report filed

### Phase E
- [ ] E1: `pytest tests/ -m "not upress"` — 0 failures
- [ ] E1: Published product count ≥ 77 (final)
- [ ] E1: Zero duplicate `product_id` in `public_report.json`
- [ ] E1: Python SRC audit — `Privacy check (SRC codes): PASS`
- [ ] E1: Shell grep — `grep -R -n -E 'SRC[0-9]{3}' output/public/` — empty output
- [ ] E1: PRD027 count ≤ 1
- [ ] E1: Cherry aliases on PRD001: 0 (re-run A1 SQL)
- [ ] E1: Active aliases on PRD028/PRD029: 0 (re-run A1 SQL)
- [ ] E1: FTPS upload confirmed in `manifest.json` (or documented reason)
- [ ] CHANGELOG: all changes under `[Unreleased]`, nothing under `[1.0.0]`

### Completion Package
- [ ] `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_COMPLETION_TEAM10.md` — all 11 required items
- [ ] Team 190 preflight request filed
- [ ] Team 190 PASS received
- [ ] `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_V1_1_QA_REQUEST_TEAM10.md` filed

---

## 7. Execution Flow Diagram

```
Session 0: Environment setup + spec read
     │
     ▼
Phase A (parallel) ─────────────────────────────────────────
A1: DB audits                     A3: Source optimization
A2: Alias triage (92 names)       A4: WhatsApp protocol + WP page
     │
     │  A2/A1 SQL ready → [H1] Handoff to Team 20 for migration 072
     │                    Wait for Team 20 confirmation
     │  A4 WP page needed → [USER ACTION REQUIRED] Nimrod
     ▼
Phase B ── [USER ACTION REQUIRED] Nimrod: full pipeline run
B1: Ingestion + normalize + aggregate + publish
     PRD027 confirmation ≤ 1
     Published products ≥ 77
     │
     ▼
Phase C (parallel) ─────────────────────────────────────────
C1: Egg unit semantics            C3: Blueberries research (→ Team 100 D1)
C2: Passion fruit disambiguation  C4: basket_tier_resolver.py (NEW)
     │
     │  C3 complete → [H3] File C3 notification to Team 100 (triggers D1 Pantry ADR)
     │  C4 tier ranges mismatch → [H3] Escalate to Team 100
     ▼
Phase D
D1: Unit normalization summary report
     │
     ▼
Phase E ── [USER ACTION REQUIRED] Nimrod: FTPS upload
E1: Final pipeline + privacy audit + full test suite
     │
     ▼
Completion Report (11 required items)
     │
     ▼
[H4] Team 190 preflight request → PASS
     │
     ▼
[H5] Team 50 QA Review Request → G-V1.1 gate
```

---

## 8. Session Startup Checklist (every session)

Run this before writing any code:

- [ ] Pull latest from repo — confirm no pending changes from another session
- [ ] `docker-compose up -d` — confirm `oma-g2-ev` is running
- [ ] `alembic current` — confirm migration head matches expected state
- [ ] Check `_COMMUNICATION/TEAM_20/reports/` for any pending migration confirmations
- [ ] Check `_COMMUNICATION/TEAM_100/reports/` for any approval responses (new products, tier ranges)
- [ ] Check `CHANGELOG.md [Unreleased]` — log what you're about to do before you start (not after)
- [ ] Re-read the relevant LOD400 spec section for today's task

---

## 9. Escalation Quick Reference

| Situation | File at | Prefix | Tag |
|-----------|---------|--------|-----|
| New product needed | `_COMMUNICATION/TEAM_100/reports/` | `YYYY-MM-DD_NEW_PRODUCT_REQUEST_` | — |
| Tier range mismatch | `_COMMUNICATION/TEAM_100/reports/` | `YYYY-MM-DD_TIER_RANGE_ESCALATION_` | — |
| Migration needed | `_COMMUNICATION/TEAM_20/reports/` | `YYYY-MM-DD_MIGRATION_REQUEST_` | — |
| Spec/code conflict | `_COMMUNICATION/TEAM_100/reports/` | `YYYY-MM-DD_DELTA_REPORT_` | — |
| Blocked — needs Nimrod | `_COMMUNICATION/TEAM_10/reports/` | `BLOCKED_` | `[USER ACTION REQUIRED]` |
| Phase complete, need Nimrod run | `_COMMUNICATION/TEAM_10/reports/` | `YYYY-MM-DD_V1_1_PHASE_[X]_READY_` | `[USER ACTION REQUIRED]` |
| Blueberry findings for ADR | `_COMMUNICATION/TEAM_100/reports/` | `YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_` | — |

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-08*  
*Constitutional clearance: Team 190 (2026-04-08) — SPEC-20260408-PHASE-A-LOD400 PASS*
