#!/usr/bin/env python3
"""
aggregate_market_ranges.py — WP-CB-MARKET-RANGES multi-engine aggregator (dual-basis).

Reads every *.json engine report in ./research_inputs/ (each = a JSON array of
{slug, hebrew_name, market_estimate:{price_min,price_max,unit,organic,source,source_url,as_of,confidence}}),
and produces, PER CROP, TWO merged estimates kept side by side (team_00: SFA teaches organic →
organic is PRIMARY in the UI; conventional is kept as a secondary detail for future organic-vs-conventional
comparison):
  - "organic"      — merged from organic sources (the headline price chip)
  - "conventional" — merged from conventional sources (small detail; often wholesale-basis from moag)

Outputs:
  - unified_market_estimates.json   (per crop: organic{} + conventional{} + primary + _flags[] + _sources[])
  - AGGREGATION_SUMMARY.md          (organic | conventional table + organic-coverage tiers for review)

Each merged estimate: robust outlier trim (drop a source whose midpoint > 3x the cheapest — e.g. a
restaurant-menu price), unit-normalized, with engines/basis/confidence. team_80 = advisory research;
team_100 reviews, then ingests via WP-CB-DATA-API (incremental, validated — NO seed --all).
"""
import json, os, glob, sys, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "research_inputs")

CANON = [
 "watermelon","edamame","blackberry","anise-hyssop","peas","arugula","artichokes","jerusalem-artichokes",
 "basil","sweet-potato","okra","onions","scallions","broccoli","ginger","jicama","carrots","cress",
 "winter-squash","bay","hibiscus","chickpea","wheat","sunflower","lettuce","eggplant","thyme","tarragon",
 "cilantro","turmeric","cabbage","cauliflower","leeks","lovage","lemon-balm","lemon-verbena","turnips",
 "melons","cucumbers","chard","sage","mint","soybean","beets","celery","tomatoes","cherry-tomato","chives",
 "salad-mix","pac-choi","fava-bean","parsley","peppers","chinese-lantern","chicory","radishes","kohlrabi",
 "kale","summer-squash","garlic","fennel","sesame","dill","bush-pole","strawberry","corn","oranges","potato",
 "spinach","new-zealand-spinach",
]
CANON_SET = set(CANON)
WHOLESALE_HINTS = ["moag", "מועצת הצמחים", "משרד החקלאות", "סיטונא", "moonsite", "pricez", "פרייסז"]

def is_wholesale(src, url):
    blob = f"{src or ''} {url or ''}".lower()
    return any(h.lower() in blob for h in WHOLESALE_HINTS)

def norm_unit(u):
    if not u:
        return ""
    u = u.strip().replace('"', '״').replace("'", "׳")
    base = u.replace(' ', '')
    if base in ('ק״ג', 'קילו', 'קילוגרם', 'קג', 'kg'): return 'ק״ג'
    if base in ('יח׳', 'יחידה', 'יח', 'unit'):          return 'יחידה'
    if base in ('אגודה', 'צרור', 'bunch'):              return 'צרור'
    if base in ('מארז', 'חבילה', 'pack'):               return 'מארז'
    return u

def grams_of(unit):
    """grams represented by a unit string, or None for bunch/unit (no weight)."""
    u = unit or ""
    if re.search(r'ק["״]?ג|קילו|\bkg\b', u):
        m = re.search(r'(\d+(?:\.\d+)?)\s*ק', u)
        return (float(m.group(1)) if m else 1) * 1000
    m = re.search(r'(\d+)(?:\s*[–-]\s*(\d+))?\s*(?:גרם|גר|g)\b', u)
    if m:
        a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
        return (a + b) / 2
    return None

# team_00 per-crop overrides (2026-06-12):
FORCE_KG = {"bush-pole"}                        # שעועית — combine fresh+frozen forms on one ₪/kg basis
UNIT_PREFER = {"strawberry": "מארז 250 גרם"}    # תות — display per 250g punnet

CONF_RANK = {"high": 3, "medium": 2, "medium-high": 2, "low": 1, "": 0}

