"""Tests for CW-07 UF/IFAS companion matrix."""
import pytest

pytestmark = pytest.mark.crop_book


class TestUfIfasCompanion:
    def test_parse_minimum_pairs(self):
        from organic_market_agent.crop_book.importer.web.uf_ifas_companion import (
            parse_uf_ifas_companion,
        )
        rows = parse_uf_ifas_companion(None)
        assert len(rows) >= 20

    def test_canonical_pair_ordering(self):
        from organic_market_agent.crop_book.importer.web._shared import canonical_pair_ids

        assert canonical_pair_ids(5, 3) == (3, 5)
        assert canonical_pair_ids(2, 2) == (2, 2)
