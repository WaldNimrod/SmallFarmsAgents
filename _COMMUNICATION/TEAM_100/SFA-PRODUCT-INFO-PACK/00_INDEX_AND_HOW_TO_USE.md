# SFA Product Information Pack — Index & How to Use

**Prepared by:** team_100 (Chief System Architect) · **Date:** 2026-06-03 · **Status:** v1.0 — product-disclosure & marketing-research base
**Subject:** SmallFarmsAgents (SFA) — the live platform at **https://sfa.nimrod.bio**
**Purpose:** a self-contained research corpus for **NotebookLM** to (a) generate marketing materials for customers, the community, and business partners, and (b) support deep product-development planning. Every document is also provided as a **PDF** (in `pdf/`) because the NotebookLM environment ingests PDFs.

---

## What SFA is, in one paragraph
SFA (SmallFarmsAgents) is an **open, free-to-use community platform for Israel's organic and small-scale farming market**. It has two live products — a **Crop Book** (an agronomic knowledge base turned calculator-driven planning tool: ~66 crops / ~368 varieties, a 13-topic taxonomy, 14 planning calculators, two-audience UX) and a **Market Index / OrganicMarketAgent** (a community price index for organic produce) — both served from `sfa.nimrod.bio`. Its distinguishing strength is a **rigorous, provenance-tracked, multi-source data model** (confidence scoring, trust tiers, a τ=0.40 validation gate) so every agronomic value carries a visible trust signal. Positioning: **"כלים פתוחים לחקלאות קטנה" — open tools for small-scale farming**, no signup, free core.

---

## Documents in this pack

| # | File | What it covers | Primary use |
|---|------|----------------|-------------|
| 00 | `00_INDEX_AND_HOW_TO_USE.md` | This index + audience map + usage notes | Orientation |
| 01 | `01_PRODUCT_OVERVIEW.md` | Mission, the two products, access ladder, value per audience | Marketing · partners |
| 02 | `02_MARKET_CONTEXT_AND_AUDIENCES.md` | Israel organic/small-farm market, problems, audience map, positioning | Marketing · strategy |
| 03 | `03_CROP_BOOK_FEATURES.md` | Crop Book deep feature catalog: 14 calculators, AssumptionFields, UX, states | Product · marketing |
| 04 | `04_MARKET_INDEX_OMA.md` | The community price index: sources, freshness, disclaimer, UX, limits | Product · marketing |
| 05 | `05_DATA_MODEL_AND_PROVENANCE.md` | Field taxonomy, multi-source enrichment, confidence/trust tiers, field_state | Technical · trust story |
| 06 | `06_TECHNICAL_ARCHITECTURE.md` | Two-tier architecture, ingest contract, stack, app-shell, design system | Technical planning |
| 07 | `07_DELIVERY_DEPLOY_OPS.md` | 3-host topology, deploy pipeline, cron, security, ops constraints | Technical · ops |
| 08 | `08_ROADMAP_AND_FUTURE_MODULES.md` | What shipped (S001→S003), future modules, server-side ideas backlog | Planning · partners |
| 09 | `09_GTM_MESSAGING.md` | Positioning, elevator pitch, audience narratives, proof points, FAQ | Marketing |
| 10 | `10_GLOSSARY_AND_KEY_FACTS.md` | Canonical terms + authoritative facts/numbers (grounding anchor) | All — accuracy |

---

## How to use this pack in NotebookLM

1. **Upload all PDFs** from the `pdf/` subfolder as sources (the `.md` files are the editable originals).
2. **Ground accuracy on doc 10** (`10_GLOSSARY_AND_KEY_FACTS`) — it lists the canonical numbers and the LIVE-vs-PLANNED-vs-PROPOSED status of every capability. When generating any claim, prefer doc 10's facts and **respect the status tags** (do not present PLANNED/PROPOSED items as shipped).
3. **By goal:**
   - *Customer / end-user marketing* → 01, 03, 04, 09 (+ 02 for framing).
   - *Community outreach* → 01, 02, 04 (community surface), 09.
   - *Business-partner / investor materials* → 01, 02, 08, 09, with the trust story from 05.
   - *Product-development planning* → 05, 06, 07, 08 (+ 03/04 for feature baselines).
4. **Status discipline (important):** capabilities are tagged **LIVE** (shipped on sfa.nimrod.bio), **PLANNED** (future modules CB-2..CB-5, LOD100 direction only), or **PROPOSED** (server-side ideas SRV-1..5, unapproved). Never blur these lines in generated copy.

---

## Provenance of this pack
Authored by team_100 from the SFA repository's authoritative sources: `_aos/context/PROJECT_CONTEXT.md`, the `documentation/` tree (architecture, data-schema, pipelines, ops, design-system), the locked work-package specs (the data-model Canon WP-CB-0, the calculator tool WP-CB-1, the enrichment layer WP-A), `_aos/roadmap.yaml`, and the live delivery-tier code (`sfa_delivery/`, `organic_market_agent/`). It reflects system state as of **2026-06-03** (S003-P004 program closed; both Crop Book v1 + Class B surfaces live). The pack is in **English** (the project's documentation language); Hebrew product/UI terms are given in parentheses to aid localized material.
