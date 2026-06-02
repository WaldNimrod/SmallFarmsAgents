---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — Team 20 Infrastructure Readiness: v1.1.0 LOD400

**Decision ID:** ARCH-20260408-TEAM20-RESPONSE-V1-1  
**From:** Team 100 (Architecture)  
**To:** Team 20 (Infrastructure), Team 10 (Feature Dev — orchestration)  
**CC:** Team 50 (QA), Nimrod (project lead)  
**Date:** 2026-04-08  
**Type:** CLARIFICATION + AMENDMENT  

---

## 1. Context

Team 20 filed infrastructure readiness review and information request at:
```
_COMMUNICATION/TEAM_20/reports/2026-04-08_V1_1_LOD400_INFORMATION_REQUEST_TEAM20.md
```

Seven items (4.1–4.7) were raised as blockers before Team 20 can author migration 072+. All seven are resolved here. Items 4.3, 4.4, and 4.5 were already addressed in `ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1` — cross-references provided below.

**Also actioned:** LOD400 spec (`SPEC-20260408-PHASE-A-LOD400`) was corrected in-place to fix all template SQL errors. An ERRATA table was added to the spec header listing ERR-01 through ERR-05.

**References:**
- `_COMMUNICATION/TEAM_20/reports/2026-04-08_V1_1_LOD400_INFORMATION_REQUEST_TEAM20.md` — triggering request
- `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` — LOD400 spec (corrected)
- `_COMMUNICATION/TEAM_100/reports/2026-04-08_TEAM50_CLARIFICATIONS_RESPONSE_TEAM100.md` — ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1

---

## 2. Findings

| Item | Finding | Severity |
|------|---------|----------|
| 4.1 scope_skip template | `rule_pattern` (wrong), missing `display_order` + `category_code` (both NOT NULL), `ON CONFLICT DO NOTHING` without target | Critical |
| 4.2 aliases template | `confidence_score` (wrong — column is `confidence`), `updated_at` (column does not exist on `product_aliases`), `ON CONFLICT DO NOTHING` without target | Critical |
| 4.3 CLI commands | Already resolved — see ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.5 | High (resolved) |
| 4.4 Pantry ADR owner | Already resolved — D1 is Team 100 deliverable — see ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.2 | High (resolved) |
| 4.5 basket_tier_resolver API | Already resolved — canonical API confirmed — see ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.3 | High (resolved) |
| 4.6 A4.3 psql example | `source_id` / `raw_name` / `raw_price` / `raw_unit` / `raw_text` wrong; `pending_manual` requires schema migration; single-step INSERT structurally impossible without FK deps | Critical |
| 4.7 H1 migration request channel | Not yet confirmed in writing | Medium |

---

## 3. Decision

### 3.1 — `catalog_scope_skip_rules` INSERT template (Team 20 item 4.1)

**RESOLVED. LOD400 spec §A2.3 corrected in-place (ERR-01).** The correct INSERT pattern is:

```python
# Tuple format: (display_order, category_code, pattern, match_type, notes)
# display_order: globally unique integer (uq_catalog_scope_skip_rules_display_order)
# category_code: one of donation | cleaning | dry_grocery | grocery | other
# match_type: one of exact | prefix | contains | regex

scope_skip_rules = [
    # (400, 'cleaning', 'שקית', 'contains', 'packaging material'),
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
```

**Finding `display_order` band for CQ-P01 batch:**
```sql
SELECT MAX(display_order) FROM catalog_scope_skip_rules;
```
Team 10's migration request must specify the starting `display_order` value for the new rules. Team 20 assigns contiguous integers from that start. Convention: use bands in increments of 10 (e.g. if MAX = 395, new rules use 400, 410, 420…).

---

### 3.2 — `product_aliases` INSERT template (Team 20 item 4.2)

**RESOLVED. LOD400 spec §A2.3 corrected in-place (ERR-02).** The correct INSERT pattern is:

