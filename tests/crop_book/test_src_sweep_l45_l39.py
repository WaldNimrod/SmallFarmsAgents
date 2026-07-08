"""WP-CB-SRC-SWEEP — L45 (IL farm 2017 base-data) + L39 (mesclun) importers.

SFA-S003-P004-WP-CB-SRC-SWEEP.

L45: OP-tier cherry-pick → crop_variety_source_values (days_to_maturity,
     in_row_spacing_cm, rows_per_bed) + internal growing_tip notes.
L39: JMF Masterclass → new named variety 'חסה בייבי' under crop 'עלי בייבי'
     + cultivar_recommendation source value + species knowledge notes (internal).
"""
import json
import pytest

pytestmark = pytest.mark.crop_book


def _make_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, CropFamily, Crop, CropVariety  # noqa
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa
    from organic_market_agent.crop_book import enrichment_models  # noqa

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(engine)


# ───────────────────────────────── L45 ──────────────────────────────────────

@pytest.fixture
def l45_session(tmp_path, monkeypatch):
    from organic_market_agent.crop_book.models import CropFamily, Crop
    import organic_market_agent.crop_book.importer.ni.il_farm_2017_l45 as l45

    table = {
        "schema_version": "1.0",
        "source": "OP:il_farm_2017_l45",
        "provenance": {"xlsx": "L45_2017_data_summary.xlsx", "sheet": "נתוני בסיס"},
        "crops": [
            {"crop_he": "חסה", "rows_per_bed": 4.0, "in_row_spacing_cm": 30.0,
             "days_to_maturity": 75.0, "dtm_raw": "60-90", "season_he": "ספט-פבר",
             "notes": "2 חסות לארגז, 60 חסות בשבוע."},
            {"crop_he": "גזר", "rows_per_bed": 4.0, "in_row_spacing_cm": 5.0,
             "days_to_maturity": 150.0, "dtm_raw": "150", "season_he": "ספט-פבר", "notes": None},
            # generic name — must be skipped (not in DB, idan SKIP_CROPS)
            {"crop_he": "תבלינים", "rows_per_bed": 4.0, "in_row_spacing_cm": 5.0,
             "days_to_maturity": None, "dtm_raw": None, "season_he": "כל השנה", "notes": "מעורב"},
        ],
    }
    cache = tmp_path / "_table.json"
    cache.write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(l45, "CACHE_FILE", cache)

    SessionLocal = _make_db()
    with SessionLocal() as s:
        fam = CropFamily(scientific_name="Asteraceae_l45", name_he="מורכבים_l45")
        s.add(fam)
        s.flush()
        s.add(Crop(name_he="חסה", family_id=fam.id, category="vegetables"))
        s.add(Crop(name_he="גזר", family_id=fam.id, category="vegetables"))
        s.commit()
    return SessionLocal, l45


def test_l45_source_values_and_notes(l45_session):
    from organic_market_agent.crop_book.models import CropVarietySourceValue
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
    SessionLocal, l45 = l45_session
    with SessionLocal() as s:
        res = l45.ingest(s)
        s.commit()
        assert res["processed"] == 2, res          # חסה + גזר; תבלינים skipped
        svs = s.query(CropVarietySourceValue).all()
        fields = {v.field_name for v in svs}
        assert {"days_to_maturity", "in_row_spacing_cm", "rows_per_bed"} <= fields
        assert all(v.source == "OP:il_farm_2017_l45" for v in svs)
        assert all(v.trust_tier == "OP" for v in svs)
        assert all(float(v.confidence_weight) == 0.80 for v in svs)
        # DTM range midpoint preserved + raw recorded in note
        dtm = [v for v in svs if v.field_name == "days_to_maturity"]
        lettuce_dtm = next(v for v in dtm if float(v.value_numeric) == 75.0)
        assert "60-90" in (lettuce_dtm.note or "")
        # internal note carries season + cultural note
        notes = s.query(CropKnowledgeNote).all()
        assert len(notes) == 2  # גזר has no notes/season? גזר has season -> note; חסה has note
        assert all(n.is_internal_farm_use_only for n in notes)
        assert all(n.note_type == "growing_tip" for n in notes)


# ───────────────────────────────── L39 ──────────────────────────────────────

