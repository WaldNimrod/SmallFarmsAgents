# Source Onboarding — Status Report & Phase 2 Plan

**Date:** 2026-04-04
**Author:** Team 100 (Architecture)
**Status:** Phase 1 COMPLETE — Phase 2 PLANNING

---

## Phase 1 Summary — COMPLETED

### Sources Registered (36 total)

| ID | Name | Display Bucket | Platform | Status | Items |
|----|------|---------------|----------|--------|-------|
| SRC001 | easyFarm platform | discovery | easyfarm | inactive | — |
| SRC002 | סבתא יהודית | grower | easyfarm | **active** | ✅ |
| SRC003 | ח'ביזה | grower | easyfarm | **active** | ✅ |
| SRC004 | קיימא בית זית | grower | easyfarm | **active** | ✅ |
| SRC005 | קיימא חוקוק | grower | easyfarm | **active** | ✅ |
| SRC006 | עץ השדה | grower | easyfarm | **active** | ✅ (small) |
| SRC007 | סלסילה | grower | — | inactive | — |
| SRC008 | שדה ירוק | grower | — | inactive (dead) | — |
| SRC009 | משק זינגר | grower | — | inactive (dead) | — |
| SRC010 | Farmerim | store | farmerim | **active** | ✅ 268 items |
| SRC011 | האורגני | store | — | inactive (login wall) | — |
| SRC012–014 | Discovery sources | discovery | — | inactive | — |
| SRC015–016 | Govt benchmarks | benchmark | — | candidate | — |
| SRC017–018 | Deprecated | benchmark | — | deprecated | — |
| SRC019–020 | Verification | verification | — | inactive | — |
| **SRC021** | **מהמשק** | **grower** | **easyfarm** | **NEW active** | **1,119 items** |
| **SRC022** | **גן השדה — ירקות אורגניים** | **grower** | **easyfarm** | **NEW active** | **283 items** |
| **SRC023** | **חווה באהבה** | **grower** | **easyfarm** | **NEW active** | **63 items** |
| **SRC024** | **משק ימין אורד** | **grower** | **easyfarm** | **NEW active** | **22 items** |
| SRC025 | ניצת הדובדבן | grower | custom_aspnet | candidate | ~68 est. |
| SRC026 | המשק של בן | grower | rexail | candidate | ~70 est. |
| SRC027 | ערן אורגני | grower | custom | candidate | TBD |
| SRC028 | הגינה של תמרי | grower | custom | candidate | TBD |
| SRC029 | משתלת הראה | grower | mypips | candidate | ~307 est. |
| SRC030 | פרי לנשמה | store | mypips | candidate | ~217 est. |
| SRC031 | הענתיות | grower | mypips | candidate | ~25 cats |
| SRC032 | משק רתם פיין | grower | mypips | candidate | ~11 cats |
| SRC033 | חוות שורשים | grower | custom | candidate | basket |
| SRC034 | משק אורגני — המעפיל | grower | custom | candidate | basket |
| SRC035 | משק יוסף | grower | custom | candidate | basket |
| SRC036 | טבע שוק | store | sellio | candidate (Phase B) | ~129 est. |

### Infrastructure Delivered

1. **`display_bucket` column** — Added to `sources` table with CHECK constraint: `grower`, `store`, `chain`, `discovery`, `benchmark`, `verification`
2. **Source type filter** — Published JSON now includes `source_types[]` and `category` per product
3. **Filter UI** — Filter bar with buttons (הכל / מגדלים / חנויות / רשתות) added to WordPress body template
4. **Published data** — 62 products from 10 active community sources, uploaded to nimrod.bio

---

## Phase 2 Plan — New Parser Development & Dictionary Optimization

### Phase 2A: Dictionary Optimization (IMMEDIATE — Team 10)

**Priority:** CRITICAL — 662 unresolvable items from new easyFarm sources

