"""WP-C6 — sparse-crop expansion tests.

Static checks (always run): the WR pack is well-formed, every crop supplies >=6
fields from the canonical enrichment vocabulary, and the importer's crop map is
complete + matches the pack.

Integration check (opt-in): if the live dev DB is reachable, assert all 19 sparse
crops have >=6 rows in crop_field_enrichment. Skips cleanly when no DB.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

PACK = Path(
    "data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json"
)

# The 19 sparse crops (DB crop_id) — WP-C6 LOD400 §2 / COVERAGE_SNAPSHOT.
SPARSE_CROP_IDS = [1, 5, 13, 16, 22, 23, 24, 28, 29, 31, 32, 34, 37, 38, 43, 47, 48, 50, 57]

# Canonical numeric enrichment field vocabulary (subset that enrichment computes).
CANONICAL_FIELDS = {
    "days_to_maturity", "germination_temp_c_min", "germination_temp_c_opt",
    "germination_temp_c_max", "in_row_spacing_cm", "rows_per_bed",
    "soil_ph_target", "soil_ph_liming_threshold", "seeds_per_gram",
    "storage_temp_c_min", "storage_temp_c_max", "storage_rh_pct_min",
    "storage_rh_pct_max", "storage_life_days", "nutrient_removal_n_kg_ha",
    "nutrient_removal_p_kg_ha", "nutrient_removal_k_kg_ha",
    "harvest_window_max_days", "days_in_gh_total", "plants_per_m2",
    "yield_per_m2_kg", "succession_interval_weeks",
}


@pytest.fixture(scope="module")
def pack() -> dict:
    return json.loads(PACK.read_text(encoding="utf-8"))


def test_pack_loads_and_has_19_crops(pack):
    assert pack["source_label"] == "WR:claude_sparse_crops_v1"
    assert pack["trust_tier"] == "WR"
    assert abs(float(pack["confidence"]) - 0.60) < 1e-9
    assert len(pack["crops"]) == 19


def test_each_crop_supplies_at_least_6_fields(pack):
    shortfalls = []
    for c in pack["crops"]:
        n = len(c.get("fields", {}))
        if n < 6:
            shortfalls.append((c["crop_id"], n))
    assert not shortfalls, f"crops with <6 fields: {shortfalls}"


def test_all_fields_in_canonical_vocabulary(pack):
    unknown = set()
    for c in pack["crops"]:
        for fn in c.get("fields", {}):
            if fn not in CANONICAL_FIELDS:
                unknown.add(fn)
    assert not unknown, f"non-canonical field_names in pack: {unknown}"


def test_numeric_ranges_sane(pack):
    """min <= max where both present (germination + storage temps)."""
    for c in pack["crops"]:
        f = c.get("fields", {})
        for lo, hi in [("germination_temp_c_min", "germination_temp_c_max"),
                       ("storage_temp_c_min", "storage_temp_c_max"),
                       ("storage_rh_pct_min", "storage_rh_pct_max")]:
            if lo in f and hi in f:
                assert float(f[lo]["value"]) <= float(f[hi]["value"]), \
                    f"{c['crop_id']}: {lo} > {hi}"


def test_importer_crop_map_matches_pack(pack):
    from organic_market_agent.crop_book.importer.ni.claude_sparse_crops_research import (
        CLAUDE_SPARSE_CROP_MAP,
    )
    assert len(CLAUDE_SPARSE_CROP_MAP) == 19
    pack_ids = {c["crop_id"] for c in pack["crops"]}
    assert set(CLAUDE_SPARSE_CROP_MAP.keys()) == pack_ids


def _db_session():
    """Return a live session or None if DB unreachable."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        if not os.environ.get("DATABASE_URL"):
            return None
        from sqlalchemy import text as _text
        from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
        from organic_market_agent.db.session import SessionFactory, engine
        # SQLAlchemy engines/sessions are lazy — construction alone never raises even when
        # the DB is unreachable. Probe connectivity explicitly (mirrors conftest.py's
        # db_session fixture) so a stale/unset DATABASE_URL correctly returns None (skip)
        # instead of failing hard later inside the test body.
        with engine.connect() as conn:
            conn.execute(_text("SELECT 1"))
        return SessionFactory()
    except Exception:
        return None


def test_live_db_all_19_crops_have_6plus_enriched_fields():
    sess = _db_session()
    if sess is None:
        pytest.skip("live DB not reachable; integration check skipped")
    from sqlalchemy import text
    with sess as session:
        rows = session.execute(text(
            """
            SELECT c.id, COUNT(DISTINCT cfe.field_name) AS ef
            FROM crops c
            LEFT JOIN crop_varieties v ON v.crop_id = c.id
            LEFT JOIN crop_field_enrichment cfe ON cfe.variety_id = v.id
            WHERE c.id = ANY(:ids)
            GROUP BY c.id
            """
        ), {"ids": SPARSE_CROP_IDS}).all()
        cov = {r[0]: r[1] for r in rows}
        missing = [cid for cid in SPARSE_CROP_IDS if cov.get(cid, 0) < 6]
        assert not missing, f"crops below 6 enriched fields: {missing} (cov={cov})"
