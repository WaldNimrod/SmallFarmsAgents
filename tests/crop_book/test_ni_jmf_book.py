"""Tests for JmfBookImporter — AC-07 + AC-09 + AC-12 groundwork.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_book")


@pytest.fixture
def full_session_with_crops():
    """Full ORM session with crops for Arugula, Lettuce, Kale."""
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
        family = CropFamily(scientific_name="Brassicaceae_b", name_he="מצליבים_b")
        session.add(family)
        session.flush()
        for name_he in ["ארוגולה", "חסה", "קייל"]:
            session.add(Crop(name_he=name_he, family_id=family.id, category='vegetables'))
        session.commit()

    with SessionLocal() as session:
        yield session


class TestJmfBookImporter:
    """AC-07: JmfBookImporter extends NIImporter correctly."""

    def test_ac07_isinstance_ni_importer(self):
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter
        from organic_market_agent.crop_book.importer.ni_importer import NIImporter

        imp = JmfBookImporter()
        assert isinstance(imp, NIImporter)

    def test_ac07_name_attribute(self):
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        assert imp.name == "jmf_book_v1"

    def test_ac07_source_label(self):
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        assert imp.source_label == "NI:jmf_book_v1"

    def test_ac09_load_knowledge_notes_from_fixtures(self, full_session_with_crops):
        """AC-09: load_knowledge_notes() returns >=6 rows from 3 fixture crops."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load_knowledge_notes(full_session_with_crops)
        assert len(rows) >= 6, f"Expected >= 6 rows from 3 fixture files, got {len(rows)}"
        for row in rows:
            assert "crop_id" in row
            assert row["trust_tier"] == "NI"
            assert row["is_internal_farm_use_only"] is True
            assert len(row["body_text"]) <= 2000

    def test_ac09_load_returns_cultivar_recommendation_rows(self, full_session_with_crops):
        """AC-09/AC-12: load() returns variety-source-value rows for cultivar_recommendation."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load(full_session_with_crops)
        # All 3 fixture crops have cultivar_recommendation
        assert len(rows) >= 3, f"Expected >= 3 cultivar rows, got {len(rows)}"
        for row in rows:
            assert "variety_id" in row
            assert row["field_name"] == "cultivar_recommendation"
            assert row["source"] == "NI:jmf_book_v1"
            assert row["trust_tier"] == "NI"
            assert row["confidence_weight"] is None
            assert row["is_outlier_rejected"] is False
