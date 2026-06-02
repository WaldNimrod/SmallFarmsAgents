# Team 100 — Architectural Approval: Catalog Quality Packages CQ-P01 through CQ-P09

**Document ID:** ARCH-20260406-CQ-MASTER  
**Date:** 2026-04-06  
**Author:** Team 100 (Architecture)  
**Status:** APPROVED — binding for all 9 packages  
**LOD:** 200 (task groups, measurable targets, parallelism decisions, verification SQL)  
**Supersedes:** LOD 100 stubs in ROADMAP.md v5.6 § Post-M13

---

## 1. Executive Summary

Team 10 defined 9 Catalog Quality packages (CQ-P01–CQ-P09) at LOD 100 in ROADMAP v5.6. This document promotes all 9 to **LOD 200**, adding:

- Measurable numeric targets and exit thresholds
- Verification SQL for every package
- Explicit parallelism authorization (phased lanes)
- Binding architectural decisions where Team 100 sign-off was required
- Data quality finding: PRD027 appears **twice** in current `public_report.json` — investigate in CQ-P02

**Current baseline (2026-04-06):**

| Metric | Value |
|--------|-------|
| Published products | **77** |
| Distinct unresolvable names | **92** (SRC021: **61**) |
| Alembic head | **071** |
| Basket products published | PRD025, PRD026, PRD027 (×2 duplicate) |
| PRD072 published unit | יחידה (should be kg for most sources) |
| PRD086 published unit | חבילה / אריזה (pack size unknown) |
| PRD067 published unit | אריזת 12 ביצים (correct for 12-pack sources) |
| Inactive basket codes | PRD028, PRD029 (migration 017 + 068) |

---

## 2. Execution Phasing & Parallelism Decision

**BINDING:** Team 100 approves the following phased parallel execution.

```
Phase α (foundation)     ┌─ CQ-P01 (alias backlog)
                         ├─ CQ-P08 (tomato guard) ──┐
                         └─ CQ-P09 (basket codes) ──┤ pure DB audit, no data dependency
                                                     │
Phase β (full run)       └─ CQ-P02 ────────────────── depends on P01 complete
                                                     │
Phase γ (product fixes)  ┌─ CQ-P03 (eggs) ──────────┤
  all parallel after P02 ├─ CQ-P04 (passion fruit) ──┤ independent product-specific
                         ├─ CQ-P05 (blueberries) ────┤ unit/alias fixes
                         └─ CQ-P07 (CSA baskets) ────┘
                                                     │
Phase δ (architecture)   └─ CQ-P06 (pantry ADR) ──── depends on P05 pattern + Team 100
```

**Rules:**
1. Phase α packages may run concurrently. CQ-P08 and CQ-P09 are pure audit — no migration risk to P01 alias work.
2. CQ-P02 **must** wait for CQ-P01 completion (fewer unresolvables = cleaner run).
3. Phase γ packages may run concurrently once CQ-P02 is complete (fresh data available).
4. CQ-P06 starts **after** CQ-P05 delivers its research table — the P05 pack-size pattern informs the P06 ADR.
5. Any package may start its **Team 100 architectural review** sub-step at any time (documentation only).

**Estimated total effort:** ~3–4 working sessions for Phase α+β; ~2 sessions for Phase γ; ~1 session for Phase δ.

---

## 3. Package Specifications (LOD 200)

---

### CQ-P01 — Unresolvable Alias Backlog Clearance

**Phase:** α (first priority)  
**Owner:** Team 10 (data) + Team 20 (migration)  
**Effort:** Medium (1–2 sessions)

#### 3.1.1 Baseline & Targets

| Metric | Baseline (2026-04-06) | Target |
|--------|-----------------------|--------|
| Distinct unresolvable raw names | 92 | **≤ 20** |
| SRC021 unresolvable count | 61 | **≤ 10** |
| Published product count | 77 | **≥ 77** (no regression) |

#### 3.1.2 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | Export current unresolvable list: `GET /unresolved/export.json?limit=500` | Team 10 |
| 2 | Triage names into buckets: (a) clear alias match, (b) new product needed, (c) scope-skip candidate, (d) ambiguous — escalate to Team 100 | Team 10 |
| 3 | For bucket (a): create Alembic migration `072_cq_p01_alias_batch.py` with `INSERT INTO product_aliases` (global or source-scoped per triage) | Team 10 + Team 20 |
| 4 | For bucket (c): add `catalog_scope_skip_rules` in same or separate migration | Team 10 |
| 5 | For bucket (b): list proposed new product codes → Team 100 approval REQUIRED before insert | Team 10 → Team 100 |
| 6 | Run `catalog_renormalize` and verify counts | Team 10 |
| 7 | Capture before/after metrics in completion report | Team 10 |

