---
document_type: MANDATE
version: "1.0"
---

# Mandate — Static HTML Parser Development (M10.3)
**Mandate ID:** MANDATE-20260404-M10-3-STATIC-PARSERS
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-04
**Priority:** HIGH
**Gate dependency:** Blocks G10 source count threshold (≥4 new parsers)
**Status:** ACTIVE

---

## 1. Context

Phase M10.1 registered 4 standalone websites as candidate sources. These sites serve static HTML
(no JS rendering required) with public product/price listings. Each requires a dedicated parser.

| Source | Code | Platform | Est. Products | Key Selectors |
|--------|------|----------|--------------|---------------|
| ניצת הדובדבן | SRC025 | ASP.NET custom | 68 | `.productcubecontainer`, `.productcubepname`, `.productcubeprice` |
| המשק של בן | SRC026 | Rexail (Next.js) | 70 | `__NEXT_DATA__` JSON in `<script>` tag |
| ערן אורגני | SRC027 | Custom | TBD | Requires deep HTML analysis |
| הגינה של תמרי | SRC028 | Custom | TBD | Requires deep HTML analysis |

**Prerequisite:** M10.2 (Dictionary Optimization) should be substantially complete before starting
M10.3, as new parsers will generate additional unresolvable items requiring the same dictionary
optimization workflow.

**Triggered by:** M10.1 source registration — candidate sources pending activation
**Related documents:**
- `_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_STATUS_AND_PHASE2_PLAN.md`
- `_COMMUNICATION/TEAM_10/MANDATE_SOURCE_SPIKE_A0_TEAM10.md` (spike results)
- `_COMMUNICATION/ROADMAP.md` (v5.0, M10.3)

---

## 2. Requirements

### Task 1 — Deep HTML Analysis for SRC027 & SRC028

Perform detailed HTML structure analysis on:
- `https://www.eranorgani.co.il/` — identify product listing pages, catalog URLs, CSS selectors
- `https://shop.tamari-farm.co.il/` — identify product listing pages, catalog URLs, CSS selectors

For each, document:
- Product container selector
- Name selector
- Price selector
- Unit selector (if present)
- Pagination pattern (if any)
- Category/section URLs to crawl

**Acceptance criterion:** Documented selector map for each source, verified against live HTML.

---

### Task 2 — Create NizatParser (SRC025)

Create `organic_market_agent/parsers/nizat.py`:
- Target categories: `/ירקות-אורגניים-c28` (vegetables), `/פירות-אורגניים-c27` (fruits)
- Product container: `.productcubecontainer`
- Name: `.productcubepname`
- Price: `.productcubeprice`
- Unit: Parse from price text (e.g., `₪14.00 לק"ג` → price=14.00, unit=kg)
- Handle dual pricing (e.g., `60.00 ליח' , 12.00 לק"ג` — prefer per-kg price)

Register in `parsers/engine.py` `_PARSER_MAP`.

**Acceptance criterion:** Parser extracts ≥60 products from nizat.com with correct name/price/unit.

---

### Task 3 — Create RexailParser (SRC026)

Create `organic_market_agent/parsers/rexail.py`:
- Target: `https://www.bensfarm.co.il/` (and future Rexail-platform stores)
- Data source: `__NEXT_DATA__` JSON embedded in `<script id="__NEXT_DATA__">` tag
- Extract products from the JSON structure (navigate to products array)
- Parse: product name, price, unit, organic flag

Register in `parsers/engine.py` `_PARSER_MAP`.

**Acceptance criterion:** Parser extracts ≥60 products from bensfarm.co.il with correct name/price/unit.

---

### Task 4 — Create Parsers for SRC027 & SRC028

Based on Task 1 analysis, create appropriate parsers for:
- `organic_market_agent/parsers/eranorgani.py` (SRC027)
- `organic_market_agent/parsers/tamari.py` (SRC028)

Register in `parsers/engine.py` `_PARSER_MAP`.

**Acceptance criterion:** Each parser extracts products with correct name/price/unit from its target site.

---

### Task 5 — Database Configuration

For each new parser, update the database:

1. Update normalizer_type constraint (if new type needed):
```sql
ALTER TABLE normalizer_profiles DROP CONSTRAINT chk_np_normalizer_type;
ALTER TABLE normalizer_profiles ADD CONSTRAINT chk_np_normalizer_type
  CHECK (normalizer_type IN ('easyfarm_catalog', 'simple_product_grid', 'basket_only',
         'retail_benchmark', 'official_wholesale', 'farmerim',
         'nizat', 'rexail', 'eranorgani', 'tamari'));
```

