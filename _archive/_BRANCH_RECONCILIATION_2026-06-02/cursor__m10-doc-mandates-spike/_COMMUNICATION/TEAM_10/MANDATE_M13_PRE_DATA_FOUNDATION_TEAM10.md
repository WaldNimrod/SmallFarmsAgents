---
document_type: MANDATE
version: "1.0"
---

# Mandate — M13-PRE Data Foundation Prerequisites (LOD 400)

**Mandate ID:** MANDATE-20260404-M13-PRE-DATA-FOUNDATION
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev) + Team 20 (Infrastructure)
**CC:** Team 50 (QA)
**Date:** 2026-04-04
**Priority:** CRITICAL
**Gate dependency:** Blocks M13-B (frontend module) start
**Status:** ACTIVE
**Related:** `MANDATE-20260404-M10-4-HEADLESS-MYPIPS`, `MANDATE-20260404-M10-5-CSA-RETAIL`, `QA-RPT-20260405-M10_5`

---

## 1. Purpose

This mandate defines the **exact data-readiness criteria** that M10.4 and M10.5 must meet before M13 frontend work can begin. Team 10 and Team 20 are already working on these milestones. This document consolidates the remaining gaps at LOD 400 (detailed task level) so that every team member knows precisely what to fix, how to verify it, and what thresholds to meet.

**Context:** M13 (Public Product Details Module) requires real data from CSA baskets, mypips storefronts, and retail sources to render meaningful details, price charts, and variant panels. The M10.5 QA run (2026-04-05) revealed 5 critical failures. M10.4 has not yet delivered any live data. Both must be resolved before M13-B.

---

## 2. M10.4 — Headless Browser / mypips Completion Requirements

These criteria supplement the existing M10.4 mandate (`MANDATE-20260404-M10-4-HEADLESS-MYPIPS`). All original acceptance criteria remain in force.

### 2.1 Infrastructure (Team 20)

| ID | Task | Verification | Status |
|----|------|-------------|--------|
| PRE-D1 | `HeadlessBrowserCollector` functional | `python3 -c "from organic_market_agent.collectors.headless_browser import HeadlessBrowserCollector; print('OK')"` | Required |
| PRE-D2 | `MypipsCollector` subclass operational | `python3 -c "from organic_market_agent.collectors.mypips import MypipsCollector; print('OK')"` | Required |
| PRE-D3 | Playwright chromium installed | `python3 -m playwright install chromium` exits 0 | Required |

### 2.2 Source Activation (Team 10)

| ID | Task | Verification | Threshold |
|----|------|-------------|-----------|
| PRE-D4 | Activate priority mypips sources | `SELECT code, is_active, status FROM sources WHERE code IN ('SRC041','SRC042','SRC053','SRC055','SRC060','SRC061','SRC062','SRC069','SRC070') ORDER BY code;` | >= 5 of 9 with `is_active=true, status='active'` |
| PRE-D5 | Run live ingestion for activated sources | `python3 -m organic_market_agent run_ingestion --run-type manual --source-code SRCXXX --normalize` for each | >= 5 sources produce `raw_extracted_items` with count > 0 |
| PRE-D6 | Fetch + normalizer profiles registered | `SELECT code, platform_family, normalizer_type FROM sources s JOIN source_fetch_profiles sfp ON sfp.source_id = s.id WHERE s.code LIKE 'SRC0%' AND s.notes = 'mypips_candidate_031';` | All activated sources have profiles |

### 2.3 Dictionary Optimization (Team 10)

| ID | Task | Verification | Threshold |
|----|------|-------------|-----------|
| PRE-D7 | Product aliases for mypips items | Aliases registered via Alembic migration | Cover common produce names from mypips stores |
| PRE-D8 | Scope-skip rules for non-produce | Non-vegetable/fruit items (dairy, prepared food, etc.) scope-skipped | Appropriate for each store's catalog |
| PRE-D9 | Resolution rate per source | ```sql SELECT s.code, COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm, COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres, ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') / NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized','unresolvable')), 0), 1) AS pct FROM sources s JOIN source_fetch_runs sfr ON sfr.source_id = s.id JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id WHERE s.code IN ('SRC041','SRC042','SRC053','SRC055','SRC060','SRC061','SRC062','SRC069','SRC070') GROUP BY s.code ORDER BY s.code; ``` | >= 85% for each activated source |
| PRE-D10 | New mypips products in catalog | `SELECT code, canonical_name_he, category FROM products WHERE code LIKE 'PRD%' ORDER BY id DESC LIMIT 20;` | All new products have correct `category` value |

