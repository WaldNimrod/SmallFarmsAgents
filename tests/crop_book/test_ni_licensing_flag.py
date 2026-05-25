"""Tests for is_internal_farm_use_only licensing flag — AC-05.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §3.1 / §7.3 / §9.
"""
import pytest

pytestmark = pytest.mark.crop_book


def _make_session_and_crop():
    """Create full ORM session and return (SessionLocal, crop_id)."""
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
        family = CropFamily(scientific_name="Asteraceae_lic", name_he="מורכבים_lic")
        session.add(family)
        session.flush()
        crop = Crop(name_he="ארוגולה_lic", family_id=family.id, category="vegetables")
        session.add(crop)
        session.flush()
        crop_id = crop.id
        session.commit()

    return SessionLocal, crop_id


class TestNiLicensingFlag:
    """AC-05: is_internal_farm_use_only=True by default; helper hardcodes True."""

    def test_ac05_default_is_true_via_helper(self):
        """_upsert_knowledge_note always sets is_internal_farm_use_only=True."""
        from sqlalchemy import text
        from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

        SessionLocal, crop_id = _make_session_and_crop()

        with SessionLocal() as session:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source="NI:jmf_book_v1",
                note_type="pest_disease",
                body_text="Test body.",
            )
            session.commit()

        with SessionLocal() as session:
            row = session.execute(
                text("SELECT is_internal_farm_use_only FROM crop_knowledge_notes WHERE crop_id=:cid"),
                {"cid": crop_id},
            ).fetchone()
        assert row[0] == 1, "is_internal_farm_use_only should be 1 (True)"

    def test_ac05_helper_hardcodes_true_even_if_false_passed(self):
        """Passing is_internal_farm_use_only=False to helper is still stored as True."""
        from sqlalchemy import text
        from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

        SessionLocal, crop_id = _make_session_and_crop()

        with SessionLocal() as session:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source="NI:jmf_book_v1",
                note_type="harvest_marker",
                body_text="Harvest at 4-6 inches.",
                is_internal_farm_use_only=False,  # should be overridden to True
            )
            session.commit()

        with SessionLocal() as session:
            row = session.execute(
                text(
                    "SELECT is_internal_farm_use_only FROM crop_knowledge_notes "
                    "WHERE note_type='harvest_marker' AND crop_id=:cid"
                ),
                {"cid": crop_id},
            ).fetchone()
        assert row[0] == 1, "is_internal_farm_use_only must always be 1 (True) regardless of arg"

    def test_ac05_trust_tier_is_ni(self):
        """Helper always sets trust_tier='NI'."""
        from sqlalchemy import text
        from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

        SessionLocal, crop_id = _make_session_and_crop()

        with SessionLocal() as session:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source="NI:test_x",
                note_type="irrigation",
                body_text="Light, frequent watering.",
                trust_tier="EX",  # should be overridden to NI
            )
            session.commit()

        with SessionLocal() as session:
            row = session.execute(
                text("SELECT trust_tier FROM crop_knowledge_notes WHERE note_type='irrigation' AND crop_id=:cid"),
                {"cid": crop_id},
            ).fetchone()
        assert row[0] == "NI"
