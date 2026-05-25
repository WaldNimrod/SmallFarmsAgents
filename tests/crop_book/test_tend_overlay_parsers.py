"""Tests for tend_overlay.py parsers against fixture CSVs.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-05, AC-09 (parse layer).
"""
import csv
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = Path("tests/crop_book/fixtures/tend_2022")
TASKS_CSV = FIXTURE_DIR / "TASKS.CSV"
GH_PLAN_CSV = FIXTURE_DIR / "GREENHOUSE_PLAN.CSV"
HARVESTS_CSV = FIXTURE_DIR / "HARVESTS.CSV"


class TestParseTasksTemplates:
    """AC-05: parse_tasks_templates returns whitelisted rows, filters blacklisted."""

    def test_fixture_tasks_parse(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, counts = parse_tasks_templates(TASKS_CSV, year=2022)
        assert len(results) > 0, "Expected some whitelisted rows"
        # Blacklisted rows (Maintenance, Irrigate, Prune) must be filtered
        assert counts["blacklist_filtered"] >= 3
        # Non-listed rows should also be counted
        assert counts["whitelist_filtered"] + counts["blacklist_filtered"] > 0

    def test_task_dicts_have_required_keys(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, _ = parse_tasks_templates(TASKS_CSV, year=2022)
        required = {"name_he", "source", "trust_tier", "task_type",
                    "timing_anchor", "days_offset"}
        for r in results:
            missing = required - r.keys()
            assert not missing, f"Row missing keys: {missing}"

    def test_source_label(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, _ = parse_tasks_templates(TASKS_CSV, year=2022)
        assert all(r["source"] == "Tend_2022" for r in results)

    def test_trust_tier_is_op(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, _ = parse_tasks_templates(TASKS_CSV, year=2022)
        assert all(r["trust_tier"] == "OP" for r in results)


class TestParseGreenhousePlan:
    """AC-08: parse_greenhouse_plan produces days_in_gh_total + days_to_first_potting."""

    def test_fixture_gh_plan_parse(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_greenhouse_plan

        results = parse_greenhouse_plan(GH_PLAN_CSV, year=2022)
        assert len(results) > 0, "Expected greenhouse plan rows"

    def test_field_names_present(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_greenhouse_plan

        results = parse_greenhouse_plan(GH_PLAN_CSV, year=2022)
        field_names = {r["field_name"] for r in results}
        # At least one of the two fields should be present
        assert field_names & {"days_in_gh_total", "days_to_first_potting"}

    def test_trust_tier_and_weight(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_greenhouse_plan
        from decimal import Decimal

        results = parse_greenhouse_plan(GH_PLAN_CSV, year=2022)
        for r in results:
            assert r["trust_tier"] == "OP"
            assert r["confidence_weight"] == Decimal("0.55")


class TestParseHarvestsAggregate:
    """AC-09: parse_harvests_aggregate never emits per-record rows."""

    def test_fixture_harvest_aggregate(self):
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        results, raw_count = parse_harvests_aggregate(HARVESTS_CSV, year=2022)
        # Fixture has 15 rows, 3 crops, each in one season
        assert raw_count == 15
        # Aggregated: max 3 crops × 4 seasons = 12 (fixture has 3 distinct crop+season groups)
        assert len(results) <= 3 * 4

    def test_aggregation_never_equals_raw_count(self):
        """Emitted aggregate rows << raw input rows (no per-record pass-through)."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        results, raw_count = parse_harvests_aggregate(HARVESTS_CSV, year=2022)
        # With 15 raw rows and 3 crops in 1 season each, aggregated count should be 3
        assert len(results) < raw_count

    def test_empty_csv_edge_case(self):
        """Empty HARVESTS CSV returns empty list without error."""
        from organic_market_agent.crop_book.importer.tend_overlay import parse_harvests_aggregate

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            w = csv.DictWriter(f, fieldnames=["Harvest Date", "Plantings",
                                               "Plantings Assigned", "Amount", "Amount Unit"])
            w.writeheader()
            tmp_path = Path(f.name)

        try:
            results, raw_count = parse_harvests_aggregate(tmp_path, year=2022)
            assert results == []
            assert raw_count == 0
        finally:
            tmp_path.unlink()
