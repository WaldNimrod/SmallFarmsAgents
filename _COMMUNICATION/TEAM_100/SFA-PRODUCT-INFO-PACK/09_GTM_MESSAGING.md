# SFA Go-to-Market Messaging Kit
**Document:** 09 — GTM Messaging
**Product:** SmallFarmsAgents / sfa.nimrod.bio
**Prepared by:** team_100 (Chief Architect)
**Date:** 2026-06-03
**For:** NotebookLM ingestion — marketing-material research, content strategy, partner conversations

> **Honesty framework used throughout:** "LIVE" = shipped and accessible at sfa.nimrod.bio today. "PLANNED" = in the roadmap as a registered future module (LOD100 placeholder, not yet built). "PROPOSED" = unapproved idea in the server-side ideas register. Nothing is described as live unless it was LOD500_LOCKED and deployed as of 2026-06-03.

---

## 1. One-Line Positioning

**English:** Open agronomic planning tools and a community organic price index for Israel's small-farm growers — free, no signup, Hebrew-first.

**Hebrew:** כלים פתוחים לתכנון חקלאי ומחירון ירקות אורגני — בחינם, ללא הרשמה, בעברית.

---

## 2. Elevator Pitch (60 seconds, English)

SmallFarmsAgents is an open community platform at sfa.nimrod.bio serving Israel's organic and small-farm growers. We publish two core products.

The first is the Market Index (מחירון שוק) — a daily community organic price index aggregated from four farmer-market sources across Israel, updated automatically, with full source transparency. It is the only open price reference for organic produce in Israel.

The second is the Crop Book (ספר גידולים) — a structured agronomic knowledge base for 66 farm crops, built from ten or more primary sources including JMF MasterClass, Israeli Ministry of Agriculture extension data, Shaham bulletins, Tend Israel operational records, and community sources. The Crop Book powers 14 planning calculators that help growers estimate seed quantities, succession timing, bed allocation, and expected revenue — all drawing from real crop data rather than generic defaults.

Both tools are free, require no account, and are Hebrew-first. The data model tracks provenance: every value has a source class and a confidence tier. This is not a price aggregator or a spreadsheet template — it is a community data commons built to the same rigor you would expect from a professional agronomic database.

---

## 3. Audience-Tailored Narratives

### 3.1 For Customers and End Users (Market Farmers and Gardeners)

**Core message:** "Plan your season with data you can trust."

SmallFarmsAgents removes the guesswork from small-farm planning. If you have grown vegetables in Israel, you know the problem: the best planning resources (Jean-Martin Fortier's MasterClass, Tend, Curtis Stone's guides) are in English, calibrated to North American conditions, and priced at or behind a paywall. Israeli extension bulletins exist but are not synthesized into planning tools. Prices at the organic market are whatever you think you can get — there is no reference.

We built sfa.nimrod.bio to change that. The Crop Book covers 66 crops in Hebrew with data from the sources you already trust: JMF/MasterClass, the Israeli Ministry of Agriculture, Shaham bulletins, Idan planning guides, and five years of Tend Israel operational data. The 14 planning calculators draw from that data — so when you calculate how many beds you need for 50kg of tomatoes per week, the yield estimate is based on what Israeli market gardeners actually produce, not a generic American default.

The Market Index shows you what organic produce sells for, updated daily from four community sources.

No account. No payment. No data shared beyond what you choose to contribute.

**Key proof points (LIVE):**
- 66 crops covered, with Hebrew names and localized variety data.
- 14 calculators covering seed quantity, sow/transplant timing, succession, bed allocation, revenue and profit comparison, and seed cost.
- Data from 10+ sources including Israeli MoA, Shaham, JMF MasterClass, Tend Israel, Curtis Stone, Bustan calendar, Idan planning guides, GROWORGANIC, FRANCHI, and others.
- Enrichment database: 5,780+ reconciled field values across crops and varieties.
- Market Index: daily data from four community farmer-market sources.
- Lighthouse mobile score 87+ performance, 95+ accessibility, 100 SEO.

---

### 3.2 For the Community (Potential Contributors and Advocates)

**Core message:** "Your knowledge belongs in a shared commons."

