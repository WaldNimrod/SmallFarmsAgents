---
document_type: MANDATE
version: "1.0"
---

# Mandate — Headless Browser Infrastructure & mypips Source Integration (M10.4)

**Mandate ID:** MANDATE-20260404-M10-4-HEADLESS-MYPIPS
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev) + Team 20 (Infrastructure)
**Date:** 2026-04-04
**Priority:** CRITICAL
**Gate dependency:** Blocks full G10 closure
**Status:** ACTIVE

---

## 1. Objective

Build headless browser infrastructure using Playwright and implement a collector/parser for mypips.app — a Firebase/React SaaS platform used by Israeli farms. Activate 9 confirmed organic produce sources and optimize their data dictionary to achieve ≥90% resolution rate.

---

## 2. Background

mypips.app is a hosted storefront platform. Content is rendered client-side via Firebase/Firestore — no HTML product data exists in the initial HTTP response. A headless browser (Playwright) is required to execute JavaScript before extracting product data.

Team 10 has already completed foundational work:
- **Migration 031:** 38 mypips candidate sources registered (SRC037–SRC074)
- **Workbook:** `data/mypips_source_onboarding_workbook.csv` — storefront metadata
- **Playbook:** `documentation/mypips-source-onboarding-playbook.md`
- **Discovery tools:** URL discovery and Firestore probe scripts

Team 100 has classified and corrected these sources:
- 9 "yes" sources → `source_tier = 'price_grid'`, `display_bucket = 'grower'`
- 3 distributors → `display_bucket = 'store'`
- 1 CSA → `source_group = 'basket_csa'`
- 13 irrelevant → `display_bucket = 'discovery'`
- 12 "maybe" growers → `display_bucket = 'grower'`, `source_tier = 'discovery'`

---

## 3. Deliverables

### Phase 1: Infrastructure (Team 20)

| ID | Deliverable | Details |
|----|-------------|---------|
| D1 | Playwright dependency | Add `playwright` to `requirements.txt`; document `playwright install chromium` setup step |
| D2 | `HeadlessBrowserCollector` | New base collector class in `organic_market_agent/collectors/headless_browser.py` — launches headless Chromium, navigates URL, waits for content selector, returns rendered HTML |
| D3 | Configuration | Add `PLAYWRIGHT_HEADLESS` (default `true`), `PLAYWRIGHT_TIMEOUT_MS` (default `30000`) to `Config` class |
| D4 | Retry logic | Integrate with existing `CollectorEngine` retry mechanism — browser crash / timeout → retry with fresh browser |

### Phase 2: mypips Collector & Parser (Team 10)

| ID | Deliverable | Details |
|----|-------------|---------|
| D5 | `MypipsCollector` | Subclass of `HeadlessBrowserCollector` in `collectors/mypips.py` — navigates to storefront URL, waits for product grid to render (`.product-card` or equivalent mypips selector), returns page HTML |
| D6 | `MypipsParser` | New parser in `parsers/mypips.py` — extracts product name, price, unit from rendered HTML; handle mypips-specific markup patterns |
| D7 | Engine registration | Register `'mypips'` in `_PARSER_MAP` (`parsers/engine.py`) and update `chk_np_normalizer_type` constraint via Alembic migration |
| D8 | Fetch/normalizer profiles | Create `source_fetch_profiles` and `normalizer_profiles` for all 9 priority sources via Alembic data migration |
| D9 | Source activation | Set `is_active = true`, `status = 'active'` for 9 priority sources |

### Phase 3: Dictionary Optimization (Team 10)

| ID | Deliverable | Details |
|----|-------------|---------|
| D10 | Aliases + products | Add product aliases, new products, scope-skip rules for mypips item names |
| D11 | Resolution target | ≥90% resolution for each activated mypips source |
| D12 | Renormalize + publish | Run `catalog_renormalize` and `run_publisher --upload` |

### Phase 4: Tests (Team 10)

| ID | Deliverable | Details |
|----|-------------|---------|
| D13 | Unit tests | `tests/test_mypips_parser.py` — at least 5 tests with mock HTML (no live browser) |
| D14 | Integration test | One live end-to-end run for at least 3 mypips sources, verifying items in `raw_extracted_items` |

---

## 4. Priority Source List (Phase 1 — activate these 9)