#### 3.1.3 Alias Policy (BINDING)

- **Default:** global alias (source_id NULL) unless the same Hebrew string maps to different products on different sources.
- **Source-scoped:** only when ambiguity is documented (e.g., "ירוקים" means different things on SRC021 vs SRC004).
- **New product codes:** require Team 100 pre-approval with proposed `code`, `canonical_name_he`, `category`, `default_measurement_unit_id`.
- **Confidence:** global aliases at 0.90; source-scoped at 0.95.

#### 3.1.4 Verification SQL

```sql
-- Before/after unresolvable count
SELECT COUNT(DISTINCT raw_product_name)
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable' AND is_quarantined = false;

-- SRC021 breakdown
SELECT COUNT(DISTINCT raw_product_name)
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE s.code = 'SRC021' AND rei.extraction_status = 'unresolvable' AND rei.is_quarantined = false;
```

#### 3.1.5 Exit Criteria

- [ ] Distinct unresolvable names ≤ 20
- [ ] SRC021 unresolvable ≤ 10
- [ ] No new product codes without Team 100 approval record
- [ ] All new aliases have confidence ≥ 0.90
- [ ] Published product count ≥ 77 (no regression)
- [ ] Before/after metrics in completion report

---

### CQ-P02 — Full Ingestion Run to Completion

**Phase:** β (after P01)  
**Owner:** Team 10 + Nimrod (operator machine)  
**Effort:** Small–Medium (1 session)

#### 3.2.1 Targets

| Metric | Target |
|--------|--------|
| `IngestionRun` status | `succeeded` |
| Published product count | **≥ 77** (no regression from P01 exit) |
| Run completion | Full — all active sources attempted, no timeout abort |

#### 3.2.2 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | Ensure `pg_dump` or `scripts/backup_postgres.sh` available; take pre-run backup | Nimrod / Team 20 |
| 2 | `python -m organic_market_agent.scheduler.run_ingestion --run-type manual --normalize` — full run, monitor for timeouts | Team 10 + Nimrod |
| 3 | If any source fails with timeout: document source code + error; file as CQ hotfix ticket (not blocking) | Team 10 |
| 4 | `python -m organic_market_agent.scheduler.run_aggregator` | Team 10 |
| 5 | `python -m organic_market_agent.scheduler.run_publisher` | Team 10 |
| 6 | Verify `output/public/public_report.json` product count and timestamp | Team 10 |
| 7 | **Investigate PRD027 duplicate** in published output (two rows with same product_id) — root cause and fix | Team 10 |

#### 3.2.3 PRD027 Duplicate Investigation (REQUIRED)

Current `public_report.json` contains PRD027 ("סל ירקות גדול") **twice** with different `avg_price` values (194.8 and 145.0). This indicates either a rolling aggregate bug or a source-level duplicate. Team 10 must:

1. Query `daily_aggregates` for PRD027 — check for distinct aggregation keys producing separate rows
2. If rolling_aggregate groups by `(product_id, source_type)` or similar, the PRD027 duplicate may come from two `display_bucket` source categories. Determine correct behavior and fix.
3. If this is a legitimate grouping (e.g., grower vs store basket), document as intentional. Otherwise, fix in rolling_aggregate.

#### 3.2.4 Verification

```sql
-- Ingestion run status
SELECT id, run_type, status, started_at, finished_at,
       sources_attempted, sources_succeeded, sources_failed
FROM ingestion_runs ORDER BY id DESC LIMIT 1;

-- Published product count (after run_publisher)
-- Check output/public/public_report.json with jq or Python

-- PRD027 duplicate check
SELECT product_id, COUNT(*) as row_count
FROM daily_aggregates
WHERE product_id = (SELECT id FROM products WHERE code = 'PRD027')
GROUP BY product_id;
```

#### 3.2.5 Exit Criteria

- [ ] IngestionRun completed with status `succeeded`
- [ ] All active sources attempted (failures documented, not blocking)
- [ ] Published product count ≥ 77
- [ ] PRD027 duplicate investigated and resolved or documented as intentional
- [ ] Run log excerpt or audit row in completion report
- [ ] Pre-run backup confirmed taken

