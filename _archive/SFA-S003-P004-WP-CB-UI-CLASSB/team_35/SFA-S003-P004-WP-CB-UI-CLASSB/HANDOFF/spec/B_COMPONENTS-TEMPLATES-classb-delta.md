# COMPONENTS + TEMPLATES — delta for Class B surfaces

> **WP:** SFA-S003-P004-WP-CB-UI-CLASSB · **From:** team_35 → team_100 → LOD400
> **Extends:** WP-CB-1 `COMPONENTS-delta.md` (§18–29) + `TEMPLATES-delta.md`.
> **Binding rule:** ONE system. Build on `tokens.css` (`--gj-*` white-green) + `cropbook-v1.css`.
> **No new palette. No cream.** New styles live in `classb.css`; new JS in `classb.js`.
> Board: `LOD300 Crop Book UI ClassB v1.html` — every frame is the `.sh` shell + real UI, carries `data-screen-label`.

---

## §3.1 App-shell — **shell as specced, with two refinements**

The `.sh` / `.sh__nav` / `.sh__nav--mobile` / `#sfa-logo` contract from §24 is confirmed. Two additions (in `classb.css`):

- **`.sh__search`** — an inline search field in the bar on desktop (≥760px). Collapses to the existing `.sh__icon ⌕` below 760px and on mobile. This is the entry to the Search surface (§3.4).
- **Account button** keeps avatar + label (`.sh__acct`), and becomes the **4th mobile tab** (`◔ חשבון`) in `.sh__nav--mobile`.
- **Footer** (`.sh__foot`) is a single quiet line: brand + "קוד פתוח · קהילתי"; about/community/privacy links hang here.
- **Logo + wordmark are the home affordance** (→ `/`). The hub is NOT a primary nav item — only book/calc/market are colour-coded (`leaf`/`sun`/`tomato` via `.is-active{.is-calc,.is-market}`).

---

## New components (all extend the kit; classes namespaced per surface)

| # | Component | Class(es) | Notes |
|---|-----------|-----------|-------|
| 30 | **Page-title band** | `.pagehead` `.pagehead__sub` `.pagehead__aside` | Quiet header strip used by market/community/etc. `.sh__body--wide` widens the body for grids. |
| 31 | **Module tile** | `.modtile` (+ `--leaf/sun/tomato/soil`) `.modtile__art/tier/glyph/body/title/desc/foot/stat/go` | Hub card. 16:9 hero (warm wash on `#f4ecdc` art panel), `.tier--*` badge top-start, glyph top-end. `.is-soon` = coming-soon (greyed, diagonal hatch, no hover-lift, "בקרוב" instead of stat). |
| 32 | **Hub group bar + explainer + audience row** | `.hub-groupbar` `.hub-intro` `.hub-grid` `.hub-manifest` `.hub-aud` `.audcard` | Reading order: open tools → `.hub-manifest` explainer band (project status: open knowledge, field experience + advanced-AI research) → `.hub-aud` audience entry cards (gardener leaf · farmer soil · planner teal, each routing into the right view) → advanced tools. `.modtile--row` = compact mobile tile (≈⅓ height, side thumbnail). |
| 33 | **Market disclaimer** | `.mkt-disc` `.mkt-disc__ic/head/list` | **Mandatory, never suppressed.** 4 bullets (מה · מאיפה · למה · למה לא), amber left-spine. Compact 1-col variant on detail page. |
| 34 | **Freshness pill** | `.fresh` (+ `--fresh/aging/stale`) | Maps to status tokens leaf/sun/tomato. On every price card + detail hero. |
| 35 | **Price card + table view** | `.pcard` (+ `.is-stale/.is-empty`) · `.mkt-aud-head` + `.aud` toggle + `.ptable .t-price` | Product · current price (tomato) · range · #sources + freshness. **Empty state is first-class**: "—", flat sparkline, "◐ תרמו מחיר" request. A **cards ⇄ table** density toggle (book's `.aud` switch) wraps both views in `#mkt-scope` `[data-aud-view]`; table reuses `.ptable`. |
| 36 | **Sparkline** | `.spark` `.spark i.hi` `.spark--empty` | Pure-CSS 7-bar mini chart; last bar emphasised. |
| 37 | **Market detail + price graph** | `.pdetail` `.pbig` `.pgraph` `.phist` `.pstat(s)` | **14-day price graph** (`.pgraph` — inline SVG line + area, tomato; data viz, not illustration) · big price hero · price-history table (day-over-day delta) · stat strip · **source breakdown reuses `.prov`** · `.xlink` to the crop in the book · compact disclaimer. |
| 38 | **Empty / stale box** | `.emptybox` | Shared empty state (market history, sparse lists). Same honesty ethos as the book's MISSING cue. |
| 39 | **Search** | `.srch-bar` `.srch-echo` `.srch-group` `.srow` | Unified results grouped by source (book / market) + query echo + per-group count. World-aware rows (book→DTM/family; market→price/freshness). `<mark>` highlights match. `.srch-nomatch` empty state → request CTA. |
| 40 | **Community (reframed)** | `.comm-wrap` `.comm-banner` `.comm-manifest` `.reqcard` `.reqchip` `.comm-collab` | **No activity feed / no community management** (removed per client). Manifesto (open contribution to gardening + farming community, built on field experience + advanced-AI research) + low-friction request/suggest form (chips incl. 🤝 collaboration) + a single WhatsApp collaboration line. Communal tone, no moderation surface. |
| 41 | **Tier explainer** | `.tier-hero` `.tier-list` `.tier-row` (+ `--leaf/sun/paper/soil/tomato`) | 5-tier ladder; reuses `.tier--*` badges. 4px left spine per tier. |
| 42 | **Account: login + profile shell** | `.acct-wrap` `.acct-card` `.acct-empty` · `.acct-profile` `.acct-prof-head` `.setgroup` `.setrow` (+ `--danger`) | Logged-out: login card + "core is open, account optional" empty state. Logged-in: Wolt/Planta-style profile head + grouped settings rows (account · modules · system). Soil accent. Stable hook; full flows later. |

