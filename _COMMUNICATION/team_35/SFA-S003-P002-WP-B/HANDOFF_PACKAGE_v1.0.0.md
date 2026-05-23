---
id: HANDOFF_PACKAGE_SFA-S003-P002-WP-B_v1.0.0
type: HANDOFF_PACKAGE
track: CONTENT
from: team_100 (smallfarmsagents Chief Architect)
to: team_35 (Design Studio — Claude Design sandbox)
date: 2026-05-23
project: smallfarmsagents
wp: SFA-S003-P002-WP-B
program: SFA-S003-P002 (Crop Book Enrichment & Consolidation)
mandate_branch: claude/gallant-elbakyan-727a60
team_00_authorization: "Direct invocation by team_00 2026-05-23 per team_35 governance §invocation: on_demand_by_team_00."
gate_model: PIPELINE_FEEDER (no L-GATE_B/V; CONTENT track per ADR044)
deliverable_phases: ["LOD200 wireframes", "LOD300 mockups + design book"]
next_step: "team_35 produces LOD200 wireframes for unified ספר גידולים + ממשק המחירון system. Iterate with team_00 until LOD200 PASS. Then advance to LOD300 mockups + design book. Hand back to team_100 for implementation packaging into a build WP."
handoff_to: team_35
handoff_context_pointer: _COMMUNICATION/team_35/SFA-S003-P002-WP-B/HANDOFF_PACKAGE_v1.0.0.md
---

# HANDOFF_PACKAGE — SFA-S003-P002-WP-B — UX/UI Overhaul

## §1 Greeting + your role

Welcome, **team_35 (Design Studio / סטודיו עיצוב)**.

You operate in the **Claude Design sandbox** (`claude-design-sandbox` engine: HTML-first design environment, project-based filesystem, live HTML preview, React/JSX inline, NO shell, NO git from inside the sandbox).

Per your governance contract:
- You map to the **CONTENT track** (ADR044 §1)
- You are a **PIPELINE_FEEDER** — produce artifacts, do not operate gates
- Invocation is **on_demand_by_team_00 only** — and team_00 has authorized this engagement on 2026-05-23
- Deliverable phases: **LOD200 wireframes** + **LOD300 mockups + design book**
- Handoff routing: your artifacts land at `_COMMUNICATION/team_35/SFA-S003-P002-WP-B/`; team_100 then folds them into the implementation pipeline

## §2 The brief

Two existing modules on `https://www.nimrod.bio/`:

| Module | Shortcode | Status |
|--------|-----------|--------|
| **ממשק המחירון** (Market Price Index) | `[sfagent_market_report]` | LIVE — daily community-sourced organic produce price index, ~32 products, refreshed nightly |
| **ספר הגידולים** (Crop Book) | `[sfagent_crop_book]` | LIVE — 52 crops × 242 varieties, deep agronomic data per crop (8 detail tabs), client-side SPA |

**team_00 directive 2026-05-23:** treat these as **one system with two modules**, and do a significant UX/UI upgrade across both. The two should feel like they belong together (shared design language, shared navigation patterns, shared mental model for the user) while preserving their distinct purposes.

**Not a re-platforming.** Both modules will continue to be WordPress shortcodes delivering HTML/JS fragments to a Flatsome child theme on uPress. The UX/UI work is at the **presentation layer** — wireframes + mockups + design book — that the implementation team (team_10) will then code.

## §3 Source of truth — existing implementations to study

These are the LIVE references. Visit them, read the markup, understand current behavior. THEN design what should change.

### §3.1 Live URLs (visit these first)
- **Market index (price report):** `https://www.nimrod.bio/smallfarmsagent/` (WP page id 91325, slug `smallfarmsagent`)
- **Crop book:** `https://www.nimrod.bio/crop-book/` (WP page hosting `[sfagent_crop_book]` shortcode + SPA)

### §3.1.1 ⚠ IMPORTANT — `/smallfarmsagent/` is currently STALE (do not let this mislead your design)

As of 2026-05-23, the market index page renders only 1 product (עגבנייה) with placeholder dates ("עודכן 2026-04-17 · 1 מוצרים · תאריך דוח: 2099-08-12"). This is **NOT the real product set**.

**Why:** the WP page was hand-edited in 2026-04-02 with baked-in HTML body fragment from the early test phase (when the upload pipeline still failed and only 1 product had data). The dynamic shortcode `[sfagent_market_report]` is correctly defined and the data layer is healthy — the canonical body fragment file at the WP media library currently contains **34 real products** (אבוקדו, ארטישוק, בזיליקום, בטטה, ביצים, בננה, בצל יבש, בצל ירוק, ברוקולי, ...) refreshed nightly. The page just doesn't reference the shortcode.

