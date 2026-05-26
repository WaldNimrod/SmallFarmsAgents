"""Tests for CW-03 UMD soil pH."""
import pytest

pytestmark = pytest.mark.crop_book


class TestUmdSoilPh:
    def test_parse_minimum_crops(self):
        from organic_market_agent.crop_book.importer.web.umd_soil_ph import parse_umd_soil_ph
        rows = parse_umd_soil_ph()
        assert len(rows) >= 30

    def test_ph_fields_present(self):
        from organic_market_agent.crop_book.importer.web.umd_soil_ph import parse_umd_soil_ph
        rows = parse_umd_soil_ph()
        assert all("soil_ph_target" in r for r in rows[:10])
