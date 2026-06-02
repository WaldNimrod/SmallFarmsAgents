#!/usr/bin/env python3
"""Vendor IconPark Outline SVGs into organic_market_agent/publisher/static/icons/iconpark.

Fetches from api.iconify.design (Iconify) with User-Agent. Bakes stroke color #1b4332.

Run from repo root after adding new slugs to the lists below:
  python3 scripts/fetch_iconpark_outline_icons.py

License: IconPark icons — Apache-2.0 (https://iconpark.oceanengine.com/official).
"""
from __future__ import annotations

import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "organic_market_agent" / "publisher" / "static" / "icons" / "iconpark"
PREFIX = "icon-park-outline"
COLOR = "1b4332"  # --sfa-green-dark
UA = "OrganicMarketAgent/1.0 (local icon vendor; contact: repo maintainer)"

# Slugs required by product_icons.PRODUCT_CODE_TO_SLUG and FILTER_ICONS (unique).
_REQUIRED = sorted(
    {
        "tomato",
        "cherry",
        "radish",
        "peas",
        "vegetables",
        "eggplant",
        "pumpkin",
        "chili",
        "leaf",
        "carrot",
        "radish-one",
        "garlic",
        "scallion",
        "pear",
        "vicia-faba",
        "bowl-one",
        "vegetable-basket",
        "tray",
        "view-grid-list",
        "seedling",
        "shop",
        "shopping-mall",
    }
)

# Likely future catalog / adjacent organic retail (same stroke family).
_EXTENDED = sorted(
    {
        "apple-one",
        "avocado",
        "avocado-one",
        "banana",
        "bread",
        "bread-one",
        "cake-one",
        "canned-fruit",
        "cheese",
        "coffee",
        "cola",
        "crab",
        "croissant",
        "doughnut",
        "drumstick",
        "egg",
        "egg-one",
        "fish",
        "fork-spoon",
        "french-fries",
        "goblet",
        "goblet-one",
        "hamburger",
        "hamburger-one",
        "honey",
        "honey-one",
        "hot-pot",
        "hot-pot-one",
        "icecream-one",
        "juice",
        "kitchen-knife",
        "kettle-one",
        "lemon",
        "liqueur",
        "macadamia-nut",
        "measuring-cup",
        "milk",
        "milk-one",
        "noodles",
        "nut",
        "orange",
        "orange-one",
        "oven",
        "oven-tray",
        "painted-eggshell",
        "peach",
        "pineapple",
        "popcorn",
        "popcorn-one",
        "pot",
        "refrigerator",
        "rice",
        "sandwich",
        "sandwich-one",
        "shrimp",
        "snacks",
        "soybean-milk-maker",
        "spoon",
        "tea",
        "tea-drink",
        "thermos-cup",
        "turkey",
        "watermelon",
        "watermelon-one",
        "chicken-leg",
        "chicken",
        "lollipop",
        "candy",
        "beer",
        "beer-mug",
        "bottle-one",
        "bowl",
        "chopping-board",
        "cook",
        "chef-hat-one",
        "tree",
        "green-house",
    }
)


def fetch_svg(slug: str) -> bytes:
    url = f"https://api.iconify.design/{PREFIX}/{slug}.svg?color=%23{COLOR}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    all_slugs = sorted(set(_REQUIRED) | set(_EXTENDED))
    DEST.mkdir(parents=True, exist_ok=True)
    ok, missing = 0, []
    for slug in all_slugs:
        path = DEST / f"{slug}.svg"
        try:
            body = fetch_svg(slug)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                missing.append(slug)
                continue
            print(f"FAIL {slug}: HTTP {e.code}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"FAIL {slug}: {exc}", file=sys.stderr)
            return 2
        if b"<svg" not in body:
            missing.append(slug)
            continue
        path.write_bytes(body)
        ok += 1
    print(f"Wrote {ok} SVGs to {DEST}")
    if missing:
        print(f"Skipped (not in set): {', '.join(missing)}")
    # Ensure required all present
    req_missing = [s for s in _REQUIRED if not (DEST / f"{s}.svg").exists()]
    if req_missing:
        print(f"ERROR: required slugs missing: {req_missing}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
