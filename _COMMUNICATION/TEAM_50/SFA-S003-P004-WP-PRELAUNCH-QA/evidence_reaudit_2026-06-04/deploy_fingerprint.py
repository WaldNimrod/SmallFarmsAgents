#!/usr/bin/env python3
"""Deploy fingerprint — live acca9b2 @ ?v=1780576560 (read-only)."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = "https://sfa.nimrod.bio"
V = "1780576560"
CTX = ssl.create_default_context()


def get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "SFA-reaudit-team50/2026-06-04"})
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def main() -> None:
    out: dict = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "base": BASE,
        "expected_sha": "acca9b2",
        "expected_v": V,
    }

    code, health_body = get(f"{BASE}/api/v1/health")
    out["health"] = {"code": code, "body": json.loads(health_body) if code == 200 else health_body[:200]}

    _, cb_css = get(f"{BASE}/public_assets/css/crop-book-v1.css?v={V}")
    _, cl_css = get(f"{BASE}/public_assets/css/classb.css?v={V}")
    out["fidelity_css"] = {
        "cb_paths_grid": "cb-paths { display: grid" in cb_css or ".cb-paths{display:grid" in cb_css.replace(" ", ""),
        "cards_grid_168": "minmax(168px" in cb_css,
        "crop_detail_1120": "max-width:1120px" in cb_css and "margin-inline:auto" in cb_css,
        "wi5_comment": "WI-5" in cb_css,
        "sh_mark_svg": ".sh__mark svg" in cl_css,
        "crop_book_v1_bytes": len(cb_css),
        "classb_bytes": len(cl_css),
    }

    _, home = get(f"{BASE}/?v={V}")
    vers = re.findall(r"(crop-book-v1|classb|crop-book-deep)\.css\?v=(\d+)", home)
    out["asset_versions_home"] = {k: v for k, v in vers}
    out["served_v_matches"] = str(V) in [v for _, v in vers]

    _, cb_html = get(f"{BASE}/crop-book/?v={V}")
    out["crop_book"] = {
        "wc_img_refs": len(re.findall(r"wc-[a-z0-9-]+\.png", cb_html)),
        "glyph_only_cards": cb_html.count("crop-glyph"),
    }

    _, mkt = get(f"{BASE}/market/?v={V}")
    eng_chips = re.findall(r">([a-z_]{8,})<", mkt)
    out["market"] = {
        "english_chip_slugs_in_html": [x for x in eng_chips if "_" in x][:15],
        "ptable_th": mkt.count("ptable__th"),
    }

    route_checks = [
        f"/crop-book/?v={V}",
        f"/crop-book/lettuce/?depth=simple&v={V}",
        f"/calc/?v={V}",
        f"/account?v={V}",
    ]
    out["route_http"] = {}
    for path in route_checks:
        code, _ = get(f"{BASE}{path}")
        out["route_http"][path] = code

    path = OUT / "deploy_fingerprint.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
