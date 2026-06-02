# Team 10 — Consolidated Mandate: v1.1.0 Release

**Document:** MANDATE_V1_1_CONSOLIDATED_TEAM10.md  
**Date:** 2026-04-07  
**Issued by:** Team 100 (Architecture)  
**Document ID:** MANDATE-20260407-V1-1-CONSOLIDATED  
**Teams:** Team 10 (primary), Team 20 (migrations), Team 100 (policy decisions), Team 80 (M9C content — non-blocking)  
**Target version:** v1.1.0  
**Gate:** G-V1.1  
**Supersedes:** `MANDATE_CQ_CATALOG_QUALITY_TEAM10.md` (individual CQ governance replaced by consolidated gate)  
**Binding decisions:** ARCH-20260406-CQ-MASTER remains authoritative for alias policy, tier ranges, cherry tokens, and all LOD 200 thresholds.

---

## 1. Scope

This mandate consolidates three work streams into a single release cycle:

| Stream | Origin | Items |
|--------|--------|-------|
| **Catalog Quality** | CQ-P01 through CQ-P09 | Alias backlog, pipeline run, product unit fixes, CSA tiers, audits, pantry ADR |
| **Source Optimization** | M10.x (frozen M10.4 + M10.5) | Pragmatic mypips + CSA/retail improvements (best-effort, no hard numeric floors) |
| **Content Foundation** | M9C | WhatsApp data submission protocol + blog placeholder page (final content from Team 80 is NOT a blocker) |

**One mandate. One completion report. One Team 190 preflight. One Team 50 QA gate.**

---

## 2. Internal Work Breakdown

### Phase A — Foundation (no dependencies, can run in parallel)

#### A1: DB Audits (ex CQ-P08 + CQ-P09)

**Purpose:** Verify data integrity guards on tomato/cherry aliases and inactive basket codes.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Audit PRD001 aliases for cherry tokens (`שרי`, `cherry`, `צ'רי`, `שרי צהוב`, `שרי אדום`) | Must return 0 rows |
| 2 | Confirm cherry aliases exist on PRD002 | Must return >= 1 row |
| 3 | Spot-check `normalized_observations` for PRD001 — no cherry items | Must return 0 rows |
| 4 | Audit active aliases on PRD028/PRD029 | Must return 0 rows |
| 5 | Confirm `is_active = false` on PRD028 and PRD029 | Verified |
| 6 | Check `normalized_observations` for rows on PRD028/PRD029 | Must return 0 rows |
| 7 | Verify CSA basket aliases target PRD025/026/027 only | SQL check |
| 8 | Confirm `docs/GLOSSARY.md` alignment for PRD001/PRD002 | Checked |
| 9 | If any drift found: create fix-forward migration | Applied |

**SQL (cherry guard):**
```sql
SELECT pa.id, pa.alias_text, p.code
FROM product_aliases pa JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001' AND pa.is_active = true
  AND (pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
    OR pa.alias_text_normalized LIKE '%צ''רי%');
```

**SQL (basket codes):**
```sql
SELECT pa.id, pa.alias_text, p.code
FROM product_aliases pa JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029') AND pa.is_active = true;
```

---

#### A2: Alias Backlog Clearance (ex CQ-P01)

**Purpose:** Reduce unresolvable items from 92 distinct names to <= 20.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Export: `GET /unresolved/export.json?limit=500` from admin | File saved |
| 2 | Triage every name: (a) alias match, (b) new product, (c) scope-skip, (d) ambiguous -> Team 100 | Triage table |
| 3 | Create migration `072_v1_1_alias_batch.py` with aliases + scope-skip rules | Migration exists |
| 4 | For new products (bucket b): submit to Team 100. WAIT for approval. | Approval reference |
| 5 | `alembic upgrade head` + `catalog_renormalize` | No errors |
| 6 | Verify unresolvable distinct names <= 20 | SQL count |
| 7 | Verify SRC021 unresolvable <= 10 | SQL count |

**Alias policy:** Global (source_id NULL) default, confidence 0.90. Source-scoped only on documented ambiguity, confidence 0.95. New product codes require Team 100 pre-approval.

---

#### A3: M10.x Pragmatic Optimization (ex M10.4/M10.5 frozen backlog)

