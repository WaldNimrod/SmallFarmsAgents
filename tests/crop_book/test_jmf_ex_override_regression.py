"""AC-13: EX override regression — ARUGULA JMF DTM must NOT override team_00 EX.

SFA-S003-P002-WP-B1 LOD400 §9 AC-13. The most important regression test.

After both:
  1. WP-A baseline (team_00 EX override: ARUGULA DTM = 21)
  2. JMF MasterClass import (ARUGULA DTM ≈ 30 from fixture)

The crop_field_enrichment row for ARUGULA / days_to_maturity MUST have:
  value_best == Decimal("21")
  winning_source_class == "EX"

This proves WP-A engine reuse is correctly wired — the JMF PR value (0.70)
cannot displace a team_00 EX hard override.
"""
import pytest
from decimal import Decimal
from pathlib import Path

pytestmark = pytest.mark.crop_book

FIXTURE = Path(__file__).parent / "fixtures" / "jmf" / "minimal_masterclass.xlsx"


@pytest.fixture(scope="module")
def ex_regression_session():
    """In-memory SQLite with all tables; seeds ARUGULA with EX override then JMF."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.db.base import Base
    from organic_market_agent.crop_book import models as _m  # noqa: F401
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    return sessionmaker(engine), engine


def test_ac13_ex_override_wins_over_jmf(ex_regression_session):
    """AC-13: After EX team_00 override (DTM=21) AND JMF import (DTM=30),
    enrichment engine yields value_best=21 and winning_source_class='EX'."""
    from organic_market_agent.crop_book.models import (
        Crop, CropVariety, CropVarietySourceValue
    )
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

    SessionFactory, engine = ex_regression_session

    with SessionFactory() as session:
        # Step 0: Need a family (family_id NOT NULL)
        from organic_market_agent.crop_book.models import CropFamily
        family = CropFamily(scientific_name="Brassicaceae", name_he="מצליבים")
        session.add(family)
        session.flush()

        # Step 1: Create ARUGULA crop + baseline variety
        arugula = Crop(name_he="ארוגולה", category="vegetables", family_id=family.id)
        session.add(arugula)
        session.flush()

        baseline_variety = CropVariety(crop_id=arugula.id, name_en=None, is_default=True)
        session.add(baseline_variety)
        session.flush()

        # Step 2: Insert team_00 EX override (DTM = 21)
        ex_sv = CropVarietySourceValue(
            variety_id=baseline_variety.id,
            field_name="days_to_maturity",
            source="team_00",
            value_numeric=Decimal("21"),
            value_text="21",
            unit="days",
            note="team_00 Israel-specific override — highest priority",
            trust_tier="EX",
            confidence_weight=None,
            is_outlier_rejected=False,
        )
        session.add(ex_sv)
        session.flush()

        # Step 3: Run JMF MasterClass import (fixture has Arugula DTM=30)
        # The fixture importer will find Arugula and upsert JMF source value
        import_jmf_masterclass(session, FIXTURE.parent)
        session.flush()

        # Step 4: Run enrichment engine
        run_enrichment(session, dry_run=False)
        session.flush()

        # Step 5: Verify AC-13
        enrichment = (
            session.query(CropFieldEnrichment)
            .filter_by(variety_id=baseline_variety.id, field_name="days_to_maturity")
            .one_or_none()
        )

        assert enrichment is not None, (
            "No crop_field_enrichment row for ARUGULA / days_to_maturity"
        )

        assert enrichment.value_best == Decimal("21"), (
            f"AC-13 FAIL: expected value_best=21 (EX override), "
            f"got {enrichment.value_best}. "
            f"JMF PR value incorrectly displaced team_00 EX override."
        )

        assert enrichment.winning_source_class == "EX", (
            f"AC-13 FAIL: expected winning_source_class='EX', "
            f"got {enrichment.winning_source_class!r}. "
            f"The JMF PR tier should never win over EX (Iron Rule — engine reuse verified)."
        )
