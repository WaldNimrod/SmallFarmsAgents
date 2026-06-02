# Phase A — v1.1.0 Implementation Spec (LOD400)

**Document ID:** SPEC-20260408-PHASE-A-LOD400  
**Date:** 2026-04-08  
**Author:** Team 100 (Architecture)  
**Status:** ACTIVE — binding for Team 10 (primary), Team 20 (migrations), Nimrod (operator)  
**Gate:** G-V1.1  
**Supersedes LOD200:** `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` (ARCH-20260406-CQ-MASTER) — still binding for policy decisions; this doc adds implementation precision  
**Consolidated mandate:** `_COMMUNICATION/TEAM_10/MANDATE_V1_1_CONSOLIDATED_TEAM10.md` (MANDATE-20260407-V1-1-CONSOLIDATED) — execution authority  
**QA gate mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md`  
**Canonical brief:** `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` (BRIEF-20260407-PHASE-AB-CANONICAL)

---

## ERRATA (post-Team 190 validation corrections)

The following in-document corrections were made after Team 190 PASS (2026-04-08) based on Team 20 schema review (`QA-INFRA-REQ-20260408-V1-1`) and Team 50 review (`QA-INFO-REQ-20260408-V1-1-LOD400`). All corrections are applied inline; this section records what changed for audit purposes.

| Errata ID | Location | Original (wrong) | Corrected |
|-----------|----------|-------------------|-----------|
| ERR-01 | §A2.3 scope_skip template | Column `rule_pattern`; `ON CONFLICT DO NOTHING` (no target) | Column `pattern`; added required `display_order` + `category_code`; `ON CONFLICT (display_order) DO NOTHING` |
| ERR-02 | §A2.3 aliases template (global + scoped) | Column `confidence_score`; included `updated_at` field; `ON CONFLICT DO NOTHING` | Column `confidence`; removed `updated_at` (does not exist on `product_aliases`); `ON CONFLICT (alias_text_normalized, source_id) DO NOTHING` |
| ERR-03 | §A4.3 psql example | `source_id`, `raw_name`, `raw_price`, `raw_unit`, `raw_text` columns; `s.source_code`; single-step INSERT | `source_fetch_run_id` + `raw_asset_id` (FK deps); `raw_product_name`, `raw_price_text`, `raw_unit_text`; `s.code`; corrected 4-step procedure |
| ERR-04 | §A4.3 `pending_manual` status | `pending_manual` used without noting schema change needed | Added note: `pending_manual` requires migration to extend `chk_rei_extraction_status` CHECK constraint |
| ERR-05 | §C4.2 basket_tier_resolver API (mandate echo) | Mandate Task 3 showed `dict | None` / `float | None` / `str | None` | Canonical: `Optional[str]` / `Optional[Decimal]` / `tuple[Optional[str], str]` — see §C4.2 which was always correct |

**Superseding document:** `ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1` and `ARCH-20260408-TEAM20-RESPONSE-V1-1` contain the binding decisions that triggered these corrections.

---

## 0. Code-vs-Plan Corrections (LOD400 baseline adjustments)

Before implementation begins, Team 10 must note the following corrections to the LOD200 description. These findings were identified by Team 100 via code review on 2026-04-08.

| # | Finding | LOD200 framing | LOD400 correction |
|---|---------|----------------|-------------------|
| F1 | PRD027 duplicate | "investigate PRD027 duplicate" | Bug is already fixed in current `rolling_aggregate.py` (groups by DB PK, emits one dict per `pid`). Test `test_publish_one_row_per_product_code` asserts uniqueness. Task is now **confirm + verify** after fresh ingestion run. |
| F2 | basket_tier_resolver | "implement tier logic in basket_handler.py or new basket_tier_resolver.py" | No tier logic exists anywhere. `basket_handler.py` only nullifies prices. `_BUILTIN_UNIT_MAP` basket_small/medium/large are **unit codes** (raw text → unit), not product tier assignments. A new `basket_tier_resolver.py` must be written from scratch (see §C4). |
| F3 | CQ-P08 | "fix-forward migration if drift" | Migration 067 already moved cherry alias from PRD001 → PRD002. Task is **audit + confirm only**. No migration expected unless drift is found. |
| F4 | CQ-P09 | "fix-forward migration if drift" | Migration 068 already re-pointed PRD028/PRD029 aliases and deleted orphans. Task is **audit + confirm only**. |
| F5 | Product count | "published products ≥77" | Current `public_report.json` has **49 products** — rolling window data is stale post-v1.0.0 declaration. The ≥77 target applies only **after** CQ-P02 full ingestion run. All Phase C/D/E metrics must be measured against post-B1 output. |
| F6 | CHANGELOG | entries in wrong version | 2026-04-08 entries were under `[1.0.0]`; corrected to `[Unreleased]` by Team 100 on 2026-04-08 (pre-authoring). |

---

## Pre-Work: CHANGELOG Check

Before any code change:

- [ ] Verify `[Unreleased]` section in `CHANGELOG.md` is the active log target (correction applied 2026-04-08 by Team 100)
- [ ] All v1.1.0 changes logged under `[Unreleased]`, not under `[1.0.0]`

---

## Execution Phases

```
Pre-work   CHANGELOG verification
     │
Phase A ───────────────────────────────────────────────────────────── (all parallel)
     ├── A1: DB Audits (CQ-P08 + CQ-P09)
     ├── A2: Alias Backlog Clearance (CQ-P01)
     ├── A3: M10.x Pragmatic Optimization
     └── A4: WhatsApp Protocol + M9C Placeholder
     │
Phase B ── B1: Full Ingestion Run + PRD027 Confirmation (CQ-P02)  ── (after A complete)
     │
Phase C ───────────────────────────────────────────────────────────── (all parallel, after B1)
     ├── C1: Eggs Unit Audit (CQ-P03)
     ├── C2: Passion Fruit Disambiguation (CQ-P04)
     ├── C3: Blueberries Research (CQ-P05)
     └── C4: CSA Basket Tier Mapping (CQ-P07)
     │
Phase D ── D1: Pantry ADR (CQ-P06)                                 ── (after C3 research table)
     │
Phase E ── E1: Final Validation + Upload                           ── (after all above)
```

---

## Phase A — Foundation (all tasks parallel)

### A1: DB Audits — Cherry Guard + Inactive Basket Codes (CQ-P08 + CQ-P09)

**Owner:** Team 10 (audit) + Team 20 (migration only if drift found)  
**Expected effort:** < 0.5 session  
**Expected outcome:** Confirmation only — migrations 067 and 068 already closed these issues.

#### A1.1 Files involved

No new files expected unless drift is found:
- IF drift: `organic_market_agent/db/versions/072_cq_p08_p09_drift_fix.py` (Team 20)
- Evidence output: completion report section with SQL results pasted verbatim

#### A1.2 Cherry Guard Audit (CQ-P08)

Run the following SQL. **All three queries must return the stated result.**

```sql
-- Query 1: MUST return 0 rows
-- Purpose: no cherry-token aliases pointing at PRD001 (regular tomato)
SELECT pa.id, pa.alias_text, pa.alias_text_normalized, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001'
  AND pa.is_active = true
  AND (
    pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
    OR pa.alias_text_normalized LIKE '%צ''רי%'
  );
