---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — Team 50 Clarifications: v1.1.0 LOD400 / G-V1.1

**Decision ID:** ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1  
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA), Team 10 (Feature Dev), Team 190 (Constitutional preflight)  
**CC:** Nimrod (project lead)  
**Date:** 2026-04-08  
**Type:** CLARIFICATION  

---

## 1. Context

Team 50 filed information request `QA-INFO-REQ-20260408-V1-1-LOD400` at:
```
_COMMUNICATION/TEAM_50/reports/2026-04-08_V1_1_LOD400_INFORMATION_REQUEST_TEAM50.md
```

Eight clarifications were required before Team 50 could execute G-V1.1. Simultaneously, Team 100 completed a cross-document review and identified three additional errors in the execution mandate (MANDATE-20260408-V1-1-LOD400-EXEC) and handoff (HANDOFF-20260408-V1-1-ORCH-TEAM10). Those have already been corrected in-place (see §3 Amendments). All eight Team 50 requests are resolved here.

**References:**
- `_COMMUNICATION/TEAM_50/reports/2026-04-08_V1_1_LOD400_INFORMATION_REQUEST_TEAM50.md` — triggering request
- `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` — primary binding spec
- `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` — execution mandate (amended)
- `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` — orchestration handoff (amended)
- `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` — QA mandate (amended to v1.1)

---

## 2. Findings

| Item | Finding | Severity |
|------|---------|----------|
| 2.1 QA mandate scope | `QA_MANDATE_G_V1_1.md` referenced only the consolidated mandate; LOD400 spec and EXEC mandate were not listed | High |
| 2.2 Phase C/D task mapping | Mandate Task 3 listed C2=Basket Alias Remapping and C3=Pantry ADR, contradicting the LOD400 spec (C2=Passion Fruit, C3=Blueberries, D1=Pantry ADR by Team 100) | Critical |
| 2.3 `basket_tier_resolver` API signature | Mandate showed `dict | None` / `float | None` / `str | None`; spec shows `str | None` / `Decimal | None` / `tuple[str | None, str]` | High |
| 2.4 PRD027 T05 rule | QA mandate said "Exactly 1 row"; LOD400 spec permits 0 or 1 (0 = below publish threshold) | High |
| 2.5 Phase B/E CLI commands | Mandate used nonexistent `--all-sources` flag and wrong module path `scheduler.run_ingestion` | High |
| 2.6 A4 SQL column name | LOD400 spec §A4.3 used `s.source_code`; ORM model defines `Source.code` (column: `code`) | Medium |
| 2.7 scope-skip migration idempotency | Spec §A2 used `ON CONFLICT DO NOTHING` without naming the backing constraint | Medium |
| 2.8 E1 SQL scope | Ambiguity: does E1 run the full A1 seven-query suite or only QA mandate checks? | Medium |

---

## 3. Decision

### 3.1 — QA Mandate Scope (Team 50 request 2.1)

**RESOLVED.** `QA_MANDATE_G_V1_1.md` has been updated to **v1.1** (2026-04-08). It now explicitly states:
- Primary binding spec: `SPEC-20260408-PHASE-A-LOD400`
- Execution order: `MANDATE-20260408-V1-1-LOD400-EXEC`
- Coordination: `HANDOFF-20260408-V1-1-ORCH-TEAM10`
- LOD400 governs over consolidated mandate at implementation detail

T01–T16 test content is unchanged. T05 criterion is updated (see §3.4).

---

### 3.2 — Phase C/D Authoritative Mapping (Team 50 request 2.2)

**RESOLVED. The LOD400 spec is the single source of truth.** The mandate (Task 3) and handoff (Sessions 3/4) have been corrected in-place. The authoritative mapping is:

| Phase | Task | Description | Owner |
|-------|------|-------------|-------|
| C1 | CQ-P03 | Egg unit semantics audit — source × unit matrix for PRD067 | Team 10 |
| C2 | CQ-P04 | Passion fruit disambiguation — source × unit matrix for PRD072 | Team 10 |
| C3 | CQ-P05 | Blueberries pack research — `source × pack_description × grams_if_known` table for PRD086 | Team 10 |
| C4 | CQ-P07 | `basket_tier_resolver.py` — new file + `basket_handler.py` modification + ≥ 8 tests | Team 10 |
| D1 | CQ-P06 | Pantry ADR (`ADR_PACK_WEIGHT_COMPARISON`) — authored **by Team 100**, triggered by C3 notification | **Team 100** |