### 2.4 End-State Verification (Team 10)

| ID | Task | Verification | Threshold |
|----|------|-------------|-----------|
| PRE-D11 | Published product count | ```bash python3 -m organic_market_agent run_publisher python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d['products']))" ``` | >= 90 |
| PRE-D12 | mypips data visible in published output | `python3 -c "import json; d=json.load(open('output/public/public_report.json')); print([p for p in d['products'] if 'grower' in (p.get('source_types') or [])][:5])"` | At least 5 new products from mypips sources |
| PRE-D13 | Unit tests green | `python3 -m pytest tests/ -q` | 0 failures |

---

## 3. M10.5 — CSA + Retail Remediation (LOD 400)

These tasks address the 5 critical failures from the M10.5 QA report (`QA-RPT-20260405-M10_5`).

### 3.1 F-M10.5-1: SRC034 (meshek organi) Extraction Failure

**Root cause investigation required.** SRC034 returned 0 `raw_extracted_items` during QA. The parser (`CsaBasketParser` with `csa_site=meshek_organi`) was tested successfully in unit tests but failed on live ingestion.

| ID | Task | Details |
|----|------|---------|
| PRE-F1a | Investigate SRC034 URL | Verify `base_url` is still correct. Navigate to the URL manually and confirm basket content is present in static HTML. Wix pages may have changed structure. |
| PRE-F1b | Check selector profile | Verify `selector_profile.csa_site` matches `meshek_organi` dispatch in `CsaBasketParser`. Run: `SELECT sfp.* FROM source_fetch_profiles sfp JOIN sources s ON s.id = sfp.source_id WHERE s.code = 'SRC034';` |
| PRE-F1c | Test live fetch | `python3 -m organic_market_agent run_ingestion --run-type manual --source-code SRC034 --normalize` — inspect `raw_extracted_items` count |
| PRE-F1d | Fix parser if needed | If URL changed or HTML structure drifted, update the parser's `meshek_organi` handler. If URL is dead, deactivate SRC034 and document. |

**Acceptance:** At least **2 of 3** CSA sources (SRC033, SRC034, SRC035) produce > 0 basket items on live ingestion.

**Verification:**
```sql
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
  AND sfr.id = (SELECT MAX(id) FROM source_fetch_runs WHERE source_id = s.id)
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code ORDER BY s.code;
```

### 3.2 F-M10.5-3: SRC036 (Teva Shuk) Normalization at 0%

**Root cause:** 12 items extracted, 9 scope-skipped (dry grocery), 3 unresolvable. The 3 unresolvable items are organic products that lack aliases mapping them to catalog products.

| ID | Task | Details |
|----|------|---------|
| PRE-F3a | Identify unresolvable items | ```sql SELECT rei.raw_product_name, rei.raw_payload_json FROM raw_extracted_items rei JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id JOIN sources s ON s.id = sfr.source_id WHERE s.code = 'SRC036' AND rei.extraction_status = 'unresolvable' ORDER BY rei.id DESC LIMIT 10; ``` |
| PRE-F3b | Add product aliases | For each unresolvable item, create a `product_alias` mapping to the correct catalog product. Items likely include: quinoa, chickpeas, oats — these may need new products (PRD070+) in category `legumes_fresh` or a new `pantry_organic` category. |
| PRE-F3c | Consider category addition | If new product categories are needed for dry-goods (pasta, grains), add them to the `chk_p_category` CHECK constraint via Alembic migration. Team 100 pre-approves `'pantry_dry'` as a category if needed. |
| PRE-F3d | Re-normalize and verify | ```bash python3 -m organic_market_agent catalog_renormalize python3 -m organic_market_agent run_ingestion --run-type manual --source-code SRC036 --normalize ``` |

**Acceptance:** SRC036 resolution rate >= 85%.

**Verification:**
```sql
SELECT
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized','unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code = 'SRC036';
```

### 3.3 F-M10.5-4: Published Product Count Regression

**Root cause:** Published count dropped from 83 to 74 after M10.5 work. Likely caused by `catalog_renormalize` interacting with migration 056 changes (new scope-skip rules removing items that previously contributed to the count).

