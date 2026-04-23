<!--
package: SmallFarmsAgents NotebookLM Package
file: SFA_01_VISION_AND_PRODUCT_IDENTITY.md
date: 2026-04-23
audience: product analysis, partnerships, technical collaborators, community stakeholders
-->

# SmallFarmsAgents — Vision, Identity, and Purpose

## What SmallFarmsAgents Is

**SmallFarmsAgents (SFA)** is a Python-powered data intelligence agent that collects, normalizes, aggregates, and publishes a transparent price index for organic vegetables sold by small Israeli farms, CSAs, farm shops, and farmers markets.

The product name **OrganicMarketAgent (OMA)** is the internal technical name for the agent. The public-facing brand is **SmallFarmsAgents**, operating under the umbrella platform **MyFarmAgents** — a volunteer initiative designed to serve Israel's small organic farming community with data intelligence tools.

SFA is the first deployed agent in the MyFarmAgents platform. The platform concept is extensible: future agents can serve other agricultural data needs under the same infrastructure.

---

## The Problem SFA Solves

### Price Opacity in Israel's Organic Market

Israel's small organic farming sector is fragmented. Farmers, CSA operators, farm shops, and weekend farmers markets all sell fresh organic vegetables — but each does so independently, with no shared pricing reference. Neither farmers, consumers, nor researchers have a unified view of what organic vegetables actually cost at source.

This opacity creates several problems:

**For consumers and communities:** Buying organic vegetables through a CSA subscription or farm shop involves trusting that pricing is fair. Without a market reference, there is no way to evaluate this. Consumers make purchasing decisions without knowing whether a price is typical, high, or anomalous for the season.

**For farmers and CSA operators:** Setting prices fairly — relative to market conditions, seasonality, and quality — requires knowing what others charge. Small farms rarely have access to this information. Large-scale market research covers supermarkets and distributors, not direct-to-consumer farm pricing.

**For researchers and advocates:** Anyone studying the organic food economy in Israel — NGOs, academic researchers, journalists, government programs — lacks a structured, normalized, regularly-updated data source covering the small-farm direct-to-consumer segment.

**The structural gap:** This price intelligence exists in the market — scattered across farm websites, CSA subscription pages, and market listings — but in raw, unnormalized form. "1 כרוב קטן" (1 small cabbage) on one site and "כרוב" (cabbage) by the kilogram on another are the same product at incomparable prices, until a normalization layer converts them to a common unit.

### What SFA Does About It

SFA is the normalization and aggregation layer that did not exist. It:

1. **Collects** raw price data from farm websites, CSA listings, and farmers markets on a daily basis
2. **Normalizes** every raw item name (in Hebrew) and price against a curated 67-product canonical catalog, converting all prices to ₪/kg equivalents
3. **Aggregates** daily statistics per product: mean price, standard deviation, count of observations, breakdown by source
4. **Quality-gates** the data before publication: outlier detection, minimum source count, staleness thresholds
5. **Publishes** the results as a transparent, publicly accessible price index via a static HTML/JSON artifact embedded in a WordPress site

The result is a daily-updated, source-cited price index that gives the community a shared reference point for organic vegetable prices.

---

## Who Uses SFA

### Current Audience (Live Product)

The public price index is accessible at `nimrod.bio/smallfarmsagent`. It is designed for:

- **Community researchers** — individuals and organizations studying organic food pricing in Israel
- **CSA members and potential members** — consumers who want to understand whether their subscription pricing is market-aligned
- **Farm shop customers** — buyers who want a price reference before their weekly market visit
- **Small farmers and CSA operators** — producers who want to understand market pricing for their own planning

### Platform Vision: MyFarmAgents

SFA operates within a broader vision: **MyFarmAgents**, a volunteer-driven platform for agricultural data intelligence in Israel. SFA is the first agent. The platform is designed to be extensible:

- Each "agent" handles a specific domain of farm data intelligence
- Common infrastructure (data pipeline, publishing, admin UI) is shared
- Different agents can serve different farming segments, geographies, or data types

Future agents could address: local market monitoring for specific regions, seasonal availability tracking, farm directory and certification data, or agricultural input pricing.

---

## What Makes SFA Different

### The Normalization Problem Is Hard

"Price data from farm websites" sounds simple. In practice, it is one of the most challenging data normalization problems in agricultural data:

- Israeli farm websites use inconsistent Hebrew product names — every farm has its own naming conventions
- Units vary: kilogram, unit (single piece), bunch, basket, pack — and conversion factors between these are product-specific
- CSA operations sell "baskets" — mixed weekly boxes — which represent a different data type from per-product pricing
- Prices change seasonally, weekly, or more frequently
- Scope must be filtered: websites that sell organic vegetables also sell cleaning products, groceries, imported goods — all of which must be excluded

SFA's normalizer handles this through a **data-driven 8-stage pipeline** — alias mappings, scope-skip rules, unit conversions — all stored in PostgreSQL and configurable without code changes. 301 scope-skip rules filter non-food items. 232 alias mappings convert raw Hebrew names to canonical products. This is the intellectual core of the system.

### Transparency by Design

The published price index includes:
- Which sources contributed data
- How many observations each price average is based on
- When data was last collected (staleness level)
- A version timestamp for every artifact

This is not a black-box price indicator. Every number has an auditable source.

### No Conflict of Interest

SFA is volunteer-built and community-oriented. It is not operated by a retailer, a competing farm, or a price comparison commercial service. The operator (Nimrod) is a consumer of the data, not a seller. This structural independence is part of the product's credibility.

---

## Current Product State (April 2026)

SFA has completed **9 milestones** of active development. The product is live in production:

- **20 data sources** registered (7 currently active)
- **67 canonical products** in the catalog
- **232 product alias mappings** (Hebrew raw names → canonical products)
- **301 scope-skip rules** (filtering out non-food and out-of-scope items)
- **174 normalized observations** in the current dataset
- **100% resolution rate** — all extractable items successfully normalized
- **127 automated tests** passing
- **Daily publishing pipeline** running on waldhomeserver (Ubuntu server, always-on)
- **WordPress integration** live at nimrod.bio/smallfarmsagent

The next direction (Post-M9) focuses on user-submitted price data and a farmer economics calculator — extending the system from passive collection to community participation.

---

## The Tagline and Positioning

SFA exists to answer one question for Israel's organic farming community: **what does organic produce actually cost at source, today?**

The product's value is in the daily update rhythm, the normalization rigor, and the transparency of sourcing. It is not a price comparison shopping tool. It is a community data resource — the kind that makes markets more transparent and communities more informed.