-- Expected: 0 rows. Any row = CRITICAL DRIFT → create migration 072 to deactivate + move to PRD002.

-- Query 2: MUST return >= 1 row
-- Purpose: cherry aliases confirmed on PRD002 (cherry tomato)
SELECT pa.id, pa.alias_text, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD002'
  AND pa.is_active = true
  AND (
    pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
  );
-- Expected: >= 1 row (migration 067 inserted at minimum "עגבניות שרי אורגניות").

-- Query 3: MUST return 0 rows
-- Purpose: spot-check normalized_observations for cherry items on PRD001
SELECT rei.raw_product_name, no2.product_id, p.code
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
JOIN raw_extracted_items rei ON no2.raw_extracted_item_id = rei.id
WHERE p.code = 'PRD001'
  AND (
    rei.raw_product_name LIKE '%שרי%'
    OR rei.raw_product_name LIKE '%cherry%'
  );
-- Expected: 0 rows.
```

**Cherry token binding list (ARCH-20260406-CQ-MASTER §3.8.2):**
`שרי`, `cherry`, `צ'רי`, `שרי צהוב`, `שרי אדום` → PRD002 exclusively.

#### A1.3 Inactive Basket Codes Audit (CQ-P09)

```sql
-- Query 4: MUST return 0 rows
-- Purpose: no active aliases targeting inactive PRD028 or PRD029
SELECT pa.id, pa.alias_text, p.code as target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029')
  AND pa.is_active = true;
-- Expected: 0 rows. Migration 068 cleared these.

-- Query 5: MUST return (PRD028, false) and (PRD029, false)
SELECT code, canonical_name_he, is_active
FROM products
WHERE code IN ('PRD028', 'PRD029');
-- Expected: both is_active = false.

-- Query 6: MUST return 0
SELECT COUNT(*) AS orphan_count
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029');
-- Expected: 0.

-- Query 7: CSA basket aliases target only PRD025/026/027
SELECT pa.alias_text, p.code AS target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE (
  pa.alias_text_normalized LIKE '%סל%'
  OR pa.alias_text_normalized LIKE '%ארגז%'
  OR pa.alias_text_normalized LIKE '%basket%'
)
AND pa.is_active = true
ORDER BY p.code;
-- Expected: all rows show PRD025, PRD026, or PRD027. No PRD028/PRD029.
```

#### A1.4 Exit Criteria (A1)

- [ ] Query 1 returns 0 rows (cherry → PRD001 guard clean)
- [ ] Query 2 returns ≥ 1 row (cherry aliases on PRD002 confirmed)
- [ ] Query 3 returns 0 rows (no cherry observations on PRD001)
- [ ] Query 4 returns 0 rows (no active aliases on PRD028/PRD029)
- [ ] Query 5: PRD028 and PRD029 both `is_active = false`
- [ ] Query 6 returns 0 (no orphan observations)
- [ ] Query 7: all CSA basket aliases target PRD025/026/027 only
- [ ] All SQL results pasted verbatim in completion report
- [ ] If ANY query shows drift: migration 072 created and applied before marking A1 complete

---

### A2: Alias Backlog Clearance (CQ-P01)

**Owner:** Team 10 (data + triage) + Team 20 (migration)  
**Expected effort:** 1–2 sessions  
**Baseline:** 92 distinct unresolvable names; SRC021 = 61 unresolvable names  
**Target:** distinct unresolvable ≤ 20; SRC021 unresolvable ≤ 10

#### A2.1 Files involved

| File | Action | Owner |
|------|--------|-------|
| `organic_market_agent/db/versions/072_cq_p01_alias_batch.py` | NEW — batch aliases + scope-skip rules | Team 20 |
| `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_CQ-P01_TRIAGE_TABLE_TEAM10.md` | NEW — triage evidence | Team 10 |

**Note on migration numbering:** If A1 requires a drift-fix migration, it takes 072 and the alias batch becomes 073. Team 10 coordinates with Team 20 to assign migration numbers in order. Alembic head must remain linear.

#### A2.2 Step-by-step

**Step 1 — Export unresolvable names**
```bash
# Requires admin server running (python -m organic_market_agent run_admin)
curl -s "http://127.0.0.1:5000/unresolved/export.json?limit=500" \
  | python3 -m json.tool > /tmp/unresolved_export.json
```

**Step 2 — Triage each name into one of four buckets**

| Bucket | Criteria | Action |
|--------|----------|--------|
| (a) Alias match | The name clearly refers to a known product already in catalog | Add alias to migration |
| (b) New product needed | Name represents a product category not yet in catalog | Escalate to Team 100 with proposed code/name/category/unit — WAIT for approval before inserting |
| (c) Scope-skip | Non-food, out-of-scope, package material, etc. | Add scope-skip rule to migration |
| (d) Ambiguous | Unclear mapping | Escalate to Team 100 with evidence (raw name, source, candidate products) |

**Alias policy (ARCH-20260406-CQ-MASTER §3.1.3, BINDING):**
- Default: global alias (`source_id = NULL`), confidence 0.90
- Source-scoped: only when same Hebrew string maps to different products on different sources, confidence 0.95
- New product codes: Team 100 pre-approval REQUIRED (submit proposed `code`, `canonical_name_he`, `category`, `default_measurement_unit_id`)

**Step 3 — Migration structure**

```python
# organic_market_agent/db/versions/072_cq_p01_alias_batch.py
# Template — adapt with actual triage results

from alembic import op
import sqlalchemy as sa

revision = '072'
down_revision = '071'  # or '072' if drift fix exists
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()

    # --- SCOPE-SKIP RULES (bucket c) ---
    # Each rule: (display_order, category_code, pattern, match_type, notes)
    # display_order must be globally unique (uq_catalog_scope_skip_rules_display_order).
    # Find next band: SELECT MAX(display_order) FROM catalog_scope_skip_rules;
    # category_code MUST be one of: donation | cleaning | dry_grocery | grocery | other
    # match_type MUST be one of: exact | prefix | contains | regex
    scope_skip_rules = [
        # (display_order, category_code, pattern, match_type, notes),
        # Example: (400, 'cleaning', 'שקית', 'contains', 'packaging material'),
    ]
    for display_order, category_code, pattern, match_type, notes in scope_skip_rules:
        conn.execute(sa.text("""
            INSERT INTO catalog_scope_skip_rules
              (display_order, category_code, pattern, match_type, is_active, notes, created_at, updated_at)
            VALUES
              (:display_order, :category_code, :pattern, :match_type, true, :notes, now(), now())
            ON CONFLICT (display_order) DO NOTHING
        """), {"display_order": display_order, "category_code": category_code,
               "pattern": pattern, "match_type": match_type, "notes": notes})

    # --- GLOBAL ALIASES (bucket a, source_id NULL) ---
    # Each alias: alias_text, product_code, confidence
    global_aliases = [
        # ('raw_hebrew_name', 'PRD0XX', 0.90),
    ]
    for alias_text, product_code, confidence in global_aliases:
        conn.execute(sa.text("""
            INSERT INTO product_aliases
              (alias_text, alias_text_normalized, product_id, source_id,
               is_active, confidence, created_at)
            SELECT
              :alias_text,
              lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
              p.id,
              NULL,
              true,
              :confidence,
              now()
            FROM products p
            WHERE p.code = :product_code
            ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
        """), {"alias_text": alias_text, "product_code": product_code,
               "confidence": confidence})

    # --- SOURCE-SCOPED ALIASES (bucket a, ambiguous names) ---
    # Each: alias_text, product_code, source_code, confidence
    scoped_aliases = [
        # ('raw_name', 'PRD0XX', 'SRC021', 0.95),
    ]
    for alias_text, product_code, source_code, confidence in scoped_aliases:
        conn.execute(sa.text("""
            INSERT INTO product_aliases
              (alias_text, alias_text_normalized, product_id, source_id,
               is_active, confidence, created_at)
            SELECT
              :alias_text,
              lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
              p.id,
              s.id,
              true,
              :confidence,
              now()
            FROM products p, sources s
            WHERE p.code = :product_code AND s.code = :source_code
            ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
        """), {"alias_text": alias_text, "product_code": product_code,
               "source_code": source_code, "confidence": confidence})

def downgrade() -> None:
    pass  # alias/scope-skip additions are not reversible in production
```