```python
# Column corrections:
#   - confidence_score → confidence  (Numeric(3,2), server_default='1.0')
#   - updated_at DOES NOT EXIST on product_aliases — omit it
#   - ON CONFLICT target: (alias_text_normalized, source_id)

# GLOBAL aliases (source_id = NULL):
conn.execute(sa.text("""
    INSERT INTO product_aliases
      (alias_text, alias_text_normalized, product_id, source_id,
       is_active, confidence, created_at)
    SELECT
      :alias_text,
      lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
      p.id, NULL, true, :confidence, now()
    FROM products p
    WHERE p.code = :product_code
    ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
"""), ...)

# SOURCE-SCOPED aliases:
conn.execute(sa.text("""
    INSERT INTO product_aliases
      (alias_text, alias_text_normalized, product_id, source_id,
       is_active, confidence, created_at)
    SELECT
      :alias_text,
      lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
      p.id, s.id, true, :confidence, now()
    FROM products p, sources s
    WHERE p.code = :product_code AND s.code = :source_code
    ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
"""), ...)
```

**Key facts about `product_aliases` table:**
- No `updated_at` column (only `created_at`)
- Column is `confidence` not `confidence_score`
- Unique constraint: `uq_alias_text_source` on `(alias_text_normalized, source_id)` — `source_id` IS NULL for global aliases (PostgreSQL treats NULL as distinct in unique constraints — this is correct behavior)

---

### 3.3 — CLI commands (Team 20 item 4.3)

**Already resolved.** See `ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.5` for the canonical Phase B and Phase E CLI blocks. Summary:
```bash
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher  # add --upload for Phase E
```
`--all-sources` and `scheduler.run_ingestion` do not exist. No Team 20 action.

---

### 3.4 — Pantry ADR owner (Team 20 item 4.4)

**Already resolved.** See `ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.2`. D1 Pantry ADR is authored by Team 100 at a fixed path. No Team 20 involvement.

---

### 3.5 — `basket_tier_resolver` API (Team 20 item 4.5)

**Already resolved.** See `ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 §3.3`. The canonical signature is `(Optional[str], Optional[Decimal], Session) -> tuple[Optional[str], str]`. No schema dependency for Team 20.

---

### 3.6 — A4.3 psql example and SRC_WA schema (Team 20 item 4.6)

**RESOLVED. LOD400 spec §A4.3 corrected in-place (ERR-03, ERR-04).** Key findings:

**Column name corrections:**

| Wrong (original spec) | Correct (live schema) |
|----------------------|----------------------|
| `source_id` (direct on `raw_extracted_items`) | No `source_id` column — rows link to `sources` via `source_fetch_run_id` → `source_fetch_runs.source_id` |
| `raw_name` | `raw_product_name` |
| `raw_price` | `raw_price_text` (VARCHAR — not numeric) |
| `raw_unit` | `raw_unit_text` |
| `raw_text` | Does not exist |
| `s.source_code` | `s.code` |

**`pending_manual` status — new schema requirement:**

`pending_manual` is not currently a valid `extraction_status` value. The live CHECK constraint is:
```sql
chk_rei_extraction_status: extraction_status IN ('extracted','normalized','unresolvable','ignored')
```

**Decision:** The SRC_WA migration (migration numbering: see §3.7) **MUST** include an ALTER to extend this constraint:

```sql
-- In upgrade():
op.execute("ALTER TABLE raw_extracted_items DROP CONSTRAINT chk_rei_extraction_status")
op.execute("""
    ALTER TABLE raw_extracted_items ADD CONSTRAINT chk_rei_extraction_status
    CHECK (extraction_status IN ('extracted','normalized','unresolvable','ignored','pending_manual'))
""")

-- In downgrade():
op.execute("ALTER TABLE raw_extracted_items DROP CONSTRAINT chk_rei_extraction_status")
op.execute("""
    ALTER TABLE raw_extracted_items ADD CONSTRAINT chk_rei_extraction_status
    CHECK (extraction_status IN ('extracted','normalized','unresolvable','ignored'))
""")
```

