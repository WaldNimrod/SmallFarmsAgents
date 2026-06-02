---
document_type: TEAM_BRIEFING
version: "1.0"
---

# Team 10 — Comprehensive Update: v1.1.0 Package Ready for Execution

**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev — primary executor and orchestrator)  
**Date:** 2026-04-08  
**Subject:** All pre-implementation corrections complete — package cleared for execution  

---

## 1. Overview

Multiple rounds of cross-team review (Team 50 pre-flight, Team 20 infrastructure review) identified errors in the mandate, handoff, and LOD400 spec. **All have been corrected.** You are now cleared to begin Phase A.

This document tells you exactly what changed and what to do first.

**Do not use any earlier versions of the mandate or handoff.** The live corrected files are your only reference.

---

## 2. Canonical document set — read these in this order

| Priority | Document | What it governs |
|----------|----------|----------------|
| 1 | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` | Implementation precision — supersedes mandate at detail level |
| 2 | `_COMMUNICATION/TEAM_10/MANDATE_V1_1_LOD400_EXEC_TEAM10.md` | Task order and acceptance criteria (amended) |
| 3 | `_COMMUNICATION/TEAM_10/HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` | Coordination, handoff protocols, artifacts checklist (amended) |
| 4 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` | What Team 50 will test — align your completion report to this (v1.1) |

---

## 3. Every change made since you last had the package

### 3.1 Mandate — `MANDATE_V1_1_LOD400_EXEC_TEAM10.md`

| Section | What changed | Why |
|---------|-------------|-----|
| **Task 3 — Phase C title** | Renamed to "Egg Semantics, Passion Fruit, Blueberries, basket_tier_resolver" | Correct name per LOD400 spec |
| **Task 3 — C2** | Was "Basket Alias Remapping" → now **"Passion Fruit Disambiguation (CQ-P04)"** | C2 in spec is PRD072, not basket aliases |
| **Task 3 — C3** | Was "Pantry ADR" → now **"Blueberries Pack Research (CQ-P05)"** | C3 in spec is PRD086 research, not the ADR |
| **Task 3 — C4 API signature** | Was `dict\|None` / `float\|None` / `str\|None` → now `Optional[str]` / `Optional[Decimal]` / `tuple[Optional[str], str]` | Canonical API — must match exactly |
| **Task 4 — entire section** | Replaced "Unit Summary Report" (no spec authority) → **"C3 Delivery to Team 100 (triggers D1 Pantry ADR)"** | Pantry ADR is Team 100's deliverable, not Team 10's |
| **Task 2 — Phase B CLI** | Removed nonexistent `--all-sources` flag; fixed module path | Actual CLI is `run_ingestion --run-type manual --normalize` |
| **Completion report items** | 11 items → 13 items: added item 4 (C2 passion fruit matrix), item 5 (C3 blueberries table); item 8 corrected from "Pantry ADR (C3)" to "D1 ADR path (Team 100-authored)" | Matches LOD400 spec exit criteria |
| **§3 Out of Scope** | "Team 20" → "infrastructure team" | Team 60 registration pending (see §6 below) |

### 3.2 Handoff — `HANDOFF_V1_1_ORCHESTRATION_TEAM10.md`

| Section | What changed |
|---------|-------------|
| **Session 3 — Phase C** | Completely rewritten: C1 (eggs), C2 (passion fruit), C3 (blueberries), C4 (basket_tier_resolver) — all four tasks now fully described with policy and acceptance guidance |
| **Session 4 — Phase D** | Replaced "Unit Summary Report" → "C3 Delivery + Team 100 ADR trigger" with clear step-by-step handoff protocol |
| **C4 API in Session 3** | Updated to canonical signature (`Optional[str]` / `Optional[Decimal]` / `tuple`) with note about `Decimal` in tests |
| **Team coordination map** | "Team 20" → "Infrastructure team (Team 60 pending formal registration)" |
| **Artifacts checklist — Phase C** | C2: passion fruit matrix; C3: blueberries table + notification report to Team 100; C4: canonical API + `Decimal` in tests |
| **Artifacts checklist — Phase D** | D1 ADR path (Team 100-authored) |
| **Execution flow diagram** | C2 → passion fruit, C3 → blueberries (→ Team 100 D1), diagram labels corrected |

