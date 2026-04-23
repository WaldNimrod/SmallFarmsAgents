<!--
package: SmallFarmsAgents NotebookLM Package
file: SFA_06_ROADMAP_AND_FUTURE_DIRECTION.md
date: 2026-04-23
audience: technical, partnerships, product analysis
-->

# SFA — Roadmap and Future Direction

## Overview

SFA completed nine milestones (M1–M9) and achieved its first production state: a live, daily-updated, transparent price index for organic vegetables. Post-M9, the product direction shifts from **passive collection** to **community participation**. Two concrete work packages define the next phase.

---

## Post-M9 Direction: From Passive to Participatory

The M1–M9 pipeline is a one-way data flow: SFA collects from farm websites, normalizes, aggregates, and publishes. The community consumes the result, but does not contribute to it.

The next direction addresses this asymmetry. The binding decision document (`SFA_POST_M9_PRODUCT_DIRECTION_LOD200_v1.0.0.md`, April 2026) defines two tracks:

| Track | Name | Summary |
|-------|------|---------|
| **WP-A1** | Moderated user submissions | Any registered user can submit price data → moderation before publication |
| **WP-A2** | Farmer economics calculator | Simple deterministic calculator for farm product economics |

Both tracks are defined at LOD200 (concept + requirements). Detailed specifications (LOD300/LOD400) will be authored after Team 190 package review.

---

## WP-A1 — Moderated User Submissions

### The Problem It Solves

SFA currently collects price data only from farm websites that have structured, machine-readable content. This creates a coverage gap: many small farms, farmers markets, and independent CSA operators:

- Don't have websites with parseable product listings
- Have websites that are too inconsistent for automated collection
- Sell through WhatsApp, Instagram, or physical market stalls — no web presence at all

These sources represent real market data that SFA cannot reach through automated collection. Community-submitted data is the path to closing this gap.

### What WP-A1 Will Build

**Submission schema:** A structured form for submitting price observations — product (from the canonical catalog dropdown), price, unit, quantity, source name, date observed. Structured inputs prevent the normalization problem from recurring: users select from canonical products rather than typing free-form Hebrew names.

**Authentication linkage:** Submissions are tied to registered user accounts. Anonymous submissions are not accepted — community accountability requires identity.

**Moderation queue:** Before a community submission affects the published index, it passes through a moderation step. A moderator (currently Nimrod) reviews the submission: plausible price range? Known source? If approved, the submission is ingested into the pipeline as a `community_submission` source type. If rejected, the user is notified.

**Audit trail:** Every submission is logged — who submitted, when, what was submitted, what the moderation decision was, and the moderator identity. This transparency is essential for community trust.

**Privacy Policy alignment:** The existing `docs/PRIVACY_POLICY.md` was written with future community submissions in mind. WP-A1 implementation must align with the documented privacy commitments.

### What WP-A1 Is Not (V1)

- **Not a full farmer certification system.** The previous planning had a multi-role ladder (`pending_farmer` / `farmer` / `verified_farmer`). This is explicitly deferred. V1 is simple: any registered user, one moderation step, binary approve/reject.
- **Not a public edit of the live index.** No Wikipedia-style community editing. Submissions go through moderation before they affect published data.
- **Not complex RBAC.** No permission tiers in V1 — the moderator is the operator.

### Strategic Value

WP-A1 transforms SFA from a passive scraper into a **community-contributed data platform**. Once community submissions are trusted and flowing, the dataset could include sources that are currently invisible to automated collection — farmers market vendors, WhatsApp-only CSAs, seasonal farm stalls.

This is what transitions SFA from a price data aggregator into a community price intelligence platform. The technical infrastructure remains the same; the data sourcing model broadens fundamentally.

---

## WP-A2 — Farmer Economics Calculator

### The Problem It Solves

Small farmers and CSA operators struggle with a specific analytical problem: setting prices correctly.

A farmer growing zucchini knows their costs — seeds, soil amendments, water, labor time, packaging, market stall fee. But translating those costs into a competitive, sustainable retail price requires calculation that most small farms do not have tools for. The result: prices are set by intuition or by copying what neighboring farms charge, without understanding whether that price covers actual costs.

SFA already publishes what the market charges. WP-A2 answers the complementary question: *what should a farm charge given its actual costs?*

### What WP-A2 Will Build

**A deterministic calculator.** Inputs → outputs. No AI, no machine learning, no conversational agent. A form with structured fields, documented formulas, and a result screen.

**Calculation scope (V1):**
- Cost per unit of production (seeds, inputs, water, labor — user-entered)
- Packaging cost per unit
- Market/distribution cost per unit (stall fee, transport)
- Target margin (user-selected: 20%, 30%, 40%...)
- **Output:** minimum sustainable retail price at the target margin
- **Comparison:** SFA market average for the same product (from the live index)

