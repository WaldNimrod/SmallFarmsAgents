# SFA Design Handoff — WP-B Implementation Package

> **Package id:** `SFA-S003-P002-WP-UI-handoff-v1.2.0`
> **From:** team_35 (design — Claude Sonnet 4.6) · 2026-05-26
> **For:** **team_100 first** (roadmap registration + routing), then team_110 (spec authoring), then sub-agent builder
> **Mandate parent:** new WP `SFA-S003-P002-WP-UI` — standalone Flask Blueprint at `sfa.nimrod.bio`
> **Status:** READY FOR TEAM_100 ROUTING
>
> ⚠ **v1.2.0 correction:** the system is **NOT WordPress**. It's a standalone
> Flask Blueprint inside the existing `organic_market_agent` codebase, served
> at `sfa.nimrod.bio` (no WP chrome). Discard v1.0.0 (WP-template) and v1.1.0
> (Flask but mis-routed to team_110). v1.2.0 is the correct package — team_100
> registers the WP and routes to team_110.

---

## What's in this package

```
_handoff/
├── README.md                          ← you are here
├── HANDOFF_LOD300.md                  Architecture, mapping to existing shortcodes,
│                                       open questions, acceptance criteria
├── DESIGN_TOKENS.md                   Canonical color, type, spacing, shadow tokens
│                                       — copy verbatim into CSS variables
├── COMPONENTS.md                      Component catalog with DOM/CSS for each
│                                       (shell, badges, cards, strips, etc.)
├── TEMPLATES.md                       Page-level templates + routing map
├── MODULES_REGISTRY.yaml              SOURCE OF TRUTH for all modules (8 today,
│                                       extensible). Mirror as PHP array.
├── IMPLEMENTATION_PLAN.md             Step-by-step build plan for Claude Code
├── team_110_activation_prompt.md      Drop this into a fresh team_110 session
│                                       to kick off LOD400 authoring
└── design/                            Live HTML design canvas (run locally,
                                        screenshot, comment, iterate)
    ├── index.html                     Entry — open in browser
    ├── *.jsx, *.css                   Source files (React + Babel inline, no build step)
    └── (vendored React, image-slot, etc.)
```

## How to use

### As team_100 (roadmap registrar + router) — START HERE

1. Open `team_100_activation_prompt.md` — that's your mandate.
2. Read this README + `HANDOFF_LOD300.md` for context.
3. Register `SFA-S003-P002-WP-UI` in `_aos/roadmap.yaml` (Iron Rule #4).
4. File handoff MSG to team_110 + copy `team_110_activation_prompt.md` into
   `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/ACTIVATION_PROMPT.md`.
5. File advisory request to team_00 for the 4 strategic open questions.
6. End session — do NOT start LOD200 authoring.

### As team_110 (spec author — after team_100 routes)

1. Read `team_110_activation_prompt.md` — your mandate.
2. Read `HANDOFF_LOD300.md` end to end.
3. Open `design/index.html` in a browser. Pan/zoom. Every artboard is
   labeled with `data-screen-label` for reference in your spec.
4. Read `DESIGN_TOKENS.md`, `COMPONENTS.md`, `TEMPLATES.md`, `MODULES_REGISTRY.yaml`.
5. Author `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD200_spec.md`
   and `LOD400_spec.md`.
6. Close the 8 open questions in `HANDOFF_LOD300.md §6` (team_00 advisory
   already filed by team_100 for the strategic ones).
7. GCR analysis — identify any locked-file impact. File GCR via team_100 if needed.

### As the builder (sub-agent — after team_110 locks LOD400)

1. Read `IMPLEMENTATION_PLAN.md` — step-by-step.
2. Copy CSS from `design/` to `organic_market_agent/sfa_app/static/`.
3. Build per LOD400 spec; design is visual ground truth for ambiguities.

---

## Visual contract — the 30-second pitch

- **Brand DNA:** Nimrod.bio (warm cream paper, Frank Ruhl Libre headings,
  hand-drawn underline accents, three-world palette: leaf/tomato/soil).
- **Voice:** "כלים גדולים לחוות קטנות" / "קטן זה יפה, לאט זה שפוי."
- **Standalone:** drop the nimrod.bio site chrome (no Astra header/footer,
  no Elementor mega-sections). Sits as its own page-template inside the same
  WordPress install.
- **Modular:** the system is an **app** — Hub home lists 8 modules, each linkable.
- **Three tiers:** Community (open) / Advanced (paid) / Tailored (custom build).
- **Mobile-first.** Desktop is an enhancement (sidebar accordion + main).
- **Community everywhere.** Every screen surfaces a way to contribute, correct, or suggest.
- **Disclaimers explicit.** The market price index leads with "what / from / why / NOT" — it's primarily a community marketing tool.

---

## Package version

- `v1.0.0` — initial delivery, WordPress page-template (incorrect). **DEPRECATED.**
- `v1.1.0` — Flask architecture, routed to team_110 directly (skipped team_100). **DEPRECATED.**
- `v1.2.0` — current. Flask Blueprint, routed to **team_100** for roadmap registration + downstream routing to team_110. WP id `SFA-S003-P002-WP-UI`.