@pytest.fixture
def l39_session(tmp_path, monkeypatch):
    from organic_market_agent.crop_book.models import CropFamily, Crop
    import organic_market_agent.crop_book.importer.ni.jmf_ft_mesclun as mesclun

    data = {
        "schema_version": "1.0",
        "crop_name_he": "עלי בייבי",
        "crop_jmf_en": "Mesclun",
        "variety": {"name_he": "חסה בייבי", "name_en": "Baby Lettuce (Salanova one-cut mix)"},
        "cultivar_recommendation": "Salanova (Red Butter, Red Sweet Crisp, ...). Avoid Green Oakleaf.",
        "species_notes": {
            "cultivar_recommendation": "זני Salanova ...",
            "growing_tip": "מרווח 4 שורות בערוגה ...",
            "irrigation": "השקיה יסודית לאחר השתילה.",
            "harvest_marker": "קטיף בסכין חדה.",
        },
        "provenance": {"pdf": "L39_mesclun_guide.pdf", "pages": "1-4"},
    }
    datafile = tmp_path / "Mesclun.json"
    datafile.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(mesclun, "_DATA_FILE", datafile)

    SessionLocal = _make_db()
    with SessionLocal() as s:
        fam = CropFamily(scientific_name="Asteraceae_l39", name_he="מורכבים_l39")
        s.add(fam)
        s.flush()
        s.add(Crop(name_he="עלי בייבי", family_id=fam.id, category="vegetables"))
        s.commit()
    return SessionLocal, mesclun


def test_l39_creates_named_variety_and_notes(l39_session):
    from organic_market_agent.crop_book.models import Crop, CropVariety, CropVarietySourceValue
    from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value
    SessionLocal, mesclun = l39_session
    with SessionLocal() as s:
        imp = mesclun.JmfFtMesclunImporter()
        # variety + source value (PATH A)
        rows = imp.load(s)
        assert len(rows) == 1
        variety_id = rows[0].pop("variety_id")
        _upsert_source_value(s, variety_id, rows[0])
        # notes (PATH B)
        for nrow in imp.load_knowledge_notes(s):
            _upsert_knowledge_note(s, **nrow)
        s.commit()

        crop = s.query(Crop).filter_by(name_he="עלי בייבי").one()
        var = s.query(CropVariety).filter_by(crop_id=crop.id, name_en="Baby Lettuce (Salanova one-cut mix)").one()
        assert var.name_he == "חסה בייבי"
        assert var.is_default is False
        sv = s.query(CropVarietySourceValue).filter_by(variety_id=var.id).one()
        assert sv.field_name == "cultivar_recommendation"
        assert sv.source == "NI:jmf_ft_mesclun_v1"
        notes = s.query(CropKnowledgeNote).filter_by(crop_id=crop.id).all()
        assert {n.note_type for n in notes} == {
            "cultivar_recommendation", "growing_tip", "irrigation", "harvest_marker"
        }
        assert all(n.is_internal_farm_use_only for n in notes)
        assert all(n.source == "NI:jmf_ft_mesclun_v1" for n in notes)


def test_l39_real_data_file_is_valid():
    """The committed Mesclun.json parses and has the required keys."""
    from pathlib import Path
    p = Path("data/jmf/extracted/jmf_ft_mesclun/Mesclun.json")
    assert p.exists()
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["crop_name_he"] == "עלי בייבי"
    assert d["variety"]["name_he"] == "חסה בייבי"
    assert d["species_notes"]


# ─────────────── masterclass re-seed robustness (WP-CB-SRC-SWEEP) ────────────

def test_masterclass_default_variety_robust_to_duplicate_nulls():
    """_default_variety_id must not crash when a crop has >1 null-name variety.

    Re-seed drift accumulates extra name_en=NULL stubs; the resolver must pick the
    is_default baseline (was .one_or_none() -> MultipleResultsFound).
    """
    from organic_market_agent.crop_book.models import CropFamily, Crop, CropVariety
    from organic_market_agent.crop_book.importer.jmf_masterclass import _default_variety_id
    SessionLocal = _make_db()
    with SessionLocal() as s:
        fam = CropFamily(scientific_name="Asteraceae_mc", name_he="מורכבים_mc")
        s.add(fam)
        s.flush()
        crop = Crop(name_he="מנגולד_mc", family_id=fam.id, category="vegetables")
        s.add(crop)
        s.flush()
        # two null-name varieties: one is_default baseline + one drift stub
        s.add(CropVariety(crop_id=crop.id, name_en=None, name_he=None, is_default=False))
        baseline = CropVariety(crop_id=crop.id, name_en=None, name_he="מצוי-ברירת מחדל", is_default=True)
        s.add(baseline)
        s.flush()
        vid = _default_variety_id(s, crop.id)  # must not raise
        assert vid == baseline.id
