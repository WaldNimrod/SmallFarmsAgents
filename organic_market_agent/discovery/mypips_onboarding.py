"""
Helpers to build MyPIPS store onboarding workbooks from verified discovery CSVs.

Canonical product categories for ``primary_catalog_alignment`` match ``products.category``:
root_vegetables, fruiting_vegetables, leafy_greens, brassicas, alliums, cucurbits,
legumes_fresh, baskets, fruits, eggs.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

BASE_HOST = "mypips.app"

# Hebrew hints in page title → likely sells fresh produce (not authoritative).
_PRODUCE_TITLE_HINTS = (
    "ירק",
    "פירות",
    "משק",
    "חקלא",
    "חווה",
    "גינה",
    "אורגני",
    "סל ",
    "סלט",
    "פרי",
)


def mypips_store_slug_from_url(url: str) -> str | None:
    """
    Return first path segment for https://mypips.app/<slug>/...
    ``None`` for /groups/*, empty path, or non-mypips hosts.
    """
    p = urlparse(url.strip())
    host = (p.netloc or "").lower()
    if host != BASE_HOST:
        return None
    parts = [x for x in p.path.split("/") if x]
    if not parts:
        return None
    if parts[0].lower() == "groups":
        return None
    return parts[0].lower()


def store_base_url(slug: str) -> str:
    return f"https://{BASE_HOST}/{slug}"


def products_entry_url(slug: str) -> str:
    return f"https://{BASE_HOST}/{slug}/products"


def display_name_from_page_title(page_title: str) -> str:
    """
    MyPIPS titles often look like:
    ``עמוד הבית | Store Name | להזמנות | ...`` or
    ``סל קניות ... | Store Name | ...``.
    """
    t = (page_title or "").strip()
    if not t:
        return ""
    parts = [x.strip() for x in t.split("|")]
    if len(parts) >= 2:
        return parts[1]
    return parts[0]


def suggest_produce_from_title(page_title: str) -> str:
    """Return yes / maybe / no for workbook guidance only."""
    t = page_title or ""
    hits = sum(1 for h in _PRODUCE_TITLE_HINTS if h in t)
    if hits >= 2:
        return "yes"
    if hits == 1:
        return "maybe"
    return "no"


def load_verified_rows(suspected_csv: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with suspected_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active = (row.get("storefront_likely_active") or "").strip().lower()
            if active not in ("true", "1", "yes"):
                continue
            rows.append(row)
    return rows


def consolidate_by_slug(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    """
    One row per store slug; prefer the row whose URL is the store base
    (single path segment) and largest body_len.
    """
    by_slug: dict[str, dict[str, Any]] = {}
    for row in rows:
        url = row.get("url", "").strip()
        slug = mypips_store_slug_from_url(url)
        if not slug:
            continue
        try:
            blen = int(row.get("body_len") or 0)
        except ValueError:
            blen = 0
        p = urlparse(url)
        segs = len([x for x in p.path.split("/") if x])
        is_base = segs == 1
        title = row.get("page_title", "")

        cur = by_slug.get(slug)
        if cur is None:
            by_slug[slug] = {
                "slug": slug,
                "url": url,
                "page_title": title,
                "body_len": blen,
                "is_base": is_base,
                "evidence_source": row.get("evidence_source", ""),
                "source_batch": row.get("source_batch", ""),
            }
            continue
        if is_base and not cur["is_base"]:
            by_slug[slug] = {
                "slug": slug,
                "url": url,
                "page_title": title,
                "body_len": blen,
                "is_base": True,
                "evidence_source": row.get("evidence_source", ""),
                "source_batch": row.get("source_batch", ""),
            }
        elif is_base == cur["is_base"] and blen > cur["body_len"]:
            cur["url"] = url
            cur["page_title"] = title
            cur["body_len"] = blen
    return by_slug


def workbook_fieldnames() -> list[str]:
    return [
        "slug",
        "store_url",
        "products_url",
        "display_name",
        "description",
        "business_focus",
        "primary_catalog_alignment",
        "offers_organic_vegetables",
        "suggested_produce_from_title",
        "include_in_ingestion",
        "notes",
        "evidence_source",
        "source_batch",
    ]


def build_workbook_rows(suspected_csv: Path) -> list[dict[str, str]]:
    raw = load_verified_rows(suspected_csv)
    consolidated = consolidate_by_slug(raw)
    out: list[dict[str, str]] = []
    for slug in sorted(consolidated.keys()):
        rec = consolidated[slug]
        title = rec["page_title"]
        disp = display_name_from_page_title(title)
        suggest = suggest_produce_from_title(title)
        out.append(
            {
                "slug": slug,
                "store_url": store_base_url(slug),
                "products_url": products_entry_url(slug),
                "display_name": disp[:200] if disp else slug,
                "description": "",
                "business_focus": "",
                "primary_catalog_alignment": "",
                "offers_organic_vegetables": "",
                "suggested_produce_from_title": suggest,
                "include_in_ingestion": "false",
                "notes": "",
                "evidence_source": rec.get("evidence_source", ""),
                "source_batch": rec.get("source_batch", ""),
            }
        )
    return out
