---
document_type: E2E_QA_REPORT
version: "1.0.0"
from: team_50 (QA & Functional Acceptance)
to: team_100 (Chief System Architect)
cc: team_00, team_99
date: 2026-06-01
wp: SFA-S003-P004
mandate: _COMMUNICATION/TEAM_50/HANDOFF_50_E2E-BROWSER-QA_2026-06-01_v1.0.0.md
merge_baseline: 8795b8a
engine: Cursor Composer
---

# E2E QA Report — SFA Delivery Tier (full surface)

## Verdict box

| Field | Value |
|-------|-------|
| **Verdict** | **PASS_WITH_FINDINGS** |
| **WP** | SFA-S003-P004 (post-merge acceptance) |
| **Environments** | LIVE `https://sfa.nimrod.bio` + HEAD `main` @ `8795b8a` (PHPUnit harness; local PHP server blocked without MySQL) |
| **Next step** | **team_99:** deploy `sfa_delivery/` from `main` via `scripts/ftp_deploy_sfa_ui.sh` (see UI_DEPLOY_RUNBOOK). **team_100:** triage F-DATA-001 (tomato family taxonomy in mirror). Re-run LIVE browser sweep after deploy. |

---

## 1. Environment

| Item | Detail |
|------|--------|
| **LIVE** | `https://sfa.nimrod.bio` — uPress Slim4/PHP, MySQL mirror (`GET /api/v1/health` → `status: ok`, `db: ok`, PHP 8.5.5) |
| **HEAD acceptance** | Repo at `8795b8a`; `composer test` → **107/107** tests, **313** assertions, 0 failures; `CropBookV1RouteTest` → **20/20** (v1 routes/filters/export/depth) |
| **Local browser** | `php -S 127.0.0.1:8080` started but all routes **HTTP 500** (no `sfa_delivery/.env` / MySQL on workstation). v1 UI acceptance used **in-memory PHPUnit** per plan fallback. |
| **Browser tool** | cursor-ide-browser MCP (375px mobile viewport); corroboration: `curl` + API JSON |
| **AOS validation** | `validate_aos.sh .` → **29 PASS / 19 SKIP / 0 FAIL** |
| **Contribute** | **Not tested** on LIVE (POST `/api/v1/contribute` returns 404 — endpoint absent on deployed build). Marked UNTESTED to avoid pollution. |

### 1.1 Deploy drift (confirmed — OPS, not product defect on HEAD)

`main` @ `8795b8a` (Crop Book v1 + patch01) is **not** deployed to LIVE. Marker probe:

| Marker | HEAD (`main`) | LIVE (`sfa.nimrod.bio`) |
|--------|---------------|-------------------------|
| `wc-cropbook-hero` in `/crop-book/` HTML | Expected | **0** |
| `crop-book-v1.css` linked | Expected | **0** (asset URL → **404**) |
| `crop-book-v1.js` | Expected | **0** |
| `/calc/export` or `calc-export` buttons | Expected | **0** |
| `mod-card__hero` on `/` | Expected (`module-*.png`) | **0** |
| `wc-tomato` on crop cards | Expected (28 crops) | **0** |
| Depth tabs `?depth=simple\|full\|drill` | Expected | **0** on `/crop-book/tomatoes/` |
| `prov-` / `assumption-field` cues | Expected | **0** |
| `POST /api/v1/contribute` | Expected | **404** |

**Implication:** Mandate items for Crop Book v1 UI, calc export, module watercolor heroes, and prov/AssumptionField must be signed off on **HEAD** (PHPUnit) until team_99 deploys. LIVE QA below covers **legacy deployed surfaces** + **data accuracy** via public API.

**Route:** team_99 — [`documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`](../../documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md), `bash scripts/ftp_deploy_sfa_ui.sh` from allowlisted egress (waldhomeserver).

---

## 2. Per-interface results

Legend: **L** = LIVE browser/curl, **H** = HEAD @ `8795b8a` (PHPUnit where LIVE lacks v1).  
Columns: loads | data-accurate | UX | rendering | notes

### Hub / global

