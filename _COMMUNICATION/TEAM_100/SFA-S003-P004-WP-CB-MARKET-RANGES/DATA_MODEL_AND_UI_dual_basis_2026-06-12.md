# Dual-basis market_estimate — data model + UI implication (team_100, 2026-06-12)

team_00 direction: SFA teaches organic, so the **organic** price is primary in the UI; keep the **conventional**
price too (גם וגם) as a secondary detail; enable a future organic-vs-conventional comparison ("worth growing
organic?"). This note records how that lands in the DB schema, the already-live chip, and future features.

## 1. DB schema — `crops.payload_json.market_estimate` (dual, backward-compatible)
```json
"market_estimate": {
  "price_min": 7.5, "price_max": 13.9, "unit": "ק״ג",   // FLAT = the ORGANIC primary (see §2)
  "primary": "organic",
  "as_of": "2026-06",
  "organic":      { "price_min": 7.5,  "price_max": 13.9, "unit": "ק״ג", "confidence": "high",
                    "engines": 2, "sources": ["סלסילה","ערן אורגני"] },
  "conventional": { "price_min": 1.93, "price_max": 3.0,  "unit": "ק״ג", "basis": "wholesale",
                    "confidence": "medium-high", "engines": 1, "sources": ["מועצת הצמחים"] }
}
```
- **Both bases stored.** `organic` = the headline; `conventional` = the secondary detail (often wholesale-basis
  from moag — flag it so it's never shown as a shelf price).
- The unified aggregator already emits `organic{}` + `conventional{}` per crop. The ingest flattens the organic
  range to the top-level `price_min/price_max/unit` (see §2) and nests both.

## 2. The LIVE estimate chip (WP-CB-UI-TAILS, already in production) — NO code change needed
The shipped `entry()` + `book_entry.php` read `market_estimate.price_min / price_max / unit` (flat). By writing the
**organic** range to those flat keys, the live "מחיר מוערך" chip shows the **organic** price as primary the moment
the data lands — zero render change. `.organic{}` / `.conventional{}` ride along for later.

## 3. Future UI (a small follow-up WP — register when ready)
- **Crop page / market detail:** under the organic price, a small secondary line — e.g. `רגיל ≈ ₪1.93–3.0` —
  reading `market_estimate.conventional`. (The chip itself stays organic-only to avoid clutter.)
- **Organic-premium comparison / calculator:** organic ÷ conventional per crop → "פרמיית אורגני" %. e.g. onions
  organic ₪7.5–13.9 vs conventional ₪1.93–3.0 → very high premium → strong case to grow organic; a crop with a
  thin premium is less worth the organic effort. Feeds a future "worth growing organic?" planner calc.

## 4. Ingest path
team_100 reviews `unified_market_estimates.json`, then ingests the dual `market_estimate` into
`crops.payload_json` via **WP-CB-DATA-API** (incremental, validated, code-preserved — **NO `seed --all`**, team_00).
Ship the STRONG/OK organic tier first; the WEAK/NONE crops wait for the organic completion round.

## 5. Status (3 engines + pending organic completion round)
- Coverage 69/70; organic tiers: 29 STRONG · 2 OK · 28 WEAK · 10 NONE.
- Organic completion round (39 crops) issued: `ACTIVATION_PROMPT_team80_web_completion_organic_2026-06-12_v1.0.0.md`.
- Conventional data retained for all crops that had it (the moag/wholesale set) — secondary, not discarded.
