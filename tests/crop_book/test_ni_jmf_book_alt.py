"""Tests for JmfBookAltImporter — AC-09 for alt edition (Q5).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_book_alt")


@pytest.fixture
def full_session_alt():
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
        family = CropFamily(scientific_name="Brassicaceae_ba", name_he="מצליבים_ba")
        session.add(family)
        session.flush()
        for name_he in ["ארוגולה", "תרד"]:
            session.add(Crop(name_he=name_he, family_id=family.id, category='vegetables'))
        session.commit()

    with SessionLocal() as session:
        yield session


class TestJmfBookAltImporter:
    """AC-09: JmfBookAltImporter loads knowledge notes from fixture caches."""

    def test_ac09_alt_edition_load_knowledge_notes(self, full_session_alt):
        from organic_market_agent.crop_book.importer.ni.jmf_book_alt import JmfBookAltImporter

        imp = JmfBookAltImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load_knowledge_notes(full_session_alt)
        assert len(rows) >= 2, f"Expected >= 2 rows from 2 fixture files, got {len(rows)}"
        for row in rows:
            assert row["source"] == "NI:jmf_book_alt_v1"
            assert row["is_internal_farm_use_only"] is True

    def test_alt_edition_source_label_differs_from_main(self):
        from organic_market_agent.crop_book.importer.ni.jmf_book_alt import JmfBookAltImporter
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        assert JmfBookAltImporter().source_label != JmfBookImporter().source_label
        assert JmfBookAltImporter().source_label == "NI:jmf_book_alt_v1"
