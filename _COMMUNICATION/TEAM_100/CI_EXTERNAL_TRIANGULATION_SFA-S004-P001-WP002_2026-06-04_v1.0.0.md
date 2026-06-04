# CI External Triangulation — 2 web-engine reports × internal synthesis

**WP:** SFA-S004-P001-WP002 · **Date:** 2026-06-04 · **Author:** Team 100
**Sources merged:** Internal 8-agent synthesis (`CI_SYNTHESIS_8COMPETITORS_*`) + **Report 1 = Perplexity** + **Report 2 = Claude (web)** — both run from our DISPATCH prompt. Raw reports preserved: `SFA-S004-CI-EXTERNAL/EXTERNAL_REPORT_{1_PERPLEXITY,2_CLAUDE_WEB}.md`.

## Verdict: strategy CONFIRMED — nothing overturned
Triple-source agreement (internal + 2 external) on the 3 core findings → now **very-high-confidence**:
1. **No market-price → plan → profit anywhere.** Both external matrices mark the market-price-index row a uniform ○ across all 13–14 tools. Revenue projection exists (Tend, Heirloom); true margin-ranking tied to a live price index does not exist anywhere. **SFA's #1 wedge — triple-confirmed.**
2. **Zero Hebrew / zero RTL anywhere.** Both external reports confirm every product is English-first (Local Line 7 EU langs, LiteFarm 8 langs — neither Hebrew/RTL); Local Line/Barn2Door/Harvie don't operate in Israel. **Moat — triple-confirmed.**
3. **No unified 5-pillar morning cockpit.** Both confirm planners stop at Plan+Execute; sales tools own Sell; nobody fuses Plan→Execute→Sell→Relate→Improve into one role-based screen. **Triple-confirmed.**

Also reinforced: all-in-one works (Farmbrite/Tend); Tend = closest all-in-one threat; Heirloom = closest philosophical sibling; freemium free-tier = table stakes.

## NEW info to merge into the SFA model
- **LiteFarm crop schema = deepest (D+):** 375 crop types, **8,000+ crop attributes**, embedded calculators (footprint, seed-required, yield) driven by planting method. → Add **LiteFarm crop-attribute model as a SECOND schema reference** alongside Tend + farmOS. (Both external reports rank LiteFarm crop-schema top-tier — richer than our internal pass credited.)
- **Local Line correction:** supports **7 languages** (EN/FR/ES/PL/HR/DE/SL) and charges **transaction fees ~0.5–2% on top of subscription + card fees** — i.e., NOT truly "no commission." Still no Hebrew/RTL; not in Israel.
- **"Soft schedules" UX pattern (high value):** auto-reforecast downstream tasks when one slips; let users mark "good enough" not "late." Directly fixes GrowVeg's "constantly behind / stressed" pain AND serves Nimrod's "field reporting must be simple + fast" priority. **Adopt.**
- **Israel-specific localization beyond translation:** regional seasonality (Negev vs Galilee), local pests, Jewish holidays, **Shabbat-friendly views**. Deepens the RTL moat.
- **Light CSA box module tied to harvest windows:** warn when predicted harvest < CSA commitment; use price index + yield to suggest share composition. Ties Sell↔Plan; complements stealing Harvie's preference-matching.
- **VegPlotter** added to home cluster (free + ~$30/yr) — confirms the home-planner pattern (no economics, no RTL).

## DIVERGENCES to verify (flagged — do not treat as settled)
1. **MGI / JM-Fortier tool identity:** Claude-web + internal = **Heirloom** (heirloom.ag, detailed dossier); Perplexity = **"Grounded Garden Planner" (free beta)** at themarketgardener.com. Possibly rebrand / codename / two distinct tools. **VERIFY.** Treat Heirloom as primary (richer evidence).
2. **Croptracker pricing:** internal + Claude-web ≈ **$5–5.99/mo per module**; Perplexity = **$27.50/mo per user, 10-user minimum**. Different models. **VERIFY.**
3. **Tend Ultimate:** $75/mo (tend.com) vs $104.30/mo (Capterra) vs ~$50/mo annual (FitGap). **VERIFY live.**
4. **Local Line "no commission"** marketing vs actual ~0.5–2% transaction fees (resolved above — fees do exist).

## Consolidated pricing benchmark (triangulated → feeds D1)
| Tool | Free | Entry paid | Top | Notes |
|---|---|---|---|---|
| Tend | ✓ | $30/mo Pro | $75–104 Ult · $400 Ent | Ultimate price conflict |
| Seedtime | ✓ | $7/mo (annual) | $14/mo | planner-only |
| Heirloom | 1-mo trial | undisclosed (JS-gated) | course bundles $2,250–3,950 | standalone price hidden |
| Farmbrite | 14-day trial | $29–39/mo | $95–109/mo | +acct-only $119/yr |
| AgriWebb | Hobby $0 | ~$125/mo | ~$400/mo | per-head (DSE) |
| Croptracker | varies | $5.99/mo/module **or** $27.50/user (10-min) | quote | ⚠ divergence |
| Local Line | trial | $79–99/mo | $199–399/mo | +0.5–2% txn fee |
| Barn2Door | none | $99–119/mo +$399 setup | quote | +2–3.9% merchant fee |
| GrowVeg | 30-day trial | ~$29/yr | — | data-hostage on cancel |
| Planter | ✓ | annual sub | $99 lifetime | bills in Israel (no Heb UI) |
| VegPlotter | ✓ basic | ~$30/yr | — | planner-only |
| farmOS / LiteFarm | OSS free | — | — | self-host |

