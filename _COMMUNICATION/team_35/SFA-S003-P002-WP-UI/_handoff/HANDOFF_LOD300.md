---
id: TEAM_35-LOD300-DELIVERY-2026-05-26
schema_version: aos_v1_team_messaging
from_team: team_35 (design)
to_team: team_100 (roadmap registrar) → team_110 (spec author)
type: LOD300_DELIVERY
subject: "SFA standalone public web app — LOD300 design package v1.2.0 (Flask Blueprint, sfa.nimrod.bio)"
date: 2026-05-26T00:00:00Z
related_wp: SFA-S003-P002-WP-UI (proposed new WP — team_100 to register)
status: DELIVERED — awaiting team_100 routing
priority: NORMAL
design_artifact: design/index.html (single HTML, design canvas, 28 artboards)
supersedes:
  - v1.0.0 (WordPress template — wrong stack)
  - v1.1.0 (Flask but routed direct to team_110, bypassing team_100 roadmap registration)
---

# LOD300 Delivery — SFA public web UI (`sfa.nimrod.bio`)

## 0. Mandate (proposed new WP: `SFA-S003-P002-WP-UI`)

Build a **standalone public web application** for SFA — Crop Book + Market Price
Index + Module Hub + Calculator (β) + Community surfaces.

**This is NOT WordPress.** It's a new Flask Blueprint inside the existing
`organic_market_agent` codebase (next to `admin/` and `crop_book/`). The existing
`[sfagent_*]` WordPress mu-plugins keep working in parallel for nimrod.bio embeds
until team_00 retires them. The new app at `sfa.nimrod.bio` is a separate
deployment target with no shared chrome.

The parent program `SFA-S003-P002-WP-B*` family (data foundation — JMF, Tend,
NI extraction, taxonomy) is already LOD500_LOCKED. This UI WP builds on top of
that data layer; it does not modify it.

The design accounts for the long-term roadmap:
- **Tier 1 — כלים לקהילה** (open): ספר גידולים, מחירון, מחשבון לחקלאי (β)
- **Tier 3 — כלים מתקדמים** (paid): תכנון עונה, ניהול לקוחות, מעקב יבול
- **Tier 2 — בדיוק לחווה שלך** (custom): חיבור Tend, יומן שדה
- Community contribution surfaces appear on every screen.

---

## 1. What's delivered

**Single design file:** `design/index.html` — pan/zoom design canvas with 28 artboards organized in 7 sections (see `_handoff/design/`).

**Source files in the design project** (live, runnable in any browser — no build step):

```
design/
├── index.html              Entry — open in browser
├── system.css              Nimrod DS v3.3 tokens
├── gj.css                  Garden Journal — mobile component styles
├── hub.css                 Module hub + tier badges
├── community.css           Feedback, contribute, suggest module
├── crop-book-deep.css      Book entry, family tree, pro table, search, crop+vars
├── desktop.css             Desktop shell (sidebar accordion + main)
├── desktop-extras.css      Desktop crop detail, market detail, calc, states
├── *.jsx                   16 React components — port to Jinja2 macros / partials
└── design-canvas.jsx       Pan/zoom design canvas (dev-only, not in production)
```

The JSX files use inline-Babel React for **fast design iteration only**. They are not the production format. Each component maps cleanly to a Jinja2 macro or partial — see `IMPLEMENTATION_PLAN.md`.

---

## 2. Target architecture

### 2.1 Stack

```
[nginx / gunicorn]
   ↓
[Flask app: organic_market_agent/sfa_app/]      ← NEW Blueprint
   ↓
[Jinja2 templates]                              ← extends design/
[SQLAlchemy → PostgreSQL]                       ← existing models, read-only
[Static assets: CSS, vegetable SVG sprite]      ← from design/, vendored
   ↓
[/wp-json equivalent → /api/v1/* JSON endpoints]
   ↓
[POST /api/v1/contribute → DB → email team_00]
```

