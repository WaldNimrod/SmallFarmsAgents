---
document_type: MANDATE
version: "1.0"
---

# Mandate — v1.1.0 Catalog Quality: LOD400 Execution Order

**Mandate ID:** MANDATE-20260408-V1-1-LOD400-EXEC  
**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev) — coordination tasks also assigned to Team 20 (Infrastructure) and Nimrod (Operator) as noted per task  
**Date:** 2026-04-08  
**Priority:** HIGH  
**Gate dependency:** Blocks G-V1.1  
**Status:** ACTIVE

---

## 1. Context

The Phase A LOD400 specification (`SPEC-20260408-PHASE-A-LOD400`) has received constitutional clearance from Team 190 (revalidation report `2026-04-08_PHASES_AB_LOD400_REVALIDATION_V2_TEAM190.md`, PASS). This mandate translates that spec into a sequenced execution order.

**The LOD400 spec is the binding reference for every implementation detail in this mandate.** When this mandate states "per spec §X", the spec governs — not the LOD200 CQ master or the earlier consolidated v1.1.0 mandate. Read the spec first.

**Triggered by:** Team 190 constitutional clearance (2026-04-08)

**Related documents:**

- `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` — **primary spec (read before coding)**
- `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` — LOD200 policy decisions (still binding for policy; this mandate adds precision)
- `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` — superseded at the LOD400 level by this mandate; retain for context
- `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` — gate criteria Team 50 will verify
- `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` — program brief (BRIEF-20260407-PHASE-AB-CANONICAL)

**LOD400 code-vs-plan corrections to note before starting (spec §0):**

| # | Correction |
|---|---|
| F1 | PRD027 duplicate is already fixed — task is **confirm + verify**, not bug-fix |
| F2 | `basket_tier_resolver.py` does not exist — must be written from scratch (spec §C4) |
| F3 | CQ-P08 cherry alias drift is already fixed (migration 067) — **audit + confirm only** |
| F4 | CQ-P09 basket alias drift is already fixed (migration 068) — **audit + confirm only** |
| F5 | Published product count is 49 today; ≥77 target applies **after** Phase B ingestion run |
| F6 | CHANGELOG `[Unreleased]` is now the correct target for all v1.1.0 entries |

---

## 2. Requirements

Tasks are ordered by execution phase. Tasks within the same phase may run in parallel unless a prerequisite is stated.

---

### Task 1 — Pre-Work + Phase A: DB Audits, Alias Backlog, Pragmatic Optimization, WhatsApp Protocol

**Phase:** Pre-work + Phase A (all Phase A sub-tasks can run in parallel)  
**Owners:** Team 10 (primary); Nimrod (A4 blog page if WP REST unavailable)  
**Spec sections:** §Pre-work, §A1, §A2, §A3, §A4

**Pre-work:** Verify `CHANGELOG.md` has `[Unreleased]` as the active log target. Log every code change there as it is made.

**A1 — DB Audits (CQ-P08 + CQ-P09):** Run the spec SQL audit queries (spec §A1.2, §A1.3) to confirm zero active cherry aliases on PRD001 and zero active aliases on PRD028/PRD029. If drift is found, apply a fix-forward migration. If no drift, document clean audit in completion report.

**A2 — Alias Backlog Clearance (CQ-P01):** Triage all 92 unresolvable raw names from `_COMMUNICATION/TEAM_10/reports/2026-04-05_CATALOG_SCAN_EXCEPTIONS_REGISTER_TEAM10.md`. Classify each as: (a) new alias → insert, (b) scope-skip rule → insert, (c) invalid → ignore. Use the spec's classification decision matrix (§A2). Coordinate with Team 20 if a new migration is needed.

**A3 — M10.x Pragmatic Optimization:** Apply targeted source configuration and normalizer rule improvements per spec §A3. No structural schema changes. Document each change with the before/after metric.

**A4 — WhatsApp Protocol + M9C Blog Placeholder:** Create `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` with all 7 required sections (spec §A4.2). Create the WordPress blog draft page via WP REST API or document as Nimrod manual action (spec §A4.4 curl command). Section 5 of the protocol document must include the `psql INSERT` example verbatim from spec §A4.3.