---

### CQ-P03 — Eggs (PRD067): Per-Source Unit Semantics

**Phase:** γ (parallel, after P02)  
**Owner:** Team 10  
**Effort:** Small (< 1 session)

#### 3.3.1 Current State

PRD067 (ביצים) currently publishes with unit `אריזת 12 ביצים` (egg_carton_12). The `_BUILTIN_UNIT_MAP` already maps "12 ביצים", "אריזת 12", "12 ביצ" → `egg_carton_12`. Migration 069 set egg_carton_12 as default.

**Potential issue:** Sources selling loose eggs (per unit) or 6-packs may be incorrectly mapped to 12-pack via the product default fallback.

#### 3.3.2 Targets

| Metric | Target |
|--------|--------|
| Source × unit matrix | Complete for all sources carrying PRD067 |
| Egg observations with correct unit | **≥ 90%** of observations labeled `egg_carton_12` where source sells 12-packs |
| Exception sources documented | Any source selling loose or 6-pack eggs explicitly listed |

#### 3.3.3 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | SQL audit: all sources with PRD067 observations, grouped by `raw_unit_text` | Team 10 |
| 2 | For each source: verify the `raw_unit_text` maps correctly through unit_resolver | Team 10 |
| 3 | If any source sells loose eggs (per-unit pricing): add `normalizer_rules` unit_map (source-scoped) to prevent fallback to egg_carton_12 | Team 10 |
| 4 | If 6-pack sources exist: propose `egg_carton_6` unit to Team 100 (requires measurement_units insert) | Team 10 → Team 100 |
| 5 | Document matrix in completion report | Team 10 |

#### 3.3.4 Verification SQL

```sql
-- Source × unit matrix for PRD067
SELECT s.code, s.name_he,
       rei.raw_unit_text,
       COUNT(*) as obs_count
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
WHERE p.code = 'PRD067' AND rei.is_quarantined = false
GROUP BY s.code, s.name_he, rei.raw_unit_text
ORDER BY s.code, obs_count DESC;
```

#### 3.3.5 Exit Criteria

- [ ] Source × unit matrix complete in completion report
- [ ] ≥ 90% of egg observations have correct unit mapping
- [ ] Any exception sources (loose, 6-pack) documented with remediation plan or explicit waiver
- [ ] No regression in published PRD067 data

**Team 100 decision:** If a source sells eggs by-the-single-unit (not carton), that source's egg observations should use unit `unit` via a source-scoped `normalizer_rules` row — do NOT fall back to egg_carton_12 for per-unit pricing. Approved.

---

### CQ-P04 — Passion Fruit (PRD072): kg vs Pack Disambiguation

**Phase:** γ (parallel, after P02)  
**Owner:** Team 10  
**Effort:** Small (< 1 session)

#### 3.4.1 Current State

- PRD072 default unit: **kg** (set by migration 069)
- Published report shows unit **יחידה** (unit) — the unit_resolver falls back to product default only if no builtin match, but "יחידה" matches `_BUILTIN_UNIT_MAP["יחידה"] = "unit"` explicitly. So the unit "unit" is **correct per source data**, not a fallback error.
- Exceptions register: 10 historical rows still with unit "יחידה"
- The real question: are these sources selling **single fruits** (unit pricing is correct) or **by kg** (unit text is wrong)?

#### 3.4.2 Targets

| Metric | Target |
|--------|--------|
| Source × unit matrix for PRD072 | Complete |
| Mixed-unit bucket | Explained per source OR unit_map rules added |

#### 3.4.3 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | SQL audit: all sources with PRD072 observations, grouped by `raw_unit_text` | Team 10 |
| 2 | For each "יחידה" source: inspect original `raw_payload_json` to determine if price is per-fruit or per-kg | Team 10 |
| 3 | If source sells by kg but lists "יחידה": add source-scoped `normalizer_rules` unit_map overriding "יחידה" → "kg" for that source + PRD072 | Team 10 |
| 4 | If source genuinely sells per-fruit: document as correct, no change | Team 10 |
| 5 | Document matrix + decisions in completion report | Team 10 |

#### 3.4.4 Verification SQL

