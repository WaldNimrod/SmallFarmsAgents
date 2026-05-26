# LOD400 — SFA-S003-P002-WP-UI — UX shell + design adoption (Slim/PHP, uPress)

**Date:** 2026-05-24
**Status:** LOD400_DRAFT — awaiting team_190 L-GATE_S validation before BUILD.
**Builder (assigned post-validation):** sfa_build (Sonnet)
**Validator:** team_190 (external, non-Claude per IR#1)
**Effort:** NORMAL (~14h estimated)
**Branch:** new BUILD branch off `claude/gallant-elbakyan-727a60` once L-GATE_S PASS.

---

## §1 Goal

Adopt the team_35 LOD300 design package (`_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/`, v1.2.0) into the live `sfa_delivery/` Slim PHP application at `https://sfa.nimrod.bio`, replacing the interim minimal templates from WP-3 with the canonical Nimrod DS v3.3 design system. The delivery tier moves from "functional" to "branded + on-design".

## §2 Architectural correction — binding for this WP

team_35 LOD300 §2.1 specified **Flask + Jinja2 + SQLAlchemy + gunicorn on waldhomeserver port 5002**. That stack choice predates and contradicts the parent decision `DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN`:

> "waldhomeserver = backend only (not strong enough for end users). uPress is the ONLY public-facing tier."

team_00 approved **Option B** (in-session 2026-05-24): adopt the **design** (CSS, tokens, mental model, components, routing intent, modules registry) but implement on the **already-deployed Slim/PHP/uPress stack**. The IMPLEMENTATION_PLAN.md from team_35 is **superseded** by §11 of this LOD400.

**What survives unchanged from team_35 LOD300:**
- All design tokens (`DESIGN_TOKENS.md`)
- All component DOM contracts (`COMPONENTS.md` — CSS class names, semantic structure)
- All route intents (`TEMPLATES.md` route map — minus `/sfa/` prefix since we're on subdomain)
- All 8 modules + 3 tiers in `MODULES_REGISTRY.yaml`
- All visual artboards (28) in `design/index.html`
- Mobile-first + desktop sidebar accordion strategy
- 3-tier language: open / beta / coming / paid / custom
- Crop-book "4 entry paths" structure (questions / family / table / search)
- Crop → varieties hierarchy (CB5)
- Mandatory market disclaimer pattern
- Community contribution surfaces in every shell

**What changes:**
- `Jinja2 macros` → **plain PHP includes** (PSR-4 autoload + `Template::render()` already exists in `sfa_delivery/app/Lib/Template.php`)
- `Flask Blueprint` → **Slim route group** (already wired in `sfa_delivery/app/routes.php`)
- `SQLAlchemy direct query on prod Postgres` → **PDO query on uPress MySQL mirror** (populated by waldhomeserver `sfa_ingest_push.py` cron — already running)
- `gunicorn on waldhomeserver:5002` → **PHP-FPM on uPress nginx** (already serving)
- `Jinja2 context_processor inject_globals` → **PHP autoload of `modules.php` + helpers** in `Bootstrap.php`
- Asset URL prefix `/sfa/` (WP-relative) → **root-relative** (subdomain-relative): `/`, `/book/`, `/market/`, `/calc/`, `/community/`, `/api/v1/*`

---

## §3 File mapping (binding)

### §3.1 CSS — copy verbatim from `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/design/` to `sfa_delivery/public_assets/css/`

| Source | Target | Curation |
|--------|--------|----------|
| `system.css` (7.6 KB) | `tokens.css` | Strip any `wp-content/themes/...` references if present; keep all `:root` custom properties |
| `gj.css` (22.8 KB) | `gj.css` | Verbatim |
| `hub.css` (9.3 KB) | `hub.css` | Verbatim |
| `community.css` (9.1 KB) | `community.css` | Verbatim |
| `crop-book-deep.css` (13.0 KB) | `crop-book-deep.css` | Verbatim |
| `desktop.css` (13.2 KB) | `desktop.css` | Verbatim |
| `desktop-extras.css` (12.6 KB) | `desktop-extras.css` | Verbatim |

The existing `site.css` (6.5 KB minimal interim from WP-3) is **deleted** — superseded by the team_35 set above. `index.php` front controller doesn't change; `_layout.php` will be rewritten to include the new CSS chain in correct cascade order (`tokens.css` first, then `gj.css`, then specifics).

### §3.2 Static assets

| Source | Target |
|--------|--------|
| Extract SVG vegetable sprite from `illustrations.jsx::CROP_ICON` | `sfa_delivery/public_assets/img/icons.svg` |
| Vanilla JS for accordion state + contribute form submit | `sfa_delivery/public_assets/js/sfa.js` (new, ~80 lines) |
| AI-rendered thumbnails (referenced in `art-prompts.jsx`) | **DEFERRED** to post-MVP. Use SVG icon as placeholder for v1. |

### §3.3 Templates — translate JSX/Jinja2 → PHP includes

Source intent in `design/*.jsx` (React for design iteration only, per team_35 README); production renders in PHP. Template tree below replaces the existing `sfa_delivery/templates/` minimal set:

```
sfa_delivery/templates/                   ← rewritten
├── _layout.php                           ← rewritten (new chrome, no shell yet)
├── shell/
│   ├── mobile.php                        ← .gj-shell wrapper (NEW)
│   ├── desktop.php                       ← .dt-shell wrapper + sidebar (NEW)
│   └── _mark_svg.php                     ← SFA logomark inline (NEW)
├── macros/                               ← Jinja2 macros → PHP partials (NEW)
│   ├── tier_badge.php
│   ├── module_card.php
│   ├── price_card.php
│   ├── crop_card.php
│   ├── variety_row.php
│   ├── contrib_strip.php
│   ├── crosslink.php
│   ├── market_disclaimer.php
│   ├── feed_item.php
│   └── timeline_bar.php
└── pages/
    ├── hub_home.php                      ← H1 / D1 — replaces existing home.php
    ├── hub_tiers.php                     ← H2 / D2 (NEW)
    ├── hub_calc.php                      ← H3 / D7 — STUB only ("בקרוב", calc deferred)
    ├── book_entry.php                    ← CB0 (NEW)
    ├── book_questions.php                ← CB1 (NEW)
    ├── book_family.php                   ← CB2 (NEW)
    ├── book_table.php                    ← CB3 / D3 — refresh of existing crop_book/list.php
    ├── book_search.php                   ← CB4 (NEW)
    ├── book_crop.php                     ← CB5 / D4 — refresh of existing crop_book/detail.php
    ├── book_variety.php                  ← extends CB5 — variety detail (NEW)
    ├── market_list.php                   ← MK1 / D5 — refresh of existing market/list.php
    ├── market_product.php                ← MK2 / D6 — refresh of existing market/detail.php
    ├── community.php                     ← H4 / D9 (NEW)
    └── search_results.php                ← D8 (NEW)
```

Existing `sfa_delivery/templates/_layout.php`, `home.php`, `crop_book/list.php`, `crop_book/detail.php`, `market/list.php`, `market/detail.php`, `error.php` are **deleted/replaced** by the above. The existing `Template::render()` helper (PHP `extract($vars)` + `ob_start()`) keeps working.

### §3.4 Controllers — extend existing + add new

| Existing controller | Change |
|---------------------|--------|
| `HealthController.php` | unchanged |
| `IngestController.php` | unchanged |
| `CropsController.php` | unchanged (JSON API) |
| `ProductsController.php` | unchanged (JSON API) |
| `HomeController.php` | renamed to `HubController.php`; gains `hub()`, `tiers()`, `calc()`, `search()` methods |
| `CropBookViewController.php` | adds `entry()`, `questions()`, `family()`, `tableView()`, `search()`, `variety()` |
| `MarketViewController.php` | adds `productHistoryApi()` (returns 28-day rolling avg JSON) |

**New controllers:**
- `CommunityController.php` — `home()` GET, `contribute()` POST `/api/v1/contribute`
- `SearchController.php` — `globalSearch()` GET `/api/v1/search?q=…`
- `ModulesController.php` — `list()` GET `/api/v1/modules` (mirrors `modules.php` data)

### §3.5 Lib additions

`sfa_delivery/app/Lib/Modules.php` (NEW) — loads `modules.php` static array, exposes `Modules::all()`, `Modules::byTier($tier)`, `Modules::byId($id)`. Mirror of `MODULES_REGISTRY.yaml` (translated once at BUILD time; team_35 YAML is the SSoT — `modules.php` is generated, with header comment "DO NOT EDIT — regenerate from MODULES_REGISTRY.yaml").

### §3.6 Migration

`sfa_delivery/migrations/004_community.sql` (NEW):
```sql
CREATE TABLE IF NOT EXISTS community_contributions (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  submitted_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  context_kind  VARCHAR(40) NOT NULL,        -- 'crop' | 'variety' | 'product' | 'general'
  context_ref   VARCHAR(120) NULL,            -- e.g. crop slug, product slug
  payload_json  JSON NOT NULL,                -- {kind, body_md, contact_optional, ...}
  source_ip_hash VARCHAR(64) NOT NULL,        -- sha256 for rate limiting
  status        VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending|reviewed|published|rejected
  reviewed_at   DATETIME NULL,
  reviewer_note TEXT NULL,
  KEY idx_cc_status_date (status, submitted_at DESC),
  KEY idx_cc_context (context_kind, context_ref),
  KEY idx_cc_rate (source_ip_hash, submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

To apply: enable `ADMIN_MIGRATE_TOKEN` on remote `.env` (rotated to empty post-WP-2), generate one-time token, call `/admin/migrate?token=…`, rotate to empty again.

---

## §4 Routes (binding) — `sfa_delivery/app/routes.php` final state

```php
// HTML
$app->get('/',                       [HubController::class, 'home']);
$app->get('/about[/]',               [HubController::class, 'tiers']);
$app->get('/search[/]',              [HubController::class, 'search']);
$app->get('/calc[/]',                [HubController::class, 'calc']);

$app->get('/book[/]',                [CropBookViewController::class, 'entry']);
$app->get('/book/questions[/]',      [CropBookViewController::class, 'questions']);
$app->get('/book/family[/]',         [CropBookViewController::class, 'family']);
$app->get('/book/table[/]',          [CropBookViewController::class, 'tableView']);
$app->get('/book/search[/]',         [CropBookViewController::class, 'search']);
$app->get('/book/{slug}[/]',         [CropBookViewController::class, 'detail']);
$app->get('/book/{slug}/variety/{vslug}[/]', [CropBookViewController::class, 'variety']);

$app->get('/market[/]',              [MarketViewController::class, 'index']);
$app->get('/market/{slug}[/]',       [MarketViewController::class, 'detail']);

$app->get('/community[/]',           [CommunityController::class, 'home']);

// API
$app->group('/api/v1', function (RouteCollectorProxy $g) {
    $g->get('/health',                       [HealthController::class, 'health']);
    $g->get('/modules',                      [ModulesController::class, 'list']);
    $g->get('/search',                       [SearchController::class, 'globalSearch']);
    $g->get('/crops',                        [CropsController::class, 'list']);
    $g->get('/crops/{slug}',                 [CropsController::class, 'detail']);
    $g->get('/products',                     [ProductsController::class, 'list']);
    $g->get('/products/{slug}',              [ProductsController::class, 'detail']);
    $g->get('/market/{slug}/history',        [MarketViewController::class, 'productHistoryApi']);
    $g->get('/community/feed',               [CommunityController::class, 'feed']);
    $g->post('/community/contribute',        [CommunityController::class, 'contribute']);
    $g->post('/ingest',                      [IngestController::class, 'receive'])
        ->add(HmacAuthMiddleware::class);
});

// Legacy / admin
$app->get('/admin/migrate',          [HealthController::class, 'migrate']);

// Backward compat: existing /crop-book/* and /market/* paths stay during transition
// (already deployed, browser-verified). Will be redirected to /book/* in §5.
$app->redirect('/crop-book/', '/book/', 301);
$app->redirect('/crop-book/{slug}', '/book/{slug}', 301);
```

**URL change:** `/crop-book/` → `/book/` (per team_35 routing map). Browser-redirect handled in Slim with 301. Backward compat: links from waldhomeserver Postgres `crops.slug` are unaffected (slug is the same).

---

## §5 Acceptance Criteria (22)

| # | AC | How to verify |
|---|----|----|
| AC-01 | All 7 CSS files copied verbatim from team_35 handoff to `sfa_delivery/public_assets/css/`, total ~75 KB | `diff` to ensure byte-equivalence with handoff files (allowing `tokens.css` curation) |
| AC-02 | `_layout.php` includes the CSS chain in correct cascade: `tokens.css` → `gj.css` → `hub.css` → `community.css` → `crop-book-deep.css` → `desktop.css` → `desktop-extras.css` | `curl -sS https://sfa.nimrod.bio/ | grep -c stylesheet` returns 7 |
| AC-03 | Google Fonts preconnect + Assistant + Frank Ruhl Libre + JetBrains Mono load in `<head>` | DOM inspect |
| AC-04 | `dir="rtl" lang="he"` on `<html>` everywhere | curl + grep |
| AC-05 | Mobile shell `.gj-shell` renders on `< 900px` viewports | Claude_in_Chrome resize to 390x844, screenshot |
| AC-06 | Desktop shell `.dt-shell` renders on `≥ 900px` with sidebar accordion using `<details>` | Claude_in_Chrome resize to 1280x900, screenshot |
| AC-07 | Hub home (`GET /`) lists 8 modules in 3 tier sections (open / paid / custom), with `tier_badge` colors matching tokens (leaf/sun/soil/tomato/paper) | DOM inspect: `.module-card` count = 8; `.tier--leaf .tier--soil .tier--tomato` all present |
| AC-08 | Crop book entry (`/book/`) presents the 4 entry paths (questions/family/table/search) per CB0 artboard | screenshot vs `_handoff/design/index.html` artboard CB0 |
| AC-09 | Crop detail (`/book/<slug>/`) shows crop → varieties hierarchy per CB5 (crop top, varieties as expandable rows) | screenshot vs CB5 |
| AC-10 | Market list (`/market/`) leads with mandatory disclaimer block "what / from / why / NOT" per design | DOM inspect first `.market-disclaimer` block has 4 sub-bullets |
| AC-11 | `community_contributions` table created on uPress MySQL (migration 004) | phpMyAdmin DESCRIBE returns the 9 columns + 3 keys |
| AC-12 | `POST /api/v1/community/contribute` accepts `{kind, context_ref, body_md, contact_optional}` JSON, returns 200 + `{id}`, rate-limited (max 3 per IP per hour) | curl × 4 from same IP, 4th returns 429 |
| AC-13 | `GET /api/v1/modules` returns JSON mirror of `MODULES_REGISTRY.yaml` (8 modules + 3 tiers + 4 pages + contact) | curl + jq validation |
| AC-14 | `GET /api/v1/search?q=עגבני` returns hits from crops + products (no community in v1 — empty `community: []` array) | curl + jq, expect `crops` array non-empty |
| AC-15 | Old route `/crop-book/` 301-redirects to `/book/` (no broken bookmarks for existing users) | `curl -sSI` returns `HTTP/2 301 location: /book/` |
| AC-16 | All Hebrew rendered correctly (no mojibake) — RTL alignment correct on all 14 page templates | Manual browser pass over each route |
| AC-17 | `LCP < 2.5s` on a simulated 4G profile (Chrome devtools throttling) for hub home + book table + market list | Lighthouse run, screenshot |
| AC-18 | Zero JS errors on all 14 page templates (`read_console_messages onlyErrors:true`) | Claude_in_Chrome console check |
| AC-19 | WCAG AA contrast on all text/background pairs in the token palette | axe-core or manual check on top 5 pages |
| AC-20 | `sfa.js` vanilla: accordion `<details>` state persists per session via `sessionStorage`; `ContribForm` submit shows inline success/error w/o page reload | Manual test |
| AC-21 | Existing `/api/v1/health`, `/api/v1/crops`, `/api/v1/products`, `/api/v1/ingest` (HMAC) all continue to function — no regression | curl smoke test each endpoint |
| AC-22 | Existing daily cron from waldhomeserver continues to push products successfully (post-deploy, observe next 06:30 push in `/data/backups/sfa-ingest-push.log`) | tail log on waldhomeserver |

---

## §6 GCR analysis

**No locked-file changes in Python on waldhomeserver.** The publisher (`sfa_ingest_push.py`) is unchanged. The Postgres canonical SSoT is read-only from the new tier's POV; no schema change there.

**On uPress side:**
- New migration `004_community.sql` adds a table — additive, no GCR
- All other PHP changes are new files or non-locked edits

**Q5 from team_35 LOD300** (variety `taste_rating` field) → **answered: not in WP-UI scope.** No data field added; CB5 detail page renders only fields already in `crop_varieties.payload_json` (which already carries days_to_maturity, planting_method, etc. from `sfa_ingest_push.py`).

**No GCR needed.**

---

## §7 Out of scope (deferred)

| Item | Reason | Where |
|------|--------|-------|
| Calculator (β) full implementation | per team_35 §6 Q7 — separate WP | WP-UI-patch01 or new WP-B3 |
| Email notification to team_00 when contribution arrives | needs SMTP credentials on uPress (or waldhomeserver-side polling) — separate concern | WP-UI-patch01 |
| Admin review UI for community contributions | not in v1 (contributions go to DB; reviewed via phpMyAdmin) | future WP |
| AI-rendered thumbnails (`art-prompts.jsx`) | per team_35 §6 Q8 — pre-render external tool, separate ops task | future |
| Server-side device detection | per team_35 §3.5 — out of scope; CSS media query at 900px is the swap | – |
| `taste_rating` variety field | per §6 above | – |
| Retire WP shortcodes on legacy site | already DONE in WP-S003-P003-WP-5 (full deletion 2026-05-24) | – |
| Search engine (global) — full FTS | v1 uses LIKE queries on `crops.hebrew_name + products.hebrew_name`; FTS = later | future |
| `/api/v1/market/<slug>/history` chart frontend rendering | endpoint serves data; chart drawing = vanilla JS in WP-UI; if too complex, ship table-only | inline |

---

## §8 Risks + mitigations

| # | Risk | Mitigation |
|---|------|------------|
| R-01 | CSS cascade order issue (a later file overrides tokens unexpectedly) | Strict order in `_layout.php`; visual diff against `design/index.html` for each page |
| R-02 | RTL bug in `<details>`/`<summary>` accordion (Safari quirks) | Test in Chrome + Safari mobile; CSS-only chevron flip via `[dir=rtl]` selector |
| R-03 | Mobile font-load FOUT (Frank Ruhl Libre is heavy) | `font-display: swap` in Google Fonts URL params (already in `index.html` of design canvas) |
| R-04 | `community_contributions` exposed to spam without auth | Rate limit by `source_ip_hash`; honeypot field; `payload_json.body_md` length cap 4000 chars |
| R-05 | Static `modules.php` drift from `MODULES_REGISTRY.yaml` | At BUILD: generator script `bin/regenerate_modules.php` that reads YAML and writes PHP array; idempotent; rerun after every YAML edit. Documented in README. |
| R-06 | Translation Jinja2 macros → PHP partials loses semantics (e.g. macro args become global `extract()`) | Each partial is small (<100 lines); test pages render the macro correctly by visual diff |
| R-07 | Existing `/crop-book/` URLs in CF cache continue to 200 (CF caches 301s) | Cache-Control: `no-cache` on the redirect response; CF purge after deploy |
| R-08 | Calculator stub (`/calc/`) confuses users seeing "beta · בקרוב" badge | Calc page shows "בטא · בפיתוח" badge + 1-paragraph explainer + WhatsApp CTA |
| R-09 | uPress nginx still doesn't fully process `.htaccess` (F-1 from WP-2) | `composer.json` + SQL files remain readable but harmless (no secrets); same as today |
| R-10 | 7 CSS files + 1 JS file load = waterfall hurts LCP | Inline tokens.css critical path in `<head>`; defer non-critical CSS; verify Lighthouse >75 |

---

## §9 Test plan

- **Visual diff (manual + Claude_in_Chrome):** for each of the 14 page templates, screenshot at 390x844 (mobile) and 1280x900 (desktop), compare against `design/index.html` artboards (CB0..CB5, MK1, MK2, H1..H4, D1..D9)
- **phpunit:** add `tests/CommunityContributeTest.php` (4 cases: happy path, rate limit, oversized body, missing required field)
- **phpunit:** add `tests/SearchTest.php` (3 cases: empty q, crops-only match, products-only match)
- **phpunit:** add `tests/ModulesTest.php` (2 cases: list count = 8, tier filter)
- **Live smoke:** AC-21 + AC-22 end-to-end on production sfa.nimrod.bio + waldhomeserver cron
- **Lighthouse:** automate via `npx lighthouse https://sfa.nimrod.bio/ --output=json` once post-deploy

Total expected new test count: ~9 unit + 5 visual baselines.

---

## §10 Definition of Done (L-GATE_V criteria)

1. All 22 ACs pass
2. `composer test` exit 0 (existing 11 + new ~9 = 20 phpunit tests pass)
3. Visual diff vs design canvas: each of the 14 page templates shows the expected artboard layout (no off-by-margin issues > 4px)
4. Lighthouse mobile: Performance ≥ 75, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 90
5. Zero console errors on any of the 14 routes (Claude_in_Chrome `read_console_messages onlyErrors:true`)
6. Old `/crop-book/*` 301-redirects work (browser test)
7. Daily cron from waldhomeserver still posts cleanly (24h observation in `/data/backups/sfa-ingest-push.log`)
8. team_190 external L-GATE_V verdict PASS or PASS_WITH_FINDINGS
9. `validate_aos.sh` 0 FAIL on spoke
10. Roadmap entry → COMPLETE/LOD500_LOCKED + BUILD_REPORT filed

---

## §11 Build plan (8 phases — replaces team_35 IMPLEMENTATION_PLAN)

| Phase | Hours | Scope | Output |
|-------|-------|-------|--------|
| B.0 | 0.5 | Branch: `claude/sfa-ui-build` off `gallant-elbakyan-727a60`. Empty `bin/regenerate_modules.php`. Migration 004 file. Verify `_handoff/` files accessible. | Branch + 1 PHP script stub + 1 migration |
| B.1 | 2 | Copy 7 CSS files + extract icons.svg from illustrations.jsx. Build `tokens.css` from `system.css`. Update `_layout.php` to include the chain in correct cascade. Deploy via FTPS. Visual verify baseline. | 7 CSS + 1 SVG + new `_layout.php` |
| B.2 | 3 | Build mobile + desktop shell partials (`shell/mobile.php`, `shell/desktop.php`, `shell/_mark_svg.php`). Build all 10 macros (`macros/*.php`). | 13 PHP files |
| B.3 | 2 | Hub: `hub_home.php`, `hub_tiers.php`, `hub_calc.php` (stub). Add `HubController.php` (rename of HomeController). Wire 4 routes. | 3 templates + 1 controller |
| B.4 | 3 | Crop book entry/questions/family/table/search (5 templates). Extend `CropBookViewController.php`. Note: `questions`+`family` need sample structure data; v1 uses static categorization in PHP. | 5 templates + controller methods |
| B.5 | 1 | Crop detail (CB5) + variety detail. Refresh `book_crop.php` + new `book_variety.php`. | 2 templates |
| B.6 | 1 | Market list + product with mandatory disclaimer macro. Refresh `market_list.php` + `market_product.php`. | 2 templates |
| B.7 | 1 | Community page + contribute form. `CommunityController.php`. Apply migration 004. `SearchController.php` + `ModulesController.php`. `sfa.js`. | 3 controllers + 1 template + JS + 1 migration |
| B.8 | 1 | Browser pass (Claude_in_Chrome screenshots × 14 routes × 2 viewports = 28). Lighthouse. Commit + BUILD_REPORT. Hand off to team_190 for L-GATE_V. | Screenshots + report |
| **Total** | **14.5** | | |

---

## §12 Definition of "L-GATE_S PASS" (this LOD400 → BUILD)

team_190 (external, non-Claude per IR#1) reviews **this LOD400** for:
1. Architectural consistency with parent DECISION_SFA-S003-P003 (Slim/PHP/uPress is enforced; no Flask resurrection)
2. AC completeness (22 ACs cover all 14 routes + APIs + regression)
3. Risk register completeness (R-01..R-10 sane)
4. GCR analysis correctness (no locked-file changes hidden)
5. Test plan adequacy (~20 phpunit covers behavior; visual diff covers presentation)
6. Out-of-scope items are genuinely deferrable (don't smuggle scope creep into v1)
7. Phase plan is realistic (14.5h is achievable for the listed deliverables)

Validation request → `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI/L-GATE_S_VALIDATION_PROMPT_v1.0.0.md`.

team_190 verdict → `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI/L-GATE_S_VERDICT_v1.0.x.md`.

If PASS or PASS_WITH_FINDINGS (no BLOCKERs): team_100 dispatches BUILD to sfa_build via canonical handoff message.

If FAIL: team_100 amends LOD400, re-submits.

---

*LOD400 authored 2026-05-24 by team_100 (smallfarmsagents). Awaiting team_190 L-GATE_S validation. No BUILD activity until then per IR#1 + IR#4.*