### Reused verbatim (no change)
`.tier--*` · `.pill--*` · `.prov` / `.prov__cls--*` (market source breakdown) · `.reqinfo` (request-info CTA, now also on empty price cards + search no-match) · `.contrib` (contribute strip) · `.xlink` (book↔market cross-link) · `.fchip` (market category filter, single-select) · `.gj-eyebrow` / `.gj-h*`.

---

## Routes (additions — Slim4/PHP, server-rendered + light JS)

| Route | Template | Controller (current) | Notes |
|-------|----------|---------------------|-------|
| `/` | `hub_home` | `HubController::home` | Module grid; cards from `MODULES_REGISTRY` (tier · hero · stat). |
| `/market/` | `market_list` | `MarketViewController::index` | Disclaimer partial (always) + `.fchip` category filter + price-card grid. Empty cards for 0-report products. |
| `/market/{slug}` | `market_product` | `MarketViewController::detail` | Price hero + `phist` history + `prov` sources + `xlink` to `/crop-book/{slug}`. Empty history → `.emptybox`. |
| `/search?q=` | `search_results` | `HubController::search` | Grouped `.srch-group` (book + market); `.srch-nomatch` → `/api/v1/contribute`. |
| `/community` | `community` | `HubController::community` | Contact + feed + `reqcard` (`POST /api/v1/contribute`). |
| `/about` | `hub_tiers` | `HubController::tiers` | 5-tier `.tier-list`. |
| `/account` | `account_landing` | *(new)* `AccountController::index` | Login shell + open-core empty state. Stable hook. |

### Shared partials
```
macros/
├── app_shell.html       .sh + nav + .sh__search + .sh__acct + footer   (Class A — team_100)
├── module_tile.html      {{ module_tile(mod) }}            ← MODULES_REGISTRY row
├── market_disclaimer.html  (the 4 bullets — included on list + detail)
├── price_card.html       {{ price_card(product) }}         ← handles fresh/aging/stale/empty
├── freshness_pill.html   {{ fresh(last_report_days, n_sources) }}
├── prov_table.html        (REUSED from WP-CB-1 — market source breakdown)
└── tier_badge.html        (REUSED — open/beta/coming/paid/custom)
```

## JS (`classb.js`, vanilla, tiny)
- `.reqchip` single-select within `.reqcard__chips`.
- Market category `.fchip` reuses `cropbook-v1.js::wireFilters` (no new code).
- Everything else is server-rendered; no framework.

## §3.8 Reference patterns (Mobbin) — UX pattern in, v2 tokens on top

> Rule (team_00): borrow the **UX pattern** (structure / layout / flow / interaction) from a named app; **never** its skin. Apply `tokens.css` v2 (white-green · Carmela · Assistant / Frank Ruhl Libre · watercolor). **Pattern conflicts → tokens win.** Tagged per surface on the board with a ▤ `.patref` chip.

| Surface | Pattern anchor | What we borrowed (pattern only) |
|---|---|---|
| App-shell | Planta · Notion · Arc | top bar + section nav + mobile bottom-tab; inline search |
| Hub / Home | Notion · Arc · Flighty launchers · Planta home | launcher grid of module cards + tier badge; explainer band; audience entry row |
| Market list | Blinkit / Zepto · Copilot Money | category tabs + product-card grid; cards⇄table density |
| Market detail | Copilot Money · Delta | big number + **time-range selector** (`.rangesel` 7י/30/90/שנה) + line/area graph + history list |
| Search | Planta · NYT Cooking | unified grouped results; related-search chips; recent-searches + empty/no-match |
| Community | Strava / Duolingo (lightness only) | friendly card tone — **feed intentionally omitted per client** (see ⚠ below) |
| About / Tiers | Notion · Linear pricing | tier ladder with per-tier price affordance |
| Account | Wolt · Planta settings | profile head + grouped settings rows (`.setgroup`/`.setrow`); login shell |
| RTL (all) | Wolt · Bit · Riseup | nav, bottom-tab, forms, price/number direction in proper Hebrew RTL |

New REV-2 components: `.rangesel` (graph time range) · `.srch-suggest`/`.schip`/`.srch-recent` (search suggestions) · `.acct-profile`/`.acct-prof-head`/`.setgroup`/`.setrow` (settings shell) · `.tier-row__price` · `.patref`.

**⚠ Open conflict — Community feed.** §3.8 lists a Strava/Duolingo "light feed"; the client explicitly removed the feed in the prior round ("no community management — form + text only"). We kept Community **feed-less**, applying only the friendly *lightness* of those patterns. **team_00 to confirm before any feed is re-added.**

---

## Open questions for team_100
1. **Account tier** — login is shown as the gate to paid/custom modules. Confirm the open core never requires it (current design assumes optional).
2. **Market units** — cards show ₪/kg · ₪/unit · ₪/bunch from `sale_unit`. Confirm the unit source field for products without a book entry.
3. **Freshness thresholds** — fresh ≤3d · aging 4–7d · stale >7d. Confirm with OrganicMarketAgent's rolling-window definition.