```sql
-- Source × unit × price for PRD072
SELECT s.code, s.name_he,
       rei.raw_unit_text,
       no2.normalized_price_value,
       mu.code as display_unit_code,
       COUNT(*) as obs_count
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD072' AND rei.is_quarantined = false
GROUP BY s.code, s.name_he, rei.raw_unit_text, no2.normalized_price_value, mu.code
ORDER BY s.code;
```

#### 3.4.5 Exit Criteria

- [ ] Source × unit matrix complete
- [ ] Each "יחידה" source classified: genuine per-fruit vs mislabeled kg
- [ ] unit_map rules added for mislabeled sources (if any)
- [ ] No regression in published PRD072 data
- [ ] Decision documented in completion report

**Team 100 decision — kg-default vs unit-default policy:**  
PRD072 product default remains **kg** (migration 069). Sources selling single fruits are correctly mapped to **unit** by the builtin map. No change to product default. Source-scoped overrides only for sources where "יחידה" is demonstrably wrong (parser extracting kg-priced items but labeling them "יחידה"). Approved.

---

### CQ-P05 — Blueberries (PRD086): Tray/Pack Size by Source

**Phase:** γ (parallel, after P02)  
**Owner:** Team 10 + Team 80 (field research if needed)  
**Effort:** Small (< 1 session, primarily research)

#### 3.5.1 Current State

- PRD086 (אוכמניות) publishes with unit `חבילה / אריזה` (retail_pack)
- avg_price = 25.67, sources: grower + store
- Pack sizes vary by source (125g vs 200g vs 250g) — currently undifferentiated

#### 3.5.2 Targets

| Metric | Target |
|--------|--------|
| Source × pack description table | Complete for all sources carrying PRD086 |
| Gram weight mapped | Where determinable from title or field knowledge |
| V1 decision | Display-only vs partial conversion — Team 100 decides |

#### 3.5.3 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | SQL audit: all sources with PRD086 observations; extract `raw_product_name`, `raw_unit_text`, `raw_payload_json` | Team 10 |
| 2 | For each source: attempt to determine pack grams from product title (e.g., "אוכמניות 125 גרם") | Team 10 |
| 3 | If title doesn't reveal weight: check source website or flag as "unknown" | Team 10 / Team 80 |
| 4 | Build research table: `source_code × pack_description × grams_if_known × price_per_100g_calc` | Team 10 |
| 5 | Propose implementation path for pack-weight normalization (future CQ-P06 or stand-alone) | Team 10 |

#### 3.5.4 Verification SQL

```sql
-- PRD086 raw data audit
SELECT s.code, s.name_he,
       rei.raw_product_name,
       rei.raw_unit_text,
       no2.normalized_price_value,
       mu.code as display_unit_code
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD086' AND rei.is_quarantined = false
ORDER BY s.code;
```

#### 3.5.5 Exit Criteria

- [ ] Research table with all sources mapped or explicitly marked "unknown"
- [ ] At least 50% of sources have grams determined
- [ ] Backlog items listed for implementation (feeds CQ-P06)
- [ ] No code changes required in this package (research only)

**Team 100 decision — V1 display policy:**  
V1 remains **display-only** — pack size information is documented but NOT used for gram-normalized comparison in the public index. The research table feeds CQ-P06 architectural design. Prices remain as-is (per pack). Approved.

---

### CQ-P06 — Pantry Dry Goods: Pack Weight Comparison Path (ADR)

**Phase:** δ (after P05 research table)  
**Owner:** Team 100 (spec) + Team 10 (spike)  
**Effort:** Medium (architecture decision + optional spike)

#### 3.6.1 Context

PRD087–PRD100 (quinoa, oats, silan, tahini, etc.) from SRC036 (Teva Shuk / Sellio) and potentially other retail sources sell by pack. Fair comparison requires knowing net grams per pack.

#### 3.6.2 Design Options

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| A | **Title regex extraction** — parse "500 גרם" from `raw_product_name` into new `pack_grams` field on `normalized_observations` | Automated, scales | Regex fragile; not all titles contain weight |
| B | **Product variants table** — new `product_variants` with `(product_id, source_id, pack_grams)` seeded by Team 10 | Explicit control, accurate | Manual maintenance per source×product |
| C | **Unit conversion extension** — add per-pack-size `measurement_units` (e.g., `pack_500g_quinoa`) with `unit_conversions` to `kg` | Leverages existing conversion pipeline | Explosion of unit codes |
| D | **Hybrid** — regex for extraction, product_variants as override/fallback | Best coverage | Two code paths to maintain |

