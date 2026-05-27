"""ZacksLeafySurveyImporter smoke test — AC-C2-06.

SFA-S003-P002-WP-C2 LOD400 §6.
Low-yield source: empty cache is acceptable per spec.
"""
import pytest

pytestmark = pytest.mark.crop_book


class TestZacksLeafySurveyImporter:
    """AC-C2-06: low-yield source loads without error; empty result acceptable."""

    def test_empty_cache_returns_no_rows(self, tmp_path):
        """Empty cache dir → load_knowledge_notes returns [] without crash."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from organic_market_agent.crop_book.models import Base
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
        from organic_market_agent.crop_book import enrichment_models  # noqa
        from organic_market_agent.crop_book.importer.ni.zacks_leafy_survey import ZacksLeafySurveyImporter

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(engine)
        with SessionLocal() as session:
            imp = ZacksLeafySurveyImporter()
            imp.cache_dir = tmp_path  # empty dir
            rows = imp.load_knowledge_notes(session)
            assert rows == []
            assert imp.load(session) == []