The agronomic knowledge that Israeli market farmers carry — what works in this climate, what doesn't, which variety performs on coastal sand vs hill terra rossa — is not written down anywhere that benefits everyone. It lives in WhatsApp groups, in individual spreadsheets, in the heads of growers with twenty years of experience.

SmallFarmsAgents is building the infrastructure to change that. We have already ingested every major published source available — JMF, the Israeli MoA, Shaham, Tend — and we are building the tools for community knowledge to flow into the commons through a structured, quality-gated enrichment pipeline.

The data model is designed for this. Source classes distinguish an expert override (EX) from a community operational observation (OP) from a web source (WB). A reconciler engine blends multiple sources into a single best estimate. Community contributions do not overwrite high-confidence data — they participate in a weighted blend that improves over time as more observations arrive.

The community section of the platform (LIVE) provides a landing point. The /contribute endpoint (LIVE) accepts structured knowledge submissions. Full community write-back with operational farm data is a planned future module (WP-CB-5, Tend integration — not yet built).

**What you can do today:**
- Use the tools. Share them with growers you know.
- Submit knowledge via the /contribute form.
- Share price observations — contact us about contributing to the Market Index source pool.

---

### 3.3 For Business Partners

**Core message:** "The only open, provenance-tracked organic produce data commons in Israel — with a growing grower community and a rigorous data model designed for integration."

SmallFarmsAgents is an infrastructure investment in Israel's organic and small-farm community. For partners in agricultural inputs, seed distribution, farm software, CSA platforms, or agricultural finance, it offers several distinct value propositions.

**Audience reach:** The platform is open and no-signup, which means every Hebrew-speaking grower who finds it via search can use it without friction. The open posture is designed to maximize reach in a market where trust is built slowly. There are no registered users to show, but the content is indexed, Hebrew-first, and positioned for the specific community we serve.

**Data quality:** The enrichment database is built to a professional standard. Values are source-tracked, confidence-tiered, and reconciled from multiple independent sources using a weighted-mean algorithm with outlier gates. The data model distinguishes expert overrides, curated institutional data, published structured data, and operational farm records. This is not scraped data with unknown provenance — it is a curated, maintained corpus.

**API capability:** The ingest pipeline is HMAC-signed and API-capable (LIVE: POST /api/v1/ingest). Data flows from the backend PostgreSQL database to the public MySQL delivery tier via a structured push. This architecture is ready for partner data feed integration.

**Market Index as a shared reference:** The Market Index is the only open, community-backed organic produce price index in Israel. For input suppliers or buyers who need a market reference, it provides a neutral, transparent benchmark.

