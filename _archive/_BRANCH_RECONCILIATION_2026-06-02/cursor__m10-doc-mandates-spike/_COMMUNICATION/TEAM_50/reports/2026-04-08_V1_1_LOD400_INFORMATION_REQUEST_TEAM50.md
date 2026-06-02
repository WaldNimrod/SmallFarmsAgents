---
document_type: QA_INFORMATION_REQUEST
version: "1.0"
---

# Team 50 — Information Completion Request (v1.1.0 / LOD400 / G-V1.1)

**Request ID:** QA-INFO-REQ-20260408-V1-1-LOD400  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture), Team 10 (Feature Dev — orchestration)  
**CC:** Team 190 (Constitutional preflight), Team 20 (Infrastructure), Nimrod (project lead)  
**Date:** 2026-04-08  
**Mode:** **Readiness / documentation only** — no test execution in this phase per project direction  

---

## 1. Team 50 role (refresher)

Per `_COMMUNICATION/.cursor/rules/team-roles.mdc` and project context:

- **Team 50 validates** implementation against the **binding spec and QA mandate**; **does not** write production code.
- **Gate decisions** are binding only when filed using `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md` after **executable** evidence.
- **Workflow:** Team 10 completion report → **Team 190 preflight PASS** → Team 50 `QA_REVIEW_REQUEST` → execute `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` → findings report.
- **Language:** All inter-team documents in **English**; terminology from [`docs/GLOSSARY.md`](docs/GLOSSARY.md).

**End goal for this program slice:** Close **Gate G-V1.1** on catalog quality, M10.x pragmatic work, M9C protocol/placeholder, post-LOD400 pipeline evidence — with **zero privacy regressions** and **aligned numeric/documentation criteria**.

**Full scope (study set):**

| Document | Role for Team 50 |
|----------|------------------|
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Canonical terms for reports and evidence |
| [`_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`](_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md) | **Primary implementation precision** (Phases A–E, SQL, exit criteria) |
| [`_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md`](_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md) | **Execution order**; must not contradict spec |
| [`_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md`](_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md) | Coordination, handoffs, artifact checklist |
| [`_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md`](_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md) | **Tests T01–T16** Team 50 will run after preflight |

---

## 2. Conflicts and ambiguities — **binding clarification required**

Team 50 cannot execute G-V1.1 with a single unambiguous criteria set until the following are **resolved in writing** (Team 100 preferred).

### 2.1 Hierarchy vs QA mandate scope statement

- **LOD400 spec** and **MANDATE-20260408-V1-1-LOD400-EXEC** state the spec supersedes the older consolidated mandate at LOD400 detail.
- **`QA_MANDATE_G_V1_1.md` §1** still lists scope as `MANDATE_V1_1_CONSOLIDATED_TEAM10.md` only.

**Request:** Issue **QA_MANDATE_G_V1_1.md v1.1** (or addendum) that explicitly binds Team 50 to **SPEC-20260408-PHASE-A-LOD400** + **MANDATE-20260408-V1-1-LOD400-EXEC**, and lists any **T01–T16** deltas if tests change.

### 2.2 Phase C task mapping: spec vs execution mandate

| Topic | LOD400 spec | MANDATE_V1_1_LOD400_EXEC Task 3 |
|-------|-------------|----------------------------------|
| C2 | Passion fruit (PRD072) disambiguation | **Basket alias remapping** |
| C3 | Blueberries research (PRD086) | **Pantry ADR** (document by Team 10) |
| C4 | `basket_tier_resolver` + tests | Same (resolver) |
| Pantry ADR | **Phase D1 — Team 100** authors ADR | Mandate says Team 10 creates C3 ADR |

**Request:** Single **authoritative mapping** (e.g. “Mandate Task 3 bullets renumbered to match spec C1–C4 and D1”) or **ARCH_DECISION** that states which document wins per item. Without this, Team 50 cannot know which completion-report sections are **mandatory** for T08–T12.

### 2.3 `basket_tier_resolver` public API

- **Spec §C4.2** embeds a large module: `resolve_basket_tier(csa_context_json: Optional[str], price_amount: Optional[Decimal], session) -> tuple[Optional[str], str]` and a `run(ctx, session)` entry point.
- **Mandate §Task 3** shows a **different** signature: `csa_context_json: dict | None`, `price_amount: float | None`, returns `str | None`.

**Request:** One **canonical signature** and return shape (for import in tests and `basket_handler`). Team 50 will assert **code matches the signed spec**, not an intermediate draft.

### 2.4 PRD027 publish criterion (T05)