**Acceptance criterion:**
- [ ] A1: SQL audit queries return 0 rows (or migration applied and re-audit returns 0); documented in completion report
- [ ] A2: All 92 names classified and acted on; triage table included in completion report
- [ ] A3: Each optimization documented with before/after observation count
- [ ] A4: Protocol document exists with all 7 sections; blog page created or escalated; CHANGELOG updated

---

### Task 2 — Phase B: Full Ingestion Run + PRD027 Confirmation

**Phase:** B (requires Task 1 complete — all Phase A tasks done and migrations applied)  
**Owner:** Team 10; Nimrod operates the full run on local machine  
**Spec section:** §B1

Run the full ingestion pipeline with all active sources, normalizer, aggregator, and publisher. This is the first post-v1.0.0 full run and will repopulate `normalized_observations` and `daily_aggregates`.

```bash
# Prerequisite: alembic upgrade head — confirm migration head before run
alembic current

# Canonical Phase B operator run (copy-paste exactly)
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

After publish, verify PRD027 appears at most once in `output/public/public_report.json`:

```bash
python3 -c "
import json
with open('output/public/public_report.json') as f:
    data = json.load(f)
prd027 = [p for p in data.get('products', []) if p.get('product_id') == 'PRD027']
print(f'PRD027 entries: {len(prd027)}')
assert len(prd027) <= 1, 'FAIL: PRD027 duplicate'
print('PRD027 uniqueness: PASS')
"
```

**Acceptance criterion:**
- [ ] All active sources fetched with ≥ 2 successes (publish threshold)
- [ ] Published product count ≥ 77
- [ ] PRD027 appears at most once in `public_report.json`
- [ ] `test_publish_one_row_per_product_code` PASS

---

### Task 3 — Phase C: Egg Semantics, Passion Fruit, Blueberries, basket_tier_resolver

**Phase:** C (requires Task 2 complete — post-ingestion metrics available)  
**Owner:** Team 10 (C1–C3 all parallel; no migrations expected unless drift found); Team 10 + infrastructure team (C4 — new file)  
**Spec sections:** §C1, §C2, §C3, §C4

**C1 — Egg Unit Semantics (CQ-P03):** Audit all sources for PRD067 (eggs). Build the source × unit matrix: classify each source as 12-pack, loose/unit, or 6-pack. Add source-scoped `normalizer_rules` unit_map entries where needed. Target: ≥ 90% of egg observations correctly mapped. See spec §C1 for full SQL and matrix format.

**C2 — Passion Fruit Disambiguation (CQ-P04):** Audit all sources for PRD072 (passion fruit). Build the source × unit matrix: classify each source as genuine per-fruit (`unit`) or mislabeled kg. Policy (ARCH-20260406-CQ-MASTER §3.4, BINDING): PRD072 default remains `kg`; `יחידה` in builtin map = `unit` is correct for genuine per-fruit — override only where demonstrably wrong. Price heuristic: passion fruit per-fruit is typically ₪3–8/unit; if price ₪20–40 and unit is `יחידה`, it is per-kg mislabeled. See spec §C2 for full SQL and classification logic.

**C3 — Blueberries Pack Research (CQ-P05):** Research-only task — no code change. Build the `source × pack_description × grams_if_known × price_per_100g_calc` table for PRD086. Use `raw_product_name` regex `\d+\s*(?:גרם|gr|g)` to detect gram values; fall back to source website inspection or flag "requires Team 80 field research." Target: ≥ 50% of sources with grams determined. This table feeds the Phase D Pantry ADR authored by Team 100 — **file the C3 table in your completion report and notify Team 100 when ready.** See spec §C3 for full SQL and table format.

**C4 — basket_tier_resolver.py (new file, CQ-P07):** Implement `organic_market_agent/normalizer/basket_tier_resolver.py` from scratch per spec §C4.2. The **canonical public API** (ARCH binding — do not deviate):

```python
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

def resolve_basket_tier(
    csa_context_json: Optional[str],   # JSON string from DB csa_context field, not a dict
    price_amount: Optional[Decimal],   # MUST be Decimal — never float (money rule)
    session: Session,
) -> tuple[Optional[str], str]:
    """
    Returns (product_code, resolution_note).
    product_code: 'PRD025' | 'PRD026' | 'PRD027' | None
    resolution_note: one of basket_tier_by_item_count | basket_tier_by_price |
                     basket_tier_default_medium | basket_too_small | basket_tier_oversized_default_large
    """
