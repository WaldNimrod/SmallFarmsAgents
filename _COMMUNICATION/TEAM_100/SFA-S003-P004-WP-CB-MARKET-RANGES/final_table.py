#!/usr/bin/env python3
"""Final result table sorted by DATA QUALITY (high→low) for sign-off.
Per crop (organic, natural display unit): range + median, n engines, std, CV% (dispersion), conventional.
Quality tier A>B>C>D>E>F; within tier sort by n desc then CV asc."""
import json, os, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "unified_market_estimates.json"), encoding="utf-8"))
canon = [s for s in re.findall(r'"([a-z0-9-]+)"',
         re.search(r'CANON = \[(.*?)\]', open(os.path.join(HERE,"aggregate_market_ranges.py")).read(), re.S).group(1))]
by = {u["slug"]: u for u in d}
HE_MISS = {"jicama": "ג'יקמה"}
# crops whose wide range is a known size/form issue (flagged in the deep-dive)
FLAG = {"strawberry": "show per 250g punnet (₪19–30); ₪/kg loose inflates",
        "bush-pole":  "fresh ₪/kg vs frozen 500g pack — different products"}

def stats(u):
    o = u["organic"]
    if not o: return None
    dom = o["unit"]
    pe = {}
    for s in u["_sources"]:
        if s["organic"] and s["unit"] == dom:
            pe.setdefault(s["engine"], []).append((s["price_min"]+s["price_max"])/2)
    pts = [statistics.mean(v) for v in pe.values()]
    n = len(pts)
    std = statistics.pstdev(pts) if n >= 2 else None
    med = o["price_median"]
    cv = (std/med*100) if (std and med) else None
    return dict(unit=dom, n=n, std=std, cv=cv, lo=o["price_min"], med=med, hi=o["price_max"], conf=o["confidence"])

def tier(u, st):
    if u["slug"] not in by: return "F"      # missing
    if not st: return "E"                    # no organic (conventional only)
    cv = st["cv"] if st["cv"] is not None else 999
    if st["n"] >= 2 and cv < 20: return "A"  # multi-source, tight
    if st["n"] >= 2 and cv < 40: return "B"  # multi-source, moderate spread
    if st["n"] >= 2: return "C"              # multi-source, wide spread
    if st["conf"] in ("high","medium","medium-high"): return "C"  # single decent source
    return "D"                               # single thin source
TR = {"A":0,"B":1,"C":2,"D":3,"E":4,"F":5}

rows = []
for slug in canon:
    if slug not in by:
        rows.append((slug, HE_MISS.get(slug,"?"), None, "F")); continue
    u = by[slug]; st = stats(u); rows.append((slug, u["hebrew_name"], st, tier(u, st)))
rows.sort(key=lambda r: (TR[r[3]], -(r[2]["n"] if r[2] else 0), (r[2]["cv"] if (r[2] and r[2]["cv"] is not None) else 999)))

def conv(u):
    c = u["conventional"]
    if not c: return "—"
    w = " ⚠whl" if "wholesale" in c["basis"] else ""
    return (f"{c['price_min']}–{c['price_max']} {c['unit']}" if c['price_max']!=c['price_min'] else f"{c['price_min']} {c['unit']}") + w
def f(x): return "—" if x is None else f"{x:.1f}"

TIER_LBL = {"A":"A 🟢 multi-source, tight (CV<20%)","B":"B 🟢 multi-source, moderate (CV 20–40%)",
            "C":"C 🟡 wide spread / single decent source","D":"D 🟡 single thin source",
            "E":"E 🟠 no organic — conventional only","F":"F ⬜ missing"}
L = ["# FINAL market-estimate table — sorted by data quality (organic-primary)\n"]
from collections import Counter
tc = Counter(r[3] for r in rows)
L.append("**Quality:** " + " · ".join(f"{t}={tc.get(t,0)}" for t in "ABCDEF") + f"  (total {len(rows)})\n")
L.append("range/median/unit = what the user sees (organic). n = engines. CV% = std÷median (lower = more agreement).\n")
cur = None
for slug, hn, st, t in rows:
    if t != cur:
        cur = t; L.append(f"\n### {TIER_LBL[t]}\n")
        L.append("| crop | he | organic: ₪ min–**med**–max | unit | n | ±std | CV% | conventional ₪ | note |")
        L.append("|------|----|---------------------------|------|---|------|-----|----------------|------|")
    if not st:
        cv = conv(by[slug]) if slug in by else "—"
        L.append(f"| {slug} | {hn} | — | — | 0 | — | — | {cv} | {FLAG.get(slug,'')} |"); continue
    rng = f"{st['lo']}–**{st['med']}**–{st['hi']}" if st['hi']!=st['lo'] else f"**{st['med']}**"
    L.append(f"| {slug} | {hn} | {rng} | {st['unit']} | {st['n']} | {f(st['std'])} | {f(st['cv'])} | {conv(by[slug])} | {FLAG.get(slug,'')} |")
open(os.path.join(HERE,"FINAL_TABLE.md"),"w",encoding="utf-8").write("\n".join(L))
print("tiers:", dict(tc))
print("\n".join(L))