#### 3.6.3 Team 100 Preliminary Direction

**Approach B** (product variants) is preferred for V1:
- Reliability over automation at this scale (~14 products × ~5 sources = ~70 rows)
- No parser changes needed
- Can be seeded via Alembic migration
- Future: Option A as enhancement when more retail sources join

**FINAL DECISION deferred** to the CQ-P06 execution phase — Team 10 must deliver the spike demonstrating approach B feasibility before Team 100 signs the binding ADR.

#### 3.6.4 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | Review CQ-P05 research table for pattern applicability to pantry SKUs | Team 100 |
| 2 | Create ADR draft: `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md` | Team 100 |
| 3 | Optional: Team 10 spike — prototype `product_variants` table, seed 5 rows, demonstrate price-per-100g calc | Team 10 |
| 4 | Team 100 signs ADR with chosen approach | Team 100 |
| 5 | If approach chosen: slice into implementation milestone(s) CQ-P06a/b | Team 100 |

#### 3.6.5 Exit Criteria

- [ ] Signed ADR document by Team 100
- [ ] Approach A, B, C, or D selected with rationale
- [ ] Implementation milestone(s) sliced if approach involves code
- [ ] No production code changes in this package (spec only unless spike approved)

---

### CQ-P07 — CSA Baskets: Line-Count → Basket Tier (PRD025/026/027)

**Phase:** γ (parallel, after P02)  
**Owner:** Team 100 (policy) + Team 10 (implementation)  
**Effort:** Medium (policy + code)

#### 3.7.1 Current State

- PRD025 (small), PRD026 (medium), PRD027 (large) active in catalog
- PRD028 (family) and PRD029 (CSA weekly) merged to PRD027/PRD026 respectively (migrations 017, 068)
- CSA sources (SRC033–SRC035) extract basket items; parser may produce basket lines but tier assignment is manual/undefined
- Current `basket_handler.py` sets `normalized_price_value = None` for all baskets (V1 policy)

#### 3.7.2 Tier Policy Ranges (BINDING)

Based on observable CSA basket sizes in Israeli organic market:

| Tier | Product Code | Item Line Count Range | Price Range Guidance |
|------|-------------|----------------------|---------------------|
| Small | PRD025 | 5–8 items | ₪80–₪130 |
| Medium | PRD026 | 9–13 items | ₪130–₪180 |
| Large | PRD027 | 14+ items | ₪170–₪250 |

**Edge cases:**
- If item count is unavailable: fall back to **price-based** tier assignment using the price range guidance
- If both unavailable: assign to **PRD026** (medium) as default with `resolution_notes` entry
- Baskets with < 5 items: scope-skip (likely not a full basket offering)

**These ranges are LOD 200 estimates.** Team 10 must validate against actual CSA source data during implementation and propose adjustments if data contradicts. Team 100 will sign final ranges in the package-level arch approval.

#### 3.7.3 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | Audit SRC033–SRC035: what basket data is currently extracted? Item counts? Price? | Team 10 |
| 2 | Implement tier assignment logic in `basket_handler.py` or new `basket_tier_resolver.py` stage | Team 10 |
| 3 | Logic: if `csa_context` contains item list → count items → apply range table → set `product_id` | Team 10 |
| 4 | If no item list: use price → range table → set `product_id` | Team 10 |
| 5 | Default fallback: PRD026 + resolution_note | Team 10 |
| 6 | Unit test: ≥ 3 scenarios (small by count, large by count, fallback by price) | Team 10 |
| 7 | Run `catalog_renormalize` for CSA sources; verify tier assignment in `normalized_observations` | Team 10 |

#### 3.7.4 Verification SQL

```sql
-- CSA basket tier distribution after implementation
SELECT p.code, p.canonical_name_he,
       COUNT(*) as obs_count,
       AVG(no2.normalized_price_value) as avg_price
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.category = 'baskets' AND p.is_active = true
GROUP BY p.code, p.canonical_name_he
ORDER BY p.code;

-- Check no aliases still point at PRD028/PRD029
SELECT pa.alias_text, p.code as target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029') AND pa.is_active = true;
```

#### 3.7.5 Exit Criteria

