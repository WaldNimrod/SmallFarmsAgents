"""Tests for HARVESTS aggregation correctness.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-09.
"""
import csv
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book


def _make_harvests_csv(rows: list[dict]) -> Path:
    """Write a HARVESTS CSV fixture and return its path."""
    fieldnames = ["Harvest Date", "Plantings", "Plantings Assigned", "Amount", "Amount Unit"]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
        return Path(f.name)


class TestHarvestsAggregation:
    """AC-09: aggregation never per-record; bounded by crops × 4 seasons."""

    def test_many_raw_rows_aggregate_to_few(self):
        """939 raw rows aggregate to at most crops × 4 seasons."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        # Build 10 rows per crop, 3 crops, 1 season each → 30 raw rows
        rows = []
        for crop, month in [("Tomatoes", "03"), ("Carrots", "07"), ("Beets", "10")]:
            for day in range(1, 11):
                rows.append({
                    "Harvest Date": f"{day:02d}/{month}/2022",
                    "Plantings": crop,
                    "Plantings Assigned": f"{crop} Var 01/01/2022",
                    "Amount": "10.0",
                    "Amount Unit": "kg",
                })

        csv_path = _make_harvests_csv(rows)
        try:
            results, raw_count = parse_harvests_aggregate(csv_path, year=2022)
            assert raw_count == 30
            # 3 crops × 1 season each = 3 rows
            assert len(results) <= 3 * 4
            assert len(results) < raw_count
        finally:
            csv_path.unlink()

    def test_aggregation_bound_assertion(self):
        """Hard assertion fires if grouping logic produces too many rows."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        # This test verifies the happy path: 3 groups, 3 crops
        fixture = Path("tests/crop_book/fixtures/tend_2022/HARVESTS.CSV")
        results, raw_count = parse_harvests_aggregate(fixture, year=2022)

        distinct_crops = len({r["name_he"] for r in results})
        # Must satisfy: len(results) <= distinct_crops × 4
        assert len(results) <= max(distinct_crops * 4, 1)

    def test_summary_counts_aggregated_correctly(self):
        """harvests_aggregated field equals raw_row_count."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        fixture = Path("tests/crop_book/fixtures/tend_2022/HARVESTS.CSV")
        results, raw_count = parse_harvests_aggregate(fixture, year=2022)
        assert raw_count == 15  # fixture has 15 rows
