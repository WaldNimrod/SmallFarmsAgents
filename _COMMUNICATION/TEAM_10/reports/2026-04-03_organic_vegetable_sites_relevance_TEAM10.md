# Organic vegetable sites — relevance scan (Team 80 handoff)

**Date:** 2026-04-03  
**Team:** 10 (Feature Dev)  
**Input:** `_COMMUNICATION/TEAM_80/organic_vegetable_sites.md`  
**Audience:** Team 10 + Team 100 (for source-policy alignment)

---

## 1. System context (what we ingest and emit)

**Agent:** OrganicMarketAgent (see `docs/GLOSSARY.md`).

**What we look for**

- **Products:** Canonical organic (and adjacent) vegetable / produce offerings, including **basket (CSA)** products as first-class line items in V1 (not decomposed to per-kg).
- **Prices:** Observable **consumer-facing** prices tied to identifiable products (per kg, per unit, per basket, etc.), stable enough to become **normalized observations** after parsing + normalization.

**Pipeline shape (simplified)**

1. **Collector** → `RawAsset` (HTML/JSON/PDF…)
2. **Parser** → `RawExtractedItem` (structured raw lines)
3. **Normalizer** → `NormalizedObservation` (canonical product + unit + price + source metadata)
4. **Aggregator** → daily aggregates; **Publisher** → public JSON/HTML artifacts

**Source roles (from existing design)**

- **Community sources:** farms, CSAs, farm shops, organic-focused retailers/aggregators — primary transparency story (“what it costs at the source / niche channel”).
- **Benchmark sources:** govt / retail comparators — context vs community prices.
- **Discovery / verification:** lower direct price yield; used to find or validate producers, not always for numeric index rows.

Any **new** site must be classified into one of these (or explicitly “out of scope for V1”) before engineering work.

---

## 2. Scoring parameters (for filtering and triage)

Use these **together**; no single score decides alone.

| Parameter | Scale / values | Meaning |
|-----------|------------------|---------|
| **GEO** | `IL` / `non-IL` | Geographic alignment with current OrganicMarketAgent focus (Israel small-farm community). |
| **SITE_BUCKET** | `farm_csa` / `il_grocery` / `global_csa` / `global_retail` / `marketplace` | Copied or derived from Team 80 sections. |
| **ROLE_FIT** | `community` / `benchmark` / `discovery` / `none` | Expected role if added as a `Source` (GLOSSARY terms). |
| **ORG_SIGNAL** | 1–5 | Strength of **organic vegetable / produce** signal on typical pages (not overall store brand). |
| **PRICE_ACCESS** | 1–5 | **Estimated** ease of obtaining stable product+price rows (structure, SPA/anti-bot, login walls). 5 = easy public price lists; 1 = opaque. |
| **NORM_FIT** | 1–5 | Fit for **Hebrew / local naming** and catalog overlap with existing normalizer + product catalog (IL sites usually higher). |
| **OPS_RISK** | L / M / H | Operational risk: breakage, rate limits, maintenance cost of parsers (not legal — see next). |
| **LEGAL_FLAG** | Y / N | **Y** = treat like `legal_review_required` in SOURCE_MAP until Team 100 / counsel says otherwise (large retailers, aggregators with ToS constraints). |
| **OVERALL** | 1–5 | Holistic value **for our stated mission today** (Israel community organic price transparency + sensible benchmarks). |
| **PRIORITY** | P0–P4 | P0 = strongest candidate next; P4 = backlog or out-of-scope unless strategy changes. |

**Filtering examples**

- “Next **community** IL sources with **OVERALL ≥ 4** and **LEGAL_FLAG = N**.”
- “**Benchmark** candidates only: `ROLE_FIT = benchmark` and `GEO = IL`.”
- “Exclude **non-IL** unless `OVERALL ≥ 4` and Nimrod approves scope expansion.”

---

## 3. Master table — all URLs from Team 80

Scores are **desk assessment** by Team 10 (not live crawl). **PRICE_ACCESS** and **OPS_RISK** must be **validated** with a short technical spike per shortlisted site.