| Route | L loads | L data | L UX | L render | H (8795b8a) | Notes |
|-------|---------|--------|------|----------|-------------|-------|
| `/` | PASS | PARTIAL | PASS | PASS | N/A browser | 3 live modules navigable (crop-book, market, calc). Coming-soon cards (תכנון עונה, ניהול לקוחות, …) are headings only — no 404. Stat drift: **66** crops / **30** products vs API **70** / **65** (F-STAT-*). No `mod-card__hero` (deploy). |
| `/about` | PASS | N/A | PASS | PASS | — | Tier list present (`hub-tier-list` / tier copy). |
| `/search` | PASS | PASS | PASS | PASS | — | `?q=חסה` 200; API `/api/v1/search?q=חסה` returns lettuce crop + products. |
| `/search?q=ZZZNOMATCH` | PASS | PASS | PASS | PASS | — | Empty/no-match state 200 (no crash). |
| `/community` | PASS | N/A | PASS | PASS | — | WhatsApp CTA, tier explainer. No market-style `mk-disclaimer` block (F-COMM-001). Feed items in sidebar on other pages; mobile snapshot did not show feed section body. |
| `/clients/` | 302→`/` | — | PASS | — | — | AC-U4-07 redirect OK. |

### Crop Book (LIVE = legacy deep template; v1 = H only)

| Route | L loads | L data | L UX | L render | H (8795b8a) | Notes |
|-------|---------|--------|------|----------|-------------|-------|
| `/crop-book/` | PASS | PASS | PASS | PASS | **PASS** (tests) | Entry paths OK. `method="get"` filter form present. **70** crop cards vs stat **66**. No hero banner / watercolor (deploy). |
| `/crop-book/?view=table` | PASS | PASS | PASS | PARTIAL | **PASS** (testBookIndexTableView) | LIVE: no `<table>` in HTML (still card layout). H: table view 200. |
| `/crop-book/?family=מצליבים` | PASS | PASS | PASS | PASS | **PASS** (family filter test) | Lettuce excluded, radish retained (curl). |
| `/crop-book/?q=ZZZNOMATCH` | PASS | — | PASS | PASS | **PASS** (empty-state + form test) | Filter bar recoverability on H verified in PHPUnit. |
| `/crop-book/tomatoes/` | PASS | PARTIAL | PASS | PASS | **PASS** (depth tests) | LIVE: rich legacy page (calendar, varieties, agronomy). DTM **70** matches API. No depth tabs / prov cues (deploy). Latin label **Aizoaceae** shown — mirror data issue (F-DATA-001). |
| `/crop-book/tomatoes/?depth=full` | PASS | — | — | — | **PASS** | Query param ignored on LIVE (no v1). H: 200 all depths. |
| `/crop-book/lettuce/` | PASS | PASS | PASS | PASS | **PASS** | API `dtm_max` 73; page shows **73 ימים** on index link. |
| `/crop-book/cauliflower/` | PASS | PASS | PASS | PASS | — | Sparse crop loads (minimal DTM). |
| `/crop-book/tomatoes/variety/bellstar/` | **404** | — | — | — | Route exists on H | Variety drill on LIVE N/A (legacy lists varieties on crop page). |
| `/crop-book/questions` | PASS | N/A | PASS | PASS | — | |
| `/crop-book/family` | PASS | N/A | PASS | PASS | — | |
| `/crop-book/family/solanaceae` | **302**→family | — | PASS | — | **PASS** (redirect test) | No 404. |
| `/crop-book/table` | PASS | N/A | PASS | PASS | — | |
| `/crop-book/search` | PASS | N/A | PASS | PASS | — | |
| `/crop-book/cover-crops` | PASS | N/A | PASS | PASS | — | |

### Calculator

| Route | L loads | L data | L UX | L render | H (8795b8a) | Notes |
|-------|---------|--------|------|----------|-------------|-------|
| `/calc/` | PASS | PASS | PARTIAL | PASS | **PASS** (calc dash test) | LIVE: **single** beta yield calc (3 spinbuttons). Changing area **50** → totals **460 kg**, **₪5704** (9.2×50×12.4) — recompute OK. **Not** 6 calcs #1,#7,#8,#9,#10,#12 (deploy). |
| `/calc/export.csv` | **404** | — | — | — | **PASS** (CSV test) | |
| `/calc/export.pdf` | **404** | — | — | — | **PASS** (print HTML test) | |

