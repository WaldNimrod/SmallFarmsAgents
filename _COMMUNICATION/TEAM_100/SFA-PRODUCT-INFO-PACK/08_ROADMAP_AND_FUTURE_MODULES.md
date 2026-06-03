# SFA Roadmap and Future Modules
**Document:** 08 — Delivery Story and Forward Roadmap
**Product:** SmallFarmsAgents / sfa.nimrod.bio
**Prepared by:** team_100 (Chief Architect)
**Date:** 2026-06-03
**For:** NotebookLM ingestion — product planning and partner conversations

> **Reading note:** All programs are described at the value level. Gate mechanics (L-GATE_S/B/V), internal team codes, and AOS governance scaffolding are referenced only where they explain what was built and why. "LOD500_LOCKED" means fully built, validated by a cross-engine external validator, and closed.

---

## 1. Delivery History: What Has Been Built

### 1.1 Pre-AOS Foundation — Milestones M1 through M9 (Early 2026)

Before the current AOS (Agent Operating System) multi-agent delivery framework was adopted, nine milestones delivered the organic market data pipeline:

- **M1–M2:** Database foundation (PostgreSQL, 23 tables, 29 products, 20 sources) and the collection layer (automated scrapers for Israeli organic retail sources).
- **M3–M4:** Normalization engine (alias resolution, unit normalization, confidence scoring, basket-product handling) and aggregation (daily aggregates, weekly snapshots, publish threshold logic).
- **M5–M6:** Admin dashboard (Flask, all pipeline controls from a web UI) and automation (cron scheduler, resilience, alert system).
- **M7:** Public publishing — the first live deployment of the Market Index, originally on www.nimrod.bio via WordPress REST API.
- **M8–M9:** UX polish, site optimization, SEO, plugin cleanup, security hardening.

These milestones established the Market Index pipeline and its daily automated data cycle. The normalizer reached 100% resolution rate (zero unresolvable items) through iterative alias and product catalog work.

---

### 1.2 S001 — AOS Canonization (April 2026)

The project was brought into the AOS multi-agent governance framework. This involved establishing the `_aos/` governance structure, lean-kit snapshot, validation scripts, and team role definitions. Externally validated by a cross-engine validator (Team 190). The primary product value of this program was organizational: it enabled reliable multi-agent, multi-engine delivery for all subsequent programs.

**Value delivered:** Stable governance foundation enabling faster, safer delivery in S002 and beyond.

---

### 1.3 S002 — Public Index Launch (May 2026)

**Goal:** Get the Market Index live with fresh daily data and a clean public presentation.

**What was built (all LOD500_LOCKED):**

| Work Package | What It Delivered |
|---|---|
| WP001 — M10 Thaw | Migrations 032/033; basket_tier_resolver; db/check tooling. Extended the data model for display bucketing. |
| WP002 — MyPIPS Sources | Migration 034 (display_bucket); Playwright-based collector for four community farmer-market sources (mashtelatharoe, anatiyot, fruit4soul, finerotem). These are the community-sourced price observations that give the Market Index its grassroots character. |
| WP003/WP006/WP007/WP008 — Delivery fixes | Resolved a critical pipeline outage (FTPS port-21 block on the home network); migrated uploads to WP REST API on port 443; wired all three upload paths (CLI, scheduler, admin UI) to the new method. Site went live with fresh daily data. |
| WP004 — Mobile UI parity | Responsive design for the market report — the public page works on mobile. |

**Outcome:** The Market Index went live at sfa.nimrod.bio with daily automated data pushes from four community sources, covering 32+ organic products.

---

### 1.4 S003-P001 — Crop Book Foundation (May 2026)

**Goal:** Build the agronomic knowledge base — the Crop Book (ספר גידולים) — from schema through public UI.

**What was built (all LOD500_LOCKED):**

| Work Package | What It Delivered |
|---|---|
| WP001 — Schema Design (LOD200) | Six-table schema: botanical families, crops, varieties, source values, conversion groups, unit conversions. Two-price architecture (documented price vs market price). Source completeness commitment. |
| WP002 — DB Migrations + Seed Importer | Six Alembic migrations (035–040); six ORM models; full importer CLI; 66 crops seeded with Hebrew names and taxonomic data. |
| WP003 — UI Views | Flask Blueprint `/crop-book/`; three routes; eight display tabs; RTL Hebrew layout; search and filter JavaScript; entity tooltips. |
| WP004 — WordPress Integration | SPA HTML + separate JSON data file; mu-plugin shortcode; publish pipeline reusing the existing dispatch_upload infrastructure with a crop_book profile. The Crop Book went live at www.nimrod.bio/crop-book/. |
| WP003-patch02 — Test Harness Cleanup | Resolved accumulated test-suite technical debt from WP003; clean baseline for subsequent work. |

