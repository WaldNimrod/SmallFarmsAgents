# Competitive Intelligence — Synthesis of 8 Competitor Studies

**WP:** SFA-S004-P001-WP002 · **Date:** 2026-06-04 · **Author:** Team 100
**Channel:** Internal — 8 parallel research sub-agents (Team 100). **Pending merge:** external multi-engine outputs (ChatGPT/Gemini/Claude.ai/Perplexity) via the DISPATCH prompt → triangulation in a follow-up pass.
**Source confidence:** Tend, Seedtime, Croptracker, AgriWebb, sales-cluster = direct-source high. Farmbrite + home-garden cluster = some pages search-synthesized (WebFetch throttled) → re-verify live prices/DB counts before quoting externally. The two headline findings (no market-price→plan loop; zero Hebrew/RTL) are **high-confidence, unanimous across all 8**.

---

## 0. The three universal findings (unanimous across all 8 competitors)

1. **Nobody closes the market-price → plan → profitability loop.** Every tool that touches economics — Tend, Farmbrite, AgriWebb, Croptracker, Local Line, Heirloom — does it **retrospectively** (your own books) or with **self-entered prices**. **None ingests an external market-price index** to answer, at planning time, *"what is most profitable to grow now?"* **Heirloom literally lists this on its public roadmap as unshipped** ("dynamic pricing recommendations from local market prices/demand"). → **SFA's sharpest, most defensible wedge.**
2. **Zero Hebrew / zero RTL — everywhere.** All 8 (plus farmOS/LiteFarm). Even $64M-funded AgriWebb and JM Fortier's Heirloom built no RTL; Farmbrite states explicitly that text direction "will not change." The only Israeli home-garden product found is a **printed paper calendar**. → Hebrew-first RTL + Israeli climate + Israeli market = **uncontested moat, not a feature.**
3. **The production↔sales loop is industry-wide open.** Sales tools (Local Line/Barn2Door/Harvie) never feed back to crop planning; planning tools (Seedtime/Heirloom/Tend) never pull real sales/demand. **The 5-pillar unified loop SFA is built to close is unbuilt across the category.**

**Three supporting findings:**
4. **The all-in-one model works** — Farmbrite proves 5-pillar breadth (crops+livestock+inventory+accounting+commerce) sells → **de-risks SFA's vision.**
5. **The brand→courses→software flywheel is proven and exactly mirrors Nimrod's model** — Heirloom/JM Fortier: book → authority → courses ($2,250–3,950, 4,000+ students) → community → software as the paid execution layer; the Masterclass *ends* with "a crop plan ready to execute in Heirloom." **But** they invite-gate the software, capping the funnel — SFA's free home-grower tier widens exactly that.
6. **Table stakes confirmed:** 14 planning calculators (Tend/Farmbrite/Seedtime/Heirloom all have planning math), **offline-first field capture** (AgriWebb/Farmbrite Scout Mode/Croptracker/Tend/Heirloom), and **owner/worker role split**. Offline-first is an architectural requirement that tensions with our headless-web → needs a **PWA/offline path**.

---

## 1. Competitor one-liners & tiering

| Competitor | Category | One-line | Threat to SFA |
|---|---|---|---|
| **Heirloom** (JM Fortier) | Market-garden planning | Closest ICP + brand/course flywheel = our mirror; agronomic depth (dynamic DTM); closed, invite-gated, beta | **Highest strategic** (same audience+model) |
| **Tend** | Market-garden all-in-one | Polished incumbent; seed→sale; self-entered-price economics; closed (API $400/mo); not farmOS | **Highest feature** (direct analog) |
| **Farmbrite** | All-in-one small farm | Broadest 5-pillar coverage; retrospective economics; English-only, no RTL | High (breadth proof + analog) |
| **Seedtime** | Crop-plan calendar | Best-in-class succession/calendar; no economics; dated UI; paywalls crop DB | Medium (planning overlap) |
| **AgriWebb** | Livestock (study only) | Category-leader UX/architecture lessons; map-cockpit + offline; no crops | Low direct / high learning |
| **Croptracker** | Fruit traceability/compliance | Compliance spine (lot codes, PHI/REI); cost→profit retrospective; rigid; enterprise | Low direct / cert lessons |
| **Local Line** | Sales/CSA/food-hub | Leader; price-list schema; 50+ reports + AI regional trends; transparent | Medium (Sell pillar) |
| **Barn2Door** | Sales/D2C | Toxic trust (hidden fees, churn); POS app | Low (anti-pattern) |
| **Harvie** | CSA (DEFUNCT Dec-2024) | Preference-matching engine = best orphaned idea | None (dead) — steal idea |
| **Home cluster** (GrowVeg/Planter/VegPlotter) | Home-garden planning | Free-tier UX bar; mobile delight; no economics; no RTL | Low (free-tier reference) |

