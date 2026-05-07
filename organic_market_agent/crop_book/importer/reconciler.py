"""Multi-source merge logic for crop_varieties unified fields.

Priority order per LOD400 §2.7:
  days_to_maturity: team_00 > JMF > Tend (with outlier rejection)
  avg_yield_per_bed_m: Tend multi-year mean > JMF
  documented_price: most recent Tend PRODUCT_SOLD
  in_row_spacing_cm / rows_per_bed: JMF > Tend
  equipment fields: JMF only
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from organic_market_agent.crop_book.constants import OUTLIER_CROPS, TEAM00_DTM_OVERRIDES

logger = logging.getLogger(__name__)

_OUTLIER_DTM_THRESHOLD = 20


def reconcile_dtm(
    name_he: str,
    tend_values: list[int | None],
    jmf_value: int | None,
) -> tuple[int | None, list[dict[str, Any]]]:
    """Return (unified_dtm, source_value_rows_to_store).

    Source value rows are dicts ready for CropVarietySourceValue insertion:
    {field_name, source, value_text, value_numeric, unit, note}
    """
    rows: list[dict[str, Any]] = []

    team00 = TEAM00_DTM_OVERRIDES.get(name_he)
    if team00 is not None:
        rows.append(
            {
                "field_name": "days_to_maturity",
                "source": "team_00",
                "value_text": str(team00),
                "value_numeric": Decimal(team00),
                "unit": "days",
                "note": "team_00 Israel-specific override — highest priority",
            }
        )

    if jmf_value is not None:
        rows.append(
            {
                "field_name": "days_to_maturity",
                "source": "JMF",
                "value_text": str(jmf_value),
                "value_numeric": Decimal(jmf_value),
                "unit": "days",
                "note": None,
            }
        )

    for tend_dtm in tend_values:
        if tend_dtm is None:
            continue
        is_outlier = (
            name_he in OUTLIER_CROPS and tend_dtm < _OUTLIER_DTM_THRESHOLD
        )
        note = "OUTLIER_REJECTED — near-harvest snapshot, below threshold" if is_outlier else None
        if is_outlier:
            logger.warning(
                "DTM outlier rejected: crop=%r tend_dtm=%d (< %d for leaf crop)",
                name_he,
                tend_dtm,
                _OUTLIER_DTM_THRESHOLD,
            )
        rows.append(
            {
                "field_name": "days_to_maturity",
                "source": "Tend",
                "value_text": str(tend_dtm),
                "value_numeric": Decimal(tend_dtm),
                "unit": "days",
                "note": note,
            }
        )

    if team00 is not None:
        return team00, rows
    if jmf_value is not None:
        return jmf_value, rows
    valid_tend = [
        v
        for v in tend_values
        if v is not None
        and not (name_he in OUTLIER_CROPS and v < _OUTLIER_DTM_THRESHOLD)
    ]
    if valid_tend:
        return valid_tend[-1], rows
    return None, rows


def reconcile_variety(source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge per-source rows into a unified crop_varieties field dict.

    Returns a partial dict suitable for setting unified fields on CropVariety.
    Only fields with a winning value are included.
    """
    unified: dict[str, Any] = {}

    def _best(field: str, prefer_sources: list[str]) -> Any:
        for src in prefer_sources:
            for row in source_rows:
                if row.get("field_name") == field and row.get("source") == src:
                    return row.get("value_numeric") or row.get("value_text")
        return None

    yield_tend_rows = [
        r
        for r in source_rows
        if r.get("field_name") == "avg_yield_per_bed_m"
        and r.get("source", "").startswith("Tend")
        and r.get("value_numeric") is not None
    ]
    if yield_tend_rows:
        vals = [r["value_numeric"] for r in yield_tend_rows]
        unified["avg_yield_per_bed_m"] = sum(vals) / len(vals)
        unified["yield_source"] = "Tend"
    else:
        jmf_yield = _best("avg_yield_per_bed_m", ["JMF"])
        if jmf_yield is not None:
            unified["avg_yield_per_bed_m"] = jmf_yield
            unified["yield_source"] = "JMF"

    for field, sources in [
        ("in_row_spacing_cm", ["JMF", "Tend"]),
        ("rows_per_bed", ["JMF", "Tend"]),
        ("planting_season", ["JMF", "Tend"]),
        ("seeder", ["JMF"]),
        ("seeder_front_gear", ["JMF"]),
        ("seeder_rear_gear", ["JMF"]),
        ("seeder_roller_plate", ["JMF"]),
    ]:
        val = _best(field, sources)
        if val is not None:
            unified[field] = val

    price_tend_rows = sorted(
        [
            r
            for r in source_rows
            if r.get("field_name") == "documented_price"
            and r.get("source", "").startswith("Tend")
        ],
        key=lambda r: r.get("source", ""),
        reverse=True,
    )
    if price_tend_rows:
        best = price_tend_rows[0]
        unified["documented_price"] = best.get("value_numeric")
        unified["documented_price_source"] = best.get("source")
        if best.get("unit"):
            unified["documented_price_unit"] = best["unit"]

    rootstock = _best("rootstock_variety", ["team_00", "Tend"])
    if rootstock:
        unified["rootstock_variety"] = rootstock
        unified["is_grafted"] = True

    return unified