def summarize(sources, prefer=None):
    """Merge per-source dicts into one estimate. The headline range uses the DOMINANT unit only
    (₪/kg can't be averaged with ₪/package), then trims a high outlier (>3x the cheapest) within it.
    `prefer` forces a specific dominant unit when present (team_00 override)."""
    if not sources:
        return None
    from collections import Counter
    unit_counts = Counter(s["unit"] for s in sources if s["unit"])
    if unit_counts:
        if prefer and prefer in unit_counts:
            dom_unit = prefer
        else:
            # dominant = most sources; tie-break prefers ק״ג, then יחידה (the canonical retail units)
            dom_unit = max(unit_counts, key=lambda u: (unit_counts[u], 2 if u == 'ק״ג' else (1 if u == 'יחידה' else 0)))
        pool0 = [s for s in sources if s["unit"] == dom_unit]
    else:
        dom_unit, pool0 = "", sources
    mids = sorted((s["price_min"] + s["price_max"]) / 2 for s in pool0)
    floor = mids[0] if mids else 0
    pool = [s for s in pool0 if floor == 0 or (s["price_min"] + s["price_max"]) / 2 <= 3 * floor] or pool0
    excluded = [s for s in sources if s not in pool]
    rmin = min(s["price_min"] for s in pool)
    rmax = max(s["price_max"] for s in pool)
    # median over per-engine midpoints (in the dominant unit) — shown to the user alongside the range
    per_eng = {}
    for s in pool:
        per_eng.setdefault(s["engine"], []).append((s["price_min"] + s["price_max"]) / 2)
    median = round(statistics.median([statistics.mean(v) for v in per_eng.values()]), 2)
    unit = dom_unit
    units_all = sorted(unit_counts.keys() - {dom_unit})  # alternative units seen (other packaging)
    engines = sorted({s["engine"] for s in pool})
    bases = sorted({s["basis"] for s in pool})
    if len(engines) >= 2:
        conf = "high"
    elif any(s["confidence"] == "high" for s in pool):
        conf = "medium-high"
    else:
        conf = max((s["confidence"] for s in pool), key=lambda c: CONF_RANK.get(c, 0)) or "low"
    out = {
        "price_min": round(rmin, 2), "price_max": round(rmax, 2), "price_median": median, "unit": unit,
        "basis": "/".join(bases), "confidence": conf, "engines": engines, "n_sources": len(pool),
    }
    if units_all:
        out["unit_options"] = units_all  # other packaging seen (e.g. ₪/package vs the dominant ₪/kg)
    if excluded:
        out["outlier_excluded"] = [f"{s['engine']}@₪{s['price_max']}" for s in excluded]
    return out