**Step 4 — Apply migration and renormalize**
```bash
alembic upgrade head
python -m organic_market_agent catalog_renormalize
```

**Step 5 — Verify with before/after metrics**
```bash
python scripts/catalog_scan_collect_metrics.py -o data/catalog_scan_metrics_after_cq_p01.json
```

#### A2.3 Verification SQL

```sql
-- After catalog_renormalize: confirm targets are met
SELECT COUNT(DISTINCT raw_product_name) AS distinct_unresolvable
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable' AND is_quarantined = false;
-- Must be <= 20

SELECT COUNT(DISTINCT rei.raw_product_name) AS src021_unresolvable
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE s.code = 'SRC021'
  AND rei.extraction_status = 'unresolvable'
  AND rei.is_quarantined = false;
-- Must be <= 10
```

#### A2.4 Exit Criteria (A2)

- [ ] Triage table filed in completion report (all 92 names classified into a/b/c/d)
- [ ] Migration applied (`alembic upgrade head` — 0 errors)
- [ ] `catalog_renormalize` completed without errors
- [ ] Distinct unresolvable ≤ 20 (SQL confirmed)
- [ ] SRC021 unresolvable ≤ 10 (SQL confirmed)
- [ ] No new product codes without Team 100 approval reference
- [ ] All new aliases have `confidence_score` ≥ 0.90
- [ ] Before/after metrics JSON saved to `data/` folder
- [ ] CHANGELOG updated under `[Unreleased]`

---

### A3: M10.x Pragmatic Optimization

**Owner:** Team 10  
**Expected effort:** 1 session (time-boxed — do not exceed)  
**Approach:** Best-effort; document what was improved and what remains as backlog. No hard numeric targets.

#### A3.1 Pre-work: source status audit

Before touching any code, run this query to understand current state:

```sql
-- Current active sources and their latest extraction status
SELECT
  s.code,
  s.name_he,
  s.platform_family,
  s.source_tier,
  s.is_active,
  sfr.status AS last_run_status,
  sfr.started_at AS last_run_at,
  COUNT(rei.id) AS total_items,
  SUM(CASE WHEN rei.extraction_status = 'normalized' THEN 1 ELSE 0 END) AS normalized,
  SUM(CASE WHEN rei.extraction_status = 'unresolvable' THEN 1 ELSE 0 END) AS unresolvable,
  SUM(CASE WHEN rei.extraction_status = 'ignored' THEN 1 ELSE 0 END) AS ignored
FROM sources s
LEFT JOIN (
  SELECT DISTINCT ON (source_id)
    id, source_id, status, started_at
  FROM source_fetch_runs
  ORDER BY source_id, started_at DESC
) sfr ON sfr.source_id = s.id
LEFT JOIN source_fetch_runs sfr2 ON sfr2.source_id = s.id
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr2.id
WHERE s.is_active = true
GROUP BY s.code, s.name_he, s.platform_family, s.source_tier, s.is_active,
         sfr.status, sfr.started_at
ORDER BY s.source_tier, normalized DESC;
```

#### A3.2 Decision tree per source (mypips SRC041–SRC074)

For each mypips source showing 0 normalized observations:

| Condition | Action |
|-----------|--------|
| `last_run_status = 'failed'` AND selector profile is stale | Update `selector_profile.json` entry + cache-bust URL (`?_oma=v1_1`) |
| `last_run_status = 'succeeded'` but 0 items extracted | Check parser: inspect `raw_extracted_items` for raw text; add aliases if needed |
| Source has not run in > 7 days | Re-activate and run in focused trigger |
| Source consistently fails across 3+ sessions | Mark `is_active = false` + document reason in completion report |
| Source produces data but low resolution | Add scope-skip rules or aliases as appropriate |

#### A3.3 Decision tree per CSA source (SRC033–SRC035)

```sql
-- Check current CSA extraction state
SELECT s.code, s.name_he,
       COUNT(rei.id) AS items,
       SUM(CASE WHEN rei.extraction_status = 'normalized' THEN 1 ELSE 0 END) AS normalized
FROM sources s
JOIN source_fetch_runs sfr ON sfr.source_id = s.id
JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033', 'SRC034', 'SRC035')
GROUP BY s.code, s.name_he;
```

For each stalled CSA source: inspect `raw_payload_json` for one extracted item to determine if `CsaBasketParser` is producing valid `csa_context`. If not: check parser selector profile, fix if < 30 minutes, otherwise document as backlog.

#### A3.4 Decision tree for SRC036 (Sellio / Teva Shuk)

Check current organic filter effectiveness:
```sql
SELECT COUNT(*) as total,
       SUM(CASE WHEN extraction_status = 'normalized' THEN 1 ELSE 0 END) as normalized,
       SUM(CASE WHEN extraction_status = 'ignored' THEN 1 ELSE 0 END) as ignored
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE s.code = 'SRC036';
```
If resolution rate < 50%: check scope-skip rules for over-blocking organic items. Fix only if change is safe and < 30 minutes.

#### A3.5 Files that may be modified

| File | Change type |
|------|-------------|
| `organic_market_agent/db/versions/07X_cq_m10x_source_fixes.py` | Optional migration — only if selector/profile changes needed |
| `data/m10x_optimization_status.json` | NEW — output of source status audit (save for completion report) |

#### A3.6 Exit Criteria (A3)

- [ ] Source status audit SQL executed and results documented
- [ ] Decision applied for each mypips source (fix / deactivate / document backlog)
- [ ] CSA source status documented
- [ ] SRC036 status documented
- [ ] Improvements applied are logged in CHANGELOG under `[Unreleased]`
- [ ] Remaining backlog items listed in completion report (no hard target)

---

### A4: M9C Placeholder + WhatsApp Submission Protocol

