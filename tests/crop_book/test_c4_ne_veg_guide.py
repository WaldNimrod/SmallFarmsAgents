"""Tests for CW-04 NE Veg Guide nutrients."""
from decimal import Decimal

import pytest

pytestmark = pytest.mark.crop_book


class TestNeVegGuide:
    def test_lbs_acre_conversion(self):
        from organic_market_agent.crop_book.importer.web._shared import lbs_acre_to_kg_ha

        assert float(lbs_acre_to_kg_ha(100)) == pytest.approx(112.09, rel=0.01)

    def test_p2o5_to_p_factor(self):
        from organic_market_agent.crop_book.importer.web._shared import P2O5_TO_P

        assert P2O5_TO_P == Decimal("0.4364")

    def test_parse_nutrient_rows(self):
        from organic_market_agent.crop_book.importer.web.ne_veg_guide_nutrients import (
            parse_ne_veg_guide,
        )
        rows = parse_ne_veg_guide(None)
        assert len(rows) >= 15
        assert rows[0]["nutrient_removal_n_kg_ha"] > 0
