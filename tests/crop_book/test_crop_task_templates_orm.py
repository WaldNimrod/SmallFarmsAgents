"""Tests for CropTaskTemplate ORM module (AC-02, AC-16b). SFA-S003-P002-WP-B1."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.crop_book


@pytest.fixture(scope="module")
def sqlite_session():
    """SQLite in-memory session with crop_task_templates table."""
    from organic_market_agent.db.base import Base
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401
    from organic_market_agent.crop_book.models import Crop  # noqa: F401 — need crops table for FK
    from organic_market_agent.crop_book import enrichment_models  # noqa: F401 — resolve lazy relationship

    engine = create_engine("sqlite:///:memory:")
    # Create crops table first (FK dependency)
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    Session = sessionmaker(engine)
    with Session() as session:
        yield session, engine


def test_crop_task_template_import():
    """AC-02: CropTaskTemplate imports cleanly."""
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate
    assert CropTaskTemplate.__tablename__ == "crop_task_templates"


def test_task_type_values_exported():
    """AC-02 / AC-03: TASK_TYPE_VALUES exported with 20 entries (14 B1 baseline + 6 B3 extensions
    per GCR-B3-1, team_00 approved 2026-05-25). B1 baseline values still present at indices 0-13.
    """
    from organic_market_agent.crop_book.crop_task_templates import TASK_TYPE_VALUES
    assert len(TASK_TYPE_VALUES) == 20, (
        f"Expected 20 entries (14 B1 + 6 B3 GCR-B3-1), got {len(TASK_TYPE_VALUES)}"
    )
    # B1 baseline still present
    assert "stale_seed_bed" in TASK_TYPE_VALUES
    assert "net_row_cover" in TASK_TYPE_VALUES
    # B3 extensions present
    assert "nursery_seed" in TASK_TYPE_VALUES
    assert "trellis" in TASK_TYPE_VALUES
    assert "fertilize" in TASK_TYPE_VALUES


def test_timing_anchor_values_exported():
    """AC-02: TIMING_ANCHOR_VALUES exported with 4 entries."""
    from organic_market_agent.crop_book.crop_task_templates import TIMING_ANCHOR_VALUES
    assert len(TIMING_ANCHOR_VALUES) == 4
    assert "seeding" in TIMING_ANCHOR_VALUES
    assert "field_prep" in TIMING_ANCHOR_VALUES


def test_days_offset_presence_only_value():
    """AC-02: DAYS_OFFSET_PRESENCE_ONLY = -32768."""
    from organic_market_agent.crop_book.crop_task_templates import DAYS_OFFSET_PRESENCE_ONLY
    assert DAYS_OFFSET_PRESENCE_ONLY == -32768


def test_is_presence_only_sentinel():
    """AC-02: is_presence_only(DAYS_OFFSET_PRESENCE_ONLY) is True."""
    from organic_market_agent.crop_book.crop_task_templates import (
        is_presence_only, DAYS_OFFSET_PRESENCE_ONLY
    )
    assert is_presence_only(DAYS_OFFSET_PRESENCE_ONLY) is True
    assert is_presence_only(0) is False
    assert is_presence_only(-7) is False


def test_column_count():
    """AC-02: CropTaskTemplate has 13 mapped columns."""
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate
    from sqlalchemy import inspect
    # Count mapper columns
    mapper = CropTaskTemplate.__mapper__
    col_names = [c.key for c in mapper.mapper.column_attrs]
    assert len(col_names) == 13, f"Expected 13 columns, got {len(col_names)}: {col_names}"


def test_days_offset_not_null_orm_level(sqlite_session):
    """AC-16b: explicit NULL days_offset fails NOT NULL at DB level.

    At the SQL level, INSERT ... days_offset=NULL must raise IntegrityError
    on both SQLite and Postgres. SQLAlchemy server_default fills in -32768
    when the column is omitted, but explicit NULL bypasses the default and
    hits the NOT NULL constraint (LOD400 §9 AC-16b).
    """
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    from organic_market_agent.crop_book.models import Crop, CropFamily

    session, engine = sqlite_session
    # Need a family + crop first
    family = session.query(CropFamily).filter_by(scientific_name="Testaceae").first()
    if family is None:
        family = CropFamily(scientific_name="Testaceae", name_he="בדיקה")
        session.add(family)
        session.flush()

    crop = session.query(Crop).filter_by(name_he="test_orm_16b").first()
    if crop is None:
        crop = Crop(name_he="test_orm_16b", category="vegetables", family_id=family.id)
        session.add(crop)
        session.flush()
    session.flush()

    # Use raw SQL with explicit NULL to prove DB-level NOT NULL is enforced
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO crop_task_templates"
                "(crop_id, source, trust_tier, task_type, days_offset)"
                " VALUES (:cid, 'JMF', 'PR', 'hoe', NULL)"
            ),
            {"cid": crop.id},
        )
        session.flush()
    session.rollback()