### Market

| Route | L loads | L data | L UX | L render | H (8795b8a) | Notes |
|-------|---------|--------|------|----------|-------------|-------|
| `/market/` | PASS | PASS | PASS | PASS | — | `mk-disclaimer` present. **65** `pcard` rows in HTML; Hebrew names legible. Category chips use **English** slugs (F-MKT-001). |
| `/market/prd017` | PASS | PASS | PASS | PASS | — | API `last_price` **15.25**; HTML contains **15.25**. Disclaimer macro on detail template. |

### API smoke (read-only)

| Endpoint | Result |
|----------|--------|
| `GET /api/v1/health` | PASS |
| `GET /api/v1/crops` | PASS — count **70** |
| `GET /api/v1/products` | PASS — count **65** |
| `GET /api/v1/assumptions` | Not probed on LIVE (assumed present if deploy includes WP-CB-1 API) |
| `POST /api/v1/contribute` | **404** on LIVE |

---

## 3. Findings

| ID | Severity | Route / area | Observation | Repro |
|----|----------|--------------|-------------|-------|
| **F-OPS-001** | **BLOCKER** (acceptance) | Deploy | `main` @ `8795b8a` UI not on LIVE: no `crop-book-v1`, hero, calc export, module heroes | `curl -sL https://sfa.nimrod.bio/crop-book/ \| grep crop-book-v1` → 0; `curl -sI .../crop-book-v1.css` → 404 |
| **F-V1-001** | **MAJOR** (LIVE only) | Crop Book v1 | Depth tabs, prov_value cues, AssumptionField, 13-topic v1 layout, watercolor art absent on LIVE | Open `/crop-book/tomatoes/` — legacy sections only |
| **F-CALC-001** | **MAJOR** (LIVE only) | `/calc/` | Mandated 6-cal dashboard + export not deployed; legacy single calc only | Open `/calc/` — no export links |
| **F-API-001** | **MAJOR** (LIVE only) | API | `POST /api/v1/contribute` → 404 | `curl -X POST .../api/v1/contribute -d '{"kind":"request-info",...}'` |
| **F-DATA-001** | **MAJOR** | Data mirror | `tomatoes` API `identity.family.scientific_name` = **Aizoaceae** (ice-plant family); UI shows as Latin name for tomato | `GET /api/v1/crops/tomatoes` vs crop detail “שם לטיני” |
| **F-STAT-001** | MINOR | `/`, `/crop-book/` | Hub/crop-book copy says **66** crops; API count **70** | Compare stat text vs `GET /api/v1/crops` |
| **F-STAT-002** | MINOR | `/` | Hub market stat **30** products; API **65** | Compare stat vs `GET /api/v1/products` |
| **F-MKT-001** | MINOR | `/market/` | Category facet labels are English (`alliums`, `leafy_greens`) | Open market index chips |
| **F-COMM-001** | MINOR | `/community` | No market-style disclaimer block; handoff asked “mandatory disclaimer” — market has `mk-disclaimer`, community uses contact lede only | Open `/community/` |
| **F-VAR-001** | MINOR (LIVE) | Variety route | `/crop-book/tomatoes/variety/bellstar/` → 404 on LIVE | Direct URL (expected until deploy + slug wiring) |

**Not flagged (per handoff §6):** glyph fallback for non-28 crops; `field_state` null on LIVE API (honest degrade once v1 deployed); proposed fields; calc PDF = print HTML; server-side pytest failures out of browser scope.

**HEAD remediation:** No code defects found in v1 route tests at `8795b8a`. Real bugs on LIVE legacy layer: **F-DATA-001**, stats drift — route to data ingest / team_10, not WP-CB-1-patch02 unless repro on HEAD after deploy.

---

## 4. Scenario matrix (GCR-002)