**Owner:** Team 10  
**Expected effort:** < 1 session  
**Note:** Team 80 delivers final blog content independently; this step only creates infrastructure.

#### A4.1 Files involved

| File | Action |
|------|--------|
| `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` | NEW |
| Blog placeholder WordPress page | NEW via WP REST API or documented for Nimrod WP action |
| Public page template update (vision block link) | OPTIONAL — only if agreed with Nimrod |

#### A4.2 WhatsApp Data Submission Protocol — required document structure

`documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` must contain ALL of the following sections:

**Section 1: Purpose**
Brief paragraph on why the protocol exists (community price data collection via WhatsApp as interim channel before in-page submission form).

**Section 2: Submission Message Format**
Required fields a farmer must provide in a WhatsApp message:
```
Mandatory:
- Product name (Hebrew, from catalog)
- Price (number in ILS)
- Unit (kg / unit / bunch / pack)
- Your farm/market name (for operator validation, NOT published)
- Date of price (today or up to 7 days ago)

Optional:
- Quantity (if selling in bulk, e.g., "5 kg for ₪30")
- Notes (quality grade, variety)
```

**Section 3: Operator Intake Steps** (ordered procedure)
1. Receive WhatsApp message
2. Validate format (all mandatory fields present)
3. Match product name to catalog (`docs/PRODUCT_CATALOG_V1.md` — canonical names)
4. Open admin UI `/aliases` — confirm product is in catalog, or flag for new product review
5. Enter data via admin UI manual observation entry (or via `psql` INSERT — see §5)
6. Confirm source attribution to a placeholder "community_whatsapp" source code
7. Reply to farmer confirming receipt (optional but encouraged)

**Section 4: Pipeline Integration Path**
- Data enters as `raw_extracted_items` row with `extraction_status = 'pending_manual'` (or `normalized` if operator pre-validates)
- `source_id` = community WhatsApp source (register SRC_WA in migration if not present)
- `market_scope = 'community'`
- Operator runs `catalog_renormalize` after batch entry
- Data appears in next publish cycle (next `run_aggregator + run_publisher`)

**Section 5: Privacy Rules**
- Farm name / operator identity NEVER enters `normalized_observations` or published output
- Only aggregated price statistics are published (per existing privacy policy in `docs/PRIVACY_POLICY.md`)
- Source attribution in published output shows only source count, not names

**Section 6: Data Validation Criteria**
- Price must be > 0 and < ₪1000/kg (flag outliers for review)
- Date must be within last 14 days
- Product must exist in catalog (no new products via WhatsApp without Team 100 approval)
- Duplicate detection: same farm + same product + same date = reject duplicate

**Section 7: Escalation**
- Ambiguous product name → flag in `/catalog/pending-aliases`
- Price seems very unusual → flag as `qa_flags` entry
- Request for new product → escalate to Team 100

#### A4.3 Executable Commands

**WP REST API — create blog draft page** (requires credentials from `.env.upress`):

```bash
# Create blog draft via WP REST API
curl -s -X POST https://nimrod.bio/wp-json/wp/v2/pages \
  -H "Authorization: Basic $(printf '%s:%s' "${WP_USER}" "${WP_APP_PASS}" | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "למה החווה שלי לא הייתה רווחית?",
    "slug": "blog-farm-not-profitable",
    "status": "draft",
    "content": "<p>תוכן בדרך — המאמר בהכנה על ידי צוות 80.</p>"
  }' | python3 -m json.tool | grep -E '"id"|"link"|"status"'
# Expected: JSON response with "status": "draft" and a page ID
# Record the page ID in the completion report
```

If WP REST approach is not available (Application Password not configured), document as **Nimrod WP action** and include this command in the completion report as `MANUAL REQUIRED`.

**psql — operator manual entry for WhatsApp-sourced observation** (Section 5 of the protocol document must include this example verbatim):

> **Schema note (ERRATA):** `raw_extracted_items` has no `source_id` column and no `raw_name`/`raw_price`/`raw_unit`/`raw_text` columns. The actual columns are `raw_product_name`, `raw_price_text`, `raw_unit_text`, and rows require FK links to `source_fetch_runs` and `raw_assets`. Additionally, `pending_manual` is a new extraction_status value that requires a migration to add it to the `chk_rei_extraction_status` CHECK constraint (included in migration that seeds SRC_WA). Use the corrected multi-step procedure below.

```sql
-- Operator manual entry for a WhatsApp community submission
-- Prerequisites:
--   1. Migration adding SRC_WA source row and 'pending_manual' to extraction_status CHECK must be applied.
--   2. Run via: psql "$DATABASE_URL"
-- Replace <YYYY-MM-DD> with today's date.

-- Step 1: Create a manual ingestion run for this batch
INSERT INTO ingestion_runs (run_type, status, triggered_by, sources_total, sources_succeeded, community_sources_succeeded)
VALUES ('manual', 'completed', 'operator_whatsapp', 1, 1, 1)
RETURNING id;
-- Record the returned id as <RUN_ID>

-- Step 2: Create a source_fetch_run entry for SRC_WA
INSERT INTO source_fetch_runs (ingestion_run_id, source_id, status)
SELECT <RUN_ID>, s.id, 'success'
FROM sources s WHERE s.code = 'SRC_WA'
RETURNING id;
-- Record the returned id as <SFR_ID>

-- Step 3: Create a raw_asset placeholder for the WhatsApp submission
INSERT INTO raw_assets (source_id, source_fetch_run_id, storage_path, file_type, checksum_sha256, bytes_size)
SELECT s.id, <SFR_ID>, 'whatsapp/manual_<YYYY-MM-DD>.txt', 'text', 'manual_entry', 0
FROM sources s WHERE s.code = 'SRC_WA'
RETURNING id;
-- Record the returned id as <ASSET_ID>

-- Step 4: Insert the raw_extracted_item with correct column names
INSERT INTO raw_extracted_items (
    source_fetch_run_id,
    raw_asset_id,
    raw_product_name,
    raw_price_text,
    raw_unit_text,
    extraction_status
)
VALUES (
    <SFR_ID>,
    <ASSET_ID>,
    'עגבניות שרי',           -- product name from WhatsApp (Hebrew, from catalog)
    '12.50',                   -- price in ILS (VARCHAR, not numeric)
    'ק"ג',                     -- unit as received
    'pending_manual'           -- requires 'pending_manual' in CHECK constraint
);

-- Verify the row was inserted
SELECT id, raw_product_name, raw_price_text, raw_unit_text, extraction_status
FROM raw_extracted_items
ORDER BY created_at DESC
LIMIT 1;
```

After batch entry: run `python -m organic_market_agent catalog_renormalize` to process all `pending_manual` rows.

#### A4.4 Blog placeholder page

Create a WordPress page with:
- Title: "למה החווה שלי לא הייתה רווחית?" (Team 80 blog post placeholder)
- Status: draft (not published until Team 80 delivers content)
- URL slug: `/blog/farm-not-profitable` (or coordinate with Nimrod for exact slug)
- Body: short placeholder paragraph noting content is coming soon

