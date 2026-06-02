---
document_type: E2E_QA_FULL_REPORT
version: "1.0.0"
from: team_50 (QA & Functional Acceptance)
to: team_100 (Chief System Architect)
cc: team_00, team_99
date: 2026-06-02
wp: SFA-S003-P004
mandate: _COMMUNICATION/TEAM_100/HANDOFF_team50_E2E-FULL_2026-06-02_v1.0.0.md
deploy_baseline_declared: ce7b07f
engine: Cursor Composer (team_50)
---

# E2E QA FULL Report — SFA Delivery Tier (LIVE)

## Verdict box

| Field | Value |
|-------|-------|
| **Verdict** | **PASS_WITH_FINDINGS** |
| **WP** | SFA-S003-P004 — post 2026-06-02 deploy acceptance |
| **Target** | LIVE `https://sfa.nimrod.bio` (read-only) |
| **Execution host** | Mac workstation (Playwright/Chromium); waldhomeserver reached via SSH — **no Playwright on server** (`NO_PLAYWRIGHT`); repo on server `a7a787a`, Mac `dd94e91` (handoff cited `ce7b07f`) |
| **Next step** | **team_100:** fix **F-CALC-002** (`crop-book-v1.js` not loaded on `/calc/`). **team_10/99:** fix **F-EXPORT-001** (`/calc/export.pdf` 404). Re-run LIVE calc browser pass after JS include fix. |

