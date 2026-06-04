# CI Round 2 — Synthesis (newly-surfaced market-garden tools)

**WP:** SFA-S004-P001-WP004 · **Date:** 2026-06-05 · **Author:** Team 100
**Targets:** MarketGardenPlanner, MyGardenPlanner, VeggieCropper, Solara (4 background agents; dossiers in session transcript). These were surfaced by WP002's external triangulation as closer to SFA's product than several originally studied.

## 0. Verdict: the hypothesis HELD — wedge & moat reinforced
**None of the 4 closes the market-price → plan → profit loop, and none has Hebrew/RTL.** Even the two most ambitious leave the wedge open:
- **MarketGardenPlanner** — its market-intelligence feature ("Market Research Insights") is **vaporware ("coming soon")**; prices self-entered.
- **Solara** — bolts on NPV/IRR/Monte-Carlo *language* but optimizes on the farmer's **own past sales**, no external price feed (and is **likely a synthetic/demo site**, not a real company).
→ The #1 wedge (Israeli market-price → forward profit planning) and the RTL moat are confirmed open against **every** competitor now examined (8 + 4 = 12, plus farmOS/LiteFarm).

## 1. Per-tool one-liners
| Tool | What it is | Closest threat? | Key gap |
|---|---|---|---|
| **MarketGardenPlanner** | Earliest-stage real all-in-one; connected Plan→Execute→Sell→Improve loop, public order forms, Square | **Highest feature-overlap** with our 5-pillar loop | No economics engine (vaporware); zero traction; Laravel closed monolith; EN/ES; solopreneur |
| **VeggieCropper** | Farmer-built agronomic timing engine + crew/manager accounts | Strong on Plan+Execute craft | **Killed its free tier in 2026** (unsustainable solo); no economics loop; bus-factor=1; EN only |
| **Solara** | Polished "university-grade science" market-garden concept | Best *messaging*, not real | **Likely synthetic/demo** (Circadian SDK, emoji founders, no footprint); self-entered prices; EN/US |
| **MyGardenPlanner** | Hobby planner with market-garden veneer; great SEO funnel | Low (planning-only) | "Market Gardener" tier = just more beds; no Sell/Relate/economics; crop-level (no varieties); Canada/EN |

**Common to all 4:** zero independent review footprint (tiny/early/unproven), closed (no API/export), no native offline mobile of note, English-only, no economics loop. The market-garden-software segment is **fragmented, shallow, and un-moated.**

## 2. MATCH (table stakes proven across these tools)
- **Backward-from-harvest scheduling with bed-turnover** (MyGardenPlanner, VeggieCropper) — clean, trusted planning UX.
- **The connected loop + public order forms + availability sheets** (MarketGardenPlanner) — proves small MGs adopt order tooling tied to the plan.
- **Crew/manager accounts with task autonomy** (VeggieCropper) — operationally mature; real in-field crew adoption.
- **CSA box-first backward planning + per-item member-satisfaction** (Solara) — smart Sell/Relate UX idea.
- **Agronomic timing chain** (VeggieCropper): `weeks-before-TP / seeds-per-cell / weeks-to-pot-up / weeks-of-harvest / planting-% per variety` + projection→planting = parity baseline for our 14 calculators.

## 3. BEAT (open lanes confirmed across all 12 competitors)
1. **Market-price → forward profit loop** — universal gap. SFA's Israeli price index → per-bed/per-crop margin → re-plan = category-defining. **Make it the hero, not a feature.**
2. **Hebrew-first / RTL + Israeli climate/market** — universal gap; structural moat none can follow cheaply.
3. **Curated agronomic KB + 14 calculators** — rivals rely on user "custom attributes" / crop-level only; no science baked in.
4. **Openness + durability** — all 4 are closed, no API/export, with real bus-factor risk (solo/synthetic). farmOS-headless + GPL + export = the anti-thesis.
5. **Commercial tier = capability, not quantity** — MyGardenPlanner's "Market Gardener" tier is just "more beds." SFA's paid tier must mean **Sell + Relate + finance**, so the paid line is *capability*.

## 4. Pricing read (refines D1)
- Low-end planners: MarketGardenPlanner **$29.99/yr** (~$2.50/mo!), MyGardenPlanner Free/$5/$19-mo (bed-count gated).
- Serious all-in-one: VeggieCropper **$50 CAD/mo flat**; Solara Home $0 / $29 / **$99/mo** (synthetic anchor).
- Willingness-to-pay for a *serious* MG ≈ **$50–99/mo** (Solara/VeggieCropper/Tend Ultimate); planners cluster **$2.50–19/mo**.
- SFA target band **~$25–40/mo** sits sensibly between; **commercial value must justify it via the economics engine** (the thing the cheap planners can't do).

## 5. ⭐ Strategic insights (new)
- **Free-tier sustainability (validates our architecture):** VeggieCropper's **unlimited-free-planning was financially unsustainable for a solo operator and was killed in 2026.** → SFA's free home-grower tier MUST be **cost-bounded by design** (stateless Tier A / rented-sandbox / no per-user crew cost) so it can't bleed the business. Keep a genuinely free home tier they abandoned, monetize the commercial tier.
- **Steal the programmatic-SEO playbook:** MyGardenPlanner's per-province/per-city planting calendars + per-crop guides + PDF lead-magnet = cheap, scalable top-of-funnel. Replicate for **Israeli regions/climate zones in Hebrew** — directly feeds the free brand-front (Nimrod's audience/funnel).
- **Steal messaging (in Hebrew):** Solara's concrete pain-list opener + "university-grade ag science, democratized" (maps to our KB+farmOS); pair with our open/GPL posture as the *anti-Solara* (real, inspectable, yours).

## 6. Net
No change to vision/platform. Wedge + moat now confirmed against **all 12 competitors + 2 OSS benchmarks**. New actionable adds: programmatic-SEO acquisition engine (Hebrew/Israel), cost-bounded free tier (architecturally already our plan), commercial-tier = capability-not-quantity, CSA box-first backward planning for Sell/Relate. **D4 fully closed.** Recommend: no further CI rounds needed — proceed to Phase 0 technical design.