- [ ] ≥ 1 CSA source produces deterministic tier assignment (reproducible in test harness)
- [ ] Tier ranges validated against actual source data
- [ ] Unit tests pass for small/medium/large/fallback scenarios
- [ ] V1 policy unchanged: `normalized_price_value = NULL` for basket products (tier assignment only sets product_id)
- [ ] No orphan basket aliases on PRD028/PRD029 (cross-check with CQ-P09)

---

### CQ-P08 — Tomato vs Cherry Tomato Regression Guard (PRD001 / PRD002)

**Phase:** α (can run immediately, pure DB audit)  
**Owner:** Team 20 (migration audit) + Team 10 (validator)  
**Effort:** Small (< 0.5 session)

#### 3.8.1 Context

PRD001 = עגבנייה (tomato), PRD002 = עגבנייה שרי (cherry tomato). Risk: alias containing "שרי" incorrectly mapped to PRD001.

#### 3.8.2 Cherry-Keyword Tokens (BINDING)

The following Hebrew tokens MUST map exclusively to PRD002 (cherry tomato), NEVER to PRD001:

- `שרי`
- `cherry`
- `צ'רי`
- `שרי צהוב` (yellow cherry)
- `שרי אדום` (red cherry)

Conversely, bare `עגבנייה` / `עגבניות` without cherry qualifier → PRD001.

#### 3.8.3 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | DB audit: check all active aliases for PRD001 — none should contain cherry tokens | Team 10 |
| 2 | DB audit: check all active aliases for PRD002 — confirm cherry tokens present | Team 10 |
| 3 | Spot-check: sample `normalized_observations` for PRD001 — verify no cherry items | Team 10 |
| 4 | If drift found: create fix-forward migration | Team 20 |
| 5 | Optional: add CI-compatible check script `scripts/check_tomato_cherry_guard.sql` | Team 10 |
| 6 | Confirm `docs/GLOSSARY.md` distinguishes PRD001/PRD002 | Team 10 |

#### 3.8.4 Verification SQL

```sql
-- MUST return 0 rows (no cherry aliases on PRD001)
SELECT pa.id, pa.alias_text, pa.alias_text_normalized, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001' AND pa.is_active = true
  AND (pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
    OR pa.alias_text_normalized LIKE '%צ''רי%');

-- SHOULD return ≥ 1 row (cherry aliases on PRD002 exist)
SELECT pa.id, pa.alias_text, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD002' AND pa.is_active = true
  AND (pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%');

-- Spot-check: no cherry products resolved to PRD001
SELECT rei.raw_product_name, no2.product_id, p.code
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
JOIN raw_extracted_items rei ON no2.raw_extracted_item_id = rei.id
WHERE p.code = 'PRD001'
  AND (rei.raw_product_name LIKE '%שרי%'
    OR rei.raw_product_name LIKE '%cherry%');
```

#### 3.8.5 Exit Criteria

- [ ] Zero `product_aliases` rows matching cherry tokens → PRD001
- [ ] ≥ 1 cherry alias confirmed on PRD002
- [ ] Spot-check: zero cherry items in PRD001 `normalized_observations`
- [ ] Glossary confirmed aligned
- [ ] Confirmation report filed

---

### CQ-P09 — Inactive Basket Codes PRD028/PRD029: Alias Target Enforcement

**Phase:** α (can run immediately, pure DB audit)  
**Owner:** Team 20 + Team 10  
**Effort:** Small (< 0.5 session)

#### 3.9.1 Context

Migration 017 merged PRD028 → PRD027 and PRD029 → PRD026, setting both as `is_active = false`. Migration 068 re-pointed remaining aliases. Risk: subsequent migrations or manual DB edits may have re-introduced aliases on inactive codes.

#### 3.9.2 Task Breakdown

| # | Task | Owner |
|---|------|-------|
| 1 | DB audit: check for any active aliases targeting PRD028 or PRD029 | Team 10 |
| 2 | DB audit: confirm PRD028 and PRD029 remain `is_active = false` | Team 10 |
| 3 | DB audit: check `normalized_observations` for any rows still on PRD028/PRD029 product_id | Team 10 |
| 4 | If drift found: create fix-forward migration `07X_cq_p09_enforce_basket_merge.py` | Team 20 |
| 5 | Document catalog merge policy as unchanged | Team 10 |

#### 3.9.3 Verification SQL