| Surface | 1 Happy | 2 Error | 3 Edge | 4 Dup | 5 Cancel |
|---------|---------|---------|--------|-------|----------|
| Crop-book filters (LIVE) | family=מצליבים narrows | — | `q=ZZZNOMATCH` 200 | N/A | clear via new GET |
| Crop-book filters (H) | PHPUnit family/dtm/q | — | empty-state keeps form | N/A | — |
| Global `/search` | `q=חסה` + API match | gibberish 200 | empty `q` 200 | N/A | — |
| Calc (LIVE) | area 50 → 460 kg / ₪5704 | — | — | N/A | — |
| Calc export (H) | CSV/PDF 200 | empty plan CSV valid | — | N/A | — |
| Contribute | **UNTESTED** (LIVE 404) | H: 400 unknown kind (PHPUnit) | — | N/A | — |
| Market | prd017 price match | — | many products listed | N/A | — |

**DB round-trip:** Read surfaces verified via API ↔ HTML. No persistent contribute test.

---

## 5. Evidence appendix

### 5.1 Deploy drift (curl)

```
crop-book: wc-cropbook-hero=0, crop-book-v1.css=0, method="get"=1
calc: calc/export=0
home: mod-card__hero=0
tomatoes: crop-book-v1.css=0, data-depth=0
crop-book-v1.css HTTP/2 404
```

### 5.2 API samples

```json
GET /api/v1/health → {"status":"ok","db":"ok","php_version":"8.5.5"}
GET /api/v1/crops → count: 70
GET /api/v1/products → count: 65
GET /api/v1/products/prd017 → last_price: 15.25
GET /api/v1/crops/tomatoes → dtm_max: 70, family_name_he: "ריסניים", identity.family.scientific_name: "Aizoaceae"
```

### 5.3 PHPUnit HEAD (CropBookV1RouteTest)

```
OK (20 tests, 49 assertions)
Includes: filter family/dtm/q, empty-state form, depth=simple|full|drill,
calc export csv/pdf, field_state from variety payload, contribute 400 unknown kind
```

Full suite: `composer test` → **107 tests, 313 assertions, 0 failures**.

### 5.4 Browser

- Tool: cursor-ide-browser @ 375px width
- Pages exercised: `/crop-book/`, `/crop-book/tomatoes/`, `/calc/` (input change), `/market/`, `/`, `/community/`
- RTL Hebrew legible; no `Array` or raw DB keys on tomato page HTML grep

---

## 6. Top issues for team_100

1. **F-OPS-001 (BLOCKER for LIVE acceptance):** Schedule team_99 deploy of `sfa_delivery/` @ `8795b8a`, then **re-run** this E2E on LIVE only for v1-specific rows (hero, v1 CSS/JS, depth, prov, calc export, module heroes).
2. **F-DATA-001:** Investigate crop family mapping in MySQL mirror / ingest for `tomatoes` (Aizoaceae vs Solanaceae) before users trust Latin/family labels.
3. **F-STAT-001/002:** Refresh `modules.php` / hub stat strings to match live API counts (70 crops, 65 products) or document intentional “curated subset” copy.

**Cosmetic batch (team_00):** F-MKT-001 English category chips; F-COMM-001 disclaimer alignment with handoff wording.

---

## 7. Overall verdict rationale

| Layer | Result |
|-------|--------|
| **HEAD `8795b8a`** | **PASS** for mandated v1 behavior (PHPUnit 20/20 Crop Book v1 + full suite green). |
| **LIVE legacy** | **PASS_WITH_FINDINGS** for deployed routes (200s, market/crop data largely accurate, calc recompute, redirects). |
| **LIVE vs mandate (post-merge UI)** | **FAIL until deploy** — tracked as F-OPS-001, not as team_10 code defect. |

**Combined verdict: PASS_WITH_FINDINGS** — ship deploy first; then conditional re-test of v1 rows on LIVE.

---

*Report filed by team_50 · 2026-06-01 · Mandate HANDOFF_50_E2E-BROWSER-QA_2026-06-01_v1.0.0.md*
