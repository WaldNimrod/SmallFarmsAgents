"""Tests for NI upsert idempotency — AC-11.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §9.
"""
import pytest

pytestmark = pytest.mark.crop_book


def _make_full_session_factory():
    """Create SQLite engine with all ORM tables (uses Base.metadata.create_all)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa: ensure registered
    from organic_market_agent.crop_book import enrichment_models  # noqa: resolve lazy FK
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(engine), engine


class TestNiIdempotency:
    """AC-11: Running NI loop twice yields same row count."""

    def test_ac11_upsert_knowledge_note_idempotent(self):
        from sqlalchemy import text
        from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note
        from organic_market_agent.crop_book.models import CropFamily, Crop

        SessionLocal, engine = _make_full_session_factory()

        # Seed a crop
        with SessionLocal() as session:
            family = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
            session.add(family)
            session.flush()
            crop = Crop(name_he="ארוגולה", family_id=family.id, category="vegetables")
            session.add(crop)
            session.flush()
            crop_id = crop.id
            session.commit()

        # First upsert
        with SessionLocal() as session:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source="NI:jmf_book_v1",
                note_type="pest_disease",
                body_text="Flea beetles affect early-season plantings.",
            )
            session.commit()

        with SessionLocal() as session:
            count_before = session.execute(
                text("SELECT COUNT(*) FROM crop_knowledge_notes")
            ).scalar()

        # Second upsert with same key — should UPDATE not INSERT
        with SessionLocal() as session:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source="NI:jmf_book_v1",
                note_type="pest_disease",
                body_text="Flea beetles — updated text.",
            )
            session.commit()

        with SessionLocal() as session:
            count_after = session.execute(
                text("SELECT COUNT(*) FROM crop_knowledge_notes")
            ).scalar()
            row = session.execute(
                text(
                    "SELECT body_text FROM crop_knowledge_notes "
                    "WHERE note_type='pest_disease'"
                )
            ).fetchone()

        assert count_before == count_after == 1, (
            f"Row count should remain 1 after re-upsert, got {count_before} -> {count_after}"
        )
        assert row[0] == "Flea beetles — updated text."
