---
document_type: MANDATE
version: "1.0"
---

# Mandate — Dictionary Optimization for New easyFarm Sources (M10.2)
**Mandate ID:** MANDATE-20260404-M10-2-DICTIONARY-OPT
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-04
**Priority:** CRITICAL
**Gate dependency:** Blocks G10 quality threshold (≥90% resolution rate)
**Status:** ACTIVE

---

## 1. Context

Phase M10.1 activated 4 new easyFarm sources (SRC021–SRC024), extracting 1,487 raw items.
Of these, **662 items are unresolvable** — the normalization dictionary lacks product aliases,
canonical products, or scope-skip rules to handle them.

Current resolution metrics per source:

| Source | Code | Extracted | Resolved | Unresolvable | Scope Skipped | Resolution % |
|--------|------|-----------|----------|-------------|---------------|-------------|
| מהמשק | SRC021 | 1,119 | 146 | **545** | 428 | 21% |
| גן השדה | SRC022 | 283 | 100 | **96** | 87 | 51% |
| חווה באהבה | SRC023 | 63 | 30 | **16** | 17 | 65% |
| משק ימין אורד | SRC024 | 22 | 13 | **5** | 4 | 72% |

Target: ≥90% resolution rate across all active community sources.

**Triggered by:** M10.1 source activation — dictionary gaps exposed
**Related documents:**
- `_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_STATUS_AND_PHASE2_PLAN.md`
- `_COMMUNICATION/ROADMAP.md` (v5.0, M10.2)

---

## 2. Requirements

### Task 1 — Query and Categorize Unresolvable Items

Query all unresolvable items from SRC021–SRC024:

```sql
SELECT rei.raw_product_name, COUNT(*) AS cnt, s.code
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE rei.extraction_status = 'unresolvable'
  AND s.code IN ('SRC021', 'SRC022', 'SRC023', 'SRC024')
GROUP BY rei.raw_product_name, s.code
ORDER BY cnt DESC;
```

Categorize each into:
- **A) Alias needed** — raw name maps to existing product (e.g., "אבוקדו האס" → "אבוקדו")
- **B) New product needed** — legitimate produce not yet in catalog
- **C) Scope skip needed** — non-produce item (groceries, dairy, eggs, baked goods, cleaning, etc.)
- **D) Already resolved** — duplicate or already handled by another alias

**Acceptance criterion:** Complete categorization of all 662 unresolvable items documented in completion report.

---

### Task 2 — Add Product Aliases

For each Category A item, insert into `product_aliases`:

```sql
INSERT INTO product_aliases (product_id, alias_text, alias_text_normalized, confidence, status, is_active, created_at)
VALUES (<product_id>, '<raw_name>', '<normalized_name>', 0.95, 'approved', true, NOW());
```

Follow the established pattern from Farmerim optimization:
- Normalize Hebrew text (remove extra spaces, standardize quotes)
- Map variety names to base product (e.g., "תפוח עץ גרנד סמית" → תפוח עץ)
- Map size variants to base product (e.g., "בטטה קטנה" → בטטה)

**Acceptance criterion:** All Category A items have active aliases in DB.

---

### Task 3 — Create New Products

For each Category B item, insert into `products`:

```sql
INSERT INTO products (code, canonical_name_he, category, default_measurement_unit_id,
                      is_organic_required, is_basket_product, is_composite, is_active,
                      created_at, updated_at)
VALUES ('<PRDxxx>', '<name_he>', '<category>', <unit_id>, true, false, false, true, NOW(), NOW());
```

Then add the alias mapping to link raw names to the new product.

Use the existing category enum: `root_vegetables`, `fruiting_vegetables`, `leafy_greens`, `brassicas`, `alliums`, `cucurbits`, `legumes_fresh`, `baskets`, `fruits`, `eggs`.

**Acceptance criterion:** All Category B items have corresponding products + aliases. Product codes follow sequential `PRDxxx` numbering.

---

### Task 4 — Add Scope-Skip Rules

For each Category C item, insert into `catalog_scope_skip_rules`:

```sql
INSERT INTO catalog_scope_skip_rules (display_order, pattern, match_type, category_code,
                                       is_active, created_at, updated_at)
VALUES (<next_display_order>, '<pattern>', '<match_type>', '<category_code>', true, NOW(), NOW());
```

Use established categories: `donation`, `cleaning`, `dry_grocery`, `grocery`, `other`.
Use match_type: `exact`, `prefix`, `contains`, `regex` as appropriate.

**Acceptance criterion:** All Category C items are covered by scope-skip rules. Re-running normalization marks these as `ignored`.

---

### Task 5 — Re-normalize and Verify

After all dictionary updates:

```bash
.venv/bin/python -m organic_market_agent catalog_renormalize
```

Verify resolution rate:

```sql
SELECT
  COUNT(*) FILTER (WHERE extraction_status = 'normalized') AS normalized,
  COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unresolvable,
  COUNT(*) FILTER (WHERE extraction_status = 'ignored') AS ignored,
  ROUND(100.0 * COUNT(*) FILTER (WHERE extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS resolution_pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.is_active = true AND s.market_scope = 'community';
```

Iterate Tasks 1–4 until `resolution_pct ≥ 90.0`.

**Acceptance criterion:** `resolution_pct ≥ 90.0` for all active community sources combined.

---

### Task 6 — Publish Updated Data

After achieving the resolution threshold:

```bash
.venv/bin/python -m organic_market_agent run_publisher --upload
```

Verify updated product count on nimrod.bio/smallfarmsagent/.

**Acceptance criterion:** Published product count ≥ 70. FTPS upload successful.

---

## 3. Out of Scope

- Creating new parsers (covered by M10.3 mandate)
- Headless browser infrastructure (covered by M10.4)
- Phase B retail sources (covered by M10.5)
- Modifying the public HTML template structure
- Any changes to the aggregation or publish engine logic

---

## 4. Verification Checklist

Run these before submitting the completion report:

```bash
# Resolution rate check
docker exec oma-g2-ev psql -U oma -d organic -c "
SELECT
  COUNT(*) FILTER (WHERE extraction_status = 'normalized') AS normalized,
  COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unresolvable,
  ROUND(100.0 * COUNT(*) FILTER (WHERE extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.is_active = true AND s.market_scope = 'community';
"

# Publish + upload
.venv/bin/python -m organic_market_agent run_publisher --upload
```

Expected results:
- [ ] Resolution rate ≥ 90% for active community sources
- [ ] Published product count ≥ 70
- [ ] FTPS upload successful
- [ ] All existing tests still pass (no regression)

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using the canonical template:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_10/reports/2026-04-XX_M10_2_DICTIONARY_OPTIMIZATION_COMPLETE_TEAM10.md`

Include this Mandate ID in the report header.

**After filing the completion report, submit to Team 50 for QA validation.**
**After QA PASS, submit to Team 100 for architectural approval.**

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
