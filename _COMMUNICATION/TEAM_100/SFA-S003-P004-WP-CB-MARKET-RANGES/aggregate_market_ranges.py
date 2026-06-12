#!/usr/bin/env python3
"""
aggregate_market_ranges.py — WP-CB-MARKET-RANGES multi-engine aggregator.

Reads every *.json engine report in ./research_inputs/ (each = a JSON array of
{slug, hebrew_name, market_estimate:{price_min,price_max,unit,organic,source,source_url,as_of,confidence}}),
merges them per crop with full provenance, flags data-quality issues, and writes:
  - unified_market_estimates.json   (per crop: recommended estimate + _sources[] + _flags[])
  - AGGREGATION_SUMMARY.md          (coverage + merged table + flags for human review)

Re-run after dropping each new engine report into research_inputs/. team_80 = advisory research; team_100
reviews the unified file, then ingests the accepted market_estimate via WP-CB-DATA-API (NO seed --all).
"""
import json, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "research_inputs")

# Canonical 70 crop slugs (from sfa.nimrod.bio/api/v1/crops, 2026-06-12) — for coverage.
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

# A source is WHOLESALE-basis (farm-gate / סיטונאי, far below consumer retail) if it matches these.
WHOLESALE_HINTS = ["moag", "מועצת הצמחים", "משרד החקלאות", "סיטונא", "moonsite"]

def is_wholesale(src, url):
    blob = f"{src or ''} {url or ''}".lower()
    return any(h.lower() in blob for h in WHOLESALE_HINTS)

def norm_unit(u):
    """Canonicalize selling units so ק\"ג == ק״ג (ASCII quote vs Hebrew gershayim) etc."""
    if not u:
        return ""
    u = u.strip().replace('"', '״').replace("'", "׳")
    base = u.replace(' ', '')
    if base in ('ק״ג', 'קילו', 'קילוגרם', 'קג', 'kg'):
        return 'ק״ג'
    if base in ('יח׳', 'יחידה', 'יח', 'unit'):
        return 'יחידה'
    if base in ('אגודה', 'צרור', 'bunch'):
        return 'צרור'
    if base in ('מארז', 'חבילה', 'pack'):
        return 'מארז'
    return u

def load_reports():
    reports = {}
    for path in sorted(glob.glob(os.path.join(INPUTS, "*.json"))):
        engine = os.path.splitext(os.path.basename(path))[0]
        try:
            reports[engine] = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            print(f"WARN: could not parse {path}: {e}", file=sys.stderr)
    return reports

