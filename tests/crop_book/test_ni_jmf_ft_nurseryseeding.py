"""Tests for JmfFtNurseryseedingImporter — AC-09 for nursery seeding source (Q5).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_ft_nurseryseeding")


@pytest.fixture
def full_session_nursery():
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
        fam1 = CropFamily(scientific_name="Asteraceae_ns", name_he="מורכבים_ns")
        fam2 = CropFamily(scientific_name="Solanaceae_ns", name_he="סולניים_ns")
        session.add_all([fam1, fam2])
        session.flush()
        session.add(Crop(name_he="חסה", family_id=fam1.id, category="vegetables"))
        session.add(Crop(name_he="עגבנייה", family_id=fam2.id, category="vegetables"))
        session.commit()

    with SessionLocal() as session:
        yield session


class TestJmfFtNurseryseedingImporter:
    """AC-09: load_knowledge_notes returns nursery_seeding_process rows (Q5)."""

    def test_ac09_nurseryseeding_rows(self, full_session_nursery):
        from organic_market_agent.crop_book.importer.ni.jmf_ft_nurseryseeding import JmfFtNurseryseedingImporter

        imp = JmfFtNurseryseedingImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load_knowledge_notes(full_session_nursery)
        assert len(rows) >= 2, f"Expected >= 2 rows (Lettuce + Tomatoes), got {len(rows)}"
        note_types = {r["note_type"] for r in rows}
        assert "nursery_seeding_process" in note_types
        for row in rows:
            assert row["source"] == "NI:jmf_ft_nurseryseeding_v1"
            assert len(row["body_text"]) <= 2000
