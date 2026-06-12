# RESEARCH MANDATE — SFA-S003-P004-WP-CB-MARKET-RANGES — team_100 → team_80 — v1.0.0

**Date:** 2026-06-12
**From:** team_100 (Chief System Architect)
**To:** team_80 (Research — advisory; engine variable)
**Authorized by:** team_00 (in-session, 2026-06-12)
**WP:** SFA-S003-P004-WP-CB-MARKET-RANGES
**Type:** RESEARCH MANDATE (market data gathering)

## 0. Why
The crop-book list shows a ₪ price chip that closes the book↔market loop. For crops with a **live** community
market price we show `בשוק ₪X/unit`. For crops with **no** live price we want an honest **estimated range**
(`מחיר מוערך ₪min–₪max/unit`). The render-side infrastructure is being built now in **WP-CB-UI-TAILS (AC-1.2)**,
which reads a per-crop payload field `market_estimate`. **This mandate gathers the DATA** that fills that field.

## 1. Objective
Produce, for each crop in the SFA crop book, a **current estimated retail price RANGE** and its **selling unit of
measure** in the **Israeli** market (organic where available), sourced from the web, with evidence and an as-of date.

## 2. Crop inventory (what to research)
The live crop set (~70 crops, Hebrew names) is the authoritative list:
- Public crop book: `https://sfa.nimrod.bio/crop-book/`
- JSON inventory: `https://sfa.nimrod.bio/api/v1/crops` (slug + hebrew_name per crop)

Research every crop you can; it is fine to return a partial set — mark crops you could not source as `unknown`
(do NOT invent a range).

## 3. Output contract (per crop) — this is what the render reads
For each crop, return an object matching the `market_estimate` field the UI consumes:
```json
{
  "slug": "<crop slug>",
  "hebrew_name": "<שם>",
  "market_estimate": {
    "price_min": <number, ₪>,
    "price_max": <number, ₪>,
    "unit": "<he selling unit, e.g. ק״ג | יחידה | צרור | 100 גרם>",
    "source": "<short source label, e.g. retailer / market index name>",
    "source_url": "<url>",
    "as_of": "YYYY-MM",
    "confidence": "high | medium | low",
    "organic": true | false
  }
}
```
Rules:
- **`price_min` / `price_max`** = a realistic current retail range (₪) for the stated `unit`. If you only find a
  single point price, set min = max and `confidence: low`.
- **`unit`** = the unit the price is quoted in (kg / each / bunch / 100g…), in Hebrew, matching how it is sold.
- **Israeli market, current** (`as_of` within ~3 months). Prefer organic; if only conventional is found, set
  `organic: false` and note it.
- **Sources mandatory** (team_80 Iron Rule #1) — every range carries `source` + `source_url`. No unsourced numbers.
- **Honest** — never fabricate. Unknown → omit the crop or mark `confidence: low` with what you found.

## 4. Suggested sources
Israeli organic/retail price points: organic retailers + delivery (e.g. עדן טבע מרקט / טבע קסטרו / חוות אורגניות /
משקים), שוק האיכרים / farmers-market listings, MyPIPS / wholesale market indices, supermarket online price pages.
Cross-check at least two sources per crop where possible; report the spread you observe as the range.

## 5. Deliverable
- Write your findings to **`_COMMUNICATION/team_80/SFA-S003-P004-WP-CB-MARKET-RANGES/FINDINGS_2026-06-DD_v1.0.0.md`**
  (your write scope is `_COMMUNICATION/team_80/` only — Iron Rule #7).
- Include: (a) a machine-readable block (JSON array of the §3 objects), (b) a short methodology note (sources,
  date window, confidence rationale), (c) any crops you could not source.
- Deliver to **team_100** (research → architecture; you have no gate authority and do NOT write to the DB).

## 6. Downstream (not your scope)
team_100 reviews the findings; ingestion of `market_estimate` into `crops.payload_json` flows through
**WP-CB-DATA-API** (incremental, validated, code-preserved — **NO `seed --all`**, per team_00). The WP-CB-UI-TAILS
render side ships independently and shows the estimate chip only once the data lands (honest empty until then).

---
*Research mandate. Israeli market, current, sourced, honest. Partial coverage acceptable; never invent a price.*
