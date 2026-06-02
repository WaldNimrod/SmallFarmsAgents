# Team 10 — Execution Mandate: Catalog Quality Packages CQ-P01–CQ-P09

**Document:** `MANDATE_CQ_CATALOG_QUALITY_TEAM10.md`  
**Date:** 2026-04-06  
**Issued by:** Team 100 (Architecture)  
**Architectural approval:** ARCH-20260406-CQ-MASTER  
**LOD:** 200  
**Teams:** Team 10 (primary), Team 20 (migrations), Team 100 (policy decisions), Team 80 (research support)

---

## 1. Scope & Authority

This mandate authorizes Team 10 to execute all 9 Catalog Quality packages in the phased parallel order defined below. The master architectural approval document (`_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md`) is the binding reference for all targets, thresholds, and policies.

**Key constraints:**
- No new product codes without Team 100 pre-approval
- No parser rewrites — alias/rule/migration fixes only (except CQ-P07 basket tier logic)
- All migrations follow the naming convention `07X_cq_pNN_description.py`
- Each package must produce a completion report before Team 190 preflight

---

## 2. Execution Order

### Phase α — Foundation (start immediately)

These three packages may run **concurrently**:

| Package | Summary | Type |
|---------|---------|------|
| **CQ-P01** | Clear alias backlog (92 → ≤20 unresolvable) | Data migration |
| **CQ-P08** | Tomato/cherry guard audit | DB audit |
| **CQ-P09** | PRD028/029 inactive enforcement | DB audit |

### Phase β — Full Run (after P01 complete)

| Package | Summary | Type |
|---------|---------|------|
| **CQ-P02** | Full ingestion → normalize → aggregate → publish | Operational run |

### Phase γ — Product Fixes (after P02 complete, all parallel)

| Package | Summary | Type |
|---------|---------|------|
| **CQ-P03** | Eggs unit audit + rules | Unit fix |
| **CQ-P04** | Passion fruit kg/unit classification | Unit fix |
| **CQ-P05** | Blueberries pack size research | Research only |
| **CQ-P07** | CSA basket tier mapping | Code + policy |

### Phase δ — Architecture (after P05 complete)

| Package | Summary | Type |
|---------|---------|------|
| **CQ-P06** | Pantry dry goods ADR + optional spike | Spec only |

---

## 3. Detailed Task Lists

### CQ-P01 — Alias Backlog Clearance

