"""Tests for CropKnowledgeNote ORM — AC-02 + AC-04b.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §4 / §9.
"""
import pytest

pytestmark = pytest.mark.crop_book


class TestCropKnowledgeNoteORM:
    """AC-02: NOTE_TYPE_VALUES has 13 entries; BODY_TEXT_MAX_LENGTH == 2000."""

    def test_ac02_note_type_values_count(self):
        from organic_market_agent.crop_book.crop_knowledge_notes import NOTE_TYPE_VALUES

        assert len(NOTE_TYPE_VALUES) == 13, (
            f"Expected 13 NOTE_TYPE_VALUES, got {len(NOTE_TYPE_VALUES)}: {NOTE_TYPE_VALUES}"
        )

    def test_ac02_note_type_values_content(self):
        from organic_market_agent.crop_book.crop_knowledge_notes import NOTE_TYPE_VALUES

        # 8 JMF book types
        assert "pest_disease" in NOTE_TYPE_VALUES
        assert "harvest_marker" in NOTE_TYPE_VALUES
        assert "storage_handling" in NOTE_TYPE_VALUES
        assert "rotation_companion" in NOTE_TYPE_VALUES
        assert "cultivar_recommendation" in NOTE_TYPE_VALUES
        assert "growing_tip" in NOTE_TYPE_VALUES
        assert "irrigation" in NOTE_TYPE_VALUES
        assert "nursery_specific" in NOTE_TYPE_VALUES
        # 2 FT baseline types
        assert "flame_weed_timing" in NOTE_TYPE_VALUES
        assert "biopesticide_spray" in NOTE_TYPE_VALUES
        # 3 Q5 additions
        assert "phytoprotection_substance" in NOTE_TYPE_VALUES
        assert "phytoprotection_application" in NOTE_TYPE_VALUES
        assert "nursery_seeding_process" in NOTE_TYPE_VALUES

    def test_ac02_body_text_max_length(self):
        from organic_market_agent.crop_book.crop_knowledge_notes import BODY_TEXT_MAX_LENGTH

        assert BODY_TEXT_MAX_LENGTH == 2000

    def test_ac04b_note_type_check_13_values(self):
        """AC-04b: All 13 note_type values are accepted; 'nonsense_type' raises IntegrityError."""
        from sqlalchemy import create_engine, text, inspect as sa_inspect
        from sqlalchemy.orm import sessionmaker
        from organic_market_agent.crop_book.crop_knowledge_notes import (
            CropKnowledgeNote,
            NOTE_TYPE_VALUES,
        )
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime, timezone

        engine = create_engine("sqlite:///:memory:")
        # Create minimal crops table + crop_knowledge_notes table from ORM
        with engine.begin() as conn:
            conn.execute(text(
                "CREATE TABLE crops (id INTEGER PRIMARY KEY AUTOINCREMENT, name_he TEXT NOT NULL)"
            ))
            conn.execute(text(
                "CREATE TABLE crop_knowledge_notes ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "crop_id INTEGER NOT NULL REFERENCES crops(id),"
                "source VARCHAR(50) NOT NULL,"
                "trust_tier VARCHAR(20) NOT NULL,"
                "note_type VARCHAR(40) NOT NULL,"
                "body_text TEXT NOT NULL,"
                "provenance_pdf VARCHAR(200),"
                "provenance_pages VARCHAR(40),"
                "is_internal_farm_use_only INTEGER NOT NULL DEFAULT 1,"
                "extraction_model VARCHAR(50),"
                "extracted_at TIMESTAMP,"
                "created_at TIMESTAMP NOT NULL,"
                "UNIQUE(crop_id, source, note_type),"
                f"CHECK(note_type IN ({','.join(repr(v) for v in NOTE_TYPE_VALUES)})),"
                "CHECK(length(body_text) <= 2000)"
                ")"
            ))
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('ארוגולה')"))

        SessionLocal = sessionmaker(engine)
        now_str = datetime.now(timezone.utc).isoformat()

        # All 13 note_type values should be accepted
        with SessionLocal() as session:
            for i, nt in enumerate(NOTE_TYPE_VALUES):
                session.execute(text(
                    "INSERT INTO crop_knowledge_notes "
                    "(crop_id, source, trust_tier, note_type, body_text, is_internal_farm_use_only, created_at) "
                    "VALUES (1, :src, 'NI', :nt, 'test body', 1, :ts)"
                ), {"src": f"NI:test_{i}", "nt": nt, "ts": now_str})
            session.commit()

        # 'nonsense_type' should raise IntegrityError
        with SessionLocal() as session:
            with pytest.raises(IntegrityError):
                session.execute(text(
                    "INSERT INTO crop_knowledge_notes "
                    "(crop_id, source, trust_tier, note_type, body_text, is_internal_farm_use_only, created_at) "
                    "VALUES (1, 'NI:bad', 'NI', 'nonsense_type', 'body', 1, :ts)"
                ), {"ts": now_str})
                session.commit()
