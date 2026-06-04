# DISPATCH — Team 80 Competitive-Intelligence Prompt (multi-engine)

**WP:** SFA-S004-P001-WP002 · **Date:** 2026-06-04 · **Author:** Team 100
**Purpose:** Self-contained CI prompt to paste into multiple web LLM engines (ChatGPT, Gemini, Claude.ai, Perplexity) in parallel. Team 100 aggregates the returned reports together with the parallel internal sub-agent dossiers.
**Method note:** Legal, public-source competitive intelligence only (sites, docs, pricing, trials, public reviews). No scraping of gated/private data.

---

## THE PROMPT (copy everything below the line)

---

**ROLE:** You are a senior product & competitive-intelligence analyst specializing in agritech / farm-management software.

**CONTEXT (read fully — you have no access to our internal files; everything you need is here):**
We are building "SFA" (working name): a **Hebrew-first, RTL "operating system for the small farm"** for the **Israeli** market. The architecture is decided. It is an agronomic + economic **engine**:
- (a) a crop knowledge base (~66 crops / ~368 varieties under a 13-topic agronomic taxonomy),
- (b) **14 planning calculators** (seed quantity to buy, transplants needed, nursery trays/date, sowing-date back-calc, harvest window, succession schedule, target yield for area, expected yield, expected revenue, plant population, frost window, fertilizer/compost, crop profit comparison, seed/input cost),
- (c) an **Israeli market price index**,
all wrapped **HEADLESS** over the open-source platform **farmOS** (we build our own Hebrew/RTL UI; farmOS is the operational backend for records/tasks).

**Audience:** small **commercial market gardeners** (JM Fortier / bio-intensive style) as the paying core; **home/private growers** as a free, brand-building community.
**North star:** *"the page every grower and farm worker opens in the morning to know what to do"* — end-to-end across 5 pillars: **Plan → Execute (field tasks) → Sell → Relate (CRM/customers) → Improve (data loop).** Monetization: **Freemium**.

We are **not** copying anyone. We are mapping the landscape to: (1) enrich our data schema, (2) find **white space** nobody serves, (3) benchmark pricing, (4) learn UX patterns and avoid known pain points.

**TASK:** Produce a rigorous competitive-intelligence report on the products below. Use ONLY public, legal sources: official sites, docs, pricing pages, free trials/demos, app stores, and **user reviews/complaints** (G2, Capterra, GetApp, Trustpilot, Reddit, Facebook groups, YouTube demos/reviews, app-store reviews). Be concrete, **cite URLs**, and clearly separate **FACT** (sourced) from **INFERENCE** (your reasoning). Flag anything you cannot verify.

**COMPETITORS:**
- Tend (tend.com)
- Seedtime (seedtime.us)
- Layout / The Market Gardener Institute tools (themarketgardener.com)
- Farmbrite (farmbrite.com)
- AgriWebb (agriwebb.com)
- Croptracker (croptracker.com)
- Sales/CSA cluster: Local Line (localline.ca), Barn2Door (barn2door.com), Harvie (harvie.farm)
- Home-garden planners: GrowVeg (growveg.com), Planter (planter.garden), and comparable tools
- Benchmark re-look only: farmOS (farmos.org) and LiteFarm (litefarm.org)

**FOR EACH COMPETITOR, cover these 10 axes:**
1. **Data model / schema** — core entities (crops, varieties, beds/fields/zones, plantings, tasks, harvests, inventory, sales, customers); depth of crop/variety attributes; any custom-field capability.
2. **Feature set** — planning, calculators (seed/yield/succession/spacing), task mgmt, harvest/inventory, sales/orders, CRM, certification/compliance, reporting/analytics.
3. **Daily cockpit** — is there a "today / what to do now" dashboard? Role-based (manager vs worker)? Mobile/field use?
4. **Pricing & monetization** — exact tiers and price points, free vs paid, free trial, per-user vs flat, usage limits.
5. **Target audience & positioning** — who they sell to (hobby / market-garden / livestock / large-scale) and core marketing message.
6. **UX/UI** — modern vs dated; mobile/responsive/native app; offline; overall polish; notable flows.
7. **Weaknesses & user complaints** — ⭐ MOST IMPORTANT: recurring pain points, missing features, churn/cancellation reasons, support complaints. Quote reviewers and cite where.
8. **Tech & integrations** — stack if discoverable; public API/webhooks; Zapier; QuickBooks/accounting; marketplace integrations; openness to 3rd parties.
9. **Localization** — supported languages; **Hebrew? any RTL support at all?** (We expect none — confirm.)
10. **Economics link** — ⭐ do they connect **market prices / actual costs to planning** to tell a grower what is most **PROFITABLE** to grow? (Our key differentiator hypothesis — report whether anyone does this.)

**DELIVERABLES (in this exact order):**
- **A. Per-competitor dossier** — the 10 axes, concise but specific, with URLs.
- **B. SCHEMA-COMPARISON MATRIX** — table: rows = data entities/attributes encountered across all tools; columns = competitors; cells = has it / depth. Goal: the *union* of how the industry models farm data.
- **C. FEATURE & PRICING MATRIX** — table of key features + price tiers across competitors.
- **D. WHITE-SPACE ANALYSIS** — where is nobody (or almost nobody) playing? Especially: Hebrew/RTL/Israel; market-price→profit planning; the unified morning cockpit; small-commercial-market-garden depth.
- **E. TOP 10 UX/PRODUCT PAIN POINTS** across the category (from axis 7) to design AROUND.
- **F. RECOMMENDATIONS for SFA** — 8–12 bullets: what to adopt, what to differentiate, pricing guidance, and specific schema fields we may be missing.

**FORMAT:** Markdown. Tables for B and C. Cite URLs inline. Be dense and useful — no padding.

---

*(End of prompt.)*
