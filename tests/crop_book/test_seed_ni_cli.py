"""Tests for seed.py NI CLI flags — AC-13 (--ni-only, --no-ni, mutual exclusion).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §8 / §9.
"""
import subprocess
import sys
import pytest

pytestmark = pytest.mark.crop_book

SEED_CMD = [sys.executable, "-m", "organic_market_agent.crop_book.importer.seed"]


class TestSeedNiCli:
    """AC-13: --ni-only, --no-ni, and mutual exclusion."""

    def test_ac13_ni_only_and_no_ni_mutually_exclusive(self):
        """--ni-only and --no-ni together should produce error."""
        result = subprocess.run(
            SEED_CMD + ["--all", "--ni-only", "--no-ni", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "seed.py should exit non-zero when --ni-only and --no-ni are both specified"
        )
        # argparse produces an error message
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()

    def test_ac13_help_contains_ni_flags(self):
        """--help output should include --ni-only and --no-ni."""
        result = subprocess.run(
            SEED_CMD + ["--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--ni-only" in result.stdout
        assert "--no-ni" in result.stdout

    def test_ac03_ni_importer_classes_count(self):
        """AC-03: NI_IMPORTER_CLASSES has exactly 7 entries (+jmf_ft_mesclun, WP-CB-SRC-SWEEP)."""
        from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES

        assert len(NI_IMPORTER_CLASSES) == 7

    def test_ac03_source_labels(self):
        """AC-03: All 7 source labels are correct."""
        from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES

        labels = {cls().source_label for cls in NI_IMPORTER_CLASSES}
        assert labels == {
            "NI:jmf_book_v1",
            "NI:jmf_book_alt_v1",
            "NI:jmf_ft_flameweed_v1",
            "NI:jmf_ft_biopesticide_v1",
            "NI:jmf_ft_phytoprotection_v1",
            "NI:jmf_ft_nurseryseeding_v1",
            "NI:jmf_ft_mesclun_v1",
        }

    def test_ac03b_b2_subclasses_absent_from_registry(self):
        """AC-03b: B2 subclasses are NOT in ni_registry.registered_labels."""
        from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES
        from organic_market_agent.crop_book.importer.ni_importer import ni_registry

        b2_labels = {cls().source_label for cls in NI_IMPORTER_CLASSES}
        registered = set(ni_registry.registered_labels)
        intersection = b2_labels & registered
        assert len(intersection) == 0, (
            f"B2 subclasses must NOT be in ni_registry; found: {intersection}"
        )

    def test_ac13_ni_only_dry_run_suppresses_jmf_and_tend(self):
        """AC-13 regression: --ni-only --dry-run must NOT run JMF MasterClass or Tend.

        F-LV-B2-01 fix verification: captures stdout+stderr and asserts zero lines
        containing JMF MasterClass, Seeding crop_families, or Parsed ... Tend markers.
        """
        result = subprocess.run(
            SEED_CMD + ["--all", "--ni-only", "--dry-run"],
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr

        # These strings appear in JMF MasterClass and Tend output — must be absent
        forbidden_patterns = [
            "JMF MasterClass:",
            "Seeding crop_families",
            "Parsed",
        ]
        violations = [
            line
            for line in combined.splitlines()
            if any(pat in line for pat in forbidden_patterns)
        ]
        assert not violations, (
            "--ni-only --dry-run must not run JMF MasterClass or Tend; "
            f"found forbidden output lines:\n" + "\n".join(violations)
        )
        # Sanity: the command should succeed (exit 0)
        assert result.returncode == 0, (
            f"seed --ni-only --dry-run exited {result.returncode};\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
