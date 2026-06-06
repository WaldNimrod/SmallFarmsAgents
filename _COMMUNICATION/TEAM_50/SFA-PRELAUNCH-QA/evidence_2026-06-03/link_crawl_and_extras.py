#!/usr/bin/env python3
"""C-F link crawl, contribute test, §7 discretionary checks."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

OUT = Path(__file__).resolve().parent
BASE = "https://sfa.nimrod.bio"
CTX = ssl.create_default_context()
UA = {"User-Agent": "SFA-prelaunch-team50/2026-06-03"}


def fetch(url: str, method: str = "GET", data: bytes | None = None, headers: dict | None = None) -> tuple[int, str, dict]:
    h = {**UA, **(headers or {})}
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace"), dict(e.headers)


def crawl(start_paths: list[str]) -> dict:
    seen: set[str] = set()
    queue = list(start_paths)
    results = []
    host = urlparse(BASE).netloc
    while queue and len(seen) < 120:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if not path.startswith("/") or path.startswith("//"):
            continue
        code, body, _ = fetch(BASE + path)
        results.append({"path": path, "code": code})
        if code != 200 or "text/html" not in body[:200].lower() and "<html" not in body[:5000].lower():
            continue
        for href in re.findall(r'href="(/[^"#?][^"]*)"', body):
            if href.startswith("/api/") or href.endswith((".css", ".js", ".png", ".webp", ".svg", ".csv")):
                continue
            if href not in seen and href not in queue:
                queue.append(href)
    return {"checked": len(results), "results": results, "broken": [r for r in results if r["code"] >= 400]}


def main() -> None:
    out: dict = {"ts": datetime.now(timezone.utc).isoformat()}

    out["link_crawl"] = crawl(["/", "/crop-book/", "/market/", "/calc/", "/community"])

    payload = json.dumps(
        {
            "kind": "request-info",
            "message": "PRELAUNCH-QA team_50 test 2026-06-03 — safe to discard",
            "contact": "qa-test@example.invalid",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    code, body, hdrs = fetch(
        f"{BASE}/api/v1/contribute",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    out["contribute"] = {"code": code, "body": body[:500], "content_type": hdrs.get("Content-Type")}

    extras = {}
    for path in ["/", "/crop-book/", "/calc/", "/robots.txt"]:
        code, body, hdrs = fetch(BASE + path if path != "/robots.txt" else BASE + path)
        extras[path] = {
            "code": code,
            "title": (re.search(r"<title>([^<]+)</title>", body) or [None, None])[1],
            "og_title": (re.search(r'property="og:title" content="([^"]*)"', body) or [None, None])[1],
            "description": (re.search(r'name="description" content="([^"]*)"', body) or [None, None])[1],
        }
    code404, body404, _ = fetch(f"{BASE}/crop-book/zzznomatch-slug-qa/")
    extras["404_crop"] = {"code": code404, "has_error_shell": "error" in body404.lower() or "404" in body404}

    _, _, hdrs = fetch(f"{BASE}/")
    extras["security_headers"] = {
        k: hdrs.get(k) or hdrs.get(k.lower())
        for k in (
            "Strict-Transport-Security",
            "X-Frame-Options",
            "Content-Security-Policy",
            "X-Content-Type-Options",
        )
    }

    _, calc_html, _ = fetch(f"{BASE}/calc/")
    extras["calc_assets"] = {
        "crop_book_v1_js": "crop-book-v1.js" in calc_html,
        "sfa_calc": "SFA_CALC" in calc_html or "crop-book-v1.js" in calc_html,
        "modcard_count": calc_html.count("modcard"),
        "modcard_disabled": calc_html.count("modcard--disabled"),
        "data_calc": len(re.findall(r'data-calc="[^"]+"', calc_html)),
    }

    out["extras"] = extras
    path = OUT / "link_crawl_and_extras.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
