"""Tests for CropContentLoader (WP-CB-CONTENT).

Verifies: authoring JSON → canonical parent + N per-source children; source_class /
display_order / winning_source_class derived from the registry; idempotent re-run with
prune; missing-crop and unknown-content_type skips.
"""
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book


@pytest.fixture
def session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import organic_market_agent.models  # noqa: F401 — registers crop_book.models
    from organic_market_agent.crop_book import content_models  # noqa: F401 — registers content tables
    from organic_market_agent.crop_book.models import Base, Crop, CropFamily

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    s = Session()
    fam = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
    s.add(fam)
    s.flush()
    # חסה = JMF_CROP_MAP['Lettuce']; ברוקולי = JMF_CROP_MAP['Broccoli'] (intentionally NOT inserted)
    s.add(Crop(name_he="חסה", category="vegetables", family_id=fam.id))
    s.commit()
    yield s
    s.close()


def _write_authoring(tmp_path: Path, crops: dict) -> Path:
    f = tmp_path / "authoring.json"
    f.write_text(json.dumps({"schema_version": "1.0", "crops": crops}, ensure_ascii=False), encoding="utf-8")
    return f


def _load(session, authoring_file):
    from organic_market_agent.crop_book.importer.content_loader import load_content
    return load_content(session, authoring_file)


def test_basic_upsert_parent_and_children(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContent, CropContentSource

    f = _write_authoring(tmp_path, {
        "Lettuce": {
            "story": {
                "canonical_md": "סיפור החסה.",
                "sources": [
                    {"source_label": "JMF", "raw_text_md": "גרסת JMF.", "source_url": None},
                    {"source_label": "NI:groworganic", "raw_text_md": "גרסה ישראלית.", "source_url": "https://x"},
                    {"source_label": "WR:claude_research", "raw_text_md": "סינתזת רשת.", "source_url": None},
                ],
            }
        }
    })
    summ = _load(session, f)
    assert summ.crops_resolved == 1
    assert summ.units_upserted == 1
    assert summ.sources_upserted == 3

    cc = session.query(CropContent).one()
    assert cc.content_type == "story"
    assert cc.text_md == "סיפור החסה."
    assert cc.source_count == 3
    # winning = best CLASS_RANK among {PR(JMF), NI, WR} → NI (rank 1)
    assert cc.winning_source_class == "NI"
    # NI is a hard-override class → confidence 1.0
    assert float(cc.confidence_score) == 1.0

    variants = session.query(CropContentSource).order_by(CropContentSource.display_order).all()
    assert [v.source_class for v in variants] == ["NI", "PR", "WR"]  # CLASS_RANK 1,2,3
    assert [v.display_order for v in variants] == [1, 2, 3]
    by_label = {v.source_label: v for v in variants}
    assert by_label["JMF"].source_class == "PR"
    assert by_label["WR:claude_research"].source_class == "WR"
    assert by_label["NI:groworganic"].source_url == "https://x"


def test_idempotent_rerun_updates_no_duplicates(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContent, CropContentSource

    f = _write_authoring(tmp_path, {
        "Lettuce": {"story": {"canonical_md": "v1", "sources": [
            {"source_label": "JMF", "raw_text_md": "a"},
        ]}}
    })
    _load(session, f)
    # Re-run with edited canonical
    f2 = _write_authoring(tmp_path, {
        "Lettuce": {"story": {"canonical_md": "v2", "sources": [
            {"source_label": "JMF", "raw_text_md": "a2"},
        ]}}
    })
    _load(session, f2)
    assert session.query(CropContent).count() == 1
    assert session.query(CropContentSource).count() == 1
    cc = session.query(CropContent).one()
    assert cc.text_md == "v2"
    assert session.query(CropContentSource).one().raw_text_md == "a2"


def test_prune_removed_source(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContentSource

    f = _write_authoring(tmp_path, {
        "Lettuce": {"story": {"canonical_md": "x", "sources": [
            {"source_label": "JMF", "raw_text_md": "a"},
            {"source_label": "WR:claude_research", "raw_text_md": "b"},
        ]}}
    })
    _load(session, f)
    assert session.query(CropContentSource).count() == 2
    # Remove the WR source on re-run → it must be pruned
    f2 = _write_authoring(tmp_path, {
        "Lettuce": {"story": {"canonical_md": "x", "sources": [
            {"source_label": "JMF", "raw_text_md": "a"},
        ]}}
    })
    summ = _load(session, f2)
    assert summ.sources_pruned == 1
    labels = {v.source_label for v in session.query(CropContentSource).all()}
    assert labels == {"JMF"}


def test_confidence_without_hard_override(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContent

    f = _write_authoring(tmp_path, {
        "Lettuce": {"care_watering": {"canonical_md": "w", "sources": [
            {"source_label": "JMF", "raw_text_md": "a"},
            {"source_label": "WR:claude_research", "raw_text_md": "b"},
        ]}}
    })
    _load(session, f)
    cc = session.query(CropContent).filter_by(content_type="care_watering").one()
    assert cc.winning_source_class == "PR"  # JMF(PR rank 2) beats WR(rank 3)
    # No EX/NI → heuristic 0.40 + 0.15*2 = 0.70
    assert float(cc.confidence_score) == 0.70


def test_missing_crop_skipped(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContent

    f = _write_authoring(tmp_path, {
        # In JMF_CROP_MAP (→ ברוקולי) but NOT inserted into the DB → skipped.
        "Broccoli": {"story": {"canonical_md": "z", "sources": []}},
        # Not in JMF_CROP_MAP at all → skipped.
        "NotACrop": {"story": {"canonical_md": "z", "sources": []}},
    })
    summ = _load(session, f)
    assert summ.crops_resolved == 0
    assert session.query(CropContent).count() == 0
    assert len(summ.skipped) >= 1


def test_unknown_content_type_skipped(session, tmp_path):
    from organic_market_agent.crop_book.content_models import CropContent

    f = _write_authoring(tmp_path, {
        "Lettuce": {
            "story": {"canonical_md": "ok", "sources": []},
            "bogus_type": {"canonical_md": "nope", "sources": []},
        }
    })
    _load(session, f)
    types = {cc.content_type for cc in session.query(CropContent).all()}
    assert types == {"story"}


def test_committed_authoring_file_loads(session):
    """The repo's data/crop_content/authoring.json loads against the lettuce fixture."""
    from organic_market_agent.crop_book.content_models import CropContent

    summ = _load(session, None)  # default path → data/crop_content/authoring.json
    # The committed exemplar authors Lettuce (חסה) — at least the story unit must land.
    assert session.query(CropContent).filter_by(content_type="story").count() == 1
    assert summ.units_upserted >= 1
