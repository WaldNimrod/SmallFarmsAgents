"""Tests for variety→species inheritance in the reconciler engine (v1.1).

Architectural principle: a variety is an OVERRIDE on the species defaults.
When (variety, field) has no own data, candidates are inherited from the
default variety of the same crop.

Tests use an in-memory SQLite DB with the minimal schema slices needed
(crops, crop_varieties, crop_variety_source_values).
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from organic_market_agent.crop_book.importer.reconciler import (
    collect_source_values_with_inheritance,
)
from organic_market_agent.crop_book.models import (
    Base,
    Crop,
    CropFamily,
    CropVariety,
    CropVarietySourceValue,
)
# Import enrichment_models so SQLAlchemy can resolve CropVariety.enrichments relationship
import organic_market_agent.crop_book.enrichment_models  # noqa: F401

pytestmark = pytest.mark.crop_book


@pytest.fixture
def session():
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False)
    with SessionLocal() as s:
        # Seed minimal: family + crop + 2 varieties (default + non-default)
        fam = CropFamily(scientific_name="Brassicaceae", name_he="מצליבים")
        s.add(fam)
        s.flush()
        crop = Crop(name_he="ארוגולה_test", name_en="Arugula", family_id=fam.id, category="vegetables")
        s.add(crop)
        s.flush()
        v_default = CropVariety(crop_id=crop.id, name_en=None, is_default=True)
        v_specific = CropVariety(crop_id=crop.id, name_en="Wild Rocket", is_default=False)
        s.add_all([v_default, v_specific])
        s.flush()
        # Default variety has Tend DTM=21
        s.add(CropVarietySourceValue(
            variety_id=v_default.id, field_name="days_to_maturity",
            source="Tend", value_text="21", value_numeric=21,
            unit="days", trust_tier="OP", confidence_weight=0.55,
        ))
        # Specific variety has only EX team_00 DTM=21 (no other source)
        s.add(CropVarietySourceValue(
            variety_id=v_specific.id, field_name="days_to_maturity",
            source="team_00", value_text="21", value_numeric=21,
            unit="days", trust_tier="EX", confidence_weight=None,
        ))
        s.commit()
        # Expose ids for tests
        s._test_default_id = v_default.id
        s._test_specific_id = v_specific.id
        yield s


def test_specific_variety_inherits_from_default_when_field_empty(session):
    """Specific variety has no own DTM data (EX excluded) → inherits from default."""
    rows = collect_source_values_with_inheritance(
        session, session._test_specific_id, field_name="days_to_maturity", exclude_ex=True
    )
    assert len(rows) == 1
    assert rows[0].variety_id == session._test_default_id  # inherited!
    assert rows[0].source == "Tend"
    assert rows[0].value_numeric == 21


def test_specific_variety_uses_own_data_when_present(session):
    """Specific variety with its own non-EX data does NOT fall back."""
    # Add OP data to specific variety
    session.add(CropVarietySourceValue(
        variety_id=session._test_specific_id, field_name="days_to_maturity",
        source="OP:Idan_2017", value_text="22", value_numeric=22,
        unit="days", trust_tier="OP", confidence_weight=0.55,
    ))
    session.commit()

    rows = collect_source_values_with_inheritance(
        session, session._test_specific_id, field_name="days_to_maturity", exclude_ex=True
    )
    assert len(rows) == 1
    assert rows[0].variety_id == session._test_specific_id  # own, NOT inherited
    assert rows[0].source == "OP:Idan_2017"
    assert rows[0].value_numeric == 22


def test_default_variety_does_not_inherit_from_itself(session):
    """Default variety has no fallback (no self-loop)."""
    rows = collect_source_values_with_inheritance(
        session, session._test_default_id, field_name="days_to_maturity", exclude_ex=True
    )
    # Only its own row
    assert len(rows) == 1
    assert rows[0].variety_id == session._test_default_id


def test_field_filter_none_inherits_per_missing_field(session):
    """When field_name=None, inheritance applies per-field for fields with no own data."""
    # Specific variety also has OWN data for a different field
    session.add(CropVarietySourceValue(
        variety_id=session._test_specific_id, field_name="harvest_window_max_days",
        source="OP:Idan_2017", value_text="30", value_numeric=30,
        unit="days", trust_tier="OP", confidence_weight=0.55,
    ))
    # Default variety has DTM (already in fixture) AND a new field
    session.add(CropVarietySourceValue(
        variety_id=session._test_default_id, field_name="documented_price",
        source="Tend", value_text="40", value_numeric=40,
        unit="ILS/bunch", trust_tier="OP", confidence_weight=0.55,
    ))
    session.commit()

    rows = collect_source_values_with_inheritance(
        session, session._test_specific_id, field_name=None, exclude_ex=True
    )
    # Should have:
    # - Own harvest_window_max_days (OP:Idan)
    # - Inherited days_to_maturity from default (Tend)
    # - Inherited documented_price from default (Tend)
    fields_per_row = sorted((r.field_name, r.variety_id == session._test_default_id) for r in rows)
    assert fields_per_row == [
        ("days_to_maturity", True),       # inherited (True = is default variety)
        ("documented_price", True),        # inherited
        ("harvest_window_max_days", False),  # own (False = NOT default variety)
    ]


def test_no_default_variety_returns_only_own(session):
    """If no default variety exists on the crop, only own rows returned."""
    # Mark v_default as is_default=False — so no default exists
    v_default = session.query(CropVariety).filter_by(id=session._test_default_id).first()
    v_default.is_default = False
    session.commit()

    rows = collect_source_values_with_inheritance(
        session, session._test_specific_id, field_name="days_to_maturity", exclude_ex=True
    )
    # Specific has no own non-EX data; no default to inherit from → empty
    assert rows == []


def test_inheritance_preserves_ex_when_exclude_ex_false(session):
    """When exclude_ex=False (production mode), EX rows are kept; inheritance still
    fires for FIELDS where own data is empty.

    Subtle case: specific has EX for DTM (so own data is non-empty for that field
    when exclude_ex=False). Therefore no inheritance for DTM in production.
    """
    rows = collect_source_values_with_inheritance(
        session, session._test_specific_id, field_name="days_to_maturity", exclude_ex=False
    )
    # Only own EX row; no fallback because own has data (EX)
    assert len(rows) == 1
    assert rows[0].source == "team_00"
    assert rows[0].trust_tier == "EX"
