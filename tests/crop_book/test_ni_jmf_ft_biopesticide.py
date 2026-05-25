"""Tests for JmfFtBiopesticideImporter — AC-09 for biopesticide source.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_ft_biopesticide")


@pytest.fixture
def full_session_bio():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, CropFamily, Crop
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
    from organic_market_agent.crop_book import enrichment_models  # noqa
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine)

    with SessionLocal() as session:
        family = CropFamily(scientific_name="Brassicaceae_bio", name_he="מצליבים_bio")
        session.add(family)
        session.flush()
        for name_he in ["קייל", "ברוקולי"]:
            session.add(Crop(name_he=name_he, family_id=family.id, category='vegetables'))
        session.commit()

    with SessionLocal() as session:
        yield session


class TestJmfFtBiopesticideImporter:
    """AC-09: load_knowledge_notes returns biopesticide_spray rows."""

    def test_ac09_biopesticide_rows(self, full_session_bio):
        from organic_market_agent.crop_book.importer.ni.jmf_ft_biopesticide import JmfFtBiopesticideImporter

        imp = JmfFtBiopesticideImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load_knowledge_notes(full_session_bio)
        assert len(rows) >= 2, f"Expected >= 2 rows (Kale + Broccoli), got {len(rows)}"
        note_types = {r["note_type"] for r in rows}
        assert "biopesticide_spray" in note_types
        for row in rows:
            assert row["source"] == "NI:jmf_ft_biopesticide_v1"
