"""WP-C4 integration tests — seed --c4-only + enrichment fields."""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.crop_book


@pytest.fixture
def crop_book_session():
    from organic_market_agent.crop_book.models import Base, Crop, CropFamily
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.planting_calendar import CropPlantingCalendar
    from organic_market_agent.crop_book.companion_matrix import CropCompanionMatrix
    from organic_market_agent.crop_book.postharvest_storage import CropPostharvestStorage
    from organic_market_agent.crop_book.models import CropVariety, CropVarietySourceValue

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropPlantingCalendar.__table__.create(engine, checkfirst=True)
    CropCompanionMatrix.__table__.create(engine, checkfirst=True)
    CropPostharvestStorage.__table__.create(engine, checkfirst=True)
    Session = sessionmaker(engine)
    with Session() as session:
        fam = CropFamily(scientific_name="Solanaceae", name_he="סולניים")
        session.add(fam)
        session.flush()
        for name_he, sci in [
            ("עגבנייה", "Solanum lycopersicum"),
            ("חסה", "Lactuca sativa"),
            ("גזר", "Daucus carota"),
            ("בזיל", "Ocimum basilicum"),
            ("פלפל", "Capsicum annuum"),
        ]:
            session.add(Crop(
                name_he=name_he, name_en=None, scientific_name=sci,
                family_id=fam.id, category="vegetables",
            ))
        session.commit()
        yield session


class TestC4Integration:
    def test_c4_ingestion_populates_tables(self, crop_book_session):
        from organic_market_agent.crop_book.importer.seed import _run_c4_ingestion

        _run_c4_ingestion(crop_book_session)
        crop_book_session.commit()

        cal = crop_book_session.execute(
            text(
                "SELECT COUNT(*) FROM crop_planting_calendar "
                "WHERE source LIKE 'NI:il_%' OR source = 'NI:shaham_extension'"
            )
        ).scalar()
        assert cal >= 1

        companions = crop_book_session.execute(
            text("SELECT COUNT(*) FROM crop_companion_matrix")
        ).scalar()
        assert companions >= 1

    def test_enrichment_picks_up_germination_field(self, crop_book_session):
        from organic_market_agent.crop_book.importer.seed import _run_c4_ingestion
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
        from organic_market_agent.crop_book.models import CropVarietySourceValue

        _run_c4_ingestion(crop_book_session)
        crop_book_session.commit()

        n_sv = crop_book_session.query(CropVarietySourceValue).filter(
            CropVarietySourceValue.source == "PR:uc_anr_germination"
        ).count()
        assert n_sv >= 1

        summary = run_enrichment(crop_book_session, dry_run=False)
        assert summary.field_count >= 1
