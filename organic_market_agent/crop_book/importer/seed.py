"""ספר גידולים seed importer CLI.

Usage:
    python -m organic_market_agent.crop_book.importer.seed --help
    python -m organic_market_agent.crop_book.importer.seed --all
    python -m organic_market_agent.crop_book.importer.seed --crops Arugula Broccoli
    python -m organic_market_agent.crop_book.importer.seed --dry-run --year 2022
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.constants import TEND_CROP_MAP
from organic_market_agent.crop_book.importer.jmf import parse_jmf_dir
from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm, reconcile_variety
from organic_market_agent.crop_book.importer.tend import (
    discover_tend_years,
    parse_crop_plan,
    parse_product_sold,
)
from organic_market_agent.crop_book.models import (
    Crop,
    CropConversionGroup,
    CropFamily,
    CropUnitConversion,
    CropVariety,
    CropVarietySourceValue,
)

logger = logging.getLogger(__name__)

_DEFAULT_SOURCE_DIR = Path("/Users/nimrod/Documents/israel Microgreens/crop data")
_DEFAULT_JMF_DIR = Path("/Users/nimrod/Documents/Market Gardening/MasterClass/Crops Data")

_CROP_FAMILIES_SEED: list[tuple[str, str]] = [
    ("Aizoaceae", "ריסניים"),
    ("Amaranthaceae", "ירבוזיים"),
    ("Amaryllidaceae", "נרקיסיים"),
    ("Apiaceae", "סלריים"),
    ("Arecaceae", "דקליים"),
    ("Asparagaceae", "אספרגוסיים"),
    ("Asteraceae", "מורכבים"),
    ("Brassicaceae", "מצליבים"),
    ("Bromeliaceae", "אנניסיים"),
    ("Caricaceae", "פפאייתיים"),
    ("Cucurbitaceae", "דלועיים"),
    ("Fabaceae", "קטניות"),
    ("Lamiaceae", "שפתניים"),
    ("Lauraceae", "דפניים"),
    ("Malvaceae", "חלמיתיים"),
    ("Musaceae", "בנניים"),
    ("Poaceae", "דשאיים"),
    ("Polygonaceae", "לשוניתניים"),
    ("Rosaceae", "ורדיים"),
    ("Rutaceae", "פגיים"),
    ("Solanaceae", "סולניים"),
    ("Verbenaceae", "ורבניים"),
    ("Zingiberaceae", "זנגוויליים"),
]

_CONVERSION_GROUPS_SEED: list[tuple[str, str]] = [
    ("עלים_בייבי", "Baby leaf crops — arugula, rocket, baby mustard, salad mix"),
    ("עלים_גדולים", "Large leaf crops — chard, kale, spinach, celery, herbs"),
    ("שורש_קטן", "Small root crops — carrot, turnip, radish, small beet"),
    ("ראש", "Head crops — lettuce, cabbage, kohlrabi, pak choi"),
    ("פרי_גדול", "Large fruit crops — tomato, zucchini, eggplant, pepper, cucumber"),
    ("עשבי_תיבול", "Fresh culinary herbs — basil, mint, sage, thyme, lemon balm"),
    ("ללא_קבוצה", "Crops with unique conversions not shared by any group"),
]

_CONVERSION_UNITS_SEED: list[tuple[str, str, str, Decimal, str | None, str]] = [
    ("עלים_בייבי", "bunch", "gram", Decimal("150"), None, "team_00"),
    ("עלים_גדולים", "bunch", "gram", Decimal("200"), None, "manual"),
    ("שורש_קטן", "bunch", "gram", Decimal("300"), None, "manual"),
    ("ראש", "head", "gram", Decimal("500"), None, "manual"),
    ("פרי_גדול", "kg", "gram", Decimal("1000"), None, "manual"),
    ("עשבי_תיבול", "bunch", "gram", Decimal("80"), None, "team_00"),
]

_BABY_CROPS = {"ארוגולה", "תערובת סלט", "גרגר נחלים"}
_LEAF_LARGE = {"מנגולד", "קייל", "תרד", "סלרי", "כוסברה", "פטרוזיליה", "שמיר"}
_ROOT_SMALL = {"גזר", "לפת", "צנונית", "סלק"}
_HEAD_CROPS = {"חסה", "כרוב", "קולורבי", "פאק צ'וי"}
_FRUIT_LARGE = {"עגבנייה", "קישוא", "חציל", "פלפל", "מלפפון"}
_HERBS = {"בזיל", "נענע", "מרווה", "טימין", "לימון בלם", "לימון ורבנה", "עירית", "אזוב מצוי"}


def _infer_conversion_group(name_he: str, category: str) -> str | None:
    if name_he in _BABY_CROPS or category == "baby":
        return "עלים_בייבי"
    if name_he in _LEAF_LARGE:
        return "עלים_גדולים"
    if name_he in _ROOT_SMALL:
        return "שורש_קטן"
    if name_he in _HEAD_CROPS:
        return "ראש"
    if name_he in _FRUIT_LARGE:
        return "פרי_גדול"
    if name_he in _HERBS or category == "herbs":
        return "עשבי_תיבול"
    return None


def _get_or_create_family(session: Session, scientific_name: str, name_he: str) -> CropFamily:
    obj = session.query(CropFamily).filter_by(scientific_name=scientific_name).first()
    if obj is None:
        obj = CropFamily(scientific_name=scientific_name, name_he=name_he)
        session.add(obj)
        session.flush()
    else:
        obj.name_he = name_he
    return obj


def _get_or_create_group(session: Session, name: str, description: str) -> CropConversionGroup:
    obj = session.query(CropConversionGroup).filter_by(name=name).first()
    if obj is None:
        obj = CropConversionGroup(name=name, description=description)
        session.add(obj)
        session.flush()
    else:
        obj.description = description
    return obj


def _get_or_create_crop(session: Session, name_he: str, data: dict[str, Any]) -> Crop:
    obj = session.query(Crop).filter_by(name_he=name_he).first()
    if obj is None:
        obj = Crop(name_he=name_he, **{k: v for k, v in data.items() if k != "name_he"})
        session.add(obj)
        session.flush()
    else:
        for k, v in data.items():
            if k == "name_he":
                continue
            if v is not None:
                setattr(obj, k, v)
    return obj


def _get_or_create_variety(
    session: Session, crop_id: int, name_en: str | None, is_default: bool, data: dict[str, Any]
) -> CropVariety:
    from organic_market_agent.crop_book.constants import DEFAULT_VARIETY_NAME_HE

    if name_en is not None:
        obj = session.query(CropVariety).filter_by(crop_id=crop_id, name_en=name_en).first()
    else:
        obj = session.query(CropVariety).filter_by(crop_id=crop_id, is_default=True).first()

    if obj is None:
        # Apply system-wide naming rule: default variety always carries name_he
        name_he_val = DEFAULT_VARIETY_NAME_HE if is_default else data.pop("name_he", None)
        obj = CropVariety(
            crop_id=crop_id,
            name_en=name_en,
            name_he=name_he_val,
            is_default=is_default,
            **{k: v for k, v in data.items() if k != "name_he"},
        )
        session.add(obj)
        session.flush()
    else:
        # Back-fill name_he on existing unnamed default varieties
        if is_default and obj.name_he is None:
            obj.name_he = DEFAULT_VARIETY_NAME_HE
        for k, v in data.items():
            if v is not None and k != "name_he":
                setattr(obj, k, v)
    return obj


def _upsert_source_value(session: Session, variety_id: int, sv: dict[str, Any]) -> None:
    obj = (
        session.query(CropVarietySourceValue)
        .filter_by(variety_id=variety_id, field_name=sv["field_name"], source=sv["source"])
        .first()
    )
    if obj is None:
        obj = CropVarietySourceValue(variety_id=variety_id, **sv)
        session.add(obj)
    else:
        for k, v in sv.items():
            setattr(obj, k, v)


def seed(
    session: Session,
    target_crops: list[str] | None,
    dry_run: bool,
    year_filter: str | None,
    source_dir: Path,
    jmf_dir: Path,
) -> None:
    """Main seed orchestration. session is a SQLAlchemy Session (any dialect)."""

    # 1. Seed botanical families
    logger.info("Seeding crop_families (%d rows)...", len(_CROP_FAMILIES_SEED))
    family_map: dict[str, CropFamily] = {}
    for scientific_name, name_he in _CROP_FAMILIES_SEED:
        if not dry_run:
            family_map[scientific_name] = _get_or_create_family(session, scientific_name, name_he)

    # 2. Seed conversion groups
    logger.info("Seeding crop_conversion_groups (%d rows)...", len(_CONVERSION_GROUPS_SEED))
    group_map: dict[str, CropConversionGroup] = {}
    for group_name, group_desc in _CONVERSION_GROUPS_SEED:
        if not dry_run:
            group_map[group_name] = _get_or_create_group(session, group_name, group_desc)

    # 3. Seed group-level unit conversions
    if not dry_run:
        for group_name, src_unit, tgt_unit, factor, context, src in _CONVERSION_UNITS_SEED:
            grp = group_map.get(group_name)
            if grp is None:
                continue
            existing = (
                session.query(CropUnitConversion)
                .filter_by(conversion_group_id=grp.id, source_unit=src_unit, context=context)
                .first()
            )
            if existing is None:
                session.add(
                    CropUnitConversion(
                        conversion_group_id=grp.id,
                        crop_id=None,
                        source_unit=src_unit,
                        target_unit=tgt_unit,
                        conversion_factor=factor,
                        context=context,
                        source=src,
                    )
                )

    # 4. Discover Tend year folders
    tend_years = discover_tend_years(source_dir)
    if year_filter:
        tend_years = [(y, p) for y, p in tend_years if y == year_filter or y == "flat"]
    if not tend_years:
        logger.warning("No Tend year data found under %s", source_dir)

    # 5. Collect all Tend rows, group by name_he
    crop_rows_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    product_prices: dict[str, Decimal] = {}
    for year, plan_path in tend_years:
        rows = parse_crop_plan(plan_path, year if year != "flat" else None)
        for row in rows:
            crop_rows_by_name[row["name_he"]].append(row)

        product_sold_path = plan_path.parent / "PRODUCT_SOLD (from macBook Air - nimrod).CSV"
        if product_sold_path.exists() and year != "flat":
            product_prices.update(parse_product_sold(product_sold_path, year))

    parse_jmf_dir(jmf_dir)

    # 6. Determine which crops to process
    if target_crops:
        names_he = []
        for c in target_crops:
            if c in TEND_CROP_MAP:
                names_he.append(TEND_CROP_MAP[c])
            else:
                logger.warning("Unknown crop name: %r (not in TEND_CROP_MAP)", c)
    else:
        names_he = list(TEND_CROP_MAP.values())

    carrot_crop_id: int | None = None
    fallback_family = next(iter(family_map.values())) if family_map else None

    for name_he in names_he:
        rows = crop_rows_by_name.get(name_he, [])
        if not rows:
            logger.warning("WARN: no Tend data found for crop %r", name_he)
            continue

        first = rows[0]
        scientific_name = first.get("family_scientific_name")
        family = family_map.get(scientific_name) if scientific_name else None
        if family is None:
            family = fallback_family
        if family is None or dry_run:
            crop_id = 0
            if dry_run:
                logger.info("[dry-run] Would process crop: %r", name_he)
            continue

        category = first.get("category") or "vegetables"
        growth_cycle = first.get("growth_cycle")
        harvest_unit_default = first.get("harvest_unit")
        group_name = _infer_conversion_group(name_he, category)
        conv_group = group_map.get(group_name) if group_name else None

        crop = _get_or_create_crop(
            session,
            name_he,
            {
                "name_en": first.get("name_en"),
                "scientific_name": first.get("scientific_name"),
                "family_id": family.id,
                "category": category,
                "growth_cycle": growth_cycle,
                "harvest_unit_default": harvest_unit_default,
                "first_fruit_year": first.get("first_fruit_year"),
                "conversion_group_id": conv_group.id if conv_group else None,
                "description": None,
                "oma_product_id": None,
            },
        )
        crop_id = crop.id

        if name_he == "גזר":
            carrot_crop_id = crop_id

        variety_rows: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            v_name = row.get("variety_name_en") or None
            variety_rows[v_name].append(row)

        if None not in variety_rows and variety_rows:
            first_key = next(iter(variety_rows))
            variety_rows[None] = list(variety_rows[first_key])

        for variety_name_en, v_rows in variety_rows.items():
            is_default = variety_name_en is None
            vfirst = v_rows[0]

            tend_dtm_values = [r.get("days_to_maturity") for r in v_rows if r.get("days_to_maturity") is not None]
            unified_dtm, dtm_sv_rows = reconcile_dtm(name_he, tend_dtm_values, None)

            source_value_rows: list[dict[str, Any]] = list(dtm_sv_rows)

            if vfirst.get("avg_yield_per_bed_m") is not None:
                source_value_rows.append({
                    "field_name": "avg_yield_per_bed_m",
                    "source": vfirst.get("source", "Tend"),
                    "value_text": str(vfirst["avg_yield_per_bed_m"]),
                    "value_numeric": vfirst["avg_yield_per_bed_m"],
                    "unit": "yield/m",
                    "note": None,
                })

            if vfirst.get("harvest_window_max_days") is not None:
                source_value_rows.append({
                    "field_name": "harvest_window_max_days",
                    "source": vfirst.get("source", "Tend"),
                    "value_text": str(vfirst["harvest_window_max_days"]),
                    "value_numeric": Decimal(vfirst["harvest_window_max_days"]),
                    "unit": "days",
                    "note": None,
                })

            doc_price = vfirst.get("documented_price")
            if doc_price is None and name_he in product_prices:
                doc_price = product_prices[name_he]
            if doc_price is not None:
                source_value_rows.append({
                    "field_name": "documented_price",
                    "source": vfirst.get("source", "Tend"),
                    "value_text": str(doc_price),
                    "value_numeric": doc_price,
                    "unit": f"ILS/{harvest_unit_default or 'unit'}",
                    "note": None,
                })

            if vfirst.get("rootstock_variety"):
                source_value_rows.append({
                    "field_name": "rootstock_variety",
                    "source": "Tend",
                    "value_text": vfirst["rootstock_variety"],
                    "value_numeric": None,
                    "unit": None,
                    "note": None,
                })

            unified = reconcile_variety(source_value_rows)

            variety = _get_or_create_variety(
                session,
                crop_id,
                variety_name_en,
                is_default,
                {
                    "is_grafted": unified.get("is_grafted", vfirst.get("is_grafted", False)),
                    "rootstock_variety": unified.get("rootstock_variety", vfirst.get("rootstock_variety")),
                    "planting_method": vfirst.get("planting_method"),
                    "days_to_maturity": unified_dtm,
                    "harvest_window_max_days": vfirst.get("harvest_window_max_days"),
                    "in_row_spacing_cm": unified.get("in_row_spacing_cm", vfirst.get("in_row_spacing_cm")),
                    "rows_per_bed": unified.get("rows_per_bed", vfirst.get("rows_per_bed")),
                    "harvest_unit": vfirst.get("harvest_unit"),
                    "avg_yield_per_bed_m": unified.get("avg_yield_per_bed_m"),
                    "yield_source": unified.get("yield_source"),
                    "documented_price": unified.get("documented_price", doc_price),
                    "documented_price_unit": unified.get("documented_price_unit"),
                    "documented_price_source": unified.get("documented_price_source", vfirst.get("source")),
                    "days_in_gh_total": vfirst.get("days_in_gh_total"),
                    "seeder": unified.get("seeder", vfirst.get("seeder")),
                    "seeder_front_gear": unified.get("seeder_front_gear", vfirst.get("seeder_front_gear")),
                    "seeder_rear_gear": unified.get("seeder_rear_gear", vfirst.get("seeder_rear_gear")),
                    "seeder_roller_plate": unified.get("seeder_roller_plate", vfirst.get("seeder_roller_plate")),
                    "harvest_stage": vfirst.get("harvest_stage"),
                    "notes": None,
                },
            )

            for sv in source_value_rows:
                sv_data = {
                    "field_name": sv["field_name"],
                    "source": sv["source"],
                    "value_text": sv.get("value_text"),
                    "value_numeric": sv.get("value_numeric"),
                    "unit": sv.get("unit"),
                    "note": sv.get("note"),
                    # GCR_1 enrichment columns — populated by reconcile_dtm; None for other sources
                    "trust_tier": sv.get("trust_tier"),
                    "confidence_weight": sv.get("confidence_weight"),
                    "is_outlier_rejected": sv.get("is_outlier_rejected", False),
                }
                _upsert_source_value(session, variety.id, sv_data)

        session.flush()

    # 7. Carrot crop-specific unit conversion overrides
    if not dry_run and carrot_crop_id is not None:
        for src_unit, context, factor, src in [
            ("bunch", "fresh", Decimal("500"), "team_00"),
            ("kg", "packaged", Decimal("1000"), "manual"),
        ]:
            existing = (
                session.query(CropUnitConversion)
                .filter_by(crop_id=carrot_crop_id, source_unit=src_unit, context=context)
                .first()
            )
            if existing is None:
                session.add(
                    CropUnitConversion(
                        conversion_group_id=None,
                        crop_id=carrot_crop_id,
                        source_unit=src_unit,
                        target_unit="gram",
                        conversion_factor=factor,
                        context=context,
                        source=src,
                    )
                )
        logger.info("Seeded carrot crop-specific unit overrides")

    if not dry_run:
        session.commit()
    logger.info("Seed complete. dry_run=%s", dry_run)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level=level, stream=sys.stdout)


_DEFAULT_JMF_MASTERCLASS_DIR = Path(
    "/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning"
)
_EXTERNAL_SOURCES_DIR = (
    Path(__file__).resolve().parents[3] / "data" / "external_sources"
)
_TEND_MULTI_YEAR_DIR = _EXTERNAL_SOURCES_DIR / "tend_multi_year"


def _run_c4_ingestion(session: Session) -> None:
    """WP-C4: Web sources (team_80 multi-engine scout)."""
    from organic_market_agent.crop_book.importer.web import (
        il_moa_calendar,
        ne_veg_guide_nutrients,
        osu_frost_tolerance,
        seeds_per_gram,
        uc_anr_germination,
        uc_davis_postharvest,
        uf_ifas_companion,
        umd_soil_ph,
    )

    logger.info("WP-C4: Web sources ingestion (8 importers)")
    modules = [
        il_moa_calendar,
        uc_anr_germination,
        osu_frost_tolerance,
        umd_soil_ph,
        ne_veg_guide_nutrients,
        seeds_per_gram,
        uf_ifas_companion,
        uc_davis_postharvest,
    ]
    for module in modules:
        summary = module.import_all(session)
        logger.info("WP-C4 %s: %s", module.__name__.split(".")[-1], summary)
    session.flush()


def _run_c1_ingestion(session: Session) -> None:
    """WP-C1: Israeli structured sources + Tend 2019/2020/2021 backfill."""
    from organic_market_agent.crop_book.importer.israeli import (
        bustan_importer,
        groworganic_importer,
        idan_planning_importer,
    )
    from organic_market_agent.crop_book.importer.jmf.cover_crops_importer import import_all as import_cover_crops
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay

    logger.info("WP-C1: Running Israeli structured data + Tend multi-year backfill")
    groworganic_importer.import_all(
        session,
        _EXTERNAL_SOURCES_DIR / "israeli" / "L01_GROWORGANIC_sowing_dates_base.xlsx",
    )
    bustan_importer.import_all(
        session,
        _EXTERNAL_SOURCES_DIR / "israeli" / "L36_BUSTAN_sowing_calendar.pdf",
    )
    idan_planning_importer.import_all(
        session,
        _EXTERNAL_SOURCES_DIR / "israeli" / "L03_IDAN_winter_planning.xlsx",
        _EXTERNAL_SOURCES_DIR / "israeli" / "L04_IDAN_summer_planning.xlsx",
    )
    import_cover_crops(
        session,
        _EXTERNAL_SOURCES_DIR / "jmf_extension" / "L12_cover_crop_chart.pdf",
    )
    for year in (2019, 2020, 2021):
        summary = import_tend_overlay(
            session, _TEND_MULTI_YEAR_DIR, year=year, dry_run=False,
        )
        logger.info("Tend overlay %s: %s", year, summary)
    session.flush()


def _run_c3_ingestion(session: Session) -> None:
    """WP-C3: Curtis Stone + Idan succession + FRANCHI + L49 diff + Tend 2018."""
    from organic_market_agent.crop_book.importer.urban_farmer import (
        curtis_profiles_importer,
        curtis_ocr_importer,
    )
    from organic_market_agent.crop_book.importer.israeli import (
        idan_seedlings_importer,
        franchi_catalog_importer,
        idan_2018_diff,
    )
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay

    logger.info("WP-C3: Curtis Stone + Israeli secondary + Tend 2018")
    summary_l40 = curtis_profiles_importer.import_all(session)
    logger.info("WP-C3 Curtis L40: %s", summary_l40)
    summary_ocr = curtis_ocr_importer.import_all(session)
    logger.info("WP-C3 Curtis OCR: %s", summary_ocr)
    summary_seedlings = idan_seedlings_importer.import_all(session, [
        _EXTERNAL_SOURCES_DIR / "israeli" / "L05a_IDAN_seedlings_winter_18-19.xlsx",
        _EXTERNAL_SOURCES_DIR / "israeli" / "L05b_IDAN_seedlings_summer_18-19.xlsx",
    ])
    logger.info("WP-C3 Idan seedlings: %s", summary_seedlings)
    summary_franchi = franchi_catalog_importer.import_all(session)
    logger.info("WP-C3 FRANCHI: %s", summary_franchi)
    summary_diff = idan_2018_diff.import_all(
        session,
        _EXTERNAL_SOURCES_DIR / "israeli" / "L49_IDAN_market_gardening_tech.xlsx",
        _EXTERNAL_SOURCES_DIR / "israeli" / "L03_IDAN_winter_planning.xlsx",
        _EXTERNAL_SOURCES_DIR / "israeli" / "L04_IDAN_summer_planning.xlsx",
    )
    logger.info("WP-C3 L49 diff: %s", summary_diff)
    summary_tend = import_tend_overlay(session, _TEND_MULTI_YEAR_DIR, year=2018, dry_run=False)
    logger.info("WP-C3 Tend 2018: %s", summary_tend)
    session.flush()


def _run_ni_ingestion(session: Session) -> None:
    """Single NI call-site block — iterates NI_IMPORTER_CLASSES once.

    B2 bypasses ni_registry.load_all() per §7.1 architectural decision.
    B2 does NOT call ni_registry.register; the 6 subclasses are NOT
    registered with ni_registry; seed.py iterates NI_IMPORTER_CLASSES
    directly with session for the variety_id / crop_id resolution.
    """
    from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    for cls in NI_IMPORTER_CLASSES:
        importer = cls()  # constructor takes no args (subclass attrs are class-level)

        # PATH A: variety-source-value rows (cultivar_recommendation only)
        for row in importer.load(session):
            # Row is fully resolved by load(); use existing WP-A signature:
            variety_id = row.pop("variety_id")
            _upsert_source_value(session, variety_id, row)

        # PATH B: crop_knowledge_notes rows (B2-specific)
        for row in importer.load_knowledge_notes(session):
            # Row is fully resolved by load_knowledge_notes(); crop_id is in the dict
            _upsert_knowledge_note(session, **row)

    session.flush()


def _run_c2_ingestion(session: Session) -> None:
    """WP-C2: Hebrew narrative NI importers (7 sources).

    Mirrors _run_ni_ingestion pattern but iterates NI_C2_IMPORTER_CLASSES.
    All C2 importers produce crop_knowledge_notes rows only (load() returns []).
    """
    from organic_market_agent.crop_book.importer.ni import NI_C2_IMPORTER_CLASSES
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    logger.info("WP-C2: Hebrew narrative NI ingestion (%d importers)", len(NI_C2_IMPORTER_CLASSES))
    for cls in NI_C2_IMPORTER_CLASSES:
        importer = cls()

        for row in importer.load(session):
            variety_id = row.pop("variety_id")
            _upsert_source_value(session, variety_id, row)

        for row in importer.load_knowledge_notes(session):
            _upsert_knowledge_note(session, **row)

    session.flush()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ספר גידולים seed importer — populate crop-book tables from Tend CSV + JMF XLSX"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", action="store_true", help="Import all crops in TEND_CROP_MAP")
    mode.add_argument(
        "--c1-only", action="store_true",
        help="Run WP-C1 importers only (Israeli structured + Tend multi-year)",
    )
    mode.add_argument(
        "--c4-only", action="store_true",
        help="Run WP-C4 web-source importers only",
    )
    mode.add_argument(
        "--c2-only", action="store_true",
        help="Run WP-C2 Hebrew narrative NI importers only",
    )
    mode.add_argument(
        "--c3-only", action="store_true",
        help="Run WP-C3 importers only (Curtis Stone + Idan succession + FRANCHI + L49 diff + Tend 2018)",
    )
    mode.add_argument(
        "--wd-only", action="store_true",
        help="Run WP-D importers only (Cursor web research — 16-crop expansion batches)",
    )
    mode.add_argument(
        "--openai-only", action="store_true",
        help="Run WP-E importer only (OpenAI Tier 1 university-extension research, 24 crops)",
    )
    mode.add_argument(
        "--idan-only", action="store_true",
        help="Run WP-F importer only (Idan farm seasonal planning records, L03/L04/L49)",
    )
    mode.add_argument(
        "--calendar-only", action="store_true",
        help="Run WP-G importer only (Israeli planting calendar — GrowOrganic L01 + Bustan L36)",
    )
    mode.add_argument(
        "--gemini-only", action="store_true",
        help="Run WP-H importer only (Gemini IL research — 20 crops incl. sweet_potato/okra/fava/chicory/etc.)",
    )
    mode.add_argument(
        "--crops", nargs="+", metavar="NAME",
        help="Import named crops (Tend English names, e.g. Arugula Broccoli)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and log without writing to DB")
    parser.add_argument("--year", metavar="YEAR", help="Restrict Tend data to a single year")
    parser.add_argument(
        "--source-dir", type=Path, default=_DEFAULT_SOURCE_DIR,
        metavar="PATH", help="Base path for Tend data (default: %(default)s)",
    )
    parser.add_argument(
        "--jmf-dir", type=Path, default=_DEFAULT_JMF_DIR,
        metavar="PATH", help="JMF XLSX directory (default: %(default)s)",
    )
    parser.add_argument(
        "--jmf-masterclass-dir", type=Path,
        default=_DEFAULT_JMF_MASTERCLASS_DIR,
        metavar="PATH",
        help="JMF MasterClass XLSX directory (default: %(default)s)",
    )
    # --jmf-only and --no-jmf are mutually exclusive (LOD400 §8.1)
    jmf_excl = parser.add_mutually_exclusive_group()
    jmf_excl.add_argument(
        "--jmf-only", action="store_true",
        help="Run only JMF MasterClass ingestion (skip Tend).",
    )
    jmf_excl.add_argument(
        "--no-jmf", action="store_true",
        help="Skip JMF MasterClass ingestion (Tend only).",
    )
    # --ni-only and --no-ni are mutually exclusive (LOD400 §8)
    ni_excl = parser.add_mutually_exclusive_group()
    ni_excl.add_argument(
        "--ni-only", action="store_true",
        help="Run only NI ingestion (skip JMF MasterClass / Tend / Tend overlay).",
    )
    ni_excl.add_argument(
        "--no-ni", action="store_true",
        help="Skip NI ingestion.",
    )
    parser.add_argument(
        "--tend-overlay-dir", type=Path,
        default=Path("/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022"),
        metavar="PATH",
        help="Tend overlay CSV directory (default: %(default)s; year inferred from dirname suffix)",
    )
    parser.add_argument(
        "--tend-overlay-year", type=int, default=2022, metavar="YEAR",
        help="Year for source label and HARVESTS aggregation (default: %(default)s)",
    )
    # --tend-overlay-only and --no-tend-overlay are mutually exclusive (LOD400 §8)
    tend_excl = parser.add_mutually_exclusive_group()
    tend_excl.add_argument(
        "--tend-overlay-only", action="store_true",
        help="Run only Tend overlay ingestion (skip JMF / NI / WP-A Tend).",
    )
    tend_excl.add_argument(
        "--no-tend-overlay", action="store_true",
        help="Skip Tend overlay ingestion.",
    )
    parser.add_argument(
        "--no-c1", action="store_true",
        help="Skip WP-C1 importers when --all is used",
    )
    parser.add_argument(
        "--no-c4", action="store_true",
        help="Skip WP-C4 importers when --all is used",
    )
    parser.add_argument(
        "--no-c2", action="store_true",
        help="Skip WP-C2 Hebrew narrative NI importers when --all is used",
    )
    parser.add_argument(
        "--no-c3", action="store_true",
        help="Skip WP-C3 importers when --all is used",
    )
    parser.add_argument(
        "--no-enrich", action="store_true",
        help="Skip enrichment_runner when --all is used (default: enrichment runs automatically with --all)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)

    # Additional mutual-exclusion validation (LOD400 §8.3)
    if args.jmf_only and getattr(args, 'crops', None):
        parser.error("--jmf-only cannot be combined with --crops")

    target_crops: list[str] | None = None
    if getattr(args, 'crops', None):
        target_crops = args.crops
    elif not args.all and not args.jmf_only and not args.ni_only and not args.c1_only and not args.c4_only and not args.c2_only and not args.c3_only and not args.wd_only and not args.openai_only and not args.idan_only and not args.calendar_only and not args.gemini_only:
        parser.error(
            "Specify --all, --c1-only, --c2-only, --c3-only, --c4-only, --wd-only, --openai-only, --idan-only, "
            "--jmf-only, --ni-only, or --crops NAME [NAME ...]"
        )

    # ── C4-only fast path (WP-C4 LOD400 §6) ──
    if args.c4_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

        with SessionFactory() as session:
            _run_c4_ingestion(session)
            enrich_summary = run_enrichment(session, dry_run=False)
            logger.info("Enrichment: %s", enrich_summary)
            session.commit()
        return

    # ── C1-only fast path (WP-C1 LOD400 §7) ──
    if args.c1_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

        with SessionFactory() as session:
            _run_c1_ingestion(session)
            enrich_summary = run_enrichment(session, dry_run=False)
            logger.info("Enrichment: %s", enrich_summary)
            session.commit()
        return

    # ── C2-only fast path (WP-C2 LOD400 §6) ──
    if args.c2_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401

        with SessionFactory() as session:
            _run_c2_ingestion(session)
            session.commit()
        return

    # ── C3-only fast path (WP-C3) ──
    if args.c3_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

        with SessionFactory() as session:
            _run_c3_ingestion(session)
            enrich_summary = run_enrichment(session, dry_run=False)
            logger.info("Enrichment: %s", enrich_summary)
            session.commit()
        return

    # ── WD-only fast path (WP-D: Cursor 16-crop web research batches) ──
    if args.wd_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.crop_book.importer.ni.cursor_crop_expansion import ingest as _wd_ingest

        with SessionFactory() as session:
            summary = _wd_ingest(session)
            enrich_summary = run_enrichment(session, dry_run=False)
            logger.info("Enrichment: %s", enrich_summary)
            session.commit()
        logger.info("WP-D complete: %s", summary)
        return

    # ── OpenAI-only fast path (WP-E: university-extension research, 24 crops) ──
    if args.openai_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.crop_book.importer.ni.openai_tier1_research import ingest as _openai_ingest

        with SessionFactory() as session:
            summary = _openai_ingest(session)
            session.commit()
        logger.info("WP-E complete: %s", summary)
        return

    # ── Gemini-only fast path (WP-H: Gemini IL research, 20 crops) ──
    if args.gemini_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.crop_book.importer.ni.gemini_il_research import ingest as _gemini_ingest

        with SessionFactory() as session:
            summary = _gemini_ingest(session)
            session.commit()
        logger.info("WP-H complete: %s", summary)
        return

    # ── Calendar-only fast path (WP-G: Israeli planting calendar L01+L36) ──
    if args.calendar_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.crop_book.importer.ni.planting_calendar import ingest as _cal_ingest

        with SessionFactory() as session:
            summary = _cal_ingest(session)
            session.commit()
        logger.info("WP-G complete: %s", summary)
        return

    # ── Idan-only fast path (WP-F: Israeli operator farm planning L03/L04/L49) ──
    if args.idan_only:
        from organic_market_agent.db.session import SessionFactory
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.crop_book.importer.ni.idan_planner import ingest as _idan_ingest

        with SessionFactory() as session:
            summary = _idan_ingest(session)
            session.commit()
        logger.info("WP-F complete: %s", summary)
        return

    # ── NI-only fast path (AC-13): runs BEFORE any JMF/Tend/Tend-overlay work ──
    if args.ni_only:
        if args.dry_run:
            logger.info("DRY RUN — no DB writes")
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from organic_market_agent.crop_book.models import Base
            from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
            from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401

            engine = create_engine("sqlite:///:memory:")
            Base.metadata.create_all(engine)
            from sqlalchemy import inspect as sa_inspect
            if "crop_task_templates" not in sa_inspect(engine).get_table_names():
                CropTaskTemplate.__table__.create(engine, checkfirst=True)
            SessionLocal = sessionmaker(engine)
            with SessionLocal() as session:
                _run_ni_ingestion(session)
        else:
            from organic_market_agent.db.session import SessionFactory
            with SessionFactory() as session:
                _run_ni_ingestion(session)
                session.commit()
        return

    if args.dry_run:
        logger.info("DRY RUN — no DB writes")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from organic_market_agent.crop_book.models import Base
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401 — resolve lazy CropFieldEnrichment relationship
        from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        # Also create crop_task_templates (not in Base.metadata via models.py)
        from sqlalchemy import inspect as sa_inspect
        if "crop_task_templates" not in sa_inspect(engine).get_table_names():
            CropTaskTemplate.__table__.create(engine, checkfirst=True)
        SessionLocal = sessionmaker(engine)
        with SessionLocal() as session:
            # JMF MasterClass ingestion (LOD400 §8.2)
            if not args.no_jmf:
                from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
                jmf_summary = import_jmf_masterclass(
                    session, args.jmf_masterclass_dir, dry_run=True,
                )
                logger.info("JMF MasterClass: %s", jmf_summary)
                if jmf_summary.map_misses:
                    logger.warning("JMF map misses (%d): %s",
                                   len(jmf_summary.map_misses),
                                   ", ".join(jmf_summary.map_misses[:10]))
                if jmf_summary.standalone_divergences:
                    logger.warning("JMF standalone divergences (%d) — master wins",
                                   len(jmf_summary.standalone_divergences))
            if args.jmf_only:
                if args.all and not args.no_enrich:
                    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
                    enrich_summary = run_enrichment(session, dry_run=True)
                    logger.info("Enrichment: %s", enrich_summary)
                return
            seed(
                session=session,
                target_crops=target_crops,
                dry_run=True,
                year_filter=args.year,
                source_dir=args.source_dir,
                jmf_dir=args.jmf_dir,
            )

            # Tend overlay ingestion (dry-run path)
            if not args.no_tend_overlay:
                from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay
                tend_summary = import_tend_overlay(
                    session, args.tend_overlay_dir, year=args.tend_overlay_year,
                    dry_run=True,
                )
                logger.info("Tend overlay: %s", tend_summary)
                if tend_summary.crop_map_misses:
                    logger.warning("Tend overlay crop_map misses (%d): %s",
                                   len(tend_summary.crop_map_misses),
                                   ", ".join(tend_summary.crop_map_misses[:10]))
                session.flush()

            if args.tend_overlay_only:
                return

            # NI ingestion runs LAST (hard-override precedence) — single call-site via helper
            if not args.no_ni:
                _run_ni_ingestion(session)
        return

    from organic_market_agent.db.session import SessionFactory

    with SessionFactory() as session:
        # JMF MasterClass ingestion BEFORE Tend (LOD400 §8.2)
        if not args.no_jmf:
            from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
            jmf_summary = import_jmf_masterclass(
                session, args.jmf_masterclass_dir, dry_run=False,
            )
            logger.info("JMF MasterClass: %s", jmf_summary)
            if jmf_summary.map_misses:
                logger.warning("JMF map misses (%d): %s",
                               len(jmf_summary.map_misses),
                               ", ".join(jmf_summary.map_misses[:10]))
            if jmf_summary.standalone_divergences:
                logger.warning("JMF standalone divergences (%d) — master wins",
                               len(jmf_summary.standalone_divergences))
            session.flush()

        if args.jmf_only:
            if args.all and not args.no_enrich:
                from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
                enrich_summary = run_enrichment(session, dry_run=False)
                logger.info("Enrichment: %s", enrich_summary)
            session.commit()
            return

        # Tend overlay ingestion (AFTER JMF, BEFORE WP-A Tend raw-material import)
        if not args.no_tend_overlay:
            from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay
            tend_summary = import_tend_overlay(
                session, args.tend_overlay_dir, year=args.tend_overlay_year,
                dry_run=False,
            )
            logger.info("Tend overlay: %s", tend_summary)
            if tend_summary.crop_map_misses:
                logger.warning("Tend overlay crop_map misses (%d): %s",
                               len(tend_summary.crop_map_misses),
                               ", ".join(tend_summary.crop_map_misses[:10]))
            session.flush()

        if args.tend_overlay_only:
            # Early return — skip remaining importers
            session.commit()
            return

        if args.all and not args.no_c1:
            _run_c1_ingestion(session)
            session.flush()

        if args.all and not args.no_c4:
            _run_c4_ingestion(session)
            session.flush()

        if args.all and not args.no_c2:
            _run_c2_ingestion(session)
            session.flush()

        if args.all and not args.no_c3:
            _run_c3_ingestion(session)
            session.flush()

        if args.all and not getattr(args, "no_wd", False):
            from organic_market_agent.crop_book.importer.ni.cursor_crop_expansion import (
                ingest as _wd_ingest,
            )
            _wd_ingest(session)
            session.flush()

        if args.all and not getattr(args, "no_openai", False):
            from organic_market_agent.crop_book.importer.ni.openai_tier1_research import (
                ingest as _openai_ingest,
            )
            _openai_ingest(session)
            session.flush()

        if args.all and not getattr(args, "no_idan", False):
            from organic_market_agent.crop_book.importer.ni.idan_planner import (
                ingest as _idan_ingest,
            )
            _idan_ingest(session)
            session.flush()

        if args.all and not getattr(args, "no_calendar", False):
            from organic_market_agent.crop_book.importer.ni.planting_calendar import (
                ingest as _cal_ingest,
            )
            _cal_ingest(session)
            session.flush()

        if args.all and not getattr(args, "no_gemini", False):
            from organic_market_agent.crop_book.importer.ni.gemini_il_research import (
                ingest as _gemini_ingest,
            )
            _gemini_ingest(session)
            session.flush()

        # Existing Tend seed call (unchanged logic)
        seed(
            session=session,
            target_crops=target_crops,
            dry_run=False,
            year_filter=args.year,
            source_dir=args.source_dir,
            jmf_dir=args.jmf_dir,
        )
        # LOD400 §13: --all automatically enriches unless --no-enrich is passed.
        if args.all and not args.no_enrich:
            from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
            logger.info("Running enrichment_runner after --all seed (pass --no-enrich to skip)...")
            summary = run_enrichment(session, dry_run=False)
            logger.info("Enrichment: %s", summary)
            session.commit()

        # NI ingestion runs LAST (hard-override wins precedence) — single call-site via helper
        if not args.no_ni:
            _run_ni_ingestion(session)
            session.commit()


if __name__ == "__main__":
    main()