**Interface:** Hebrew RTL, mobile-friendly. A farmer should be able to fill this in on their phone while setting up their market stall.

**No saved profiles in V1.** Each calculation is ephemeral — the user enters, calculates, reads the result. Historical multi-farm comparison is out of scope for V1.

### What WP-A2 Is Not (V1)

- **Not an AI agent.** No LLM, no conversational flow. Deterministic formulas only.
- **Not a multi-farm comparison tool.** One farm at a time.
- **Not a portfolio or financial management tool.** SFA is about pricing transparency, not farm business management software.

### Strategic Value

WP-A2 makes SFA useful to **farmers**, not just consumers and researchers. Without this, SFA's value proposition is asymmetric: it helps buyers understand market prices, but gives nothing back to the producers who are the community's foundation.

A farmer using WP-A2 gets:
- A principled price for their product based on their actual costs
- A comparison against the market average they're operating in
- A tool they can use every season as input costs change

This is the first step toward SFA becoming genuinely bidirectional — a community resource for both buyers and sellers.

---

## Frozen Items (Not Scheduled)

The LOD200 package explicitly freezes the prior **M10 bundle** — a set of earlier planning items that are no longer aligned with current direction:

- **WP: Farmer Roles System** — multi-role RBAC with farmer certification levels. Superseded by WP-A1's simpler approach.
- **FarmCostAgent concept** — an AI-powered conversational agent for farm economics. Superseded by WP-A2's deterministic calculator.
- **In-page contribution form spec** — an earlier design for contribution that predated the moderation model.

These items are **frozen**, not deleted. They are preserved for reference but are not authorized for implementation until explicitly thawed by Team 100.

---

## M9C — Content and Community Engagement (Out of Development Scope)

M9C is a planned set of content and community engagement actions — blog posts, community outreach, social media presence, partnership conversations. This milestone is **outside the scope of the development team** (Team 10/20).

M9C is owned by **Team 80** (Product & Strategy) and **Nimrod** (owner). It will proceed on its own timeline, independently of the technical work packages.

M9C includes:
- Published explanation of SFA's methodology (how normalization works, how the price index is computed)
- Outreach to Israeli organic farming communities and CSA networks
- Potential partnerships with agricultural NGOs, researchers, and farming publications
- Community feedback channels

---

## MyFarmAgents Platform Vision

SFA is described as the "first agent" in a broader platform concept: **MyFarmAgents**.

The idea: a volunteer-driven platform of specialized data intelligence tools for Israel's agricultural community, under one umbrella brand. SFA (OrganicMarketAgent) is the first deployed agent — focused on vegetable price transparency. Future agents could address:

- **Regional market monitors** — price data for specific regions (e.g., North, Center, South separately)
- **Seasonal availability tracking** — what is in season, what farms are harvesting
- **Farm directory and certification data** — organic certification status, farm profiles, contact information
- **Agricultural input pricing** — cost of fertilizers, soil amendments, seeds for small farmers
- **Export / import prices** — reference data for farms considering distribution channels

This vision is currently a concept — it is not being built. SFA V1 is a single-agent system. The platform concept describes the extensibility potential, not the current development plan.

**What makes the platform concept technically credible:** SFA's pipeline architecture is already modular. The collector/parser/normalizer/aggregator/publisher chain is designed around source types and product catalogs, not hard-coded to any specific domain. Adding a new agent with a different product catalog (say, agricultural inputs instead of vegetables) would require a new catalog and new parsers, but could reuse the core pipeline infrastructure.

---

## Timeline Summary

| Period | What |
|--------|------|
| March 2026 | M1–M3 complete (Foundation, Collection, Normalizer) |
| Late March 2026 | M4–M6 complete (Aggregator, Admin UI, Automation) |
| Early April 2026 | M7–M9 complete (Publishing, UX, Site Optimization) |
| April 12, 2026 | S001 complete — AOS canonization |
| April 2026 | Post-M9 LOD200 package submitted to Team 190 |
| Next | WP-A1 (Moderated submissions) — pending Team 190 review |
| Next | WP-A2 (Farmer calculator) — parallel to WP-A1 or sequenced |
| Ongoing | M9C (Content/community) — Team 80 + Nimrod |
| Long-term | MyFarmAgents platform expansion |

---

## Why WP-A1 and WP-A2 Are the Right Next Steps

**WP-A1 (submissions)** addresses the fundamental limitation of automated collection: not all market participants have parseable web presences. Community contributions close this gap, but require a trust model (moderation) before community data affects the published index. Building the moderation layer first is the correct sequencing.

**WP-A2 (calculator)** addresses the community's bilateral nature: price transparency for consumers is only half the value. A tool that helps farmers price their products correctly closes the loop — it makes the community's data valuable to producers, not just buyers.

Together, these two work packages move SFA from a read-only data product into a read-write community platform — while keeping the quality gate (moderation) that protects the index's credibility.
