# team_80 Activation Prompt — SFA-S003-P004-WP-CB-MARKET-RANGES (web research, inline)

**For team_00:** team_80 runs in the browser (web search). Paste the block below into a web-capable research
agent (ChatGPT / Perplexity / Gemini / Claude.ai with web). It is fully self-contained — the 70 crops are inline,
and the agent returns its findings inline as JSON (no repo/DB access). team_100 then ingests via WP-CB-DATA-API.

---

```
# Mission — Israeli market price ranges + selling units for 70 crops (team_80 research)
# Project: SmallFarmsAgents crop book (sfa.nimrod.bio). You work in the browser; search the live web.
# Everything you need is in this message. Return findings INLINE as JSON — you have no file/DB access.

## Objective
For each of the 70 crops listed below, find the CURRENT (as-of within ~3 months) **Israeli retail price RANGE**
(min–max, in ₪) and the **selling UNIT** the price is quoted in. Prefer **organic**; if only conventional is
found, use it and flag `organic: false`. Every number must be sourced — never guess.

## Why it matters
The crop book shows an estimated-price chip ("מחיר מוערך ₪min–₪max / unit") for crops with no live community price.
Your ranges fill that estimate. It must be honest and sourced, or it doesn't ship.

## Output — return ONE JSON array, one object per crop you could source:
[
  {
    "slug": "carrots",
    "hebrew_name": "גזר",
    "market_estimate": {
      "price_min": 8.0,
      "price_max": 14.0,
      "unit": "ק״ג",                 // Hebrew selling unit: ק״ג | יחידה | צרור | חבילה | 100 גרם | אגודה ...
      "organic": true,
      "source": "עדן טבע מרקט",       // short source label
      "source_url": "https://...",
      "as_of": "2026-06",
      "confidence": "high"            // high | medium | low
    }
  }
]
Rules:
- price_min / price_max in ₪ for the stated unit. Found only one price point → set min = max, confidence: "low".
- Cross-check ≥2 sources where you can; report the observed spread as the range.
- NEVER invent a number. If you can't source a crop, omit it and add its hebrew_name to a final "unsourced" list.
- Keep the slug EXACTLY as given (it's the database key).

## Suggested Israeli sources (search these + the open web)
Organic retail/delivery: עדן טבע מרקט · טבע קסטרו · ניל"י · "אורגני בקליק" · משקים/חוות אורגניות · מנדלי.
Farmers markets: שוק האיכרים (ת״א/באר שבע/וכו׳). Wholesale/index: מדד מחירי סיטונאי, שוק צריפין.
Conventional baseline (flag organic:false): שופרסל / רמי לוי online price pages.
Example query: "מחיר גזר אורגני קילו 2026" · "עגבניות אורגני מחיר ק\"ג".

## The 70 crops (hebrew_name — slug — category)
VEGETABLES:
אפונה — peas · ארוגולה — arugula · ארטישוק — artichokes · ארטישוק ירושלמי — jerusalem-artichokes ·
אדממה — edamame · בטטה — sweet-potato · במיה — okra · בצל — onions · בצל ירוק — scallions · ברוקולי — broccoli ·
ג'ינג'ר — ginger · ג'יקמה — jicama · גזר — carrots · גרגר נחלים — cress · דלעת — winter-squash · חומוס — chickpea ·
חיטה — wheat · חמניה — sunflower · חסה — lettuce · חציל — eggplant · כרוב — cabbage · כרובית — cauliflower ·
כרישה — leeks · לובסטייה — lovage · לפת — turnips · מלון — melons · מלפפון — cucumbers · מנגולד — chard ·
סויה — soybean · סלק — beets · סלרי — celery · עגבנייה — tomatoes · עלי בייבי — salad-mix · פאק צ'וי — pac-choi ·
פול — fava-bean · פלפל — peppers · פנס סיני — chinese-lantern · ציקוריה — chicory · צנונית — radishes ·
קולורבי — kohlrabi · קייל — kale · קישוא — summer-squash · שום — garlic · שומר — fennel · שעועית — bush-pole ·
תירס — corn · תפוח אדמה — potato · תרד — spinach · תרד ניו-זילנד — new-zealand-spinach
HERBS:
אזוב מצוי — anise-hyssop · בזיל — basil · היביסקוס — hibiscus · טימין — thyme · טרגון — tarragon ·
כוסברה — cilantro · כורכום — turmeric · לימון בלם — lemon-balm · לימון ורבנה — lemon-verbena · מרווה — sage ·
נענע — mint · עירית — chives · פטרוזיליה — parsley · שומשום — sesame · שמיר — dill
FRUITS:
אבטיח — watermelon · אוסנה — blackberry · עגבניית שרי — cherry-tomato · תות שדה — strawberry
FRUIT TREES:
דפנה — bay · תפוז — oranges

## Deliverable
Reply with: (1) the JSON array above, (2) a short methodology note (which sources, date window, how you set
confidence), (3) the "unsourced" crop list. Partial coverage is fine — accuracy + sources beat completeness.
```

---
*Self-contained inline web-research package. team_80 = advisory research (no repo/DB write). team_100 reviews the
returned JSON and ingests `market_estimate` into `crops.payload_json` via WP-CB-DATA-API (incremental, validated,
NO `seed --all`). Feeds the WP-CB-UI-TAILS estimate chip (render infra already live).*
