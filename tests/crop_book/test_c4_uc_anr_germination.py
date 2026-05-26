"""Tests for CW-01 UC ANR germination importer."""
import pytest

pytestmark = pytest.mark.crop_book


class TestUcAnrGermination:
    def test_parse_returns_rows(self):
        from organic_market_agent.crop_book.importer.web.uc_anr_germination import (
            parse_uc_anr_germination,
        )
        rows = parse_uc_anr_germination()
        assert len(rows) >= 20

    def test_fahrenheit_to_celsius_spot(self):
        from organic_market_agent.crop_book.importer.web._shared import fahrenheit_to_celsius

        assert float(fahrenheit_to_celsius(32)) == 0.0
        assert float(fahrenheit_to_celsius(77)) == 25.0

    def test_tomato_germination_range(self):
        from organic_market_agent.crop_book.importer.web.uc_anr_germination import (
            parse_uc_anr_germination,
        )
        rows = {r["crop_en"]: r for r in parse_uc_anr_germination()}
        assert "Tomato" in rows
        t = rows["Tomato"]
        assert t["germination_temp_c_min"] < t["germination_temp_c_opt"]
        assert t["germination_temp_c_opt"] < t["germination_temp_c_max"]
