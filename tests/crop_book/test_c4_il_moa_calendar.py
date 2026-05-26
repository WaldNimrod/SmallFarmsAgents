"""Tests for CW-05 IL MoA + Shaham calendar (CRITICAL)."""
import json

import pytest

pytestmark = pytest.mark.crop_book


class TestIlMoaCalendar:
    def test_parse_minimum_rows(self):
        from organic_market_agent.crop_book.importer.web.il_moa_calendar import (
            parse_il_moa_calendar,
        )
        moa, shaham = parse_il_moa_calendar()
        assert len(moa) + len(shaham) >= 30

    def test_hebrew_preservation_in_extract(self):
        from organic_market_agent.crop_book.importer.web._shared import load_extract

        for key in ("il_moa_garden_guide", "shaham_extension"):
            raw = load_extract(key)
            if not raw:
                continue
            blob = json.dumps(raw, ensure_ascii=False)
            assert "\\u05" not in blob or "עגבניה" in blob
            assert "עגבניה" in blob or "חסה" in blob

    def test_ni_source_labels(self):
        from organic_market_agent.crop_book.importer.web.il_moa_calendar import (
            SOURCE_MOA,
            SOURCE_SHAHAM,
        )
        assert SOURCE_MOA == "NI:il_moa_garden_guide"
        assert SOURCE_SHAHAM == "NI:shaham_extension"

    def test_region_constant(self):
        from organic_market_agent.crop_book.importer.web.il_moa_calendar import REGION
        assert REGION == "IL_general"
