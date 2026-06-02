---
id: SFA-S003-P004-WP-CB-UI-CLASSB-LOD400
wp: SFA-S003-P004-WP-CB-UI-CLASSB — implement the team_35 v2 design across all non-crop-book surfaces
gate: L-GATE_S (pending) — authored 2026-06-02
status: DRAFT v0.9.0 — pending team_00 clarifications (§9) → lock v1.0.0 → team_190 L-GATE_S
author: team_100 (Chief System Architect)
date: 2026-06-02
design_ssot: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/
depends_on: SFA-S003-P004-WP-CB-UI-ALIGN  # app-shell + palette (Class A)
builder: team_10 (Claude Sonnet) → QA team_50 (VISUAL) → L-GATE_V team_190 (non-Claude, IR#1)
---

# LOD400 — WP-CB-UI-CLASSB: Hub · Market · Search · Community · About · Account (v2)

> Implement team_35's Class B design package **exactly** — structure/style/layout per the boards; content/fields
> wired from the existing delivery-tier code. The package is byte-clean (tokens.css + cropbook-v1.* identical to
> v1 — no palette drift). Build on the Class A app-shell (WP-CB-UI-ALIGN). Delivery tier only; no backend/migration.

## 0. Read first
- Design SSoT: `…/HANDOFF/design/Board-B-*.html` (visual truth) + `…/HANDOFF/design/classb.css` (42KB) +
  `classb.js` (1.4KB) + `…/HANDOFF/spec/B_COMPONENTS-TEMPLATES-classb-delta.md` (§30–42 + routes + partials).
- Class A app-shell contract (built by WP-CB-UI-ALIGN): `.sh`/`.sh__nav`/`.sh__search`/`.sh__acct`/`.sh__nav--mobile`/`#sfa-logo`.
- Current delivery code being re-skinned: `sfa_delivery/templates/pages/{hub_home,market_list,market_product,search_results,community,hub_tiers}.php` + controllers.

## 1. Goal
Every non-crop-book surface renders in the v2 white-green system with the team_35 Class B components — visually
faithful to Board-B — while displaying the **real data the controllers already provide**.

## 2. Scope — 7 surfaces (+ shell refinements)
Build each template to the matching Board-B frame; port `classb.css` into `public_assets/css/classb.css` and
`classb.js` into `public_assets/js/classb.js` (load `cropbook-v1.js` first, then `classb.js`).

| # | Route | Template (modify) | Controller | Board frame | New components |
|---|-------|-------------------|------------|-------------|----------------|
| 2.1 | shell refine | `_layout.php` + Class-A shell | — | `shell-desktop/mobile` | `.sh__search` inline (≥760px → `.sh__icon`), account=4th mobile tab, `.sh__foot` |
| 2.2 | `/` | `pages/hub_home.php` | `HubController::home` | `hub-home`, `hub-home-mobile` | `.modtile`(+`--row`/`.is-soon`), `.hub-intro/groupbar/grid/manifest/aud`, `.audcard` |
| 2.3 | `/market/` | `pages/market_list.php` | `MarketViewController::index` | `market-list` | `.mkt-disc`(mandatory), `.mkt-tools`+`.fchips`+`.mkt-legend`, `.pcard`(+`.is-stale/.is-empty`), `.spark`, `.fresh`, cards⇄table via `.aud`+`.ptable` |
| 2.4 | `/market/{slug}` | `pages/market_product.php` | `MarketViewController::detail` | `market-detail` | `.pdetail`, `.pbig`, `.pgraph`+`.rangesel`, `.phist`, `.pstats/.pstat`, `.prov`(reused), `.xlink`, `.emptybox`, compact `.mkt-disc` |
| 2.5 | `/search` | `pages/search_results.php` | `HubController::search` | `search-results`, `search-nomatch` | `.srch-bar/echo/suggest/group/rows`, `.srow`, `.srch-nomatch`+`.reqinfo`, `.srch-recent` |
| 2.6 | `/community` | `pages/community.php` | `HubController::community` | `community` | `.comm-wrap/banner/manifest/collab`, `.reqcard`+`.reqchip` (feed-LESS per §9-Q1) |
| 2.7 | `/about` | `pages/hub_tiers.php` | `HubController::tiers` | `about-tiers` | `.tier-hero`, `.tier-list`, `.tier-row`(+`--leaf/sun/paper/soil/tomato`) |
| 2.8 | `/account` | `pages/account_landing.php` *(new)* | `AccountController::index` *(new)* | `account`, `account-profile` | `.acct-empty/wrap/card/field/btn`, `.acct-profile`, `.setgroup`, `.setrow`(+`--danger`) |

Shared partials (per spec): `macros/{module_tile,market_disclaimer,price_card,freshness_pill}.php`;
reuse existing `prov_table`, `tier_badge`.

## 3. Data binding (content + fields from CODE — confirmed available)
- **Hub tiles** ← `Modules::all()['modules']` (id/name/tier/stat/hero). Heroes already in `public_assets/img/heroes/`.
- **Market list/detail** ← `MarketViewController` already exposes: `products` (name/unit/last_price/last_price_date/
  freshness_days) + per-product aggregates (min/median/max/source_count) + **`fetchHistory(28)` + `/api/v1/market/{slug}/history`**
  + `prov` source breakdown. ✅ The 14-day graph, history table, sparkline, freshness pill, source breakdown are
  ALL backed by existing data — no new schema. (Sparkline = last-7 of history; graph range selector see §9-Q3.)
- **Search** ← `HubController::search` already queries crops + products by `hebrew_name LIKE`. Group results
  book/market per `.srch-group`. (Suggestions/recent = client localStorage; see §9-Q4.)
- **Community** ← `POST /api/v1/contribute` exists (AssumptionsController::contribute, jsonl capture). `.reqchip`
  adds a `kind` value; reuse.
- **About/tiers** ← `Modules::all()['tiers']` (5 tiers already defined).
- **Account** ← NEW `AccountController::index`: render the logged-OUT shell (login card + open-core empty state).
  The logged-IN `account-profile` is built as a static shell (no auth backend in v1) — see §9-Q2.

## 4. Field-fidelity rule (team_00, binding)
Interface/style/structure = EXACT to Board-B. Content/labels/values = from code. No raw DB keys to users
(reuse `field_label()`/Hebrew labels). No invented data — where a value isn't in the mirror, show the designed
empty/stale state (`.pcard.is-empty`, `.emptybox`, `.srch-nomatch`) — never a fake number.

## 5. Acceptance criteria (VISUAL fidelity mandatory)
- **AC-1** classb.css + classb.js ported; `cropbook-v1.js` loads before `classb.js` on all Class B pages.
- **AC-2** each of the 7 surfaces matches its Board-B frame (palette/type/spacing/components) — QA captures a
  design-vs-live screenshot pair per surface (desktop + mobile).
- **AC-3** market: disclaimer ALWAYS present; cards⇄table toggle works; freshness pill 3-state correct; price
  graph + `.rangesel` render from history API; empty/stale states show on 0-report products (no fake prices).
- **AC-4** hub: module-tile grid + tier badges + coming-soon (`.is-soon`) state + audience cards + manifest band.
- **AC-5** search: grouped book/market results + `<mark>` highlight + no-match state with request CTA.
- **AC-6** community feed-LESS (manifesto + reqcard) unless §9-Q1 reopens it; about = 5-tier ladder; account =
  login shell + open-core empty state (+ profile shell).
- **AC-7** no regression: `composer test` green (+ new route/macro tests for account + market detail + search);
  `validate_aos` 0 FAIL; no LOCKED Python/migration touched; all routes 200; RTL legible; no raw keys/"Array"/stray "—".

## 6. Build sequence (per team_35 README §6)
tokens (already) → app-shell refine (2.1) → hub (2.2) → market list+detail (2.3/2.4) → search (2.5) →
community (2.6) → about (2.7) → account (2.8) → wire endpoints (contribute/history/export) → tests.

## 7. Orchestration
LOD400 lock (after §9) → **team_190 L-GATE_S** (non-Claude) → **team_10 build** → **team_50 VISUAL QA**
(design-vs-live per surface, desktop+mobile — the standard the prior rounds lacked) → **team_190 L-GATE_V**
(non-Claude, IR#1/#5, incl. visual fidelity) → ADR042 closure.

## 8. Out of scope
Backend/calculator/migrations; real auth (account is a shell); populating market price DATA (F-MKT-002 is an
ingest/data-freshness item, not UI); crop-book/calculator screens (Class A); WP-CB-MIG2 schema work.

## 9. OPEN QUESTIONS for team_00 (must resolve before LOD400 v1.0.0 lock)
team_35 + team_100 surfaced these — each changes the build:
1. **Community feed (CONFLICT).** team_35 delivered Community **feed-less** (manifesto + request form only),
   citing your earlier "no community management — form + text only." The Mobbin note had suggested a light feed.
   **Confirm feed-less** (team_100 recommends yes — matches your prior directive), or re-add a feed?
2. **Account scope for v1.** No auth backend exists. Build the account as a **visual shell only** (login form +
   open-core empty state + static profile-settings layout, non-functional), as a stable nav hook? (team_100: yes —
   matches team_35 "stable hook, full flows later".) Or defer `/account` entirely to a later module?
3. **Market graph time-ranges.** History API serves up to 28 days; the design's `.rangesel` offers 7/30/90/year.
   For v1: wire **7 + 28-day** (real data) and show 90/year as disabled-until-data, or implement all four against
   whatever history exists? (team_100: 7+28 live, 90/year disabled — honest, no fake series.)
4. **Search suggestions/recent.** Client-side localStorage for recent searches + static suggestion chips (no new
   backend), acceptable for v1? (team_100: yes.)
5. **Market units & freshness thresholds** (team_35 Q3): cards show ₪/kg·unit·bunch from `sale_unit`; freshness
   fresh ≤3d / aging 4–7d / stale >7d. Confirm these thresholds match OrganicMarketAgent's rolling window.

*team_100 will lock LOD400 v1.0.0 on your answers, then route team_190 L-GATE_S.*