**Purpose:** Best-effort improvement of mypips and CSA/retail sources in a single session. No hard numeric floors — maximize what we can.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Review current mypips source status (SRC041-070): which are producing data, which are stalled | Status table |
| 2 | For stalled mypips sources: quick-fix selector profiles, cache-bust URLs, or deactivate if hopeless | Changes documented |
| 3 | Review CSA sources (SRC033-SRC035): check extraction status, fix CsaBasketParser issues if quick | Status documented |
| 4 | Review SRC036 (Sellio): check organic filter effectiveness, fix if quick | Status documented |
| 5 | Add any missing aliases discovered during source review | Migration or renormalize |
| 6 | Document what was improved, what remains as backlog | In completion report |

**Constraint:** This step is time-boxed to ONE session. Do not chase hard targets. Document what was achieved and what remains.

---

#### A4: M9C Placeholder + WhatsApp Protocol (ex M9C partial)

**Purpose:** Create the infrastructure for content without blocking on Team 80's final blog post.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Document WhatsApp data submission protocol in `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` | File exists |
| 2 | Create blog placeholder page template (WordPress-ready, content TBD) | Template ready |
| 3 | Add blog link anchor to public page vision block (link to placeholder) | Template updated |
| 4 | Process definition: how incoming WhatsApp data gets into the pipeline | Documented |

**Note:** Team 80 delivers final blog content independently. G9C (final content gate) closes separately after v1.1.0 if needed.

---

### Phase B — Full Pipeline Run (depends on A1, A2, A3)

#### B1: Full Ingestion + Publish + PRD027 Fix (ex CQ-P02)

**Purpose:** Execute a complete pipeline run on fresh data, resolve the PRD027 duplicate.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Pre-run DB backup via `scripts/backup_postgres.sh` or equivalent | Backup timestamped |
| 2 | `python -m organic_market_agent.scheduler.run_ingestion --run-type manual --normalize` (full, no timeout) | Run completes |
| 3 | Document any source failures (not blocking) | Listed in report |
| 4 | **PRD027 investigation:** query `daily_aggregates` for duplicate rows; inspect `rolling_aggregate.py` grouping logic | Root cause found |
| 5 | Fix PRD027 duplicate (code fix or data fix as appropriate) | Applied |
| 6 | `python -m organic_market_agent.scheduler.run_aggregator` | Completes |
| 7 | `python -m organic_market_agent.scheduler.run_publisher` | Report updated |
| 8 | Verify published product count >= 77 | Confirmed |

---

### Phase C — Product Fixes (depends on B1, all parallel)

#### C1: Eggs Unit Audit (ex CQ-P03)

**Purpose:** Verify egg sources correctly map to `egg_carton_12` where selling 12-packs.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | SQL audit: all sources with PRD067, grouped by `raw_unit_text` | Matrix built |
| 2 | Classify each source: 12-pack, loose, or 6-pack | In matrix |
| 3 | If loose/6-pack: add source-scoped `normalizer_rules` unit_map | Rule inserted |
| 4 | If 6-pack: propose `egg_carton_6` to Team 100 | Approval if needed |
| 5 | `catalog_renormalize` if rules changed | Stable |

**Target:** >= 90% of egg observations correctly mapped. Exception sources documented.

---

#### C2: Passion Fruit Disambiguation (ex CQ-P04)

**Purpose:** Classify each PRD072 source: genuine per-fruit vs mislabeled kg.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | SQL audit: sources with PRD072, `raw_unit_text`, price | Matrix built |
| 2 | For each "יחידה" source: inspect `raw_payload_json` | Classified |
| 3 | If per-kg but labeled "יחידה": add source-scoped unit_map rule | Rule inserted |
| 4 | If genuinely per-fruit: document as correct | Noted |
| 5 | `catalog_renormalize` if changed | Stable |

**Policy:** Product default remains kg (migration 069). "יחידה" in builtin map is correct for genuine per-fruit.

---

#### C3: Blueberries Pack Research (ex CQ-P05)

**Purpose:** Document pack sizes per source for PRD086. Research only, no code changes.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | SQL audit: sources with PRD086, `raw_product_name`, price | Data extracted |
| 2 | Determine pack grams from title or field knowledge | Noted |
| 3 | Build table: `source_code x pack_description x grams_if_known` | Complete |
| 4 | List backlog items for pantry ADR (D1) | Items listed |