| ID | Task | Details |
|----|------|---------|
| PRE-F4a | Identify missing products | Compare current published products against pre-M10.5 baseline: ```bash python3 -c "import json; d=json.load(open('output/public/public_report.json')); codes=sorted(p['product_id'] for p in d['products']); print(f'{len(codes)} products:', codes)" ``` Cross-reference against the known 83-product set. |
| PRE-F4b | Check for over-aggressive scope-skip | Review rules from migration 056: `SELECT pattern, source_scope FROM catalog_scope_skip_rules WHERE id > (SELECT MAX(id) - 20 FROM catalog_scope_skip_rules);` — ensure no global rules are suppressing valid community source items. |
| PRE-F4c | Re-normalize all sources | ```bash python3 -m organic_market_agent catalog_renormalize python3 -m organic_market_agent run_publisher ``` |

**Acceptance:** Published product count >= 83 (the pre-M10.5 baseline). Combined with mypips (PRE-D11), final target is >= 90.

### 3.4 F-M10.5-2: SRC036 Organic Count (WAIVED)

**Team 100 waiver W-M10.5-AC2:** The original threshold of >= 20 organic items from SRC036 is **waived to >= 12**. Rationale: 12 genuine organic items from a single retail source is a valid V1 start. The `selector_profile` extension mechanism allows adding more category URLs without code changes.

**No action required from Team 10** for this item.

### 3.5 F-M10.5-5: Teva Shuk Visibility in Live Output

This is a downstream consequence of F-M10.5-3 (0% resolution). Once SRC036 has normalized observations, they will flow through the publisher automatically.

**Verification (after F-M10.5-3 fix):**
```bash
python3 -m organic_market_agent run_publisher --upload
curl -sL "https://www.nimrod.bio/smallfarmsagent/" | python3 -c "
import sys, json
html = sys.stdin.read()
print('store filter:', 'data-filter=\"store\"' in html)
"
```

---

## 4. Combined M13-PRE Gate Criteria

All criteria must be met before M13-B (Frontend Details Module) can begin.

| # | Criterion | Threshold | Source |
|---|-----------|-----------|--------|
| G-PRE-1 | mypips sources active and producing data | >= 5 of 9 with normalized_observations | M10.4 |
| G-PRE-2 | mypips resolution rate | >= 85% per activated source | M10.4 |
| G-PRE-3 | CSA extraction coverage | >= 2 of 3 CSA sources producing basket items | M10.5 |
| G-PRE-4 | SRC036 resolution rate | >= 85% | M10.5 |
| G-PRE-5 | Published product count | >= 90 (combined baseline + mypips + retail) | Combined |
| G-PRE-6 | Full test suite | 0 failures | Regression |
| G-PRE-7 | Live page updated | `run_publisher --upload` succeeds, HTTP 200 | Deployment |

---

## 5. Delivery Process

```
Step 1: Team 10 + Team 20 complete M10.4 implementation
        → File: _COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M10_4_COMPLETION_TEAM10.md

Step 2: Team 10 complete M10.5 remediation per §3 above
        → File: _COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M10_5_REMEDIATION_TEAM10.md

Step 3: Team 10 file combined QA request to Team 50
        → Request re-QA of M10.4 + M10.5 together

Step 4: Team 50 validate all G-PRE criteria (§4)
        → File QA report with PASS/FAIL

Step 5: On PASS → Team 100 declares M13-PRE complete
        → M13-A may proceed in parallel (schema/code work)
        → M13-B may begin (frontend with real data)

Step 6: Return completion notice to Team 100
        → _COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M13_PRE_COMPLETION_TEAM10.md
```

---

## 6. Timeline Guidance

M13-PRE is not a new development effort — it is the completion of existing M10.4/M10.5 work with sharpened acceptance criteria. Team 10 should treat this as a focused sprint to close out M10 data gaps.

M13-A (Publisher JSON v3 extensions) may begin in parallel once this mandate is acknowledged, since the schema/code work does not require live data. However, integration tests for M13-A will need real data from M13-PRE.

---

## 7. Out of Scope

- M13-A deliverables (publisher JSON extensions) — separate phase
- M13-B deliverables (frontend module) — blocked on M13-PRE
- New parser development (beyond fixing existing M10.5 parsers)
- Activation of "maybe" mypips sources (secondary review)
- Chain/benchmark sources (future)

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
