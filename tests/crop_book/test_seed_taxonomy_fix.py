"""Seed-pipeline taxonomy + derived-field guard tests (team_00 2026-06-10).

Proves the three fixes that stop `seed --all` from producing bad data:

  (a) The 3 non-canonical Hebrew names resolve to EXISTING canonical crops
      (no new crop is minted):
        בזיליקום (Basil)    → בזיל   (canonical)
        רוטבגה  (Rutabaga)  → לפת    (Turnips)
        תערובת סלט (Salad Mix) → עלי בייבי (Lettuce: Salad Mix)
  (b) The 5 keep-crops are created with a correct name_en + the SAME family as
      their botanical sibling (NOT the 'Unknown' placeholder family).
  (c) The post-seed strip removes all 5 forbidden DERIVED fields from BOTH
      crop_variety_source_values and crop_field_enrichment.

In-memory SQLite only — no live DB. Run with:
    .venv/bin/python -m pytest tests/crop_book/test_seed_taxonomy_fix.py -q
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.crop_book


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def Session():
    """Fresh in-memory SQLite engine with all crop-book tables created."""
    from organic_market_agent.db.base import Base
    from organic_market_agent.crop_book import models as _m  # noqa: F401
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    return sessionmaker(engine)


def _add_family(session, scientific_name: str, name_he: str | None = None):
    from organic_market_agent.crop_book.models import CropFamily
    fam = CropFamily(scientific_name=scientific_name, name_he=name_he)
    session.add(fam)
    session.flush()
    return fam


def _add_crop(session, name_he: str, family_id: int, name_en: str | None = None):
    from organic_market_agent.crop_book.models import Crop
    crop = Crop(name_he=name_he, name_en=name_en, category="vegetables", family_id=family_id)
    session.add(crop)
    session.flush()
    return crop


# ---------------------------------------------------------------------------
# (a) Duplicate names resolve to canonical crops — no new crop minted
# ---------------------------------------------------------------------------

def test_map_targets_are_canonical_names():
    """The 3 source labels now point at the canonical name_he, not the dup names."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP, TEND_CROP_MAP

    assert JMF_CROP_MAP["Basil"] == "בזיל"
    assert JMF_CROP_MAP["Rutabaga"] == "לפת"
    assert TEND_CROP_MAP["Lettuce: Salad Mix"] == "עלי בייבי"

    # The non-canonical names must NOT be targets of any name-mapping table.
    for dup in ("בזיליקום", "רוטבגה", "תערובת סלט"):
        assert dup not in JMF_CROP_MAP.values(), f"{dup!r} still a JMF_CROP_MAP target"
        assert dup not in TEND_CROP_MAP.values(), f"{dup!r} still a TEND_CROP_MAP target"


def test_il_basil_aliases_resolve_to_canonical():
    """IL_CROP_MAP basil aliases now resolve to canonical 'בזיל' (not 'בזיליקום')."""
    from organic_market_agent.crop_book.constants import resolve_il_crop

    assert resolve_il_crop("בזיליקום") == "בזיל"
    assert resolve_il_crop("בזיליקום (ריחן)") == "בזיל"
    assert resolve_il_crop("בזיל") == "בזיל"


