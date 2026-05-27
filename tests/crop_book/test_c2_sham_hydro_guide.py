"""ShamHydroGuideImporter tests — AC-C2-05.

SFA-S003-P002-WP-C2 LOD400 §6.
Tests: ≥10 crops with hydro_suitability, Hebrew encoding preserved.
"""
import json
import pytest

pytestmark = pytest.mark.crop_book

_HYDRO_CROPS = [
    "חסה", "תרד", "בזיליקום", "עירית", "נענע", "כוסברה",
    "פטרוזיליה", "עגבנייה שרי", "מלפפון", "פלפל",
]


@pytest.fixture
def hydro_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, CropFamily, Crop
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
    from organic_market_agent.crop_book import enrichment_models  # noqa

    for crop_he in _HYDRO_CROPS:
        entry = {
            "schema_version": "1.0",
            "source": "NI:sham_hydro_guide_v1",
            "crop_he": crop_he,
            "provenance": {"pdf": "L09.pdf", "extraction_model": "claude-sonnet-4-6", "extracted_at": ""},
            "notes": {"hydro_suitability": f"מתאים לגידול הידרופוני — {crop_he}"},
        }
        (tmp_path / f"{crop_he}.json").write_text(
            json.dumps(entry, ensure_ascii=False), encoding="utf-8"
        )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine)
    with SessionLocal() as session:
        fam = CropFamily(scientific_name="Mixed_c2d", name_he="מעורב_c2d")
        session.add(fam)
        session.flush()
        for crop_he in _HYDRO_CROPS:
            session.add(Crop(name_he=crop_he, family_id=fam.id, category="vegetables"))
        session.commit()

    return SessionLocal, tmp_path


class TestShamHydroGuideImporter:
    """AC-C2-05: ≥10 crops with hydro_suitability loaded."""

    def test_hydro_suitability_ge_ten_crops(self, hydro_session):
        """load_knowledge_notes produces ≥10 hydro_suitability rows."""
        from organic_market_agent.crop_book.importer.ni.sham_hydro_guide import ShamHydroGuideImporter
        SessionLocal, tmp_path = hydro_session
        with SessionLocal() as session:
            imp = ShamHydroGuideImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            assert len(rows) >= 10, f"Expected ≥10 hydro_suitability rows, got {len(rows)}"

    def test_hydro_hebrew_body_text_preserved(self, hydro_session):
        """Hebrew body_text stored as raw UTF-8, not ASCII-escaped."""
        from organic_market_agent.crop_book.importer.ni.sham_hydro_guide import ShamHydroGuideImporter
        SessionLocal, tmp_path = hydro_session
        with SessionLocal() as session:
            imp = ShamHydroGuideImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            for row in rows:
                assert "\\u05" not in row["body_text"], "Hebrew must not be escaped"
                assert "מתאים" in row["body_text"] or len(row["body_text"]) > 0
