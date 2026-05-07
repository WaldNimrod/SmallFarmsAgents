#!/usr/bin/env python3
"""
Merge Team 80 suspected MyPIPS URLs with Team 10 experiment URLs, probe each URL,
and write a CSV with storefront_likely_active (is_likely_active heuristic).

Usage (repo root):
    python3 scripts/mypips_verify_suspected_csv.py \\
        --in-csv _COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv \\
        --out-csv _COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv \\
        --delay 0.5
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import httpx  # noqa: E402

from organic_market_agent.discovery.mypips_scan import (  # noqa: E402
    DEFAULT_HEADERS,
    extract_title,
    is_likely_active,
)

# URLs validated in 2026-04-05 multi-layer discovery (L1+L2 probe); all were active=True except hilinoa.
_TEAM10_STORE_URLS = [
    "https://mypips.app/barshah",
    "https://mypips.app/anatiyot",
    "https://mypips.app/arava",
    "https://mypips.app/bestfruit",
    "https://mypips.app/brodavkameshek",
    "https://mypips.app/cohen",
    "https://mypips.app/finerotem",
    "https://mypips.app/fourminimonline",
    "https://mypips.app/freshness",
    "https://mypips.app/fruit4soul",
    "https://mypips.app/hagitsigal",
    "https://mypips.app/mahlevot-habraun",
    "https://mypips.app/mashtelatharoe",
    "https://mypips.app/meshek-herskovits",
    "https://mypips.app/meshek27",
    "https://mypips.app/mesheknaveh",
    "https://mypips.app/mypips",
    "https://mypips.app/nimrod",
    "https://mypips.app/organicaganyarak-home",
    "https://mypips.app/poli",
    "https://mypips.app/popisrael",
    "https://mypips.app/sal-hagolan",
    "https://mypips.app/salata",
    "https://mypips.app/shaked",
    "https://mypips.app/solomon",
    "https://mypips.app/the-group",
    "https://mypips.app/thelab",
    "https://mypips.app/veghit",
    "https://mypips.app/vigenbari",
    "https://mypips.app/we-connect",
]


def _norm_url(u: str) -> str:
    u = u.strip()
    if not u:
        return ""
    p = urlparse(u)
    if not p.scheme:
        u = "https://" + u
        p = urlparse(u)
    netloc = (p.netloc or "").lower()
    if netloc == "mypips.app":
        path = (p.path or "/").lower()
        return f"https://mypips.app{path}" + (f"?{p.query}" if p.query else "")
    return u


async def _fetch_one(client: httpx.AsyncClient, url: str) -> tuple[int, int, bool, str]:
    try:
        resp = await client.get(url, follow_redirects=True)
        text = resp.text or ""
        active = is_likely_active(resp.status_code, text)
        title = extract_title(text) if text else ""
        return resp.status_code, len(text), active, title
    except httpx.HTTPError:
        return 0, 0, False, ""
    except Exception:
        return 0, 0, False, ""


async def _run(urls: list[str], delay: float, timeout_s: float) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    timeout = httpx.Timeout(timeout_s)
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=timeout) as client:
        for i, url in enumerate(urls):
            status, blen, active, title = await _fetch_one(client, url)
            out.append(
                {
                    "url": url,
                    "http_status": status,
                    "body_len": blen,
                    "storefront_likely_active": active,
                    "page_title": title[:500] if title else "",
                }
            )
            if delay > 0 and i + 1 < len(urls):
                await asyncio.sleep(delay)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-csv", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    rows_in: list[dict[str, str]] = []
    with args.in_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("url", "").strip():
                rows_in.append(row)

    seen: set[str] = set()
    merged: list[dict[str, str]] = []

    for row in rows_in:
        nu = _norm_url(row["url"])
        if not nu.startswith("https://mypips.app"):
            continue
        if nu in seen:
            continue
        seen.add(nu)
        merged.append(
            {
                "url": nu,
                "confidence": row.get("confidence", ""),
                "basis": row.get("basis", ""),
                "evidence_source": row.get("evidence_source", ""),
                "source_batch": "team80_csv",
            }
        )

    for u in _TEAM10_STORE_URLS:
        nu = _norm_url(u)
        if nu in seen:
            continue
        seen.add(nu)
        merged.append(
            {
                "url": nu,
                "confidence": "high",
                "basis": "Team 10 L1+L2 discovery experiment 2026-04-05; probed active storefront",
                "evidence_source": "team10_layer_experiment",
                "source_batch": "team10_experiment",
            }
        )

    urls = [m["url"] for m in merged]
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = asyncio.run(_run(urls, args.delay, args.timeout))
    res_by_url = {r["url"]: r for r in results}

    fieldnames = [
        "url",
        "http_status",
        "body_len",
        "storefront_likely_active",
        "page_title",
        "checked_at",
        "confidence",
        "basis",
        "evidence_source",
        "source_batch",
    ]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for m in merged:
            u = m["url"]
            r = res_by_url[u]
            w.writerow(
                {
                    "url": u,
                    "http_status": r["http_status"],
                    "body_len": r["body_len"],
                    "storefront_likely_active": r["storefront_likely_active"],
                    "page_title": r["page_title"],
                    "checked_at": checked_at,
                    "confidence": m["confidence"],
                    "basis": m["basis"],
                    "evidence_source": m["evidence_source"],
                    "source_batch": m["source_batch"],
                }
            )

    active_n = sum(1 for r in results if r["storefront_likely_active"])
    print(f"Wrote {len(merged)} rows to {args.out_csv}")
    print(f"storefront_likely_active=True: {active_n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
