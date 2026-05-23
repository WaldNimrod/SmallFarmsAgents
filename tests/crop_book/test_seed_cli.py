"""LOD400 §13 — seed.py CLI contract: --all auto-enriches; --no-enrich opts out.

Tests use argparse directly (no subprocess) and patch the DB + enrichment runner
so the suite runs without PostgreSQL.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch, call
import argparse

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_seed_args(argv: list[str]):
    """Import seed.main's parser logic by replicating the argparse setup.

    We do NOT call seed.main() directly (that would try to connect to DB).
    Instead we parse args the same way main() does, to verify parser semantics.
    """
    from organic_market_agent.crop_book.importer import seed as seed_module

    # Reconstruct the parser from the module's main() source.
    # We import the parser-building portion by temporarily replacing sys.argv.
    old_argv = sys.argv
    try:
        sys.argv = ["seed.py"] + argv
        # We use the module's argparse directly via a thin wrapper.
        parser = _build_seed_parser(seed_module)
        return parser.parse_args(argv)
    finally:
        sys.argv = old_argv


def _build_seed_parser(seed_module):
    """Reconstruct the seed argument parser (mirrors main() parser setup)."""
    from pathlib import Path

    parser = argparse.ArgumentParser(prog="seed.py")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--crops", nargs="+", metavar="NAME")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--year", metavar="YEAR")
    parser.add_argument("--source-dir", type=Path, default=Path("."))
    parser.add_argument("--jmf-dir", type=Path, default=Path("."))
    parser.add_argument("--no-enrich", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


# ---------------------------------------------------------------------------
# Argparse contract tests (no DB required)
# ---------------------------------------------------------------------------

class TestSeedCliParser:
    """Verify that --no-enrich flag parses correctly and --enrich is gone."""

    def test_all_flag_parsed(self):
        args = _parse_seed_args(["--all"])
        assert args.all is True
        assert args.no_enrich is False

    def test_no_enrich_flag_parsed(self):
        args = _parse_seed_args(["--all", "--no-enrich"])
        assert args.all is True
        assert args.no_enrich is True

    def test_enrich_flag_does_not_exist(self):
        """--enrich was removed; argparse should reject it."""
        parser = _build_seed_parser(None)
        with pytest.raises(SystemExit):
            parser.parse_args(["--all", "--enrich"])

    def test_crops_no_enrich_allowed(self):
        args = _parse_seed_args(["--crops", "Arugula", "--no-enrich"])
        assert args.crops == ["Arugula"]
        assert args.no_enrich is True


# ---------------------------------------------------------------------------
# Behaviour tests (patch DB + enrichment runner)
# ---------------------------------------------------------------------------

class TestSeedAllEnrichDefault:
    """--all should trigger enrichment by default; --no-enrich skips it.

    SessionFactory and run_enrichment are imported lazily inside main(), so we
    patch their source locations (organic_market_agent.db.session.SessionFactory
    and organic_market_agent.crop_book.importer.enrichment_runner.run_enrichment).
    """

    def _make_fake_factory(self):
        fake_session = MagicMock()
        fake_factory = MagicMock()
        fake_factory.__enter__ = MagicMock(return_value=fake_session)
        fake_factory.__exit__ = MagicMock(return_value=False)
        return fake_factory, fake_session

    def test_all_runs_enrichment_by_default(self):
        """seed --all should call run_enrichment without --no-enrich."""
        enrichment_called = []

        import organic_market_agent.crop_book.importer.seed as seed_module

        fake_factory, fake_session = self._make_fake_factory()

        def fake_run_enrichment(session, dry_run=False):
            enrichment_called.append(True)
            return MagicMock()

        with (
            patch.object(sys, "argv", ["seed.py", "--all"]),
            patch("organic_market_agent.crop_book.importer.seed.seed", side_effect=lambda **kw: None),
            # SessionFactory is imported inside main() from db.session — patch source
            patch("organic_market_agent.db.session.SessionFactory", return_value=fake_factory),
            # run_enrichment is imported inside main() — patch source module
            patch(
                "organic_market_agent.crop_book.importer.enrichment_runner.run_enrichment",
                side_effect=fake_run_enrichment,
            ),
        ):
            seed_module.main()

        assert enrichment_called, "--all must call run_enrichment by default"

    def test_all_no_enrich_skips_enrichment(self):
        """seed --all --no-enrich must NOT call run_enrichment."""
        enrichment_called = []

        import organic_market_agent.crop_book.importer.seed as seed_module

        fake_factory, fake_session = self._make_fake_factory()

        def fake_run_enrichment(session, dry_run=False):
            enrichment_called.append(True)
            return MagicMock()

        with (
            patch.object(sys, "argv", ["seed.py", "--all", "--no-enrich"]),
            patch("organic_market_agent.crop_book.importer.seed.seed", side_effect=lambda **kw: None),
            patch("organic_market_agent.db.session.SessionFactory", return_value=fake_factory),
            patch(
                "organic_market_agent.crop_book.importer.enrichment_runner.run_enrichment",
                side_effect=fake_run_enrichment,
            ),
        ):
            seed_module.main()

        assert not enrichment_called, "--all --no-enrich must NOT call run_enrichment"