### 2.2 Existing primitives that stay

- `organic_market_agent/admin/` — Flask admin app, port 5001, auth-protected. **Not touched.**
- `organic_market_agent/crop_book/` — existing read-only Blueprint with 3 routes (`/crop-book/`, `/crop-book/<slug>/`, `/api/crops`). **Models reused; views referenced as semantic SSoT.**
- `organic_market_agent/publisher/` — generates static JSON artifacts (for the WP shortcode pipeline). **Not touched.** The new app reads the same SQLAlchemy models — no need to round-trip through JSON.
- `wordpress/mu-plugins/sfagent-*.php` — keep working at nimrod.bio for now. **Not modified.** They embed published HTML. The new standalone app is a separate deployment target.

### 2.3 New: `organic_market_agent/sfa_app/`

```
organic_market_agent/sfa_app/
├── __init__.py             create_app() — public Flask app factory, no auth
├── routes/
│   ├── hub.py              /  /about/  /search/
│   ├── book.py             /book/  /book/questions/  /book/family/
│   │                       /book/table/  /book/search/
│   │                       /book/<slug>/  /book/<slug>/variety/<vslug>/
│   ├── market.py           /market/  /market/<slug>/
│   ├── calc.py             /calc/
│   ├── community.py        /community/  /api/v1/contribute
│   └── modules.py          module registry endpoint
├── templates/
│   ├── base.html           full HTML doc — NO shared chrome with admin
│   ├── shell/
│   │   ├── mobile.html     .gj-shell + header + body + footer
│   │   └── desktop.html    .dt-shell + sidebar accordion + main
│   ├── macros/
│   │   ├── tier_badge.html
│   │   ├── module_card.html
│   │   ├── price_card.html
│   │   ├── crop_card.html
│   │   ├── variety_row.html
│   │   ├── contrib_strip.html
│   │   ├── crosslink.html
│   │   ├── market_disclaimer.html
│   │   └── feed_item.html
│   └── pages/
│       ├── hub_home.html
│       ├── hub_tiers.html
│       ├── hub_calc.html
│       ├── book_entry.html
│       ├── book_questions.html
│       ├── book_family.html
│       ├── book_table.html
│       ├── book_search.html
│       ├── book_crop.html
│       ├── book_variety.html
│       ├── market_list.html
│       ├── market_product.html
│       ├── community.html
│       └── search_results.html
├── static/
│   ├── tokens.css          ← copy from design/system.css (curated)
│   ├── gj.css              ← copy from design/gj.css
│   ├── hub.css             ← copy from design/hub.css
│   ├── community.css       ← copy from design/community.css
│   ├── crop-book-deep.css  ← copy from design/crop-book-deep.css
│   ├── desktop.css         ← copy from design/desktop.css
│   ├── desktop-extras.css  ← copy from design/desktop-extras.css
│   ├── sfa.js              vanilla JS — accordion state, contrib form submit
│   └── icons.svg           vegetable SVG sprite extracted from illustrations.jsx
├── modules.py              SFA_MODULES + TIERS dicts (Python mirror of yaml)
├── helpers.py              freshness, ttl, breadcrumbs, format helpers
└── contribute.py           POST handler + rate limiting + email
```

### 2.4 Deployment