**For your design work, the REAL current data shape is at:**
- Manifest (provenance + counts): `https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-manifest.json` (live, currently `product_count: 34, report_date: 2026-05-09`)
- Full body fragment (the HTML the shortcode WOULD return): `https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-public-report-body.html` (~107KB, 34 product rows in dual layout)
- Raw report data (for understanding what fields exist): `https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-public-report.json` (JSON; each product has product_id, canonical_name_he, category, sample_size, distinct_sources, min/max/avg/median price, etc.)

team_00 is tracking the page fix as a separate operational item; once fixed, `/smallfarmsagent/` will show the 34-product list. **Design your wireframes against the rich data shape (34 products, multi-column metrics, community-source attribution), NOT against the misleading 1-product current render.**

### §3.2 Current HTML/CSS/JS source — repo references

The HTML/CSS the public sees is generated by these (you'll review the rendered output, not edit these — they're LOD500_LOCKED implementation):

**Market report:**
- `organic_market_agent/publisher/templates/public_report_body.html` (the fragment uploaded to WP)
- `organic_market_agent/publisher/templates/public_report.html` (standalone preview)
- CSS deployed at `wp-content/themes/flatsome-child/sfagent-base.css` (design tokens, shared)

**Crop book:**
- `organic_market_agent/crop_book/publisher/templates/crop_book_body.html` (the SPA fragment uploaded to WP — ~30 KB HTML + inline CSS + inline JS)
- `organic_market_agent/crop_book/publisher/templates/crop_book.html` (standalone preview)
- `organic_market_agent/crop_book/publisher/static/sfagent-crop-book.js` (the SPA JS — vanilla, no React; ~115 KB)
- Data shape: `sfagent-crop-book-data.json` (~388 KB raw, ~15 KB gzipped; 52 crops × 242 varieties × source_values per field)
- 8 detail tabs: varieties, description, economics, care, equipment, sources, timeline, field-data

**Admin reference (for content depth understanding, not public surface):**
- Flask admin: `organic_market_agent/crop_book/views.py` + `templates/crop_book/{index,crop,_macros}.html`
- Visit local admin (if running): `http://localhost:5001/crop-book/`

### §3.3 What the user sees today — quick characterization
- **Market report:** Hebrew RTL list of products with prices, freshness indicator, community-source attribution. Simple, dense.
- **Crop book:** Hebrew RTL grid of crop cards → click → SPA detail panel with 8 tabs. Functional but visually utilitarian (no images, lots of tables, dense numerics).

## §4 Constraints you MUST respect

| Constraint | Why | Implication for design |
|------------|-----|------------------------|
| **WordPress shortcode delivery** | Architecture: each module is a `[sfagent_*]` shortcode rendering inside a WP page on Flatsome child theme. uPress hosting. | Designs ship as HTML fragments. No SPA framework outside what already exists (vanilla JS for crop_book; static HTML for market). Can leverage modern CSS (Grid, Flex, CSS variables). |
| **RTL Hebrew primary** | Israeli audience. All text Hebrew first, English secondary. | `dir="rtl" lang="he"` on root. Test with Hebrew strings, not lorem. Numerics LTR within RTL flow. |
| **Mobile-first** | Significant mobile traffic to nimrod.bio. WP004 noted mobile parity deferred. | Wireframes start mobile portrait; tablet + desktop are progressive. |
| **Static published artifacts** | Both modules deliver as uploaded static HTML/JSON; not server-rendered at request time. | No personalization, no user state, no auth. Designs assume anonymous public reader. |
| **Existing design tokens** | `sfagent-base.css` defines shared tokens (green-dark, green-mid, green-light, sand, sand-dark, gold). | You may evolve the palette but propose explicit token names; team_10 implements. |
| **System fonts** | uPress + Flatsome use system font stacks; no Google Fonts (mu-plugin restriction + performance). | Use system-ui / -apple-system / Heebo fallback for Hebrew. |
| **No client-side images currently** | Crop book has zero crop photos (text + tables only). Market has no charts. | If you propose images/charts, flag explicitly as scope expansion — sourcing photos is its own work. |
| **AOS_DIRECTORY_CANON write scope** | Your artifacts MUST land under `_COMMUNICATION/team_35/SFA-S003-P002-WP-B/`. Nowhere else. | No code writes; no governance edits. Pure design artifacts. |

## §5 What WP-A is doing in parallel (you do NOT need to wait)

team_110 (AOS Domain Architect) is concurrently designing the data-enrichment architecture (WP-A) — more sources, deeper data, per-field weight/trust policy.

**Your design must accommodate richer data per crop**, even if the data isn't there yet:
- More source attribution surfacing (the "מקורות" tab is the existing analog)
- Confidence / quality signal per data point (vs binary present/absent)
- More fields per crop/variety as enrichment lands
- Possibly: hover-state showing source provenance on any displayed value

