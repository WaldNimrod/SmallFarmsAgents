---
id: SFA-S003-P004-WP-CB-CALC-QA-LIVE
mandate_from: team_100 (Chief Architect — builder engine: Claude Opus)
mandate_to: team_50 (visual / functional QA — cross-engine, non-Claude per IR#1/#5)
re: LIVE PRODUCTION QA of the calculator (deployed) — post-deploy verification
follows: SFA-S003-P004-WP-CB-CALC-QA-FULL (branch QA PASS v2.0.0)
created: 2026-06-07
status: OPEN — team_50 action requested on PRODUCTION
---

# MANDATE — team_50 LIVE QA: WP-CB-CALC (production)

WP-CB-CALC (14/15 goals) is **deployed to production**. The prior FULL QA (PASS v2) ran locally on the branch; **this mandate is the production re-verify** on `https://sfa.nimrod.bio/calc/`. Builder = Claude → verdict must be **non-Claude** (IR#1/IR#5).

## Deploy under test
- Live: `https://sfa.nimrod.bio/calc/` · assets `?v=1780865050` · main @ `2f31d89`.
- team_99 deploy + curl smoke already PASSED (page 200, markers present, `frost_regions.json` 200, `SFA_DATEC` live, `רווח גולמי` absent).

## Scope (in-browser, production)
1. Re-confirm the FULL-QA checklist on the **live** page: 15-goal grid · "15 מטרות" · #13 "השוואת גידולים" · the 14 live goals compute · honest states (bare crop → nodata; water → "בפיתוח") · session/export/assumptions.
2. **F-01 live:** #9 leads with ק״ג; ₪ secondary ("מדד השוק · להמחשה").
3. The 5 newly-live goals on production: succession (date list) · seed_cost (₪ / honest — when no price) · frost (region picker; coastal=open-window note; an inland region=range) · nursery (trays + tray-sow date) · compare (basket 2–6 → rank by ק״ג/מ׳).
4. **Run `qa_probe.mjs` against `/calc/` specifically** (the team_99 probe defaulted to `/` — please target the calc path) on mobile (375) + desktop (1440): no horizontal overflow, no forbidden text, **0 console errors**.

## Caveats (unchanged, non-blocking)
- Result shapes render as **plain formatted text** — `mock.css` styled cards arrive with the UI-redesign CSS pass (F-02/F-03/F-04 deferred). QA **function**, not final styling.

## Verdict
Non-Claude L-GATE QA verdict (PASS / findings) for **production** via `_COMMUNICATION/team_100/`. This is the production sign-off feeding team_190's final validation.