**Team 10 completion report requirement for Phase D:** File `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md` and cross-reference D1 ADR path (or note "pending Team 100 authorship" if ADR not yet filed).

The concepts "Basket Alias Remapping" and "Unit Summary Report" **do not exist** in the LOD400 spec. They are removed from all documents. Basket alias correctness is a by-product of C4's `basket_tier_resolver` integration — no separate audit task.

---

### 3.3 — `basket_tier_resolver` Canonical API (Team 50 request 2.3)

**RESOLVED.** The LOD400 spec §C4.2 is the binding API. The mandate has been corrected. The canonical signature (Team 50 will assert against this exactly):

```python
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

def resolve_basket_tier(
    csa_context_json: Optional[str],   # JSON string from DB — NOT a dict
    price_amount: Optional[Decimal],   # Decimal — NEVER float (money rule)
    session: Session,
) -> tuple[Optional[str], str]:
    """
    Returns (product_code, resolution_note).
    product_code: 'PRD025' | 'PRD026' | 'PRD027' | None
    resolution_note: 'basket_tier_by_item_count' | 'basket_tier_by_price' |
                     'basket_tier_default_medium' | 'basket_too_small' |
                     'basket_tier_oversized_default_large'
    """
```

Tests must use `Decimal("120")` etc. — never `120.0` or `float`. Any deviation from this signature is a T11 FAIL.

---

### 3.4 — PRD027 T05 Pass Rule (Team 50 request 2.4)

**RESOLVED.** The correct rule is **≤ 1**. `QA_MANDATE_G_V1_1.md` T05 has been updated:

> **≤ 1 entry for PRD027** (0 = below publish threshold: PASS with note; 1 = confirmed: PASS; 2+ = FAIL)

Rationale: PRD027 (large basket) is published only when ≥ 2 distinct sources provide large-basket observations in the current window. Zero is a valid outcome if no large CSA baskets were observed. "Exactly 1" was an error — it would fail a legitimate sparse-data run.

---

### 3.5 — Canonical CLI Blocks (Team 50 request 2.5)

**RESOLVED.** The actual entrypoints are defined in `organic_market_agent/__main__.py`. The mandate has been corrected. Copy-paste these exactly:

