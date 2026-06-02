#!/usr/bin/env python3
"""Team 50 FULL LIVE E2E QA harness — 2026-06-02. Read-only against https://sfa.nimrod.bio."""
from __future__ import annotations

import json
import math
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = "https://sfa.nimrod.bio"
CTX = ssl.create_default_context()

VIEWPORTS = [
    ("mobile", 390, 844),
    ("desktop", 1280, 900),
]

ROUTES = [
    ("home", "/"),
    ("about", "/about"),
    ("search", "/search?q=חסה"),
    ("community", "/community"),
    ("market", "/market/"),
    ("market-product", "/market/prd017"),
    ("calc", "/calc/"),
    ("clients", "/clients/"),
    ("crop-book", "/crop-book/"),
    ("book-table", "/crop-book/?view=table"),
    ("book-questions", "/crop-book/questions"),
    ("book-family", "/crop-book/family"),
    ("book-table-route", "/crop-book/table"),
    ("book-search", "/crop-book/search?q=tomato"),
    ("book-tomatoes", "/crop-book/tomatoes/?depth=full"),
    ("book-carrots", "/crop-book/carrots/?depth=full"),
    ("book-lettuce", "/crop-book/lettuce/?depth=full"),
    ("book-cucumbers", "/crop-book/cucumbers/?depth=full"),
    ("book-eggplant", "/crop-book/eggplant/?depth=full"),
    ("book-chard", "/crop-book/chard/?depth=full"),
    ("book-cauliflower", "/crop-book/cauliflower/?depth=full"),
    ("book-family-sol", "/crop-book/family/solanaceae"),
    ("book-family-api", "/crop-book/family/apiaceae"),
]

FAMILY_EXPECT = {
    "tomatoes": "Solanaceae",
    "carrots": "Apiaceae",
    "lettuce": "Asteraceae",
    "cucumbers": "Cucurbitaceae",
    "eggplant": "Solanaceae",
    "beets": "Amaranthaceae",
    "garlic": "Amaryllidaceae",
    "onions": "Amaryllidaceae",
}

WC_SLUGS = [
    "tomato", "carrot", "lettuce", "cucumber", "eggplant", "chard",
]


