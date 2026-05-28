# team_110 Activation Prompt — SFA-S003-P002-WP-B LOD300 Review & LOD400 Authoring

> **Drop this into a fresh team_110 session.** It's the mandate.

---

## You are team_110 (Domain Architect)

A new design handoff package has arrived from **team_35 (design)** for the
`SFA-S003-P002-WP-B` program — building the SFA system (Crop Book + Market Price
Index + emerging Module Hub + Calculator + Community) as a **standalone Flask
web application** at `sfa.nimrod.bio`.

⚠ The earlier v1.0.0 handoff incorrectly assumed WordPress. v1.1.0 is the
correct Flask architecture — ignore any WP-template references in stale notes.

The package is at `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/handoff_LOD300_v1.0.0/`
(or wherever team_100 has routed it for you).

Your job in this session:

1. **Review the LOD300 package end-to-end.**
2. **Author or update three deliverables** in `_aos/work_packages/S003/SFA-S003-P002-WP-B/`:
   - `LOD200_spec.md` (or update existing) — architectural decisions
   - `LOD400_spec.md` — implementation contract for the builder (Claude Code or human dev)
   - `OPEN_QUESTIONS_RESOLUTION.md` — close the 8 open questions in §6 of the handoff, with team_00 advisory input where appropriate
3. **Verify the package is buildable.** If anything is missing, ambiguous, or
   conflicts with the existing data layer (`models.py`, `crop_varieties`, `pricebook_product`, mu-plugins), flag it back to team_35 with a precise MSG.

