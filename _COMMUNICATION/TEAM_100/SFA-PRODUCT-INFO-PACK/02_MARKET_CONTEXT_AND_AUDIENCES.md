# SFA Market Context and Audiences
**Document:** 02 — Market Context and Audiences
**Product:** SmallFarmsAgents / sfa.nimrod.bio
**Prepared by:** team_100 (Chief Architect)
**Date:** 2026-06-03
**For:** NotebookLM ingestion — go-to-market and product-development planning

---

## 1. The Market: Israel's Organic and Small-Farm Sector

### 1.1 Landscape Overview

Israel has a small but active organic and small-scale farming community. It includes professional market gardeners (חקלאי שוק) who grow vegetables and herbs for direct sale at farmers' markets and through community-supported agriculture (CSA) boxes, home and community gardeners who grow food at a larger-than-hobby scale, and a broader community of learners, students, and food-sovereignty advocates.

The Israeli organic sector is characterized by:

- A small number of certified organic producers relative to the total agricultural base.
- Strong grassroots interest in sustainable, low-input, and regenerative growing methods, partly fueled by the global market-gardening movement popularized by Jean-Martin Fortier (JMF).
- Limited availability of localized, Hebrew-language agronomic reference material. Most internationally recognized market-gardening resources (Fortier's MasterClass, Tend software, Curtis Stone's guides) are in English and not calibrated to Israeli growing conditions, climate zones, or Hebrew crop nomenclature.
- A fragmented price-information landscape. Organic and specialty-produce prices in Israel are not systematically published. There is no open, community-maintained reference for what organic vegetables actually sell for at farmers' markets or farm gates.
- Community-building activity happening in dispersed channels (WhatsApp groups, Facebook communities), without a shared data commons.

### 1.2 Core Problems SFA Addresses