**Outcome:** The Crop Book was live with 66 crops, browsable by the public, with agronomic data served from the database.

---

### 1.5 S003-P002 — Data Enrichment Program (May–June 2026)

**Goal:** Build the multi-source confidence layer and ingest agronomic data from every available trusted source into the Crop Book.

This program had four wave tracks (A through C) and a full UX overhaul. All LOD500_LOCKED.

#### WP-A — Multi-Source Confidence Layer

The most architecturally significant work package. Established:

- **SOURCE_REGISTRY** with seven source classes: EX (expert override), NI (curated institutional/narrative), PR (published structured), OP (operational farm records), MK (market price), WB (web), UC (unclassified).
- **FIELD_POLICY** — per-field rules for how to reconcile multiple source values (weighted mean, hard winner, outlier gate, multi-year operational mean).
- **Reconciler engine** — blends source values into a single best estimate per field per crop variety, with outlier detection (MAD-based gate), calibration harness (CALIBRATED/MARGINAL/MISALIGNED), and provenance output.
- **crop_field_enrichment table** — the output of the reconciler: one winning value per field per variety, with source provenance and confidence tier.
- **validate_enrichment.py** — calibration shadow-run tool for ongoing data quality monitoring.

#### WP-B Waves — Source Ingestion (JMF/MasterClass, PDF, Tend)

- **WP-B1 / patches 01–08:** JMF MasterClass Excel base layer ingested (CROP CHART, CROP ASSOCIATED TASKS, DIRECT SEEDING CHART, NURSERY CHART, CULTIVARS). Full alias extension for the live workbook; Hebrew crop name corrections (phonetic transliterations); botanical taxonomy refinements; cultivar cleanup (baselines-only policy); storage/washing M2M data; variety parser noise cleanup.
- **WP-B2:** JMF PDF extraction — six NIImporter subclasses processing The Market Gardener ebook (240 pages) and Fiche Technique PDFs. LLM-assisted extraction with JSON caching.
- **WP-B3:** Tend Israel adaptation overlay — OP-tier data from Tend TASKS.CSV, GREENHOUSE_PLAN.CSV, and HARVESTS.CSV aggregated into the enrichment layer. Blends with the JMF PR baseline.

#### WP-C Waves — External Sources Integration

Five waves ingesting additional sources, each adding to the crop_field_enrichment and crop_knowledge_notes tables:

| Wave | Sources Ingested | Value Added |
|------|-----------------|-------------|
| C1 | Israeli structured: GROWORGANIC sowing calendar, Idan winter/summer planning, JMF cover crops, Bustan calendar; Tend multi-year backfill (2019/2020/2021, ~358 total harvest rows) | First Israeli-localized structured data; engine v1.1 variety→species inheritance fix (enrichment grew 8.9× to 2,848 rows) |
| C2 | Hebrew narrative: AOSNOT 1.3MB Hebrew per-crop encyclopedia, שה"מ variety trials, שה"מ hydro manual, Dr. Zacks leafy survey, JMF FT extensions | 40 NI knowledge notes across six sources; deep Hebrew agronomic narrative |
| C3 | Curtis Stone OCR (Anthropic Vision API); Idan succession patterns; FRANCHI seed catalog; Tend 2018 | Expanded variety source values; field-specific confidence moderation for DTM rows |
| C4 | Eight web importers from multi-engine scouting (OpenAI, Perplexity, Gemini); Israeli MoA and Shaham planting calendar (56 rows — critical Israeli gap-fill) | Companion matrix, postharvest storage, Israeli government extension data integrated |
| C5 | Data discipline: crop_source_weights table (DB-driven trust-tier weights), data cleanup, EX overrides for confident-knowledge fields | WR (synthesized research) trust tier added; weights tunable via SQL without code deploy |
| C6 | Sparse crops WR synthesis: 19 crops with ≤2 enriched fields expanded to ≥6 fields via Claude-assisted structured synthesis | All 66 crops now have meaningful agronomic data |

