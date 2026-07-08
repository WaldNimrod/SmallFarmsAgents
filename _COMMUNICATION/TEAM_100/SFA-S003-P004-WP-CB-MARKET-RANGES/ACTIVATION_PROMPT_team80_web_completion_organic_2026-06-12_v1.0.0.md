# team_80 COMPLETION ROUND (organic-focused) — SFA-S003-P004-WP-CB-MARKET-RANGES

**For team_00:** precise 2nd round. Three engines already covered 69/70, but **39 crops still lack a solid
ORGANIC retail price** (only conventional, or a single weak organic source). SFA teaches organic growing, so the
**organic price is the primary** number — this round fills exactly those 39 organic gaps. Paste into a web research
agent; it returns JSON inline. (Different engine than last time = a real 2nd opinion.)

---

```
# Completion round — ORGANIC retail prices for 39 Israeli crops (team_80 research)
# Project: SmallFarmsAgents crop book (sfa.nimrod.bio). Browser research; return findings INLINE as JSON.

## What's different this round
A previous pass already priced most crops. These 39 still have NO solid ORGANIC retail price (we only have
conventional, or one weak source). We TEACH ORGANIC, so we need the **organic** consumer-retail price for each.
Focus your effort here. Conventional is secondary (nice-to-have, not required).

## Objective — for EACH of the 39 crops below
Find the CURRENT (within ~3 months) **Israeli ORGANIC retail price RANGE** (min–max, ₪) + the selling UNIT,
from real organic shops/delivery. Cross-check ≥2 organic sources where possible. If a crop genuinely has NO
organic retail listing in Israel (some specialty herbs/legumes don't), say so in the "no_organic_found" list —
do NOT substitute a conventional price as if it were organic, and never invent a number.

## Output — ONE JSON array (organic prices):
[
  {
    "slug": "beets",
    "hebrew_name": "סלק",
    "market_estimate": {
      "price_min": 9.0,
      "price_max": 14.0,
      "unit": "ק״ג",                 // ק״ג | יחידה | צרור | מארז | "חבילה 500 גרם" ...
      "organic": true,               // MUST be true this round (we want organic)
      "source": "סלסילה; ערן אורגני",
      "source_url": "https://...",
      "as_of": "2026-06",
      "confidence": "high"           // high (3+) | medium (2) | low (1 source)
    }
  }
]
Rules: ₪ for the stated unit; one price point → min=max + "low"; keep the slug EXACTLY; organic MUST be true.

## Best Israeli ORGANIC sources (these worked last round — start here)
סלסילה (salsila.co.il) · טבע קסטל (tevacastel / Wolt) · שדה ירוק (sadeyarok.co.il) · ערן אורגני (eranorgani.co.il) ·
ניצת הדובדבן (nizat.com) · פארמרים (farmerim.com) · אורגני שופ (organishop.co.il) · משק זינגר (zinger-organic.com) ·
FarmDirect (farmdirect.co.il) · נוי השדה (noyhasade.co.il) · שופרסל GREEN (organic section). Search e.g.
"סלק אורגני מחיר קילו" · "תות שדה אורגני מחיר".

## The 39 crops needing an organic price (hebrew_name — slug)
אדממה — edamame · אוסנה — blackberry · אזוב מצוי — anise-hyssop · ארוגולה — arugula · ארטישוק — artichokes ·
ארטישוק ירושלמי — jerusalem-artichokes · במיה — okra · ג'ינג'ר — ginger · ג'יקמה — jicama · גרגר נחלים — cress ·
דפנה — bay · היביסקוס — hibiscus · חיטה — wheat · חמניה — sunflower · טרגון — tarragon · כורכום — turmeric ·
כרישה — leeks · לובסטייה — lovage · לימון בלם — lemon-balm · לימון ורבנה — lemon-verbena · לפת — turnips ·
מרווה — sage · סויה — soybean · סלק — beets · סלרי — celery · עירית — chives · פול — fava-bean ·
פנס סיני — chinese-lantern · ציקוריה — chicory · צנונית — radishes · קולורבי — kohlrabi · קייל — kale ·
שום — garlic · שומשום — sesame · שמיר — dill · שעועית — bush-pole · תות שדה — strawberry · תרד — spinach ·
תרד ניו-זילנד — new-zealand-spinach

## Deliverable
Reply with (1) the JSON array (organic only), (2) a short methodology note (which organic shops, date window),
(3) a "no_organic_found" list of crops with no Israeli organic retail listing. Accuracy + organic sourcing beat
completeness — a confirmed "not sold organic retail in IL" is a useful answer too.
```

---
*Targeted organic completion. team_100 merges this into the dual-basis aggregator (organic = primary chip,
conventional already stored as secondary). Drop the returned JSON into research_inputs/ and re-run.*