**Pricing read (D1):** free tier = table stakes; commercial band ~**$25–40/mo equiv** (Tend Pro $30, Farmbrite $29–39); price **below Tend Pro** for Israeli incomes; **flat/transparent, no %-of-sales, no setup fees** (counters the category's #1 trust complaint). Meter on bed-count/planted-area.

## Net
- **D4 (competitive schema mapping): RESOLVED** — triple-source.
- **D1 (pricing): benchmark consolidated** — ready for a pricing decision.
- **No change** to platform decision (farmOS headless) or the vision. Everything reinforces it.
- **4 verification items** logged above (non-blocking; close opportunistically).
- Schema enrichment: add LiteFarm crop-attribute depth as a second reference; add per-bed economic attributes + price-time-series (already in our plan).

---

# Round 2 — +OpenAI +Gemini (4 external reports total, 2026-06-05)

Raw added: `SFA-S004-CI-EXTERNAL/EXTERNAL_REPORT_{3_OPENAI,4_GEMINI}.md`. **Quadruple-source** (internal + Perplexity + Claude-web + OpenAI + Gemini) → the 3 core findings now at **maximal confidence**, and all 4 Round-1 divergences RESOLVED.

## Round-1 divergences — RESOLVED
1. **MGI tool = Heirloom** (heirloom.ag) — confirmed by OpenAI + Gemini + Claude-web. (Perplexity's "Grounded Garden Planner beta" was imprecise.) **Heirloom standalone ≈ $475/yr** ($149/yr legacy upgrade), bundled in Crop Plan Accelerator **$699** / Masterclass $2,250–2,525 (Gemini).
2. **Croptracker = $27.50/user/mo, 10-user minimum ≈ $275/mo practical floor** (OpenAI + Perplexity). The "$5.99/module" (Gemini/Claude-web) is a teaser base. → **Croptracker is ENTERPRISE-priced, not cheap** — corrects the D1 benchmark.
3. **Tend Ultimate = $75/mo monthly / ~$50/mo billed annually**; Pro $30 / ~$20 annual. Reconciled.
4. **AgriWebb (current) = $30 / $39 / $55 per mo** + add-ons (Grazing $300/yr, PastureKey $1,000/yr) — lower than the old $45–400 figure (Gemini/OpenAI).
5. Local Line: 0% commission claim BUT processing fees scale by tier — confirmed (fees exist).

## NEW competitors surfaced — NOT in our 8-set (⚠ candidates for a Round-2 CI WP)
- **MarketGardenPlanner** (marketgardenplanner.com) — closest new **all-in-one**: beds/crops/schedule/auto-tasks/harvest/customers/orders/payments + expected-vs-actual. **Closest to our 5-pillar loop of anything seen.**
- **MyGardenPlanner** (mygardenplanner.ca) — AI biointensive; Home $5/mo, **Market Gardener $19/mo ($179/yr)**.
- **VeggieCropper** (veggiecropper.com) — farmer-built; free crop planning; crew/manager accounts.
- **Solara** (solara.ag) — market-garden; succession + revenue tracking.
- (Old Farmer's Almanac Garden Planner = GrowVeg engine.)
**None has Hebrew/RTL or a live market-price index** (wedge + moat hold), but these are closer market-garden competitors than several we studied → warrant a focused Round-2 scan.

## NEW for the build (from OpenAI + Gemini)
- **Price-index data source identified:** Israeli **Wholesale Market Price Index (Ministry of Agriculture)** — concrete feed for the #1 wedge (Gemini).
- **Schema field:** `water_source_salinity_index` (Israel irrigation/salinity) + `rtl_metadata`, `israeli_market_id`, `nursery_tray_cell_count` (Gemini).
- **LiteFarm crop schema re-confirmed** as the best open-source crop-management reference (crop type → varietal → crop-management-plan; estimated yield + estimated value/yield + real-time P/L). Use as the 2nd schema reference (alongside Tend + farmOS).
- Pain points reinforced & sharpened: Tend support-abandonment + hard-to-cancel; GrowVeg data-loss-on-cancel → SFA principles: **downgrade-not-delete, offline-first, transparent self-cancel, no setup fees, standard 2.9% processing**.
- Harvie: bankruptcy/shutdown confirmed (OpenAI cites bankruptcy-protection filing) — reinforces the lock-in / build-don't-integrate lesson.

## Net (4-source)
No change to vision or platform (farmOS headless) — **wedge & moat reinforced at maximal confidence.** D4 fully resolved. D1: Croptracker re-priced to enterprise (~$275/mo), Heirloom standalone $475/yr; SFA commercial-tier target band still **~$25–40/mo** (Tend Pro $30, Farmbrite $29, MyGardenPlanner-MG $19). **One new finding requiring a decision: ~4 additional market-garden tools (esp. MarketGardenPlanner) to scan in a Round-2 CI** — recommend a small follow-up WP.
