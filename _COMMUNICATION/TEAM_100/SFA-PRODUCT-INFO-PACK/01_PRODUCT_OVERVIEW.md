# SFA — SmallFarmsAgents: Product Overview

**Document type:** Product information — overview layer
**Date:** 2026-06-03
**Status:** Live product, active development
**Audience:** NotebookLM research corpus; go-to-market planning; product strategy

---

## Abstract

SmallFarmsAgents (SFA) is an open-access, community-anchored digital platform serving Israel's organic and small-farm sector. Live at **sfa.nimrod.bio**, it delivers two complementary products — a **Crop Book** (ספר גידולים) that transforms agronomic reference data into a calculator-driven planning tool, and a **Market Index** (מחירון) that publishes a transparent, rolling community price index for organic produce. The platform is free at its core, requires no account creation to use, and is designed around the principle of radical transparency: every data point — price observation, agronomic value, or planning assumption — carries its source, confidence level, and freshness so that users can trust what they see. SFA is built for the specific conditions of Israeli organic agriculture: Hebrew-first UX, Israeli market channels, local farm varieties, and the realities of small-plot operation.

---

## 1. Mission and positioning

### 1.1 Mission statement

SFA's mission is stated in its own headline: **"כלים פתוחים לחקלאות קטנה"** — open tools for small farming. The platform exists because Israel's small-farm and organic-garden community lacked a single, trustworthy, free source for two critical planning inputs: agronomic planning knowledge (how to grow) and market pricing knowledge (what things are worth at the source).

### 1.2 Positioning

| Dimension | SFA's position |
|-----------|----------------|
| Access model | Open core — free to use, no signup required for core features |
| Data model | Community-sourced, multi-provider, transparent provenance |
| Primary language | Hebrew (UI, product names, community content); English in technical layer |
| Geography | Israel — local farm channels, Israeli market prices, Israeli climate context |
| Technology | Slim4/PHP + MySQL front-end on uPress (sfa.nimrod.bio); Python/PostgreSQL data pipeline on waldhomeserver |
| Tone | Honest and practical — "no silent magic"; missing data is shown as missing, not hidden |

### 1.3 Open/free philosophy

SFA is not a SaaS product trying to acquire paying users. Its free-tier tools (Crop Book and Market Index) are genuinely free — no freemium gate, no login wall, no "premium features" lock. The five-tier product ladder (explained in §4) reserves paid tiers for advanced operational tools (client management, field journal, custom integrations) that require account infrastructure. The foundation — knowledge and market data — remains permanently open.

---

## 2. The three pillars

### 2.1 Crop Book — agronomic knowledge as planning tool

The **Crop Book** (ספר גידולים) is a multi-source agronomic knowledge base for ~66 crops and ~368 varieties, organized around a 13-topic taxonomy (species identity, planting calendar, nursery, spacing/population, yield, market/price, fertility/nutrition, frost/climate, succession, harvest, postharvest storage, equipment/seeder, companions/rotation). The core product decision that defines the Crop Book — in contrast to a conventional reference guide — is that the data is not merely displayed but wired into **14 calculators** that turn it into field-ready planning outputs: how many seed grams to buy, how many nursery trays to prepare, when to sow if you want to harvest on a specific date, how many beds you need for a target yield, what fertilizer rate to apply, which crops are most profitable per bed-meter.

The Crop Book is the platform's deepest product and the longest-running development program (S003, spanning multiple months and dozens of work packages).

### 2.2 Market Index — community price transparency

The **Market Index** (מחירון) is a rolling community price index for organic produce in Israel. It aggregates price observations from multiple sources — including MyPIPS farm-shop data — normalizes them against a product catalog, computes rolling averages and price ranges, and publishes the result with explicit freshness indicators. The index is honest about its limitations: it is not a replacement for any single seller's pricing but a transparent community signal of what organic produce costs at the source.

The mandatory disclaimer on every market page names what the data is, where it comes from, why it exists, and what it is not — a design choice that reflects the platform's transparency-first values.

