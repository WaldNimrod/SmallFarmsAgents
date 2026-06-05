"""Tests for source_registry.py — SFA-S003-P002-WP-A LOD400 §17 Step 10."""

from __future__ import annotations

import pytest


def test_team00_is_ex_hard_override() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("team_00")
    assert spec.cls == "EX"
    assert spec.is_hard_override is True
    assert spec.weight is None


def test_jmf_is_pr_class() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("JMF")
    assert spec.cls == "PR"
    assert spec.weight == 0.70
    assert spec.is_hard_override is False


def test_tend_years_are_op_class() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    for label in ("Tend_2018", "Tend_2019", "Tend_2020", "Tend_2021", "Tend_2022", "Tend"):
        spec = get_source_spec(label)
        assert spec.cls == "OP", f"{label} should be OP class"
        assert spec.weight == 0.55


def test_ni_prefix_detected() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("NI:rehovot_trials_2024")
    assert spec.cls == "NI"
    assert spec.is_hard_override is True
    assert spec.weight is None


def test_oma_prefix_detected_as_mk() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("OMA:tomatoes_2024")
    assert spec.cls == "MK"
    assert spec.weight == 0.40


def test_wb_prefix_detected() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("WB:wikipedia")
    assert spec.cls == "WB"
    assert spec.weight == 0.30


def test_uc_prefix_requires_moderation() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("UC:user123")
    assert spec.cls == "UC"
    assert spec.requires_moderation is True
    # UC weight is NULL by design (DB SSOT seed, migration 056): user-community
    # sources are "excluded from blend until a moderator sets a weight". The blend
    # uses a per-candidate moderation_weight, not this registry placeholder
    # (reconciler.py §requires_moderation). WP-C5 Decision 5 made the DB the SSOT;
    # the prior 0.15 constant was stale once UC:* was seeded NULL.
    assert spec.weight is None


def test_unknown_source_falls_back_to_low_trust_wb() -> None:
    from organic_market_agent.crop_book.source_registry import get_source_spec

    spec = get_source_spec("totally_unknown_source_xyz")
    assert spec.cls == "WB"
    assert spec.weight == 0.20


def test_class_rank_order() -> None:
    from organic_market_agent.crop_book.source_registry import CLASS_RANK

    # EX must have lowest rank (highest priority)
    assert CLASS_RANK["EX"] < CLASS_RANK["NI"] < CLASS_RANK["PR"]
    assert CLASS_RANK["PR"] < CLASS_RANK["OP"] < CLASS_RANK["MK"]
    assert CLASS_RANK["MK"] < CLASS_RANK["WB"] < CLASS_RANK["UC"]


def test_is_hard_override_helper() -> None:
    from organic_market_agent.crop_book.source_registry import is_hard_override

    assert is_hard_override("team_00") is True
    assert is_hard_override("NI:some_file") is True
    assert is_hard_override("JMF") is False
    assert is_hard_override("Tend_2022") is False