#### WP-UI — Design System and UX Overhaul

The platform was migrated from the legacy WordPress/nimrod.bio delivery to sfa.nimrod.bio (Slim 4/PHP on uPress). The design system (team_35 LOD300) was adopted:

- **Brand:** White-green palette (--gj-paper #f8fbf8), fonts Assistant/Frank Ruhl Libre/Carmela, Devora watercolor crop art, RTL Hebrew.
- **Full app-shell** (.sh/.sh__nav) site-wide.
- **Per-crop agronomic data surfaced** on crop detail pages (16-field set from crop_field_enrichment; delta-vs-default highlight).
- **70 crop icon system** — per-crop watercolor art with SVG fallback.
- **72 broken links fixed**; persistent global navigation; species-first detail layout.

---

### 1.6 S003-P004 — Crop Book v1: Calculator-Driven Planning Tool (May–June 2026)

**Goal:** Turn the Crop Book from a read-only reference into an interactive planning tool with 14 calculators.

**What was built (all LOD500_LOCKED as of 2026-06-03):**

| Work Package | What It Delivered |
|---|---|
| WP-CB-0 — Crop Data Model Canon | Foundational architecture document: 6-type field taxonomy (reconciled-numeric, categorical, list, computed, identity, provenance), layer-ownership rules, canonical unit registry, canonical enums, crop_attribute table for categoricals, compute-don't-store rules (plants_per_m², average revenue), future-vision namespace. Cross-engine validated. |
| WP-CB-MIG — Data Model Migration | Eight-phase migration executing the Canon against the live database (head 059): unit normalization, enum canonicalization, crop_attribute table, derived/duplicate field removal, field renames, drop-columns. Views and engine fixed to read the new structure. |
| WP-CB-MIG2 — Data Model Expansion | Thirteen-topic CROP_TOPICS taxonomy; seven new field groups (seeder/seeder_settings, irrigation_type, root_depth_class, common_pests, sale/harvest unit, labor_rate_harvest/wash, plantings_per_season, harvest_weeks_span); needs_summer_shade ratified; Canon expanded to v1.3.0. Migration 060. |
| WP-CB-1 — Calculator Tool | 14 calculators (pure Python functions + JavaScript parity): seed quantity, seed cost, tray count, sow date, transplant date, succession schedule, beds-for-target-yield, germination rate, expected revenue, plant population, germination percentage, market-price lookup, crop-profit comparison, seed/input cost. AssumptionField pattern (germination_rate=90%, bed_width=80cm). Two-audience UX: card view (gardener) / table view (farmer); Simple/Full/Drill-down depth; complete/partial state (τ=0.40). |
| WP-CB-1-patch01 | JS↔Python parity for calcs #7/#9/#12; server-side filters on book_index; /calc PDF/CSV export; watercolor art wiring (28 crop masters). |
| WP-CB-UI-ALIGN (Class A) | Visual alignment to team_35 LOD300: cream palette killed (--gj-paper #f8fbf8 everywhere); .sh app-shell site-wide; /calc fixed (14 calcs surfaced, JS loaded); crop pages humanized (Hebrew enum labels replacing raw DB keys). |
| WP-CB-UI-CLASSB (Class B) | Seven new UX surfaces: hub/home, market list+detail, search, community, about, account shell. classb.css/js adopted from team_35; AccountController; 7-route test suite; all surfaces LIVE on sfa.nimrod.bio. |
| WP-CB-DATA — Enrichment Mirror | crop_field_enrichment and crop_attribute mirrored to the uPress MySQL delivery tier (migrations 004/005 on the delivery DB; 1,010 rows pushed). /calc book-chips now bind from live data; crop pages read structured provenance from the tables. LIVE as of 2026-06-03. |

---

## 2. Current Live State (as of 2026-06-03)

| Feature | Status | URL |
|---------|--------|-----|
| Market Index (מחירון שוק) | LIVE — daily automated updates | sfa.nimrod.bio/market/ |
| Crop Book browse (66 crops, Hebrew) | LIVE | sfa.nimrod.bio/crop-book/ |
| Crop Book calculators (14) | LIVE | sfa.nimrod.bio/calc/ |
| Crop detail pages with agronomic data | LIVE — 1,010 enrichment rows live | sfa.nimrod.bio/crop-book/{slug} |
| Search | LIVE | sfa.nimrod.bio/search |
| Community section | LIVE (feed = static placeholder; community write-back not yet live) | sfa.nimrod.bio/community |
| About | LIVE | sfa.nimrod.bio/about |
| Account | LIVE as UI shell — "coming soon" (בקרוב); no auth backend yet | sfa.nimrod.bio/account |

**Data pipeline:** Market Index data is scraped daily from four MyPIPS community sources, normalized by the OrganicMarketAgent pipeline running on waldhomeserver, and pushed to the uPress MySQL mirror via HMAC-signed API. Crop Book data is enriched on the Mac-hosted PostgreSQL database and pushed manually (server DB alignment pending as a separate operational follow-up).

---

## 3. Future Modules (LOD100 Placeholders — Not Built)

These four modules are formally registered as future work. They are NOT built, NOT funded, and NOT scheduled. They are LOD100 direction briefs — enough to ensure WP-CB-1 designed stable API contracts they can consume.

Each module is a consumer of Crop Book calculator outputs. The Crop Book is the agronomic knowledge and calculator layer; these modules extend it into operational planning, task management, sales, and farm-data feedback.

> **Status clarity:** These modules are FUTURE and PROPOSED. Nothing below is shipped or under active development. They are documented here for product-planning and partner-conversation purposes.

---

### 3.1 WP-CB-2 — Planner v0 (Bed-Map / Season Plan)

**Purpose:** Allow a grower to assign specific crops to physical beds and build a season plan.

**Consumes from Crop Book:**
- `beds_for_target_yield` (Calculator #7) — tells the Planner how many beds a target harvest requires.
- `plant_population` (Calculator #10) — density per bed.
- `succession_schedule` (Calculator #6) — when to sow successive batches.
- Sow and harvest dates (Calculators #4/#5).

**Value:** Turns calculator outputs into a concrete spatial and temporal plan. A grower inputs "I want 20kg of tomatoes per week from Week 14 to Week 30" and gets a bed layout and sowing schedule — derived entirely from Crop Book data, not from guesses.

**Owns:** Scheduling logic and bed layout. Does not re-derive agronomic truth — reads it from Crop Book.

---

### 3.2 WP-CB-3 — Tasks (Crop Task Scheduling)

**Purpose:** Generate dated field tasks from a planting plan.

**Consumes from Crop Book:**
- `crop_task_templates` — already seeded from the JMF MasterClass (CROP ASSOCIATED TASKS sheet), anchored on sow/transplant/harvest dates.
- Sow and harvest dates (Calculators #4/#5).
- Seed and tray procurement timelines (Calculators #1/#3).

**Value:** A grower knows not just when to sow but what to do each day — seeding trays, transplanting, irrigation changes, harvest windows — all calculated from the crop's agronomic profile.

**Owns:** Task timeline. Reads anchors from Crop Book and Planner.

---

### 3.3 WP-CB-4 — Sales / POS

**Purpose:** Revenue planning and point-of-sale integration.

**Consumes from Crop Book:**
- `expected_revenue` (Calculator #9).
- `crop_profit_comparison` (Calculator #13).
- `seed_input_cost` (Calculator #14).
- `documented_price` — the farm-gate price from the enrichment layer.
- OMA Market Index (MK-class source) — live market price reference for comparison.

**Value:** Connects agronomic planning to financial reality. A grower can project revenue from a planned crop mix, compare actual vs expected, and integrate with point-of-sale (market stall or CSA).

**Owns:** Transactions. Reads economics from Crop Book.

---

### 3.4 WP-CB-5 — Tend Integration (Operational Write-Back Loop)

**Purpose:** Feed real farm operational data back into the enrichment layer, closing the loop between the knowledge base (what crops should yield/cost) and farm reality (what they actually yield/cost on a specific farm).

**Consumes from Crop Book:**
- `crop_field_enrichment` — the current best-estimate values.
- Provenance and source class metadata.

**Writes:**
- OP-class (operational) source values that participate in the reconciler — a Tend farm's actual harvest data becomes a weighted input to future enrichment runs.

**Value:** The Crop Book becomes a living document — it learns from what farms actually produce. Individual farms benefit from collective knowledge; the collective benefits from individual operational data.

**Owns:** The operational feedback loop. Has sanctioned write access to OP-class source values only.

---

## 4. Server-Side Ideas Backlog (PROPOSED — Unapproved)

The following ideas were surfaced during the WP-CB-DATA and Class B UI build sessions. Each was explicitly **not** implemented — they are logged here with provenance for future triage. None are approved, funded, or scheduled.

> **Status:** All entries are PROPOSED. team_00 decides if any becomes a real work package. Nothing below is live or under development.

| ID | Idea | Source | What / Why | Blast Radius | Status |
|----|------|--------|-----------|--------------|--------|
| SRV-1 | Server-side search ranking / full-text index | team_50 E2E QA; team_35 §3.4 suggestions | Current `/search` uses `hebrew_name LIKE`. A ranked or fuzzy index would improve relevance and power suggest-as-you-type. | Search controller, possibly a search index/table | PROPOSED — unapproved |
| SRV-2 | Market graph 90-day and yearly aggregates | team_35 §3.3 graph range selector | History API currently serves ≤28 days. 90-day and yearly ranges would require pre-computed aggregates. | Ingest/aggregation pipeline + history endpoint | PROPOSED — unapproved. UI shows these ranges as disabled (בקרוב). |
| SRV-3 | Account authentication backend | team_35 §3.7 account surface | Real login/profile/subscription flows behind the v1 account UI shell. | New auth subsystem | PROPOSED — unapproved. Current UI is a shell with "coming soon" copy. |
| SRV-4 | Market price data freshness | team_50 finding F-MKT-002 | The uPress MySQL mirror is not currently populated with `last_price`/`product_prices` rows for the price history display. | OMA ingest pipeline / sfa_ingest_push | PROPOSED — unapproved (data/ops, not UI) |
| SRV-5 | Live hub stats (real DB counts on tiles) | team_50 VISUAL_QA | Hub tiles show static counts from configuration (e.g., "66 גידולים / 30 מוצרים"). Live counts would track real DB state. | Hub controller + counts query/endpoint | PROPOSED — unapproved. Class B design intentionally uses static counts. |

---

## 5. Roadmap Summary View

```
COMPLETE (LOD500_LOCKED)
│
├─ M1–M9     Core pipeline + admin + public market index (www.nimrod.bio era)
├─ S001      AOS canonization (governance + multi-agent framework)
├─ S002      Market Index public launch (sfa.nimrod.bio, MyPIPS sources, daily data)
├─ S003-P001 Crop Book foundation (66 crops, schema, importer, UI)
├─ S003-P002 Multi-source enrichment (reconciler, 7 source classes, ~5,780+ enrichment rows)
│   ├─ WP-A  Confidence layer + reconciler engine
│   ├─ WP-B  JMF/MasterClass + Tend Israel ingestion
│   ├─ WP-C  Israeli ext. + Hebrew narrative + web sources + cleanup
│   └─ WP-UI Design system adoption (sfa.nimrod.bio, team_35 LOD300)
└─ S003-P004 Crop Book v1 (calculators + two-audience UX + enrichment mirror)
    ├─ WP-CB-0   Data model Canon (field taxonomy, units, enums, attributes)
    ├─ WP-CB-MIG Migration executing the Canon
    ├─ WP-CB-MIG2 13-topic taxonomy + 7 new field groups
    ├─ WP-CB-1   14 calculators + AssumptionFields + two-audience UX
    ├─ WP-CB-1-p01 Parity, filters, export, watercolor art
    ├─ WP-CB-UI-ALIGN Class A visual alignment (app-shell, humanized labels)
    ├─ WP-CB-UI-CLASSB Class B surfaces (hub/market/search/community/about/account)
    └─ WP-CB-DATA Enrichment mirror to uPress MySQL (book-chips + structured provenance LIVE)

FUTURE (LOD100 PLACEHOLDER — not built, not scheduled)
│
├─ WP-CB-2  Planner v0 (bed-map / season plan)
├─ WP-CB-3  Tasks (crop task scheduling from templates)
├─ WP-CB-4  Sales / POS (revenue planning + farm-gate transactions)
└─ WP-CB-5  Tend integration (operational write-back loop)

PROPOSED (ideas register — unapproved)
│
├─ SRV-1  Search ranking / full-text index
├─ SRV-2  90-day / yearly market aggregates
├─ SRV-3  Account auth backend
├─ SRV-4  Market price data freshness
└─ SRV-5  Live hub stats
```
