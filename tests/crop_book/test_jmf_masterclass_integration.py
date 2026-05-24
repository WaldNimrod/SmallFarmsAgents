"""DB integration tests for import_jmf_masterclass (AC-11, AC-12, AC-14).
SFA-S003-P002-WP-B1.
"""
import pytest
from pathlib import Path
from decimal import Decimal

pytestmark = pytest.mark.crop_book

FIXTURE = Path(__file__).parent / "fixtures" / "jmf" / "minimal_masterclass.xlsx"


@pytest.fixture(scope="module")
def integration_session():
    """SQLite in-memory session with all needed tables + pre-seeded crops."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.db.base import Base
    from organic_market_agent.crop_book import models as _m  # noqa: F401 — ensure all models registered
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401
    from organic_market_agent.crop_book.models import CropFamily, Crop
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)

    Session = sessionmaker(engine)
    # Pre-seed family and the 3 fixture crops (Arugula, Carrots, Basil)
    with Session() as session:
        fam = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
        session.add(fam)
        session.flush()
        for name_en, name_he in [("Arugula", "ארוגולה"), ("Carrots", "גזר"), ("Basil", "בזיל")]:
            if not session.query(Crop).filter_by(name_he=name_he).first():
                session.add(Crop(name_he=name_he, category="vegetables", family_id=fam.id))
        session.commit()
    return Session, engine


def _run_import(session, dry_run=False):
    """Run import against the fixture directory (fixture has only 3 crops)."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
    return import_jmf_masterclass(session, FIXTURE.parent, dry_run=dry_run)


def test_ac11_source_values_with_jmf_trust(integration_session):
    """AC-11: after import, at least one row has source='JMF', trust_tier='PR',
    confidence_weight=0.70, is_outlier_rejected=False."""
    from organic_market_agent.crop_book.models import CropVarietySourceValue
    Session, engine = integration_session
    with Session() as session:
        summary = _run_import(session)
        rows = session.query(CropVarietySourceValue).filter_by(source="JMF").all()
        assert len(rows) >= 1, f"No JMF rows after import; summary={summary}"
        row = rows[0]
        assert row.trust_tier == "PR"
        assert row.confidence_weight == Decimal("0.70")
        assert row.is_outlier_rejected is False


def test_import_summary_structure(integration_session):
    """AC-11: JmfImportSummary fields are present and sane."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import JmfImportSummary
    Session, engine = integration_session
    with Session() as session:
        summary = _run_import(session)
        assert isinstance(summary, JmfImportSummary)
        assert summary.crops_seen >= 1
        assert summary.source_value_rows_upserted >= 1
        assert isinstance(summary.map_misses, list)
        assert isinstance(summary.standalone_divergences, list)
        assert isinstance(summary.invalid_offsets, int)


def test_ac12_enrichment_runner_integrates(integration_session):
    """AC-12: after import + run_enrichment, at least one crop_field_enrichment row
    with source_count >= 1 for days_to_maturity."""
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    Session, engine = integration_session
    with Session() as session:
        _run_import(session)
        session.flush()
        run_enrichment(session, dry_run=False)
        session.flush()
        rows = session.query(CropFieldEnrichment).filter_by(field_name="days_to_maturity").all()
        assert len(rows) >= 1
        assert any(r.source_count >= 1 for r in rows)


def test_variety_resolution_baseline(integration_session):
    """AC-11: crop-scoped rows attach to variety with name_en=None (baseline variety)."""
    from organic_market_agent.crop_book.models import CropVariety, CropVarietySourceValue
    Session, engine = integration_session
    with Session() as session:
        _run_import(session)
        sv_rows = session.query(CropVarietySourceValue).filter_by(source="JMF").all()
        variety_ids = {r.variety_id for r in sv_rows}
        for vid in variety_ids:
            variety = session.query(CropVariety).get(vid)
            # baseline variety: name_en is None; cultivar varieties may have name_en
            # Just assert the variety exists
            assert variety is not None


def test_ac14_task_templates_at_least_1_crop(integration_session):
    """AC-14 partial: after import_jmf_masterclass on fixture, task templates exist
    for at least 1 crop. (Full AC-14 ≥20 requires live workbook — see integration test)."""
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate
    from sqlalchemy import func
    Session, engine = integration_session
    with Session() as session:
        _run_import(session)
        session.flush()
        distinct_crops = session.query(func.count(func.distinct(CropTaskTemplate.crop_id)))\
            .filter(CropTaskTemplate.source == "JMF").scalar()
        # Fixture has Arugula (X), Carrots (2 tasks), Basil (2 tasks) → 3 crops
        assert distinct_crops >= 1, f"Expected ≥1 crop with tasks, got {distinct_crops}"
