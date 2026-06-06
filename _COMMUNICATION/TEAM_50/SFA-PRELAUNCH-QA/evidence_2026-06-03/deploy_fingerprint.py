#!/usr/bin/env python3
"""Phase 0 deploy fingerprint — read-only."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = "https://sfa.nimrod.bio"
CTX = ssl.create_default_context()


def get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "SFA-prelaunch-team50/2026-06-03"})
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def main() -> None:
    out: dict = {"ts": datetime.now(timezone.utc).isoformat(), "base": BASE}

    code, health_body = get(f"{BASE}/api/v1/health")
    out["health"] = {"code": code, "body": json.loads(health_body) if code == 200 else health_body[:200]}

    _, cb_css = get(f"{BASE}/public_assets/css/crop-book-v1.css")
    _, cl_css = get(f"{BASE}/public_assets/css/classb.css")
    out["patch01_css"] = {
        "wi5_cb_paths_grid": "cb-paths { display: grid" in cb_css,
        "wi5_comment": "WI-5" in cb_css,
        "wi6_sh_mark_svg": ".sh__mark svg { width: 100%" in cl_css,
        "wi6_comment": "WI-6" in cl_css,
        "crop_book_v1_css_bytes": len(cb_css),
        "classb_css_bytes": len(cl_css),
    }

    _, home = get(f"{BASE}/")
    vers = re.findall(r"(crop-book-v1|classb)\.css\?v=(\d+)", home)
    out["asset_versions_home"] = {k: v for k, v in vers}

    class_b = {}
    probes = {
        "hub_home_inner": ("/", "hub-home__inner"),
        "community_contact_webp": ("/community", "contact.webp"),
        "search_reqinfo": ("/search?q=zzznomatch190", "reqinfo"),
        "search_glyph": ("/search?q=zzznomatch190", "◐"),
        "market_ptable_th": ("/market/", "ptable__th"),
    }
    for key, (path, marker) in probes.items():
        _, html = get(f"{BASE}{path}")
        class_b[key] = html.count(marker)
    _, comm = get(f"{BASE}/community")
    class_b["community_aria_current"] = comm.count('aria-current="page"')
    class_b["community_footer_self_link"] = bool(
        re.search(r'href="/community"[^>]*>קהילה</a>', comm) and 'aria-current="page"' not in comm
    )
    out["class_b_markers"] = class_b

    _, crops_raw = get(f"{BASE}/api/v1/crops")
    crops = json.loads(crops_raw)
    items = crops if isinstance(crops, list) else crops.get("items", [])
    slugs = [x.get("slug") for x in items]
    out["crops"] = {
        "count": len(items),
        "test_slugs": {
            s: s in slugs
            for s in (
                "tomatoes",
                "lettuce",
                "carrots",
                "cauliflower",
                "anise-hyssop",
            )
        },
    }

    _, products_raw = get(f"{BASE}/api/v1/products")
    products = json.loads(products_raw)
    pitems = products if isinstance(products, list) else products.get("items", [])
    priced = [p for p in pitems if p.get("last_price") is not None]
    out["products"] = {
        "count": len(pitems),
        "market_detail_slug": priced[0]["slug"] if priced else "prd017",
        "priced_count": len(priced),
    }

    route_checks = [
        "/crop-book/",
        "/crop-book/lettuce/?depth=simple",
        "/crop-book/tomatoes/?depth=full",
        "/crop-book/anise-hyssop/variety/variety-11/",
        "/calc/",
        "/calc/print",
        "/account",
    ]
    out["route_http"] = {}
    for path in route_checks:
        code, _ = get(f"{BASE}{path}")
        out["route_http"][path] = code

    out["mandate_sha_7fbcf89"] = {
        "expected": "7fbcf89",
        "live_wi5": out["patch01_css"]["wi5_cb_paths_grid"],
        "live_wi6": out["patch01_css"]["wi6_sh_mark_svg"],
        "deploy_report_sha": "08f529d",
        "live_matches_mandate_tip": out["patch01_css"]["wi5_cb_paths_grid"]
        and out["patch01_css"]["wi6_sh_mark_svg"],
    }

    path = OUT / "deploy_fingerprint.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
