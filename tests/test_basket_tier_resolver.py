"""Unit tests for CSA basket tier resolution (SPEC-20260408-PHASE-A-LOD400 §C4.8)."""
from __future__ import annotations

import json
from decimal import Decimal
from unittest.mock import MagicMock

from organic_market_agent.normalizer.basket_tier_resolver import (
    _extract_item_count,
    resolve_basket_tier,
)


class TestExtractItemCount:
    def test_explicit_item_count_field(self):
        data = json.dumps({"item_count": 10, "price": 150})
        assert _extract_item_count(data) == 10

    def test_contents_as_list(self):
        data = json.dumps(
            {
                "contents": [
                    "עגבניות",
                    "מלפפון",
                    "גזר",
                    "חסה",
                    "פלפל",
                    "בצל",
                    "קישוא",
                    "תרד",
                    "כוסברה",
                ]
            }
        )
        assert _extract_item_count(data) == 9

    def test_contents_as_string_with_number(self):
        data = json.dumps({"contents": "12 מוצרים שבועיים"})
        assert _extract_item_count(data) == 12

    def test_none_when_empty(self):
        assert _extract_item_count(None) is None

    def test_none_when_no_count_fields(self):
        data = json.dumps({"price": 120})
        assert _extract_item_count(data) is None

    def test_plain_text_multiline(self):
        text = "עגבניות\nמלפפון\nגזר\nחסה\nפלפל\nבצל"
        assert _extract_item_count(text) == 6


class TestResolveTier:
    def setup_method(self):
        self.mock_session = MagicMock()

    def test_tier_small_by_item_count(self):
        """6 items → PRD025 (small: 5–8 items)"""
        ctx_json = json.dumps({"item_count": 6})
        code, note = resolve_basket_tier(ctx_json, Decimal("100"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_item_count"

    def test_tier_medium_by_item_count(self):
        """11 items → PRD026 (medium: 9–13 items)"""
        ctx_json = json.dumps({"item_count": 11})
        code, note = resolve_basket_tier(ctx_json, Decimal("150"), self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_by_item_count"

    def test_tier_large_by_item_count(self):
        """15 items → PRD027 (large: 14+ items)"""
        ctx_json = json.dumps({"item_count": 15})
        code, note = resolve_basket_tier(ctx_json, Decimal("220"), self.mock_session)
        assert code == "PRD027"
        assert note == "basket_tier_by_item_count"

    def test_tier_medium_by_price_fallback(self):
        """No item count, price ₪150 → PRD026 (price range ₪130–180)"""
        code, note = resolve_basket_tier(None, Decimal("150"), self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_by_price"

    def test_tier_small_by_price_fallback(self):
        """No item count, price ₪95 → PRD025 (price range ₪80–130)"""
        code, note = resolve_basket_tier(None, Decimal("95"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_price"

    def test_tier_default_when_no_data(self):
        """No count, no price → PRD026 (default medium)"""
        code, note = resolve_basket_tier(None, None, self.mock_session)
        assert code == "PRD026"
        assert note == "basket_tier_default_medium"

    def test_too_small_basket_returns_none(self):
        """< 5 items → None (scope-skip signal)"""
        ctx_json = json.dumps({"item_count": 3})
        code, note = resolve_basket_tier(ctx_json, Decimal("50"), self.mock_session)
        assert code is None
        assert note == "basket_too_small"

    def test_count_priority_over_price(self):
        """Item count takes priority over price even if price would resolve differently"""
        ctx_json = json.dumps({"item_count": 6})
        code, note = resolve_basket_tier(ctx_json, Decimal("160"), self.mock_session)
        assert code == "PRD025"
        assert note == "basket_tier_by_item_count"

    def test_oversized_by_price_above_band(self):
        """Price above ₪250 large band → PRD027 with oversized note (mandate canonical API)"""
        code, note = resolve_basket_tier(None, Decimal("300"), self.mock_session)
        assert code == "PRD027"
        assert note == "basket_tier_oversized_default_large"

    def test_oversized_by_extreme_item_count(self):
        """Extreme item count → PRD027 with oversized note"""
        ctx_json = json.dumps({"item_count": 10000})
        code, note = resolve_basket_tier(ctx_json, Decimal("1"), self.mock_session)
        assert code == "PRD027"
        assert note == "basket_tier_oversized_default_large"