| # | URL | GEO | SITE_BUCKET | ROLE_FIT | ORG_SIGNAL | PRICE_ACCESS | NORM_FIT | OPS_RISK | LEGAL_FLAG | OVERALL | PRIORITY | Notes |
|---|-----|-----|-------------|----------|------------|--------------|----------|----------|------------|---------|----------|-------|
| 1 | https://www.chubeza.com/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 5 | P0 | Same brand as existing easyFarm CSA path; confirm relationship vs `chubeza.easyfarm.co.il` before duplicate source. |
| 2 | https://www.bensfarm.co.il/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 4 | P1 | Farm direct / shop; verify public price list structure. |
| 3 | https://www.haorgani.co.il/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 5 | P0 | **Already SRC011** in SOURCE_MAP; do not re-register — verify coverage gaps only. |
| 4 | https://www.offaime.co.il/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 4 | P1 | Farm / direct sales; spike collector feasibility. |
| 5 | https://www.hameshek.com/ | IL | farm_csa | community | 4 | 3 | 5 | M | N | 4 | P1 | “Hameshek”-type farm retail; confirm organic focus pages. |
| 6 | https://www.etzhasadeh.co.il/ | IL | farm_csa | community | 4 | 4 | 5 | M | N | 4 | P1 | Likely related to עץ השדה ecosystem; compare to SRC006 (`etzhasade.easyfarm.co.il`) — avoid duplicate entity. |
| 7 | https://www.meshekhavivian.co.il/ | IL | farm_csa | community | 4 | 3 | 5 | M | N | 4 | P1 | Farm shop; public pricing TBD. |
| 8 | https://www.nizat.com/ | IL | farm_csa | community | 4 | 3 | 5 | M | N | 4 | P1 | Verify product/price surfaces. |
| 9 | https://www.ecofarm.co.il/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 4 | P1 | Organic positioning; spike structure. |
| 10 | https://www.meshekrappaport.co.il/ | IL | farm_csa | community | 4 | 3 | 5 | M | N | 4 | P1 | Farm direct. |
| 11 | https://www.meshek8.co.il/ | IL | farm_csa | community | 4 | 3 | 5 | M | N | 4 | P1 | Farm direct. |
| 12 | https://www.organic-israel.com/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 4 | P1 | Organic retailer / multi-vendor possible; clarify if prices are per-producer. |
| 13 | https://www.teva-market.co.il/ | IL | farm_csa | community | 5 | 3 | 5 | M | N | 4 | P1 | Organic market positioning; may overlap grocery patterns. |
| 14 | https://www.shufersal.co.il/ | IL | il_grocery | benchmark | 3 | 2 | 4 | H | Y | 3 | P2 | Major grocery; high anti-bot / SPA / ToS risk; benchmark only if policy allows. |
| 15 | https://www.rami-levy.co.il/ | IL | il_grocery | benchmark | 3 | 2 | 4 | H | Y | 3 | P2 | Same as above. |
| 16 | https://www.victoryonline.co.il/ | IL | il_grocery | benchmark | 3 | 2 | 4 | H | Y | 3 | P2 | Same as above. |
| 17 | https://www.tivtaam.co.il/ | IL | il_grocery | benchmark | 3 | 2 | 4 | H | Y | 3 | P2 | Same as above. |
| 18 | https://www.yohananof.co.il/ | IL | il_grocery | benchmark | 3 | 2 | 4 | H | Y | 3 | P2 | Same as above. |
| 19 | https://www.riverford.co.uk/ | non-IL | global_csa | none | 5 | 3 | 1 | M | N | 2 | P4 | Reference / UX only unless scope expands beyond IL. |
| 20 | https://www.abelandcole.co.uk/ | non-IL | global_csa | none | 5 | 3 | 1 | M | N | 2 | P4 | Same. |
| 21 | https://www.farmfreshtoyou.com/ | non-IL | global_csa | none | 5 | 3 | 1 | M | N | 2 | P4 | Same. |
| 22 | https://www.imperfectfoods.com/ | non-IL | global_csa | none | 4 | 2 | 1 | H | Y | 2 | P4 | US box model; legal/ops heavier. |
| 23 | https://www.misfitsmarket.com/ | non-IL | global_csa | none | 4 | 2 | 1 | H | Y | 2 | P4 | Same. |
| 24 | https://www.growingcommunities.org/ | non-IL | global_csa | none | 5 | 2 | 1 | M | N | 2 | P4 | Community CSA reference. |
| 25 | https://www.organicdeliverycompany.co.uk/ | non-IL | global_csa | none | 5 | 3 | 1 | M | N | 2 | P4 | UK delivery; out of scope for IL index. |
| 26 | https://www.oddbox.co.uk/ | non-IL | global_csa | none | 4 | 3 | 1 | M | N | 2 | P4 | Same. |
| 27 | https://www.thevegboxcompany.co.uk/ | non-IL | global_csa | none | 5 | 3 | 1 | M | N | 2 | P4 | Same. |
| 28 | https://www.freshdirect.com/ | non-IL | global_retail | none | 3 | 2 | 1 | H | Y | 2 | P4 | US grocery ecom. |
| 29 | https://www.thrivemarket.com/ | non-IL | global_retail | none | 4 | 2 | 1 | H | Y | 2 | P4 | Membership model; poor fit. |
| 30 | https://www.farmboxdirect.com/ | non-IL | global_retail | none | 4 | 2 | 1 | M | Y | 2 | P4 | US. |
| 31 | https://www.greenbean.com/ | non-IL | global_retail | none | 3 | 2 | 1 | M | Y | 2 | P4 | Verify actual domain/product (ambiguous name). |
| 32 | https://www.baldorfood.com/ | non-IL | global_retail | none | 2 | 2 | 1 | M | Y | 1 | P4 | B2B / wholesale tone; weak consumer index fit. |
| 33 | https://www.localharvest.org/ | non-IL | marketplace | discovery | 4 | 2 | 2 | M | Y | 2 | P4 | Directory; discovery not price rows. |
| 34 | https://www.farmigo.com/ | non-IL | marketplace | discovery | 3 | 2 | 2 | H | Y | 2 | P4 | Platform; unclear public price API. |
| 35 | https://www.crowdfarming.com/ | non-IL | marketplace | discovery | 4 | 2 | 2 | M | Y | 2 | P4 | EU focus; discovery / future scope. |
| 36 | https://www.realfoodhub.com/ | non-IL | marketplace | discovery | 4 | 2 | 2 | M | Y | 2 | P4 | UK hub. |
| 37 | https://www.bigbasket.com/ | non-IL | marketplace | benchmark | 3 | 2 | 1 | H | Y | 1 | P4 | India retail; no IL mission fit. |