**Canonical Phase B operator run:**
```bash
# Prerequisite: alembic current (confirm head)
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

**Canonical Phase E final run (with FTPS upload):**
```bash
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher --upload
```

**Notes for Team 50:**
- `run_ingestion --normalize` runs ingestion + normalizer in one pass (via the `--normalize` flag) — this is the correct single-call pattern.
- `--all-sources` **does not exist** in the CLI — omitting `--source-code` runs all active sources by default.
- `scheduler.run_ingestion` **does not exist** — the command is `run_ingestion` at top-level.
- `run_normalizer`, `run_aggregator`, `run_publisher` are valid standalone commands for re-run scenarios.

---

### 3.6 — A4 SQL Column Name (Team 50 request 2.6)

**RESOLVED.** The `sources` ORM model (`organic_market_agent/models/sources.py` line 48) defines:
```python
code: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, unique=True)
```

The correct SQL filter is `WHERE s.code = 'SRC_WA'` — **not** `source_code`. The LOD400 spec §A4.3 must be treated as having this correction. Team 50's T13 evidence will use `s.code`.

**Note on spec errata:** The LOD400 spec §A4.3 uses `source_code` in the example `INSERT`/`SELECT` queries. Treat this as a documentation error — the DB column is `code`. Team 10 must use `s.code` in all actual SQL. This errata will be noted in the next spec revision cycle.

---

### 3.7 — scope-skip Migration Idempotency (Team 50 request 2.7)

**RESOLVED.** The unique constraint backing `ON CONFLICT DO NOTHING` for `catalog_scope_skip_rules` is:
```
uq_catalog_scope_skip_rules_display_order  (column: display_order)
```
Defined in migration `024_catalog_scope_skip_rules.py`:
```python
sa.UniqueConstraint("display_order", name="uq_catalog_scope_skip_rules_display_order")
```

Therefore the correct migration pattern for all scope-skip seed inserts is:
```sql
INSERT INTO catalog_scope_skip_rules (..., display_order, ...)
VALUES (...)
ON CONFLICT (display_order) DO NOTHING
```
This is idempotent and safe for re-runs. The spec §A2 Step 3 implies this pattern; the backing constraint name is `uq_catalog_scope_skip_rules_display_order`.

**Note on Team 60 / infrastructure migrations:** Nimrod has indicated that Team 60 may own infrastructure/migrations in the organization. **Team 60 is not yet registered in project documentation** (ROADMAP, project-context, team-roles). Until formally registered, all migration requests are directed to the infrastructure team as currently documented (Team 20). Team 100 will flag this for Nimrod to formalize.

---

### 3.8 — E1 SQL Scope (Team 50 request 2.8)

**RESOLVED.** The two sets of SQL checks serve different purposes and are **complementary, not competing**:

| Who runs it | When | What |
|-------------|------|------|
| **Team 10** (Phase E) | Before filing completion report | Full A1 seven-query suite from LOD400 §A1 — comprehensive audit, results pasted in completion report |
| **Team 50** (G-V1.1) | When executing QA mandate | T06/T07 `COUNT(*)` checks from `QA_MANDATE_G_V1_1.md` — targeted validation of spec-defined criteria |

Team 10's E1 output (full A1 suite) is attached to the completion report. Team 50 scripts and runs the QA mandate checks independently. Team 50 does **not** need to re-run Team 10's full A1 suite — T06/T07 are the QA gate criteria. Team 10's A1 suite is supporting evidence.

---

## 4. Amendments Issued

| Amendment ID | Target Document | Change |
|-------------|----------------|--------|
| AMD-01 | `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` | Task 3: C2→Passion Fruit, C3→Blueberries, C4 API corrected; Task 4: replaced "Unit Summary Report" with C3→D1 handoff; CLI Phase B fixed; completion report items 6/7 added |
| AMD-02 | `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` | Sessions 3/4 rewritten: C1–C4 fully described, D1 ADR ownership clarified, artifacts checklist corrected, flow diagram updated |
| AMD-03 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` | Updated to v1.1: LOD400 spec + EXEC mandate added to scope, T05 changed to "≤ 1", T12 updated to note Team 100 authorship |

---

## 5. Information Team 10 Must Preload for QA Request

Per Team 50's §3, Team 10 must attach the following to the `QA_REVIEW_REQUEST`:

| Item | Path / format | Needed for |
|------|--------------|-----------|
| `catalog_scan_collect_metrics.py` JSON — before and after | `data/normalizer_baseline_before.json` + `data/normalizer_baseline_after.json` | T01/T02 baseline |
| A2 triage table (92 names classified) | In completion report body | T02/T03 |
| Phase B ingestion run row + source success/fail table | Completion report §Phase B | T16 |
| C1 source × unit matrix (eggs / PRD067) | Completion report §Phase C | T08 |
| C2 source × unit matrix (passion fruit / PRD072) | Completion report §Phase C | T09 |
| C3 blueberries research table | Completion report §Phase C | T10 |
| D1 Pantry ADR path (Team 100-authored) | Completion report §Phase D cross-ref | T12 |
| M9C WhatsApp protocol document path | `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` | T13 |
| M9C blog placeholder status (WP REST PASS or Nimrod manual action documented) | Completion report §Phase A4 | T14 |
| Team 190 preflight PASS report path | Required precondition per §5 of QA mandate | Gate precondition |

---

## 6. Next Steps

| Team | Action | When |
|------|--------|------|
| Team 50 | Acknowledge receipt of this ARCH_DECISION; attach path to future `QA_REVIEW_REQUEST` | Before G-V1.1 execution |
| Team 10 | Read amended mandate + handoff; begin Phase A (Pre-work + A1–A4) | Immediately |
| Team 10 | File C3 notification to Team 100 upon completing blueberries research | During Session 4 |
| Team 100 | Author D1 Pantry ADR upon receipt of C3 notification from Team 10 | Within session of C3 delivery |
| Team 100 | Clarify Team 60 registration with Nimrod and update ROADMAP + team-roles accordingly | Before next sprint |
| Nimrod | Confirm Team 60 existence and registration (or confirm Team 20 retains migrations) | At next available opportunity |

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-08*  
*This decision is binding on all teams unless overridden by Nimrod.*