**SRC_WA source row seed (same migration):**
```sql
INSERT INTO sources (
    code, name, base_url, source_group, market_scope, sales_channel,
    status, priority, is_active
) VALUES (
    'SRC_WA',
    'WhatsApp Community Submissions',
    NULL,
    'direct_price',
    'community',
    'community_direct',
    'active',
    3,
    true
) ON CONFLICT (code) DO NOTHING;
```

**Correct operator INSERT (4-step — corrected spec §A4.3):** See the corrected LOD400 spec §A4.3 for the full 4-step psql procedure using correct column names and FK chain.

**Migration number:** This SRC_WA migration is **separate from the CQ-P01 alias batch**. See §3.7 for migration numbering plan.

---

### 3.7 — Migration intake channel H1 (Team 20 item 4.7)

**CONFIRMED.** The `H1` handoff protocol is the **only** intake channel for Team 20 migration work in this release cycle.

**Process:**
1. Team 10 files: `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_072_REQUEST_TEAM10.md`
2. The request must include: full SQL or row-by-row spec, any A1 drift fix SQL, confirmation Team 10 has NOT run `alembic upgrade head`
3. Team 20 creates the revision file, applies `alembic upgrade head` on validation DB, files confirmation
4. Team 10 does NOT apply migrations unilaterally

**Revised migration numbering plan (due to `pending_manual` requirement):**

| Migration | Purpose | Owner | Prerequisite |
|-----------|---------|-------|-------------|
| 072 | CQ-P01 alias batch + scope-skip rules (A2) | Team 20 | Team 10 migration request filed |
| 073 | SRC_WA source row + `pending_manual` CHECK constraint extension (A4) | Team 20 | Team 100 confirms SRC_WA is approved |
| 074 | (Optional) A1 drift fix — only if §A1 SQL audit shows cherry/basket drift | Team 20 | Team 10 A1 audit results |

**If A1 drift fix is needed:** Team 10 files a separate migration request for A1; it takes the next available number after 073 or may be batched into 072 if the drift fix is small and Team 10 requests it before 072 is authored.

**SRC_WA approval gate:** Team 100 (Nimrod) must confirm `SRC_WA` is an approved source code before Team 20 seeds the row. This is not a Team 20 decision. **Status: APPROVED** — `SRC_WA` is referenced in the LOD400 spec §A4 and the WhatsApp protocol is in scope for M9C.

---

## 4. Amendments Issued

| Amendment ID | Target Document | Change |
|-------------|----------------|--------|
| AMD-T20-01 | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` | §A2.3: corrected `catalog_scope_skip_rules` INSERT (added `display_order`, `category_code`; fixed `pattern`; fixed `ON CONFLICT`); corrected `product_aliases` INSERT (fixed `confidence`, removed `updated_at`, fixed `ON CONFLICT`) |
| AMD-T20-02 | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` | §A4.3: rewritten psql example with correct columns, 4-step FK chain, `pending_manual` migration note |
| AMD-T20-03 | `_COMMUNICATION/TEAM_100/reports/2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md` | ERRATA table added at document header (ERR-01 through ERR-05) |

---

## 5. Next Steps

| Team | Action | When |
|------|--------|------|
| Team 20 | Use corrected templates from this document and amended spec §A2.3 for migration 072 authoring | After Team 10 files H1 migration request |
| Team 20 | Include `pending_manual` CHECK extension + SRC_WA seed row in migration 073 | After Team 10 files A4 migration request |
| Team 10 | File H1 migration request for alias batch (072) per HANDOFF §5.1 | After A2 triage complete (Phase A) |
| Team 10 | File H1 migration request for SRC_WA + pending_manual (073) | After A4 WhatsApp protocol document is drafted |
| Team 50 | Note: `pending_manual` in extraction_status is a valid post-migration status — include in T13 verification | Before G-V1.1 execution |

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-08*  
*This decision is binding on all teams unless overridden by Nimrod.*
