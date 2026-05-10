"""CropBookPublisher — renders ספר גידולים artifacts for WordPress publication.

WP004 / L-GATE_B implementation.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session, joinedload

from organic_market_agent.crop_book.models import (
    Crop,
    CropConversionGroup,
    CropFamily,
    CropUnitConversion,
    CropVariety,
)
from organic_market_agent.crop_book.publisher.entity_registry_data import (
    ENTITY_REGISTRY,
    validate_entity_registry,
)

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "crop_book.v1"
DATA_VERSION = "1.0.0"

CROP_BOOK_DATA_URL_SENTINEL = 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"'

CATEGORIES = {
    "vegetables":  "ירקות",
    "herbs":       "עשבי תיבול",
    "baby":        "עלים בייבי",
    "legumes":     "קטניות",
    "fruits":      "פירות",
    "fruit_trees": "עצי פרי",
    "grains":      "דגנים",
    "cover_crops": "גידולי כיסוי",
}

SEASON_TOKENS = [
    {"key": "summer", "tokens": ["קיץ", "summer"],          "emoji": "☀️"},
    {"key": "spring", "tokens": ["אביב", "spring"],          "emoji": "🌸"},
    {"key": "winter", "tokens": ["חורף", "winter"],          "emoji": "🌧"},
    {"key": "fall",   "tokens": ["סתיו", "fall", "autumn"],  "emoji": "💨"},
]


class CropBookPublishAbortError(Exception):
    """Raised when publisher cannot safely produce artifacts."""


# ---------------------------------------------------------------------------
# Private dict helpers (module-level, not methods)
# ---------------------------------------------------------------------------

def _source_value_to_dict(sv: Any) -> dict:
    return {
        "field_name":    sv.field_name,
        "source":        sv.source,
        "value_text":    sv.value_text,
        "value_numeric": float(sv.value_numeric) if sv.value_numeric is not None else None,
        "unit":          sv.unit,
        "note":          sv.note,
    }


def _variety_to_dict(v: CropVariety) -> dict:
    return {
        "id":                          v.id,
        "name_he":                     v.name_he,
        "name_en":                     v.name_en,
        "is_default":                  bool(v.is_default),
        "is_grafted":                  bool(v.is_grafted) if v.is_grafted is not None else False,
        "rootstock_variety":           v.rootstock_variety,
        "planting_method":             v.planting_method,
        "days_to_maturity":            v.days_to_maturity,
        "harvest_window_min_days":     v.harvest_window_min_days,
        "harvest_window_max_days":     v.harvest_window_max_days,
        "in_row_spacing_cm":           float(v.in_row_spacing_cm) if v.in_row_spacing_cm is not None else None,
        "rows_per_bed":                v.rows_per_bed,
        "planting_season":             v.planting_season,
        "succession_interval_weeks":   v.succession_interval_weeks,
        "harvest_stage":               v.harvest_stage,
        "harvest_unit":                v.harvest_unit,
        "avg_yield_per_bed_m":         float(v.avg_yield_per_bed_m) if v.avg_yield_per_bed_m is not None else None,
        "yield_source":                v.yield_source,
        "documented_price":            float(v.documented_price) if v.documented_price is not None else None,
        "documented_price_unit":       v.documented_price_unit,
        "documented_price_source":     v.documented_price_source,
        "avg_revenue_per_bed_m":       float(v.avg_revenue_per_bed_m) if v.avg_revenue_per_bed_m is not None else None,
        "pricebook_product_id":        v.pricebook_product_id,
        "days_to_germinate_gh":        v.days_to_germinate_gh,
        "days_in_gh_total":            v.days_in_gh_total,
        "seeder":                      v.seeder,
        "seeder_front_gear":           v.seeder_front_gear,
        "seeder_rear_gear":            v.seeder_rear_gear,
        "seeder_roller_plate":         v.seeder_roller_plate,
        "notes":                       v.notes,
        "source_values":               [_source_value_to_dict(sv) for sv in (v.source_values or [])],
    }


def _crop_to_dict(crop: Crop) -> dict:
    varieties_sorted = sorted(crop.varieties or [], key=lambda v: v.id)
    return {
        "id":                   crop.id,
        "name_he":              crop.name_he,
        "name_en":              crop.name_en,
        "scientific_name":      crop.scientific_name,
        "family_id":            crop.family_id,
        "category":             crop.category,
        "growth_cycle":         crop.growth_cycle,
        "harvest_unit_default": crop.harvest_unit_default,
        "first_fruit_year":     crop.first_fruit_year,
        "conversion_group_id":  crop.conversion_group_id,
        "description":          crop.description,
        "oma_product_id":       crop.oma_product_id,
        "varieties":            [_variety_to_dict(v) for v in varieties_sorted],
    }


def _family_to_dict(f: CropFamily) -> dict:
    return {
        "id":             f.id,
        "scientific_name": f.scientific_name,
        "name_he":        f.name_he,
    }


def _group_to_dict(g: CropConversionGroup) -> dict:
    return {
        "id":          g.id,
        "name":        g.name,
        "description": g.description,
    }


def _conversion_to_dict(c: CropUnitConversion) -> dict:
    return {
        "id":                  c.id,
        "conversion_group_id": c.conversion_group_id,
        "crop_id":             c.crop_id,
        "source_unit":         c.source_unit,
        "target_unit":         c.target_unit,
        "conversion_factor":   float(c.conversion_factor) if c.conversion_factor is not None else None,
        "context":             c.context,
        "source":              c.source,
        "note":                c.note,
    }


def _artifact_version(gen: datetime) -> str:
    return gen.strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# Publisher class
# ---------------------------------------------------------------------------

class CropBookPublisher:
    """Renders ספר גידולים artifacts for WordPress publication.

    Stateless — instantiate once, call run() per publish.
    """

    SCHEMA_VERSION = SCHEMA_VERSION
    DATA_VERSION   = DATA_VERSION

    def run(
        self,
        session: Session,
        output_dir: Path,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Render and write 3 artifacts into output_dir.

        Returns summary dict: output_dir, files, crop_count, variety_count,
        data_size_bytes, generated_at.

        Raises CropBookPublishAbortError on abort conditions.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        gen = generated_at or datetime.now(timezone.utc)
        if gen.tzinfo is None:
            gen = gen.replace(tzinfo=timezone.utc)

        logger.info("CropBookPublisher: starting render (generated_at=%s)", gen.isoformat())

        # --- Validate entity registry ---
        try:
            validate_entity_registry(ENTITY_REGISTRY)
        except ValueError as exc:
            raise CropBookPublishAbortError(f"entity registry invalid: {exc}") from exc

        # --- DB queries ---
        crops = (
            session.query(Crop)
            .options(
                joinedload(Crop.family),
                joinedload(Crop.varieties).joinedload(CropVariety.source_values),
                joinedload(Crop.conversion_group).joinedload(CropConversionGroup.conversions),
            )
            .order_by(Crop.name_he)
            .all()
        )

        if not crops:
            raise CropBookPublishAbortError(
                "crop count is 0 — refusing to publish an empty book"
            )

        families = (
            session.query(CropFamily)
            .order_by(CropFamily.scientific_name)
            .all()
        )
        conversion_groups = (
            session.query(CropConversionGroup)
            .order_by(CropConversionGroup.name)
            .all()
        )
        crop_conversions = (
            session.query(CropUnitConversion)
            .filter(CropUnitConversion.crop_id.isnot(None))
            .all()
        )
        group_conversions = (
            session.query(CropUnitConversion)
            .filter(CropUnitConversion.conversion_group_id.isnot(None))
            .all()
        )
        all_conversions = crop_conversions + group_conversions

        variety_count = sum(len(c.varieties or []) for c in crops)

        # --- Assemble data JSON ---
        data_payload = {
            "schema":       self.SCHEMA_VERSION,
            "data_version": self.DATA_VERSION,
            "generated_at": gen.isoformat(),
            "categories":   CATEGORIES,
            "season_tokens": SEASON_TOKENS,
            "families":          [_family_to_dict(f) for f in families],
            "conversion_groups": [_group_to_dict(g) for g in conversion_groups],
            "conversions":       [_conversion_to_dict(c) for c in all_conversions],
            "entity_registry":   ENTITY_REGISTRY,
            "crops":             [_crop_to_dict(c) for c in crops],
        }

        data_json = json.dumps(data_payload, ensure_ascii=False, indent=2)
        data_path = output_dir / "sfagent-crop-book-data.json"
        data_path.write_text(data_json, encoding="utf-8")
        data_size_bytes = len(data_json.encode("utf-8"))

        # --- Render body fragment ---
        templates_dir = Path(__file__).parent / "templates"
        static_dir    = Path(__file__).parent / "static"
        spa_js = (static_dir / "sfagent-crop-book.js").read_text(encoding="utf-8")

        jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        body_tpl = jinja_env.get_template("crop_book_body.html")
        body_html = body_tpl.render(
            spa_js=spa_js,
            data_url="./sfagent-crop-book-data.json",
        )

        # Sentinel assertion — AC-17
        if CROP_BOOK_DATA_URL_SENTINEL not in body_html:
            raise CropBookPublishAbortError(
                "body fragment missing CROP_BOOK_DATA_URL sentinel — template drift"
            )

        body_path = output_dir / "sfagent-crop-book-body.html"
        body_path.write_text(body_html, encoding="utf-8")

        # --- Manifest ---
        av = _artifact_version(gen)
        manifest = {
            "schema_version":    "crop_book.manifest.v1",
            "artifact_version":  av,
            "generated_at":      gen.isoformat(),
            "crop_count":        len(crops),
            "variety_count":     variety_count,
            "source_value_count": sum(
                len(v.source_values or [])
                for c in crops
                for v in (c.varieties or [])
            ),
            "data_size_bytes":   data_size_bytes,
            "artifacts": {
                "body":     "sfagent-crop-book-body.html",
                "data":     "sfagent-crop-book-data.json",
                "manifest": "sfagent-crop-book-manifest.json",
            },
        }
        manifest_path = output_dir / "sfagent-crop-book-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info(
            "CropBookPublisher: wrote %d crops / %d varieties to %s (version=%s)",
            len(crops), variety_count, output_dir, av,
        )

        return {
            "output_dir":      str(output_dir.resolve()),
            "files":           [
                "sfagent-crop-book-body.html",
                "sfagent-crop-book-data.json",
                "sfagent-crop-book-manifest.json",
            ],
            "crop_count":      len(crops),
            "variety_count":   variety_count,
            "data_size_bytes": data_size_bytes,
            "generated_at":    gen.isoformat(),
        }
