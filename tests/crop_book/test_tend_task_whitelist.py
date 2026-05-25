"""Tests for TEND_TASK_WHITELIST and TEND_TASK_BLACKLIST constants.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-04, AC-05.
"""
import pytest

pytestmark = pytest.mark.crop_book

FIXTURE_TASKS = "tests/crop_book/fixtures/tend_2022/TASKS.CSV"


class TestTendTaskWhitelistConstants:
    """AC-04: TEND_TASK_WHITELIST + TEND_TASK_BLACKLIST importable with correct counts."""

    def test_whitelist_importable(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_WHITELIST
        assert isinstance(TEND_TASK_WHITELIST, frozenset)

    def test_whitelist_count(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_WHITELIST
        assert len(TEND_TASK_WHITELIST) == 11, (
            f"Expected 11 whitelist entries, got {len(TEND_TASK_WHITELIST)}"
        )

    def test_blacklist_importable(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_BLACKLIST
        assert isinstance(TEND_TASK_BLACKLIST, frozenset)

    def test_blacklist_count(self):
        from organic_market_agent.crop_book.constants import TEND_TASK_BLACKLIST
        assert len(TEND_TASK_BLACKLIST) == 10, (
            f"Expected 10 blacklist entries, got {len(TEND_TASK_BLACKLIST)}"
        )

    def test_option_b_additions_in_whitelist(self):
        """Trellis and Fertilize & Amend are in whitelist (Option B)."""
        from organic_market_agent.crop_book.constants import TEND_TASK_WHITELIST
        assert "Trellis" in TEND_TASK_WHITELIST
        assert "Fertilize & Amend" in TEND_TASK_WHITELIST

    def test_original_9_in_whitelist(self):
        """All 9 original PROGRAM_BRIEF §4 categories are in whitelist."""
        from organic_market_agent.crop_book.constants import TEND_TASK_WHITELIST
        originals = {
            "Transplant", "Greenhouse Sow", "Direct Sow", "Weed",
            "Row Cover & Mulch", "Stale Bed", "Pest & Disease",
            "Potting up", "Thin",
        }
        missing = originals - TEND_TASK_WHITELIST
        assert not missing, f"Missing from whitelist: {missing}"


class TestTendTaskWhitelistParsing:
    """AC-05: Parse fixture TASKS.CSV — whitelisted rows included; blacklisted rows excluded."""

    def test_whitelisted_rows_returned(self):
        """Whitelisted task types produce output dicts."""
        from pathlib import Path
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, counts = parse_tasks_templates(Path(FIXTURE_TASKS), year=2022)
        task_types = {r["task_type"] for r in results}
        # Transplant → at_seeding_transplanting
        assert "at_seeding_transplanting" in task_types

    def test_blacklisted_rows_excluded(self):
        """Blacklisted task types (Maintenance, Irrigate, Prune) are excluded."""
        from pathlib import Path
        from organic_market_agent.crop_book.constants import TEND_TASK_BLACKLIST
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        results, counts = parse_tasks_templates(Path(FIXTURE_TASKS), year=2022)
        assert counts["blacklist_filtered"] >= 3  # Maintenance, Irrigate, Prune

    def test_non_listed_rows_dropped_with_warn(self, caplog):
        """Task types not in whitelist or blacklist are counted as whitelist_filtered."""
        import csv
        import tempfile
        from pathlib import Path
        from organic_market_agent.crop_book.importer.tend_overlay import parse_tasks_templates

        # Write a CSV with an unknown task type
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            w = csv.DictWriter(f, fieldnames=["Task Type", "Method", "Sub-method",
                                               "Plantings Assigned", "Input", "Description"])
            w.writeheader()
            w.writerow({
                "Task Type": "UnknownTaskXYZ",
                "Method": "",
                "Sub-method": "",
                "Plantings Assigned": "Tomatoes 01/01/2022",
                "Input": "",
                "Description": "",
            })
            tmp_path = Path(f.name)

        import logging
        with caplog.at_level(logging.WARNING):
            results, counts = parse_tasks_templates(tmp_path, year=2022)

        assert counts["whitelist_filtered"] >= 1
        tmp_path.unlink()
