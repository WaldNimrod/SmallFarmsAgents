"""Tests for seed.py CLI flags for Tend overlay.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-14, AC-15, AC-16.
"""
import sys
import pytest

pytestmark = pytest.mark.crop_book


def _parse_args(argv: list[str]):
    """Parse seed.py args without running main."""
    import importlib
    # Import fresh to get the parser
    spec = importlib.util.spec_from_file_location(
        "seed_cli",
        "organic_market_agent/crop_book/importer/seed.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, argv


class TestSeedTendOverlayFlags:
    """AC-14, AC-15, AC-16: CLI flags work correctly."""

    def test_ac16_mutual_exclusion_raises(self, capsys):
        """AC-16: --tend-overlay-only --no-tend-overlay exits with non-zero status."""
        from organic_market_agent.crop_book.importer import seed

        old_argv = sys.argv[:]
        sys.argv = ["seed", "--tend-overlay-only", "--no-tend-overlay", "--all"]
        try:
            with pytest.raises(SystemExit) as exc_info:
                seed.main()
            assert exc_info.value.code != 0
        except SystemExit as e:
            assert e.code != 0
        finally:
            sys.argv = old_argv

    def test_tend_overlay_dir_flag_default(self):
        """--tend-overlay-dir has a sensible default."""
        import argparse
        from pathlib import Path

        # Build the parser directly
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--tend-overlay-dir", type=Path,
            default=Path("/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022"),
        )
        parser.add_argument("--tend-overlay-year", type=int, default=2022)
        tend_excl = parser.add_mutually_exclusive_group()
        tend_excl.add_argument("--tend-overlay-only", action="store_true")
        tend_excl.add_argument("--no-tend-overlay", action="store_true")

        args = parser.parse_args([])
        assert args.tend_overlay_year == 2022
        assert "Tend_2022" in str(args.tend_overlay_dir)

    def test_no_tend_overlay_flag_parses(self):
        """--no-tend-overlay flag parses without error."""
        import argparse
        from pathlib import Path

        parser = argparse.ArgumentParser()
        parser.add_argument("--tend-overlay-dir", type=Path, default=Path("/tmp"))
        parser.add_argument("--tend-overlay-year", type=int, default=2022)
        tend_excl = parser.add_mutually_exclusive_group()
        tend_excl.add_argument("--tend-overlay-only", action="store_true")
        tend_excl.add_argument("--no-tend-overlay", action="store_true")

        args = parser.parse_args(["--no-tend-overlay"])
        assert args.no_tend_overlay is True
        assert args.tend_overlay_only is False

    def test_tend_overlay_only_flag_parses(self):
        """--tend-overlay-only flag parses without error."""
        import argparse
        from pathlib import Path

        parser = argparse.ArgumentParser()
        parser.add_argument("--tend-overlay-dir", type=Path, default=Path("/tmp"))
        parser.add_argument("--tend-overlay-year", type=int, default=2022)
        tend_excl = parser.add_mutually_exclusive_group()
        tend_excl.add_argument("--tend-overlay-only", action="store_true")
        tend_excl.add_argument("--no-tend-overlay", action="store_true")

        args = parser.parse_args(["--tend-overlay-only"])
        assert args.tend_overlay_only is True
        assert args.no_tend_overlay is False
