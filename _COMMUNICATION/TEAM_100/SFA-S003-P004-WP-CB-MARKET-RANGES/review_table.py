#!/usr/bin/env python3
"""Full statistical review table for pre-ingest sign-off.
Normalizes weight units to ₪/kg so prices are COMPARABLE (₪/kg, ₪/200g→₪/kg, etc. collapse to one basis);
bunch/unit items (צרור/יחידה/מארז-no-weight) keep their own basis. Per crop, on the DOMINANT basis:
n engines, mean ± std of per-engine values, dispersion CV%, range, TRUE outliers (>2σ), conventional, status."""
import json, os, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "unified_market_estimates.json"), encoding="utf-8"))
canon = [s for s in re.findall(r'"([a-z0-9-]+)"',
         re.search(r'CANON = \[(.*?)\]', open(os.path.join(HERE, "aggregate_market_ranges.py")).read(), re.S).group(1))]
by = {u["slug"]: u for u in d}
he = {u["slug"]: u["hebrew_name"] for u in d}
HE_MISS = {"jicama": "ג'יקמה"}

def grams_of(unit):
    """grams represented by a unit string, or None for bunch/unit (no weight)."""
    u = unit or ""
    if re.search(r'ק["״]?ג|קילו|\bkg\b', u):
        m = re.search(r'(\d+(?:\.\d+)?)\s*ק', u)            # "חבילה 1 ק״ג"
        return (float(m.group(1)) if m else 1) * 1000
    m = re.search(r'(\d+)(?:\s*[–-]\s*(\d+))?\s*(?:גרם|גר|g)\b', u)  # "מארז 190–200 גרם"
    if m:
        a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
        return (a + b) / 2
    return None

def basis_val(s):
    """Return (basis, value) for a source: ('₪/kg', kg-price) if weighable, else (unit, price)."""
    mid = (s["price_min"] + s["price_max"]) / 2
    g = grams_of(s["unit"])
    if g:
        return "₪/kg", round(mid * 1000 / g, 2)
    return (s["unit"] or "?"), mid

def analyze(u):
    org = [s for s in u["_sources"] if s["organic"]]
    if not org:
        return None
    # group per basis → per engine → values
    bb = {}
    for s in org:
        b, v = basis_val(s)
        bb.setdefault(b, {}).setdefault(s["engine"], []).append(v)
    # dominant basis = most distinct engines
    dom = max(bb, key=lambda b: len(bb[b]))
    pe = {e: statistics.mean(vs) for e, vs in bb[dom].items()}
    pts = list(pe.values())
    n = len(pts)
    mean = statistics.mean(pts)
    std = statistics.pstdev(pts) if n >= 2 else None
    cv = (std / mean * 100) if (std and mean) else None
    lo, hi = min(pts), max(pts)
    outliers = []
    if std and std > 0:
        for e, v in pe.items():
            if abs(v - mean) > 2 * std:
                outliers.append(f"{e}≈{round(v)}")
    minority = {b: sorted({e for e in bb[b]}) for b in bb if b != dom}
    return dict(basis=dom, n=n, mean=mean, std=std, cv=cv, lo=lo, hi=hi,
                outliers=outliers, minority=minority, conf=u["organic"]["confidence"])

def conv_kg(u):
    c = u["conventional"]
    if not c:
        return "—"
    g = grams_of(c["unit"])
    if g and g != 1000:
        lo, hi = round(c["price_min"] * 1000 / g, 1), round(c["price_max"] * 1000 / g, 1)
        u_ = "₪/kg"
    else:
        lo, hi, u_ = c["price_min"], c["price_max"], c["unit"]
    w = " ⚠whl" if "wholesale" in c["basis"] else ""
    return (f"{lo}–{hi} {u_}" if hi != lo else f"{lo} {u_}") + w

def status(u, a):
    if u["slug"] not in by: return "MISSING"
    if not a: return "NONE-org"
    if a["n"] >= 2: return "STRONG"
    if a["conf"] in ("high", "medium", "medium-high"): return "OK"
    return "WEAK"