```sql
-- MUST return 0 rows (no active aliases on inactive basket codes)
SELECT pa.id, pa.alias_text, p.code as target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029') AND pa.is_active = true;

-- Confirm inactive status
SELECT code, canonical_name_he, is_active
FROM products
WHERE code IN ('PRD028', 'PRD029');

-- MUST return 0 rows (no observations on inactive codes)
SELECT COUNT(*) as orphan_count
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029');

-- CSA aliases target correct codes
SELECT pa.alias_text, p.code as target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE pa.alias_text_normalized LIKE '%סל%' AND pa.is_active = true
ORDER BY p.code;
```

#### 3.9.4 Exit Criteria

- [ ] Zero active aliases on PRD028/PRD029
- [ ] PRD028 and PRD029 confirmed `is_active = false`
- [ ] Zero `normalized_observations` rows on PRD028/PRD029
- [ ] CSA basket aliases confirmed targeting PRD025/026/027 only
- [ ] Catalog merge policy documented as unchanged

**Team 100 decision:** Catalog merge policy for baskets remains as defined in migration 017. PRD028 and PRD029 are permanently inactive. Any future basket tier needs are addressed via PRD025/026/027 only. Approved.

---

## 4. Cross-Package Quality Gates

### 4.1 Governance Flow (per package)

```
Team 10 implementation
    ↓
Team 10 files completion report
    ↓
Team 190 validates completion package (constitutional preflight)
    ↓ (pass)
Team 50 QA (where applicable — P01/P02/P03/P04/P07 require QA; P05/P06/P08/P09 are research/audit only)
    ↓ (pass)
Team 100 acknowledges closure
```

### 4.2 Packages Requiring Full Team 50 QA

| Package | QA Required | Rationale |
|---------|-------------|-----------|
| CQ-P01 | **Yes** | Alias changes affect normalization pipeline output |
| CQ-P02 | **Yes** | Full pipeline run — regression check mandatory |
| CQ-P03 | **Yes** | Unit mapping changes — verify published data |
| CQ-P04 | **Yes** | Unit mapping changes — verify published data |
| CQ-P05 | No | Research table only, no code change |
| CQ-P06 | No | ADR/spec only, no production code |
| CQ-P07 | **Yes** | Basket tier logic — new normalizer behavior |
| CQ-P08 | Team 190 sufficient | Pure audit, fix-forward migration if needed |
| CQ-P09 | Team 190 sufficient | Pure audit, fix-forward migration if needed |

### 4.3 Post-CQ Regression Baseline

After all CQ packages complete, the following must hold:

| Metric | Minimum |
|--------|---------|
| Published product count | ≥ 77 (current) |
| Unresolvable distinct names | ≤ 20 |
| Test suite | 0 failures |
| PRD028/PRD029 active aliases | 0 |
| Cherry aliases on PRD001 | 0 |
| CSA tier assignment | ≥ 1 source reproducible |

---

## 5. File Naming Convention (confirmed from ROADMAP v5.6)

| Artifact | Path |
|----------|------|
| This document | `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_APPROVAL_CQ_PACKAGES_MASTER_TEAM100.md` |
| Per-package approval (if needed) | `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_ARCH_APPROVAL_CQ-P0X_TEAM100.md` |
| Team 190 validation | `_COMMUNICATION/TEAM_190/reports/YYYY-MM-DD_CQ-P0X_PACKAGE_VALIDATION_TEAM190.md` |
| Team 10 completion | `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_CQ-P0X_COMPLETION_TEAM10.md` |

**Note:** This master document serves as the architectural approval for **all 9 packages**. Individual per-package ARCH_APPROVAL files are NOT required unless Team 10 requests a scope change that needs a new Team 100 sign-off.

---

## 6. Signature

**Approved by:** Team 100 (Architecture)  
**Document ID:** ARCH-20260406-CQ-MASTER  
**Scope:** CQ-P01 through CQ-P09 at LOD 200  
**Parallelism:** Phase α/β/γ/δ as defined in §2  
**Binding decisions:**
- §3.1.3 — Alias policy (global default, source-scoped on ambiguity)
- §3.3 — Egg per-unit pricing policy
- §3.4 — Passion fruit kg-default policy
- §3.5 — Blueberries V1 display-only
- §3.6 — Pantry ADR preliminary direction (approach B)
- §3.7.2 — CSA basket tier ranges (LOD 200 estimates, subject to data validation)
- §3.8.2 — Cherry-keyword tokens (binding)
- §3.9 — Basket merge policy unchanged
