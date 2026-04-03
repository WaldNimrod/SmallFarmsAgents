# Source onboarding plan — Phase A (farms) vs Phase B (retail / large operators)

**Date:** 2026-04-04  
**From:** Team 10 (with Nimrod direction)  
**To:** Team 100 (Architecture)  
**Purpose:** Plan phased addition of new `Source` rows, collectors, and **separate presentation** for Phase B in the product.

**References**

* `_COMMUNICATION/TEAM_80/organic_vegetable_sites.md` (link seed list)  
* `_COMMUNICATION/TEAM_10/reports/2026-04-03_organic_vegetable_sites_relevance_TEAM10.md` (relevance scan)  
* `docs/GLOSSARY.md` — `Source`, `market_scope`, community vs benchmark  
* `docs/SOURCE_MAP_MASTER_HE.md` — existing IDs and `legal_review_required` policy

---

## 1. Product direction (for planning)

* **OrganicMarketAgent** ingests **consumer-facing product + price** signals, normalizes to canonical products, aggregates, publishes.  
* **Phase A** targets **farms, growers, direct sales, CSA-style** channels (community story).  
* **Phase B** targets **Nizat, Teva Market, national grocery chains, and other large retail / marketing-scale operators** — Nimrod requires these to be **shown separately** from Phase A sources in the system (UX + data model / `market_scope` or equivalent — **Team 100 to specify**).

---

## 2. Phase A — farms and growers (Israel)

**Scope:** All **farm / direct / grower** URLs from Team 80’s Israel section **except** those moved to Phase B (Nizat, Teva Market).

**Action for Team 100**

* Define gate criteria: dedupe vs existing `Source` (e.g. **SRC003** Chubeza easyFarm vs `chubeza.com`; **SRC006** vs `etzhasadeh.co.il`; **SRC011** **haorgani.co.il** already active).  
* One spike per URL: public price surface, `platform_family` / `fetch_mode`, normalizer profile class.  
* Approve new `Source` codes and `market_scope` (expected: **community**).

**Phase A URL list (11)**

* `https://www.chubeza.com/`  
* `https://www.bensfarm.co.il/`  
* `https://www.haorgani.co.il/` *(existing **SRC011** — gap analysis only unless second surface is justified)*  
* `https://www.offaime.co.il/`  
* `https://www.hameshek.com/`  
* `https://www.etzhasadeh.co.il/` *(align with **SRC006** — avoid duplicate logical source)*  
* `https://www.meshekhavivian.co.il/`  
* `https://www.ecofarm.co.il/`  
* `https://www.meshekrappaport.co.il/`  
* `https://www.meshek8.co.il/`  
* `https://www.organic-israel.com/`

---

## 3. Phase B — Nizat, Teva Market, large retail / chains

**Scope (explicit)**

* `https://www.nizat.com/`  
* `https://www.teva-market.co.il/`  
* Israel **online grocery** URLs from Team 80 (national-scale retail):

  * `https://www.shufersal.co.il/`  
  * `https://www.rami-levy.co.il/`  
  * `https://www.victoryonline.co.il/`  
  * `https://www.tivtaam.co.il/`  
  * `https://www.yohananof.co.il/`

**Additional Phase B candidates (for Team 100 to confirm and extend)**

* **Already in SOURCE_MAP** as retail/benchmark-style: **SRC017** (Pricez), **SRC018** (CHP) — treat under same **Phase B presentation and legal** rules if brought to `active`.  
* **Large aggregators / marketing-scale** portals (e.g. multi-vendor organic retail) — Team 100 to name which existing or new URLs belong in Phase B vs Phase A (e.g. if the primary role is **benchmark / retail breadth** rather than single-farm direct).

**Action for Team 100**

* **Separate system presentation:** specify UI labels, report sections, filters, and/or artifact layout so Phase B observations are **not mixed** with Phase A “farm / direct” story unless the user explicitly opts in.  
* **Data model:** confirm use of **`market_scope`** (`community` vs `benchmark`) and/or a new facet (e.g. `source_tier`, `display_bucket`) if `benchmark` alone is insufficient.  
* **Legal:** default **`legal_review_required = true`** for Phase B net-new national retailers until counsel/ToS review (same class as SRC017/SRC018).  
* **Engineering:** expect **higher** anti-bot / SPA / maintenance cost — prioritize after Phase A unless product mandates parallel track.

**Phase B URL count (explicit list above):** 7 (Nizat + Teva Market + 5 grocery chains) **plus** catalogued candidates (Pricez, CHP) and any further sites Team 100 adds.

---

## 4. Out of scope for this plan (unless roadmap changes)

* **Global** URLs in Team 80 (UK/US/EU marketplaces) — no Israel index value under current charter.  
* **Discovery-only** marketplaces (LocalHarvest, Farmigo, …) — not price-row sources for V1 index.

---

## 5. Decisions requested from Team 100

* Approve **Phase A vs B** split as the **official onboarding sequence** (A first, B second unless parallel exception).  
* Publish **spec snippet** (English) for **“separate display”** of Phase B: fields, UI rules, publish JSON shape if affected.  
* Confirm **dedupe rules** for Chubeza / Etz ha-Sade / HaOrgani vs existing `Source` rows.  
* List **additional Phase B URLs** beyond this report under consistent criteria (large company / national retail / marketing aggregator).

---

## 6. Handoff to Team 20 / Team 10

* After Team 100 signs off: Team 20 seeds `sources` + `source_fetch_profiles` stubs; Team 10 implements collectors/parsers per approved profiles.

---

**[USER ACTION REQUIRED]** None for filing — Nimrod approval of Phase B “separate presentation” detail may be needed once Team 100 returns a concrete UX/data spec.
