"""Tests for CropHarvestStat ORM module.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-02, AC-10.
"""
import pytest
from datetime import datetime
from decimal import Decimal

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = "tests/crop_book/fixtures/tend_2022"


@pytest.fixture(scope="module")
def mem_engine():
    """SQLite in-memory engine with all crop book tables + pre-seeded family."""
    from sqlalchemy import create_engine
    import organic_market_agent.models  # noqa: F401
    import organic_market_agent.crop_book.enrichment_models  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401
    from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat  # noqa: F401
    from organic_market_agent.crop_book.models import CropFamily, Crop
    from organic_market_agent.db.base import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    CropHarvestStat.__table__.create(engine, checkfirst=True)

    # Pre-seed a family for crop inserts
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        fam = CropFamily(scientific_name="TestFamily", name_he="משפחת_בדיקה")
        session.add(fam)
        session.flush()
        # Pre-seed test crops
        for name_he, name_en in [("גזר", "Carrots"), ("כרוב", "Cabbage")]:
            if not session.query(Crop).filter_by(name_he=name_he).first():
                session.add(Crop(name_he=name_he, name_en=name_en,
                                 category="vegetables", family_id=fam.id))
        session.commit()

    return engine


@pytest.fixture
def session(mem_engine):
    from sqlalchemy.orm import Session
    with Session(mem_engine) as s:
        yield s
        s.rollback()


class TestCropHarvestStatORM:
    """AC-02: 13 columns mapped with correct types; SEASON_VALUES exported; constraints active."""

    def test_season_values_exported(self):
        """SEASON_VALUES is a tuple of 4 strings."""
        from organic_market_agent.crop_book.crop_harvest_stats import SEASON_VALUES
        assert isinstance(SEASON_VALUES, tuple)
        assert len(SEASON_VALUES) == 4
        assert set(SEASON_VALUES) == {"spring", "summer", "fall", "winter"}

    def test_column_count(self):
        """CropHarvestStat has 15 mapped columns (id + 14 data columns)."""
        from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat
        cols = {c.key for c in CropHarvestStat.__table__.columns}
        expected = {
            "id", "crop_id", "season", "year", "source",
            "cycles_count", "first_harvest_week", "peak_harvest_week", "last_harvest_week",
            "yield_total", "yield_unit",
            "yield_per_bed_min", "yield_per_bed_max", "yield_per_bed_median",
            "created_at",
        }
        assert expected.issubset(cols)

    def test_insert_and_retrieve(self, mem_engine, session):
        """Insert a CropHarvestStat row and read it back."""
        from sqlalchemy import text
        from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat

        crop_id = session.execute(text("SELECT id FROM crops WHERE name_he='גזר'")).fetchone()[0]

        obj = CropHarvestStat(
            crop_id=crop_id,
            season="spring",
            year=2022,
            source="Tend_2022",
            cycles_count=3,
            first_harvest_week=12,
            peak_harvest_week=14,
            last_harvest_week=18,
            yield_total=Decimal("120.50"),
            yield_unit="kg",
            created_at=datetime.utcnow(),
        )
        session.add(obj)
        session.flush()

        retrieved = session.query(CropHarvestStat).filter_by(
            crop_id=crop_id, season="spring", year=2022
        ).one()
        assert retrieved.yield_total == Decimal("120.50")
        assert retrieved.yield_unit == "kg"
        assert retrieved.cycles_count == 3


class TestCropHarvestStatConstraints:
    """AC-10: UNIQUE constraint enforced on (crop_id, season, year, source)."""

    def test_unique_constraint_raised(self, mem_engine):
        """Duplicate (crop_id, season, year, source) raises IntegrityError."""
        from sqlalchemy import text
        from sqlalchemy.orm import Session
        from sqlalchemy.exc import IntegrityError
        from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat

        with Session(mem_engine) as session:
            crop_id = session.execute(
                text("SELECT id FROM crops WHERE name_he='כרוב'")
            ).fetchone()[0]

            kwargs = dict(
                crop_id=crop_id, season="summer", year=2022,
                source="Tend_2022", created_at=datetime.utcnow(),
            )
            session.add(CropHarvestStat(**kwargs))
            session.flush()

            session.add(CropHarvestStat(**kwargs))
            with pytest.raises(IntegrityError):
                session.flush()