```

Tier resolution order: (1) item count from `csa_context_json` → parse JSON string → extract `item_count` or `len(contents)`, (2) price bands if no count, (3) default PRD026 (medium). Modify `organic_market_agent/normalizer/basket_handler.py` to call `basket_tier_resolver.run(ctx, session)` **after** nullifying `ctx.normalized_price_value = None` (spec §C4.7). Write `tests/test_basket_tier_resolver.py` with **≥ 8 named test cases** using `Decimal` for price arguments — see spec §C4.8 for the exact 8 required scenarios.

**Acceptance criterion:**
- [ ] `basket_tier_resolver.py` exists and matches canonical API above exactly
- [ ] `basket_handler.py` calls tier resolver after price nullification
- [ ] `tests/test_basket_tier_resolver.py` has ≥ 8 named test cases, all PASS (all using `Decimal`)
- [ ] C1 egg unit matrix present in completion report (all active PRD067 sources)
- [ ] C2 passion fruit source × unit matrix present (per-source classification)
- [ ] C3 blueberries research table present (source × pack_description × grams_if_known)
- [ ] Team 100 notified via report when C3 table is ready (triggers D1 Pantry ADR)

---

### Task 4 — Phase D: C3 Delivery to Team 100 (triggers D1 Pantry ADR)

**Phase:** D (requires Task 3 Phase C complete — specifically C3 blueberries research table)  
**Owner:** Team 10 (delivery); **Team 100** (D1 ADR authorship)  
**Spec section:** §D1

**Phase D has two parts:**

**Team 10 action:** File the C3 blueberries research table in the completion report (already required in Task 3 acceptance criteria). Then file a notification report to Team 100:

```
_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md
```

This report must include: (a) the completed C3 research table, (b) any pack-size patterns observed for PRD087–PRD100 dry goods, (c) confirmation that no code change was made in C3.

**Team 100 action (D1 — Pantry ADR):** Upon receipt of the C3 notification, Team 100 authors the Pantry architectural decision record at:
```
_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md
```

This is a **Team 100 deliverable**, not a Team 10 deliverable. Team 10's Phase D responsibility ends with filing the C3 notification report. Team 10 does NOT write the ADR.

**Why this matters for the completion package:** Team 50 will check T12 (Pantry ADR present). The ADR path must appear in Team 10's completion report as a cross-reference, but the document is authored by Team 100. If Team 100 has not yet filed D1 when Team 10 files its completion report, note the ADR as "pending Team 100 authorship" and include the C3 notification report path instead.

**Acceptance criterion (Team 10):**
- [ ] C3 blueberries research table filed in completion report
- [ ] `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_C3_BLUEBERRY_FINDINGS_TEAM10.md` filed
- [ ] D1 ADR path referenced in completion report (Team 100 authors independently)

---

### Task 5 — Phase E: Final Publish, Privacy Audit, Gate Evidence Package

**Phase:** E (requires Tasks 1–4 all complete)  
**Owner:** Team 10; Nimrod (FTPS upload)  
**Spec section:** §E1

Run the final pipeline, audit privacy, and publish to uPress.

```bash
# Final pipeline run
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher --upload
```

Privacy audit — both checks must pass:

```bash
# Python check
python3 -c "
import json, re
with open('output/public/public_report.json') as f:
    text = f.read()
src_matches = re.findall(r'SRC\d+', text)
if src_matches:
    print(f'FAIL: Source codes found: {set(src_matches)}')
else:
    print('Privacy check (SRC codes): PASS')
"

# Shell grep scan — expected: zero matches
grep -R -n -E 'SRC[0-9]{3}' output/public/
# Expected output: (empty)
```

Run full test suite:

```bash
pytest tests/ -m "not upress" -q
```

**Acceptance criterion:**
- [ ] `pytest tests/ -m "not upress"` — 0 failures
- [ ] Published product count ≥ 77
- [ ] Zero duplicate `product_id` in `public_report.json`
- [ ] `grep -R -E 'SRC[0-9]{3}' output/public/` — empty output
- [ ] PRD027 appears at most once
- [ ] Cherry aliases on PRD001: 0 (re-run A1 SQL)
- [ ] Active aliases on PRD028/PRD029: 0 (re-run A1 SQL)
- [ ] FTPS upload to uPress succeeded (or documented reason)
- [ ] CHANGELOG complete — all v1.1.0 changes under `[Unreleased]`

---

## 3. Out of Scope

- Phase B (M11 specification documents) — this is a separate milestone activated only after G-V1.1 PASS
- Any new sources not already in the `sources` table
- Modifying the 8-stage normalizer pipeline structure (only adding the tier resolver call in `basket_handler.py`)
- Database schema changes beyond what Team 100 specifies in the LOD400 spec (coordinate all migrations with the infrastructure team before applying — see Escalation §6 for migration handoff protocol)
- Public UI / WordPress template changes (publishing the report to uPress is in scope; changing the public report HTML template is not unless spec §A3 requires it)
- Any changes that contradict the privacy policy in `docs/PRIVACY_POLICY.md`

---

## 4. Verification Checklist

Before filing the completion report, run all of the following:

```bash
# 1. Database head check
alembic current