**Partnership opportunities (discussion only — not currently formalized):**
- Seed or input supplier co-branding on relevant Crop Book pages.
- Data feed partnerships (contribute additional structured sources to the enrichment pipeline).
- Integration with farm management platforms (connect calculator outputs to a partner's planning tools).
- Sponsorship of the open platform to reach the small-farm community.

---

## 4. Key Differentiators (Proof-Ready)

| Differentiator | Proof / Evidence |
|----------------|-----------------|
| Open + free core | sfa.nimrod.bio is fully accessible without account or payment — verified in browser, no registration wall. |
| 66 crops, Hebrew-first | Crop Book database: 66 crops seeded, Hebrew names in `crops.name_he`, all UI in Hebrew RTL. |
| 14 planning calculators | Live at sfa.nimrod.bio/calc/ — all 14 calculators functional with AssumptionField defaults visible. |
| Multi-source provenance | 10+ source classes integrated; crop_field_enrichment table has 5,780+ rows with source class, confidence tier, and field_state (VALIDATED/PARTIAL/INFERRED) stamped at ingest. |
| Israel-localized | Israeli MoA + Shaham data (56+ planting calendar rows), Tend Israel operational overlay (5 years of harvest data), Idan planning guides, Bustan calendar — all integrated. |
| Community organic price index | Market Index: four MyPIPS community sources, daily automated pipeline, 32+ products, source-transparent. |
| Rigorous data model | Weighted-mean reconciler with MAD-based outlier gate; τ=0.40 validation threshold; calibration harness (CALIBRATED/MARGINAL/MISALIGNED); seven source classes with defined trust tiers; field-level policies per FIELD_POLICY registry. |
| Two-audience UX | Card view (gardener) / table view (farmer); simple/full/drill-down depth per crop; responsive mobile layout (Lighthouse performance 87+). |
| Watercolor brand identity | 28+ Devora watercolor crop masters integrated, composed deterministically from brand masters — consistent, authentic visual identity. |

---

## 5. Content Themes by Channel

### 5.1 Organic Market Farmers (WhatsApp groups, Instagram, farmers' market community)

| Theme | Content Ideas | Status Signal |
|-------|--------------|---------------|
| Planning made tangible | "How many beds do you need for 20kg of tomatoes per week?" — show the calculator at work | LIVE calculator |
| Price transparency | "What did cherry tomatoes sell for at the organic market this week?" — Market Index screenshot | LIVE data |
| Succession timing | "Never run out of lettuce — how succession planting works with real dates" | LIVE calculator #6 |
| Data from trusted sources | "Where does our data come from? JMF, the Israeli MoA, Tend, and your community." | LIVE enrichment pipeline |
| Hebrew crop names | "What is the Hebrew name for Pak Choi? We have it." | LIVE — 66 crops with name_he |

### 5.2 Home Gardeners and Learners (Online forums, permaculture groups, agricultural schools)

| Theme | Content Ideas | Status Signal |
|-------|--------------|---------------|
| Approachable planning | "Growing your first vegetable garden? Start with the Crop Book." | LIVE card view |
| No barriers | "No account. No payment. Just open the browser and start." | LIVE posture |
| Learn from real data | "Our germination rate default is 90% — here is why and how to adjust it." | LIVE AssumptionField |
| Hebrew-first | "Agricultural tools in Hebrew — finally." | LIVE |
| Understanding provenance | "What does VALIDATED mean on a crop page? Here is how to read data confidence." | LIVE provenance cues |

### 5.3 Community and Advocates (Food sovereignty, sustainable agriculture, open-source communities)

| Theme | Content Ideas | Status Signal |
|-------|--------------|---------------|
| Open commons | "We built the data model so contributions don't overwrite — they improve." | LIVE architecture |
| Data for the public good | "The only open organic price index in Israel — no paywall, no registration." | LIVE Market Index |
| Community sourcing | "Four farmer-market sources feed the price index — could yours be next?" | LIVE pipeline |
| Future write-back | "Plan: your farm's harvest data could improve the recommendations for everyone." | PLANNED (WP-CB-5) |

### 5.4 Business Partners and Press (Agricultural press, food industry, investment)

| Theme | Content Ideas | Status Signal |
|-------|--------------|---------------|
| Market data | "Daily organic produce price index from four community sources — open API." | LIVE |
| Data quality | "10+ sources, 5,780+ reconciled enrichment rows, provenance-tracked." | LIVE |
| Platform growth | "66 crops, 14 calculators, daily price updates — built in one quarter." | LIVE |
| Integration | "HMAC-signed ingest API, structured data model, partner-ready architecture." | LIVE |
| Future modules | "Planned: bed planner, task scheduling, farm POS, and operational write-back." | PLANNED |

---

## 6. FAQ-Style Talking Points

### "Is it really free? What is the catch?"

Yes, the Crop Book and Market Index are free, with no registration required and no paywall. The platform is a community project. There is no subscription, no freemium tier on the core tools, and no data monetization. The open posture is a deliberate design choice, not a temporary promotional state. (LIVE)

### "How many crops does it cover?"

66 crops, all with Hebrew names and agronomic data. This includes common vegetables (tomatoes, lettuce, cucumbers, peppers, carrots), herbs (basil, parsley, cilantro), and specialty crops (ginger, turmeric, pak choi, various Mediterranean herbs). Each crop has been enriched from multiple sources. (LIVE)

### "Where does the data come from?"

Ten or more primary sources, including: the JMF MasterClass (Excel planning tool + The Market Gardener book, 240 pages); the Israeli Ministry of Agriculture (שה"מ) variety trials and hydroponic manual; Shaham agronomic bulletins; Idan winter and summer planning guides; Bustan calendar; five years of Tend Israel operational harvest data (2018–2022); the GROWORGANIC Israeli sowing calendar; FRANCHI seed catalog; the Curtis Stone master chart; and four community farmer-market sources for the price index. (LIVE)

### "What is the data confidence model?"

Every data value in the Crop Book has a source class (EX expert / NI curated / PR published / OP operational / MK market / WB web) and a confidence tier determined by a weighted-mean reconciler with outlier gates. The UI shows VALIDATED (≥ τ=0.40 blended confidence), PARTIAL, or INFERRED cues on each field. You can see how confident the data is before using it in a calculation. (LIVE)

### "What are the 14 calculators?"

1. Seed quantity (by target yield and germination rate)
2. Seed cost (by unit price and seed quantity)
3. Tray count (for transplanted crops)
4. Sow date (from target harvest date)
5. Transplant date (from sow date and nursery days)
6. Succession schedule (interval and batch count for continuous supply)
7. Beds for target yield (by yield per bed and spacing)
8. Germination rate (observed vs expected)
9. Expected revenue (by yield and market price)
10. Plant population (plants per bed by spacing)
11. Germination percentage (from tray counts)
12. Market price lookup (live from the enrichment layer)
13. Crop profit comparison (across crops for a fixed bed allocation)
14. Seed and input cost comparison

All calculators use real crop data from the enrichment layer as defaults — not generic numbers. (LIVE)

### "What is the Market Index and how is it updated?"

The Market Index is a community organic produce price index aggregated daily from four Israeli community sources (mashtelatharoe, anatiyot, fruit4soul, finerotem) via an automated Playwright-based scraping pipeline. Prices are normalized by product, unit, and basket tier. The index covers 32+ products and is published daily on sfa.nimrod.bio/market/. (LIVE)

### "Does it work on mobile?"

Yes. The platform is designed responsive-first. Lighthouse mobile score: performance 87+, accessibility 95+, SEO 100. (LIVE)

### "What planning modules are coming next?"

Four future modules are in the roadmap (PLANNED — not built yet): a bed-map/season Planner (WP-CB-2), a crop task scheduler (WP-CB-3), a Sales/POS module for revenue tracking (WP-CB-4), and a Tend integration for operational write-back (WP-CB-5). Each is designed to consume the calculator outputs already built into the Crop Book — the foundation is ready; the downstream modules are next.

### "Is there an API?"

The ingest API is live (POST /api/v1/ingest, HMAC-SHA256 signed) — this is how the backend pipeline pushes data to the delivery tier. It is currently an internal pipeline endpoint, not a public partner API. Partner data feed integration is technically feasible given the architecture. (LIVE pipeline; partner API not yet formalized)

### "What is the business model?"

The platform is currently operated as a community project. There is no paid tier, subscription, or advertising. The long-term business model is not yet finalized. Partnership and sponsorship conversations are open.

---

## 7. Brand Voice Guidelines

| Attribute | Description | Example |
|-----------|------------|---------|
| **Grounded** | Always reference what is real vs planned. Never overclaim. | "66 crops live today" not "hundreds of crops" |
| **Specific** | Numbers and sources over generalities. | "10+ primary sources" not "many sources" |
| **Hebrew-first** | Hebrew is the primary product language. Translations serve the community. | Product UI is Hebrew; marketing can be bilingual |
| **Open and honest** | Acknowledge what is not yet built. The roadmap is public. | "planned, not yet live" for future modules |
| **Technical when needed** | The grower community is sophisticated. Data quality arguments land. | "provenance-tracked" and "confidence tier" are usable terms |
| **Not startup-hype** | Avoid superlatives, "revolutionary," "disrupting," etc. | Describe what the tool does, not how great it is |

---

## 8. Positioning Matrix

| Axis | SFA Position |
|------|-------------|
| Open vs closed | Fully open — no registration, no paywall on core tools |
| Local vs global | Israel-localized — Hebrew, Israeli sources, Israeli growing conditions |
| Community vs corporate | Community-built — price data from growers, knowledge from growers |
| Static vs data-driven | Data-driven — calculators draw from live enrichment layer, Market Index updates daily |
| Beginner vs expert | Both — card/simple view for gardeners; table/full/drill view for market farmers |
| Proven vs aspirational | Proven core (Market Index + Crop Book + 14 calculators LIVE); future modules clearly marked as planned |
