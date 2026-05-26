"""Tests for CW-06 seeds per gram cross-validation."""
import pytest

pytestmark = pytest.mark.crop_book


class TestSeedsPerGram:
    def test_cross_validate_produces_rows(self):
        from organic_market_agent.crop_book.importer.web.seeds_per_gram import (
            cross_validate_seeds,
        )
        rows = cross_validate_seeds()
        assert len(rows) >= 10

    def test_cross_val_note_when_close(self):
        from organic_market_agent.crop_book.importer.web.seeds_per_gram import (
            cross_validate_seeds,
        )
        rows = cross_validate_seeds()
        cross = [r for r in rows if r.get("note")]
        assert len(cross) >= 1
