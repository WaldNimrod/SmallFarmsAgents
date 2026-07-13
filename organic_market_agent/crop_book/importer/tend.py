"""Tend CSV parser — reads CROP_PLAN and PRODUCT_SOLD CSVs.

Column mapping follows LOD400 §2.8. All field names returned are English DB column names.
Source tag format: 'Tend_{year}' (e.g. 'Tend_2022') or 'Tend' for flat export.
"""

from __future__ import annotations

import csv
import logging
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.constants import (
    CATEGORY_MAP,
    GROWTH_CYCLE_MAP,
    HARVEST_STAGE_MAP,
    HARVEST_UNIT_MAP,
    PLANTING_METHOD_MAP,
    TEND_CROP_EN_CANON,
    TEND_CROP_MAP,
    TEND_FAMILY_MAP,
)

logger = logging.getLogger(__name__)

_SHEKEL_RE = re.compile(r"[₪,\s]")


def _parse_decimal(raw: str | None) -> Decimal | None:
    if not raw:
        return None
    cleaned = _SHEKEL_RE.sub("", raw).strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_int(raw: str | None) -> int | None:
    d = _parse_decimal(raw)
    if d is None:
        return None
    try:
        return int(d)
    except (ValueError, ArithmeticError):
        return None


def parse_crop_plan(path: Path, year: str | None = None) -> list[dict[str, Any]]:
    """Parse a Tend CROP_PLAN CSV and return a list of row dicts.

    Each dict uses English DB column names as keys. Crops not found in
    TEND_CROP_MAP are skipped with a WARN log.
    """
    source_tag = f"Tend_{year}" if year else "Tend"
    rows: list[dict[str, Any]] = []

    try:
        fh = path.open(encoding="utf-8-sig")
    except OSError:
        logger.warning("CROP_PLAN file not found: %s", path)
        return rows

    with fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            crop_en = (raw.get("Crop") or "").strip()
            if not crop_en:
                continue

            name_he = TEND_CROP_MAP.get(crop_en)
            if name_he is None:
                logger.warning("TEND_CROP_MAP: unknown crop %r, skipping row", crop_en)
                continue

            family_tend = (raw.get("Family Name") or "").strip()
            scientific_name = TEND_FAMILY_MAP.get(family_tend)
            if not scientific_name and family_tend:
                logger.warning("TEND_FAMILY_MAP: unknown family %r for crop %r", family_tend, crop_en)

            category_raw = (raw.get("Category") or "").strip()
            category = CATEGORY_MAP.get(category_raw)
            if not category and category_raw:
                logger.warning("CATEGORY_MAP: unknown category %r for crop %r", category_raw, crop_en)

            harvest_unit_raw = (raw.get("Harvest Unit") or "").strip()
            harvest_unit = HARVEST_UNIT_MAP.get(harvest_unit_raw)

            growth_cycle_raw = (raw.get("Growing Cycle") or "").strip()
            growth_cycle = GROWTH_CYCLE_MAP.get(growth_cycle_raw)

            planting_raw = (raw.get("Planting Method") or "").strip()
            planting_method = PLANTING_METHOD_MAP.get(planting_raw)

            harvest_stage_raw = (raw.get("Harvest Stage") or "").strip()
            harvest_stage = HARVEST_STAGE_MAP.get(harvest_stage_raw)

            rootstock_raw = (raw.get("Rootstock") or "").strip()
            is_grafted = bool(rootstock_raw)

            in_row_raw = (raw.get("In-Row Spacing") or "").strip()
            in_row_unit = (raw.get("In-Row Spacing Unit") or "cm").strip().lower()
            in_row_val = _parse_decimal(in_row_raw)
            if in_row_val is not None and "inch" in in_row_unit:
                in_row_val = in_row_val * Decimal("2.54")

            row: dict[str, Any] = {
                "name_he": name_he,
                # Canonical DB name_en: pinned where the raw Tend name would slugify
                # away from the production (SSoT) slug (e.g. "Soybeans"→"Soybean").
                "name_en": TEND_CROP_EN_CANON.get(crop_en, crop_en),
                "scientific_name": scientific_name,
                "family_scientific_name": scientific_name,
                "category": category,
                "growth_cycle": growth_cycle,
                "harvest_unit": harvest_unit,
                "harvest_stage": harvest_stage,
                "planting_method": planting_method,
                "is_grafted": is_grafted,
                "rootstock_variety": rootstock_raw or None,
                "variety_name_en": (raw.get("Variety") or "").strip() or None,
                "days_to_maturity": _parse_int(raw.get("DTM")),
                "harvest_window_max_days": _parse_int(raw.get("Harvest Window")),
                "in_row_spacing_cm": in_row_val,
                "rows_per_bed": _parse_int(raw.get("Rows Per Bed")),
                "avg_yield_per_bed_m": _parse_decimal(raw.get("Avg Yield Rate")),
                "documented_price": _parse_decimal(raw.get("Avg. Sales Price")),
                "days_in_gh_total": _parse_int(raw.get("Days In Greenhouse")),
                "seeder": (raw.get("Seeder") or "").strip() or None,
                "seeder_front_gear": (raw.get("Front gear") or "").strip() or None,
                "seeder_rear_gear": (raw.get("Rear gear") or "").strip() or None,
                "seeder_roller_plate": (raw.get("Roller plate") or "").strip() or None,
                "first_fruit_year": _parse_int(raw.get("First Fruiting Year")),
                "source": source_tag,
            }
            rows.append(row)

    logger.info("Parsed %d rows from %s (source=%s)", len(rows), path, source_tag)
    return rows


def parse_product_sold(path: Path, year: str) -> dict[str, Decimal]:
    """Parse PRODUCT_SOLD CSV; return {product_name_he: net_price_per_unit}.

    Price computed as net_sales / total_qty_sold (both non-zero).
    """
    prices: dict[str, Decimal] = {}
    try:
        fh = path.open(encoding="utf-8-sig")
    except OSError:
        logger.warning("PRODUCT_SOLD file not found: %s", path)
        return prices

    with fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            name = (raw.get("Product Name") or "").strip()
            qty = _parse_decimal(raw.get("Total Qty Sold"))
            net = _parse_decimal(raw.get("Net Sales"))
            if not name or not qty or not net or qty == 0:
                continue
            price = net / qty
            prices[name] = price

    logger.info("Parsed %d product prices from %s (year=%s)", len(prices), path, year)
    return prices


def discover_tend_years(base_dir: Path) -> list[tuple[str, Path]]:
    """Return [(year, crop_plan_path)] for all discovered Tend year folders.

    Also includes the flat CROP_PLAN at base_dir itself (year='flat').
    """
    results: list[tuple[str, Path]] = []

    if not base_dir.exists():
        logger.warning("WARN: Tend source_dir not found, skipping: %s", base_dir)
        return results

    flat = base_dir / "CROP_PLAN (from macBook Air - nimrod).CSV"
    if flat.exists():
        results.append(("flat", flat))

    for child in sorted(base_dir.iterdir()):
        if child.is_dir() and child.name.startswith("Tend_"):
            year = child.name.replace("Tend_", "")
            plan = child / "CROP_PLAN (from macBook Air - nimrod).CSV"
            if plan.exists():
                results.append((year, plan))
            else:
                logger.warning("WARN: year %s folder found but CROP_PLAN missing: %s", year, child)

    return results
