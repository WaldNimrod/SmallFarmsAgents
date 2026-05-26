"""Tests for groworganic_importer (L01) — WP-C1 AC-C1-03/04."""
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

L01 = Path("data/external_sources/israeli/L01_GROWORGANIC_sowing_dates_base.xlsx")


@pytest.fixture(scope="module")
def parsed_rows():
    from organic_market_agent.crop_book.importer.israeli.groworganic_importer import (
        parse_groworganic,
    )
    return parse_groworganic(L01)


class TestGroworganicImporter:
    def test_parses_many_rows(self, parsed_rows):
        assert len(parsed_rows) >= 30

    def test_activity_types_valid(self, parsed_rows):
        for row in parsed_rows:
            assert row.activity_type in ("seed", "transplant")

    def test_sx_split_into_two_activities(self):
        from organic_market_agent.crop_book.importer.israeli._shared import decode_l01_cell

        assert decode_l01_cell("SX") == {"seed", "transplant"}
        assert decode_l01_cell("XS") == {"seed", "transplant"}

        rows = [
            r for r in __import__(
                "organic_market_agent.crop_book.importer.israeli.groworganic_importer",
                fromlist=["parse_groworganic"],
            ).parse_groworganic(L01)
            if "ברוקולי" in r.crop_name_he
        ]
        activities = {r.activity_type for r in rows}
        assert "seed" in activities or "transplant" in activities