---

## 2. SCHEMA-COMPARISON MATRIX — the union of how the industry models a farm

| Entity / pattern | Who does it well | Adopt for SFA? |
|---|---|---|
| **Farm → Field/Block → Bed → Planting** hierarchy on a map | Heirloom, Tend, Farmbrite, AgriWebb (paddock) | ✅ Core spine (maps to farmOS land/plant assets) |
| **Planting spans multiple beds + relay/intercrop geometry** | Heirloom (✓) | ✅ **Gap to nail** — Tend criticized for *no* sub-bed geometry |
| **Growing Templates** — multiple per crop, cascade/clone, per-stage yield curves | Tend | ✅ Strong schema backbone |
| **Typed record carrying cost/revenue** (event = inventory+history+compliance+margin) | AgriWebb | ✅ Maps to farmOS Quantity model |
| **Dynamic Days-to-Maturity** = cultivar × live weather × soil temp | Heirloom (headline innovation) | ✅ Differentiator to match/beat |
| **Price Lists** — one inventory → many price contexts (CSA/wholesale/market) | Local Line | ✅ Sell-pillar spine |
| **Preference-matching** — member prefs × harvest availability → auto-box | Harvie (orphaned) | ✅ Relate-pillar differentiator (steal) |
| **Compliance spine** — mandatory lot codes + Critical Tracking Events + auto PHI/REI | Croptracker | ✅ Adopt — but make input DB **self-serve** (their #1 complaint) |
| **Custom fields** | Tend/Farmbrite (tier-gated), Heirloom (overrides) | ✅ farmOS native; don't tier-gate the crop DB |
| **Workload/labor prediction** from the plan | Heirloom, Croptracker (piece-rate) | ◐ Phase-later |

## 3. FEATURE & PRICING MATRIX

| | Free tier | Paid entry | Top tier | Economics | Hebrew/RTL | API/open | Offline |
|---|---|---|---|---|---|---|---|
| **Heirloom** | ✗ (trial 1mo) | undisclosed (single plan) | — | projection-only (mkt-price = roadmap) | ✗ | ✗ closed | mobile field app |
| **Tend** | ✅ $0 | $30/mo | $400/mo (API) | self-entered prices | ✗ | $400/mo only | partial/new |
| **Farmbrite** | ✗ (trial) | $19/mo | $95/mo | retrospective P&L | ✗ (explicit) | API/webhooks (Plus+) | ✅ Scout Mode |
| **Seedtime** | ✅ $0 | $7/mo (annual) | $14/mo | ✗ none | ✗ | ✗ | unverified |
| **AgriWebb** | ✗ (trial) | ~$45/mo | ~$400/mo | retrospective margin | ✗ | GraphQL API | ✅ offline-first |
| **Croptracker** | free ver/trial | ~$5/module | quote | cost→profit retrospective | ✗ | paid REST API | ✅ + scanners |
| **Local Line** | ✗ (trial) | ~$79/mo | ~$319/mo | best: AI regional trends (stops at "top sellers") | ✗ | Zapier only | — |
| **Barn2Door** | ✗ | ~$99/mo +setup | ~$299 +setup | descriptive only | ✗ | Zapier/QBO | POS app |
| **Home cluster** | ✅ generous | $18–84/yr | — | ✗ (GrowVeg parts-list only) | ✗ | ✗ | mixed (GrowVeg no phone) |

**Pricing read for D1:** A real **free tier is rare** (only Tend, Seedtime, home cluster) → SFA's free home-grower tier is differentiated acquisition. Home-grower paid ≈ **$18–84/yr**; commercial ≈ **$30–95/mo** (Tend/Farmbrite band); sales platforms **$79–319/mo**. Metering idea: **bed-count / planted-area** (analog to AgriWebb per-DSE). Payment take on Sell: keep low/transparent (**Local Line 2.5–2.9%** good; **Barn2Door ~3.9% + setup fees** toxic; **Harvie 7%** = dead). **AVOID:** hidden setup fees, data-hostage-on-cancel, invite-gate.

## 4. WHITE-SPACE ANALYSIS — where nobody (or almost nobody) plays

1. 🥇 **Market-price → plan → "most profitable to grow"** (forward, external price index). Nobody ships it; Heirloom promises it. **SFA's #1 wedge.**
2. 🥇 **Hebrew-first RTL + Israeli Mediterranean climate dates + Israeli market.** Zero competitors; only a paper calendar exists. **Pure moat.**
3. 🥇 **The closed production↔sales loop** (sold-out → plant more next cycle). The 5-pillar unified loop is unbuilt anywhere.
4. **The unified "morning cockpit"** spanning Plan/Execute/Sell/Relate. Everyone stops at a task list (Heirloom/Tend/Seedtime) or a fulfillment list (Local Line). Nobody unifies, and none is role-aware across pillars in one screen.
5. **Beautiful mobile spatial canvas + daily task cockpit together** (free tier). Planter owns mobile layout, Seedtime owns the cockpit — nobody owns both.
6. **A free tier that never locks/wipes data** + transparent freemium (anti-GrowVeg/Barn2Door/Heirloom-gate).

## 5. TOP PAIN POINTS TO DESIGN AROUND

1. **Dated/clunky UI** (Seedtime "2000s website"; Croptracker admin; GrowVeg "clunky").
2. **Paywalling the crop database** (Seedtime: "pay to add my plant = useless" → churn). → Keep crop book free.
3. **Free/paid confusion + billing surprises** (Seedtime, Barn2Door).
4. **Data hostage on cancel** (GrowVeg deletes access). → Never lock/wipe.
5. **No offline / mobile-web parity gaps** (Tend, GrowVeg has no phone planner).
6. **Rigid schema** — no sub-bed/intercrop geometry (Tend), single-season cells (Planter), locked chemical DB (Croptracker).
7. **Thin/black-hole support** (Tend) — vs. human support as a moat (Farmbrite "never AI chatbots").
8. **Breadth-over-depth cognitive load + steep learning curve** (Farmbrite, Croptracker).
9. **Opaque pricing / setup fees / invite-gate** (Barn2Door, Heirloom).
10. **Data portability friction** (Farmbrite: no export/bulk-edit; closed APIs everywhere).

## 6. RECOMMENDATIONS FOR SFA

**Differentiate (lead with these):**
- **Market-price→plan→profit engine** (Israeli price index + profit-comparison calc) — the feature the whole category lacks and Heirloom only promises.
- **Hebrew-first RTL + Israeli climate/market** — structural moat.
- **The unified 5-pillar morning cockpit** + the closed production↔sales loop.
- **Open & portable** (headless-over-farmOS, export, no lock-in) as the anti-Heirloom/anti-Tend.

**Adopt (table stakes / reference designs):**
- Schema: Farm→Block→Bed→Planting + **Growing Templates** (Tend) + **typed-costed-records** (AgriWebb) + **dynamic DTM** (Heirloom) + **sub-bed/relay geometry** (the gap Tend left) + **price-lists** (Local Line) + **preference-matching** (Harvie, orphaned) + **compliance spine** (Croptracker, made self-serve).
- 14 calculators to parity (seed/succession/yield/spacing) — but **exposed as discrete tools** + wired to economics.
- Offline-first PWA path; owner/worker roles.
- Free-tier UX: tap-to-place + color-coded companion feedback (Planter); snap-to-grid hiding math (GrowVeg); daily task cockpit w/ per-task how-to (Seedtime).

**Business model:**
- Copy the **course→plan→software flywheel** (Nimrod's consultancy/courses → output a plan artifact that drops into the cockpit), but **widen the funnel** with a free home-grower tier (Heirloom invite-gates; we don't).
- Pricing: free home tier; commercial ~$30–95/mo band; meter on bed-count/planted-area; transparent, no setup fees, low payment take, never wipe data.

**D3 update (Sell/Relate):** **BUILD, do not integrate.** No clean integration target — Harvie dead (lock-in lesson), Barn2Door toxic, Local Line a Zapier-only competitor. The killer production↔sales loop cannot be bought, only built. Use Local Line/ Barn2Door/Harvie as reference designs.

---

## 7. Status & next

- **Internal CI pass: COMPLETE** (8/8 dossiers — full text in session transcript a92759f3.../a89ebd75.../ab18e4f8.../af3a616d.../aed5689c.../a85b37d4.../a92b23da.../a38048216).
- **Pending:** merge external multi-engine outputs (DISPATCH prompt) → triangulate; re-verify search-synthesized prices (Farmbrite, home cluster) on live pages.
- **Resolves:** D4 (competitive schema mapping) — substantially. **Informs:** D1 (pricing), D3 (Sell/Relate = build).
- **Feeds:** the detailed technical platform plan (Phase 0) + SFA data-model enrichment.
