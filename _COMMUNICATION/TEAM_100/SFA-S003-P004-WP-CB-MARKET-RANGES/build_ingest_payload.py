#!/usr/bin/env python3
"""unified_market_estimates.json → market_estimate_payload.json (slug → the market_estimate object
written into crops.payload_json). Flat top-level = the PRIMARY estimate (organic if present, else
conventional) so the live chip works unchanged; nested organic{}/conventional{} + optional note."""
import json, os
H=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(H,"unified_market_estimates.json"),encoding="utf-8"))
def slim(e):
    if not e: return None
    o={"price_min":e["price_min"],"price_max":e["price_max"],"price_median":e["price_median"],
       "unit":e["unit"],"confidence":e["confidence"],"n_sources":e["n_sources"]}
    if "wholesale" in e.get("basis",""): o["basis"]="wholesale"
    return o
out={}
for u in d:
    org,conv=u["organic"],u["conventional"]
    prim = org or conv
    if not prim: continue
    me={"price_min":prim["price_min"],"price_max":prim["price_max"],"price_median":prim["price_median"],
        "unit":prim["unit"],"primary":"organic" if org else "conventional","as_of":"2026-06"}
    if org: me["organic"]=slim(org)
    if conv: me["conventional"]=slim(conv)
    if u.get("note"): me["note"]=u["note"]
    out[u["slug"]]=me
json.dump(out,open(os.path.join(H,"market_estimate_payload.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(f"built market_estimate for {len(out)} crops")
print("hibiscus:", json.dumps(out.get("hibiscus"),ensure_ascii=False))
print("tomatoes:", json.dumps(out.get("tomatoes"),ensure_ascii=False))