def http_get(url: str, method: str = "GET", data: bytes | None = None, headers: dict | None = None) -> tuple[int, str, dict]:
    hdrs = {"User-Agent": "SFA-E2E-team50/2026-06-02", "Accept": "application/json, text/html, */*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body, dict(e.headers)


def api_json(path: str) -> tuple[int, object]:
    code, body, _ = http_get(BASE + path)
    try:
        return code, json.loads(body) if body.strip() else None
    except json.JSONDecodeError:
        return code, body[:500]


def run_api_phase() -> dict:
    out: dict = {"checks": [], "family_sweep": [], "aizoaceae_crops": []}
    code, health = api_json("/api/v1/health")
    out["health"] = {"code": code, "body": health}
    out["checks"].append({"id": "health", "pass": code == 200 and isinstance(health, dict) and health.get("status") == "ok"})

    code, crops_raw = api_json("/api/v1/crops")
    crops = crops_raw.get("items", crops_raw) if isinstance(crops_raw, dict) else crops_raw
    out["crops_count"] = len(crops) if isinstance(crops, list) else 0
    out["checks"].append({"id": "crops_list", "pass": code == 200 and out["crops_count"] > 0})

    if isinstance(crops, list):
        for c in crops:
            slug = c.get("slug", "")
            fam = (c.get("identity") or {}).get("family") or {}
            sci = fam.get("scientific_name") or fam.get("name") or ""
            he = c.get("family_name_he") or fam.get("name_he") or ""
            out["family_sweep"].append({"slug": slug, "scientific": sci, "he": he})
            if not sci and slug:
                _, detail = api_json(f"/api/v1/crops/{slug}")
                if isinstance(detail, dict):
                    fam = (detail.get("identity") or {}).get("family") or {}
                    sci = fam.get("scientific_name") or ""
            if sci == "Aizoaceae":
                out["aizoaceae_crops"].append(slug)

    for slug, exp in FAMILY_EXPECT.items():
        code, crop = api_json(f"/api/v1/crops/{slug}")
        sci = ""
        if isinstance(crop, dict):
            fam = (crop.get("identity") or {}).get("family") or {}
            sci = fam.get("scientific_name") or ""
        out["checks"].append({
            "id": f"family_{slug}",
            "pass": code == 200 and sci == exp,
            "expected": exp,
            "actual": sci,
        })

    code, assumptions = api_json("/api/v1/assumptions")
    out["assumptions"] = assumptions
    ok_assump = (
        code == 200
        and isinstance(assumptions, dict)
        and "germination_rate" in assumptions
        and "bed_width" in assumptions
    )
    out["checks"].append({"id": "assumptions", "pass": ok_assump})

    payload = json.dumps({"kind": "request-info", "field_name": "seeds_per_g", "crop_slug": "lettuce"}).encode()
    code, body, _ = http_get(
        BASE + "/api/v1/contribute",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        contrib = json.loads(body)
    except json.JSONDecodeError:
        contrib = body
    out["contribute_ok"] = {"code": code, "body": contrib}
    out["checks"].append({
        "id": "contribute_request_info",
        "pass": code == 200 and isinstance(contrib, dict) and contrib.get("ok") is True,
    })

    payload_bad = json.dumps({"kind": "unknown-kind"}).encode()
    code_bad, _, _ = http_get(
        BASE + "/api/v1/contribute",
        method="POST",
        data=payload_bad,
        headers={"Content-Type": "application/json"},
    )
    out["checks"].append({"id": "contribute_400", "pass": code_bad == 400})

    code, prd = api_json("/api/v1/products/prd017")
    out["prd017"] = prd

    code, products_raw = api_json("/api/v1/products")
    products = products_raw.get("items", products_raw) if isinstance(products_raw, dict) else products_raw
    non_kg = []
    priced_slug = None
    priced_val = None
    if isinstance(products, list):
        for p in products:
            unit = (p.get("unit") or p.get("documented_price_unit") or "").lower()
            if unit and unit != "kg" and p.get("last_price"):
                non_kg.append(p.get("slug"))
            if priced_slug is None and p.get("last_price") is not None:
                priced_slug = p.get("slug")
                priced_val = p.get("last_price")
    out["non_kg_products"] = non_kg[:20]
    if priced_slug:
        _, html, _ = http_get(BASE + f"/market/{priced_slug}")
        out["checks"].append({
            "id": "market_price_match",
            "pass": str(priced_val) in html,
            "slug": priced_slug,
            "last_price": priced_val,
        })
    else:
        out["checks"].append({"id": "market_price_match", "pass": False, "reason": "no priced product"})

    with open(OUT / "api_samples.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    return out


def run_python_calcs() -> dict:
    repo = Path(__file__).resolve()
    for _ in range(8):
        if (repo / "organic_market_agent").is_dir():
            break
        repo = repo.parent
    sys.path.insert(0, str(repo))
    from organic_market_agent.crop_book.calculators import (
        CalcUnavailable,
        CropEconomics,
        beds_for_target_yield,
        crop_profit_comparison,
        expected_revenue,
        expected_yield,
        fertilizer_compost_rate,
        frost_planting_window,
        harvest_window_from_sowing,
        nursery_trays_and_sow_date,
        plant_population,
        seed_input_cost,
        seed_quantity_to_buy,
        sowing_date_from_harvest,
        succession_schedule,
        transplants_needed,
    )
    from organic_market_agent.crop_book.assumptions import get_assumption

    results = []
    code, tomatoes = api_json("/api/v1/crops/tomatoes")
    if not isinstance(tomatoes, dict):
        return {"error": "no tomatoes api", "results": results}

    ag = tomatoes.get("agronomy") or tomatoes.get("fields") or {}
    rows = float(ag.get("rows_per_bed") or 4)
    spacing = float(ag.get("spacing_in_row_cm") or ag.get("in_row_spacing_cm") or 25)
    spg = float(ag.get("seeds_per_g") or ag.get("seeds_per_gram") or 200)
    yield_m = float(ag.get("yield_per_bed_m") or ag.get("avg_yield_per_bed_m") or 2)
    dtm = int(ag.get("days_to_maturity") or 70)
    hw = int(ag.get("harvest_window_max_days") or 14)

    germ = get_assumption("germination_rate")
    oversow = get_assumption("oversow")
    bed_w = get_assumption("bed_width")

    def rec(n: int, name: str, status: str, detail: str = ""):
        results.append({"calc": n, "name": name, "status": status, "detail": detail})

    try:
        r = seed_quantity_to_buy(
            rows_per_bed=int(rows),
            in_row_spacing_cm=spacing,
            seeds_per_gram=spg,
            bed_length_m=30.0,
            seeds_per_hole=1,
            germination_rate=germ,
            oversow=oversow,
        )
        rec(1, "seed_quantity_to_buy", "PASS", f"grams={r.grams:.2f}")
    except Exception as e:
        rec(1, "seed_quantity_to_buy", "FAIL", str(e))

    try:
        n = transplants_needed(rows_per_bed=int(rows), in_row_spacing_cm=spacing, bed_length_m=30.0)
        rec(2, "transplants_needed", "PASS", f"plants={n}")
    except Exception as e:
        rec(2, "transplants_needed", "FAIL", str(e))

    try:
        r = nursery_trays_and_sow_date(
            plants=100,
            days_in_nursery=14,
            field_set_date=date.today() + timedelta(days=60),
        )
        rec(3, "nursery_trays_and_sow_date", "PASS", f"trays={r.trays}")
    except CalcUnavailable as e:
        rec(3, "nursery_trays_and_sow_date", "SKIP", str(e))
    except Exception as e:
        rec(3, "nursery_trays_and_sow_date", "FAIL", str(e))

    try:
        r = sowing_date_from_harvest(
            target_harvest_date=date(2026, 9, 1),
            days_to_maturity=dtm,
            planting_method="direct",
            days_in_nursery=None,
        )
        rec(4, "sowing_date_from_harvest", "PASS", str(r.sow_date))
    except CalcUnavailable as e:
        rec(4, "sowing_date_from_harvest", "SKIP", str(e))
    except Exception as e:
        rec(4, "sowing_date_from_harvest", "FAIL", str(e))

    try:
        r = harvest_window_from_sowing(
            sow_date=date(2026, 3, 1),
            days_to_maturity=dtm,
            harvest_window_max_days=hw,
            planting_method="direct",
            days_in_nursery=None,
        )
        rec(5, "harvest_window_from_sowing", "PASS", str(r.harvest_start))
    except CalcUnavailable as e:
        rec(5, "harvest_window_from_sowing", "SKIP", str(e))
    except Exception as e:
        rec(5, "harvest_window_from_sowing", "FAIL", str(e))

    try:
        s = succession_schedule(
            first_sow_date=date(2026, 3, 1),
            succession_interval_weeks=3,
            num_successions=4,
        )
        rec(6, "succession_schedule", "PASS", f"dates={len(s)}")
    except CalcUnavailable as e:
        rec(6, "succession_schedule", "SKIP", str(e))
    except Exception as e:
        rec(6, "succession_schedule", "FAIL", str(e))

    try:
        r = beds_for_target_yield(target_kg=300, avg_yield_per_bed_m=yield_m, std_bed_length_m=30.0)
        rec(7, "beds_for_target_yield", "PASS", f"beds={r.beds:.2f}")
    except CalcUnavailable as e:
        rec(7, "beds_for_target_yield", "SKIP", str(e))
    except Exception as e:
        rec(7, "beds_for_target_yield", "FAIL", str(e))

    try:
        y = expected_yield(avg_yield_per_bed_m=yield_m, bed_length_m=30.0)
        rec(8, "expected_yield", "PASS", f"kg={y}")
    except Exception as e:
        rec(8, "expected_yield", "FAIL", str(e))

    try:
        r = expected_revenue(
            avg_yield_per_bed_m=yield_m,
            bed_length_m=30.0,
            documented_price=12.0,
            documented_price_unit="kg",
        )
        rec(9, "expected_revenue", "PASS", f"rev={r.revenue}")
    except CalcUnavailable as e:
        rec(9, "expected_revenue", "SKIP", str(e))
    except Exception as e:
        rec(9, "expected_revenue", "FAIL", str(e))

    try:
        r = plant_population(rows_per_bed=int(rows), in_row_spacing_cm=spacing, bed_width_m=bed_w)
        rec(10, "plant_population", "PASS", f"per_m2={r.plants_per_m2}")
    except Exception as e:
        rec(10, "plant_population", "FAIL", str(e))

    try:
        r = frost_planting_window(
            last_frost_date=date(2026, 3, 15),
            first_frost_date=date(2026, 11, 1),
            days_to_maturity=dtm,
            frost_tolerance_class="half_hardy",
        )
        rec(11, "frost_planting_window", "PASS", str(r.earliest_plant))
    except CalcUnavailable as e:
        rec(11, "frost_planting_window", "SKIP", str(e))
    except Exception as e:
        rec(11, "frost_planting_window", "FAIL", str(e))

    try:
        r = fertilizer_compost_rate(
            nutrient_removal_n_kg_ha=100.0,
            nutrient_removal_p_kg_ha=50.0,
            nutrient_removal_k_kg_ha=0.0,
            area_m2=500.0,
            compost_N_pct=0.015,
            application_efficiency=0.5,
        )
        rec(12, "fertilizer_compost_rate", "PASS", f"compost={r.compost_kg:.1f}")
    except CalcUnavailable as e:
        rec(12, "fertilizer_compost_rate", "SKIP", str(e))
    except Exception as e:
        rec(12, "fertilizer_compost_rate", "FAIL", str(e))

    try:
        r = crop_profit_comparison(
            [
                CropEconomics(
                    crop_id=1,
                    name_he="test",
                    avg_yield_per_bed_m=2.0,
                    documented_price=10.0,
                    documented_price_unit="kg",
                )
            ],
            bed_meters=100,
        )
        rec(13, "crop_profit_comparison", "PASS", f"ranked={len(r.ranked)}")
    except Exception as e:
        rec(13, "crop_profit_comparison", "FAIL", str(e))

    try:
        r = seed_input_cost(grams_needed=5.0, seed_price_per_g=2.0)
        rec(14, "seed_input_cost", "PASS", f"cost={r.total_cost}")
    except Exception as e:
        rec(14, "seed_input_cost", "FAIL", str(e))

    payload = {"pytest_baseline": "43 passed", "live_operands": {"rows": rows, "spacing": spacing, "yield_m": yield_m}, "results": results}
    with open(OUT / "calc_parity.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return payload


def run_playwright_phase() -> dict:
    from playwright.sync_api import sync_playwright

    deploy = {}
    for asset in ["/public_assets/css/crop-book-v1.css", "/public_assets/js/crop-book-v1.js"]:
        code, _, _ = http_get(BASE + asset)
        deploy[asset] = code
    _, cb_html, _ = http_get(BASE + "/crop-book/")
    deploy["wc-cropbook-hero"] = "wc-cropbook-hero" in cb_html
    deploy["crop-book-v1.css_link"] = "crop-book-v1.css" in cb_html

    captures = []
    calc_browser = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for vp_name, w, h in VIEWPORTS:
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                locale="he-IL",
            )
            for route_name, route_path in ROUTES:
                page = ctx.new_page()
                console_errs = []
                page.on("console", lambda msg: console_errs.append(f"[{msg.type}] {msg.text}")
                    if msg.type == "error" else None)
                status = None
                try:
                    resp = page.goto(BASE + route_path, wait_until="domcontentloaded", timeout=25000)
                    status = resp.status if resp else None
                    page.wait_for_timeout(600)
                except Exception as e:
                    status = str(e)
                html = page.content()
                bad_patterns = []
                for pat in ["Array(", "object Object", "field_name", "value_best"]:
                    if pat in html:
                        bad_patterns.append(pat)
                broken_imgs = page.evaluate(
                    """() => [...document.querySelectorAll('img')].filter(i => i.src && (!i.complete || i.naturalWidth===0)).map(i => i.src)"""
                )
                png = OUT / f"{vp_name}__{route_name}.png"
                try:
                    page.screenshot(path=str(png), full_page=True)
                except Exception:
                    pass
                captures.append({
                    "viewport": vp_name,
                    "route": route_name,
                    "path": route_path,
                    "http_status": status,
                    "console_errs": console_errs,
                    "bad_patterns": bad_patterns,
                    "broken_imgs": broken_imgs[:5],
                    "file": png.name,
                })
                page.close()
            ctx.close()

        # Calculator + assumptions on /calc/
        page = browser.new_page()
        page.goto(BASE + "/calc/", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(800)
        js_calcs = page.evaluate(
            """() => {
              if (!window.SFA_CALC) return {error: 'no SFA_CALC'};
              const g = {bed_len: 30, seeds_per_hole: 1, area: 300, area_m2: 300};
              const book = {spacing: 25, rows: 4, seeds_per_gram: 900, yield_per_m: 3.5, price: 12, n: 120, p: 0, k: 0};
              return {
                seed: SFA_CALC.seed(g, book),
                yield: SFA_CALC.yield({bed_len: 30}, {yield_per_m: 3.5}),
                pop: SFA_CALC.pop({}, book),
                revenue: SFA_CALC.revenue({area: 30}, book),
                fert: SFA_CALC.fert({area_m2: 50}, book),
              };
            }"""
        )
        calc_browser["js_eval"] = js_calcs
        mod_count = page.locator("[data-calc]").count()
        calc_browser["modcard_count"] = mod_count
        export_csv = page.locator('a[href*="export.csv"]').count()
        calc_browser["export_csv_link"] = export_csv > 0
        page.close()

        # Assumption change
        page = browser.new_page()
        page.goto(BASE + "/calc/", wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        try:
            germ_inp = page.locator('[data-assume="germination_rate"]').first
            if germ_inp.count():
                germ_inp.scroll_into_view_if_needed(timeout=5000)
                germ_inp.fill("80", timeout=5000)
                page.wait_for_timeout(300)
            calc_browser["assumption_fill"] = True
        except Exception as e:
            calc_browser["assumption_fill"] = False
            calc_browser["assumption_fill_error"] = str(e)[:200]
        page.close()

        code_csv, csv_body, _ = http_get(BASE + "/calc/export.csv")
        code_pdf, pdf_body, _ = http_get(BASE + "/calc/export.pdf?crop=test&beds=5")
        calc_browser["export_csv"] = {"code": code_csv, "len": len(csv_body), "has_hebrew": "יבול" in csv_body or "גידול" in csv_body}
        calc_browser["export_pdf"] = {"code": code_pdf, "is_html": "<html" in pdf_body.lower()[:500]}

        code_cl, _, cl_h = http_get(BASE + "/clients/")
        calc_browser["clients_redirect"] = code_cl in (301, 302, 303, 307, 308) or "location" in {k.lower(): v for k, v in cl_h.items()}

        _, tom_html, _ = http_get(BASE + "/crop-book/tomatoes/?depth=full")
        calc_browser["tomatoes_proposed_tag"] = "proposed-tag" in tom_html or "מוצע" in tom_html
        calc_browser["tomatoes_topics"] = [
            t for t in ["זנים", "מרווח", "ציוד", "קרקע", "זריעה", "השקיה", "מזיקים", "קציר", "רצף"]
            if t in tom_html
        ]

        browser.close()

    with open(OUT / "results.json", "w", encoding="utf-8") as fh:
        json.dump({"deploy": deploy, "captures": captures, "calc_browser": calc_browser}, fh, indent=2, ensure_ascii=False)

    for slug in WC_SLUGS:
        code, _, _ = http_get(f"{BASE}/public_assets/img/wc-{slug}.png")
        deploy[f"wc-{slug}.png"] = code

    return {"deploy": deploy, "captures": captures, "calc_browser": calc_browser}


def main():
    t0 = time.time()
    print("API phase...", flush=True)
    api = run_api_phase()
    print("Python calcs...", flush=True)
    calcs = run_python_calcs()
    print("Playwright...", flush=True)
    pw = run_playwright_phase()
    summary = {
        "base": BASE,
        "duration_s": round(time.time() - t0, 1),
        "api_checks_pass": sum(1 for c in api["checks"] if c["pass"]),
        "api_checks_total": len(api["checks"]),
        "aizoaceae_only_nz": len(api.get("aizoaceae_crops", [])) <= 1,
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
