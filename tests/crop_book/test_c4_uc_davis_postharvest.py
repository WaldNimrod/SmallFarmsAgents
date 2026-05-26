"""Tests for CW-08 UC Davis postharvest."""
import pytest

pytestmark = pytest.mark.crop_book


class TestUcDavisPostharvest:
    def test_parse_minimum_commodities(self):
        from organic_market_agent.crop_book.importer.web.uc_davis_postharvest import (
            parse_uc_davis_postharvest,
        )
        rows = parse_uc_davis_postharvest(None)
        assert len(rows) >= 30

    def test_scientific_name_field(self):
        from organic_market_agent.crop_book.importer.web.uc_davis_postharvest import (
            parse_uc_davis_postharvest,
        )
        rows = parse_uc_davis_postharvest(None)
        assert rows[0]["scientific_name"]
