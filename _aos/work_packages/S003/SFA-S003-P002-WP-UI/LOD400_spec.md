# LOD400 — SFA-S003-P002-WP-UI — UX shell + design adoption (Slim/PHP, uPress)

**Version:** v1.0.3 (Q1=A amendment — team_00 BEM-SSoT clarification for RE-BUILD)
**Date:** 2026-05-24 (R1) → 2026-05-27 (R2 amendment + R2 verdict cleanup) → 2026-05-27 20:00 IDT (v1.0.3 Q1=A amendment)
**Status:** LOD400_LOCKED — L-GATE_S R2 PASS_WITH_FINDINGS (team_190, 2026-05-27). Post-revoke RE-BUILD active per `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md`. Ready for BUILD dispatch.
**Builder (assigned post-validation):** sfa_build (Sonnet)
**Validator:** team_190 (external, non-Claude per IR#1)
**Effort:** NORMAL (~13h estimated — slightly reduced after community-writes scope drop)
**Branch:** new BUILD branch off `claude/gallant-elbakyan-727a60` once L-GATE_S PASS.

---

## §0 Round 2 amendment summary (responding to team_190 verdict v1.0.0)

team_190 R1 verdict (`_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`, 2026-05-27) returned FAIL with 5 findings. Round 2 changes:

| Finding | Severity | Remediation |
|---------|----------|-------------|
| **LV-S-1** Public community writes contradict S003 read-only delivery-tier + schema-frozen-at-6-tables | BLOCKER | **Community write surfaces fully removed from this WP.** Migration 004 deleted. `CommunityController::contribute` + `feed` removed. `POST /api/v1/community/contribute` + `GET /api/v1/community/feed` removed. Community visual surfaces (`ContribStrip` macro, `community.php` page) remain but link to WhatsApp/email via `modules.php::contact` (presentation-only, zero backend writes). All community DB functionality deferred to S004 per `documentation/03-data-and-schema/sfa-mysql-mirror.md §9`. See §7 deferral. |
| **LV-S-2** URL contract change `/crop-book/*` → `/book/*` violates frozen public URL contract | BLOCKER | **`/crop-book/*` restored as canonical URLs.** team_35 design used `/book/*` per their nested-WP assumption, but on our subdomain the binding contract per `DECISION_SFA-S003-P003` + `documentation/02-architecture/sfa-delivery-tier.md §5` is `/crop-book/*`. The 14 templates port team_35's design intent under the canonical URL prefix. No 301 needed (no existing `/book/*` to redirect). |
| **LV-S-3** ACs don't cover every page + endpoint | MAJOR | §5 restructured into route-by-route matrix: each of 14 HTML routes + 7 API routes has at least one functional AC, plus non-functional ACs. |
| **LV-S-4** Risk/test environment specifics under-declared | MAJOR | §9 declares phpunit dialect (sqlite::memory: per existing WP-2 pattern with dialect-aware controllers), visual-diff ownership (Claude_in_Chrome @ BUILD-time B.8a, ±4px threshold). §8 R-04 refocused now that NAT-rate-limit risk is moot (no contribute endpoint); R-11 added for PHP/uPress compat (PHP 8.1+ verified via `/api/v1/health` + ext list). |
| **LV-S-5** B.8 budget not credible (28 screenshots + Lighthouse + report in 1h) | MINOR | B.8 split into B.8a (browser evidence, 1.5h) + B.8b (Lighthouse + commit + BUILD_REPORT, 1h). Total 14.5h → 13h (community drop offsets the +1.5h split). |

Total scope shrinks by ~1.5h via community removal, then grows by ~0.5h via B.8 split. Net: ~13h.

---

## §0.5 — team_00 in-session approval (Q1=A) — 2026-05-27 20:00 IDT (17:00 UTC)

**Status:** APPROVED IN-SESSION
**Authority:** team_00 (Principal — direct in-session response)
**Recorded by:** team_100 (this RE-BUILD orchestrator session)
**Trigger:** Decision Brief filed 2026-05-27 by team_100 — 3 opening questions before P.1 execution.

### Decision

When `MANDATE_WP-UI-RE-BUILD_v1.0.0.md §3` BEM class names diverge from `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` (e.g., mandate uses `module-card` but COMPONENTS.md declares `.mod-card`; mandate uses `crop-detail__h1` but COMPONENTS.md uses `cb-crop-hero__title`), **`COMPONENTS.md` is the binding SSoT for the actual class names emitted in HTML.** Mandate §3 is treated as colloquial shorthand documenting *intent* — not as a literal grep target.

### Provenance

- **Q raised:** team_100 Decision Brief 2026-05-27 (after sub-agent research surfaced the drift, ~16:30 IDT)
- **A given:** team_00 in-session response 2026-05-27 ~19:55 IDT: "1. a + להוסיף הערה באפיון שהנושא אושר עי צוות 00 עם הזמן של עכשיו למניעת פסילה מיותרת"
- **Recorded here per team_00 directive** to forestall mistaken rejection at L-GATE_V.

### Effect on §5 ACs (Visual fidelity)

The visual-fidelity acceptance criteria (§5.2 in the mandate, mirrored under LOD400 §5) MUST be evaluated against the **COMPONENTS.md class set**, not the mandate §3 stub names. team_190 cross-engine validator should:

1. Read this §0.5 block first.
2. Reference the canonical `BEM_MAPPING_TABLE` that BUILD_REPORT v2.0.0 §3 will include — listing every mandate §3 name → its canonical COMPONENTS.md equivalent (e.g., `module-card → mod-card`, `crop-detail__head → cb-crop-hero`).
3. Run `grep -c` checks against COMPONENTS.md names (which the rebuild emits), not mandate stub names.

### Effect on rebuild execution

- team_100 (this session, orchestrator) instructs all family-build sub-agents to emit **COMPONENTS.md class names verbatim**.
- No dual-class duplication required.
- `BEM_MAPPING_TABLE` to live in BUILD_REPORT v2.0.0 §3 — single source of cross-reference.

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
- Asset URL prefix `/sfa/` (WP-relative) → **root-relative** (subdomain-relative): `/`, `/crop-book/`, `/market/`, `/calc/`, `/community/`, `/api/v1/*` (per binding §4 + LV-S-2 R2 — `/crop-book/*` is the canonical URL contract)

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
| Vanilla JS for `<details>` accordion state persistence via `sessionStorage` (NO contribute-form submit — community writes deferred per LV-S-1 R2) | `sfa_delivery/public_assets/js/sfa.js` (new, ~40 lines) |
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
    ├── community.php                     ← H4 / D9 — STATIC ONLY (no form). Renders "join us" copy + WhatsApp link from modules.php::contact. Per LV-S-1 R2.
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
- `SearchController.php` — `globalSearch()` GET `/api/v1/search?q=…`
- `ModulesController.php` — `list()` GET `/api/v1/modules` (mirrors `modules.php` data)

**REMOVED (per LV-S-1 R2 amendment):** `CommunityController.php` is NOT created. The `/community/` page is served by `HubController::community()` as a static info page (WhatsApp link + "join us" copy from `modules.php::contact`). No POST endpoints. No DB.

### §3.5 Lib additions

`sfa_delivery/app/Lib/Modules.php` (NEW) — loads `modules.php` static array, exposes `Modules::all()`, `Modules::byTier($tier)`, `Modules::byId($id)`. Mirror of `MODULES_REGISTRY.yaml` (translated once at BUILD time; team_35 YAML is the SSoT — `modules.php` is generated, with header comment "DO NOT EDIT — regenerate from MODULES_REGISTRY.yaml").

### §3.6 Migrations

**No new migrations in this WP.** R1 had proposed `004_community.sql` for a `community_contributions` table; **REMOVED per LV-S-1**. The MySQL schema remains the 4 data + 2 plumbing tables per `documentation/03-data-and-schema/sfa-mysql-mirror.md §2` (frozen).

Any future community-write storage is deferred to **S004** and will require: (a) a new team_00 DECISION authorizing public writes on the delivery tier, (b) an update to `documentation/02-architecture/sfa-delivery-tier.md` §6 + `documentation/03-data-and-schema/sfa-mysql-mirror.md` §9, (c) a new numbered migration in that future WP.

---

## §4 Routes (binding) — `sfa_delivery/app/routes.php` final state

**URL contract honored:** `/crop-book/*` remains canonical per parent `DECISION_SFA-S003-P003` §4-Architecture + `documentation/02-architecture/sfa-delivery-tier.md §5` (frozen public URL contract). team_35 design's `/book/*` references are decorative intent only — our implementation uses the canonical prefix throughout templates, controllers, and modules registry generation.

```php
// HTML
$app->get('/',                       [HubController::class, 'home']);
$app->get('/about[/]',               [HubController::class, 'tiers']);
$app->get('/search[/]',              [HubController::class, 'search']);
$app->get('/calc[/]',                [HubController::class, 'calc']);

$app->get('/crop-book[/]',           [CropBookViewController::class, 'entry']);
$app->get('/crop-book/questions[/]', [CropBookViewController::class, 'questions']);
$app->get('/crop-book/family[/]',    [CropBookViewController::class, 'family']);
$app->get('/crop-book/table[/]',     [CropBookViewController::class, 'tableView']);
$app->get('/crop-book/search[/]',    [CropBookViewController::class, 'search']);
$app->get('/crop-book/{slug}[/]',    [CropBookViewController::class, 'detail']);
$app->get('/crop-book/{slug}/variety/{vslug}[/]', [CropBookViewController::class, 'variety']);

$app->get('/market[/]',              [MarketViewController::class, 'index']);
$app->get('/market/{slug}[/]',       [MarketViewController::class, 'detail']);

$app->get('/community[/]',           [HubController::class, 'community']);  // static info page only — no DB writes; links to WhatsApp/email via modules.php::contact

// API (read-only public, plus HMAC ingest unchanged)
$app->group('/api/v1', function (RouteCollectorProxy $g) {
    $g->get('/health',                       [HealthController::class, 'health']);
    $g->get('/modules',                      [ModulesController::class, 'list']);
    $g->get('/search',                       [SearchController::class, 'globalSearch']);
    $g->get('/crops',                        [CropsController::class, 'list']);
    $g->get('/crops/{slug}',                 [CropsController::class, 'detail']);
    $g->get('/products',                     [ProductsController::class, 'list']);
    $g->get('/products/{slug}',              [ProductsController::class, 'detail']);
    $g->get('/market/{slug}/history',        [MarketViewController::class, 'productHistoryApi']);
    $g->post('/ingest',                      [IngestController::class, 'receive'])
        ->add(HmacAuthMiddleware::class);
});

// Admin
$app->get('/admin/migrate',          [HealthController::class, 'migrate']);
```

**REMOVED from R1 (per LV-S-1 BLOCKER):**
- `CommunityController` class (no longer needed; community page is static via `HubController::community`)
- `POST /api/v1/community/contribute` endpoint (no public write surface in S003 per binding architecture)
- `GET /api/v1/community/feed` endpoint (no community DB to feed from in S003)

All community contribution functionality (write paths, feed, admin review) is deferred to **S004** per `documentation/03-data-and-schema/sfa-mysql-mirror.md §9`. The visual `ContribStrip` macro renders a WhatsApp link from `modules.php::contact` (presentation-only).

**No URL redirects needed** — `/crop-book/*` was already the live URL; we are not changing it.

---

## §5 Acceptance Criteria (route-by-route matrix per LV-S-3 R2)

### §5.1 Foundation ACs (asset chain + shells)

| # | AC | How to verify |
|---|----|----|
| AC-01 | All 7 CSS files copied verbatim from team_35 handoff to `sfa_delivery/public_assets/css/`, total ~75 KB | `diff` to ensure byte-equivalence with handoff files (allowing `tokens.css` curation) |
| AC-02 | `_layout.php` includes the CSS chain in correct cascade: `tokens.css` → `gj.css` → `hub.css` → `community.css` → `crop-book-deep.css` → `desktop.css` → `desktop-extras.css` | `curl -sS https://sfa.nimrod.bio/ \| grep -c '<link.*stylesheet'` returns 7 |
| AC-03 | Google Fonts preconnect + Assistant + Frank Ruhl Libre + JetBrains Mono load in `<head>` | DOM inspect; verify 2 `<link rel=preconnect>` + 1 `<link href=fonts.googleapis.com/css2...>` |
| AC-04 | `dir="rtl" lang="he"` on `<html>` on every served page | curl + grep across all 14 routes |
| AC-05 | Mobile shell `.gj-shell` renders on `< 900px` viewports | Claude_in_Chrome resize to 390x844, screenshot of `/`, verify `.gj-shell` present, `.dt-shell` absent |
| AC-06 | Desktop shell `.dt-shell` renders on `≥ 900px` with sidebar accordion using `<details>` | Claude_in_Chrome resize to 1280x900, screenshot of `/`, verify `.dt-shell .dt-side details` count ≥ 4 |

### §5.2 Per-route ACs (1 functional check per route, +1 visual)

| # | Route | Functional AC | Visual AC |
|---|-------|---------------|-----------|
| AC-07 | `GET /` (hub home, H1/D1) | curl returns 200; DOM has `.module-card` count = 8 grouped under 3 tier sections (open/paid/custom); each card shows `tier_badge` with token color | Claude_in_Chrome screenshot mobile + desktop vs artboards H1+D1 |
| AC-08 | `GET /about` (tiers explainer, H2/D2) | curl returns 200; DOM contains 5 tier labels in Hebrew (כלים לקהילה / בטא · ניסיוני / בקרוב / כלים מתקדמים / בדיוק לחווה שלך) | screenshot mobile + desktop vs H2+D2 |
| AC-09 | `GET /search?q=עגבני` (search results, D8) | curl returns 200; DOM lists results from `crops` + `products`; "0 results" state if `?q=` empty | screenshot vs D8 |
| AC-10 | `GET /calc` (calc stub, H3/D7) | curl returns 200; DOM shows "בטא · בפיתוח" badge + 1-paragraph explainer + WhatsApp link from `modules.php::contact` | screenshot vs H3+D7 |
| AC-11 | `GET /crop-book/` (entry, CB0) | curl returns 200; DOM presents 4 entry-path cards (questions/family/table/search) each with `<a href="/crop-book/{entry}">` | screenshot vs CB0 |
| AC-12 | `GET /crop-book/questions` (CB1) | curl returns 200; DOM has at least 5 question cards (static categorization for v1) each linking to a filter of `/crop-book/table?cat=…` | screenshot vs CB1 |
| AC-13 | `GET /crop-book/family` (CB2) | curl returns 200; DOM renders family-tree taxonomy from `crops.family_name_he` GROUP BY (no new schema) | screenshot vs CB2 |
| AC-14 | `GET /crop-book/table` (CB3/D3) | curl returns 200; table shows all 52 crops; supports `?category=` filter (verify with `?category=vegetables` returns 34) | screenshot vs CB3+D3 |
| AC-15 | `GET /crop-book/search?q=עגב` (CB4) | curl returns 200; DOM lists matches from `crops.hebrew_name LIKE '%עגב%'` | screenshot vs CB4 |
| AC-16 | `GET /crop-book/{slug}` (CB5/D4) e.g. `/crop-book/anise-hyssop` | curl returns 200; DOM shows crop top + varieties section (per CB5) merging top-level cols + `payload_json` | screenshot vs CB5+D4 |
| AC-17 | `GET /crop-book/{slug}/variety/{vslug}` extends CB5 | curl returns 200 for any (crop, variety) pair from DB; 404 with Hebrew page for nonexistent | screenshot vs CB5 (variety expansion) |
| AC-18 | `GET /market/` (MK1/D5) | curl returns 200; first DOM block is `.market-disclaimer` with 4 sub-items (what/from/why/NOT); table lists 65 products | screenshot vs MK1+D5 |
| AC-19 | `GET /market/{slug}` (MK2/D6) e.g. `/market/onion-dry` | curl returns 200; DOM shows price + 28-day history table from `product_prices` (or "—" if empty) | screenshot vs MK2+D6 |
| AC-20 | `GET /community` (H4/D9) | curl returns 200; DOM is static info page with WhatsApp link `<a href="https://wa.me/{contact.whatsapp}">`; **NO form, NO POST surface** (per LV-S-1 R2) | screenshot vs H4+D9 |

### §5.3 API ACs (read-only, public)

| # | API endpoint | Functional check |
|---|--------------|------------------|
| AC-21 | `GET /api/v1/health` (regression) | returns `{status:"ok", php_version, db:"ok"}` JSON; HTTP 200 |
| AC-22 | `GET /api/v1/modules` | returns JSON mirror of `MODULES_REGISTRY.yaml` (8 modules + 3 tiers + 4 pages + contact); `jq '.modules \| length' == 8` |
| AC-23 | `GET /api/v1/search?q=עגב` | returns `{crops: [...], products: [...]}`; both arrays present even if empty; `jq` valid |
| AC-24 | `GET /api/v1/crops` (regression) | returns 52 crops; unchanged from WP-2 |
| AC-25 | `GET /api/v1/crops/{slug}` (regression) | returns single crop with merged `payload_json`; unchanged |
| AC-26 | `GET /api/v1/products` (regression) | returns 65 products; unchanged |
| AC-27 | `GET /api/v1/products/{slug}` (regression) | returns single product; unchanged |
| AC-28 | `GET /api/v1/market/{slug}/history?days=28` | returns `[{price_date, price, source}, ...]` JSON; empty array if no aggregates |
| AC-29 | `POST /api/v1/ingest` with valid HMAC (regression) | returns 200 + `{accepted, rejected}`; HMAC middleware unchanged |
| AC-30 | `POST /api/v1/ingest` with bad HMAC (regression) | returns 401 |

### §5.4 Non-functional ACs

| # | AC | How to verify |
|---|----|----|
| AC-31 | `LCP < 2.5s` mobile-throttled (Chrome devtools simulated 4G) for hub home + crop-book/table + market list | Lighthouse JSON report, capture `audits["largest-contentful-paint"].numericValue` for 3 routes |
| AC-32 | Zero JS console errors across all 14 HTML routes | Claude_in_Chrome `read_console_messages onlyErrors:true` per route, all return empty |
| AC-33 | WCAG AA contrast for `--gj-ink/--gj-paper`, `--gj-ink-soft/--gj-paper`, `--gj-leaf-deep/--gj-paper`, `--status-stale/--gj-paper`, `--gj-paper/--gj-soil-deep` | axe-core script or manual contrast-ratio check; record ratios |
| AC-34 | `sfa.js` vanilla: `<details>` open-state persists across page reload via `sessionStorage` | Manual: open accordion, F5, accordion still open |
| AC-35 | Hebrew rendering: visible-text inspection on all 14 routes shows no mojibake, no LTR-leakage in number sequences (e.g. dates render `2026-05-23`, prices `15.25 ₪`) | Manual browser pass |

### §5.5 Regression / live-system ACs

| # | AC | How to verify |
|---|----|----|
| AC-36 | Existing `https://sfa.nimrod.bio/api/v1/health` continues to return ok post-deploy | curl smoke from Mac |
| AC-37 | Daily cron from waldhomeserver (`30 6 * * *` runs `sfa_ingest_push.py`) continues successfully | tail `/data/backups/sfa-ingest-push.log` 24h post-deploy; expect ≥1 successful push log line |
| AC-38 | Old WP page deletion + s887 separation (per WP-S003-P003-WP-5) remains intact: `https://www.nimrod.bio/smallfarmsagent/` still returns 404 | curl |

**Total: 38 ACs** (up from 22 in R1) — fully covers all 14 HTML routes + 8 API endpoints + 5 non-functional + 3 regression. Each AC is independently testable.

---

## §6 GCR analysis (R2 — no locked-file changes; no canonical doc drift)

**No locked-file changes anywhere.**
- waldhomeserver Python: untouched. Publisher (`sfa_ingest_push.py`) unchanged.
- uPress MySQL schema: untouched. R1 had proposed adding `community_contributions`; **removed per LV-S-1 R2**. Schema remains 4 data + 2 plumbing tables, fully consistent with `documentation/03-data-and-schema/sfa-mysql-mirror.md §2`.
- URL contract: untouched. R1 had proposed `/book/*`; **reverted to canonical `/crop-book/*` per LV-S-2 R2**. Fully consistent with `documentation/02-architecture/sfa-delivery-tier.md §5` frozen URL contract.

**Q5 from team_35 LOD300** (variety `taste_rating` field) → not in WP-UI scope. No data field added; CB5 detail page renders only fields already in `crop_varieties.payload_json` from `sfa_ingest_push.py`.

**No GCR needed. No canonical doc updates needed.** This LOD400 R2 is fully additive within existing binding contracts.

---

## §7 Out of scope (deferred)

| Item | Reason | Where |
|------|--------|-------|
| **Public community write surfaces (contribute form, contributions DB, feed)** | **per LV-S-1 R2** — S003 delivery tier is read-only per binding architecture; community writes require a new team_00 DECISION + canonical doc updates first | **S004** (per `documentation/03-data-and-schema/sfa-mysql-mirror.md §9`) |
| Email notification on contribution arrival | moot for S003 (no contributions to notify on) | S004 — bundle with community DB |
| Admin review UI for community contributions | moot for S003 | S004 |
| Calculator (β) full implementation | per team_35 §6 Q7 — separate WP | new WP-B3 in S003-P002 or S004 |
| AI-rendered thumbnails (`art-prompts.jsx`) | per team_35 §6 Q8 — pre-render external tool, separate ops task | future |
| Server-side device detection | per team_35 §3.5 — CSS media query at 900px is the swap | – |
| `taste_rating` variety field | per §6 — schema not modified | – |
| Retire WP shortcodes on legacy site | already DONE in WP-S003-P003-WP-5 (full deletion 2026-05-24) | – |
| Search engine (global) — full FTS | v1 uses LIKE queries on `crops.hebrew_name + products.hebrew_name`; FTS = later | future |
| `/api/v1/market/<slug>/history` chart frontend rendering | endpoint serves data; chart drawing = vanilla JS in B.7 if achievable; if too complex, ship table-only | inline B.7 |
| New `/book/*` URL aliases | per LV-S-2 R2 — canonical URLs remain `/crop-book/*`; team_35's `/book/*` design intent is decorative | if needed: future DECISION |

---

## §8 Risks + mitigations (R2)

| # | Risk | Mitigation |
|---|------|------------|
| R-01 | CSS cascade order issue (a later file overrides tokens unexpectedly) | Strict order in `_layout.php`; visual diff against `design/index.html` for each page |
| R-02 | RTL bug in `<details>`/`<summary>` accordion (Safari quirks) | Test in Chrome + Safari mobile; CSS-only chevron flip via `[dir=rtl]` selector |
| R-03 | Mobile font-load FOUT (Frank Ruhl Libre is heavy) | `font-display: swap` in Google Fonts URL params (already in `index.html` of design canvas) |
| R-04 | ~~`community_contributions` spam~~ — **moot in R2** (no contribute endpoint) | N/A — community write surface deferred to S004 |
| R-05 | Static `modules.php` drift from `MODULES_REGISTRY.yaml` | At BUILD: generator script `bin/regenerate_modules.php` reads YAML and writes PHP array; idempotent; rerun after every YAML edit. Documented in `sfa_delivery/README.md`. CI-eventually could diff on commit. |
| R-06 | Translation Jinja2 macros → PHP partials loses semantics (e.g. macro args become global `extract()`) | Each partial is small (<100 lines); test pages render the macro correctly by visual diff per AC-07..AC-20 |
| R-07 | ~~CF cache stale 301~~ — **moot in R2** (no 301 since URL contract unchanged) | N/A |
| R-08 | Calculator stub (`/calc/`) confuses users seeing "בטא · בקרוב" badge | Calc page shows "בטא · בפיתוח" badge + 1-paragraph explainer + WhatsApp CTA from `modules.php::contact` |
| R-09 | uPress nginx still doesn't fully process `.htaccess` (F-1 carry-over from WP-2) | `composer.json` + SQL files remain readable but harmless (no secrets); same as today — no regression introduced |
| R-10 | 7 CSS files + 1 JS file load = waterfall hurts LCP | Inline tokens.css critical path in `<head>`; HTTP/2 multiplex on Cloudflare; verify Lighthouse mobile Performance ≥ 75 via AC-31 |
| **R-11** | **PHP/uPress version compat** (per LV-S-4 R2): assumes PHP 8.1+ with `pdo_mysql`, `openssl`, `json` extensions. Already verified at WP-2 deploy (PHP 8.5.5). | At B.1 deploy, re-call `/api/v1/health` (returns `php_version`); fail BUILD if `<8.1`. Composer constraint `"php": ">=8.1"` already enforces locally. Extension check via `php -m` on remote not available (no shell); rely on existing `IngestController` working (proves pdo_mysql + json present). |
| R-12 | Cloudflare cache invalidation after deploy (users see old CSS) | Append `?v={git_short_sha}` to CSS link in `_layout.php` (cache-bust per release); CF respects query-string variation by default |

---

## §9 Test plan (R2 — environment specifics declared per LV-S-4)

### §9.1 phpunit (unit + integration)

- **Backend:** `sqlite::memory:` per existing WP-2 pattern (`phpunit.xml` already has `<env name="DB_DSN" value="sqlite::memory:"/>`). Controllers use dialect detection (`PDO::ATTR_DRIVER_NAME`) for any MySQL-specific SQL (already proven in `IngestController::upsert` from WP-2). Tests do NOT hit live MySQL on uPress.
- **Test files added:**
  - `tests/SearchTest.php` — 3 cases: empty `q`, crops-only match, products-only match
  - `tests/ModulesTest.php` — 2 cases: list count = 8, `byTier(open)` returns 3
  - `tests/MarketHistoryTest.php` — 2 cases: empty product, populated product
  - `tests/RouteSmokeTest.php` — 14 cases: each HTML route returns 200 on a seeded in-memory DB
- **REMOVED from R1:** `tests/CommunityContributeTest.php` — community writes deferred to S004 per LV-S-1 R2.
- **Total new tests:** ~21 (down from R1's ~9 + community = 13; up due to RouteSmokeTest covering AC-07..AC-20 mechanically)
- **Runner:** `composer test` from `sfa_delivery/` (already wired in WP-2).

### §9.2 Visual diff

- **Owner:** sfa_build at BUILD phase **B.8a** (Claude_in_Chrome MCP).
- **Method:** navigate to each of the 14 HTML routes at 2 viewports (390×844 mobile, 1280×900 desktop), screenshot to disk, compare against the matching artboard in `_handoff/design/index.html` (CB0..CB5, MK1, MK2, H1..H4, D1..D9, D3, D5, D6, D7, D8, D9).
- **Threshold:** ±4 px on critical-element positioning (titles, cards, buttons). Off-by-margin > 4 px = AC fail for that specific route's visual AC.
- **Artifacts:** all 28 screenshots saved to `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/visual_diff/` and referenced in BUILD_REPORT.
- **L-GATE_V re-verification by team_190:** team_190 reviews the BUILD_REPORT's visual artifacts independently and may re-run a sample via Claude_in_Chrome if available, or accept the artifacts if cross-engine policy precludes browser access.

### §9.3 Lighthouse

- **Owner:** sfa_build at B.8b. **Runner:** `npx lighthouse https://sfa.nimrod.bio/{route} --output=json --form-factor=mobile --throttling-method=simulate` for 3 representative routes: `/`, `/crop-book/table`, `/market/`.
- **Thresholds per AC-31:** Performance ≥ 75, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 90. JSON reports saved to `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/lighthouse/`.

### §9.4 Live smoke (regression)

- AC-21 + AC-29 + AC-30 (HMAC ingest), AC-36 (health), AC-37 (waldhomeserver cron 24h observation), AC-38 (legacy site separation) all run from Mac via curl. Output captured in BUILD_REPORT.

### §9.5 Test ownership matrix

| Test category | Who runs it | When | Where artifact lives |
|---------------|-------------|------|---------------------|
| phpunit (~21 new + 11 existing = ~32) | sfa_build | Local dev pre-deploy (B.0..B.7) + post-deploy (B.8b) | BUILD_REPORT inline |
| Visual diff (28 screenshots) | sfa_build via Claude_in_Chrome | B.8a | `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/visual_diff/` |
| Lighthouse (3 routes × 1 form-factor) | sfa_build via npx | B.8b | `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/lighthouse/` |
| Live smoke (8 curls) | sfa_build | B.8b | BUILD_REPORT inline |
| L-GATE_V cross-check | team_190 (external, non-Claude) | post-BUILD | `_COMMUNICATION/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` |

---

## §10 Definition of Done (L-GATE_V criteria — R2)

1. All **38 ACs** pass (§5.1..§5.5)
2. `composer test` exit 0 (existing 11 + new ~21 = ~32 phpunit tests pass)
3. Visual diff vs design canvas: each of the 14 page templates shows the expected artboard layout (≤ 4 px off-by-margin per AC-07..AC-20)
4. Lighthouse mobile: Performance ≥ 75, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 90 (per AC-31)
5. Zero console errors on any of the 14 routes (per AC-32)
6. URL contract unchanged: `/crop-book/*` paths return 200; no broken bookmarks (per AC-11..AC-17)
7. Daily cron from waldhomeserver still posts cleanly (24h observation in `/data/backups/sfa-ingest-push.log`, per AC-37)
8. team_190 external L-GATE_V verdict PASS or PASS_WITH_FINDINGS (no BLOCKERs)
9. `validate_aos.sh` 0 FAIL on spoke
10. Roadmap entry → COMPLETE/LOD500_LOCKED + BUILD_REPORT filed at `_COMMUNICATION/team_00/WP-UI_BUILD_REPORT_v1.0.0.md`

---

## §11 Build plan (R2 — 9 phases, replaces team_35 IMPLEMENTATION_PLAN)

| Phase | Hours | Scope | Output |
|-------|-------|-------|--------|
| B.0 | 0.5 | Branch: `claude/sfa-ui-build` off `gallant-elbakyan-727a60`. Add `bin/regenerate_modules.php` (YAML→PHP generator). Verify `_handoff/` files accessible. **No migration file (per LV-S-1 R2).** | Branch + 1 PHP generator |
| B.1 | 2 | Copy 7 CSS files + extract icons.svg from illustrations.jsx. Build `tokens.css` from `system.css`. Update `_layout.php` to include CSS chain in correct cascade + cache-bust query string (R-12). Deploy via FTPS. Visual verify baseline. Probe `/api/v1/health` → confirm PHP ≥ 8.1 (R-11). | 7 CSS + 1 SVG + new `_layout.php` |
| B.2 | 3 | Build mobile + desktop shell partials (`shell/mobile.php`, `shell/desktop.php`, `shell/_mark_svg.php`). Build all 10 macros (`macros/*.php`) including refactored `contrib_strip.php` (WhatsApp link, no form). | 13 PHP files |
| B.3 | 2 | Hub: `hub_home.php`, `hub_tiers.php`, `hub_calc.php` (stub), `community.php` (STATIC info page, no form per LV-S-1 R2). Add `HubController.php` (rename of HomeController) with methods: `home`, `tiers`, `calc`, `search`, `community`. Wire 5 routes. | 4 templates + 1 controller |
| B.4 | 3 | Crop book entry/questions/family/table/search (5 templates). Extend `CropBookViewController.php` with `entry()`, `questions()`, `family()`, `tableView()`, `search()`. Note: `questions`+`family` use static categorization in PHP arrays (no new schema). All routes mounted at `/crop-book/*` per LV-S-2 R2. | 5 templates + controller methods |
| B.5 | 1 | Crop detail (CB5) + variety detail. Refresh `book_crop.php` + new `book_variety.php`. Wire `/crop-book/{slug}` + `/crop-book/{slug}/variety/{vslug}`. | 2 templates |
| B.6 | 1 | Market list + product with mandatory disclaimer macro. Refresh `market_list.php` + `market_product.php`. Add `MarketViewController::productHistoryApi()`. | 2 templates + 1 controller method |
| B.7 | 1 | `SearchController.php` (GET `/api/v1/search`) + `ModulesController.php` (GET `/api/v1/modules`) + `sfa.js` (vanilla — `<details>` sessionStorage persist, no form-submit logic since no contribute form). **No community POST/feed routes** (per LV-S-1 R2). | 2 controllers + JS |
| **B.8a** (split per LV-S-5) | **1.5** | Browser pass via Claude_in_Chrome: 14 routes × 2 viewports = 28 screenshots; sample console-error check per AC-32; diff against `_handoff/design/index.html` artboards with ±4 px tolerance. Save to `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/visual_diff/`. | 28 screenshots + diff notes |
| **B.8b** (split per LV-S-5) | **1** | Lighthouse on 3 routes (mobile profile) → JSON reports → `_COMMUNICATION/team_10/SFA-S003-P002-WP-UI/lighthouse/`. Run live-smoke curls (AC-21, AC-29, AC-30, AC-36, AC-38). Write BUILD_REPORT_v1.0.0.md. Commit + push. Hand off to team_190 for L-GATE_V. | Lighthouse + smoke logs + BUILD_REPORT |
| **Total** | **13** | (R1 was 14.5; community drop = −1.5h, B.8 split = +0.5h; net −1.5h. Actually net = −1.5h, so total = 13h.) | |

### Phase dependencies (DAG)

```
B.0 → B.1 → B.2 ─┬→ B.3 ─┐
                 ├→ B.4 ─┤
                 ├→ B.5 ─┤
                 ├→ B.6 ─┼→ B.7 → B.8a → B.8b → L-GATE_V dispatch
```

Macros (B.2) gate all page templates (B.3..B.6); B.7 endpoints have no template dependency. B.8a/b run after all builds complete.

---

## §12 L-GATE_S — STATUS (after R2)

**team_190 R2 verdict: PASS_WITH_FINDINGS — DISPATCH_BUILD.**
- Verdict file: `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md`
- Engine: GPT-5.5 / Cursor (non-Claude per IR#1)
- Date: 2026-05-27
- Both R1 BLOCKERs (LV-S-1 community writes, LV-S-2 URL contract) resolved
- 2 MINOR findings carried forward (LV-S-6 stale `/book/` text in §2 + `sfa.js` contribute mention in §3.2; LV-S-7 stale §12 wording) — addressed inline in this v1.0.2 cleanup commit
- `validate_aos.sh`: 29 PASS / 17 SKIP / 0 FAIL

**Validated against (canonical):**
1. Architectural consistency with `DECISION_SFA-S003-P003` — PASS_WITH_FINDINGS (stale text only)
2. AC completeness — PASS (38 ACs cover all 14 routes + 10 API + 5 non-functional + 3 regression)
3. Risk register adequacy — PASS (R-04/R-07 marked moot; R-11/R-12 added)
4. GCR analysis correctness — PASS (no canonical doc drift; fully additive within binding contracts)
5. Test plan adequacy — PASS (sqlite::memory + visual-diff threshold + Lighthouse ownership matrix in §9.5)
6. Out-of-scope discipline — PASS (community writes explicitly deferred to S004)
7. Phase plan realism — PASS (B.8 split into B.8a + B.8b; 9 phases; 13h total)

**Disposition:** L-GATE_S CLOSED. WP-UI status → BUILDING. team_100 dispatches canonical L-GATE_B mandate to sfa_build (team_10, Claude Sonnet).

---

*LOD400 v1.0.0 authored 2026-05-24 by team_100. team_190 R1 verdict FAIL 2026-05-27 (5 findings: 2 BLOCKER + 2 MAJOR + 1 MINOR).*
*LOD400 v1.0.1 amended 2026-05-27 by team_100 — full Round 2 change summary in §0.*
*LOD400 v1.0.2 cleanup 2026-05-27 by team_100 — addresses team_190 R2 verdict findings LV-S-6 (stale /book/ + contribute-form text in §2/§3.2) + LV-S-7 (stale §12 wording). team_190 R2 PASS_WITH_FINDINGS, DISPATCH_BUILD. LOD400_LOCKED.*