def f(x): return "—" if x is None else (f"{x:.1f}" if isinstance(x, float) else str(x))

rows = []
for i, slug in enumerate(canon, 1):
    if slug not in by:
        rows.append((i, slug, HE_MISS.get(slug, "?"), None, "MISSING")); continue
    u = by[slug]; a = analyze(u); rows.append((i, slug, he.get(slug, ""), a, status(u, a)))

ship = sum(1 for *_, s in rows if s in ("STRONG", "OK"))
L = ["# Market-ranges — FULL STATISTICAL REVIEW (₪/kg-normalized, pre-ingest sign-off)\n"]
L.append(f"4 engines · 7 reports · weight units normalized to **₪/kg** for comparability (bunch/unit kept as-is).\n")
L.append(f"**{sum(1 for *_,s in rows if s!='MISSING')}/70 covered** · STRONG {sum(1 for *_,s in rows if s=='STRONG')} · "
         f"OK {sum(1 for *_,s in rows if s=='OK')} · WEAK {sum(1 for *_,s in rows if s=='WEAK')} · "
         f"no-organic {sum(1 for *_,s in rows if s=='NONE-org')} · missing {sum(1 for *_,s in rows if s=='MISSING')} · ship-ready {ship}\n")
L.append("| # | crop | he | basis | n | mean | ±std | CV% | range | outliers | conv | status |")
L.append("|---|------|----|-------|---|------|------|-----|-------|----------|------|--------|")
for i, slug, hn, a, st in rows:
    if not a:
        cv = conv_kg(by[slug]) if slug in by else "—"
        L.append(f"| {i} | {slug} | {hn} | — | 0 | — | — | — | — | — | {cv} | **{st}** |"); continue
    other = (" +" + ",".join(f"{len(v)}×{b}" for b, v in a["minority"].items())) if a["minority"] else ""
    rng = f"{f(a['lo'])}–{f(a['hi'])}" if a['hi'] != a['lo'] else f(a['lo'])
    flag = "🔴" if (a["cv"] or 0) >= 35 or a["outliers"] else ("🟡" if st in ("WEAK","OK") else "🟢")
    L.append(f"| {i} | {slug} | {hn} | {a['basis']}{other} | {a['n']} | {f(a['mean'])} | {f(a['std'])} | "
             f"{f(a['cv'])} | {rng} | {'; '.join(a['outliers']) or '—'} | {conv_kg(by[slug])} | {flag}{st} |")

# attention sections
L.append("\n## 🔴 High dispersion (CV ≥ 35%) or outliers — eyeball before ingest\n")
for i, slug, hn, a, st in rows:
    if a and ((a["cv"] or 0) >= 35 or a["outliers"]):
        L.append(f"- **{slug}** ({hn}): {a['basis']} {f(a['lo'])}–{f(a['hi'])}, mean {f(a['mean'])} ±{f(a['std'])} (CV {f(a['cv'])}%)"
                 + (f" · OUTLIERS {', '.join(a['outliers'])}" if a["outliers"] else "")
                 + (f" · minority bases {dict((b,len(v)) for b,v in a['minority'].items())}" if a["minority"] else ""))
L.append("\n## Gaps (decide: omit, or show conventional)\n")
for i, slug, hn, a, st in rows:
    if st in ("MISSING", "NONE-org"):
        L.append(f"- **{slug}** ({hn}): {st} · conventional: {conv_kg(by[slug]) if slug in by else 'none'}")
open(os.path.join(HERE, "REVIEW_TABLE.md"), "w", encoding="utf-8").write("\n".join(L))
print(f"ship-ready {ship} · high-disp/outlier {sum(1 for *_,a,_ in rows if a and ((a['cv'] or 0)>=35 or a['outliers']))} · "
      f"gaps {sum(1 for *_,s in rows if s in ('MISSING','NONE-org'))}")
