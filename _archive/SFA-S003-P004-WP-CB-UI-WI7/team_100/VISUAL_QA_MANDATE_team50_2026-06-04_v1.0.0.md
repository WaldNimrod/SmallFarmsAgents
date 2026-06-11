# VISUAL QA MANDATE — WP-CB-UI-WI7 — team_100 → team_50 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 · **To:** team_50 (QA) · **Routed by:** team_00
**Precondition:** team_10 build of the WI-7 decisions + INFO cleanups is **deployed live** (team_99 DEPLOY_REPORT) — run this only after the deploy report exists; cache-bust to the served `?v=`.

## Why team_50 (not team_35)
Per team_00: team_35 (design) **cannot take screenshots or do visual comparison** — they deliver design decisions only. **team_50 owns the visual screenshot-vs-Board verification.** Use the dependency-free CDP harness (`_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs`, Node 18+) — **never curl** for layout (curl can't see the rendered box model). Production QA: no cert-bypass.

## Scope — verify the WI-7 changes on LIVE sfa.nimrod.bio vs Board-A/B (1440 + 375)
- **Q2 category chips** (`/market/`): the chip Hebrew labels match team_35's `DESIGN_DECISIONS` exactly; no raw English keys; renders cleanly.
- **Q3 yield unit** (crop/variety pages where a yield/removal value shows): the unit string matches the decision (ק״ג/דונם or ק״ג/הקטר); no English unit token.
- **Q4 leading-questions** (`/crop-book/questions` + the entry-card): the question set, copy, and sub-labels match the design; **each question link lands on a non-empty, correct result set** (click-through via CDP); the entry-card count is truthful.
- **Q5 eyebrows** (hub `/` tiles + audience cards): per-element matches the decision (Hebraized/softened/kept); no stray English "menu" reads where the decision said Hebraize.
- **INFO cleanups:** the dead `/crop-book/table?category=summer` URL no longer returns a 0-result page (removed or redirected); no visible regression on the calc page.
- **Regression guard:** the FIDELITY result still holds — 70 crops render watercolor art, cards 168px, crop page centered, no 375 overflow.

## Deliverable
`_COMMUNICATION/team_50/SFA-S003-P004-WP-CB-UI-WI7/VISUAL_QA_REPORT_v1.0.0.md` — per-item PASS/FAIL with screenshot evidence + a GO / GO-WITH-FIXES / NO-GO. Notify team_100. (This is a quality verification, NOT the constitutional L-GATE_V — that gate already PASSED at FIDELITY close; this confirms the WI-7 polish.)
