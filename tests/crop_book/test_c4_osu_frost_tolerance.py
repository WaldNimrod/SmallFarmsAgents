"""Tests for CW-02 OSU frost tolerance + cross-validation."""
import pytest

pytestmark = pytest.mark.crop_book


class TestOsuFrostTolerance:
    def test_normalize_frost_labels(self):
        from organic_market_agent.crop_book.importer.web._shared import normalize_frost_label

        assert normalize_frost_label("Hardy") == "hardy"
        assert normalize_frost_label("Semi-hardy") == "semi_hardy"
        assert normalize_frost_label("Very tender") == "very_tender"
        assert normalize_frost_label("Tender") == "tender"

    def test_reconcile_two_of_three(self):
        from organic_market_agent.crop_book.importer.web._shared import reconcile_frost_classes

        chosen, note = reconcile_frost_classes(["hardy", "hardy", "tender"])
        assert chosen == "hardy"
        assert "consensus" in note

    def test_parse_osu_rows(self):
        from organic_market_agent.crop_book.importer.web.osu_frost_tolerance import (
            parse_osu_frost_tolerance,
        )
        rows = parse_osu_frost_tolerance()
        assert len(rows) >= 15
        assert all(r["frost_tolerance_class"] in (
            "hardy", "semi_hardy", "tender", "very_tender"
        ) for r in rows)