- **Host:** waldhomeserver (per `_aos/lean-kit/modules/12-home-server-infrastructure/`)
- **Process:** gunicorn behind nginx — own service unit (`sfa-public.service`)
- **Port:** new entry in port-registry (suggest 5002 to keep admin's 5001 free)
- **Domain:** `sfa.nimrod.bio` — nginx vhost reverse-proxies → gunicorn:5002
- **TLS:** Let's Encrypt via existing certbot infrastructure on waldhomeserver
- **Static assets:** served by nginx directly from `organic_market_agent/sfa_app/static/`
- **DB:** reads from existing PostgreSQL (read-only user `sfa_public`, scoped to public-safe tables)

The old WP-embedded version at `nimrod.bio/*` keeps working through the existing mu-plugins until team_00 decides to retire them.

---

## 3. UX architecture (unchanged by stack)

The design itself is platform-neutral. All decisions about Tier language, Community surfaces, mobile-first, market disclaimer, and crop+varieties hierarchy stay exactly as designed and documented in the design canvas. See:

- `DESIGN_TOKENS.md` — canonical CSS tokens
- `COMPONENTS.md` — every UI component with DOM contract
- `TEMPLATES.md` — page-by-page Jinja2 contract (rewritten for Flask)
- `MODULES_REGISTRY.yaml` — single source of truth for modules

### 3.1 Three-tier language (locked)

| Tier | Hebrew label |
|------|--------------|
| `open`   | **כלים לקהילה** |
| `beta`   | **בטא · ניסיוני** |
| `coming` | **בקרוב** |
| `paid`   | **כלים מתקדמים** |
| `custom` | **בדיוק לחווה שלך** |

### 3.2 Crop Book is the foundation knowledge layer

Four mandated entry paths: questions, family tree, pro table, advanced search. Each crop has a **crop → varieties** hierarchy.

### 3.3 Market is primarily a community marketing tool

Mandatory disclaimer block at the top of every market view. Wording is fixed.

### 3.4 Community surfaces in every page

Every shell renders at least one path to contribute. Mobile: floating button + inline ContributeStrip. Desktop: sidebar accordion + ContributeStrip in module pages.

### 3.5 Mobile-first, desktop is enhancement

Single HTML per route. CSS media query at `min-width: 900px` swaps mobile shell for desktop shell. No server-side device detection in v1.

---

## 4. Mapping to existing code

| Existing | New SFA app interaction |
|----------|------------------------|
| `crop_book.views:crop_list` (`/crop-book/`) | `sfa_app.routes.book:table` reuses same SQLAlchemy queries, different template |
| `crop_book.views:crop_detail` (`/crop-book/<slug>/`) | `sfa_app.routes.book:crop` reuses same query, renders new shell + crop+vars hierarchy |
| `crop_book.views:api_crops` (`/api/crops`) | `sfa_app.routes.book:api_crops_filter` is the **identical** filter logic — reuse Filter SSoT |
| Models: `Crop`, `CropVariety`, `CropVarietySourceValue` | Reused as-is, read-only |
| Models: `PricebookProduct`, `MarketObservation`, aggregates | Reused as-is, read-only |
| `publisher/rolling_aggregate.py` | Reused for market 7-day rolling avg |
| `admin/auth.py`, `audit.py` | **NOT** used. Public app is auth-less. |
| Static assets `sfagent-base.css`, `sfagent-crop-book.css` | **Not** loaded. New app has its own CSS in `sfa_app/static/`. |

### 4.1 No locked-file changes expected

| File | GCR? | Change? |
|------|------|---------|
| `models.py` (`Crop`, `CropVariety`) | no | read-only access only |
| `crop_book/views.py` | no | new app doesn't modify the existing blueprint; can call helper functions if they're refactored to a service layer |
| `publisher/` | no | not touched by new app |
| WP mu-plugins | no | keep working independently |

The new Blueprint adds files only — `models.py` already has every field the design needs. **If** the design adds a field (e.g. variety `taste_rating` 1–5 used in CB5 mockup) that doesn't exist in DB, that becomes a GCR_1 for `models.py` + new migration — team_110 to identify in LOD200.

---

## 5. New REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/api/v1/modules` | Module registry JSON (mirror of `modules.py`) |
| GET    | `/api/v1/search?q=<term>` | Global search across crops + products + community |
| GET    | `/api/v1/market/<slug>/history?days=28` | Trend chart data for market detail |
| GET    | `/api/v1/community/feed?limit=10` | Recent contributions for hub home & sidebar |
| POST   | `/api/v1/contribute` | Auth-less, rate-limited contribution submission |

All return JSON; all `/api/v1/*` is CORS-open for community embedding later.

---

## 6. Open questions for team_110 LOD200 / LOD400

| # | Question | Default |
|---|----------|---------|
| Q1 | Sub-domain `sfa.nimrod.bio` is final, or alt routing? | sfa.nimrod.bio confirmed (already live as old WP-embed) |
| Q2 | Reuse `admin/__init__.py:create_app` pattern, or fresh app factory? | **fresh** — public app has different config (no auth, public-readonly DB user) |
| Q3 | Shared models package vs duplicate model files? | shared — `organic_market_agent.models.*` imported by both `admin/` and `sfa_app/` |
| Q4 | `/api/v1/contribute` storage: new `community_contributions` table OR option-style row? | new table (migration) — proper queue with admin review later |
| Q5 | Variety `taste_rating` field — exists? add? | flag for LOD200 to check `CropVariety` schema. If missing, GCR_1 + new migration. |
| Q6 | Frontend JS — vanilla, Alpine.js, htmx, or React island? | **vanilla** (minimal — accordion state + form submit + simple chart); matches existing `crop_book/publisher/static/sfagent-crop-book.js` pattern |
| Q7 | Calculator (β) scope in WP-B1 or WP-B3? | WP-B3 — keep WP-B1 to shell + hub + book + market |
| Q8 | AI background images: pre-render once and ship as `static/img/*.webp`, or runtime? | pre-render — fewer moving parts |
| Q9 | nimrod.bio WP-embed: retire eventually? | Out of scope for WP-B. team_00 decides timing. |

---

## 7. Acceptance criteria

- [ ] `sfa.nimrod.bio` serves the new standalone Flask app (gunicorn + nginx)
- [ ] No code from the WP mu-plugins is referenced
- [ ] Mobile shell renders at all routes (<900px)
- [ ] Desktop shell renders with sidebar accordion (≥900px)
- [ ] Existing crop/variety/market data renders without schema changes
- [ ] Hub home lists 8 modules from `modules.py`, grouped into 3 tier sections
- [ ] All 4 book entry paths (questions / family / table / search) work
- [ ] Book crop detail shows the crop → varieties hierarchy (per design CB5)
- [ ] Market list/detail leads with the mandatory disclaimer block
- [ ] `POST /api/v1/contribute` accepts a submission, persists, emails team_00
- [ ] LCP < 2.5s on 4G, no JS errors, WCAG AA contrast
- [ ] Existing admin (port 5001) keeps working
- [ ] Existing nimrod.bio WP-embed keeps working (we did not touch those mu-plugins)

---

## 8. References

- Design canvas: `design/index.html` (open in browser — 28 artboards)
- Module registry source of truth: `MODULES_REGISTRY.yaml`
- Existing Flask crop book: `organic_market_agent/crop_book/views.py`
- Existing Flask admin: `organic_market_agent/admin/`
- Production URL (current WP-embedded view): `https://sfa.nimrod.bio/` — to be replaced
- Server registry: `_aos/lean-kit/modules/12-home-server-infrastructure/`

---

## 9. Done-criteria for THIS handoff

- [x] LOD300 design package delivered as single HTML
- [x] All artboards labeled with `data-screen-label`
- [x] Module catalog single-source-of-truth in YAML
- [x] Three-tier UX language locked
- [x] Community surfaces in every screen
- [x] Mobile + desktop variants for all key screens
- [x] **Corrected** architecture mapping: Flask + Jinja2 + SQLAlchemy (not WP)
- [ ] team_110 ACK + LOD400 spec authoring
- [ ] team_00 advisory on Q1, Q5, Q7, Q9

---

*Issued 2026-05-25 by team_35 (design).*
*Supersedes the WordPress-assumption v1.0.0 from 2026-05-24.*