| Problem | Why It Matters | SFA's Response |
|---------|---------------|----------------|
| **Fragmented agronomic knowledge** | Market gardeners and home growers lack a single, localized, Hebrew-language reference for crop planning. JMF and other trusted sources are English-only and not calibrated to Israeli conditions, varieties, and seasons. | The Crop Book (ספר גידולים) — a structured, multi-source agronomic knowledge base for 66 crops, localized to Israel. |
| **No transparent organic price reference** | Producers and buyers have no open benchmark for organic vegetable prices. This disadvantages small producers who cannot negotiate from a shared data baseline. | The Market Index (מחירון שוק) — a community organic price index aggregated from multiple retail and farm sources, published openly with provenance. |
| **Manual, error-prone planning** | Bed allocation, succession scheduling, seed ordering, and revenue estimation are done ad hoc — in spreadsheets or from memory. Errors compound across a season. | Crop Book calculators — 14 deterministic planning tools feeding from agronomic data (yield, spacing, germination rates) so each calculation inherits real crop knowledge. |
| **Sign-up walls and paywalls** | Most digital farm-management tools require registration and charge subscription fees, which creates friction for small and beginning farmers who may not be ready to commit. | Open, no-signup, free-core posture — every public tool is accessible without an account. |
| **Israel-specific blind spots** | International tools do not include Israeli sources, Hebrew plant names, local calendar conventions, or Israeli agricultural extension data. | Multi-source enrichment: the Israeli Ministry of Agriculture (MoA / שה"מ), Shaham bulletins, Idan planning guides, Bustan calendar, and Tend Israel operational data are all integrated alongside the international JMF/MasterClass baseline. |

---

## 2. Positioning Statement

> **SmallFarmsAgents (sfa.nimrod.bio)** is an open, community platform offering free agronomic knowledge and planning tools for Israel's small-farm and organic-growing community — Hebrew-first, no signup required, built on provenance-tracked data from the sources growers already trust.

Short form: **כלים פתוחים לחקלאות קטנה** ("Open tools for small-scale farming")

---

## 3. Differentiators

| Differentiator | What It Means in Practice |
|----------------|--------------------------|
| **Open and free core** | The Crop Book, calculators, and Market Index are fully accessible without an account or payment. No freemium gate on core agronomic functions. |
| **Provenance-backed data** | Every data point has a source class (EX expert / NI curated / PR published / OP operational / MK market / WB web) and a confidence tier. Users can see where a value comes from. The reconciler blends multiple sources into a single best estimate — it does not just show raw scraped data. |
| **Israel-localized** | Hebrew crop names, Israeli seasons, Israeli MoA and Shaham extension data, local market prices, and the Tend Israel operational overlay. Not a translation of an English tool. |
| **Two-audience UX** | The Crop Book is designed for both the gardener audience (card view — approachable, visual) and the market-farmer/table-farmer audience (table view — dense, comparative). Calculators expose simple and full depth levels. |
| **Calculator math tied to crop data** | The 14 planning calculators do not use generic defaults — each draws from the crop_field_enrichment best-estimate values for the specific crop being planned. |
| **Community price index** | The Market Index is not a single retailer's price list. It aggregates from four MyPIPS community sources and normalizes by product and unit. Updated daily. |
| **No lock-in** | No account, no data collection beyond aggregate analytics, no vendor relationship required. |

---

## 4. Audience Map

### 4.1 Market Farmers (חקלאי שוק)

**Profile:** Professional or semi-professional growers selling at farmers' markets (שוק אורגני), through CSA boxes, or wholesale. Typically 0.1–2 hectares under cultivation. Many use raised-bed systems inspired by the market-gardening method.

**Needs:**
- Agronomic planning data calibrated to their scale and crop mix.
- Succession scheduling (when to sow the next batch so supply is continuous).
- Yield estimation, bed allocation, and revenue projection for seasonal planning.
- Price reference to set competitive and fair prices.
- Variety selection guidance anchored to local performance data.

**How SFA Serves Them:**
- Crop Book table view shows all agronomic parameters side-by-side across crops — useful for planning crop mix and rotation.
- Calculators include succession scheduling (#6), beds-for-target-yield (#7), seed quantity (#1–#3), transplant timing (#4–#5), plant population (#10), and revenue/profit comparison (#9, #13, #14).
- Market Index gives weekly community price benchmarks for organic produce.
- Tend operational overlay (OP-class data) feeds real Israeli farm performance data back into the enrichment layer.

**Messaging Hook:** "Plan your season from real data, not guesses — crop spacing, succession timing, and revenue estimates all drawn from what Israeli market gardeners actually grow."

---

### 4.2 Home and Market Gardeners (גננים)

**Profile:** Home gardeners at the ambitious end of the spectrum — growing seriously for household food, sharing with neighbors, or exploring small-scale farming. May be transitioning toward market-farming. Often follow JMF or permaculture methods.

**Needs:**
- Accessible, Hebrew-language guidance on crop planning basics.
- Germination rates, spacing, days-to-maturity, and season windows for common vegetables.
- Simple tools that don't require agronomic expertise to use.
- Visual, approachable presentation.

**How SFA Serves Them:**
- Crop Book card view presents each crop's key parameters visually, with a simple/full depth toggle.
- AssumptionField pattern makes calculators usable without expert knowledge — sensible defaults (germination rate 90%, bed width 80 cm) are shown openly and can be adjusted.
- The Crop Book covers 66 crops with localized Hebrew names and variety information.
- Questions section explains planning concepts in plain language.

**Messaging Hook:** "Everything you need to plan a successful vegetable garden — in Hebrew, without registering, without paying."

---

### 4.3 Learners and Students (לומדים וסטודנטים)

**Profile:** Agricultural students, permaculture-course participants, aspiring market gardeners researching the profession, researchers studying the Israeli organic sector.

**Needs:**
- Reliable, citable reference data for crops.
- Understanding of how organic price indices work.
- Access to methodology and data provenance (not just results).

**How SFA Serves Them:**
- The Crop Book exposes provenance cues — VALIDATED / PARTIAL / INFERRED badges signal data confidence.
- Source classes (EX / NI / PR / OP / MK / WB) are documented and visible.
- Market Index includes methodology transparency (community sources listed, confidence thresholds explained).
- The platform's data model is rigorous: multi-source reconciliation, outlier gates (MAD-based), τ=0.40 validation threshold — appropriate for citation in academic or professional contexts.

**Messaging Hook:** "Agronomic data with provenance — not just numbers, but numbers you can trace."

---

### 4.4 Community Contributors

**Profile:** Growers, researchers, and enthusiasts who want to contribute local knowledge, price observations, or variety data to the commons.

**Needs:**
- A safe, low-friction way to share what they know.
- Confidence that their contributions are handled with data discipline (not just added as noise).
- Recognition that their contribution improves the commons.

**How SFA Serves Them:**
- The /contribute endpoint is available (currently a submit-your-knowledge form — community write-back is a planned feature, not yet live as a structured two-way loop).
- The community feed section surfaces community activity.
- Future Tend integration (CB-5, planned) will create a formal operational write-back path from farm records.

**Messaging Hook:** "Your farm knowledge belongs in a shared commons — contribute and help build the most localized organic farming dataset in Israel."

---

### 4.5 Business Partners

**Profile:** Agricultural input suppliers, seed companies, farm-management software vendors, CSA-box platforms, agricultural extension organizations, and investment/grant bodies interested in the Israeli organic food system.

**Needs:**
- Understanding of the platform's data quality and reach.
- Clarity on the business model and partnership opportunities.
- Proof that the platform serves a real, engaged community.

**How SFA Serves Them:**
- Market Index gives suppliers and buyers a shared price reference.
- Crop Book is a canonical data asset — extensible as a vendor product catalog or agronomic advice layer.
- Open/free-core model creates a large, unregistered audience that can be a channel for partner visibility.
- Data model is API-capable — the ingest pipeline is HMAC-signed, structured, and deployable as a partner data feed.

**Messaging Hook:** "The only open, provenance-tracked organic produce price index in Israel — built on community sources with daily updates and a transparent methodology."

---

## 5. Competitive and Category Context

SFA does not compete directly with any single Israeli product. Its closest category peers are:

| Comparator | Category | Gap SFA Fills |
|------------|----------|---------------|
| Tend (international) | Farm management software | Israel-localized knowledge layer; open/free-core; no signup barrier |
| JMF MasterClass | English-language agronomic education | Hebrew; Israel-specific; interactive calculators |
| Israeli MoA publications (שה"מ) | Official extension data | Consumer-friendly UX; combined with private-sector sources; continuously updated |
| Generic price scraping services | Price data | Community provenance; agricultural normalization; Hebrew nomenclature |
| Spreadsheet-based planning | Farm planning | Pre-populated with crop data; succession/yield logic built in |

SFA occupies a unique white space: open community infrastructure for small-farm knowledge in Israel.

---

## 6. Platform Posture Summary

| Attribute | Value |
|-----------|-------|
| Registration required | No — fully open |
| Core tools free | Yes |
| Language | Hebrew-first; English in code and documentation |
| Data provenance | Always visible — source class + confidence tier |
| Update frequency | Market Index: daily (automated pipeline). Crop Book: continuous enrichment from new sources. |
| Hosting | sfa.nimrod.bio (uPress, Cloudflare edge) |
| Community stance | Open commons — no paywalls, no lock-in |
