"""Enrichment publisher — SFA-S003-P002-WP-A LOD400 §17 Step 9.

Reads crop_field_enrichment rows from the DB and writes a single JSON file:
    output/sfagent-crop-book-enrichment.json

**WP-A scope: JSON file generation ONLY.**
No WordPress upload in WP-A (dispatch_upload is NOT called here).
Upload is deferred to WP-B after Flask UI and publisher profile are spec'd.
See LOD400 §14 (F-01 resolution) and §19 LOD500_LOCKED inventory.

JSON schema:
    {
      "generated_at": "<ISO-8601 UTC>",
      "variety_count": <int>,
      "fields": [
        {
          "variety_id": <int>,
          "crop_name_he": <str>,
          "crop_name_en": <str | null>,
          "variety_name_en": <str | null>,
          "field_name": <str>,
          "value_best": <str | null>,          -- Decimal serialised as string
          "value_min": <str | null>,
          "value_max": <str | null>,
          "confidence_score": <str | null>,
          "source_count": <int>,
          "winning_source_class": <str | null>,
          "computed_at": "<ISO-8601 UTC>"
        },
        ...
      ]
    }
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
from organic_market_agent.crop_book.models import Crop, CropVariety

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_PATH = Path("output/sfagent-crop-book-enrichment.json")


def _decimal_default(obj: Any) -> Any:
    """JSON encoder fallback for Decimal and datetime."""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialisable")


def publish_enrichment(
    session: Session,
    output_path: Optional[Path] = None,
) -> Path:
    """Generate the enrichment JSON file from crop_field_enrichment rows.

    Args:
        session:      Active SQLAlchemy session (read-only queries).
        output_path:  Target file path; defaults to output/sfagent-crop-book-enrichment.json.

    Returns:
        Resolved path of the written JSON file.

    Raises:
        OSError: If the output directory cannot be created or file cannot be written.

    Note:
        This function does NOT call dispatch_upload() — WP-A scope is local file only.
    """
    if output_path is None:
        output_path = _DEFAULT_OUTPUT_PATH

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load all enrichment rows with variety + crop info
    rows = (
        session.query(CropFieldEnrichment, CropVariety, Crop)
        .join(CropVariety, CropFieldEnrichment.variety_id == CropVariety.id)
        .join(Crop, CropVariety.crop_id == Crop.id)
        .order_by(Crop.name_he, CropVariety.name_en, CropFieldEnrichment.field_name)
        .all()
    )

    variety_ids: set[int] = set()
    fields_list: list[dict[str, Any]] = []

    for enrichment, variety, crop in rows:
        variety_ids.add(variety.id)
        fields_list.append({
            "variety_id": variety.id,
            "crop_name_he": crop.name_he,
            "crop_name_en": crop.name_en,
            "variety_name_en": variety.name_en,
            "field_name": enrichment.field_name,
            "value_best": str(enrichment.value_best) if enrichment.value_best is not None else None,
            "value_min": str(enrichment.value_min) if enrichment.value_min is not None else None,
            "value_max": str(enrichment.value_max) if enrichment.value_max is not None else None,
            "confidence_score": (
                str(enrichment.confidence_score) if enrichment.confidence_score is not None else None
            ),
            "source_count": enrichment.source_count,
            "winning_source_class": enrichment.winning_source_class,
            "computed_at": enrichment.computed_at.isoformat() if enrichment.computed_at else None,
        })

    from datetime import datetime, timezone
    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "variety_count": len(variety_ids),
        "fields": fields_list,
    }

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=_decimal_default)

    logger.info(
        "Enrichment JSON written: %s (%d fields, %d varieties)",
        output_path, len(fields_list), len(variety_ids),
    )
    return output_path.resolve()