Document the page creation method in completion report (WP REST API call or Nimrod admin action).

#### A4.5 Exit Criteria (A4)

- [ ] `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` exists with all 7 sections
- [ ] Submission format table is complete (mandatory + optional fields)
- [ ] Operator intake procedure is numbered and actionable
- [ ] Privacy section references `docs/PRIVACY_POLICY.md`
- [ ] Blog placeholder page created (or documented as Nimrod WP action)
- [ ] CHANGELOG updated under `[Unreleased]`

---

## Phase B — Full Pipeline Run (after all Phase A tasks complete)

### B1: Full Ingestion Run + PRD027 Confirmation + CQ-P02 Closure (CQ-P02)

**Owner:** Team 10 + Nimrod (operator machine for full run)  
**Prerequisite:** A2 migration applied (`alembic upgrade head` stable)  
**Expected effort:** 1 session

#### B1.1 Pre-run preparation

```bash
# 1. Take pre-run DB backup
pg_dump $DATABASE_URL -F c -f "backups/pre_cq_p02_$(date +%Y%m%d_%H%M%S).dump"
# or: scripts/backup_postgres.sh (if pg_dump not on PATH, use Docker exec)
docker exec oma-g2-ev pg_dump -U postgres organic_market -F c \
  > "backups/pre_cq_p02_$(date +%Y%m%d_%H%M%S).dump"

# 2. Confirm alembic head
alembic current
# Must show latest migration (072 or 073 depending on A1/A2 numbering)
```

#### B1.2 PRD027 uniqueness pre-confirmation (BEFORE full run)

This confirms Finding F1 — the duplicate is a historical artifact, not a current bug:

```bash
# Confirm test passes on current code (no DB data needed for this assertion)
pytest tests/test_publisher_local.py::test_publish_one_row_per_product_code -v
# Expected: PASSED
```

If this test does not exist or fails: STOP. File a blocking report to Team 100 before proceeding.

#### B1.3 Full ingestion run

```bash
# Full ingestion + normalize in one command
# Do NOT use --skip-normalize or source_code filter — this must be a complete run
python -m organic_market_agent scheduler.run_ingestion \
  --run-type manual \
  --normalize

# Monitor for completion — do not interrupt
# Expected: status = 'succeeded' or 'partial' (some source failures acceptable)
```

Log any source failures with their source code and error message in the completion report. Source failures are NOT blocking for CQ-P02 closure.

#### B1.4 Aggregate + publish

```bash
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

#### B1.5 Post-run verification

```sql
-- Confirm ingestion run completed
SELECT id, run_type, status, started_at, finished_at,
       sources_attempted, sources_succeeded, sources_failed
FROM ingestion_runs
ORDER BY id DESC
LIMIT 1;
-- status must be 'succeeded' or 'partial' (not 'failed' or 'running')
```

```bash
# Verify published product count
python3 -c "
import json
with open('output/public/public_report.json') as f:
    data = json.load(f)
products = data.get('products', [])
codes = [p['product_id'] for p in products]
print(f'Total published: {len(products)}')
print(f'Unique codes: {len(set(codes))}')
print(f'Duplicates: {[c for c in codes if codes.count(c) > 1]}')
assert len(codes) == len(set(codes)), 'DUPLICATE product_id in output!'
print('Uniqueness check: PASS')
"
# Total published must be >= 77
# Duplicates list must be empty
```

#### B1.6 PRD027 specific check

```bash
python3 -c "
import json
with open('output/public/public_report.json') as f:
    data = json.load(f)
prd027 = [p for p in data.get('products', []) if p['product_id'] == 'PRD027']
count = len(prd027)
print(f'PRD027 entries: {count}')
if count == 0:
    print('PRD027 not in published output (insufficient data — acceptable if < 2 sources)')
elif count == 1:
    print(f'PRD027 PASS: exactly 1 entry, avg={prd027[0].get(\"avg_price\", \"N/A\")}')
else:
    print(f'FAIL: PRD027 appears {count} times — investigate rolling_aggregate.py')
"
```

#### B1.7 Exit Criteria (B1)

- [ ] Pre-run DB backup confirmed
- [ ] `test_publish_one_row_per_product_code` passes BEFORE run
- [ ] Ingestion run completed with status `succeeded` or `partial`
- [ ] All active sources attempted (partial failures documented, not blocking)
- [ ] `run_aggregator` completed without error
- [ ] `run_publisher` completed without error
- [ ] Published product count ≥ 77 (confirmed via Python check)
- [ ] Zero duplicate `product_id` entries in `public_report.json`
- [ ] PRD027 appears 0 or 1 times (both acceptable — 0 = below threshold, 1 = clean)
- [ ] Ingestion run SQL row pasted in completion report (id, status, timestamps, source counts)
- [ ] CHANGELOG updated under `[Unreleased]`

---

## Phase C — Product Fixes (all parallel, after B1)

### C1: Eggs Unit Audit (CQ-P03)

**Owner:** Team 10  
**Expected effort:** < 1 session  
**Target:** ≥ 90% of egg observations correctly mapped; exception sources documented

#### C1.1 Source × unit matrix audit

```sql
SELECT
  s.code AS source_code,
  s.name_he AS source_name,
  rei.raw_unit_text,
  mu.code AS resolved_unit,
  COUNT(*) AS obs_count
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD067'
  AND rei.is_quarantined = false
GROUP BY s.code, s.name_he, rei.raw_unit_text, mu.code
ORDER BY s.code, obs_count DESC;
```

#### C1.2 Decision per source type

| raw_unit_text | Resolved to | Verdict | Action |
|---------------|-------------|---------|--------|
| "12 ביצים" / "אריזת 12" | egg_carton_12 | Correct | None |
| "יחידה" / "unit" | unit | Depends | Inspect raw_payload_json: if price/dozen→ add unit_map rule |
| (empty) | egg_carton_12 | Via product default | Acceptable (product default = egg_carton_12 per migration 069) |

If any source sells **loose eggs** (per-unit pricing), add a source-scoped `normalizer_rules` row:
```sql
INSERT INTO normalizer_rules
  (normalizer_profile_id, rule_kind, match_pattern, match_type, replacement_value,
   priority, is_active, created_at, updated_at)
SELECT
  np.id, 'unit_map', 'יחידה', 'exact', 'unit', 10, true, now(), now()
FROM normalizer_profiles np
JOIN sources s ON s.id = np.source_id
WHERE s.code = 'SRC0XX';  -- replace with actual source code
```

If 6-pack sources exist: submit `egg_carton_6` unit proposal to Team 100 — do NOT insert new measurement_unit without approval.

#### C1.3 Exit Criteria (C1)

- [ ] Source × unit matrix complete in completion report
- [ ] ≥ 90% of egg observations have `egg_carton_12` where source sells 12-packs
- [ ] Exception sources (loose, 6-pack) documented with remediation plan or explicit waiver
- [ ] Any `normalizer_rules` changes applied and `catalog_renormalize` run
- [ ] No regression in PRD067 published data

---

### C2: Passion Fruit Disambiguation (CQ-P04)

**Owner:** Team 10  
**Expected effort:** < 1 session  
**Baseline:** PRD072 default unit = kg (migration 069). Published unit shows "יחידה" for some sources — these may be correctly per-fruit or incorrectly labeled.

#### C2.1 Audit SQL

```sql
SELECT
  s.code AS source_code,
  s.name_he,
  rei.raw_unit_text,
  rei.raw_price_text,
  no2.normalized_price_value,
  mu.code AS resolved_unit
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD072'
  AND rei.is_quarantined = false
