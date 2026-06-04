# BRIEF — SFA Vision Re-Lock & Platform Direction

**ID:** SFA-VISION-RELOCK-001
**Version:** 1.0.0
**Date:** 2026-06-04
**Author:** Team 100 (Architecture / Chief Architect)
**Status:** APPROVED IN-SESSION by Team 00 (Nimrod) — vision phrasing locked; open DECISIONS logged below
**Type:** Strategic planning brief (post base-layer; pre new-development)
**Supersedes for vision intent:** the stale `roadmap.yaml` `project.notes` definition ("price index for organic vegetables") as the *sole* product description. The price index becomes one input pillar, not the whole product.

---

## 0. Executive Summary

After completing the SFA base layer (price index pipeline + Crop Book + 14 calculators + delivery tier), this session charted the next phase: **adopt an existing open-source farm-management platform as the operational Delivery Tier, wrap it headless to a Hebrew-first product, and grow it into the daily operating system of the small farm.**

Two decisions are locked:
1. **Vision re-lock** — north star, mission, 5 pillars, audience, monetization model.
2. **Platform direction** — **farmOS** selected (over LiteFarm), used **headless** (our own frontend), delivered in **three tiers** (no-account / rented sandbox / permanent instance).

A competitive comparison across *several* additional systems (to map the full schema space) is deferred to the **next session** as the lead follow-up task.

---

## 1. VISION RE-LOCK

### North Star (the dream)
> **"מערכת ההפעלה של החווה הקטנה — הדף שכל מגדל פותח בבוקר."**
> *The operating system of the small farm — the page every grower opens in the morning.*

### Mission (the scope)
An **end-to-end envelope** — from profitable planning, through daily field execution, to sales and customers — with a **local (Israeli) agronomic-economic brain** at its core.

### The 5 Pillars
| # | Pillar | What | Provided by |
|---|--------|------|-------------|
| 1 | **Plan** | What/when/how-much to grow; profitability | 🧠 SFA brain (Crop Book + 14 calculators) |
| 2 | **Execute** | "What do I do today"; field tasks; logging | farmOS operational layer + our frontend |
| 3 | **Sell** | Orders, market, pricing | Integration + the price index |
| 4 | **Relate** | CRM, CSA members, customers | Integration (external sales/CRM system) |
| 5 | **Improve** | Data loop, profitability, benchmarking | 🧠 SFA reconciler + analytics |

The **"morning cockpit"** is the unifying surface across all five — and it is the **headless frontend we own**. Role-aware: **Manager** sees planning/profitability; **Worker** sees today's field tasks (maps to farmOS roles Manager/Worker/Viewer).

> **Discipline:** the north star is the *dream* (full cockpit). What we build *first* is the **wedge** (free Crop Book + profitability calculators = brand front). This prevents "build everything at once."

### Audience
- **Primary depth / paying:** small **commercial market gardeners** (JM Fortier / bio-intensive style) — few, but it's a business, with real willingness to pay for tools that make/save money. This is what the notebookLM spec targets (beds, bed-meters, succession).
- **Brand engine / community:** **home / private growers** — already Nimrod's course customers; values-aligned; **they establish the brand** both for SFA and for Nimrod as a domain consultant. The free tier brings the (mostly budget-less) community in to know the system → which **generates downstream work** (courses, consulting, custom development).

### Monetization — **Freemium + strong indirect**
- **Direct:** rented-sandbox (pay-per-use) + permanent-instance (subscription) + custom development for clients.
- **Indirect (possibly larger):** the free tier is a **brand & lead-gen asset** for Nimrod's broader business (courses, consulting, custom projects). The free tier's ROI is measured substantially in **brand, trust, community** — not only in paid conversion.
- **Strategic implication:** because the free tier is the brand surface, the **free Crop Book + calculators in Hebrew, beautifully done, are the most critical thing to nail first.** Paid farm-management (farmOS) comes after.

---

## 2. PLATFORM DECISION — farmOS (headless)

