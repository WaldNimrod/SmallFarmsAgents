"""AC-07 test: seed.py --all --dry-run smoke against master XLSX.

Asserts that after patch01, the JMF MasterClass CROP CHART (master workbook,
50 rows) has ≤ 8 entries that are NOT in JMF_CROP_MAP, confirming the alias
additions took effect. The spec projects ~6-8 genuinely-unmapped crops remain
(Baby Mustard, Rapini, and a few others).

Note: seed.py --all --dry-run also processes standalone XLSX files (Direct
Seeding / Nursery charts) which may use slightly different crop name variants
and contribute additional map misses. This test isolates the master CROP CHART
miss count — the target of the patch — using parse_crop_chart directly.

SFA-S003-P002-WP-B1-patch01.
"""
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

_LIVE_MASTERCLASS_DIR = Path(
    "/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning"
)

_LIVE_MASTERCLASS_XLSX = _LIVE_MASTERCLASS_DIR / (
    "CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX"
)

# Maximum number of master CROP CHART crops with no JMF_CROP_MAP entry after patch01
# (Baby Mustard, Rapini + a few others that remain genuinely unmapped)
_MAX_CROP_CHART_MISSES = 8


def test_ac07_seed_dry_run_warn_only_for_unmapped():
    """AC-07 (patch01): master CROP CHART has ≤ 8 crops not in JMF_CROP_MAP after patch01."""
    if not _LIVE_MASTERCLASS_XLSX.exists():
        pytest.skip(f"Live masterclass XLSX not present at {_LIVE_MASTERCLASS_XLSX}")

    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP

    rows = parse_crop_chart(_LIVE_MASTERCLASS_XLSX)
    crop_names = [r["crop_jmf_en"] for r in rows]

    mapped = [c for c in crop_names if c in JMF_CROP_MAP]
    unmapped = [c for c in crop_names if c not in JMF_CROP_MAP]

    print(f"\nMaster CROP CHART: {len(crop_names)} crops")
    print(f"Mapped:   {len(mapped)}")
    print(f"Unmapped ({len(unmapped)}): {sorted(set(unmapped))}")

    assert len(unmapped) <= _MAX_CROP_CHART_MISSES, (
        f"Expected ≤ {_MAX_CROP_CHART_MISSES} unmapped crops in master CROP CHART after patch01, "
        f"got {len(unmapped)}: {sorted(set(unmapped))}"
    )


def test_ac07b_seed_dry_run_no_error_exit():
    """AC-07b (patch01): seed.py --all --dry-run exits 0 with no ERROR-level log lines."""
    import subprocess
    import sys

    if not _LIVE_MASTERCLASS_DIR.exists():
        pytest.skip(f"Live masterclass directory not present at {_LIVE_MASTERCLASS_DIR}")

    result = subprocess.run(
        [
            sys.executable, "-m", "organic_market_agent.crop_book.importer.seed",
            "--all", "--dry-run",
            "--jmf-masterclass-dir", str(_LIVE_MASTERCLASS_DIR),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    combined = result.stdout + result.stderr
    error_lines = [ln for ln in combined.splitlines() if ln.startswith("ERROR")]
    assert not error_lines, (
        f"Unexpected ERROR log lines:\n" + "\n".join(error_lines)
    )
    assert result.returncode == 0, (
        f"seed --all --dry-run exited {result.returncode}.\nstdout: {result.stdout[:300]}"
    )
