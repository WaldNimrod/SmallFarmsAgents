# DESIGN MANDATE — WP-CB-UI-WI7 (FIDELITY WI-7 completions) — team_100 → team_35 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 (Chief Architect) · **To:** team_35 (Design) · **Routed by:** team_00
**WP:** SFA-S003-P004-WP-CB-UI-WI7 · **Design SSoT:** Board-A (crop+calc) / Board-B (hub/market/…) — paths in `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md` frontmatter `design_ssot`.

## ⚠ Capability note (team_00 ruling)
team_35 delivers **TEXT / SPEC decisions only**. Do **NOT** attempt screenshots or visual-vs-live comparison — that capability belongs to **team_50** (who will visually verify the implemented result on the live site after build). Your output is the authoritative design DECISIONS that team_10 implements.

## Context
WP-CB-UI-FIDELITY is LOD500_LOCKED and live (sfa.nimrod.bio @ acca9b2). Its L-GATE_V left four design questions (WI-7) for team_35 authority + a few INFO items. team_100 shipped sensible interim defaults; you confirm or refine.

## Decisions requested — deliver a `DESIGN_DECISIONS` artifact with each answered

- **Q2 — Market category chip wording.** Current live Hebrew labels (FieldRegistry `ENUM_LABELS['category']`):
  `root_vegetables→ירקות שורש · leafy_greens→ירוקי עלים · fruits→פירות · fruiting_vegetables→ירקות פרי · cucurbits→דלועיים · brassicas→כרוביים · alliums→בצליים` plus interim defaults `legumes_fresh→קטניות טריות · eggs→ביצים · baskets→סלים`. **Confirm or correct each** vs Board-B voice (final Hebrew string per key).

- **Q3 — Yield / nutrient-removal area unit.** `kg_per_ha`-class fields currently display **`ק״ג/הקטר`** (hectare) — chosen to avoid a silent 10× error. The Israeli small-farm audience works in **dunam**. **Decide the display unit** (ק״ג/דונם vs ק״ג/הקטר). ⚠ **Data-basis dependency:** the *stored* value's basis (per-dunam vs per-hectare) must be confirmed by team_100/data before any unit relabel — flag this in your decision; do NOT assume a 10× conversion.

- **Q4 — Leading-question set + semantics.** `/crop-book/questions` currently shows 3 data-backed questions: `מה מתאים לקיץ?`/`מה זורעים לחורף?` (→ season filter via `sowing_months ∪ transplant_months`) + `מה גדל מהר?` (→ `dtm_max=60`). **Design the final set** (which questions, each backed by data we actually have — months / DTM / family / etc.) and **define the "מתאים לקיץ" semantics**: does it mean *sown in* the season's months (current behavior) or *grown/harvested in* the season? Give the question list + each one's intended filter + the Hebrew copy + sub-label.

- **Q5 — English mono eyebrows.** Hub tiles / audience cards carry English mono eyebrows (CALC, MARKET, CROP-BOOK, FARMER, GARDENER, FIELD-LOG, planner). team_00 reads some as "English menus." **Decide per element:** Hebraize / soften / keep-as-decorative (and the replacement Hebrew strings where Hebraized). Board-B intent governs.

## Deliverable
`_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-WI7/DESIGN_DECISIONS_v1.0.0.md` — Q2-Q5 answered with exact strings/tokens/rules team_10 can implement verbatim. Notify team_100. **No visual QA** — team_50 verifies the built result.

## Then (team_100 sequences)
team_100 → team_10 BUILD (your decisions + the 2 INFO cleanups) → team_99 deploy → **team_50 VISUAL QA** (CDP screenshot-vs-Board on live) → team_100 records.
