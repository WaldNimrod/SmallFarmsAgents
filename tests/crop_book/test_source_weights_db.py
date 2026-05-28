"""Tests for source_weights_db — DB-backed source weights resolver (WP-C5 Phase A).

Covers:
  - Exact-match lookup in DB
  - Prefix-pattern fallback (e.g. 'WR:cornell' → 'WR:*' row)
  - Hard-override semantics (EX/NI: weight NULL, is_hard_override=True)
  - WR tier presence with weight 0.60 (Decision #5)
  - Cache reset via invalidate_cache()
  - Fallback to Python constants when DB row missing
  - Fallback when DB unavailable (no session, table absent)
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from organic_market_agent.crop_book import source_weights_db
from organic_market_agent.crop_book import source_registry

pytestmark = pytest.mark.crop_book


# ---------------------------------------------------------------------------
# Fixture — in-memory SQLite with crop_source_weights mirror schema
# ---------------------------------------------------------------------------
@pytest.fixture
def session():
    """Yield a SQLAlchemy Session bound to in-memory SQLite with seeded weights."""
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(sa.text("""
            CREATE TABLE crop_source_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_label VARCHAR(100) NOT NULL UNIQUE,
                trust_tier VARCHAR(20) NOT NULL,
                weight NUMERIC(5,4),
                is_hard_override BOOLEAN NOT NULL DEFAULT 0,
                requires_moderation BOOLEAN NOT NULL DEFAULT 0,
                notes TEXT,
                updated_at TEXT
            )
        """))
        # Minimal seed: representative rows from migration 056
        seeds = [
            ("team_00",        "EX", None, 1, 0),
            ("NI:*",           "NI", None, 1, 0),
            ("NI:il_moa",      "NI", None, 1, 0),
            ("JMF",            "PR", 0.70, 0, 0),
            ("PR:*",           "PR", 0.70, 0, 0),
            ("WR:*",           "WR", 0.60, 0, 0),
            ("OP:*",           "OP", 0.55, 0, 0),
            ("OP:CurtisStone", "OP", 0.55, 0, 0),
            ("MK:*",           "MK", 0.40, 0, 0),
            ("WB:*",           "WB", 0.30, 0, 0),
            ("UC:*",           "UC", None, 0, 1),
        ]
        conn.execute(
            sa.text("""
                INSERT INTO crop_source_weights
                  (source_label, trust_tier, weight,
                   is_hard_override, requires_moderation)
                VALUES (:l, :t, :w, :h, :m)
            """),
            [{"l": l, "t": t, "w": w, "h": h, "m": m} for l, t, w, h, m in seeds],
        )

    SessionLocal = sessionmaker(engine, expire_on_commit=False)
    source_weights_db.invalidate_cache()
    with SessionLocal() as s:
        yield s
    source_weights_db.invalidate_cache()


@pytest.fixture
def empty_session():
    """Session bound to a DB *without* the crop_source_weights table —
    forces full fallback to Python constants."""
    engine = sa.create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(engine, expire_on_commit=False)
    source_weights_db.invalidate_cache()
    with SessionLocal() as s:
        yield s
    source_weights_db.invalidate_cache()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestExactMatch:
    def test_team_00_is_hard_override(self, session):
        spec = source_weights_db.get_source_spec("team_00", session=session)
        assert spec.cls == "EX"
        assert spec.weight is None
        assert spec.is_hard_override is True

    def test_jmf_pr_weight(self, session):
        spec = source_weights_db.get_source_spec("JMF", session=session)
        assert spec.cls == "PR"
        assert spec.weight == 0.70
        assert spec.is_hard_override is False

    def test_concrete_ni_label(self, session):
        spec = source_weights_db.get_source_spec("NI:il_moa", session=session)
        assert spec.cls == "NI"
        assert spec.is_hard_override is True


class TestPrefixPatternFallback:
    def test_wr_prefix_resolves_to_060(self, session):
        """Decision #5 — WR tier weight = 0.60 (Option B Moderate)."""
        spec = source_weights_db.get_source_spec(
            "WR:cornell-mediterranean-herbs", session=session
        )
        assert spec.cls == "WR"
        assert spec.weight == 0.60
        assert spec.is_hard_override is False

    def test_unknown_ni_prefix_inherits_hard_override(self, session):
        spec = source_weights_db.get_source_spec("NI:new_source", session=session)
        assert spec.cls == "NI"
        assert spec.is_hard_override is True

    def test_unknown_op_prefix_inherits_055(self, session):
        spec = source_weights_db.get_source_spec("OP:NewFarm_2027", session=session)
        assert spec.cls == "OP"
        assert spec.weight == 0.55

    def test_uc_prefix_inherits_moderation_flag(self, session):
        spec = source_weights_db.get_source_spec("UC:user_42", session=session)
        assert spec.cls == "UC"
        assert spec.requires_moderation is True
        assert spec.weight is None


