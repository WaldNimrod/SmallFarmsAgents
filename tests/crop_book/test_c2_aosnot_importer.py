"""AosnotImporter unit + DB integration tests — AC-C2-02, AC-C2-03, AC-C2-10.

SFA-S003-P002-WP-C2 LOD400 §6.
"""
import json
import pytest

pytestmark = pytest.mark.crop_book

_C2_NOTE_TYPES = ("frost_tolerance", "flowering_date", "pollination_mechanism", "israeli_regions")


def _make_aosnot_fixture(tmp_path, crop_he: str, notes: dict) -> None:
    entry = {
        "schema_version": "1.0",
        "source": "NI:aosnot_v1",
        "crop_he": crop_he,
        "provenance": {"pdf": "L02.docx", "extraction_model": "claude-sonnet-4-6", "extracted_at": ""},
        "notes": {nt: notes.get(nt) for nt in _C2_NOTE_TYPES},
    }
    (tmp_path / f"{crop_he}.json").write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def aosnot_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, CropFamily, Crop
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
    from organic_market_agent.crop_book import enrichment_models  # noqa

    # Create fixtures with 5 crops, each having all 4 C2 note_types
    crops_data = {
        "חסה": ("עמיד לקרה קלה", "ינואר-פברואר", "עצמי", "כל הארץ"),
        "עגבנייה": ("רגיש לקרה", "מרץ-אפריל", "חרקים ורוח", "מרכז וצפון"),
        "מלפפון": ("רגיש לקרה", "אפריל-מאי", "דבורים", "בית ממוגן"),
        "פלפל": ("רגיש מאוד לקרה", "מרץ-מאי", "דבורים", "מרכז"),
        "כרוב": ("עמיד לקרה", "פברואר-מרץ", "עצמי", "כל הארץ"),
    }
    for crop_he, (ft, fd, pm, ir) in crops_data.items():
        _make_aosnot_fixture(tmp_path, crop_he, {
            "frost_tolerance": ft,
            "flowering_date": fd,
            "pollination_mechanism": pm,
            "israeli_regions": ir,
        })

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine)
    with SessionLocal() as session:
        fam = CropFamily(scientific_name="Mixed_c2b", name_he="מעורב_c2b")
        session.add(fam)
        session.flush()
        for crop_he in crops_data:
            session.add(Crop(name_he=crop_he, family_id=fam.id, category="vegetables"))
        session.commit()

    return SessionLocal, tmp_path


class TestAosnotImporter:
    """AC-C2-02/03/10: extraction rows, per-crop field coverage, NI hard-override."""

    def test_load_returns_empty_list(self, aosnot_session):
        """AC-C2: load() returns [] (narrative source, no cultivar_recommendation)."""
        from organic_market_agent.crop_book.importer.ni.aosnot_variety_info import AosnotImporter
        SessionLocal, tmp_path = aosnot_session
        with SessionLocal() as session:
            imp = AosnotImporter()
            imp.cache_dir = tmp_path
            assert imp.load(session) == []

    def test_load_knowledge_notes_all_four_types(self, aosnot_session):
        """AC-C2-03: frost_tolerance, flowering_date, pollination_mechanism, israeli_regions loaded."""
        from organic_market_agent.crop_book.importer.ni.aosnot_variety_info import AosnotImporter
        SessionLocal, tmp_path = aosnot_session
        with SessionLocal() as session:
            imp = AosnotImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            note_types_found = {r["note_type"] for r in rows}
            for nt in _C2_NOTE_TYPES:
                assert nt in note_types_found, f"Expected note_type {nt!r} in rows"

    def test_ni_hard_override_trust_tier(self, aosnot_session):
        """AC-C2-10: all rows have trust_tier='NI' and source='NI:aosnot_v1'."""
        from organic_market_agent.crop_book.importer.ni.aosnot_variety_info import AosnotImporter
        SessionLocal, tmp_path = aosnot_session
        with SessionLocal() as session:
            imp = AosnotImporter()
            imp.cache_dir = tmp_path
            rows = imp.load_knowledge_notes(session)
            assert len(rows) > 0
            for row in rows:
                assert row["trust_tier"] == "NI"
                assert row["source"] == "NI:aosnot_v1"
                assert row["is_internal_farm_use_only"] is True