@pytest.mark.parametrize(
    "jmf_en, canonical_he",
    [("Basil", "בזיל"), ("Rutabaga", "לפת")],
)
def test_jmf_dup_names_resolve_no_new_crop(Session, jmf_en, canonical_he):
    """When JMF processes 'Basil'/'Rutabaga', it finds the existing canonical crop
    and mints NO new crop (the dup name never becomes a row)."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    from organic_market_agent.crop_book.importer.jmf_masterclass import _create_jmf_crop
    from organic_market_agent.crop_book.models import Crop

    with Session() as session:
        fam = _add_family(session, "Lamiaceae", "שפתניים")
        # Pre-seed the canonical crop the dup name must resolve to.
        _add_crop(session, canonical_he, fam.id)
        session.commit()

        before = session.query(Crop).count()

        # Replicate jmf_masterclass resolve-then-create logic.
        name_he = JMF_CROP_MAP[jmf_en]
        assert name_he == canonical_he
        crop_obj = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop_obj is None:  # would only fire if the map were still wrong
            crop_obj = _create_jmf_crop(session, name_he)
        session.commit()

        after = session.query(Crop).count()
        assert after == before, "A new crop was minted for a dup name"
        # The dup name must NOT exist as a crop.
        dup = {"Basil": "בזיליקום", "Rutabaga": "רוטבגה"}[jmf_en]
        assert session.query(Crop).filter_by(name_he=dup).one_or_none() is None


def test_salad_mix_resolves_no_new_crop(Session):
    """TEND 'Lettuce: Salad Mix' resolves to existing 'עלי בייבי'; 'תערובת סלט' is never minted."""
    from organic_market_agent.crop_book.constants import TEND_CROP_MAP
    from organic_market_agent.crop_book.importer.seed import _get_or_create_crop
    from organic_market_agent.crop_book.models import Crop

    with Session() as session:
        fam = _add_family(session, "Asteraceae", "מורכבים")
        _add_crop(session, "עלי בייבי", fam.id, name_en="Lettuce: Salad Mix")
        session.commit()

        before = session.query(Crop).count()
        name_he = TEND_CROP_MAP["Lettuce: Salad Mix"]
        assert name_he == "עלי בייבי"
        _get_or_create_crop(session, name_he, {"family_id": fam.id, "category": "baby"})
        session.commit()

        assert session.query(Crop).count() == before
        assert session.query(Crop).filter_by(name_he="תערובת סלט").one_or_none() is None


# ---------------------------------------------------------------------------
# (b) Keep-crops created with correct name_en + sibling family
# ---------------------------------------------------------------------------

_KEEP_CASES = [
    ("סלרי שורש", "Celeriac", "סלרי", "Apiaceae"),
    ("כרוב סיני", "Chinese Cabbage", "כרוב", "Brassicaceae"),
    ("פלפל חריף", "Hot Pepper", "פלפל", "Solanaceae"),
    ("עגבניות מורשת", "Heirloom Tomato", "עגבנייה", "Solanaceae"),
    ("כרוב ניצנים", "Brussels Sprouts", "כרוב", "Brassicaceae"),
]


@pytest.mark.parametrize("name_he, name_en, sibling_he, family_sci", _KEEP_CASES)
def test_keep_crop_uses_sibling_family_when_present(
    Session, name_he, name_en, sibling_he, family_sci
):
    """When the botanical sibling already exists, the keep-crop reuses ITS family
    and gets the correct name_en — never the 'Unknown' placeholder."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import _create_jmf_crop
    from organic_market_agent.crop_book.models import CropFamily

    with Session() as session:
        sibling_fam = _add_family(session, family_sci)
        _add_crop(session, sibling_he, sibling_fam.id)
        session.commit()

        crop = _create_jmf_crop(session, name_he)
        session.commit()

        assert crop.name_en == name_en
        assert crop.family_id == sibling_fam.id
        # Family must NOT be the 'Unknown' placeholder.
        fam = session.query(CropFamily).filter_by(id=crop.family_id).one()
        assert fam.scientific_name == family_sci
        assert fam.scientific_name != "Unknown"