class TestCacheBehavior:
    def test_cache_hit_does_not_requery_db(self, session):
        # First call — populates cache.
        spec1 = source_weights_db.get_source_spec("JMF", session=session)
        assert spec1.weight == 0.70

        # Mutate DB to simulate weight change.
        session.execute(sa.text(
            "UPDATE crop_source_weights SET weight = 0.99 WHERE source_label = 'JMF'"
        ))
        session.commit()

        # Cache should still return original weight.
        spec_cached = source_weights_db.get_source_spec("JMF", session=session)
        assert spec_cached.weight == 0.70

        # After invalidation, fresh read picks up the change.
        source_weights_db.invalidate_cache()
        spec_fresh = source_weights_db.get_source_spec("JMF", session=session)
        assert spec_fresh.weight == 0.99


class TestFallbackToConstants:
    def test_no_db_row_falls_back_to_python_constants(self, empty_session):
        # Table doesn't exist — DB lookup fails silently → falls back to
        # source_registry constants.
        spec = source_weights_db.get_source_spec("team_00", session=empty_session)
        assert spec.cls == "EX"
        assert spec.is_hard_override is True

    def test_no_db_row_unknown_label_returns_wb_default(self, empty_session):
        spec = source_weights_db.get_source_spec(
            "totally_unknown_source", session=empty_session
        )
        assert spec.cls == "WB"
        assert spec.weight == 0.20


class TestSourceRegistryDelegation:
    """source_registry.get_source_spec must keep its callable signature
    and delegate to source_weights_db transparently — falling back to
    Python constants if no DB is available."""

    def test_legacy_signature_unchanged(self):
        """The legacy entrypoint must still accept (label) only."""
        spec = source_registry.get_source_spec("JMF")
        assert spec.cls == "PR"
        assert spec.weight == 0.70

    def test_wr_prefix_through_legacy_api(self):
        """WR class is reachable via legacy get_source_spec, even with no DB."""
        source_weights_db.invalidate_cache()
        spec = source_registry.get_source_spec("WR:cornell-some-source")
        assert spec.cls == "WR"
        assert spec.weight == 0.60

    def test_wr_in_class_rank(self):
        """CLASS_RANK must include WR slotted between PR and OP."""
        assert "WR" in source_registry.CLASS_RANK
        assert source_registry.CLASS_RANK["PR"] < source_registry.CLASS_RANK["WR"]
        assert source_registry.CLASS_RANK["WR"] < source_registry.CLASS_RANK["OP"]


class TestSeedRegistryShape:
    """Sanity checks on the Python-constant fallback seed."""

    def test_team_00_present_as_ex_hard_override(self):
        spec = source_registry.SOURCE_REGISTRY["team_00"]
        assert spec.cls == "EX"
        assert spec.is_hard_override is True
        assert spec.weight is None

    def test_wr_class_sentinel_present(self):
        spec = source_registry.SOURCE_REGISTRY["_WR_CLASS_SENTINEL"]
        assert spec.cls == "WR"
        assert spec.weight == 0.60