def main():
    reports = {}
    for path in sorted(glob.glob(os.path.join(INPUTS, "*.json"))):
        engine = os.path.splitext(os.path.basename(path))[0]
        try:
            reports[engine] = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            print(f"WARN: bad {path}: {e}", file=sys.stderr)
    if not reports:
        print("No engine reports in research_inputs/."); return

    by_slug, he_name, unknown = {}, {}, set()
    for engine_file, rows in reports.items():
        engine = re.split(r'[-_]', engine_file)[0]  # base engine (gemini-round2_* → gemini) — no double-count
        for row in rows:
            slug = (row.get("slug") or "").strip()
            me = row.get("market_estimate") or {}
            if not slug or not me:
                continue
            if slug not in CANON_SET:
                unknown.add(slug)
            he_name.setdefault(slug, row.get("hebrew_name", ""))
            src, url = me.get("source", ""), me.get("source_url", "")
            by_slug.setdefault(slug, []).append({
                "engine": engine,
                "price_min": float(me.get("price_min", 0) or 0),
                "price_max": float(me.get("price_max", me.get("price_min", 0)) or 0),
                "unit": norm_unit(me.get("unit") or ""),
                "organic": bool(me.get("organic", False)),
                "source": src, "source_url": url,
                "as_of": me.get("as_of", ""), "confidence": me.get("confidence", ""),
                "basis": "wholesale" if is_wholesale(src, url) else "retail",
            })

    unified = []
    for slug in sorted(by_slug, key=lambda s: CANON.index(s) if s in CANON_SET else 999):
        srcs = by_slug[slug]
        if slug in FORCE_KG:  # team_00: convert every weight-bearing source to ₪/kg so forms combine
            for s in srcs:
                g = grams_of(s["unit"])
                if g and g != 1000:
                    s["price_min"] = round(s["price_min"] * 1000 / g, 2)
                    s["price_max"] = round(s["price_max"] * 1000 / g, 2)
                    s["unit"] = "ק״ג"
        org = summarize([s for s in srcs if s["organic"]], UNIT_PREFER.get(slug))
        conv = summarize([s for s in srcs if not s["organic"]], UNIT_PREFER.get(slug))
        flags = []
        if not org:
            flags.append("no-organic-source")
        elif len(org["engines"]) == 1:
            flags.append("organic-single-source")
        if org and "unit_options" in org:
            flags.append("organic-unit-ambiguity:" + "/".join(org["unit_options"]))
        if org and org["price_min"] > 0 and org["price_max"] / org["price_min"] >= 3:
            flags.append(f"organic-wide-spread(x{round(org['price_max']/org['price_min'],1)})")
        unified.append({
            "slug": slug, "hebrew_name": he_name.get(slug, ""),
            "primary": "organic" if org else "conventional",
            "organic": org, "conventional": conv,
            "_flags": flags, "_sources": srcs,
        })

    json.dump(unified, open(os.path.join(HERE, "unified_market_estimates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    covered = {u["slug"] for u in unified}
    missing = [s for s in CANON if s not in covered]
    # organic coverage tiers
    def org_tier(u):
        o = u["organic"]
        if not o: return "NONE"
        if len(o["engines"]) >= 2: return "STRONG"
        if o["confidence"] in ("high", "medium", "medium-high"): return "OK"
        return "WEAK"
    tiers = {"STRONG": [], "OK": [], "WEAK": [], "NONE": []}
    for u in unified: tiers[org_tier(u)].append(u["slug"])
    need = tiers["WEAK"] + tiers["NONE"] + [m for m in missing if m not in covered]

    L = []
    L.append("# Aggregation Summary — WP-CB-MARKET-RANGES (organic-primary, dual-basis)\n")
    L.append(f"**Engines:** {', '.join(sorted(reports))}  ·  **Coverage:** {len(covered)}/70  ·  "
             f"**Organic tiers:** STRONG {len(tiers['STRONG'])} · OK {len(tiers['OK'])} · WEAK {len(tiers['WEAK'])} · NONE {len(tiers['NONE'])}\n")
    if unknown: L.append(f"**⚠ Unknown slugs:** {', '.join(sorted(unknown))}\n")
    L.append("## Per crop — ORGANIC (primary) vs conventional (secondary)\n")
    L.append("| slug | 🌱 organic ₪ | unit | conf | conventional ₪ | unit | flags |")
    L.append("|------|-------------|------|------|----------------|------|-------|")
    def rng(e): return "—" if not e else (f"{e['price_min']}" if e['price_min']==e['price_max'] else f"{e['price_min']}–{e['price_max']}")
    for u in unified:
        o, c = u["organic"], u["conventional"]
        L.append(f"| {u['slug']} | {rng(o)} | {o['unit'] if o else ''} | {o['confidence'] if o else ''} "
                 f"| {rng(c)} | {c['unit'] if c else ''} | {'; '.join(u['_flags'])} |")
    L.append(f"\n## Organic completion-round TARGET ({len(need)} crops — WEAK organic or none)\n")
    L.append(", ".join(need) + "\n")
    L.append(f"## Missing entirely ({len(missing)}/70)\n")
    L.append(", ".join(missing) + "\n")
    open(os.path.join(HERE, "AGGREGATION_SUMMARY.md"), "w", encoding="utf-8").write("\n".join(L))

    print(f"engines: {', '.join(sorted(reports))}  ·  coverage: {len(covered)}/70")
    print(f"organic tiers: STRONG={len(tiers['STRONG'])} OK={len(tiers['OK'])} WEAK={len(tiers['WEAK'])} NONE={len(tiers['NONE'])}")
    print(f"organic completion-round target: {len(need)} crops")

if __name__ == "__main__":
    main()