**Row count:** 37 distinct sites (Team 80 file lists 13 + 5 + 9 + 5 + 5 = 37 URLs).

---

## 4. Overlap with existing SOURCE_MAP (do not duplicate)

Cross-check `docs/SOURCE_MAP_MASTER_HE.md` (English rewrite pending):

- **haorgani.co.il** → SRC011 (active).
- **etzhasadeh** vs **etzhasade** easyFarm host → likely same operator family; coordinate with Team 100 before adding a second `Source`.
- **chubeza.com** vs **chubeza.easyfarm.co.il** (SRC003) → same brand; one logical source preferred.

---

## 5. Recommended next actions (Team 10)

1. **Shortlist:** All IL rows with `PRIORITY` P0–P1 and `LEGAL_FLAG = N`, excluding known SRC duplicates.
2. **Spike per shortlist:** One-page note: URL pattern, login required?, HTML vs JSON, sample product lines, **estimate** parser family (`easyfarm` / `html_page` / other).
3. **Gate:** New `Source` rows + `legal_review_required` for any `LEGAL_FLAG = Y` (mirror SOURCE_MAP policy).
4. **Non-IL backlog:** Keep table for strategy discussions; do not implement unless Nimrod + Team 100 extend geographic scope.

---

## 6. Blockers / questions for Team 100 or Nimrod

- Whether **national grocery chains** (Shufersal, Rami Levy, …) are in-scope for **benchmark** collectors under current legal posture (compare SRC017/SRC018 notes).
- Whether **chubeza.com** and **chubeza.easyfarm.co.il** should remain a **single** `Source` with multiple fetch profiles or two sources.

---

**End of report.**
