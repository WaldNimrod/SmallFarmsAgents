"""Tests for JmfFtPhytoprotectionImporter — AC-09 for phytoprotection source (Q5).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_ft_phytoprotection")


@pytest.fixture
def full_session_phyto():
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
        family = CropFamily(scientific_name="Solanaceae_ph", name_he="סולניים_ph")
        session.add(family)
        session.flush()
        for name_he in ["עגבנייה", "פלפל"]:
            session.add(Crop(name_he=name_he, family_id=family.id, category='vegetables'))
        session.commit()

    with SessionLocal() as session:
        yield session


class TestJmfFtPhytoprotectionImporter:
    """AC-09: load_knowledge_notes returns phytoprotection note_types (Q5)."""

    def test_ac09_phytoprotection_rows(self, full_session_phyto):
        from organic_market_agent.crop_book.importer.ni.jmf_ft_phytoprotection import JmfFtPhytoprotectionImporter

        imp = JmfFtPhytoprotectionImporter()
        imp.cache_dir = FIXTURE_DIR
        rows = imp.load_knowledge_notes(full_session_phyto)
        # 2 crops * 2 note types each = 4 rows minimum
        assert len(rows) >= 4, f"Expected >= 4 rows (2 crops x 2 note types), got {len(rows)}"
        note_types = {r["note_type"] for r in rows}
        assert "phytoprotection_substance" in note_types
        assert "phytoprotection_application" in note_types
        for row in rows:
            assert row["source"] == "NI:jmf_ft_phytoprotection_v1"
            assert row["is_internal_farm_use_only"] is True
