"""Tests for jmf_book + jmf_book_alt dedup handling — AC-16 (Q5).

Verifies that both sources produce crop_knowledge_notes rows for the same crop
with the same note_type (different source label — UNIQUE constraint allows it).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §9 / AC-16.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR_BOOK = pathlib.Path("tests/crop_book/fixtures/ni/jmf_book")
FIXTURE_DIR_ALT = pathlib.Path("tests/crop_book/fixtures/ni/jmf_book_alt")


@pytest.fixture
def mock_session_both():
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
        family = CropFamily(scientific_name="Brassicaceae_ded", name_he="מצליבים_ded")
        session.add(family)
        session.flush()
        crop = Crop(name_he="ארוגולה", family_id=family.id, category="vegetables")
        session.add(crop)
        session.flush()
        session.commit()

    with SessionLocal() as session:
        yield session


class TestNiDedupAltEdition:
    """AC-16: jmf_book + jmf_book_alt both produce rows for same crop (different source)."""

    def test_ac16_both_editions_produce_rows_for_same_crop(self, mock_session_both):
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter
        from organic_market_agent.crop_book.importer.ni.jmf_book_alt import JmfBookAltImporter

        book_imp = JmfBookImporter()
        book_imp.cache_dir = FIXTURE_DIR_BOOK

        alt_imp = JmfBookAltImporter()
        alt_imp.cache_dir = FIXTURE_DIR_ALT

        book_rows = book_imp.load_knowledge_notes(mock_session_both)
        alt_rows = alt_imp.load_knowledge_notes(mock_session_both)

        # Arugula is in both fixture dirs
        book_arugula = [r for r in book_rows if r.get("body_text")]
        alt_arugula = [r for r in alt_rows if r.get("body_text")]

        assert len(book_arugula) > 0, "jmf_book should produce rows for Arugula"
        assert len(alt_arugula) > 0, "jmf_book_alt should produce rows for Arugula"

        # Both should have different source labels
        book_sources = {r["source"] for r in book_arugula}
        alt_sources = {r["source"] for r in alt_arugula}
        assert "NI:jmf_book_v1" in book_sources
        assert "NI:jmf_book_alt_v1" in alt_sources
        assert book_sources.isdisjoint(alt_sources), (
            "Sources must differ so UNIQUE(crop_id, source, note_type) allows both rows"
        )

    def test_ac16_unique_constraint_allows_both_rows(self):
        """Both rows can coexist in DB because source differs."""
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from organic_market_agent.crop_book.crop_knowledge_notes import NOTE_TYPE_VALUES
        from datetime import datetime, timezone

        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as conn:
            conn.execute(text(
                "CREATE TABLE crop_knowledge_notes ("
                "id INTEGER PRIMARY KEY,"
                "crop_id INTEGER NOT NULL,"
                "source VARCHAR(50) NOT NULL,"
                "trust_tier VARCHAR(20) NOT NULL,"
                "note_type VARCHAR(40) NOT NULL,"
                "body_text TEXT NOT NULL,"
                "is_internal_farm_use_only INTEGER NOT NULL DEFAULT 1,"
                "created_at TIMESTAMP NOT NULL,"
                "UNIQUE(crop_id, source, note_type),"
                f"CHECK(note_type IN ({','.join(repr(v) for v in NOTE_TYPE_VALUES)}))"
                ")"
            ))
            now_str = datetime.now(timezone.utc).isoformat()
            # Insert row from jmf_book
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes "
                "(crop_id, source, trust_tier, note_type, body_text, created_at) "
                "VALUES (1, 'NI:jmf_book_v1', 'NI', 'pest_disease', 'Body A.', :ts)"
            ), {"ts": now_str})
            # Insert row from jmf_book_alt for same crop + note_type — should succeed
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes "
                "(crop_id, source, trust_tier, note_type, body_text, created_at) "
                "VALUES (1, 'NI:jmf_book_alt_v1', 'NI', 'pest_disease', 'Body B.', :ts)"
            ), {"ts": now_str})

        SessionLocal = sessionmaker(engine)
        with SessionLocal() as session:
            from sqlalchemy import text as sqla_text
            count = session.execute(sqla_text("SELECT COUNT(*) FROM crop_knowledge_notes")).scalar()
        assert count == 2, "Both jmf_book and jmf_book_alt rows should coexist"
