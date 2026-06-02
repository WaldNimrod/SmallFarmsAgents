---
document_type: MANDATE
version: "1.0"
---

# Mandate — M10 Execution Corrections & Integration Guidance
**Mandate ID:** MANDATE-20260404-M10-CORRECTIONS
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-04
**Priority:** HIGH
**Gate dependency:** Supplements MANDATE-20260404-M10-2 and MANDATE-20260404-M10-3
**Status:** ACTIVE

---

## 1. Context

Team 100 has reviewed Team 10's independent mypips onboarding work (migration 031, workbook,
playbook) alongside the M10.2 and M10.3 mandates already issued. This mandate provides:

1. **Corrections already applied** by Team 100 to the database — Team 10 must align their plans
2. **Precise execution guidance** to ensure the mandates produce a fully updated live interface
3. **Integration notes** on how mypips work feeds into M10.4

**Triggered by:** Team 100 review of `2026-03-30_MYPIPS_ONBOARDING_MIGRATION_031_TEAM100.md`
**Related mandates:**
- `_COMMUNICATION/TEAM_10/MANDATE_M10_2_DICTIONARY_OPTIMIZATION_TEAM10.md`
- `_COMMUNICATION/TEAM_10/MANDATE_M10_3_STATIC_PARSERS_TEAM10.md`

---

## 2. Corrections Applied by Team 100 (informational — no action required)

Team 100 has already executed the following changes directly in the database. Team 10 must NOT
revert or duplicate these. If creating follow-up migrations, these changes must be reflected.

### 2.1 Duplicate Sources Removed

The following 4 sources were manually registered by Team 100 before migration 031 existed.
They duplicated mypips stores from the migration and contained no data (0 runs, 0 profiles).
**They have been deleted.**

| Deleted | Name | Replaced By | Migration Name |
|---------|------|------------|----------------|
| SRC029 | משתלת הראה | **SRC053** | משלוחי ירקות ופירות — טריים מהשדה לצרכן |
| SRC030 | פרי לנשמה | **SRC049** | השחקן שהפך לירקן |
| SRC031 | הענתיות | **SRC038** | הענתיות |
| SRC032 | משק רתם פיין | **SRC044** | משק רתם פיין בנימינה |

**Current source count:** 70 (was 74).

### 2.2 Display Bucket Corrections

Migration 031 set all 38 mypips sources to `display_bucket = 'grower'`. Team 100 has corrected:

- **13 sources → `discovery`**: Non-produce businesses (café, flowers, honey, dairy, holidays, SaaS, clearance)
- **3 sources → `store`**: Distributors, not direct growers (SRC049 fruit4soul, SRC052 דביבוני, SRC066 סנדרה)
- **1 source → basket_csa**: SRC038 הענתיות (CSA model)

### 2.3 Source Tier Corrections

- **9 confirmed produce sources → `price_grid`**: SRC041, 042, 053, 055, 060, 061, 062, 069, 070
- These are the workbook "yes" sources — highest priority for activation once parser exists.

---

## 3. Requirements for M10.2 Execution (Dictionary Optimization)

### 3.1 Scope Expansion

The M10.2 mandate targets SRC021–024 (662 unresolvable). Your plan **must also include**
these pre-existing sources that are below the 90% threshold:

| Source | Current Resolution | Issue |
|--------|-------------------|-------|
| SRC004 קיימא בית זית | **38.2%** (598 unresolvable) | Large catalog with many non-produce items — needs scope-skip rules |
| SRC006 עץ השדה | **0%** (6 unresolvable) | Small — 6 items need aliases |
| SRC010 Farmerim | **81.8%** (116 unresolvable) | Regression from 100% — new items appeared since last optimization |

### 3.2 Mandatory End State

The mandate is NOT complete until ALL of the following are true:

1. Resolution rate ≥ 90% for **every** active community source individually
2. `catalog_renormalize` has been run successfully
3. `run_publisher --upload` has been executed
4. The published page at `https://www.nimrod.bio/smallfarmsagent/` shows updated data
5. Published product count ≥ 70

### 3.3 Verification Command Sequence

