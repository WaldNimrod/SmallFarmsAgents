"""ShamVarietyTrialsImporter tests — AC-C2-04.

SFA-S003-P002-WP-C2 LOD400 §6.
Tests: table format, ≥5 lettuce variety trial score rows.
"""
import json
import pytest

pytestmark = pytest.mark.crop_book

_LETTUCE_VARIETIES = [
    "חסה בטביה 1", "חסה בטביה 2", "חסה רומנית", "חסה ריגת", "חסה בטביה 5", "חסה ירוקה"
]


@pytest.fixture
def variety_trials_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, CropFamily, Crop
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
    from organic_market_agent.crop_book import enrichment_models  # noqa

    crops_table = {var: {"variety_trial_score": f"ציון: 8.5 — {var}"} for var in _LETTUCE_VARIETIES}
    table_data = {
        "schema_version": "1.0",
        "source": "NI:sham_variety_trials_v1",
        "provenance": {"pdf": "L11.pdf", "extraction_model": "claude-sonnet-4-6", "extracted_at": ""},
        "crops": crops_table,
    }
    (tmp_path / "_table.json").write_text(
        json.dumps(table_data, ensure_ascii=False), encoding="utf-8"
    )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine)
    with SessionLocal() as session:
        fam = CropFamily(scientific_name="Asteraceae_c2c", name_he="מורכבים_c2c")
        session.add(fam)
        session.flush()
        for var in _LETTUCE_VARIETIES:
            session.add(Crop(name_he=var, family_id=fam.id, category="vegetables"))
        session.commit()

    return SessionLocal, tmp_path


class TestShamVarietyTrialsImporter:
    """AC-C2-04: ≥5 lettuce variety_trial_score rows produced."""

    def test_table_json_loaded(self, variety_trials_session):
        """_table.json with schema_version='1.0' loads without error."""
        from organic_market_agent.crop_book.importer.ni.sham_variety_trials import ShamVarietyTrialsImporter
        SessionLocal, tmp_path = variety_trials_session
        with SessionLocal() as session:
            imp = ShamVarietyTrialsImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            assert len(rows) >= 5, f"Expected ≥5 variety_trial_score rows, got {len(rows)}"

    def test_variety_trial_score_note_type(self, variety_trials_session):
        """All rows have note_type='variety_trial_score'."""
        from organic_market_agent.crop_book.importer.ni.sham_variety_trials import ShamVarietyTrialsImporter
        SessionLocal, tmp_path = variety_trials_session
        with SessionLocal() as session:
            imp = ShamVarietyTrialsImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            for row in rows:
                assert row["note_type"] == "variety_trial_score"
                assert row["trust_tier"] == "NI"