- **`QA_MANDATE_G_V1_1` T05:** “Exactly 1 row … (or documented intentional with Team 100 sign-off)”.
- **LOD400 §B1.5 / §B1.6:** PRD027 may appear **0 or 1** times (0 = below publish threshold).

**Request:** Confirm T05 pass rule: **≤ 1** always sufficient, or **exactly 1** required when product is in catalog with sufficient sources.

### 2.5 Phase B / E CLI — single command path

At least three patterns appear across spec and handoff:

- Spec §B1.3: `python -m organic_market_agent scheduler.run_ingestion --run-type manual --normalize`
- Mandate Task 2: `scheduler.run_ingestion --run-type manual --all-sources` then `run_normalizer`, `run_aggregator`, `run_publisher`
- Handoff Session 2: `run_ingestion --run-type manual --normalize` (module path may differ)

**Request:** One **copy-paste block** labeled “canonical Phase B operator run” and one for **Phase E**, verified against **actual** `python -m organic_market_agent` entrypoints in repo.

### 2.6 A4 example SQL — `sources` column name

- LOD400 §A4.3 example uses `WHERE s.source_code = 'SRC_WA'`.
- ORM [`organic_market_agent/models/sources.py`](organic_market_agent/models/sources.py) exposes `Source.code`, not `source_code`.

**Request:** Correct the spec/mandate example to `s.code = 'SRC_WA'` (or document the real column if different in DB). Team 50 will treat **protocol doc + migration reality** as the test target for T13 once filed.

### 2.7 `catalog_scope_skip_rules` migration template

- Spec §A2 Step 3 uses `ON CONFLICT DO NOTHING` on `catalog_scope_skip_rules` without defining a **unique constraint** in the snippet.

**Request:** Team 20 / Team 100: confirm **idempotent insert pattern** for scope-skip rows (constraint name or alternative pattern) so migrations are reviewable.

### 2.8 T06/T07 vs E1 re-audit SQL

- **QA mandate** T06/T07 use `COUNT(*)`-style checks.
- **Mandate §4 verification** uses a grouped `SELECT` on PRD001/PRD028/PRD029.

**Request:** State whether **E1** must re-run **full A1 seven-query suite** from LOD400 §A1 or only the **QA mandate** SQL. Team 50 will script what Team 100 designates.

---

## 3. Information Team 10 should preload before QA request

To avoid BLOCKED cycles when Team 50 runs T08–T14:

| Item | Why Team 50 needs it |
|------|----------------------|
| Path to **92-name triage table** (A2) | Evidence for T02/T03 causality |
| **Before/after** `catalog_scan_collect_metrics.py` JSON paths | Baseline vs post-CQ-P01 |
| **Phase B** ingestion run row + source success/fail table | T16 traceability |
| **C1/C2/C3** matrices per **resolved** spec mapping | T08–T10 |
| **Team 100 Pantry ADR** final path (`ADR_PACK_WEIGHT_COMPARISON` per spec D1) | T12 |
| **WhatsApp protocol** path + blog placeholder status (WP REST vs Nimrod manual) | T13–T14 |
| **Team 190 preflight report** path + PASS id | QA precondition per `QA_MANDATE_G_V1_1` §5 |

---

## 4. What Team 50 will **not** do until clarifications land

- No G-V1.1 **PASS/FAIL** decision.
- No substitute for **Team 190** preflight.
- No re-interpretation of **LOD200** policy (ARCH-20260406-CQ-MASTER) when LOD400 explicitly corrects implementation detail — Team 100 must state precedence in one place.

---

## 5. Requested responses (checklist for Team 100 / Team 10)

- [ ] **QA_MANDATE_G_V1_1** updated or addendum issued (scope + any T01–T16 changes).
- [ ] **Phase C / D ownership** table signed (spec vs mandate alignment).
- [ ] **`basket_tier_resolver` canonical API** declared.
- [ ] **PRD027 T05** rule finalized (0 vs 1 appearance).
- [ ] **Canonical CLI** blocks for Phase B and Phase E.
- [ ] **A4 SQL** column fix for `sources.code`.
- [ ] **A2 migration** idempotency note for scope-skip inserts.
- [ ] **E1 SQL** scope: full A1 suite vs QA-only checks.

Reply may be a single **ARCH_DECISION** or an amended **LOD400 errata** section; Team 50 will attach that path to the future `QA_REVIEW_REQUEST` execution record.

---

*Filed by: Team 50 (QA)*  
*Next action (after responses): await Team 10 completion package + Team 190 PASS + formal `QA_REVIEW_REQUEST`, then execute `QA_MANDATE_G_V1_1.md`.*