| Source | Extracted | Resolved | Unresolvable | Scope Skipped |
|--------|-----------|----------|-------------|---------------|
| SRC021 מהמשק | 1,119 | 146 (13%) | **545** | 428 |
| SRC022 גן השדה | 283 | 100 (35%) | **96** | 87 |
| SRC023 חווה באהבה | 63 | 30 (48%) | **16** | 17 |
| SRC024 משק ימין אורד | 22 | 13 (59%) | **5** | 4 |

**Work required:**
1. Query unresolvable items, identify patterns
2. Add product aliases to `product_aliases` table
3. Add new products to `products` table for items not yet in catalog
4. Add `catalog_scope_skip_rules` for non-produce items
5. Re-run normalization cycle, iterate until ≥90% resolution

### Phase 2B: Static HTML Parsers (Team 10)

New parsers for sites that serve static HTML (no JS rendering needed):

| Priority | Source | Platform | Products | Parser Effort |
|----------|--------|----------|----------|---------------|
| P0 | SRC025 ניצת הדובדבן | ASP.NET custom | 68 | Medium — `.productcubecontainer` selectors |
| P0 | SRC026 המשק של בן | Rexail (`__NEXT_DATA__` JSON) | 70 | Medium — JSON parse from script tag |
| P1 | SRC027 ערן אורגני | Custom | TBD | Needs deeper HTML analysis |
| P1 | SRC028 הגינה של תמרי | Custom | TBD | Needs deeper HTML analysis |

**Work required per source:**
1. Create parser class in `organic_market_agent/parsers/`
2. Register in `parsers/engine.py` `_PARSER_MAP`
3. Add normalizer_type to `chk_np_normalizer_type` constraint
4. Create `source_fetch_profiles` with correct selectors
5. Create `normalizer_profiles`
6. Set source `is_active = true, status = 'active'`
7. Run pipeline + dictionary optimization (Phase 2A pattern)

### Phase 2C: Headless Browser Infrastructure + mypips (Team 20 + Team 10)

Requires Playwright/Selenium integration for JS-rendered sites:

| Source | Platform | Products | Notes |
|--------|----------|----------|-------|
| SRC029 משתלת הראה | mypips/Firebase | 307 | Orders active |
| SRC030 פרי לנשמה | mypips/Firebase | 217 | Orders closed |
| SRC031 הענתיות | mypips/Firebase | 25+ cats | CSA model |
| SRC032 משק רתם פיין | mypips/Firebase | 11 cats | Orders closed |

**Work required:**
1. Add Playwright dependency to project
2. Create `HeadlessBrowserCollector` base class
3. Create `MypipsCollector` extending headless collector
4. Create `MypipsParser` for DOM extraction
5. One collector serves all mypips stores via parameterized handle

### Phase 2D: CSA Basket & Phase B (Future)

| Source | Type | Notes |
|--------|------|-------|
| SRC033–035 | CSA basket | Basket-level pricing only |
| SRC036 | Phase B retail | Sellio platform, mostly conventional |

---

## Recommended Execution Order

```
Phase 2A (Dictionary)     ←— IMMEDIATE, blocks quality
    ↓
Phase 2B (Static parsers) ←— 1-2 weeks, highest ROI
    ↓
Phase 2C (Headless)       ←— 2-3 weeks, infrastructure investment
    ↓
Phase 2D (CSA + Phase B)  ←— Deferred, lower priority
```

---

## Mandates Required

| Mandate | Team | Content | Blocks |
|---------|------|---------|--------|
| A3 — Dictionary optimization | Team 10 | Resolve 662 unresolvable items from SRC021-024 | Quality |
| A2 — Static parsers | Team 10 | Build parsers for SRC025-028 | Source count |
| A4 — QA validation | Team 50 | Validate all new sources + filter | Go-live |
| B0 — Headless infrastructure | Team 20 | Playwright integration | mypips sources |
| B1 — mypips parsers | Team 10 | MypipsCollector + MypipsParser | SRC029-032 |

---

*Prepared by: Team 100 (Architecture)*
*Date: 2026-04-04*
