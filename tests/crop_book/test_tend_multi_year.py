"""Tests for Tend multi-year overlay (2019–2021) — WP-C1 AC-C1-09..11."""
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

TEND_DIR = Path("data/external_sources/tend_multi_year")


class TestTendMultiYear:
    def test_find_flat_csv_paths(self):
        from organic_market_agent.crop_book.importer.tend_overlay import _find_csv_for_year

        for year in (2019, 2020, 2021):
            p = _find_csv_for_year(
                TEND_DIR, year,
                "HARVESTS (from macBook Air - nimrod).CSV",
                ["harvests.csv"],
            )
            assert p is not None, f"missing HARVESTS for {year}"
            assert p.name.startswith(f"Tend_{year}_")

    def test_harvest_aggregation_counts(self):
        from organic_market_agent.crop_book.importer.tend_overlay import (
            _find_csv_for_year,
            parse_harvests_aggregate,
        )

        expected_raw = {2019: 1884, 2020: 3720, 2021: 1723}
        for year, raw_count in expected_raw.items():
            path = _find_csv_for_year(
                TEND_DIR, year,
                "HARVESTS (from macBook Air - nimrod).CSV",
                ["HARVESTS.CSV", "harvests.csv"],
            )
            _, raw_n = parse_harvests_aggregate(path, year)
            assert raw_n == raw_count, f"year {year}"

    def test_crop_plan_row_counts(self):
        import csv

        expected = {2019: 442, 2020: 724, 2021: 552}
        for year, count in expected.items():
            path = TEND_DIR / f"Tend_{year}_CROP_PLAN.csv"
            with path.open(encoding="utf-8-sig") as fh:
                rows = sum(1 for _ in csv.DictReader(fh))
            assert rows == count
