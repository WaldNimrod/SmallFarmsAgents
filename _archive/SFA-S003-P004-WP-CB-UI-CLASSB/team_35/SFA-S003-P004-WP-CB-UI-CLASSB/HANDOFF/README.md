# Handoff — SFA UI, full interface (Class A + Class B)

> **WP:** SFA-S003-P004-WP-CB-UI-CLASSB · **From:** team_35 (Design Studio) · **To:** team_100 → Claude Code build
> **Date:** 2026-06-02 · **Status:** approved by team_00 (Community feed = one open flag, see §7)
> **Live site being re-skinned:** `https://sfa.nimrod.bio/` — every surface moves to the **v2 white-green** system.

This package is the **complete UI contract for the whole product** — both the already-delivered **Class A** screens (Crop Book + Calculator) and the new **Class B** screens (Hub, Market, Search, Community, About, Account, App-shell). It is assembled into one bundle so the build has a single, consistent source of truth. **One design system, eight token files, two boards, two spec sets.**

---

## 1 · About the design files

The files in `design/` are **design references created in HTML/CSS/JS** — two pannable spec boards that prototype the intended look and behaviour. **They are not production code to ship as-is.** The task is to **recreate these designs in the target codebase** using its patterns.

**Target delivery tier (locked by the WP):** **Slim4 / PHP on uPress** — server-rendered templates + **light vanilla JS** for the interactive bits (calculators, filters, toggles). No SPA framework. The two JS files (`cropbook-v1.js`, `classb.js`) are plain ES5-ish vanilla so they port almost 1:1. Treat HTML/CSS as the visual contract and the JS as the behaviour contract.

The whole UI is **Hebrew, RTL** (`dir="rtl"`). Brand: **Nimrod.bio AOS DS v3.4 → v2 white-green** + watercolor crop masters + Carmela display font.

**Fidelity: high.** Final colours, type, spacing, radii, shadows and interactions are all specified in `design/tokens.css` + `design/cropbook-v1.css` + `design/classb.css`. Recreate pixel-accurately. **Caveat:** the boards are *spec canvases* — the `.board`, `.sec`, `.frame`, `.notes`, `.ab__label`, `.patref` chips and English annotations are **review chrome, NOT product**. Build only what is *inside* the `.sh` app shells.

---

## 2 · File map

```
design_handoff_classb/
  README.md          ← this file (the whole-interface contract)
  index.html         ← navigable surface map — open this first
  design/
    Board-A-Book-and-Calculator.html        ← book index · crop 3-depths · calculators · assumptions · states · rotation
    Board-B-Hub-Market-Search-Community-About-Account.html   ← app-shell · hub · market(list+detail) · search · community · about · account
    tokens.css         ← :root design tokens + base type. PORT THIS FIRST (verbatim).
    cropbook-v1.css    ← Class A components (.cb-/.cv-/.af/.topic/.ref/.aud/.ftop/.ptable…)
    classb.css         ← Class B components (.sh__search/.modtile/.audcard/.mkt-*/.pcard/.pgraph/.srch-*/.comm-*/.tier-*/.acct-*…)
    cropbook-v1.js     ← Class A behaviour (calculators, assumptions, filters, depth tabs, audience switch, tooltips, pagination)
    classb.js          ← Class B behaviour (request chips, price-graph range selector)
    assets/
      Carmela.ttf                          ← wordmark/hero display font (confirm web-embed license — A_OPEN_ISSUES Q3)
      wc-lettuce/radish/parsley/dill.png   ← Class A flat crop masters (mix-blend-mode: multiply on near-white)
      crops/wc-*.png                       ← Class B crop masters (12, same treatment)
      heroes/*.webp                        ← 8 module heroes (warm washes, hub cards)
      contact.webp                         ← community banner wash
  spec/
    A_COMPONENTS-delta.md   A_DESIGN_TOKENS-delta.md   A_TEMPLATES-delta.md   A_OPEN_ISSUES.md
    B_COMPONENTS-TEMPLATES-classb-delta.md   ← Class B components (§30–42), routes, partials, §3.8 reference-pattern table
```

> **System logo** is an inline SVG `<symbol id="sfa-logo">` defined once at the top of each board `<body>` (a sprout over three planting beds). **Not an image file.** Reuse via `<use href="#sfa-logo"/>`. Do not use the old garden/radish mark.

---

## 3 · The surfaces (the whole interface)

### Class A — already delivered & approved (WP-CB-1). Do NOT redesign; build as-is.
| Route | Surface | Board frame (`data-screen-label`) | Key UI |
|---|---|---|---|
| `/crop-book/` | **Book index** | `book-entry` | Audience switch (Cards⇄Table) · **advanced filter bar** `.ftop` (family · season/date · sow-vs-transplant · summer-shade · frost · DTM range · completeness) · cards grid w/ season-bar + yield mini-bar · per-meter table w/ calc columns · 25/page pagination |
| `/crop-book/{slug}/` | **Crop page — 3 depths** | `crop-lettuce` (complete), `crop-radish-partial` (mobile/partial) | **Depth tabs**: פשוט (headline + per-topic summary) · מלא (every field, collapsible topic sections) · העמקה (variety-comparison table + per-source JMF reference sheet + provenance hierarchy). One route, depth = param. |
| `/calc/` | **Calculator dashboard** | `calc-page` | Dark context strip → wired module cards (`.modcard`, feeds between them) → sticky summary → PDF/CSV export |
| — | AssumptionField · states · rotation | `s-assume`, `s-states`, `s-rotation` | First-class `.af` · validated/unvalidated/missing cues · family rotation chip |

