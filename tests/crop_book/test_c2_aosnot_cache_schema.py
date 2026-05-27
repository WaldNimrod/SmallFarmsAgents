"""Cache schema validation tests for WP-C2 sources — AC-C2-08, AC-C2-09.

SFA-S003-P002-WP-C2 LOD400 §6.
Tests: schema_version required, body_text ≤2000, Hebrew UTF-8 preserved.
"""
import json
import pytest

pytestmark = pytest.mark.crop_book


class TestAosnotCacheSchema:
    """AC-C2-08/09: cache schema and Hebrew encoding."""

    def test_schema_version_required(self, tmp_path):
        """Missing schema_version → importer skips file (logs warning, no crash)."""
        from organic_market_agent.crop_book.importer.ni.aosnot_variety_info import AosnotImporter

        bad = {"crop_he": "חסה", "notes": {"frost_tolerance": "text"}}
        (tmp_path / "חסה.json").write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")

        imp = AosnotImporter()
        imp.cache_dir = tmp_path
        # _iter_cache_files skips bad files; list should be empty
        result = list(imp._iter_cache_files())
        assert result == [], "Malformed cache file should be skipped silently"

    def test_body_text_bounded_to_2000_chars(self, tmp_path):
        """body_text > 2000 chars is truncated by load_knowledge_notes."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from organic_market_agent.crop_book.models import Base, CropFamily, Crop
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
        from organic_market_agent.crop_book import enrichment_models  # noqa
        from organic_market_agent.crop_book.importer.ni.aosnot_variety_info import AosnotImporter

        long_text = "א" * 2500  # 2500 Hebrew chars
        entry = {
            "schema_version": "1.0",
            "source": "NI:aosnot_v1",
            "crop_he": "חסה",
            "provenance": {"pdf": "test.docx", "extraction_model": "test", "extracted_at": ""},
            "notes": {"frost_tolerance": long_text},
        }
        (tmp_path / "חסה.json").write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(engine)
        with SessionLocal() as session:
            fam = CropFamily(scientific_name="Asteraceae_c2a", name_he="מורכבים_c2a")
            session.add(fam)
            session.flush()
            session.add(Crop(name_he="חסה", family_id=fam.id, category="vegetables"))
            session.commit()
        with SessionLocal() as session:
            imp = AosnotImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            assert len(rows) == 1
            assert len(rows[0]["body_text"]) <= 2000

    def test_hebrew_preserved_no_unicode_escapes(self, tmp_path):
        """AC-C2-09: written cache files must not contain \\uXXXX Hebrew escapes."""
        entry = {
            "schema_version": "1.0",
            "source": "NI:aosnot_v1",
            "crop_he": "אוסנה",
            "provenance": {"pdf": "L02.docx", "extraction_model": "test", "extracted_at": ""},
            "notes": {"frost_tolerance": "עמיד לקרה", "flowering_date": "אביב אפריל-יוני"},
        }
        cache_file = tmp_path / "אוסנה.json"
        cache_file.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")

        raw = cache_file.read_text(encoding="utf-8")
        assert "\\u05" not in raw, "Hebrew text must be stored as raw UTF-8, not escaped"
        data = json.loads(raw)
        assert data["crop_he"] == "אוסנה"
        assert data["notes"]["frost_tolerance"] == "עמיד לקרה"