**Selected: farmOS.** Decisive advantages over LiteFarm:
1. **API built for integration** — documented JSON:API + OAuth2 + official `farmOS.py` client. (LiteFarm's REST API is internal-only to its own SPA — no public contract, no webhooks, no OpenAPI → brittle across upgrades.)
2. **Flexible data model** — Asset/Log/Quantity/Term + custom fields can hold our 13-topic taxonomy and `value_best`/validated-state provenance. (LiteFarm's schema is rigid; no generic custom-field mechanism.)
3. **Blessed, documented self-host** (Docker) — aligns with our waldhomeserver discipline. (LiteFarm self-host is feasible but unsupported/undocumented.)

**LiteFarm's decisive negatives:** **0 RTL / 0 Hebrew** (8 LTR locales; RTL retrofit into a 17k-commit React app is a major ongoing effort) + internal-only API. *Its strengths (modern UI, multi-tenancy, organic-certification tooling) did not outweigh these for our case — and the headless decision neutralizes its UI advantage.*

**Mode: HEADLESS.** We build our own product-grade Hebrew/RTL frontend against the JSON:API; we do **not** wrap the dated Drupal theme. This simultaneously solves (a) UX quality, (b) Hebrew/RTL (we own 100%), and (c) GPL boundary (our engine/calculators/frontend are separate processes over HTTP → not derivative works).

---

## 3. DELIVERY ARCHITECTURE — Three Tiers

All three are served by the same headless frontend + the SFA engine (SSoT + 14 calculators).

| Tier | What | Persistence | Cost to us | Pays |
|------|------|-------------|-----------|------|
| **A — No account** | Crop Book + 14 calculators + plan + export, anonymous | browser session / draft | ~0 (stateless, ∞ concurrency) | free |
| **B — Rented sandbox** | Full farmOS, spun up on demand for hours/days | "bundle" loaded → ephemeral container → saved + reset on end | per-use orchestration | pay-per-use 💰 |
| **C — Permanent instance** | Always-on farmOS for serious operators | live volume, always mounted | instance-per-farm | subscription 💰💰 |

### The "bundle" concept (unifies the tiers)
The user's data = a **DB/volume snapshot** (lossless), NOT a field-by-field logical export. Same concept, different lifecycle:
- Tier A: bundle in browser session (ephemeral).
- Tier B: bundle in cheap storage → restored into an ephemeral container on rental → saved back → container reset.
- Tier C: bundle IS the always-mounted live volume.

**Promotion ladder (natural upgrades):** anonymous draft → "save as bundle" (→ Tier B) → "keep always-on" (→ Tier C).

### Why the rented sandbox (Tier B) is strategically strong
- Fits **farming seasonality** (intense planning a few times/year, not continuous).
- **Kills the upgrade-debt problem** of Tier 1 multi-tenancy: ephemeral instances always boot the *current* farmOS version + import the bundle → no per-instance accumulated upgrade debt.
- Embodies the **open model / data ownership** Nimrod values — the user holds their bundle and can leave (even self-host) → zero lock-in.

### Tier B — non-negotiable safety (the #1 risk)
- Auto-save snapshots **during** the session (not only at end).
- **Verify backup success BEFORE** tearing down the container.
- Versioned backups.
- **Latency mitigation:** warm pool of pre-booted blank instances; restore DB into them on demand.
- **Schema-migration note:** bundle created on older farmOS → boot newer → Drupal `update.php` runs on import; test round-trips across versions.

---

## 4. RISK DUE-DILIGENCE (4 questions from Team 00)

| # | Question | Verdict | Note |
|---|----------|---------|------|
| 1 | **Multi-tenancy long-term** | 🟡 Sensitive but managed | farmOS is single-tenant; N farms = N instances. **Tier A + Tier-B ephemerality drastically reduce this** (most users cost ~0, no upgrade debt). For tens of farms: routine Docker orchestration. **Scale model beyond tens = OPEN DECISION (D2).** This is LiteFarm's only structural win. |
| 2 | **License** | 🟢 Safe | GPL-2.0-or-later (NOT AGPL). In SaaS+headless we never *distribute* modified code → modifications stay private; our engine/frontend/calculators stay proprietary. Red line: never ship modified farmOS code to a client; rebrand (no "farmOS" trademark). |
| 3 | **Bus-factor** ("if it disappears, do we fall?") | 🟢 Managed | Headless + self-host + GPL + we hold the data → upstream death = maintenance inconvenience, not existential. Real risk = ongoing **Drupal security maintenance**. Backstop: **Farmier** (commercial managed-hosting by the lead maintainer) exists as a sustainability safety net. Guardrails: keep our Postgres as SSoT; thin anti-corruption layer; budget Drupal upkeep. |
| 4 | **Modules & phasing** | 🟢 Clear | ESSENTIAL: `api`, `entity/asset/log/quantity/plan`, `role/login/owner`, `taxonomy` + domain asset/log types. NICE: `import/export/csv`, `map/geo`, `quick`, `inventory`. IRRELEVANT (headless): `ui` theme. **DEFER `farm_crop_plan`** (alpha; that gap = our differentiation). |

### On Farmier (clarification for Team 00)
There is **one** external paid party: **Michael Stenta / Farmier** (farmOS managed hosting). Two relationship depths — (a) hosting customer, (b) deeper ops partnership. **We chose self-host**, so Farmier is **not our path** — relevant only as a bus-factor backstop and a fallback if instance ops ever exceed our capacity (not expected at tens-of-farms scale).

---

## 5. OPEN DECISIONS (logged, not yet resolved)

- **D1 — Monetization specifics:** Freemium *model* chosen; exact tier boundaries, sandbox-rental pricing, subscription pricing, and custom-dev packaging are **open**.
- **D2 — Multi-tenancy scale model:** instance-per-farm is fine for tens. The architecture for hundreds (if ever) — self-orchestration vs Farmier partnership vs rethink operational store — is **open** and tied to the business model.
- **D3 — Sales/CRM integration targets:** Pillars 3 (Sell) & 4 (Relate) imply integrating an external sales + customer-management system. Specific targets/standards **open**.
- **D4 — Competitive schema mapping:** see §6.

---

## 6. NEXT-SESSION TASK (defined by Team 00)

> **Competitive comparison across several additional farm-management systems** (beyond farmOS + LiteFarm) to map the **full schema space** — entities, data models, planning features, integration surfaces — and validate/enrich our 13-topic taxonomy and 5-pillar model. Run as a **dedicated session**. Candidate systems to scope: Tend, Farmbrite, AgriWebb, Bloom (Local Line), Layout/JM-Fortier tooling, Sett, Croptracker, and others surfaced during scoping. Deliverable: a schema-comparison matrix feeding the SFA data model + cockpit design.

This brief (the farmOS/LiteFarm deep-dive + vision re-lock) is the **base** that comparison builds on.

---

## 7. Phased Roadmap (high-level, to be detailed)

- **Phase 0 — Foundation:** farmOS self-host (Docker), essential modules, custom module for the 13-topic taxonomy on plant/variety, OAuth2 service client, anti-corruption layer; **establish SFA Postgres as SSoT**.
- **Phase 1 — READ (+ brand front):** Hebrew/RTL headless frontend; free Tier A (Crop Book + 14 calculators + plan + export); push `value_best` via JSON:API; render validated/unvalidated. *(Brand-critical — do first, do excellently.)*
- **Phase 2 — COMPUTE:** calculators stay in the Python engine; results written to farmOS as Quantities; AssumptionField interactive pattern client-side.
- **Phase 3 — WRITE:** pull operational logs (harvest/seeding/transplanting) → HMAC ingest → reconciler loop.
- **Phase 4 — Tiers B/C:** rented-sandbox orchestration (warm pool, bundle save/restore, backup-before-teardown) + permanent instances.
- **Phase 5 — Cockpit + Sell/Relate:** role-aware morning dashboard; sales/CRM integrations (per D3).

---

*End of brief. Open DECISIONS D1–D4 carried to next session. Vision phrasing LOCKED per Team 00 in-session approval 2026-06-04.*