**Scope note:** This is **team_50 internal QA** only. It does **not** substitute for a **team_190** non-Claude constitutional gate (Iron Rules #1 / #5).

---

## 1. Environment

| Item | Detail |
|------|--------|
| **LIVE** | `https://sfa.nimrod.bio` — PHP 8.5.5, MySQL ok (`GET /api/v1/health`) |
| **Harness** | `_COMMUNICATION/TEAM_50/SFA-S003-P004/e2e_evidence_2026-06-02/run_e2e_qa.py` + Playwright headless Chromium |
| **Evidence dir** | `_COMMUNICATION/TEAM_50/SFA-S003-P004/e2e_evidence_2026-06-02/` — `results.json`, `api_samples.json`, `calc_parity.json`, `summary.json`, 46× PNG (mobile + desktop) |
| **AOS validation** | `validate_aos.sh .` → **29 PASS / 19 SKIP / 0 FAIL** |
| **Python calc baseline** | `pytest tests/crop_book/test_calculators.py` → **43 passed** |
| **Constraints** | No ingest POST, no deploy, no git checkout/reset/commit |

### 1.1 Deploy regression (F-OPS-001 — **CLOSED**)

| Marker | 2026-06-01 LIVE | 2026-06-02 LIVE |
|--------|-----------------|-----------------|
| `crop-book-v1.css` | 404 | **200** |
| `crop-book-v1.js` (asset URL) | 404 | **200** |
| `/crop-book/` `wc-cropbook-hero` | absent | **present** |
| `/` `mod-card__hero` | absent | **present** |
| `/calc/` export links in HTML | absent | **present** |

WP-CB-MIG2 + FTPS UI deploy is **live**. F-OPS-001 from 2026-06-01 is **resolved**.

---

## 2. Per-area summary

| Area | Result | One-line evidence |
|------|--------|-------------------|
| **A — Interface health** | **PASS_WITH_FINDINGS** | All mandated routes **200** (or acceptable redirect); **zero** JS `console` errors across 46 captures; **F-CALC-002** `/calc/` missing `crop-book-v1.js` |
| **B — Data validation** | **PASS_WITH_FINDINGS** | F-DATA-001 **fixed** (tomato→Solanaceae; only `new-zealand-spinach`→Aizoaceae); topics + מוצע render; hub stat drift; market mirror has **no** `last_price` on sampled products |
| **C — Calculators** | **PARTIAL** | Python **43/43** PASS; LIVE `/calc/` panels **inert** (no `SFA_CALC`); **5** modcards not 14; **PDF export 404** |
| **D — API** | **PASS_WITH_FINDINGS** | health/crops/assumptions/contribute **PASS**; market price UI↔API check **skipped** (no priced row) |

---

## 3. Interface health (Area A)

Legend: **M** = mobile 390×844, **D** = desktop 1280×900. Screenshots: `e2e_evidence_2026-06-02/{viewport}__{route}.png`.

### Hub / global

| Route | M | D | HTTP | Console | Notes |
|-------|---|---|------|---------|-------|
| `/` | PASS | PASS | 200 | 0 | `mod-card__hero` present; stats **66** crops / **30** products (F-STAT-*) |
| `/about` | PASS | PASS | 200 | 0 | |
| `/search?q=חסה` | PASS | PASS | 200 | 0 | |
| `/community` | PASS | PASS | 200 | 0 | |
| `/clients/` | PASS | PASS | 200* | 0 | *Playwright follows **302→/** ; `curl -I` confirms **302** Location `/` — AC met |

### Market

| Route | M | D | HTTP | Console | Notes |
|-------|---|---|------|---------|-------|
| `/market/` | PASS | PASS | 200 | 0 | `mk-disclaimer` in HTML |
| `/market/prd017` | PASS | PASS | 200 | 0 | Page loads; API `last_price` **null** (F-MKT-002) |

### Crop Book

| Route | M | D | HTTP | Console | Notes |
|-------|---|---|------|---------|-------|
| `/crop-book/` | PASS | PASS | 200 | 0 | v1 hero + `crop-book-v1.css`; **70** cards in API |
| `/crop-book/?view=table` | PASS | PASS | 200 | 0 | |
| `/crop-book/questions` | PASS | PASS | 200 | 0 | |
| `/crop-book/family` | PASS | PASS | 200 | 0 | |
| `/crop-book/table` | PASS | PASS | 200 | 0 | |
| `/crop-book/search?q=tomato` | PASS | PASS | 200 | 0 | |
| `/crop-book/tomatoes/?depth=full` | PASS | PASS | 200 | 0 | `crop-book-v1.js` loaded; מוצע tags present |
| `/crop-book/carrots/?depth=full` | PASS | PASS | 200 | 0 | |
| `/crop-book/lettuce/?depth=full` | PASS | PASS | 200 | 0 | |
| `/crop-book/cucumbers/?depth=full` | PASS | PASS | 200 | 0 | |
| `/crop-book/eggplant/?depth=full` | PASS | PASS | 200 | 0 | |
| `/crop-book/chard/?depth=full` | PASS | PASS | 200 | 0 | |
| `/crop-book/cauliflower/?depth=full` | PASS | PASS | 200 | 0 | sparse crop OK |
| `/crop-book/family/solanaceae` | PASS | PASS | 200 | 0 | Not 404 (was 302 in PHPUnit in-memory); family page renders |
| `/crop-book/family/apiaceae` | PASS | PASS | 200 | 0 | |

**RTL / placeholders:** No `Array(`, `object Object`, `field_name`, or `value_best` leaks in captured HTML.

**Watercolor cards:** Index uses `/public_assets/img/crops/wc-*.png` (HEAD **200**). Playwright flagged some cards as `broken_imgs` on first paint — likely **lazy-load timing** (assets return 200 on direct fetch). Hero `wc-cropbook-hero.webp` **200**.

### Calculator route

| Route | M | D | HTTP | Console | Notes |
|-------|---|---|------|---------|-------|
| `/calc/` | PARTIAL | PARTIAL | 200 | 0 | **F-CALC-002:** HTML has 5× `data-calc` modcards (duplicated blocks in DOM → 10 nodes) but **no** `<script src="crop-book-v1.js">` — only `sfa.js`. `window.SFA_CALC` **undefined** after `networkidle`. |

---

## 4. Data validation (Area B)

### 4.1 Family taxonomy (F-DATA-001 — **CLOSED**)

Detail API spot-checks (identity.family.scientific_name):

| Slug | Expected | Actual | PASS |
|------|----------|--------|------|
| tomatoes | Solanaceae | Solanaceae | yes |
| carrots | Apiaceae | Apiaceae | yes |
| lettuce | Asteraceae | Asteraceae | yes |
| cucumbers | Cucurbitaceae | Cucurbitaceae | yes |
| eggplant | Solanaceae | Solanaceae | yes |
| beets | Amaranthaceae | Amaranthaceae | yes |
| garlic | Amaryllidaceae | Amaryllidaceae | yes |
| onions | Amaryllidaceae | Amaryllidaceae | yes |

**Aizoaceae sweep (70 crops, detail-enriched):** only **`new-zealand-spinach`** → Aizoaceae. **PASS.**

List endpoint omits `scientific_name` on items (Hebrew `family_name_he` only) — UI detail pages use detail API; no false Aizoaceae on tomato after deploy.

### 4.2 Thirteen-topic taxonomy

On `/crop-book/tomatoes/?depth=full`, visible topic labels include (subset — empty-field topics skipped per template): **זנים, מרווח, קרקע, זריעה, השקיה, מזיקים, קציר, רצף**. **PARTIAL** vs full 13 headers (ציוד, הכנת ערוגה, טיפוח, שטיפה not rendered — `fields[]` empty). **Expected** until backfill; not a render crash.

### 4.3 Proposed fields (“מוצע”)

Tomatoes full depth: **`proposed-tag` / מוצע** present. Empty proposed values **not** flagged as defects (per handoff).

### 4.4 Market

- Disclaimer: **PASS** on index.
- Price match: **SKIP** — no product in `GET /api/v1/products` `items[]` with non-null `last_price` at test time (`prd017` → `last_price: null`).

---

## 5. Calculator validation (Area C)

### 5.1 Coverage matrix (all 14)

| # | Calculator | LIVE UI | JS live recompute | Python SSOT |
|---|------------|---------|-------------------|-------------|
| 1 | seed_quantity_to_buy | `/calc/` panel only | **NO** (no v1.js) | **PASS** (pytest + harness) |
| 2 | transplants_needed | none | — | **PASS** (pytest) |
| 3 | nursery_trays_and_sow_date | none | — | **PASS** (pytest + harness) |
| 4 | sowing_date_from_harvest | none | — | **PASS** (pytest) |
| 5 | harvest_window_from_sowing | none | — | **PASS** (pytest + harness) |
| 6 | succession_schedule | none | — | **PASS** (pytest) |
| 7 | beds_for_target_yield | none (JS exists, no modcard) | — | **PASS** (pytest + harness) |
| 8 | expected_yield | `/calc/` + crop modal on book pages | book: js loaded; **calc: NO** | **PASS** |
| 9 | expected_revenue | `/calc/` panel | **NO** on `/calc/` | **PASS** (pytest + harness) |
| 10 | plant_population | `/calc/` panel | **NO** | **PASS** (pytest + harness) |
| 11 | frost_planting_window | none | — | **PASS** (pytest) |
| 12 | fertilizer_compost_rate | `/calc/` panel | **NO** | **PASS** (pytest + harness) |
| 13 | crop_profit_comparison | none | — | **PASS** (pytest) |
| 14 | seed_input_cost | none | — | **PASS** (pytest) |

**Dashboard copy** claims “14 מחשבונים” but LIVE renders **5** interactive modcards (#1, #8, #10, #9, #12) — **F-CALC-003** (documentation/coverage gap, not formula bug).

### 5.2 AssumptionFields

`/calc/` includes assumption inputs in HTML (`data-assume="germination_rate"` default 90%). Could not drive live recompute on `/calc/` because **CALC JS not loaded**. On crop-book pages, v1.js loads — **not re-tested** in this pass for germ change (blocked by F-CALC-002 on dashboard).

### 5.3 Exports

| Export | HTTP | Content |
|--------|------|---------|
| `/calc/export.csv` | **200** | Minimal CSV header only (`שדה,ערך` — 14 bytes) — **PARTIAL** |
| `/calc/export.pdf` | **404** | **FAIL** (F-EXPORT-001) |

### 5.4 F-50-patch01-01 (revenue non-kg)

`non_kg_products` with priced rows: **empty**. Latent JS revenue bug **unreachable** — **PASS** (no live non-kg priced crop).

### 5.5 Root cause — F-CALC-002

[`sfa_delivery/templates/_layout.php`](../../../../sfa_delivery/templates/_layout.php) loads `crop-book-v1.js` only when `$active === 'crop-book'`. `/calc/` sets `$active = 'calc'`, so LIVE calc dashboard gets **CSS but not CALC JS**. Confirmed: `curl /calc/` has no `crop-book-v1.js` script tag; `/crop-book/tomatoes/` includes it.

---

## 6. API validation (Area D)

| Endpoint | Result | Evidence |
|----------|--------|----------|
| `GET /api/v1/health` | **PASS** | `status: ok`, `db: ok` |
| `GET /api/v1/crops` | **PASS** | `count: 70` |
| `GET /api/v1/crops/{slug}` | **PASS** | Family spot-checks §4.1 |
| `GET /api/v1/assumptions` | **PASS** | `germination_rate`, `bed_width`, `post_url` present |
| `POST /api/v1/contribute` request-info | **PASS** | **200**, `{"ok":true}` — F-API-001 **CLOSED** |
| `POST /api/v1/contribute` unknown kind | **PASS** | **400** |
| UI↔API price | **SKIP** | No priced product in mirror |

---

## 7. Findings (prioritized)

| ID | Severity | Area | Observation | Repro |
|----|----------|------|-------------|-------|
| **F-CALC-002** | **MAJOR** | `/calc/` | Calculator dashboard modcards do not recompute — `crop-book-v1.js` not included (only `sfa.js`). `window.SFA_CALC` undefined. | `curl -sL https://sfa.nimrod.bio/calc/ \| grep crop-book-v1.js` → 0; compare `/crop-book/tomatoes/` → script present |
| **F-EXPORT-001** | **MAJOR** | `/calc/export.pdf` | PDF export route returns **404** | `curl -sI https://sfa.nimrod.bio/calc/export.pdf` |
| **F-CALC-003** | MINOR | `/calc/` | UI claims 14 calculators; **5** modcards rendered; #7 `beds` JS exists but no panel | Open `/calc/` |
| **F-STAT-001** | MINOR | `/` | Hub **66** crops vs API **70** | Compare `/` copy vs `GET /api/v1/crops` |
| **F-STAT-002** | MINOR | `/` | Hub **30** products vs API **65** items | Compare `/` vs `GET /api/v1/products` |
| **F-MKT-002** | MINOR | Market | No `last_price` on sampled products (`prd017` null) — cannot verify price display | `GET /api/v1/products/prd017` |
| **F-MKT-001** | MINOR | `/market/` | Category chips English slugs (regression from 2026-06-01) | Visual on index |

**Closed regressions:** F-OPS-001, F-DATA-001, F-API-001.

**Not defects (expected):** empty מוצע proposed fields; partial 13-topic headers; F-50-patch01-01 unreachable.

---

## 8. Regression vs 2026-06-01 report

| Prior ID | 2026-06-02 status |
|----------|-------------------|
| F-OPS-001 deploy drift | **CLOSED** |
| F-DATA-001 tomato Aizoaceae | **CLOSED** |
| F-API-001 contribute 404 | **CLOSED** |
| F-V1-001 / F-CALC-001 v1 UI absent | **CLOSED** (superseded by F-CALC-002 JS scope) |
| F-STAT-001/002 | **OPEN** (minor) |
| F-MKT-001 | **OPEN** (minor) |

---

## 9. Evidence appendix

- **Full machine output:** `e2e_evidence_2026-06-02/results.json`, `api_samples.json`, `calc_parity.json`, `summary.json`
- **Screenshots:** 46 files `mobile__*.png`, `desktop__*.png` under `e2e_evidence_2026-06-02/`
- **API sample:**

```json
GET /api/v1/crops/tomatoes → identity.family.scientific_name: "Solanaceae"
GET /api/v1/health → {"status":"ok","db":"ok"}
POST /api/v1/contribute → {"ok":true}
```

- **pytest:** `43 passed` in `tests/crop_book/test_calculators.py`

---

## 10. Top items for team_100

1. **F-CALC-002:** Include `crop-book-v1.js` on `/calc/` (e.g. `$active === 'calc' \|\| $active === 'crop-book'` in `_layout.php`) and re-run LIVE calc recompute + AssumptionField test.
2. **F-EXPORT-001:** Restore `/calc/export.pdf` route (200 print HTML per HEAD PHPUnit) on uPress.
3. **F-CALC-003:** Align dashboard copy vs rendered modules, or add remaining calculator panels per catalog.
4. **F-STAT-001/002:** Refresh hub stat strings to API counts (70 / 65) or document intentional subset.
5. **F-MKT-002:** Confirm ingest/publish path for community `last_price` on products (data ops), then re-test market price match.

---

## 11. Overall verdict rationale

| Layer | Result |
|-------|--------|
| **2026-06-02 deploy (data + v1 UI shell)** | **PASS** — F-OPS-001 closed; family fix verified; contribute API live |
| **LIVE calculator UX on `/calc/`** | **FAIL** subset — JS not wired (F-CALC-002) + PDF 404 (F-EXPORT-001) |
| **Formula / Python SSOT** | **PASS** — 43/43 pytest |

**Combined verdict: PASS_WITH_FINDINGS** — deployment validation succeeds for crop-book v1 and F-DATA-001; calculator **dashboard** and PDF export need team_10/100 fix before calling calc area production-ready.

---

*Report filed by team_50 · 2026-06-02 · Mandate HANDOFF_team50_E2E-FULL_2026-06-02_v1.0.0.md*
