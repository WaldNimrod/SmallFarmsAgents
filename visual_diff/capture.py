#!/usr/bin/env python3
"""
SFA UI RE-BUILD: 42-screenshot capture sub-agent D2.
3 viewports x 14 routes = 42 PNGs, plus per-route diagnostics.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://sfa.nimrod.bio"
OUT_DIR = Path("/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/visual_diff")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("mobile", 390, 844),
    ("tablet", 768, 1024),
    ("desktop", 1280, 900),
]

ROUTES = [
    ("home",            "/"),
    ("about",           "/about"),
    ("search",          "/search?q=tomato"),
    ("calc",            "/calc"),
    ("crop-book",       "/crop-book/"),
    ("book-questions",  "/crop-book/questions"),
    ("book-family",     "/crop-book/family"),
    ("book-table",      "/crop-book/table"),
    ("book-search",     "/crop-book/search?q=tomato"),
    ("book-crop",       "/crop-book/anise-hyssop"),
    ("book-variety",    "/crop-book/anise-hyssop/variety/variety-1"),
    ("market",          "/market/"),
    ("market-product",  "/market/prd017"),
    ("community",       "/community"),
]


def capture_one(context, vp_name, route_name, route_path):
    """Capture a single screenshot + diagnostics. Returns dict result."""
    page = context.new_page()
    console_errs = []
    http_status = None

    page.on("console", lambda msg: console_errs.append(f"[{msg.type}] {msg.text}")
            if msg.type in ("error", "warning") else None)

    def on_response(resp):
        nonlocal http_status
        if resp.url.rstrip("/") == (BASE + route_path).rstrip("/") or \
           resp.url.split("?")[0].rstrip("/") == (BASE + route_path.split("?")[0]).rstrip("/"):
            if http_status is None:
                http_status = resp.status

    page.on("response", on_response)

    err = None
    try:
        resp = page.goto(BASE + route_path, wait_until="networkidle", timeout=20000)
        if resp is not None and http_status is None:
            http_status = resp.status
    except Exception as e:
        err = str(e)
        # Fallback: try domcontentloaded
        try:
            resp = page.goto(BASE + route_path, wait_until="domcontentloaded", timeout=15000)
            if resp is not None and http_status is None:
                http_status = resp.status
            err = f"networkidle-timeout, fell back to domcontentloaded: {err}"
        except Exception as e2:
            err = f"{err} | dom-fallback also failed: {e2}"

    # tiny settle for fonts/lazy images
    try:
        page.wait_for_timeout(700)
    except Exception:
        pass

    # Diagnostics
    title = None
    gj_visible = None
    dt_visible = None
    gj_count = 0
    dt_count = 0
    horiz_overflow = None
    body_w = None
    body_h = None
    try:
        title = page.title()
    except Exception:
        pass
    try:
        gj_count = page.locator(".gj-shell").count()
        dt_count = page.locator(".dt-shell").count()
        if gj_count > 0:
            gj_visible = page.locator(".gj-shell").first.is_visible()
        if dt_count > 0:
            dt_visible = page.locator(".dt-shell").first.is_visible()
    except Exception:
        pass
    try:
        horiz_overflow = page.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        dims = page.evaluate(
            "() => ({w: document.body.scrollWidth, h: document.body.scrollHeight})"
        )
        body_w = dims.get("w")
        body_h = dims.get("h")
    except Exception:
        pass

    out_path = OUT_DIR / f"{vp_name}__{route_name}.png"
    try:
        page.screenshot(path=str(out_path), full_page=True)
        size = out_path.stat().st_size if out_path.exists() else 0
    except Exception as e:
        err = (err or "") + f" | screenshot-fail: {e}"
        size = 0

    page.close()

    return {
        "viewport": vp_name,
        "route": route_name,
        "path": route_path,
        "http_status": http_status,
        "title": title,
        "gj_shell_count": gj_count,
        "dt_shell_count": dt_count,
        "gj_visible": gj_visible,
        "dt_visible": dt_visible,
        "horiz_overflow_px": horiz_overflow,
        "body_w": body_w,
        "body_h": body_h,
        "file": out_path.name,
        "file_size_bytes": size,
        "console_errs": console_errs,
        "error": err,
    }


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for vp_name, w, h in VIEWPORTS:
            print(f"\n=== Viewport: {vp_name} {w}x{h} ===", flush=True)
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=1,
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
                ) if vp_name == "mobile" else None,
                is_mobile=(vp_name == "mobile"),
                has_touch=(vp_name in ("mobile", "tablet")),
            )
            for route_name, route_path in ROUTES:
                t0 = time.time()
                r = capture_one(ctx, vp_name, route_name, route_path)
                dt = time.time() - t0
                r["duration_s"] = round(dt, 2)
                results.append(r)
                status_str = r["http_status"] if r["http_status"] is not None else "?"
                err_str = " ERR=" + r["error"][:80] if r["error"] else ""
                print(
                    f"  [{status_str}] {route_name:<16} {r['file']:<40} "
                    f"size={r['file_size_bytes']:>8}B  gj={r['gj_visible']} dt={r['dt_visible']} "
                    f"hOverflow={r['horiz_overflow_px']}  t={dt:.1f}s{err_str}",
                    flush=True,
                )
            ctx.close()
        browser.close()

    with open(OUT_DIR / "results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"\nWrote {len(results)} results to {OUT_DIR / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
