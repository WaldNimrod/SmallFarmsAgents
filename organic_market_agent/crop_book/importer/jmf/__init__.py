"""JMF importers package (WP-C1 cover crops + legacy jmf.py re-exports)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_legacy_path = Path(__file__).resolve().parent.parent / "jmf.py"
_spec = importlib.util.spec_from_file_location(
    "organic_market_agent.crop_book.importer._jmf_legacy",
    _legacy_path,
)
_legacy = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_legacy)

parse_jmf_dir = _legacy.parse_jmf_dir

from organic_market_agent.crop_book.importer.jmf.cover_crops_importer import (  # noqa: E402
    import_all as import_cover_crops,
    parse_cover_crops,
)

__all__ = ["parse_jmf_dir", "import_cover_crops", "parse_cover_crops"]
