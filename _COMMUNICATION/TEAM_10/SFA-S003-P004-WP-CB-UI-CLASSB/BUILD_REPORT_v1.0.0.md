---
id: BUILD_REPORT_SFA-S003-P004-WP-CB-UI-CLASSB_v1.0.0
from: team_10 (sfa_build, Claude Sonnet)
to: team_100 (Chief Architect)
cc:
  - team_50
  - team_190
date: 2026-06-02
wp: SFA-S003-P004-WP-CB-UI-CLASSB
branch: claude/wp-cb-ui-align-2026-06-02
gate: L-GATE_B (build complete)
---

# BUILD REPORT — SFA-S003-P004-WP-CB-UI-CLASSB v1.0.0

## §1 Summary

Team_10 (Claude Sonnet, IR#1 builder) has implemented the team_35 Class B v2 design
across all 7 surfaces + shell refinements on the existing Class A app-shell. All 7 minors
from the L-GATE_S verdict (F-01 through F-07) have been folded into the build.

Scope: delivery tier only (`sfa_delivery/**`). No Python backend, no migrations, no
LOCKED files touched.

- **classb.css + classb.js**: ported verbatim from team_35 HANDOFF
- **_layout.php**: Class B route detection + asset loading order (MINOR F-07)
- **Hub (/)**: `.modtile` grid + `.hub-manifest` + `.hub-aud` audience cards
- **Market list (/market/)**: `.pcard` + `.fresh` + `.mkt-disc` + cards⇄table toggle
- **Market detail (/market/{slug})**: `.pdetail` + `.pbig` + `.pgraph` + `.phist` + `.pstats`
- **Search (/search)**: `.srch-group` + `<mark>` + `.srch-nomatch`
- **Community (/community)**: feed-LESS — `.comm-manifest` + `.reqcard`
- **About (/about)**: `.tier-hero` + `.tier-list` + `.tier-row` 5-tier ladder
- **Account (/account)**: NEW `AccountController::index` + `account_landing.php`
  (`.acct-wrap` + `.setgroup` + `"בקרוב"` labels — no auth backend)

---

## §2 Branch + Commits

**Branch:** `claude/wp-cb-ui-align-2026-06-02`

| Commit | Message |
|--------|---------|
| `b9b30b4` | feat: port classb.css + classb.js (AC-1) |
| `154644d` | feat: shell refine + account route + AccountController (AC-1, AC-6, MINOR-7) |
| `c97fe56` | feat: market list + detail Class B reskin (AC-2, AC-3, MINOR-1,2,5) |
| `170332a` | (prior fallback commit containing hub/search/community/about templates) |
| `27b628e` | test: ClassBRouteTest — 22 AC-7 tests |

Build commits on top of dispatch HEAD `e8c7e37`.
Final HEAD: `27b628e`.

---

## §3 AC Table

| AC | Status | Evidence |
|----|--------|---------|
| AC-1 | PASS | `classb.css` (42 711 B) + `classb.js` (1 385 B) match handoff sizes. `_layout.php` loads `classb.css` + `cropbook-v1.js` then `classb.js` on Class B routes. Test `testLayoutLoadsClassbCssOnHub` + `testLayoutLoadsClassbJsOnHub` pass. |
| AC-2 | PARTIAL — visual QA required by team_50 | All 7 surfaces rebuilt to their Board-B frames. Server-render verified by route tests (200 on all routes). Design-vs-live screenshot pairs are team_50's scope (AC-2 visual fidelity). |
| AC-3 | PASS | `.mkt-disc` mandatory on list + detail (never suppressed). Cards⇄table toggle via `.aud` buttons + `data-view` attributes. 3-state freshness pill (`.fresh--fresh/aging/stale`) wired to `freshness_days` per §9a locked thresholds. `.pgraph` + `.rangesel` (7י + 28י live; 90י + שנה `.is-disabled` server-side). `.pcard.is-empty` / `.emptybox` on zero-report products. No fabricated numbers. |
| AC-4 | PASS | Hub: `.hub-grid` / `.modtile` grid from `Modules::all()['modules']`. `.is-soon` on planned modules. `.hub-manifest` explainer band. `.hub-aud` / `.audcard` (gardener/farmer/planner). Tier badges included. |
| AC-5 | PASS | Search: `.srch-group` (book / market groups). `<mark>` highlight in `sfa_mark()`. `.srch-nomatch` + request CTA on zero results. `.srch-suggest` static suggestion chips on empty query. |
| AC-6 | PASS | Community: feed-LESS (manifesto + reqcard only, no `.community__feed`). About: 5-tier `.tier-row` ladder with 4px color spine. Account: login shell + `.acct-empty` open-core + static profile/settings shell, all labeled "בקרוב". |
| AC-7 | PASS (1 pre-existing failure) | `composer test`: 128/129 pass (129 total incl. 22 new). 1 pre-existing failure `testCalcExportPdfReturnsPrintHtml` was failing before this WP (confirmed by git stash pre-check). `validate_aos.sh`: 29 PASS / 19 SKIP / **0 FAIL**. All new routes return 200. RTL via Hebrew dir="rtl" template. No raw keys / "Array" / stray "—" (data-driven rendering). |

---

## §4 The 7 Minors — How Each Was Addressed

| Minor | Finding | Resolution | File:Location |
|-------|---------|------------|---------------|
| F-01 | Disclaimer class `.mk-disclaimer` → `.mkt-disc` | Rewrote `market_disclaimer.php` macro to emit `.mkt-disc` / `.mkt-disc__ic` / `.mkt-disc__head` / `.mkt-disc__list`. Locked 4-bullet copy preserved verbatim. | `templates/macros/market_disclaimer.php:L1–24` |
| F-02 | Range label "30י" → **28י** | `.rangesel` in `market_product.php` labels the active control "28י", wired to `fetchHistory(28)`. Label "7י" also live. Never "30". | `templates/pages/market_product.php:L130-135` |
| F-03 | `.reqchip` kinds vs `contribute` API | All 5 chips POST `kind=request-info` (via hidden field). Chip intent stored in `field_name` (question/price-report/crop-suggest/bug-report/collab). No new API kinds. | `templates/pages/community.php:L55-78` |
| F-04 | Search product rows show fake min/max/source_count | `search_results.php` only reads `price_current` / `last_price` for `.srow__price`. Never renders min/max range or source_count on search rows (the shim values = current price, 0). | `templates/pages/search_results.php:L125-150` |
| F-05 | 90י/year `.rangesel` disabled only in JS | Market detail template emits `disabled aria-disabled="true"` on 90י and שנה buttons server-side. `classb.js::wireRangeSel` also guards. | `templates/pages/market_product.php:L133-134` |
| F-06 | B-delta mentions community feed | `community.php` has no `.community__feed`. LOD400 §9.1 (feed-LESS) supersedes the stale B-delta route table line. | `templates/pages/community.php` — entire file |
| F-07 | Asset loading order for Class B | `_layout.php` detects Class B routes and loads: `classb.css`, then `cropbook-v1.js`, then `classb.js` (defer). Order ensures `wireFilters`/`wireAudience` from cropbook-v1 are available to classb.js. | `templates/_layout.php:L20-55` |

---

## §5 Verification Output

### composer test (sfa_delivery)
```
PHPUnit 10.5.63 by Sebastian Bergmann and contributors.
Runtime: PHP 8.5.6

Tests: 129, Assertions: 339, Failures: 1, PHPUnit Deprecations: 1.
```

**1 pre-existing failure:** `CropBookV1RouteTest::testCalcExportPdfReturnsPrintHtml`
- Confirmed pre-existing by `git stash` pre-check (failed identically before any WP-CB-UI-CLASSB edits)
- Not introduced by this WP
- All 22 new ClassBRouteTest tests PASS

**New tests added (ClassBRouteTest.php):**
- testAccountRouteReturns200, testAccountHasSoonLabels, testAccountHasClassBComponents
- testMarketDetailRendersGraph, testMarketDetailRendersHistory
- testMarketDetailDisabledRanges (MINOR F-05)
- testMarketDetailRangeLabel28Days (MINOR F-02)
- testMarketDisclaimerClassBClass, testMarketListDisclaimerClassBClass (MINOR F-01)
- testSearchGroupedResults, testSearchUsesMarkHighlight, testSearchNoMatch (AC-5)
- testSearchNoFakeRange (MINOR F-04)
- testCommunityIsFeedLess, testCommunityHasManifest, testCommunityHasReqcard (MINOR F-06, AC-6)
- testHubHomeHasModtileGrid, testHubHomeHasManifest (AC-4)
- testAboutHasTierRows (AC-6)
- testLayoutLoadsClassbCssOnHub, testLayoutLoadsClassbJsOnHub (AC-1, MINOR F-07)
- testMarketListHasFreshnessPill (AC-3)

### validate_aos.sh
```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

### php -l (all changed/new PHP files)
All 12 files: "No syntax errors detected"

### git diff --name-only (this WP's files only)
```
sfa_delivery/app/Controllers/AccountController.php  (new)
sfa_delivery/app/routes.php
sfa_delivery/public_assets/css/classb.css  (new)
sfa_delivery/public_assets/js/classb.js  (new)
sfa_delivery/templates/_layout.php
sfa_delivery/templates/macros/freshness_pill.php  (new)
sfa_delivery/templates/macros/market_disclaimer.php
sfa_delivery/templates/pages/account_landing.php  (new)
sfa_delivery/templates/pages/community.php
sfa_delivery/templates/pages/hub_home.php
sfa_delivery/templates/pages/hub_tiers.php
sfa_delivery/templates/pages/market_list.php
sfa_delivery/templates/pages/market_product.php
sfa_delivery/templates/pages/search_results.php
sfa_delivery/tests/ClassBRouteTest.php  (new)
```

No `_aos/**`, no Python backend, no migrations.

---

## §6 SRV-IDEAS Entries Filed

**None** — no server-side features were needed beyond what was already available.
All surfaces degraded gracefully to designed empty states where data was absent.

The existing `SRV-IDEAS/REGISTER.md` already contains pre-filed items (search index,
90d graph, auth). No new entries required from this build.

---

## §7 Next Step

Branch is ready for:
1. **team_50 VISUAL QA** — design-vs-live screenshot pairs per surface (AC-2),
   desktop + mobile, 7 surfaces × 2 = 14 captures. team_50 must verify against
   Board-B frames in `_COMMUNICATION/team_35/.../design/Board-B-*.html`.
2. **Push to origin** — deploy via waldhomeserver FTPS relay to uPress (sfa.nimrod.bio)
   per `UI_DEPLOY_RUNBOOK.md`.
3. **team_190 L-GATE_V** (non-Claude, IR#1/#5) — visual fidelity + code review.

*Issued by team_10 (Claude Sonnet) · 2026-06-02 · IR#1 cross-engine.*