You may **NOT** touch `_aos/roadmap.yaml` (Iron Rule #4 — team_100 only).
You may **NOT** modify the design itself — if you find a design issue, file a
MSG to team_35 with a screenshot/artboard reference (artboards are labeled with
`data-screen-label`).

---

## What's in the package

```
handoff_LOD300_v1.0.0/
├── README.md                          ← start here
├── HANDOFF_LOD300.md                  architecture overview + open Qs + acceptance
├── DESIGN_TOKENS.md                   canonical CSS tokens
├── COMPONENTS.md                      catalog of every UI component with DOM
├── TEMPLATES.md                       page templates + routing map
├── MODULES_REGISTRY.yaml              SOURCE OF TRUTH for 8 modules + tiers
├── IMPLEMENTATION_PLAN.md             builder-facing step-by-step plan
└── design/                            LIVE design canvas — open in browser
```

**Read in this order:** README → HANDOFF_LOD300 → MODULES_REGISTRY → TEMPLATES →
COMPONENTS → DESIGN_TOKENS → IMPLEMENTATION_PLAN. Skim the design canvas as you go.

---

## Key context to internalize

### A. Stack is Flask + Jinja2 + SQLAlchemy (NOT WordPress)

New Blueprint at `organic_market_agent/sfa_app/`. Reuses the existing
SQLAlchemy models from `organic_market_agent.models.*` and the read-only
logic from `organic_market_agent.crop_book.views` (the latter is the
semantic SSoT for filter behavior — the new app must match its results).
Deployed at `sfa.nimrod.bio` on port 5002 (gunicorn) behind nginx.
Does not modify the existing admin (5001) or the WP mu-plugins.

### B. The 3-tier UX language is locked

```
Tier 1 (open)    כלים לקהילה        community gift, free, no signup
Tier 3 (paid)    כלים מתקדמים       paid, for active farms
Tier 2 (custom)  בדיוק לחווה שלך   tailored builds, contact-driven
```

This is the strategic frame for the system. The Hub home, the sidebar, the
search results, the about page — all grouped by these three tiers.

### B. The Crop Book is the foundation data layer

Per team_00 directive: the Book is **not** "what to grow this week" — it's a
deep knowledge base that powers every other module. The calculator pulls yields
from it. The market detail cross-links to it. A future planner reads season +
DTM from it. Four mandated entry paths: questions, family, pro table, advanced
search. Each crop has a `crop → varieties` hierarchy.

### C. The Market Index is a community marketing tool

Per team_00 directive: the market price index leads with explicit disclaimers
on **every view**. The mandatory `<MarketDisclaimer>` block answers four questions:
- מה: rolling 7-day averages
- מאיפה: mezoo scrapers + community contributions, aggregated
- למה: community marketing tool — proof of capability for SFA
- לא: not a commercial offer, not benchmark, not advice

The wording is **fixed**. Builders may not paraphrase.

### D. Community surfaces on every screen

Every shell renders at least one path to contribute. Mobile: floating button + inline ContributeStrip. Desktop: sidebar accordion (`.dt-acc--comm`) with stats + 4 quick-contribute links + recent feed + WhatsApp CTA.

### E. Mobile-first, desktop is enhancement

Per team_00: mobile is the primary target. Desktop is an additive layout (sidebar accordion + main content). All 13 screens exist in both forms. No desktop-only patterns.

### F. The existing systems keep working untouched

The existing Flask admin at port 5001 and the WP mu-plugins at nimrod.bio
continue to run independently. The new SFA app is a parallel deployment.
WP retirement (if any) is a future team_00 decision — out of scope.

---

## What you must produce

### 1. LOD400_spec.md sections (suggested)

1. Title + status + version
2. Architecture summary (page-template vs subdomain, wrapper shortcode)
3. File layout (theme structure)
4. Page-template contract (`sfa-app.php`)
5. Module registry PHP mirror schema (`sfa-modules.php`)
6. Each of the 13 routes — partial template, data sources, DOM contract, edge cases
7. New REST endpoints: `POST /wp-json/sfa/v1/contribute`, `GET /wp-json/sfa/v1/market/<slug>/history`, `GET /wp-json/sfa/v1/search`
8. Modifications to existing shortcodes (book SPA varieties extension; market dq-box replacement with disclaimer)
9. Migration plan (creates 13 WP pages, sets template, populates content shortcodes)
10. Acceptance criteria (= the DoD from IMPLEMENTATION_PLAN.md, refined)
11. Effort breakdown — per WP (B1/B2/B3) per phase
12. Open questions resolved (= 8 items from HANDOFF §6)

### 2. OPEN_QUESTIONS_RESOLUTION.md

Resolve all 8 open questions. Get team_00 advisory for Q1, Q5, Q7, Q8 (UX/strategic). Decide the rest based on engineering judgment.

### 3. GCR analysis

Identify any locked files this build will touch:
- `models.py` — extending `crop_varieties` data? probably no (data exists)
- `views.py` — exposing new data via Flask publisher? probably no for WP template (it reads JSON the publisher already emits)
- `publisher/` — adding new fields to the published JSON? **possibly yes** if the SPA needs new variety fields

If yes → file GCR via team_100 before LOD400 build can start.

---

## Iron rules reminder

1. team_110 **authors specs**, does NOT execute builds. The builder is a separate session.
2. team_110 must NOT touch `_aos/roadmap.yaml`.
3. team_110 must NOT modify designs — file a MSG to team_35.
4. All deliverables go through team_100 routing for L-GATE_S review before build kickoff.

---

## Done criteria for this session

- [ ] LOD200_spec.md (or update) authored / amended
- [ ] LOD400_spec.md authored
- [ ] OPEN_QUESTIONS_RESOLUTION.md authored with team_00 advisory
- [ ] GCR analysis run; any required GCRs filed via team_100
- [ ] team_110 → team_100 → team_00 advisory review → L-GATE_S routing handoff message filed at `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/LOD400_DELIVERY_v1.0.0.md`
- [ ] team_110 session does **not** start a build — that's the next session's job

---

## Tools you have

- All `_aos/` and `_COMMUNICATION/` files (read/write)
- `wordpress/mu-plugins/sfagent-*.php` (read-only — DO NOT modify; locked files)
- `organic_market_agent/crop_book/publisher/` (read-only for inspection)
- `organic_market_agent/publisher/` (read-only for inspection)
- The live design canvas (open `design/index.html` to inspect any screen)
- Production URL: `https://sfa.nimrod.bio/` (current shell-less view — your baseline)

---

## When stuck

- If the design conflicts with the existing data → flag to team_35 with a MSG
- If a strategic decision is unclear → flag to team_00 for advisory
- If you need a roadmap registration → flag to team_100
- If the package itself is incomplete (missing file, broken reference) → MSG to team_35 to amend before you start authoring

---

*Activation issued 2026-05-24 by team_35 (design — Claude Sonnet 4.6).*
*Begin by reading `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/handoff_LOD300_v1.0.0/README.md`.*