### 3.3 LOD400 spec — `2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`

| Errata ID | Location | What was corrected |
|-----------|----------|--------------------|
| ERR-01 | §A2.3 scope_skip migration template | `rule_pattern` → `pattern`; added `display_order` + `category_code` (both required); `ON CONFLICT (display_order) DO NOTHING` |
| ERR-02 | §A2.3 product_aliases migration template | `confidence_score` → `confidence`; removed `updated_at` (does not exist); `ON CONFLICT (alias_text_normalized, source_id) DO NOTHING` |
| ERR-03 | §A4.3 psql example | Wrong column names (`raw_name`, `raw_price`, `raw_unit`, `raw_text`, `source_id`) → correct names with 4-step FK chain |
| ERR-04 | §A4.3 `pending_manual` status | Added note: `pending_manual` requires migration 073 to extend CHECK constraint |
| ERR-05 | Header reference | Errata table added for audit trail |

**The corrected templates are the only versions you should copy from.** Do not use any earlier printed/cached version.

---

## 4. New scope item: migration 073 required for Phase A4

This was not in the original plan. When you draft the WhatsApp protocol (`WHATSAPP_DATA_SUBMISSION_PROTOCOL.md`) in Phase A4, you must also **file an H1 migration request** for Team 20 to create migration 073:

**Migration 073 contains:**
1. `SRC_WA` source row seed in `sources` table
2. ALTER TABLE to extend `chk_rei_extraction_status` CHECK constraint to include `'pending_manual'`

**Your H1 request for 073:**
```
_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_073_REQUEST_TEAM10.md
```
Include: the SRC_WA row spec and confirmation you have not run `alembic upgrade head`.

**Migration numbering:**

| Migration | Purpose | You file H1 when... |
|-----------|---------|---------------------|
| 072 | CQ-P01 alias batch + scope-skip rules (A2) | A2 triage complete |
| 073 | SRC_WA seed + `pending_manual` CHECK extension | A4 protocol document drafted |
| 074 | (Optional) A1 drift fix | A1 SQL audit shows drift |

---

## 5. Phase C task reference — the authoritative mapping

Read this table carefully. The original mandate had C2 and C3 wrong. This is what you implement:

| Task | CQ Package | Product | Owner | Output |
|------|-----------|---------|-------|--------|
| **C1** | CQ-P03 | PRD067 (eggs) | Team 10 | Source × unit matrix — ≥ 90% correctly mapped |
| **C2** | CQ-P04 | PRD072 (passion fruit) | Team 10 | Source × unit matrix — per-source classification (genuine vs mislabeled) |
| **C3** | CQ-P05 | PRD086 (blueberries) | Team 10 | Research table: `source × pack_description × grams_if_known × price_per_100g_calc` |
| **C4** | CQ-P07 | baskets | Team 10 | `basket_tier_resolver.py` + `basket_handler.py` modification + ≥ 8 tests |
| **D1** | CQ-P06 | pantry dry goods | **Team 100** | Pantry ADR — authored by Team 100 after C3 notification |

**"Basket Alias Remapping" and "Unit Summary Report" do not exist.** They were removed. Do not implement them.

---