**Target:** >= 50% of sources with grams determined. V1 remains display-only.

---

#### C4: CSA Basket Tier Mapping (ex CQ-P07)

**Purpose:** Deterministic mapping from basket observations to PRD025/026/027 tiers.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Audit SRC033-SRC035: basket data, item counts, price, `csa_context` | Audit table |
| 2 | Validate tier ranges against actual data: Small 5-8 items/80-130NIS, Medium 9-13/130-180, Large 14+/170-250 | Ranges confirmed or adjusted |
| 3 | If ranges need adjustment: submit to Team 100 | Approval |
| 4 | Implement tier logic in `basket_handler.py` or new `basket_tier_resolver.py` | Code |
| 5 | Logic: item count -> range -> product_id; else price -> range; else default PRD026 + note | Implemented |
| 6 | V1 policy: `normalized_price_value = None` for baskets (tier only sets product_id) | Verified |
| 7 | Unit tests: >= 3 scenarios (small by count, large by count, fallback by price) | Tests pass |
| 8 | `catalog_renormalize` for CSA sources | Tier distribution checked |

**Dependency:** CQ-P09 (A1) must confirm PRD028/029 are clean before this step.

---

### Phase D — Architecture (depends on C3)

#### D1: Pantry ADR (ex CQ-P06)

**Purpose:** Architecture decision for PRD087-PRD100 like-for-like comparison by net grams.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Review C3 blueberries research table for patterns | Reviewed |
| 2 | Optional spike: prototype `product_variants` table (non-production) | Spike results |
| 3 | Submit findings to Team 100 for ADR sign-off | Submitted |

**Output:** Team 100 issues signed ADR. No production code changes in this step.

---

### Phase E — Final Validation (depends on all above)

#### E1: Final Full Pipeline Run + Regression

**Purpose:** Confirm all changes work together; produce the v1.1.0 candidate artifacts.

**Tasks:**

| # | Task | Verification |
|---|------|-------------|
| 1 | Full pipeline run: ingest -> normalize -> aggregate -> publish | Completes |
| 2 | Publish to local + upload to uPress | Upload OK |
| 3 | Regression: all existing tests pass | 0 failures |
| 4 | Privacy audit: zero source codes/names in public JSON/HTML | Confirmed |
| 5 | PRD027 duplicate resolved in final output | Confirmed |
| 6 | Published product count >= 77 | Confirmed |
| 7 | Unresolvable distinct names <= 20 | Confirmed |

---

## 3. Completion Deliverables

When all phases complete, Team 10 must produce:

1. **Completion report:** `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_COMPLETION_TEAM10.md`
   - Before/after metrics for every phase
   - SQL verification evidence
   - Source x unit matrices (eggs, passion fruit, blueberries)
   - CSA tier validation data
   - M10.x improvement summary
   - Open items / backlog

2. **Team 190 preflight:** Submit completion report for constitutional validation

3. **Team 50 QA:** After Team 190 pass, submit for gate G-V1.1 per `QA_MANDATE_G_V1_1.md`

---

## 4. Escalation Protocol

- **New product codes:** Submit to Team 100 with proposed code/name/category/unit. Wait for approval.
- **Ambiguous aliases:** Escalate to Team 100 with evidence (raw names, sources, candidate products).
- **Tier range adjustments:** Submit data to Team 100 for policy sign-off.
- **Operator access (CQ-P02/B1):** Coordinate with Nimrod for full pipeline run on operator machine.
- **Blocking issues:** File immediately in `_COMMUNICATION/TEAM_10/reports/` with `BLOCKING_` prefix.

---

## 5. Timeline

| Phase | Estimated | Dependencies |
|-------|-----------|-------------|
| A (A1+A2+A3+A4) | 2-3 sessions | None (parallel) |
| B (B1) | 1 session | A complete |
| C (C1+C2+C3+C4) | 2 sessions | B complete (parallel) |
| D (D1) | 0.5 session | C3 complete |
| E (E1) | 1 session | All complete |
| **Total** | **6-8 sessions** | |

---

**Issued by:** Team 100 (Architecture)  
**Effective immediately.**  
**Gate:** G-V1.1  
**Target version:** v1.1.0