ORDER BY s.code, no2.observed_at DESC;
```

#### C2.2 Classification rules

For each source where `raw_unit_text = 'יחידה'`:

1. Inspect `raw_payload_json` for original product title — does it say "פסיפלורה 1 יח'" (per-fruit) or "פסיפלורה למשקל" / "פסיפלורה קילו"?
2. Check price range: passion fruit per-fruit typically ₪3–₪8/unit. If price is ₪20–₪40, it is per-kg mislabeled as unit.
3. Document classification in matrix: `genuine_per_fruit` | `mislabeled_kg` | `ambiguous`

For `mislabeled_kg`: add source-scoped unit_map rule (same pattern as C1).

**Policy (ARCH-20260406-CQ-MASTER §3.4, BINDING):** PRD072 default remains kg. "יחידה" in builtin map = `unit` is correct for genuine per-fruit. Override only where demonstrably wrong.

#### C2.3 Exit Criteria (C2)

- [ ] Source × unit matrix complete in completion report
- [ ] Each "יחידה" source classified (`genuine_per_fruit` / `mislabeled_kg` / `ambiguous`)
- [ ] `normalizer_rules` unit_map rules added for mislabeled sources (if any)
- [ ] `catalog_renormalize` run if rules changed
- [ ] No regression in published PRD072 data

---

### C3: Blueberries Pack Research (CQ-P05)

**Owner:** Team 10  
**Expected effort:** < 1 session (research only — no code change)  
**V1 policy:** Display-only; no gram-normalized price calculation. Feeds Phase D ADR.

#### C3.1 Audit SQL

```sql
SELECT
  s.code AS source_code,
  s.name_he,
  rei.raw_product_name,
  rei.raw_unit_text,
  no2.normalized_price_value,
  mu.code AS unit
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD086'
  AND rei.is_quarantined = false
ORDER BY s.code;
```

#### C3.2 Research table format (required in completion report)

| source_code | source_name | raw_product_name | raw_unit | price | pack_description | grams_if_known | price_per_100g_calc |
|-------------|-------------|------------------|----------|-------|------------------|----------------|---------------------|
| SRC0XX | ... | "אוכמניות 125 גרם" | חבילה | ₪25 | 125g punnet | 125g | ₪20/100g |
| ... | | | | | | | |

**How to determine grams:**
- Check `raw_product_name` for gram values (regex: `\d+\s*(?:גרם|gr|g)`)
- If not in name: check source website directly (Team 10) or flag as "requires Team 80 field research"
- Target: ≥ 50% of sources with grams determined

**Backlog items for Phase D (Pantry ADR):** list any pack-size patterns observed that apply to PRD087–PRD100 (dry goods category). This research directly informs the D1 ADR.

#### C3.3 Exit Criteria (C3)

- [ ] Research table complete in completion report (all active PRD086 sources)
- [ ] ≥ 50% of sources have `grams_if_known` determined
- [ ] `price_per_100g_calc` column populated where grams known
- [ ] Backlog items for D1 (Pantry ADR) listed
- [ ] No code change — this is research only

---

### C4: CSA Basket Tier Mapping (CQ-P07)

**Owner:** Team 100 (policy) + Team 10 (implementation)  
**Expected effort:** Medium (1–2 sessions including tests)  
**This is the only Phase C item that creates new production code.**

#### C4.1 Files involved

| File | Action |
|------|--------|
| `organic_market_agent/normalizer/basket_tier_resolver.py` | NEW |
| `organic_market_agent/normalizer/basket_handler.py` | MODIFIED — calls tier resolver |
| `tests/test_basket_tier_resolver.py` | NEW — ≥ 8 test cases |

#### C4.2 basket_tier_resolver.py — full specification

```python
# organic_market_agent/normalizer/basket_tier_resolver.py
"""
Resolve CSA basket item → PRD025 (small), PRD026 (medium), or PRD027 (large).

Tier assignment policy (ARCH-20260406-CQ-MASTER §3.7.2, BINDING):
  Small  (PRD025): 5–8  items OR ₪80–130
  Medium (PRD026): 9–13 items OR ₪130–180   [default fallback]
  Large  (PRD027): 14+  items OR ₪170–250

Resolution order:
  1. Item count from csa_context_json (explicit item list or item_count field)
  2. Price-based range if no item count available
  3. Default PRD026 (medium) if neither available

Special cases:
  - item_count < 5: not a valid basket → return None (caller scope-skips)
  - Both count and price available: count takes priority
"""
from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import Product
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Tier ranges (BINDING — ARCH-20260406-CQ-MASTER §3.7.2)
_ITEM_COUNT_TIERS = [
    (5, 8, "PRD025"),    # small
    (9, 13, "PRD026"),   # medium
    (14, 9999, "PRD027"), # large
]

_PRICE_TIERS = [
    (Decimal("80"), Decimal("130"), "PRD025"),
    (Decimal("130"), Decimal("180"), "PRD026"),
    (Decimal("170"), Decimal("250"), "PRD027"),
]

_DEFAULT_TIER_CODE = "PRD026"
_NOTE_DEFAULT = "basket_tier_default_medium"
_NOTE_BY_COUNT = "basket_tier_by_item_count"
_NOTE_BY_PRICE = "basket_tier_by_price"
_NOTE_TOO_SMALL = "basket_too_small"
_NOTE_OVERSIZED = "basket_tier_oversized_default_large"


def _extract_item_count(csa_context_json: Optional[str]) -> Optional[int]:
    """
    Parse item count from csa_context JSON field.

    Supported formats:
      {"item_count": 10, ...}
      {"contents": ["item1", "item2", ...], ...}
      {"contents": "5 מוצרים", ...}  -- extract first integer

    Returns None if unparseable.
    """
    if not csa_context_json:
        return None
    try:
        data = json.loads(csa_context_json)
    except (json.JSONDecodeError, TypeError):
        # Try treating as plain-text line count (legacy format)
        lines = [l.strip() for l in str(csa_context_json).splitlines() if l.strip()]
        return len(lines) if len(lines) >= 2 else None

    if "item_count" in data and isinstance(data["item_count"], int):
        return data["item_count"]

    contents = data.get("contents")
    if isinstance(contents, list):
        return len(contents)
    if isinstance(contents, str):
        match = re.search(r"\d+", contents)
        if match:
            return int(match.group())

    return None


def _tier_by_count(count: int) -> Optional[str]:
    """Map item count to product code. Returns None if count < 5 (scope-skip signal)."""
    if count < 5:
        return None  # caller should add _NOTE_TOO_SMALL
    for low, high, code in _ITEM_COUNT_TIERS:
        if low <= count <= high:
            return code
    # count >= 14 already caught by last range; this handles edge case
    return "PRD027"


