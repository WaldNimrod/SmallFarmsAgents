# Glossary & Key Facts — accuracy anchor for SFA

> **Purpose:** the canonical fact sheet. When generating any material, ground numbers and capability claims here, and **respect the status tags**: **LIVE** = shipped on sfa.nimrod.bio (2026-06-03) · **PLANNED** = future module, direction only, not built · **PROPOSED** = idea backlog, unapproved. Do not present PLANNED/PROPOSED as shipped.

## Identity & positioning
- **SFA** = SmallFarmsAgents. **Live site:** https://sfa.nimrod.bio (LIVE).
- **Positioning:** "כלים פתוחים לחקלאות קטנה" — *open tools for small-scale farming*. **Open · no signup · free core.**
- **Market:** Israel's organic / small-scale farming (market farmers, gardeners, learners, community).
- **Language:** UI is Hebrew, RTL. This documentation pack is English.

## The two live products
- **Crop Book (ספר גידולים)** — agronomic knowledge base + calculator-driven planning tool. **LIVE.**
- **Market Index / OrganicMarketAgent (מחירון / OMA)** — community organic-produce price index. **LIVE.**
- **Content surfaces (Class B):** hub/home, market list+detail, search, community, about/tiers, account-shell. **LIVE.**

## Canonical numbers (verify against these)
- **Crops:** ~**66**; **varieties:** ~**368**. (Crop Book data set.)
- **Calculators:** **14** (planning tool, WP-CB-1). **AssumptionFields:** **8** keys (e.g. germination_rate default **90%**, bed_width default **80 cm**).
- **Crop topics taxonomy:** **13** topics (CROP_TOPICS).
- **Confidence validation threshold:** **τ = 0.40** → `field_state` = VALIDATED / UNVALIDATED / MISSING (VALIDATED if confidence ≥ τ OR a high-trust source class wins).
- **Source classes:** 7-class trust hierarchy (e.g. **EX** expert, **NI** narrative-inferred, **PR** parsed-records, **OP** operational, **MK** market, **WB** web, **UC** unconfirmed) — see doc 05 for the authoritative list + weights.
- **Field taxonomy types:** T1 reconciled-numeric (enrichment) · T2 categorical · T3 list · T4 derived (computed, not stored) · T5 identity · T6 provenance.
- **Market freshness window:** **7 days** rolling; pills = fresh / aging / stale. Graph ranges **7-day + 28-day LIVE**; **90-day / yearly = disabled** (aggregates not yet built → PROPOSED SRV-2).
- **Enrichment mirror (WP-CB-DATA):** ~**767** `crop_field_enrichment` + ~**243** `crop_attribute` rows pushed live (≈**1010** rows). **LIVE.**

## Architecture facts
- **Backend:** Python 3.11, Flask, **PostgreSQL** (canonical SSoT, `oma-postgres`, alembic head ~060), SQLAlchemy 2.x + Alembic, Docker, httpx; Playwright for some collectors.
- **Delivery tier:** **Slim 4 / PHP 8 + PDO/MySQL**, served from **uPress** at sfa.nimrod.bio.
- **Data transport:** canonical Postgres → MySQL mirror via an **HMAC-signed ingest API** (`sfa_ingest_push.py` → `POST /api/v1/ingest`); idempotency-keyed upsert.
- **Three-host topology (NEVER conflate):**
  | Role | Machine | Serves end users? |
  |------|---------|-------------------|
  | Web host + live MySQL | **uPress** (sfa.nimrod.bio) | **YES — only here** |
  | Backend / pipeline (Postgres SSoT, scrapers, cron) | **waldhomeserver** | No |
  | Deploy / push relay (FTPS, egress IP allowlisted) | **waldhomeserver** | n/a (relay) |
- **Design system:** white-green v2 (`--gj-*` tokens, paper `#f8fbf8`); fonts Assistant (body) + Frank Ruhl Libre (headings) + Carmela (wordmark); watercolor crop art; `.sh` app-shell; RTL.

## Status of capabilities
- **LIVE:** Crop Book (66 crops, 14 calculators, AssumptionFields, two-audience Cards/Table UX, Simple/Full/Drill depth, complete/partial state, provenance cues, CSV/print export); Market Index (multi-source incl. MyPIPS, rolling averages, freshness, disclaimer, list+detail, 7/28-day graph); all Class B surfaces; the enrichment data binding `/calc` book-chips + crop-page structured provenance.
- **PLANNED (future modules — LOD100 direction only, NOT built):** **CB-2 Planner v0** (bed-map / season plan) · **CB-3 Tasks** (crop task scheduling) · **CB-4 Sales / POS** · **CB-5 Tend integration** (operational write-back loop). Each consumes Crop Book calculator outputs.
- **PROPOSED (server-side ideas backlog — unapproved):** **SRV-1** search ranking / full-text index · **SRV-2** market 90-day/yearly aggregates · **SRV-3** account auth backend · **SRV-4** market price-data freshness (mirror price rows) · **SRV-5** live hub stats.

## Key terms
- **AssumptionField** — a first-class UI pattern: a user-adjustable default (e.g. germination 90%) feeding a calculator, with an explainer + link.
- **field_state** — backend-stamped trust label per field (VALIDATED/UNVALIDATED/MISSING); the UI renders it verbatim (no client-side threshold math).
- **value_best / winning_source_class / confidence_score** — the reconciled point estimate, the trust class that won, and its confidence, per (crop, field).
- **two-audience UX** — Cards view (gardener) vs Table view (market farmer), same data.
- **complete / partial crop** — a crop is COMPLETE iff all mandatory fields are VALIDATED; otherwise PARTIAL.
- **AOS** — the multi-agent delivery organization/governance behind the build (lean-gate ladder, cross-engine validation). Internal process context, not a customer-facing feature.

## Do-not-state (common pitfalls for generated copy)
- Do **not** say the site is hosted on the home server or on WordPress/`www.nimrod.bio` — it is the Slim4/PHP app on **uPress** (`sfa.nimrod.bio`).
- Do **not** present Planner/Tasks/POS/Tend or any SRV idea as available — they are PLANNED/PROPOSED.
- Do **not** imply paid tiers for the core — the core is **free**; "tiers" refers to an access/capability ladder (community → beta → advanced/custom), with several levels still "בקרוב/coming".
- Do **not** invent crop counts, prices, or accuracy figures beyond those above; agronomic values carry provenance/confidence and are not guarantees.