# 2. Full test suite
pytest tests/ -m "not upress" -q

# 3. Catalog audit (re-run A1 SQL)
psql "$DATABASE_URL" -c "
SELECT pa.product_id, COUNT(*) AS cherry_aliases
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE pa.is_active = TRUE
  AND p.code IN ('PRD001','PRD028','PRD029')
GROUP BY pa.product_id;
"
# Expected: 0 rows for PRD001 cherry aliases; 0 rows for PRD028/PRD029

# 4. PRD027 uniqueness
python3 -c "
import json
with open('output/public/public_report.json') as f:
    d = json.load(f)
n = sum(1 for p in d.get('products',[]) if p.get('product_id')=='PRD027')
print(f'PRD027 count: {n} — {\"PASS\" if n <= 1 else \"FAIL\"}')"

# 5. Privacy grep
grep -R -n -E 'SRC[0-9]{3}' output/public/

# 6. basket_tier_resolver tests
pytest tests/test_basket_tier_resolver.py -v
```

Expected results:

- [ ] `alembic current` shows `head` at revision **073** (or latest applied after Team 20 infra delivery)
- [ ] All tests pass (0 failures, ≤ 2 expected skips)
- [ ] SQL audit: 0 cherry aliases on PRD001, 0 aliases on PRD028/PRD029
- [ ] PRD027 count: 0 or 1
- [ ] Privacy grep: empty output
- [ ] `test_basket_tier_resolver.py`: all 8+ test cases PASS
- [ ] Published product count ≥ 77
- [ ] FTPS upload confirmed in `output/public/manifest.json`

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using the canonical template:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_COMPLETION_TEAM10.md`

Include this Mandate ID (`MANDATE-20260408-V1-1-LOD400-EXEC`) in the report header.

The completion report **must include** (per LOD400 spec §Completion Report Requirements):

1. Before/after metrics table (from `catalog_scan_collect_metrics.py` output)
2. Triage table (A2) — all 92 names classified
3. Source × unit matrix for eggs (C1) — all active PRD067 sources, ≥ 90% correctly mapped
4. Source × unit matrix for passion fruit (C2) — per-source classification (genuine per-fruit vs mislabeled kg)
5. Blueberries research table (C3) — `source × pack_description × grams_if_known × price_per_100g_calc`
6. PRD027 confirmation evidence (product count + uniqueness check output — ≤ 1)
7. `basket_tier_resolver.py` test output (≥ 8 named cases, all PASS)
8. D1 Pantry ADR path (authored by Team 100 — include cross-reference or "pending Team 100 authorship")
9. Privacy audit output (Python + grep — both PASS)
10. Final `pytest` output (test count, pass/fail)
11. FTPS upload confirmation (manifest entry or documented failure reason)
12. Full CHANGELOG diff under `[Unreleased]` for this release cycle
13. Any escalated blockers and their resolution status

After filing the completion report, also file a **QA Review Request** to Team 50:
`_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md`  
Save it at: `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_V1_1_QA_REQUEST_TEAM10.md`

The QA gate criteria are in `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md`.

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition and the last successful step
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide (e.g. blog page creation, FTPS credentials, new product catalog decision)

Common escalation paths:
- Migration needed → coordinate with Team 20; do not apply unapproved schema changes
- New product type found in alias triage → escalate to Team 100 before adding to catalog
- PRD027 still absent after full ingestion run → escalate to Team 100 (potential basket source gap)
- FTPS upload fails → document in completion report; Nimrod will resolve manually

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-08*  
*Authorized by: Team 100 (Architecture) — constitutional clearance confirmed by Team 190 (2026-04-08)*