| Source | Name | URL | Est. Products |
|--------|------|-----|---------------|
| SRC041 | פירות וירקות מיתר | `https://mypips.app/bestfruit` | ~50 |
| SRC042 | משק ברודבקה | `https://mypips.app/brodavkameshek` | ~40 |
| SRC053 | משתלת הראה | `https://mypips.app/mashtelatharoe` | ~307 |
| SRC055 | משק 27 | `https://mypips.app/meshek27` | ~60 |
| SRC060 | אורגניקא גן ירק | `https://mypips.app/organicaganyarak-home` | ~50 |
| SRC061 | משק אורגני בן יהודה | `https://mypips.app/organicfarm` | ~80 |
| SRC062 | משק מלקט | `https://mypips.app/poli` | ~60 |
| SRC069 | משק סולומון | `https://mypips.app/solomon` | ~50 |
| SRC070 | הקבוצה פירות וירקות אורגניים | `https://mypips.app/the-group` | ~50 |

### Secondary sources (activate after Phase 1 success, manual review first)

12 "maybe" grower sources (SRC040, 043, 044, 050, 054, 056, 059, 064, 065, 067, 072, 073) remain as `discovery`. Team 10 may propose activation for any that prove to have organic produce after manual review.

---

## 5. Technical Guidance

### mypips Page Structure (from spike)

mypips.app stores are Firebase-hosted React SPAs. Key observations:
- Initial HTML is a shell (`<div id="root">`) with no product data
- Products load via Firestore queries after JS execution
- Typical wait target: presence of product cards in the DOM
- Price is typically displayed in NIS with format `₪XX.XX`
- Some stores use category tabs — ensure all categories are loaded

### Alternative: Firestore API Direct Access

If Playwright proves unstable, an alternative approach is to intercept Firestore REST calls:
- mypips storefronts query `firestore.googleapis.com/v1/projects/mypips-app/databases/(default)/documents/`
- Team 10 MAY implement a `MypipsFirestoreCollector` that queries the API directly instead of rendering
- This is an acceptable alternative — document the approach chosen

### Collector Architecture

```
HeadlessBrowserCollector (base)
  ├── launch_browser() → playwright.chromium.launch(headless=True)
  ├── navigate(url, wait_selector, timeout) → page HTML
  ├── close() → cleanup
  └── retry-aware: browser crash → re-launch + retry

MypipsCollector(HeadlessBrowserCollector)
  ├── collect(source, fetch_profile) → raw HTML
  └── wait_selector from fetch_profile.selector_profile["wait_for"]
```

---

## 6. Acceptance Criteria

| # | Criterion | Threshold |
|---|-----------|-----------|
| AC1 | Playwright installs and runs headless Chromium in dev environment | Binary |
| AC2 | `HeadlessBrowserCollector` fetches rendered HTML from at least 1 JS-heavy site | Binary |
| AC3 | `MypipsCollector` + `MypipsParser` extract products from all 9 priority sources | ≥7 of 9 sources |
| AC4 | Resolution rate per activated mypips source | ≥90% |
| AC5 | Published product count increases | ≥90 (currently 83) |
| AC6 | All existing tests pass (no regression) | 0 failures |
| AC7 | New unit tests for mypips parser | ≥5 tests PASS |
| AC8 | Live page at `nimrod.bio/smallfarmsagent/` updated with new data | HTTP 200 + new products visible |

---

## 7. Out of Scope

- Activating "maybe" or "no" mypips sources (secondary review only)
- CSA basket sources (M10.5)
- Phase B retail sources (M10.5)
- Changes to existing parsers or templates
- Any admin UI changes beyond what's needed for mypips source management

---

## 8. QA and Sign-off Process

```
Step 1: Team 10 + Team 20 implement and file Completion Report
        → _COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M10_4_COMPLETION_TEAM10.md

Step 2: Team 10 files QA Review Request to Team 50
        → _COMMUNICATION/TEAM_50/QA_REQUEST_M10_4_TEAM10.md

Step 3: Team 50 validates:
        - All acceptance criteria AC1–AC8
        - Full pytest suite green
        - Live page renders correctly
        - Resolution rates verified per source
        → Files QA report with PASS/FAIL

Step 4: Team 100 architectural review
        → Verifies headless infrastructure is clean, no security issues
        → Signs off on M10.4 sub-gate

Step 5: Return completion notice to Team 100
        → _COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M10_4_COMPLETION_NOTICE_TEAM10.md
```

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-04*
*Authorized by: Team 100 (Architecture)*