But you do NOT need to wait for WP-A spec. Design against the EXISTING schema (it's a baseline) and team_00 will iterate with you if WP-A's outputs need design accommodation.

## §6 Deliverables (canonical CONTENT-track phases)

### Phase 1 — LOD200 (Wireframes)
Path: `_COMMUNICATION/team_35/SFA-S003-P002-WP-B/LOD200_WIREFRAMES_2026-05-XX_v1.X.X.md` (or an HTML/preview file in same directory)

Wireframes covering:
1. **Unified system mental model** — how a visitor navigates between market report and crop book and perceives them as one whole
2. **Mobile portrait** primary layouts for each module's main view + key detail views
3. **Crop book grid + detail** redesigned (8-tab structure may collapse/reorganize per your judgment)
4. **Market report list + per-product detail** redesigned
5. **Cross-linking patterns** (e.g. a market product → crop book deep-dive; a crop book variety → live market price)
6. **Empty states + freshness indicators**
7. **Source attribution UI pattern** (extends current "מקורות" tab thinking — see WP-A briefing)

Hand back to team_00 for review. Iterate.

### Phase 2 — LOD300 (Mockups + Design Book)
Path: `_COMMUNICATION/team_35/SFA-S003-P002-WP-B/LOD300_MOCKUPS_2026-05-XX_v1.X.X.md` + supporting `.html` previews

Includes:
1. **Hi-fi mockups** of every wireframe screen (mobile + tablet + desktop)
2. **Design book / system documentation**:
   - Color tokens (palette, semantic names like `--sfa-crop-card-bg`, `--sfa-market-fresh`)
   - Typography scale + Hebrew/English pairing rules
   - Spacing scale (consistent rhythm)
   - Component inventory (cards, tabs, badges, freshness pills, source chips, etc.)
   - Interaction states (hover, focus, active, disabled)
3. **Implementation handoff notes** — anything the implementer needs to know that isn't obvious from the mockups

Hand back to team_100. team_100 packages the LOD300 + design book into an implementation WP for team_10 (becomes a separate sibling WP under SFA-S003-P002).

## §7 What WE care about — UX/UI principles

Not prescriptive — these are signals on the priorities, not absolute rules:
1. **Information density is OK** — our users are farmers and ag-curious, they want depth. Don't dumb it down for the sake of "clean".
2. **Trust signals matter** — community-sourced data + multi-source crop book → make provenance visible without making it noisy.
3. **Hebrew first, not localized-as-afterthought** — Hebrew numerals, Hebrew dates, Hebrew unit abbreviations are first-class.
4. **Fast is a feature** — both modules are static-published; designs should keep that contract.
5. **Internal coherence > novel surprises** — when in doubt, choose the option that makes the two modules feel more unified.

## §8 Sandbox environment notes (you already know, restated for clarity)

- You have HTML/CSS/JS/JSX inline previewing — use it for mockups
- You don't have shell access — file references in this package use absolute paths so team_100 can resolve them on the host filesystem when relaying answers to questions
- You cannot push commits — your artifacts land in `_COMMUNICATION/team_35/SFA-S003-P002-WP-B/`; team_100 commits them on the canonical branch
- If you need to see live output: ask team_00 to fetch the rendered HTML from the WP URLs (HTTP) or from the repo paths (filesystem) — they can paste it back

## §9 What success looks like

team_00 accepts the LOD200 wireframes (likely after 1–2 iteration rounds). team_00 accepts the LOD300 mockups + design book. team_100 packages it into a build WP. team_10 implements. team_190 validates. The result: visitors to nimrod.bio see one coherent system instead of two utilitarian shortcodes.

## §10 References

| Reference | Purpose |
|-----------|---------|
| Live: `https://www.nimrod.bio/` | Market index landing |
| Live: `https://www.nimrod.bio/crop-book/` | Crop book SPA |
| Repo (host): `organic_market_agent/publisher/templates/` | Market report HTML templates |
| Repo (host): `organic_market_agent/crop_book/publisher/` | Crop book SPA source |
| Governance: `_aos/governance/team_35.md` | Your contract |
| Governance: `_aos/governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` §1 (Track 6 — CONTENT) | Your gate model |
| Parallel WP: `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-A/HANDOFF_CONTEXT_v1.0.0.md` | Data enrichment context (informational; your design must accommodate richer data) |
| Crop book LOD400 spec (LOD500_LOCKED): `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` | Current production architecture for crop book |
| Project context: `_aos/context/PROJECT_CONTEXT.md` | Project + product background |

---

*Handoff package prepared 2026-05-23 by team_100 (smallfarmsagents).*
*Authorization: team_00 in-session 2026-05-23.*
*Track: CONTENT (ADR044). Gate model: PIPELINE_FEEDER (no L-GATE_B/V).*
