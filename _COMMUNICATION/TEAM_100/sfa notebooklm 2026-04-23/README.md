<!--
package: SmallFarmsAgents NotebookLM Package
file: README.md
date: 2026-04-23
audience: all audiences
-->

# SmallFarmsAgents — NotebookLM Information Package

**Prepared for:** Partners, collaborators, funders, community stakeholders, technical evaluators  
**Date:** 2026-04-23  
**Product:** SmallFarmsAgents (OrganicMarketAgent) — Transparent Price Index for Israel's Organic Small Farms  
**Status:** Live in production — 9 milestones complete, Post-M9 direction defined  
**Prepared by:** Team 100 (Chief System Architect)

---

## What Is This Package

This folder contains **7 documents** about **SmallFarmsAgents (SFA)** — a volunteer-built data intelligence system that publishes a transparent, daily-updated price index for organic vegetables sold by small Israeli farms, CSAs, farm shops, and farmers markets.

SFA is a smaller project than TikTrack — it has a tighter scope and a more focused audience. This package covers everything: the product vision, the full technical pipeline, every milestone delivered, the data model, operational infrastructure, roadmap, and governance.

Upload all 7 files to NotebookLM for full coverage of the product.

---

## File List

| File | Content |
|------|---------|
| `SFA_01_VISION_AND_PRODUCT_IDENTITY.md` | What SFA is, the problem it solves, who uses it, what makes it different |
| `SFA_02_ARCHITECTURE_AND_PIPELINE.md` | Full technical stack, the 5-stage data pipeline, 8-stage normalizer, CLI commands, admin UI |
| `SFA_03_DELIVERED_MILESTONES_AND_STATUS.md` | All 9 milestones in detail — what each built, gate results, current system state |
| `SFA_04_DATA_MODEL_AND_CATALOG.md` | 31 PostgreSQL tables, the product catalog (67 products), 232 aliases, 301 scope-skip rules |
| `SFA_05_OPERATIONS_AND_INFRASTRUCTURE.md` | waldhomeserver, WordPress integration, FTPS upload, daily pipeline, admin operations |
| `SFA_06_ROADMAP_AND_FUTURE_DIRECTION.md` | WP-A1 (community submissions), WP-A2 (farmer calculator), MyFarmAgents platform vision |
| `SFA_07_GOVERNANCE_AND_TEAM.md` | AOS governance framework, team model, cross-engine validation, LOD standard, gate lifecycle |

---

## Upload Recommendation

Upload all 7 files. SFA is compact enough that the full picture fits within NotebookLM's context effectively.

**Start with:** `SFA_01` (vision) → `SFA_02` (pipeline) → `SFA_03` (milestones)  
**For technical depth:** Add `SFA_04` (data model) + `SFA_05` (operations)  
**For roadmap conversations:** `SFA_06` + `SFA_07`

---

## Suggested First Queries for NotebookLM

**For a product overview:**
- "What is SmallFarmsAgents and what problem does it solve for Israel's organic farming community?"
- "Who are the users of SFA and how does the public price index work?"
- "What makes SFA's normalization approach different from a simple price aggregator?"

**For technical conversations:**
- "Walk me through the full data pipeline from raw web page to published price index."
- "How does the 8-stage normalizer work and why is it called data-driven?"
- "What is the FTPS challenge with uPress and how was it solved?"
- "How does SFA handle products sold in different units (bunch vs. kg vs. unit)?"

**For data and catalog questions:**
- "How many products and aliases are in the catalog and how were they built?"
- "What is the resolution rate and what does it mean to have 100% resolution?"
- "What are scope-skip rules and how do they work?"
- "What's special about how CSA baskets are handled compared to individual products?"

**For partnership and community conversations:**
- "What is the Post-M9 direction and what would community submissions add?"
- "What is the Farmer Economics Calculator and why does it matter for the community?"
- "What is MyFarmAgents and how does SFA fit into that broader vision?"
- "How is SFA credible as a community resource — who operates it and is there a conflict of interest?"

**For governance and team conversations:**
- "What is AOS governance and why does a volunteer project use it?"
- "How does cross-engine validation work in SFA's development?"
- "What is the LOD standard and how were SFA's milestones specified?"

---

## Generate an Audio Overview

After uploading all files, use NotebookLM's **Audio Overview** feature for a conversational summary. Customize the prompt:

- **For community partners:** "Focus on the community value — who benefits from SFA, what the price index does for consumers and farmers, and where the product is going with community submissions and the farmer calculator."
- **For technical evaluators:** "Focus on the data pipeline architecture — how data flows from farm websites to a published price index, the normalization challenge and how it's solved, and the infrastructure stack."
- **For funders or supporters:** "Focus on what has been built, the quality and governance rigor behind it, the current production state, and the roadmap for community participation."
- **For farmers or CSA operators:** "Focus on the farmer-facing value — what the price index shows them, how community submissions would work, and what the farmer economics calculator would do."

---

## Key Facts for Quick Reference

| Metric | Value |
|--------|-------|
| Pipeline stages | 5 (Collect → Parse → Normalize → Aggregate → Publish) |
| Normalizer stages | 8 (Scope skip → Alias → Organic → Price → Unit → Quantity → Normalize → Basket) |
| Canonical products | 67 |
| Product aliases | 232 |
| Scope-skip rules | 301 |
| Active sources | 7 of 20 registered |
| Normalized observations | 174 |
| Resolution rate | **100%** |
| Automated tests | 127 passing |
| Milestones complete | M1–M9 + S001 (AOS canonization) |
| Production server | waldhomeserver (Ubuntu 24.04, always-on home server) |
| Public URL | nimrod.bio/smallfarmsagent |
| Tech stack | Python 3.11+, PostgreSQL 15, Flask admin, FTPS, WordPress |
| Governance | AOS L0 spoke profile |

---

## Notes on Content

All content in this package is sourced from SFA's canonical documentation (`documentation/` hub), architecture reports, milestone records, and the Post-M9 product direction specification. Where specific numbers are given (product count, alias count, observation count), these reflect the system state as of April 23, 2026.

The product is live and running daily. Numbers may increase as new sources are added and the catalog expands.
