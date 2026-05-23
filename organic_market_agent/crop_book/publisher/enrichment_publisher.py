"""Enrichment publisher — SFA-S003-P002-WP-A LOD400 §14 / AC-17.

Reads crop_field_enrichment rows from the DB and writes a single JSON file:
    output/sfagent-crop-book-enrichment.json

**WP-A scope: JSON file generation ONLY.**
No WordPress upload in WP-A (dispatch_upload is NOT called here).
Upload is deferred to WP-B after Flask UI and publisher profile are spec'd.
See LOD400 §14 (F-01 resolution) and §19 LOD500_LOCKED inventory.

JSON schema (AC-17 locked):
    {
      "generated_at": "<ISO-8601 UTC>",
      "schema_version": "1.0",
      "enriched_fields": ["days_to_maturity", "avg_yield_per_bed_m", ...],
      "varieties": {
        "<variety_id>": {
          "<field_name>": {
            "best":         <number | null>,
            "min":          <number | null>,
            "max":          <number | null>,
            "confidence":   <number | null>,
            "source_count": <int>,
            "winning_class": <str | null>
          }
        }
      }
    }
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
from organic_market_agent.crop_book.models import Crop, CropVariety

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_PATH = Path("output/sfagent-crop-book-enrichment.json")
_SCHEMA_VERSION = "1.0"


def _to_float(value: Any) -> float | None:
    """Convert Decimal or None to float for JSON serialisation."""
    if value is None:
        return None
    return float(value)


def publish_enrichment(
    session: Session,
    output_path: Optional[Path] = None,
) -> Path:
    """Generate the AC-17 enrichment JSON file from crop_field_enrichment rows.

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

    # Load all enrichment rows ordered for deterministic output
    rows = (
        session.query(CropFieldEnrichment, CropVariety, Crop)
        .join(CropVariety, CropFieldEnrichment.variety_id == CropVariety.id)
        .join(Crop, CropVariety.crop_id == Crop.id)
        .order_by(CropFieldEnrichment.variety_id, CropFieldEnrichment.field_name)
        .all()
    )

    # Build AC-17 nested structure: {str(variety_id): {field_name: {...}}}
    varieties: dict[str, dict[str, Any]] = {}
    enriched_fields_seen: list[str] = []

    for enrichment, variety, crop in rows:
        vid = str(variety.id)
        if vid not in varieties:
            varieties[vid] = {}

        field = enrichment.field_name
        if field not in enriched_fields_seen:
            enriched_fields_seen.append(field)

        varieties[vid][field] = {
            "best": _to_float(enrichment.value_best),
            "min": _to_float(enrichment.value_min),
            "max": _to_float(enrichment.value_max),
            "confidence": _to_float(enrichment.confidence_score),
            "source_count": enrichment.source_count,
            "winning_class": enrichment.winning_source_class,
        }

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": _SCHEMA_VERSION,
        "enriched_fields": sorted(set(enriched_fields_seen)),
        "varieties": varieties,
    }

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    logger.info(
        "Enrichment JSON written: %s (%d varieties, %d enriched fields)",
        output_path, len(varieties), len(payload["enriched_fields"]),
    )
    return output_path.resolve()