```bash
# Step 1: Re-normalize everything
.venv/bin/python -m organic_market_agent catalog_renormalize

# Step 2: Verify per-source resolution
docker exec oma-g2-ev psql -U oma -d organic -c "
SELECT s.code, s.name,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.is_active = true AND s.market_scope = 'community'
GROUP BY s.code, s.name ORDER BY pct;
"

# Step 3: Publish and upload
.venv/bin/python -m organic_market_agent run_publisher --upload

# Step 4: Verify published product count
python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(f'Products: {len(d[\"products\"])}')"
```

---

## 4. Requirements for M10.3 Execution (Static Parsers)

### 4.1 Pre-requisite

M10.2 must be substantially complete (≥90% resolution for existing sources) before starting M10.3.
New parsers will generate additional unresolvable items requiring the same dictionary workflow.

### 4.2 Per-Source Implementation Checklist

For **each** of SRC025 (nizat), SRC026 (bensfarm), SRC027 (eranorgani), SRC028 (tamari):

- [ ] Deep HTML analysis → document selectors
- [ ] Create parser class in `organic_market_agent/parsers/`
- [ ] Register in `parsers/engine.py` `_PARSER_MAP`
- [ ] Update `chk_np_normalizer_type` constraint if new type added
- [ ] Create `source_fetch_profiles` row with selectors (set `is_active = true`)
- [ ] Create `normalizer_profiles` row (set `is_active = true`)
- [ ] Set source `is_active = true, status = 'active'`
- [ ] Run pipeline: `run_ingestion --run-type manual --source-code SRCxxx --normalize`
- [ ] Dictionary optimization until ≥ 85% resolution for the source
- [ ] Re-run catalog_renormalize
- [ ] Run publisher + upload

### 4.3 Spike Data Available

Team 100's spike results for reference:

| Source | Platform | Key Selectors | Est. Products |
|--------|----------|--------------|---------------|
| SRC025 nizat.com | ASP.NET | `.productcubecontainer`, `.productcubepname`, `.productcubeprice` | 68 |
| SRC026 bensfarm.co.il | Rexail/Next.js | `__NEXT_DATA__` JSON in `<script>` tag | 70 |
| SRC027 eranorgani.co.il | Custom | Needs analysis | TBD |
| SRC028 tamari-farm.co.il | Custom | Needs analysis | TBD |

### 4.4 Mandatory End State

Same as M10.2: updated live page at nimrod.bio with ≥ 80 published products.

---

## 5. mypips Work Integration (M10.4 Preparation)

Team 10's migration 031, workbook, playbook, and discovery scripts are acknowledged and approved
as **foundation for M10.4**. The following decisions are now binding:

1. **All 38 mypips sources remain as `candidate` / `inactive`** — no activation without headless parser
2. **Priority order when M10.4 starts:**
   - First: 9 "yes" sources (SRC041, 042, 053, 055, 060, 061, 062, 069, 070)
   - Second: 15 "maybe" sources (pending manual review of storefronts)
   - Skip: 14 "no" sources (remain `discovery` permanently unless reclassified)
3. **Normalizer type:** `simple_product_grid` placeholder is acceptable until `mypips` type is created
4. **Dynamic code allocation** pattern from migration 031 is approved as standard practice
5. **Do NOT create a mypips parser or collector as part of M10.2 or M10.3** — M10.4 is a separate mandate

---

## 6. QA and Sign-off Process

For **each** completed mandate (M10.2 and M10.3):

```
Step 1: Team 10 files Completion Report
        → _COMMUNICATION/TEAM_10/reports/2026-04-XX_M10_X_..._COMPLETE_TEAM10.md

Step 2: Team 10 files QA Review Request to Team 50
        → _COMMUNICATION/TEAM_50/QA_REQUEST_M10_X_TEAM10.md

Step 3: Team 50 performs validation
        → Verify resolution rates, published product counts, live page rendering
        → Files QA report with PASS/FAIL

Step 4: Team 100 architectural approval
        → Verifies no regression, data quality meets threshold
        → Signs off on gate progress toward G10
```

**Gate G10 opens only when BOTH M10.2 and M10.3 have QA PASS + Team 100 approval.**

---

## 7. Out of Scope

- Activating any mypips source (M10.4)
- Headless browser / Playwright infrastructure (M10.4)
- Phase B retail sources (M10.5)
- Changes to the public HTML template structure (delivered in M10.1)
- Rolling back or modifying migration 031 — it is stable and approved

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
