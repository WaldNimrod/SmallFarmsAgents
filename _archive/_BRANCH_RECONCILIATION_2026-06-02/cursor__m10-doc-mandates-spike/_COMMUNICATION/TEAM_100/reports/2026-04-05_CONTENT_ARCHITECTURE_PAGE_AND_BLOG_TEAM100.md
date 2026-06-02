# Content Architecture Review — Public Page and Blog Post
**Date:** 2026-04-05
**From:** Team 100 (Architecture)
**Topic:** Content alignment for the public market page and the accompanying WordPress blog post

## Background
Team 100 reviewed the current public-page copy sources, the current WordPress body template, Team 80 content handoff materials, and the active privacy / publish architecture documents.

Reviewed sources:
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/05_copy.md`
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/06_blog_post.md`
- `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/03_ui_spec.md`
- `_COMMUNICATION/TEAM_80/M8_feedback_team80_to_team100.md`
- `organic_market_agent/publisher/templates/public_report_body.html`
- `docs/PRIVACY_POLICY.md`
- `documentation/01-overview/PROJECT_VISION_AND_SYSTEM_MAP.md`
- `_COMMUNICATION/TEAM_100/reports/2026-04-04_M13_ARCHITECTURAL_APPROVAL_TEAM100.md`

This review addresses content from an architectural perspective only: message accuracy, privacy, scope discipline, and consistency between the public page and the blog narrative.

## Findings
### Critical
1. Team 80's copy handoff is based on a pricing calculator product, not the current implemented product.
   Evidence: `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/05_copy.md` says "Choose a crop / Adjust costs / Get a realistic price". The current system is a public aggregated price index, not a calculator. Reusing this wording would misdescribe the product.

2. Public-facing content must not imply farm-level visibility or identifiable source attribution.
   Architecture and privacy policy permit only aggregated data, source counts, ranges, and freshness indicators. Any copy that suggests a user can inspect a specific farm, price list, or seller-level contribution would violate the privacy contract.

### High
1. The current page disclaimer is too narrow about data origin.
   The body template currently says the page collects data from public sources of organic growers in the community. This is no longer sufficiently accurate once store / chain / CSA variants exist in the public model. Content should refer to relevant public sources and aggregated observations, not only growers.

2. The current page introduction mixes product messaging with consulting / service-sales messaging.
   The public page is the product surface of OrganicMarketAgent. It should primarily explain the index: what it is, how to read it, what its limits are, and why privacy matters. Consulting-style CTA language about inventory systems, delivery scheduling, and hydroponics broadens the promise beyond the current product and weakens architectural clarity.

3. The blog post draft is structurally reasonable but currently too personal and underspecified for a public product launch post.
   The post should not rely on unsupported autobiographical claims as the main proof of value. It should connect a personal origin story to a precise public product: transparent aggregated pricing, community benefit, privacy protection, and realistic scope.

### Medium
1. The page and post need a single canonical message hierarchy.
   The page should answer "what this is" and "how to read it" quickly. The blog post should answer "why this exists" and "why this approach is different". If both try to do everything, both will become unfocused.

2. The page should avoid promising operational outcomes the system does not compute directly.
   Phrases like "price with confidence" are acceptable if grounded in aggregated data. Phrases implying profitability calculation, cost accounting, or decision automation are not yet accurate for this page.

## Decisions
### 1. Canonical product framing
The public page must describe the system as:
- a transparent aggregated price index
- based on public data from multiple relevant sources
- privacy-preserving by design
- updated data, not a quote or recommendation

The page must not describe the system as:
- a pricing calculator
- a quoting engine
- a marketplace
- a seller comparison tool
- a farm management suite

### 2. Canonical privacy message
The privacy message must remain simple and explicit:
- only aggregated data is shown
- no farm-level pricing is exposed
- specific growers / vendors cannot be identified from the public output

This privacy statement should appear in both:
- the public page
- the blog post

### 3. Canonical narrative split
Public page:
- explain the index in one short opening block
- explain freshness / aggregation / source-count logic in plain language
- invite contribution or feedback only after the core explanation

Blog post:
- open with the real problem: pricing opacity for small organic farms
- explain why aggregated shared visibility is useful
- explain why privacy is non-negotiable
- position this page as the first practical public output
- close with a community invitation

### 4. Content boundaries for claims
Allowed claims:
- aggregated prices
- multiple-source methodology
- transparency and freshness indicators
- community benefit
- privacy by design
- evolving public infrastructure for the farming community

Disallowed or high-risk claims unless separately verified and approved:
- exact profitability outcomes
- exact farmer savings or income improvements
- farm-level or seller-level comparisons
- statements implying full market coverage
- statements implying the system is already a broader operations platform

## Required Actions
- [ ] Replace calculator-oriented legacy copy with index-oriented copy — Owner: Team 100 / Nimrod
- [ ] Tighten the public page opening block so it explains the product before introducing Nimrod or future services — Owner: Team 100 / Nimrod
- [ ] Rewrite the disclaimer so it matches current source-model reality and privacy rules — Owner: Team 100 / Team 10
- [ ] Draft the blog post around problem → method → privacy → community invitation — Owner: Team 100 / Nimrod
- [ ] Keep one shared wording set for privacy, transparency, and what the system is / is not — Owner: Team 100

## Working Copy Direction (for drafting)
Recommended page structure:
1. Title: price index, not calculator
2. One short paragraph: what the index is
3. One short paragraph: how to read it
4. One short privacy / transparency block
5. Table
6. Community CTA
7. Optional founder note kept short and secondary

Recommended blog structure:
1. The pricing visibility problem
2. Why existing tools do not solve it for small farms
3. Why aggregated public signals are useful
4. Why privacy constraints matter
5. What this first version does today
6. What it does not do yet
7. Invitation to follow / contribute

## Gates Opened / Blocked
No gate decision in this document.
This is a content-architecture alignment review only.