def _tier_by_price(price: Optional[Decimal]) -> Optional[str]:
    """Map price to product code using price range guidance."""
    if price is None or price <= 0:
        return None
    for low, high, code in _PRICE_TIERS:
        if low <= price <= high:
            return code
    if price < Decimal("80"):
        return None  # too cheap — likely not a full basket
    if price > Decimal("250"):
        return "PRD027"  # large basket, above defined range
    return None


def resolve_basket_tier(
    csa_context_json: Optional[str],
    price_amount: Optional[Decimal],
    session: Session,
) -> tuple[Optional[str], str]:
    """
    Determine basket tier product code.

    Returns:
        (product_code, resolution_note)
        product_code: PRD025/PRD026/PRD027 or None if basket is too small / invalid
        resolution_note: string to append to ctx.resolution_notes
    """
    count = _extract_item_count(csa_context_json)

    if count is not None:
        if count < 5:
            return (None, _NOTE_TOO_SMALL)
        code = _tier_by_count(count)
        return (code, _NOTE_BY_COUNT)

    # No item count — fall back to price
    price_code = _tier_by_price(price_amount)
    if price_code is not None:
        return (price_code, _NOTE_BY_PRICE)

    # Default fallback
    return (_DEFAULT_TIER_CODE, _NOTE_DEFAULT)


def run(ctx: NormContext, session: Session) -> NormContext:
    """
    Stage entry point: assign basket tier (product_id) based on csa_context and price.
    Called from basket_handler.run() when is_basket_product = True.
    """
    csa_context_raw = None
    if ctx.raw_payload_json:
        try:
            payload = json.loads(ctx.raw_payload_json) if isinstance(ctx.raw_payload_json, str) \
                      else ctx.raw_payload_json
            csa_context_raw = payload.get("csa_context") if isinstance(payload, dict) else None
        except (json.JSONDecodeError, TypeError):
            pass

    product_code, note = resolve_basket_tier(
        csa_context_json=csa_context_raw,
        price_amount=ctx.price_amount,
        session=session,
    )

    ctx.resolution_notes.append(note)

    if product_code is None:
        # Too small or invalid — keep existing product_id from alias stage
        logger.debug("basket_tier_resolver: no tier assigned (%s), keeping alias product_id=%s",
                     note, ctx.product_id)
        return ctx

    # Look up DB id for the resolved product code
    product_id = session.execute(
        sa.select(Product.id).where(Product.code == product_code, Product.is_active.is_(True))
    ).scalar_one_or_none()

    if product_id is None:
        logger.warning("basket_tier_resolver: product_code %s not found in DB", product_code)
        return ctx

    if ctx.product_id != product_id:
        logger.info("basket_tier_resolver: reassigning product %s → %s (%s)",
                    ctx.product_id, product_id, product_code)
        ctx.product_id = product_id

    return ctx
```

#### C4.3 basket_handler.py — modification

```python
# organic_market_agent/normalizer/basket_handler.py
# MODIFIED — add tier resolver call after price nullification
"""Stage 7: Enforce basket product policy — nullify price, assign tier via resolver."""
from __future__ import annotations

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.normalizer import basket_tier_resolver


def run(ctx: NormContext, session: Session) -> NormContext:
    """Basket products: nullify normalized price (V1 policy), then assign tier."""
    if not ctx.is_basket_product:
        return ctx

    # V1 policy: baskets do not carry normalized price
    ctx.normalized_price_value = None
    ctx.normalized_unit_id = None
    ctx.normalization_method = None
    ctx.resolution_notes.append("basket_product_no_normalization")

    # Assign tier (PRD025/026/027) based on csa_context and price
    ctx = basket_tier_resolver.run(ctx, session)

    return ctx
```

#### C4.4 tests/test_basket_tier_resolver.py — required test cases

All tests use only `resolve_basket_tier()` (unit tests, no DB):

```python
# tests/test_basket_tier_resolver.py
import json
from decimal import Decimal
import pytest
from unittest.mock import MagicMock

from organic_market_agent.normalizer.basket_tier_resolver import (
    resolve_basket_tier,
    _extract_item_count,
)


class TestExtractItemCount:
    def test_explicit_item_count_field(self):
        data = json.dumps({"item_count": 10, "price": 150})
        assert _extract_item_count(data) == 10

    def test_contents_as_list(self):
        data = json.dumps({"contents": ["עגבניות", "מלפפון", "גזר", "חסה", "פלפל",
                                        "בצל", "קישוא", "תרד", "כוסברה"]})
        assert _extract_item_count(data) == 9

    def test_contents_as_string_with_number(self):
        data = json.dumps({"contents": "12 מוצרים שבועיים"})
        assert _extract_item_count(data) == 12

    def test_none_when_empty(self):
        assert _extract_item_count(None) is None

    def test_none_when_no_count_fields(self):
        data = json.dumps({"price": 120})
        assert _extract_item_count(data) is None

    def test_plain_text_multiline(self):
        # Legacy format: multiline text with each line = one item
        text = "עגבניות\nמלפפון\nגזר\nחסה\nפלפל\nבצל"
        assert _extract_item_count(text) == 6


