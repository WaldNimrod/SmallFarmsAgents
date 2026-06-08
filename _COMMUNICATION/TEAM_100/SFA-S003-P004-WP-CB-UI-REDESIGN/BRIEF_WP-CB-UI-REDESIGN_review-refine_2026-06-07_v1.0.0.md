# BRIEF — SFA-S003-P004-WP-CB-UI-REDESIGN — team_100 → team_35 — v1.0.0

**Date:** 2026-06-07
**Author:** team_100 (Chief Architect)
**WP:** SFA-S003-P004-WP-CB-UI-REDESIGN (proposed — REGISTER pending on roadmap)
**Type:** DESIGN_BRIEF
**Target LOD stage:** LOD300 (hi-fi) — **mode: design REVIEW + REFINEMENT of an existing mockup set** (not a from-scratch wireframe pass)
**Target delivery:** Step 1 (review) within this engagement; Step 2 (revised mockups) after team_00 discussion

---

## 1. Context

The SFA public UI (crop book + market + calculator) was judged "below criticism" by team_00 (unclear IA, weak information density, illegible sizing, CRM-like complexity for what is a simple knowledge site). team_100 + team_00 ran a redesign and produced a **complete hi-fi mockup set of 7 surfaces** on a LOCKED design system, with agreed principles (below). Before we write the executable spec and implement, we want a **fresh, critical design-review pass in the claude-design environment** — find what still fails, what hurts UX, what can be sharper — then, after discussion with team_00, deliver a refined version ready for implementation. The mockups are standalone HTML and render live in the sandbox.

## 2. Scope

```yaml
mode: "review_then_refine"   # critique first (for discussion), revise after
what_to_review_and_refine:
  - screen_id: home            # home.html — hub entry
    purpose: "entry → 3 tools → audiences → manifest → contribute"
  - screen_id: book_list       # book_list.html — crop index
    purpose: "decision-relevant crop cards + visible filters/sort"
  - screen_id: crop_card       # crop_card.html — the centerpiece
    purpose: "lifecycle spine + universal drill-down + knowledge ⓘ + cross-links"
  - screen_id: calc            # calc.html — 15-goal planning calculator
    purpose: "ASK builder + 5 result shapes + honest no-data + basket + region picker"
  - screen_id: market          # market.html — community price index
    purpose: "drill-down price cards + 28-day trend + book/calc cross-links"
  - screen_id: assumptions     # assumptions.html — base-parameters management
    purpose: "scalable assumptions editor (groups, search, used-in, defaults)"
  - screen_id: cropdata_entry  # cropdata_entry.html — internal guided classification (lower polish)
    purpose: "fast keyboard-driven crop data entry"
variant_count: 1   # this is refine-to-one, not breadth-first wireframes

out_of_scope:
  - "Production code / LOD400 executable spec (team_100 / team_200)."
  - "Inventing a NEW visual language — the design system is LOCKED (see §4)."
  - "New product features beyond the locked set (calc engine is owned by the parallel WP-CB-CALC)."
  - "Dark mode (deferred)."
```

## 3. Audience & environment

```yaml
target_user: "Two audiences served by ONE interface: (a) the home/amateur gardener — curious, non-professional; (b) the local market farmer — needs data, depth, detail. Per team_00 decision the page is NOT split by an audience toggle; instead a universal drill-down (closed = key data for everyone, open = depth) serves both."
device: "mobile-first (the app shipped under WP-CB-MOBILE); must also be excellent desktop. Verify 375px and ~1200px."
input_mode: "touch + pointer + keyboard"
language: "HE"
rtl: true
dark_mode: "deferred — not this pass"
accessibility: "Readability is a first-class concern (illegible sizing was a core complaint): font baseline, line-length, contrast on the white-green palette, tap-target size, focus states, RTL correctness (no bidi breakage on numbers/units/dates)."
```

## 4. Design language (HARD INPUT — do not invent)

```yaml
design_system: "mock.css (provided) — mirrors the LOCKED nimrod.bio Design System v3 (tokens.css). Treat as canon."
tone: "warm, editorial, community knowledge-brand — NOT a CRM / dashboard. Generous whitespace, few-but-rich, not many-stripes-little-info."
brand_tokens_to_respect:
  - "Palette: white-green paper (--gj-paper #f8fbf8 / --gj-ink / --gj-leaf / --gj-tomato / --gj-sun) + provenance accents."
  - "Type: Frank Ruhl Libre (headings, serif) + Assistant (body) + JetBrains Mono (mono). No new families."
  - "Watercolor crop illustrations (wc/*.png) are the visual identity — never emoji, never invented art."
  - "ONE shell container (--shell-max ~1100px) applied uniformly to header + body across ALL pages (the consistency fix)."
  - "Radii/shadow/spacing tokens from mock.css only."
rule: "No tokens outside mock.css without a DESIGN_SYSTEM_EXTENSION_REQUEST to team_100."
```

## 5. Content samples (real — already embedded in the mockups; render verbatim)