def main():
    reports = load_reports()
    if not reports:
        print("No engine reports in research_inputs/. Drop <engine>.json files there and re-run.")
        return

    # slug -> list of source dicts (with engine + basis)
    by_slug = {}
    he_name = {}
    unknown_slugs = set()
    for engine, rows in reports.items():
        for row in rows:
            slug = (row.get("slug") or "").strip()
            me = row.get("market_estimate") or {}
            if not slug or not me:
                continue
            if slug not in CANON_SET:
                unknown_slugs.add(slug)
            he_name.setdefault(slug, row.get("hebrew_name", ""))
            src = me.get("source", ""); url = me.get("source_url", "")
            by_slug.setdefault(slug, []).append({
                "engine": engine,
                "price_min": float(me.get("price_min", 0) or 0),
                "price_max": float(me.get("price_max", me.get("price_min", 0)) or 0),
                "unit": norm_unit(me.get("unit") or ""),
                "organic": bool(me.get("organic", False)),
                "source": src, "source_url": url,
                "as_of": me.get("as_of", ""),
                "confidence": me.get("confidence", ""),
                "basis": "wholesale" if is_wholesale(src, url) else "retail",
            })

    unified = []
    for slug in sorted(by_slug, key=lambda s: CANON.index(s) if s in CANON_SET else 999):
        srcs = by_slug[slug]
        engines = sorted({s["engine"] for s in srcs})
        units = sorted({s["unit"] for s in srcs if s["unit"]})
        bases = sorted({s["basis"] for s in srcs})
        organics = {s["organic"] for s in srcs}
        retail = [s for s in srcs if s["basis"] == "retail"]
        organic_retail = [s for s in retail if s["organic"]]
        # Recommended pool: prefer organic-retail > retail > all (the chip is consumer/retail facing).
        pool = organic_retail or retail or srcs
        # Robust outlier trim for the recommended RANGE: drop a source whose midpoint is > 3x the pool's
        # median midpoint (e.g. a restaurant-menu price). Dropped sources stay in _sources (transparency).
        mids = sorted((s["price_min"] + s["price_max"]) / 2 for s in pool)
        floor = mids[0] if mids else 0  # cheapest source midpoint
        pool_r = [s for s in pool if floor == 0 or (s["price_min"] + s["price_max"]) / 2 <= 3 * floor] or pool
        excluded = [s for s in pool if s not in pool_r]
        rmin = min(s["price_min"] for s in pool_r)
        rmax = max(s["price_max"] for s in pool_r)
        # unit: consensus of the trimmed pool, else the most common
        pool_units = [s["unit"] for s in pool_r if s["unit"]]
        unit = max(set(pool_units), key=pool_units.count) if pool_units else (units[0] if units else "")
        pool = pool_r  # the recommended estimate (range/unit/confidence) uses the trimmed pool
        flags = []
        if excluded:
            flags.append("outlier-excluded:" + "/".join(f"{s['engine']}@₪{s['price_max']}" for s in excluded))
        if len(units) > 1: flags.append(f"unit-conflict:{'/'.join(units)}")
        if "wholesale" in bases and "retail" not in bases: flags.append("wholesale-only-basis(below-retail)")
        if "wholesale" in bases and "retail" in bases: flags.append("mixed-basis(wholesale+retail)")
        if organics == {False}: flags.append("conventional-only(no-organic-source)")
        if len(srcs) == 1 and srcs[0]["confidence"] == "low": flags.append("single-source-low-confidence")
        if rmin > 0 and rmax / rmin >= 2.5: flags.append(f"wide-spread(x{round(rmax/rmin,1)})")
        # derived confidence
        if len({s["engine"] for s in pool}) >= 2: conf = "high"
        elif any(s["confidence"] == "high" for s in pool): conf = "medium-high"
        else: conf = max((s["confidence"] for s in pool), key=lambda c: {"high":3,"medium":2,"low":1,"":0}.get(c,0))
        unified.append({
            "slug": slug,
            "hebrew_name": he_name.get(slug, ""),
            "market_estimate": {
                "price_min": round(rmin, 2), "price_max": round(rmax, 2), "unit": unit,
                "organic": bool(organic_retail),
                "as_of": max((s["as_of"] for s in srcs), default=""),
                "confidence": conf,
            },
            "_engines": engines,
            "_flags": flags,
            "_sources": srcs,
        })

    out_json = os.path.join(HERE, "unified_market_estimates.json")
    json.dump(unified, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    covered = [u["slug"] for u in unified]
    missing = [s for s in CANON if s not in set(covered)]
    flagged = [u for u in unified if u["_flags"]]

    # Summary markdown
    lines = []
    lines.append(f"# Aggregation Summary — WP-CB-MARKET-RANGES (multi-engine)\n")
    lines.append(f"**Engines merged:** {', '.join(sorted(reports))}  ·  **Coverage:** {len(covered)}/70  ·  **Flagged for review:** {len(flagged)}\n")
    if unknown_slugs:
        lines.append(f"**⚠ Unknown slugs (not in canonical 70):** {', '.join(sorted(unknown_slugs))}\n")
    lines.append("## Merged estimates\n")
    lines.append("| slug | ₪ range | unit | organic | basis | conf | engines | flags |")
    lines.append("|------|---------|------|---------|-------|------|---------|-------|")
    for u in unified:
        me = u["market_estimate"]
        bases = '/'.join(sorted({s["basis"] for s in u["_sources"]}))
        rng = f"{me['price_min']}–{me['price_max']}" if me['price_max'] != me['price_min'] else f"{me['price_min']}"
        lines.append(f"| {u['slug']} | {rng} | {me['unit']} | {'✓' if me['organic'] else '—'} | {bases} | {me['confidence']} | {len(u['_engines'])} | {'; '.join(u['_flags'])} |")
    lines.append(f"\n## Missing ({len(missing)}/70 — no engine sourced these yet)\n")
    lines.append(", ".join(f"{s}" for s in missing) + "\n")
    open(os.path.join(HERE, "AGGREGATION_SUMMARY.md"), "w", encoding="utf-8").write("\n".join(lines))

    # console
    print(f"engines: {', '.join(sorted(reports))}")
    print(f"coverage: {len(covered)}/70  ·  missing: {len(missing)}  ·  flagged: {len(flagged)}")
    print(f"basis breakdown: retail-only={sum(1 for u in unified if {s['basis'] for s in u['_sources']}=={'retail'})}, "
          f"wholesale-involved={sum(1 for u in unified if any(s['basis']=='wholesale' for s in u['_sources']))}")
    print(f"organic-retail crops: {sum(1 for u in unified if u['market_estimate']['organic'])}")
    print(f"→ {out_json}")
    print(f"→ {os.path.join(HERE,'AGGREGATION_SUMMARY.md')}")

if __name__ == "__main__":
    main()