> **"Advanced search"** = the `.ftop` advanced-filter panel on the book index (`book-entry` frame, "סינון מתקדם" toggle). It is the in-page, multi-parameter search; there is no separate search screen for the book (Class B `/search` is the *global* crops+market search).

### Class B — new in this WP (extends the same system)
| Route | Surface | Board frame | Pattern (§3.8) |
|---|---|---|---|
| (shell) | **App-shell** | `shell-desktop`, `shell-mobile` | Planta · Notion · Arc |
| `/` | **Hub / Home** | `hub-home`, `hub-home-mobile` | Notion/Arc/Flighty launchers + Planta |
| `/market/` | **Market list** | `market-list` | Blinkit/Zepto + Copilot (cards⇄table) |
| `/market/{slug}` | **Market detail** | `market-detail` | Copilot Money / Delta (graph + range selector + history) |
| `/search?q=` | **Search** | `search-results`, `search-nomatch` | Planta / NYT Cooking |
| `/community` | **Community** | `community` | Strava/Duolingo lightness (feed-less — §7) |
| `/about` | **About / Tiers** | `about-tiers` | Notion / Linear pricing |
| `/account` | **Account** | `account`, `account-profile` | Wolt / Planta settings |

Full per-component contracts: **`spec/A_COMPONENTS-delta.md`** (Class A) and **`spec/B_COMPONENTS-TEMPLATES-classb-delta.md`** (Class B, incl. the §3.8 reference-pattern table + routes + partials).

---

## 4 · Design tokens (port `design/tokens.css` verbatim)

**Palette — v2 white-green (no cream, no new palette).**
`--gj-paper #f8fbf8` · `--gj-paper-2 #eef4ee` · `--gj-paper-3 #dde8dd` · `--gj-ink #1f2a22` · `--gj-ink-soft #5d6b5e` · `--gj-line #dce6dc`.
**Accent worlds:** leaf `#6f8a45`/`#4d6a2c` (book/open/validated/primary) · tomato `#c24f2c`/`#8e3018` (market/attention/missing) · sun `#d39a32`/`#a4711a` (beta/calc/unvalidated) · soil `#8b5d2f`/`#5a3c1a` (paid/account/result numerals) · code/teal `#2d8a8c`/`#1f5e60` (digital/AssumptionField).
**Type:** body `Assistant` · headings/numbers `Frank Ruhl Libre` · mono/eyebrows `JetBrains Mono` (LTR technical only — never Hebrew labels) · wordmark `Carmela`. Hebrew labels always use the body face.
**Radii** 8/12/14/18/99px · **shadows** green-neutral s/m/l · **spacing** 4-pt (4…48).
Soft tints use `color-mix(in oklch, var(--gj-X) N%, var(--gj-paper))`. **If any borrowed UX pattern conflicts with these tokens, the tokens win.**

---

## 5 · Interactions & behaviour (the two JS files)

- **Class A** (`cropbook-v1.js`): live calculator recompute (`CALC[kind]` pure formulas) · AssumptionField expand/override/reset · editable book value (`.bv__in` → `.is-overridden`) · filter chips + advanced-panel toggle + reset · audience switch · depth tabs · topic collapse · field-info tooltip injection (`FIELD_INFO`) · pagination · calc-modal overlay.
- **Class B** (`classb.js`): request/suggest chip single-select · price-graph time-range segmented control. Market category chips + the market cards⇄table toggle **reuse** `cropbook-v1.js` (`wireFilters`, `wireAudience`) — load `cropbook-v1.js` first, then `classb.js`.
- Tooltips open on hover **and** `:focus-within` (keyboard accessible). Motion budget: hover lift 140–180ms, chevron/✎ rotations; no large animations.

---

## 6 · Build order (suggested)

1. **`tokens.css`** verbatim (`:root` + base type + font imports). Verify RTL + fonts load.
2. **App-shell** (`.sh` + `.sh__nav` + `.sh__search` + `.sh__acct` + mobile `.sh__nav--mobile`) + the `#sfa-logo` symbol + footer. (§3.1 — unblocks every page.)
3. **Hub** (`/`) — module-tile launcher grid + explainer band + audience row. (§3.2.)
4. **Market** list + detail (disclaimer always-on · cards⇄table · freshness · price graph + range selector · `.prov` source breakdown · empty/stale). (§3.3.)
5. **Book index** + **crop 3-depths** + **calculator dashboard** (Class A — port from `cropbook-v1.*`).
6. **Search** · **Community** · **About** · **Account** (Class B remainder).
7. Wire endpoints: `/api/v1/contribute` (request-info / suggest), `/api/v1/assumptions`, `/calc/export.{pdf,csv}`.

Re-open either board in a browser to compare pixel-for-pixel — they are the source of truth for spacing and colour.

---

## 7 · Open items for team_100 / team_00

1. **⚠ Community feed (conflict).** §3.8 reference note suggests a Strava/Duolingo "light feed"; the client explicitly removed the feed ("no community management — form + text only"). Delivered **feed-less** (manifesto + request form). **Confirm before re-adding any feed.**
2. **Account tier.** Login is shown as the gate to paid/custom modules; the open core must never require it (design assumes optional).
3. **Market units & freshness window.** Cards show ₪/kg · ₪/unit · ₪/bunch from `sale_unit`; freshness fresh ≤3d · aging 4–7d · stale >7d — confirm against OrganicMarketAgent's rolling window.
4. Class A open questions remain in **`spec/A_OPEN_ISSUES.md`** (8 items + JMF gap-analysis).