2. Create fetch profiles with correct selectors:
```sql
INSERT INTO source_fetch_profiles (source_id, platform_family, fetch_mode, entry_url, selector_profile, is_active)
VALUES
  (25, 'nizat', 'html_page', 'https://www.nizat.com/פירות-וירקות-אורגניים-ניצת-הדובדבן-c2', '<selectors>'::jsonb, true),
  (26, 'rexail', 'html_page', 'https://www.bensfarm.co.il/', '<selectors>'::jsonb, true),
  (27, '<platform>', 'html_page', 'https://www.eranorgani.co.il/', '<selectors>'::jsonb, true),
  (28, '<platform>', 'html_page', 'https://shop.tamari-farm.co.il/', '<selectors>'::jsonb, true);
```

3. Create normalizer profiles:
```sql
INSERT INTO normalizer_profiles (source_id, normalizer_type, is_active) VALUES
  (25, 'nizat', true), (26, 'rexail', true), (27, '<type>', true), (28, '<type>', true);
```

4. Activate sources:
```sql
UPDATE sources SET is_active = true, status = 'active' WHERE id IN (25, 26, 27, 28);
```

**Acceptance criterion:** All 4 sources have active fetch profiles, normalizer profiles, and are set to `is_active=true`.

---

### Task 6 — Pipeline Runs and Dictionary Optimization

For each newly activated source:

```bash
.venv/bin/python -m organic_market_agent run_ingestion --run-type manual --source-code SRC025 --normalize
.venv/bin/python -m organic_market_agent run_ingestion --run-type manual --source-code SRC026 --normalize
.venv/bin/python -m organic_market_agent run_ingestion --run-type manual --source-code SRC027 --normalize
.venv/bin/python -m organic_market_agent run_ingestion --run-type manual --source-code SRC028 --normalize
```

After initial runs, perform dictionary optimization (same workflow as M10.2):
1. Query unresolvable items
2. Add aliases, new products, scope-skip rules
3. Re-normalize until ≥85% resolution per source

**Acceptance criterion:** Each source achieves ≥85% resolution rate. Combined active community resolution remains ≥90%.

---

### Task 7 — Publish and Upload

After all sources are optimized:

```bash
.venv/bin/python -m organic_market_agent run_publisher --upload
```

**Acceptance criterion:** Published product count ≥ 80. FTPS upload successful.

---

## 3. Out of Scope

- Headless browser / Playwright infrastructure (M10.4)
- mypips.app sources (M10.4)
- CSA basket sources (M10.5)
- Phase B retail sources (M10.5)
- Modifications to aggregation logic or publish engine
- Public template UI changes beyond what was delivered in M10.1

---

## 4. Verification Checklist

Run these before submitting the completion report:

```bash
# Per-source extraction test
for src in SRC025 SRC026 SRC027 SRC028; do
  echo "=== $src ===" && .venv/bin/python -m organic_market_agent run_ingestion \
    --run-type manual --source-code $src --normalize
done

# Overall resolution rate
docker exec oma-g2-ev psql -U oma -d organic -c "
SELECT s.code, s.name,
  COUNT(*) FILTER (WHERE extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN ('SRC025','SRC026','SRC027','SRC028')
GROUP BY s.code, s.name;
"

# Publish
.venv/bin/python -m organic_market_agent run_publisher --upload
```

Expected results:
- [ ] SRC025 extracts ≥60 products
- [ ] SRC026 extracts ≥60 products
- [ ] SRC027 extracts products (count TBD after Task 1)
- [ ] SRC028 extracts products (count TBD after Task 1)
- [ ] Per-source resolution rate ≥85%
- [ ] Combined community resolution rate ≥90%
- [ ] Published product count ≥80
- [ ] FTPS upload successful
- [ ] All existing tests still pass (no regression)

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using the canonical template:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_10/reports/2026-04-XX_M10_3_STATIC_PARSERS_COMPLETE_TEAM10.md`

Include this Mandate ID in the report header.

**After filing the completion report, submit to Team 50 for QA validation.**
**After QA PASS, submit to Team 100 for architectural approval.**

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide
4. Common blockers:
   - Site structure changed since spike → re-analyze HTML, update selectors
   - Site returns 403/anti-bot → report to Team 100 for alternative approach
   - Products require login → report to Team 100 for deprioritization decision

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
