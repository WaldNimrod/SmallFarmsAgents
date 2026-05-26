#!/usr/bin/env python3
"""One-time download of WP-C4 web sources to data/external_sources/web/<source>/.

Usage:
    python3 scripts/download_web_sources.py --source all
    python3 scripts/download_web_sources.py --source uc_anr_germination
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "data" / "external_sources" / "web"

SOURCES: dict[str, str] = {
    "uc_anr_germination": "https://ucanr.edu/sites/default/files/2017-11/164220.pdf",
    "purdue_germination": (
        "https://ag.purdue.edu/department/hla/extension/extension-publications-library/"
        "ext-pubs/ho-186-w.html"
    ),
    "osu_frost_tolerance": (
        "https://extension.oregonstate.edu/news/"
        "plant-cold-hardy-vegetables-now-spring-harvest"
    ),
    "csu_planting_guide": (
        "https://extension.colostate.edu/resource/vegetable-planting-guide/"
    ),
    "umn_field_planning": (
        "https://extension.umn.edu/vegetable-growing-guides-farmers/"
        "crop-and-field-planning-tools-vegetable-farmers"
    ),
    "umd_soil_ph": (
        "https://extension.umd.edu/sites/extension.umd.edu/files/2021-03/B-1.pdf"
    ),
    "ne_veg_guide_nutrients": (
        "https://nevegetable.org/cultural-practices/removal-nutrients-soil"
    ),
    "fao_fertilizer_use": (
        "https://www.fao.org/3/i0058e/i0058e.pdf"
    ),
    "il_moa_garden_guide": (
        "https://www.moag.gov.il/vic/tochniyot/DocLib/gan.pdf"
    ),
    "shaham_extension": "https://www.moag.gov.il/vic/shaham/Pages/default.aspx",
    "vital_seeds_count": "https://www.vitalseeds.co.uk/seeds-per-gram/",
    "osborne_seed_count": "https://www.johnnyseeds.com/growers-library/seed-planting-schedule.html",
    "uf_ifas_companion": (
        "https://edis.ifas.ufl.edu/publication/HS389"
    ),
    "uc_davis_postharvest": (
        "https://extension.k-state.edu/foodsafety/produce/resources/docs/"
        "storage-guidelines-UCDavis.pdf"
    ),
}

USER_AGENT = "SmallFarmsAgents-WP-C4/1.0 (educational crop-book ingestion)"


def _ext_from_url(url: str, content_type: str | None) -> str:
    path = urlparse(url).path.lower()
    if path.endswith(".pdf"):
        return ".pdf"
    if path.endswith(".html") or path.endswith(".htm"):
        return ".html"
    if content_type:
        if "pdf" in content_type:
            return ".pdf"
        if "html" in content_type:
            return ".html"
    return ".bin"


def download_one(client: httpx.Client, key: str, url: str) -> dict[str, Any]:
    out_dir = WEB_ROOT / key
    out_dir.mkdir(parents=True, exist_ok=True)
    meta: dict[str, Any] = {"source": key, "url": url, "ok": False, "path": None, "status": None}
    try:
        resp = client.get(url, follow_redirects=True)
        meta["status"] = resp.status_code
        if resp.status_code != 200:
            return meta
        ext = _ext_from_url(url, resp.headers.get("content-type"))
        fname = f"source{ext}"
        dest = out_dir / fname
        dest.write_bytes(resp.content)
        meta["ok"] = True
        meta["path"] = str(dest.relative_to(ROOT))
        meta_path = out_dir / "download_meta.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except httpx.HTTPError as exc:
        meta["error"] = str(exc)
    return meta


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Download WP-C4 web sources")
    parser.add_argument(
        "--source",
        required=True,
        help="Source key or 'all'",
    )
    args = parser.parse_args()
    keys = list(SOURCES.keys()) if args.source == "all" else [args.source]
    if args.source != "all" and args.source not in SOURCES:
        parser.error(f"Unknown source: {args.source}")
    results: list[dict[str, Any]] = []
    with httpx.Client(timeout=60.0, headers={"User-Agent": USER_AGENT}) as client:
        for key in keys:
            logging.info("Downloading %s ...", key)
            results.append(download_one(client, key, SOURCES[key]))
    ok = sum(1 for r in results if r.get("ok"))
    audit_path = ROOT / "_COMMUNICATION" / "team_10" / "SFA-S003-P002-WP-C4"
    audit_path.mkdir(parents=True, exist_ok=True)
    summary = {"total": len(results), "ok": ok, "results": results}
    (audit_path / "download_run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8",
    )
    logging.info("Downloaded %d / %d sources", ok, len(results))
    return 0 if ok >= 10 or args.source != "all" else 1


if __name__ == "__main__":
    sys.exit(main())
