"""Tests for cache JSON schema validation — AC-08.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §5 / §9.
"""
import json
import pathlib
import tempfile
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = pathlib.Path("tests/crop_book/fixtures/ni/jmf_book")


class TestNiCacheSchema:
    """AC-08: Schema validation rejects malformed JSON."""

    def test_ac08_missing_schema_version_raises(self):
        """Missing schema_version -> ValueError."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        bad_data = json.dumps({
            "crop_jmf_en": "Arugula",
            "notes": {"pest_disease": "some text"},
        })
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(bad_data)
            tmp_path = pathlib.Path(f.name)

        try:
            with pytest.raises(ValueError, match="schema_version"):
                imp._load_cache_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_ac08_unknown_note_type_raises(self):
        """Unknown note_type key -> ValueError."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        bad_data = json.dumps({
            "schema_version": "1.0",
            "crop_jmf_en": "Arugula",
            "notes": {"completely_unknown_type": "body text"},
        })
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(bad_data)
            tmp_path = pathlib.Path(f.name)

        try:
            with pytest.raises(ValueError, match="unknown note_type key"):
                imp._load_cache_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_ac08_body_text_over_limit_raises(self):
        """body_text > 2000 chars -> ValueError."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        bad_data = json.dumps({
            "schema_version": "1.0",
            "crop_jmf_en": "Arugula",
            "notes": {"pest_disease": "X" * 2001},
        })
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(bad_data)
            tmp_path = pathlib.Path(f.name)

        try:
            with pytest.raises(ValueError, match="body_text > 2000"):
                imp._load_cache_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_ac08_valid_fixture_passes_validation(self):
        """Valid fixture JSON passes schema validation."""
        from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter

        imp = JmfBookImporter()
        fixture_path = FIXTURE_DIR / "Arugula.json"
        data = imp._load_cache_file(fixture_path)
        assert data["schema_version"] == "1.0"
        assert data["crop_jmf_en"] == "Arugula"
        assert isinstance(data["notes"], dict)