**Target:** Distinct unresolvable names ≤ 20; SRC021 ≤ 10; published products ≥ 77.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Export: `GET /unresolved/export.json?limit=500` from admin (http://127.0.0.1:5000) | File saved |
| 2 | Triage every name into: (a) alias match, (b) new product, (c) scope-skip, (d) ambiguous → Team 100 | Triage table in report |
| 3 | Create migration `072_cq_p01_alias_batch.py`: `INSERT INTO product_aliases` for bucket (a); `INSERT INTO catalog_scope_skip_rules` for bucket (c) | Migration file exists |
| 4 | For bucket (b): submit list to Team 100 with proposed code/name/category/unit. WAIT for approval | Approval reference in report |
| 5 | `alembic upgrade head` + `catalog_renormalize` | No errors |
| 6 | Verify counts: `SELECT COUNT(DISTINCT raw_product_name) FROM raw_extracted_items WHERE extraction_status = 'unresolvable' AND is_quarantined = false` | ≤ 20 |
| 7 | Verify SRC021: same query with `JOIN sources WHERE code = 'SRC021'` | ≤ 10 |
| 8 | File completion report: `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_CQ-P01_COMPLETION_TEAM10.md` | Report exists |

**Alias policy reminder:**
- Global alias: confidence 0.90
- Source-scoped: confidence 0.95
- Ambiguous strings → escalate to Team 100 (don't guess)

---

### CQ-P02 — Full Ingestion Run

**Dependency:** CQ-P01 complete.  
**Target:** IngestionRun succeeded; products ≥ 77; PRD027 duplicate resolved.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Pre-run backup: `scripts/backup_postgres.sh` or equivalent | Backup file timestamped |
| 2 | `python -m organic_market_agent.scheduler.run_ingestion --run-type manual --normalize` (full, no timeout) | Run completes |
| 3 | Document any source failures (timeout, HTTP error) — not blocking | Failures listed in report |
| 4 | `python -m organic_market_agent.scheduler.run_aggregator` | Completes |
| 5 | `python -m organic_market_agent.scheduler.run_publisher` | `output/public/public_report.json` updated |
| 6 | Verify product count ≥ 77 | Python/jq check |
| 7 | **PRD027 duplicate:** `SELECT product_id, COUNT(*) FROM daily_aggregates WHERE product_id = (SELECT id FROM products WHERE code = 'PRD027') GROUP BY product_id` — if >1 aggregation row, investigate root cause in `rolling_aggregate.py` | Documented |
| 8 | File completion report | Report exists |

---

### CQ-P03 — Eggs Unit Audit

**Dependency:** CQ-P02 complete.  
**Target:** Source × unit matrix; ≥ 90% correct egg_carton_12 mapping.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run audit SQL (see arch approval §3.3.4): all sources with PRD067, grouped by `raw_unit_text` | Matrix built |
| 2 | For each source: is it 12-pack, loose, or 6-pack? | Classified in matrix |
| 3 | If loose/6-pack: add source-scoped `normalizer_rules` unit_map overriding product default | Migration if needed |
| 4 | If 6-pack exists: propose `egg_carton_6` to Team 100 (measurement_units insert needed) | Approval request |
| 5 | `catalog_renormalize` if rules changed | Counts stable |
| 6 | File completion report with matrix | Report exists |

---

### CQ-P04 — Passion Fruit Unit Classification

**Dependency:** CQ-P02 complete.  
**Target:** Source × unit matrix; each source classified.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run audit SQL (arch approval §3.4.4): sources with PRD072, `raw_unit_text`, price | Matrix built |
| 2 | For each "יחידה" source: inspect `raw_payload_json` — is price per-fruit or per-kg? | Classified |
| 3 | If per-kg but labeled "יחידה": add source-scoped `normalizer_rules` unit_map: `{match_pattern: "יחידה", replacement_value: "kg"}` for that source | Rule inserted |
| 4 | If genuinely per-fruit: document as correct, no change | Noted in matrix |
| 5 | `catalog_renormalize` if rules changed | No regression |
| 6 | File completion report | Report exists |

---

### CQ-P05 — Blueberries Pack Size Research

**Dependency:** CQ-P02 complete.  
**Target:** Research table; ≥ 50% sources with grams known. **No code changes.**

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run audit SQL (arch approval §3.5.4): sources with PRD086, `raw_product_name`, price | Data extracted |
| 2 | For each source: attempt to determine pack grams from title or payload | Grams noted |
| 3 | If title ambiguous: check source website or flag "unknown" | Flagged |
| 4 | Build table: `source_code × pack_description × grams_if_known × price_per_100g_calc` | Table complete |
| 5 | List backlog items for CQ-P06 implementation | Items listed |
| 6 | File completion report with research table | Report exists |

---

### CQ-P06 — Pantry ADR (spec + optional spike)

**Dependency:** CQ-P05 research table.  
**Target:** ADR document; approach selected. **No production code.**

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Review CQ-P05 research table for applicability to PRD087–PRD100 | Patterns noted |
| 2 | Optional spike: prototype `product_variants` table (5 rows, non-production branch) | PR or branch link |
| 3 | Submit findings to Team 100 for ADR sign-off | Team 100 response |
| 4 | File completion report referencing ADR | Report exists |

**Note:** Team 100 will issue the signed ADR separately. Team 10's role is research input and optional spike.

---

### CQ-P07 — CSA Basket Tier Mapping

**Dependency:** CQ-P02 complete + CQ-P09 confirms PRD028/029 clean.  
**Target:** ≥ 1 CSA source with deterministic tier assignment.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Audit SRC033–SRC035: what basket data is extracted? Item counts? Price? `csa_context`? | Audit table |
| 2 | Validate tier ranges from arch approval (§3.7.2) against actual data | Ranges confirmed or adjusted |
| 3 | If ranges need adjustment: submit to Team 100 for approval | Approval reference |
| 4 | Implement tier logic: new function in `basket_handler.py` or new `basket_tier_resolver.py` | Code |
| 5 | Logic: item count available → range table → product_id; else price → range table → product_id; else default PRD026 + note | Implemented |
| 6 | V1 policy unchanged: `normalized_price_value = None` for baskets (tier only sets product_id) | Verified |
| 7 | Unit tests: ≥ 3 scenarios (small by count, large by count, fallback by price) | Tests pass |
| 8 | `catalog_renormalize` for CSA sources; verify tier distribution | SQL check |
| 9 | File completion report | Report exists |

---

### CQ-P08 — Tomato/Cherry Guard

**Target:** Zero cherry aliases → PRD001.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run audit SQL (arch approval §3.8.4): cherry tokens on PRD001 aliases | Must return 0 rows |
| 2 | Verify cherry aliases exist on PRD002 | Must return ≥ 1 row |
| 3 | Spot-check: no cherry items in PRD001 observations | Must return 0 rows |
| 4 | If drift found: create fix migration | Migration applied |
| 5 | Confirm `docs/GLOSSARY.md` alignment | Checked |
| 6 | File confirmation report | Report exists |

---

### CQ-P09 — Inactive Basket Codes Guard

**Target:** Zero active aliases on PRD028/PRD029.

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Run audit SQL (arch approval §3.9.3): active aliases on PRD028/PRD029 | Must return 0 rows |
| 2 | Confirm `is_active = false` on both codes | Verified |
| 3 | Check for orphan observations on PRD028/PRD029 | Must return 0 rows |
| 4 | Verify CSA aliases target PRD025/026/027 only | SQL check |
| 5 | If drift found: create fix migration | Migration applied |
| 6 | File confirmation report | Report exists |

---

## 4. Completion Report Template

Every completion report must follow this structure:

```markdown
# CQ-P0X Completion Report — Team 10

**Date:** YYYY-MM-DD  
**Package:** CQ-P0X — [title]  
**Architectural approval:** ARCH-20260406-CQ-MASTER  

## Summary
[1-2 sentences]

## Baseline (before)
[Metrics from before this package]

## Changes Made
[List of migrations, rules, aliases added]

## Results (after)
[Metrics after changes]

## Verification Evidence
[SQL output screenshots or copied results]

## Open Items
[Any items deferred or escalated]

## Attachments
[Links to migration files, exports, etc.]
```

---

## 5. Communication Protocol

- **Escalations to Team 100:** New product codes, ambiguous alias triage, tier range adjustments, CQ-P06 ADR input
- **Escalations to Nimrod:** Operator machine access for CQ-P02, source website research for CQ-P05
- **Team 190 preflight:** Submit completion report → Team 190 validates → then Team 50 QA (where required)
- **Blocking issues:** File immediately in `_COMMUNICATION/TEAM_10/reports/` with `BLOCKING_` prefix

---

## 6. Estimated Timeline

| Phase | Packages | Estimated Sessions |
|-------|----------|--------------------|
| α | P01 + P08 + P09 | 2–3 sessions |
| β | P02 | 1 session |
| γ | P03 + P04 + P05 + P07 | 2–3 sessions |
| δ | P06 | 1 session |
| **Total** | | **6–8 sessions** |

---

**Issued by:** Team 100 (Architecture)  
**Effective immediately.**