### 2.3 Future operational modules

SFA's roadmap (S004 and beyond) extends the platform toward operational tools: a field **Planner** (bed maps driven by Crop Book calculator outputs), a **Task manager** (sow/transplant/harvest task sequences from calculator date outputs), a **Sales/POS** module (revenue and margin tracking), and a **Tend integration** (write-back loop for real farm data to improve agronomic confidence scores). These modules are architecturally pre-wired — the Crop Book v1 calculators already specify typed output contracts for downstream consumers — but are not yet live.

---

## 3. Current live product and technical status

### 3.1 Live URLs and delivery topology

The live site is served from **uPress** at **sfa.nimrod.bio** (Slim4/PHP 8 + PDO/MySQL). The backend data pipeline — scrapers, the PostgreSQL data store, the enrichment engine, and the publish push — runs on **waldhomeserver** (a home server acting as the deploy relay). End users never interact with the home server; they see only the uPress-hosted front-end.

| Component | Location | Technology |
|-----------|----------|-----------|
| Web front-end (public) | uPress sfa.nimrod.bio | Slim 4 / PHP 8, MySQL read-mirror |
| Data pipeline + Postgres | waldhomeserver | Python 3.11, PostgreSQL 15, Docker |
| Deploy relay | waldhomeserver (allowlisted egress) | lftp FTPS to uPress |
| Ingest API | sfa.nimrod.bio/api/v1/ingest | HMAC-SHA256 signed POST |

### 3.2 What is live today

- **Crop Book** — live at sfa.nimrod.bio/crop-book/. Full agronomic knowledge base for ~66 crops / ~368 varieties. Multi-source enriched data with confidence and provenance cues. Per-crop detail pages with 8 content tabs. Two-audience UX (gardener cards / farmer table). A dedicated calculator dashboard (/calc/) exposing all 14 calculators. The complete/partial state system (VALIDATED / UNVALIDATED / MISSING per field, with τ=0.40 confidence threshold).
- **Market Index** — live at sfa.nimrod.bio/market/. Rolling price index for organic produce. Multi-source collectors including MyPIPS (Playwright-based). Freshness pills (fresh 0–3 days / aging 4–7 / stale 7+). Cards and table density toggle. Per-product detail pages with 7-day and 28-day price history graphs (90-day and year-range disabled pending aggregate data).
- **Hub/home** — sfa.nimrod.bio/. Module grid with open tools and coming-soon tiles. Audience entry cards (gardener / farmer / planner).
- **Community** — sfa.nimrod.bio/community/. Feed-less manifesto + request/suggest form. No social feed (deliberate design: avoid noise, focus on knowledge contribution).
- **About/tiers** — sfa.nimrod.bio/about. Five-tier product ladder explained.
- **Account** — shell page ("coming soon").

### 3.3 Data status

- Crop Book: 66 crops, 368+ varieties in PostgreSQL. Multi-source enrichment pipeline (7 source-class taxonomy: EX expert override, NI Nimrod input, PR primary reference, OP operational farm data, MK market sourced, WB web-research, UC user-contributed). Two fields wired for calculator use specifically this phase: `days_in_nursery_cell` and `succession_interval_weeks`.
- Market Index: 65+ products in the MySQL read-mirror. 25 total sources, including 4 MyPIPS community shop sources (mashtelatharoe, anatiyot, fruit4soul, finerotem). Daily automated data push from waldhomeserver to uPress.

---

## 4. Product tier ladder

SFA uses a five-tier access model displayed on the /about page:

| Tier | Hebrew label | What it includes | Access |
|------|-------------|-----------------|--------|
| **Open** | פתוח | Crop Book, Market Index, Calculator dashboard | Free, no signup |
| **Beta** | בטא | Field calculator in active development | Free, feedback requested |
| **Coming** | בקרוב | Field journal and planning modules | Not yet available |
| **Paid** | תשלום | Client manager, yield tracking | Subscription (future) |
| **Custom** | מותאם | Tend integration, custom farm integrations | Contact-based |

