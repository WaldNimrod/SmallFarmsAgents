"""Tests for cover_crops_importer (L12) — WP-C1 AC-C1-08."""
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

L12 = Path("data/external_sources/jmf_extension/L12_cover_crop_chart.pdf")


class TestCoverCropsImporter:
    def test_parse_cover_crops(self):
        from organic_market_agent.crop_book.importer.jmf.cover_crops_importer import (
            parse_cover_crops,
        )

        rows = parse_cover_crops(L12)
        assert len(rows) >= 10

    def test_category_grouping(self):
        from organic_market_agent.crop_book.importer.jmf.cover_crops_importer import (
            parse_cover_crops,
        )

        rows = parse_cover_crops(L12)
        categories = {r["category"] for r in rows}
        assert "legume" in categories or "cereal" in categories

    def test_temp_zone_coercion(self):
        from organic_market_agent.crop_book.importer.jmf.cover_crops_importer import (
            _parse_temp_c,
            _parse_zone,
        )

        assert _parse_temp_c("45°F (7°C)") == 7
        assert _parse_zone("Hardiness zone 7") == 7