class TestResolveTier:
    def setup_method(self):
        self.mock_session = MagicMock()

    def test_tier_small_by_item_count(self):
        """6 items → PRD025 (small: 5–8 items)"""
        ctx_json = json.dumps({"item_count": 6})
        code, note = resolve_basket_tier(ctx_json, Decimal("100"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_item_count"

    def test_tier_medium_by_item_count(self):
        """11 items → PRD026 (medium: 9–13 items)"""
        ctx_json = json.dumps({"item_count": 11})
        code, note = resolve_basket_tier(ctx_json, Decimal("150"), self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_by_item_count"

    def test_tier_large_by_item_count(self):
        """15 items → PRD027 (large: 14+ items)"""
        ctx_json = json.dumps({"item_count": 15})
        code, note = resolve_basket_tier(ctx_json, Decimal("220"), self.mock_session)
        assert code == "PRD027"
        assert note == "basket_tier_by_item_count"

    def test_tier_medium_by_price_fallback(self):
        """No item count, price ₪150 → PRD026 (price range ₪130–180)"""
        code, note = resolve_basket_tier(None, Decimal("150"), self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_by_price"

    def test_tier_small_by_price_fallback(self):
        """No item count, price ₪95 → PRD025 (price range ₪80–130)"""
        code, note = resolve_basket_tier(None, Decimal("95"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_price"

    def test_tier_default_when_no_data(self):
        """No count, no price → PRD026 (default medium)"""
        code, note = resolve_basket_tier(None, None, self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_default_medium"

    def test_too_small_basket_returns_none(self):
        """< 5 items → None (scope-skip signal)"""
        ctx_json = json.dumps({"item_count": 3})
        code, note = resolve_basket_tier(ctx_json, Decimal("50"), self.mock_session)
        assert code is None
        assert note == "basket_too_small"

    def test_count_priority_over_price(self):
        """Item count takes priority over price even if price would resolve differently"""
        # 6 items → PRD025 regardless of price suggesting PRD026
        ctx_json = json.dumps({"item_count": 6})
        code, note = resolve_basket_tier(ctx_json, Decimal("160"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_item_count"
```

#### C4.5 catalog_renormalize + verification

After implementation:
```bash
python -m organic_market_agent catalog_renormalize
```

```sql
-- Verify tier distribution after renormalize
SELECT p.code, p.canonical_name_he, COUNT(*) AS obs_count
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.category = 'baskets' AND p.is_active = true
GROUP BY p.code, p.canonical_name_he
ORDER BY p.code;
-- Must show at least 1 row for ≥ 1 CSA source producing a deterministic tier
```

#### C4.6 Exit Criteria (C4)

- [ ] `organic_market_agent/normalizer/basket_tier_resolver.py` exists with full implementation
- [ ] `basket_handler.py` modified to call tier resolver
- [ ] `tests/test_basket_tier_resolver.py` exists with ≥ 8 test cases (all PASS)
- [ ] V1 policy maintained: `normalized_price_value = NULL` for all basket products
- [ ] ≥ 1 CSA source produces reproducible tier assignment to PRD025/026/027
- [ ] `catalog_renormalize` completed without error
- [ ] Tier distribution SQL result pasted in completion report
- [ ] No active aliases on PRD028/PRD029 (cross-check with A1)
- [ ] CHANGELOG updated under `[Unreleased]`

---

## Phase D — Architecture (after C3 research table)

### D1: Pantry ADR (CQ-P06)

**Owner:** Team 100 (spec) — this is authored by Team 100, not Team 10  
**Expected effort:** < 1 session  
**Note:** CQ-P06 is spec-only. Any implementation requires a separate mandate after ADR is signed.

#### D1.1 File to create

Team 100 produces:
`_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md`

#### D1.2 Required ADR content (binding structure)

**Context:** PRD087–PRD100 (quinoa, oats, tahini, silan, etc.) sell by pack. Fair comparison requires knowing net grams per pack to compute price-per-100g.

**Design options table (must appear in ADR):**

| Option | Approach | Pros | Cons | Verdict |
|--------|----------|------|------|---------|
| A | Title regex (`\d+\s*גרם` from `raw_product_name`) | Automated | Fragile; not all titles contain weight | Rejected for V1 |
| B | `product_variants` table `(product_id, source_id, pack_grams)` | Explicit, reliable, ~70 rows | Manual maintenance | **PREFERRED** |
| C | New `measurement_units` per pack size | Leverages conversion pipeline | Explosion of unit codes | Rejected |
| D | Hybrid (regex + B as override) | Best coverage | Two code paths | Future enhancement |

**Preliminary direction (ARCH-20260406-CQ-MASTER §3.6.3):** Approach B preferred.

**Team 10 spike scope (if needed before final decision):** Create one migration inserting 5 rows into a prototype `product_variants` table; demonstrate `price_per_100g = price / pack_grams * 100` calculation in `rolling_aggregate.py`. Report feasibility to Team 100.

**ADR sections:**
1. Context (why pack weight comparison matters)
2. Options analysis table (above)
3. Decision (Team 100 sign-off on approach B or amended choice)
4. Implementation plan (if chosen: new Alembic migration for `product_variants` table, seed data for PRD087–PRD100 × known sources, `rolling_aggregate.py` extension)
5. Out of scope (V1: no gram-normalized price in public JSON until implementation milestone is created)

#### D1.3 Exit Criteria (D1)

- [ ] ADR document created at specified path
- [ ] Approach B confirmed or alternative chosen with rationale
- [ ] Implementation plan present (future milestone scope)
- [ ] Team 100 sign-off signature in document

---

## Phase E — Final Validation

### E1: Final Full Pipeline Run + Regression + Upload

**Owner:** Team 10 + Nimrod  
**Expected effort:** 1 session  
**Note:** Run only after all Phase A–D work is complete and all tests pass.

#### E1.1 Full regression run

```bash
# Run full test suite (excluding live uPress tests)
pytest tests/ -m "not upress" -v
# Expected: 0 failures. All skips documented.
```

#### E1.2 Final pipeline run

```bash
python -m organic_market_agent scheduler.run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher --upload
```

#### E1.3 Privacy audit

```bash
# Verify no source codes or names leaked into public output
python3 -c "
import json, re
with open('output/public/public_report.json') as f:
    text = f.read()
    data = json.loads(text)

# Check for SRC patterns
src_matches = re.findall(r'SRC\d+', text)
if src_matches:
    print(f'FAIL: Source codes found: {set(src_matches)}')
else:
    print('Privacy check (SRC codes): PASS')
"
```

```bash
# Shell grep scan — run immediately after publish (expected: zero matches)
grep -R -n -E 'SRC[0-9]{3}' output/public/
# Expected output: (empty — no lines printed)
# Any match is a FAIL: source codes must not appear in any public output file
```

#### E1.4 Final exit criteria (E1)

- [ ] `pytest tests/ -m "not upress"` — 0 failures
- [ ] Published product count ≥ 77
- [ ] Unresolvable distinct names ≤ 20
- [ ] Zero duplicate `product_id` in `public_report.json`
- [ ] Privacy audit: zero SRC codes / source names in public JSON or HTML
- [ ] PRD027 appears at most once
- [ ] Cherry aliases on PRD001: 0 (re-run A1 SQL)
- [ ] Active aliases on PRD028/PRD029: 0 (re-run A1 SQL)
- [ ] FTPS upload to uPress succeeded (or documented reason for failure)
- [ ] CHANGELOG complete — all changes under `[Unreleased]`

---

## Completion Report Requirements

Team 10 files: `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_V1_1_COMPLETION_TEAM10.md`

Must include:

1. Before/after metrics table (from `catalog_scan_collect_metrics.py` output)
2. Triage table (A2) — all 92 names classified
3. Source × unit matrix for eggs (C1)
4. Source × unit matrix for passion fruit (C2)
5. Blueberries research table (C3)
6. CSA tier distribution SQL result (C4)
7. M10.x source status summary (A3) — what was improved, what remains as backlog
8. Ingestion run log excerpt (B1)
9. Final pytest output (E1) — pasted verbatim
10. Privacy audit result (E1)
11. Open items / known backlog (honest list)

---

## Escalation Protocol

| Situation | Action |
|-----------|--------|
| New product code needed (bucket b in A2) | Submit to Team 100: code proposal with `canonical_name_he`, `category`, `default_unit` |
| Ambiguous alias in triage | Escalate to Team 100 with raw name, source, two candidate products |
| Tier range adjustment needed for CSA (C4) | Submit data to Team 100; wait for policy update |
| egg_carton_6 unit needed (C1) | Submit to Team 100 for measurement_units approval |
| Blocking issue | File `BLOCKING_*_TEAM10.md` immediately |

---

**Authored by:** Team 100 (Architecture)  
**Document ID:** SPEC-20260408-PHASE-A-LOD400  
**Binding authority:** This document supersedes LOD200 descriptions in ARCH-20260406-CQ-MASTER for implementation precision. Policy decisions in CQ-MASTER remain binding.