@pytest.mark.parametrize("name_he, name_en, sibling_he, family_sci", _KEEP_CASES)
def test_keep_crop_falls_back_to_botanical_family_when_sibling_absent(
    Session, name_he, name_en, sibling_he, family_sci
):
    """JMF runs before Tend seed in --all, so the sibling crop may not exist yet.
    The keep-crop must still get the correct botanical family (created if needed),
    never the 'Unknown' placeholder."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import _create_jmf_crop
    from organic_market_agent.crop_book.models import CropFamily

    with Session() as session:
        # No sibling crop and no pre-existing family.
        crop = _create_jmf_crop(session, name_he)
        session.commit()

        assert crop.name_en == name_en
        fam = session.query(CropFamily).filter_by(id=crop.family_id).one()
        assert fam.scientific_name == family_sci
        assert fam.scientific_name != "Unknown"


def test_unmapped_crop_still_uses_placeholder_family(Session):
    """An unmapped JMF crop (not a keep-crop) still falls back to 'Unknown' —
    behaviour for the existing crops is unchanged."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import _create_jmf_crop
    from organic_market_agent.crop_book.models import CropFamily

    with Session() as session:
        crop = _create_jmf_crop(session, "צמח לא ממופה")
        session.commit()
        assert crop.name_en is None
        fam = session.query(CropFamily).filter_by(id=crop.family_id).one()
        assert fam.scientific_name == "Unknown"


# ---------------------------------------------------------------------------
# (c) Derived-field strip removes all 5 forbidden fields from BOTH tables
# ---------------------------------------------------------------------------

_DERIVED = [
    "yield_per_m2_kg",
    "nutrient_removal_p2o5_kg_ha",
    "nutrient_removal_k2o_kg_ha",
    "plants_per_m2",
    "avg_revenue_per_bed_m",
]


def test_strip_derived_fields_removes_all_five_from_both_tables(Session):
    from organic_market_agent.crop_book.importer.seed import strip_derived_fields
    from organic_market_agent.crop_book.models import (
        Crop,
        CropFamily,
        CropVariety,
        CropVarietySourceValue,
    )
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment

    with Session() as session:
        fam = _add_family(session, "Solanaceae")
        crop = _add_crop(session, "עגבנייה", fam.id)
        variety = CropVariety(crop_id=crop.id, is_default=True)
        session.add(variety)
        session.flush()

        # Seed one forbidden row per field in BOTH tables, plus a KEEP row.
        for fld in _DERIVED:
            session.add(CropVarietySourceValue(
                variety_id=variety.id, field_name=fld, source="idan_planner",
                value_numeric=Decimal("1.0"),
            ))
            session.add(CropFieldEnrichment(
                variety_id=variety.id, field_name=fld, value_best=Decimal("1.0"),
                source_count=1,
            ))
        # A legitimate (non-derived) field that must SURVIVE the strip.
        session.add(CropVarietySourceValue(
            variety_id=variety.id, field_name="days_to_maturity", source="JMF",
            value_numeric=Decimal("55"),
        ))
        session.add(CropFieldEnrichment(
            variety_id=variety.id, field_name="days_to_maturity",
            value_best=Decimal("55"), source_count=1,
        ))
        session.commit()

        result = strip_derived_fields(session)
        session.commit()

        # All 5 forbidden fields gone from BOTH tables.
        for fld in _DERIVED:
            sv = session.execute(
                text("SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"),
                {"fn": fld},
            ).scalar()
            en = session.execute(
                text("SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"),
                {"fn": fld},
            ).scalar()
            assert sv == 0, f"{fld} still in source_values"
            assert en == 0, f"{fld} still in enrichment"
            assert result["source_values"][fld] == 1
            assert result["enrichment"][fld] == 1

        # The legitimate field survived.
        assert session.execute(
            text("SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = 'days_to_maturity'")
        ).scalar() == 1
        assert session.execute(
            text("SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = 'days_to_maturity'")
        ).scalar() == 1


def test_strip_derived_fields_is_idempotent(Session):
    """A second strip on a clean DB deletes nothing and does not error."""
    from organic_market_agent.crop_book.importer.seed import strip_derived_fields

    with Session() as session:
        result = strip_derived_fields(session)
        session.commit()
        assert all(v == 0 for v in result["source_values"].values())
        assert all(v == 0 for v in result["enrichment"].values())
