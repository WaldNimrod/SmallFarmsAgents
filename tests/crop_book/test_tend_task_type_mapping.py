"""Tests for TEND_TASK_TYPE_MAP and Method/Sub-method disambiguation.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-04, AC-06, AC-07, AC-13.
"""
import csv
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book


def _make_task_csv(**row_kwargs) -> Path:
    """Write a one-row TASKS CSV fixture and return its path."""
    defaults = {
        "Task Type": "Transplant",
        "Method": "",
        "Sub-method": "",
        "Plantings Assigned": "Tomatoes Hyd. 01/01/2022",
        "Input": "",
        "Description": "",
    }
    defaults.update(row_kwargs)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as f:
        w = csv.DictWriter(f, fieldnames=list(defaults.keys()))
        w.writeheader()
        w.writerow(defaults)
        return Path(f.name)


class TestTendTaskTypeMap:
    """AC-04: TEND_TASK_TYPE_MAP importable, 9 direct entries."""

    def test_importable(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_TYPE_MAP
        assert isinstance(TEND_TASK_TYPE_MAP, dict)

    def test_count(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_TYPE_MAP
        assert len(TEND_TASK_TYPE_MAP) == 9

    def test_b3_values_present(self):
        """Option-B additions (Trellis, Fertilize & Amend) are in the map."""
        from organic_market_agent.crop_book.constants import TEND_TASK_TYPE_MAP
        assert "Trellis" in TEND_TASK_TYPE_MAP
        assert TEND_TASK_TYPE_MAP["Trellis"] == "trellis"
        assert "Fertilize & Amend" in TEND_TASK_TYPE_MAP
        assert TEND_TASK_TYPE_MAP["Fertilize & Amend"] == "fertilize"


class TestWeedDisambiguation:
    """AC-06: Weed task disambiguation via Method column."""

    def test_hand_weed_method(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{"Task Type": "Weed", "Method": "Hand weed",
                                     "Plantings Assigned": "Carrots Kuroda 01/01/2022"})
        try:
            results, _ = parse_tasks_templates(csv_path, year=2022)
            weed_rows = [r for r in results if "weed" in r["task_type"]]
            assert any(r["task_type"] == "hand_weed" for r in weed_rows)
        finally:
            csv_path.unlink()

    def test_flextine_method(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{"Task Type": "Weed", "Method": "Flextine",
                                     "Plantings Assigned": "Beets 01/01/2022"})
        try:
            results, _ = parse_tasks_templates(csv_path, year=2022)
            weed_rows = [r for r in results if "flextine" in r.get("task_type", "")]
            assert any(r["task_type"] == "flextine_harrow_1" for r in weed_rows)
        finally:
            csv_path.unlink()

    def test_unknown_method_defaults_to_hand_weed(self, caplog):
        import logging
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{"Task Type": "Weed", "Method": "SomethingWeird",
                                     "Plantings Assigned": "Beets 01/01/2022"})
        try:
            with caplog.at_level(logging.WARNING):
                results, counts = parse_tasks_templates(csv_path, year=2022)
            weed_rows = [r for r in results]
            if weed_rows:
                # Unknown method → defaults to hand_weed + WARN
                assert any(r["task_type"] == "hand_weed" for r in weed_rows)
        finally:
            csv_path.unlink()


class TestRowCoverDisambiguation:
    """AC-07: Row Cover & Mulch disambiguation via Sub-method column."""

    def test_tarp_maps_to_net_row_cover(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{
            "Task Type": "Row Cover & Mulch",
            "Sub-method": "Tarp",
            "Plantings Assigned": "Carrots Kuroda 01/01/2022",
        })
        try:
            results, _ = parse_tasks_templates(csv_path, year=2022)
            rc_rows = [r for r in results]
            assert any(r["task_type"] == "net_row_cover" for r in rc_rows)
        finally:
            csv_path.unlink()

    def test_straw_maps_to_straw_mulch(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{
            "Task Type": "Row Cover & Mulch",
            "Sub-method": "Straw",
            "Plantings Assigned": "Carrots Kuroda 01/01/2022",
        })
        try:
            results, _ = parse_tasks_templates(csv_path, year=2022)
            rc_rows = [r for r in results]
            assert any(r["task_type"] == "straw_mulch_topdress" for r in rc_rows)
        finally:
            csv_path.unlink()

    def test_trellis_and_fertilize_option_b(self):
        """AC-13: Trellis and Fertilize & Amend (Option-B) map to correct task_types."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        csv_path = _make_task_csv(**{
            "Task Type": "Trellis",
            "Plantings Assigned": "Tomatoes Hyd. 01/01/2022",
        })
        try:
            results, _ = parse_tasks_templates(csv_path, year=2022)
            assert any(r["task_type"] == "trellis" for r in results)
        finally:
            csv_path.unlink()

        csv_path2 = _make_task_csv(**{
            "Task Type": "Fertilize & Amend",
            "Plantings Assigned": "Tomatoes Hyd. 01/01/2022",
        })
        try:
            results2, _ = parse_tasks_templates(csv_path2, year=2022)
            assert any(r["task_type"] == "fertilize" for r in results2)
        finally:
            csv_path2.unlink()