The open tier is genuinely free and complete — not a stripped-down version. Paid tiers address operational overhead that justifies recurring cost (client billing, advanced tracking).

---

## 5. Value proposition per audience

### 5.1 Home / market gardener (גינאי ביתי)

- Access to an agronomic knowledge base that consolidates JMF MasterClass planning data, expert overrides, and community-sourced values into a single, reliable reference.
- 14 calculators that handle the math of seed buying, tray sizing, succession timing, yield estimation, and plant population — without spreadsheets.
- Honest about data gaps: calculators are disabled (not silently wrong) when a required data field is missing.
- Accessible via the Cards view — crop cards with key numbers at a glance, suitable for mobile browsing.

### 5.2 Small / organic farmer (חקלאי קטן)

- Everything the gardener gets, plus farmer-specific tools: beds-for-target-yield, succession scheduling, expected revenue, crop profit comparison, and fertilizer/compost rate calculators.
- Table view — compact, multi-crop comparison in a farmer-density layout.
- Market Index with rolling price averages and source counts — a community-sourced signal for pricing decisions, not a replacement for market relationships.
- Complete/partial crop state makes it easy to see which crops have well-validated data (all calculators enabled) and which are still being built out.

### 5.3 Learner / student

- The Crop Book's Simple / Full / Drill-down depth model lets learners start with headline values and dig into source provenance and confidence levels at their own pace.
- Explainers attached to every AssumptionField (e.g., why germination rate defaults to 90%, what bed width 80 cm means) link to published content on nimrod.bio.
- Free and no-login — no barrier to explore.

### 5.4 Community / contributor

- Community page with request/suggest form — anyone can ask for a missing crop, flag an error, or suggest a price observation.
- Market Index's contribute prompt surfaces the mechanism for price data contributions.
- Platform design invites contribution without making it mandatory — the data is useful without a user account.

### 5.5 Business partner / agronomist

- API-quality data structure (confidence scores, source provenance, field states) suitable for integration with farm management software.
- Typed calculator output contracts (date sequences, bed-meter outputs, revenue/margin figures) designed as stable APIs for downstream operational tools.
- Custom tier for direct Tend integration, field journal connection, or bespoke farm-specific tooling.

---

## 6. Design principles

1. **No silent magic** — missing data shows "—" and a "request info" prompt; low-confidence data shows an asterisk; freshness shows a color-coded pill. Nothing is hidden.
2. **Open by default** — core tools require no account. The tier ladder exists, but the free tier is not crippled.
3. **Community-sourced, expert-anchored** — price and agronomic data come from community sources, but expert overrides (EX/NI trust classes) take precedence where available and are visually distinguished.
4. **Hebrew-first UX** — all user-facing content is in Hebrew. English appears only in technical internals. Product names and market data reflect Israeli terminology.
5. **Two audiences, one dataset** — the same underlying data powers both the gardener (Cards) and farmer (Table) view. Audience switching changes density and which calculators are foregrounded, not the data itself.
6. **Honest empty states** — if there is no price data, the card says so. If a calculator is disabled because a required field is missing, it explains which field and why.

---

## 7. Roadmap summary (current phase)

The current active program is **S003-P004** — Crop Book v1, the calculator-driven planning tool layer. This builds on the completed enrichment data layer (S003-P002) which established the multi-source confidence infrastructure, loaded the JMF MasterClass Excel data, and operationalized the reconciler. S003-P004 adds the 14 calculators, the AssumptionField pattern, the complete/partial state UI, and the two-audience experience (Cards/Table with Simple/Full/Drill-down depth).

Future programs (S004+) will build the Planner (bed maps), Tasks, Sales/POS, and the Tend integration, using the typed output contracts that the Crop Book v1 calculators already specify.

---

*Sources: PROJECT_VISION_AND_SYSTEM_MAP.md, _aos/context/PROJECT_CONTEXT.md, _aos/roadmap.yaml, sfa_delivery/templates/pages/hub_home.php, hub_tiers.php, community.php, _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md, LOD400_spec.md.*
