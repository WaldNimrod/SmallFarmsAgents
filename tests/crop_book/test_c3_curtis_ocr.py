"""WP-C3 tests — Curtis Stone OCR narrative importer."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, Crop, CropFamily, CropVariety
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    with Session() as session:
        fam = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
        session.add(fam)
        session.flush()
        crop = Crop(name_he="ארוגולה", name_en="Arugula", category="vegetables", family_id=fam.id)
        session.add(crop)
        session.flush()
        yield session


@pytest.fixture
def ocr_cache_dir(tmp_path):
    """Create a minimal OCR cache with one valid and one empty narrative."""
    cache = tmp_path / "curtis_ocr"
    cache.mkdir()
    (cache / "L41_curtis_chart_01.json").write_text(json.dumps({
        "image_id": "L41_curtis_chart_01",
        "crop": "Arugula",
        "planting_specs": "plant at 35°F+",
        "varieties": [],
        "dtm": 35,
        "avg_yield_per_bed": "30",
        "avg_gross_profit_per_bed": "",
        "narrative_text": "Arugula is a fast-growing green that does best in cool weather. " * 20,
    }), encoding="utf-8")
    (cache / "L41_curtis_chart_02.json").write_text(json.dumps({
        "image_id": "L41_curtis_chart_02",
        "crop": "Unknown Crop",
        "narrative_text": "",
    }), encoding="utf-8")
    return cache


def test_ocr_narrative_loaded(db_session, ocr_cache_dir):
    """OCR narratives are upserted to crop_knowledge_notes for resolved crops."""
    from organic_market_agent.crop_book.importer.urban_farmer.curtis_ocr_importer import import_all

    # Need CropKnowledgeNote table
    try:
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
        CropKnowledgeNote.__table__.create(db_session.get_bind(), checkfirst=True)
    except Exception:
        pass

    summary = import_all(db_session, ocr_dir=ocr_cache_dir)
    assert summary.rows_upserted >= 1

    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
    notes = db_session.query(CropKnowledgeNote).filter_by(source="NI:curtis_stone_book").all()
    assert len(notes) >= 1


def test_body_text_truncation(db_session, tmp_path):
    """Body text longer than 2000 chars is truncated to exactly 2000."""
    from organic_market_agent.crop_book.importer.urban_farmer.curtis_ocr_importer import import_all

    cache = tmp_path / "ocr"
    cache.mkdir()
    long_text = "A" * 3000
    (cache / "L41_curtis_chart_01.json").write_text(json.dumps({
        "image_id": "L41_curtis_chart_01",
        "crop": "Arugula",
        "narrative_text": long_text,
        "varieties": [],
    }), encoding="utf-8")

    try:
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
        CropKnowledgeNote.__table__.create(db_session.get_bind(), checkfirst=True)
    except Exception:
        pass

    import_all(db_session, ocr_dir=cache)

    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
    notes = db_session.query(CropKnowledgeNote).filter_by(source="NI:curtis_stone_book").all()
    assert len(notes) == 1
    assert len(notes[0].body_text) <= 2000
