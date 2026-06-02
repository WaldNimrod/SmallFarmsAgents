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

## 9. team_00 DECISIONS (resolved 2026-06-02 — LOD400 v1.0.0)
1. **Community = feed-less — CONFIRMED.** team_35's feed-less delivery is correct; it reflects a team_00 update
   sent directly to them. Build manifesto + `.reqcard` request form only. No activity feed. (Closes the conflict.)
2. **Account = UI shell only + "בקרוב" label — CONFIRMED.** Build `/account` as visual-only: login card +
   open-core empty state + static profile/settings layout, each carrying a **"בקרוב"** badge. No auth backend,
   no functional submit. Stable nav hook.
3. **Graph time-ranges — APPROVED.** `.rangesel` wires **7 + 28-day from real history**; **90-day + year render
   disabled** (`.is-disabled`, "בקרוב") — never a fabricated series. (Honest-data rule.)
4. **Search suggestions/recent — APPROVED, WITH CONDITION.** Client-side localStorage only (recent searches) +
   static suggestion chips; **no new backend**. ⚠ team_00 condition: **any server-side change proposed by the
   build (search ranking, new endpoints, indexing, etc.) is NOT approved** — it is logged as an *idea to review*
   in a future WP register (`SFA-S003-P004-WP-SRV-IDEAS`, opened 2026-06-02), with clear provenance ("proposed,
   unapproved"). The build must stay UI/client-side; if it believes a server change is required, it STOPS and
   files the idea, not implements it.
5. **Market units & freshness — APPROVED IN PRINCIPLE; thresholds locked to the OMA 7-day window (see §9a).**

## 9a. Market units + freshness — APPROVED TABLE (real values, v1.0.0)
Grounded in the live system (not invented): `freshness_days = today − last_price_date` (computed at ingest,
`sfa_ingest_push.py`); the OMA window is **7 days** (the live disclaimer states "ממוצעים מתגלגלים … 7 ימים
אחרונים"). `unit` comes from `measurement_units.unit_symbol` per product; `sale_unit` aliases `harvest_unit_default`.

**Freshness pill (3-state, on the 7-day window):**
| State | `freshness_days` | Pill class | Color | Label (he) | Example |
|-------|------------------|-----------|-------|------------|---------|
| Fresh | `≤ 3` | `.fresh--fresh` | leaf | "טרי · עודכן היום/אתמול" | price_date = today → 0d → fresh |
| Aging | `4–7` | `.fresh--aging` | sun | "מתעדכן · לפני N ימים" | price_date = 5d ago → aging |
| Stale | `> 7` (or null) | `.fresh--stale` | tomato | "ישן · לפני N ימים" / "אין דיווח" | 9d ago → stale; null → empty card |

**Price unit display (from product `unit` / `sale_unit`):**
| Source value (`unit_symbol`) | Display (he) | Example card price |
|------------------------------|--------------|--------------------|
| `kg` | ₪ N.NN · לק״ג | "₪ 8.50 · לק״ג" |
| `unit` / `יח׳` | ₪ N.NN · ליחידה | "₪ 3.00 · ליחידה" |
| `bunch` / `אגודה` | ₪ N.NN · לאגודה | "₪ 5.00 · לאגודה" |
| (null / unknown) | ₪ N.NN | "₪ 8.50" (no unit suffix) |
| (no price row) | — · אין דיווח + ◐ תרמו מחיר | empty `.pcard.is-empty` |

> ⏳ **team_00 to APPROVE this §9a table** (decision #5 was "approve in principle, show me the full table with
> examples"). On approval the spec is fully locked v1.0.0. Thresholds (≤3 / 4–7 / >7) and the 7-day window are the
> only freshness numbers; if OMA's window differs, adjust here only.

*Locked to v1.0.0 on team_00 approval of §9a → then team_190 L-GATE_S.*
