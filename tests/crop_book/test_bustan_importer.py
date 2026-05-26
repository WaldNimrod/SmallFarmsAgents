"""Tests for bustan_importer (L36) — WP-C1 AC-C1-06."""
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

L36 = Path("data/external_sources/israeli/L36_BUSTAN_sowing_calendar.pdf")


class TestBustanImporter:
    def test_parse_extracts_crops(self):
        from organic_market_agent.crop_book.importer.israeli.bustan_importer import (
            parse_bustan,
        )

        rows = parse_bustan(L36)
        crops = {r.crop_name_he for r in rows}
        assert len(crops) >= 20

    def test_month_flags_set(self):
        from organic_market_agent.crop_book.importer.israeli.bustan_importer import (
            parse_bustan,
        )

        rows = parse_bustan(L36)
        assert any(r.month_mar or r.month_sep or r.month_oct for r in rows)

    def test_bustan_legend_decoding(self):
        from organic_market_agent.crop_book.importer.israeli._shared import (
            decode_bustan_token,
        )

        assert decode_bustan_token("ש/ז") == {"seed", "transplant"}
        assert decode_bustan_token("ז") == {"seed"}
        assert decode_bustan_token("ש") == {"transplant"}
