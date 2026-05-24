"""Idempotency tests for import_jmf_masterclass (AC-07a, AC-07b). SFA-S003-P002-WP-B1."""
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book

FIXTURE = Path(__file__).parent / "fixtures" / "jmf" / "minimal_masterclass.xlsx"


@pytest.fixture(scope="module")
def idempotency_session():
    """Clean SQLite in-memory session for idempotency tests + pre-seeded crops."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.db.base import Base
    from organic_market_agent.crop_book import models as _m  # noqa: F401
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401
    from organic_market_agent.crop_book.models import CropFamily, Crop

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)

    SessionFactory = sessionmaker(engine)
    # Pre-seed family + fixture crops
    with SessionFactory() as session:
        fam = CropFamily(scientific_name="Apiaceae", name_he="סלריים")
        session.add(fam)
        session.flush()
        for name_he in ["ארוגולה", "גזר", "בזיל"]:
            if not session.query(Crop).filter_by(name_he=name_he).first():
                session.add(Crop(name_he=name_he, category="vegetables", family_id=fam.id))
        session.commit()
    return SessionFactory, engine


def test_ac07a_idempotent_row_counts(idempotency_session):
    """AC-07a: running import twice produces same row count in both tables."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
    from organic_market_agent.crop_book.models import CropVarietySourceValue
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate
    SessionFactory, engine = idempotency_session

    with SessionFactory() as session:
        summary1 = import_jmf_masterclass(session, FIXTURE.parent)
        session.flush()
        sv_count_1 = session.query(CropVarietySourceValue).filter_by(source="JMF").count()
        tt_count_1 = session.query(CropTaskTemplate).filter_by(source="JMF").count()

        # Second import — same session (simulates re-import with same data)
        summary2 = import_jmf_masterclass(session, FIXTURE.parent)
        session.flush()
        sv_count_2 = session.query(CropVarietySourceValue).filter_by(source="JMF").count()
        tt_count_2 = session.query(CropTaskTemplate).filter_by(source="JMF").count()

        assert sv_count_1 == sv_count_2, (
            f"source_values count changed on re-import: {sv_count_1} → {sv_count_2}"
        )
        assert tt_count_1 == tt_count_2, (
            f"task_templates count changed on re-import: {tt_count_1} → {tt_count_2}"
        )


def test_ac07b_no_integrity_error_on_reimport(idempotency_session):
    """AC-07b: no IntegrityError on re-import (upsert is safe)."""
    from sqlalchemy.exc import IntegrityError
    from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
    SessionFactory, engine = idempotency_session

    with SessionFactory() as session:
        try:
            import_jmf_masterclass(session, FIXTURE.parent)
            session.flush()
            import_jmf_masterclass(session, FIXTURE.parent)
            session.flush()
        except IntegrityError as e:
            pytest.fail(f"IntegrityError on re-import: {e}")