```yaml
samples:
  hero_crop: "עגבנייה · Solanum lycopersicum · משפחת הסולניים · 6 זנים"
  crop_card_spine: ["מתי לשתול (לוח שנה)", "איך לשתול (משתלה⇄שדה)", "טיפול לאורך העונה (השקיה/דישון/הגנה/חברה)", "יבול צפוי"]
  in_season_treatments: "נחושת מונעת לכימשון כל 7–10 ימים · שמן נים בדמדומים · חרס קאוליני · ≈4–6 ק״ג קומפוסט/מ״ר (זווית אורגנית)"
  calc_goals: "15 מטרות עם זמינות כנה (זמין/בקרוב/מודל-נפרד); 5 צורות-תוצאה: scalar / DATE / DATE RANGE / DATE LIST / RANKED LIST (+scalar+DATE)"
  market_products: "עגבנייה ₪9.40/ק״ג ▲4% · מלפפון ₪6.80 ▼2% · בצל (ישן · 9 ימים) — עם טווח/חציון/מקורות/גרף 28-יום"
  honest_no_data: "בטטה (ללא נתוני תאריך) → מצב 'אין עדיין נתון — לא ממציאים מספר · עזרו להשלים'"
```

## 6. States to cover (verify all render well)

```yaml
states_required:
  - "normal — content present"
  - "drill-down: closed (key data visible) AND open (depth) — the core interaction"
  - "honest no-data / coming-soon (calc goals, missing crop data) — never a fake number"
  - "market: fresh / aging / stale (greyed)"
  - "knowledge ⓘ: hover tooltip (L1) → modal 'ידע SFA' (L2)"
  - "mobile (375px) reflow of every screen"
not_required_this_pass: ["dark mode", "error/offline", "loading skeletons"]
```

## 7. Interactions

```yaml
primary_actions:
  - "drill-down expand/collapse per topic (crop card stages, market cards)"
  - "open knowledge modal from any field ⓘ"
  - "calc: pick goal → result shape changes; basket multi-select (#13); region picker (#11); live time-anchor"
  - "cross-link: crop ↔ market ↔ calc ↔ complementary content (nimrod.bio)"
  - "contribute CTA → tailored form (stub)"
navigation_model: "per-page; crop card has a sticky stage-nav; calc is a 4-step builder + result"
flow_description: "Universal pattern across the whole UI: general level visible, clear per-topic drill-down for depth. This replaces a separate farmer interface."
```

## 8. Tweak inventory (expose as live tweaks in the review prototype)

```yaml
tweaks:
  - "type_baseline (current / +1 step / +2 step) — to settle readability"
  - "density (compact / comfortable / spacious)"
  - "drilldown_default (key-only closed / first-open / all-open)"
  - "card_columns (auto / 2 / 3) for book_list + market"
  - "illustration_scale (S / M / L) in hero + cards"
  - "accent_usage (restrained / current / lively) for --gj-tomato/sun"
```

## 9. Open questions / known gaps

```yaml
open_questions:
  - id: Q-A
    question: "book_list cards: keep the current static card, or adopt the SAME drill-down pattern (closed=key, open=depth) as crop_card / market for full consistency?"
    default_if_unanswered: "propose both in the review; recommend the consistent drill-down; let team_00 decide."
  - id: Q-B
    question: "Is the lifecycle spine (מתי→איך→טיפול→יבול) the right primary IA for the crop card, or should the review stress-test an alternative?"
    default_if_unanswered: "keep the spine; critique within it; flag only if a materially better IA emerges."
  - id: Q-C
    question: "Readability target: what minimum body/secondary font sizes for mobile + desktop? (current uses 17px body, smaller for secondary)."
    default_if_unanswered: "recommend a baseline in the review for team_00 sign-off."
  - id: Q-D
    question: "Knowledge-brand depth: how far to push the 'ידע SFA' modal (definition+formula+source+contribute) as a brand surface?"
    default_if_unanswered: "treat as a brand pillar; refine the modal; do not expand scope."
```

## 10. Delivery expectation

```yaml
engagement_shape: "TWO steps, with a team_00 discussion gate between them (team_00 directive)."
step_1_review:
  artifact: "REVIEW_RESPONSE (per lean-kit template) — a prioritized UX critique across all 7 screens."
  must_include:
    - "Per-screen findings: failures / problems / improvement opportunities, each with severity (blocker / major / minor / polish) and a concrete proposed fix."
    - "Cross-cutting findings (consistency, readability, RTL, mobile, hierarchy, accessibility, the honest-data ethos)."
    - "What is working and should be preserved (so refinement does not regress strengths)."
    - "Any DESIGN_SYSTEM_EXTENSION_REQUEST if a fix needs a token outside mock.css."
  purpose: "Basis for discussion with team_00 — do NOT mass-revise before that discussion."
step_2_refine:
  trigger: "After team_00 discusses the review and selects which findings to action."
  artifact: "HANDOFF package (per lean-kit template) — revised hi-fi mockups (HTML on mock.css) for the actioned items + screen-by-screen narrative + state notes + tweak inventory + assumptions log."
  purpose: "Implementation-ready design for team_100 to fold into the LOD400 + team_200 build."
sign_off: "Team 00 (at the discussion gate, and on the Step-2 handoff)."
revision_rounds_budgeted: 3
```
