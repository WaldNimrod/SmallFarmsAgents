"""WP-C3 integration test — source_registry entries and import chain smoke test."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.crop_book


def test_c3_source_registry_entries():
    """All WP-C3 OP sources resolve correctly in source_registry."""
    from organic_market_agent.crop_book.source_registry import get_source_spec

    c3_sources = [
        ("OP:CurtisStone", "OP", 0.55),
        ("NI:curtis_stone_book", "NI", None),
        ("OP:Idan_seedlings", "OP", 0.55),
        ("OP:FRANCHI_catalog", "OP", 0.55),
        ("OP:Idan_2018", "OP", 0.55),
    ]
    for label, expected_cls, expected_weight in c3_sources:
        spec = get_source_spec(label)
        assert spec.cls == expected_cls, f"{label}: expected cls={expected_cls}, got {spec.cls}"
        if expected_weight is not None:
            assert abs(spec.weight - expected_weight) < 0.001, f"{label}: weight mismatch"
        else:
            assert spec.weight is None or spec.is_hard_override, f"{label}: should be hard override"