## 6. `basket_tier_resolver` canonical API — implement this exactly

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
    resolution_note: basket_tier_by_item_count | basket_tier_by_price |
                     basket_tier_default_medium | basket_too_small |
                     basket_tier_oversized_default_large
    """
```

**Tests MUST use `Decimal` for price arguments** — `Decimal("120")`, never `120.0`. Team 50 will assert this.

---

## 7. Phase D — how to notify Team 100 (triggers D1 Pantry ADR)

When C3 research table is complete, file a notification report:

```
_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md
```

Include:
1. The completed C3 blueberries research table
2. Any pack-size patterns noticed for PRD087–PRD100 dry goods
3. Explicit statement: "No code change made in C3"

After you file this, Team 100 independently authors the D1 Pantry ADR. **You do not write the ADR.**  
In your completion report: reference the D1 ADR path, or note "pending Team 100 authorship" if not yet filed.

---

## 8. H1 protocol reminder — you file, Team 20 authors

**You must NOT run `alembic upgrade head` yourself for v1.1 migrations.**

For each migration:
1. File the H1 request in `_COMMUNICATION/TEAM_20/reports/`
2. Wait for Team 20 confirmation before proceeding
3. Then run downstream pipeline steps

---

## 9. Canonical Phase B and Phase E CLI blocks

Use these exactly — no variants:

```bash
# Phase B — full ingestion run
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher

# Phase E — final run with FTPS upload
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher --upload
```

`--all-sources` and `scheduler.run_ingestion` do not exist. Both commands above supersede any earlier version.

---

## 10. Completion report checklist (13 required items)

Your completion report (`_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_COMPLETION_TEAM10.md`) must include all 13 items:

1. Before/after metrics table (`catalog_scan_collect_metrics.py` output)
2. A2 triage table — all 92 names classified
3. C1 source × unit matrix (eggs / PRD067) — all active sources, ≥ 90% correctly mapped
4. C2 source × unit matrix (passion fruit / PRD072) — per-source classification
5. C3 blueberries research table — `source × pack_description × grams_if_known × price_per_100g_calc`
6. PRD027 confirmation evidence — product count + uniqueness check (≤ 1)
7. `basket_tier_resolver.py` test output — ≥ 8 named cases, all PASS (all use `Decimal`)
8. D1 Pantry ADR path (Team 100-authored) — or "pending Team 100 authorship" with C3 notification path
9. Privacy audit output — Python + grep both PASS
10. Final `pytest` output — test count, pass/fail
11. FTPS upload confirmation — manifest entry or documented failure
12. Full CHANGELOG diff under `[Unreleased]`
13. Any escalated blockers and their resolution status

---

## 11. Session startup checklist (every session)

Before starting any work session on v1.1.0:

```bash
# 1. Confirm migration head
alembic current

# 2. Confirm tests pass baseline
pytest tests/ -m "not upress" -q

# 3. Review what phase you are in (Pre-work → A → B → C → D → E)
```

Read the mandate Task you are currently working on before writing code.  
If you're unsure about a decision → check LOD400 spec first. If spec doesn't cover it → escalate to Team 100 (do not invent).

---

## 12. Escalation quick reference

| Situation | Action |
|-----------|--------|
| A2 triage: name maps to product not in catalog | File to Team 100 with proposed code/name/category/unit — WAIT for approval |
| A2 triage: ambiguous mapping | File to Team 100 with evidence — WAIT |
| C4 tier ranges in real CSA data don't match spec bands | File to Team 100 with actual distribution — WAIT |
| Migration needed → alembic step | File H1 to Team 20 — do NOT run alembic yourself |
| Any change contradicts LOD400 spec | STOP. Escalate to Team 100 with specific contradiction |
| Blocker requiring Nimrod decision | File with `[USER ACTION REQUIRED]` heading |

---

## 13. Starting now — Phase A first steps

**Your immediate next actions:**

1. **Pre-work:** Update CHANGELOG, confirm `alembic current` at `071`, run full test suite baseline
2. **A1:** Run the cherry/basket SQL audit queries from LOD400 spec §A1. If drift found → file H1 to Team 20 for migration 074. If no drift → proceed to A2.
3. **A2:** Run `python scripts/catalog_scan_collect_metrics.py` to capture baseline. Then pull all 92 unresolvable names from DB (spec §A2 SQL). Triage each name into bucket (a)/(b)/(c)/(d). File H1 to Team 20 with alias/scope-skip SQL. Wait for migration 072 confirmation before `catalog_renormalize`.
4. **A3:** M10.x source optimizations — spec §A3 for the full list.
5. **A4:** Draft `WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` (all 7 sections). File H1 to Team 20 for migration 073 (SRC_WA + pending_manual). Create WP blog draft page via REST API or document as Nimrod manual action.

Good luck. Team 100 is available for escalations.

---

*From: Team 100 (Architecture) — 2026-04-08*
