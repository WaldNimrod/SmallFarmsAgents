"""AC-04 test: live master XLSX workbook coverage ≥ 42/50. SFA-S003-P002-WP-B1-patch01.

Requires the live JMF MasterClass XLSX on Nimrod's disk.
Skipped automatically if the file is not present (CI / other machines).
"""
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book

_LIVE_MASTERCLASS_DIR = Path(
    "/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning"
)

_LIVE_MASTERCLASS_XLSX = _LIVE_MASTERCLASS_DIR / (
    "CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX"
)


def test_ac04_live_workbook_coverage_min_42_of_50():
    """AC-04 (patch01): ≥ 42 of 50 live-workbook crop_jmf_en values map to JMF_CROP_MAP."""
    if not _LIVE_MASTERCLASS_XLSX.exists():
        pytest.skip(f"Live masterclass XLSX not present at {_LIVE_MASTERCLASS_XLSX}")

    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP

    rows = parse_crop_chart(_LIVE_MASTERCLASS_XLSX)
    crop_names = [r["crop_jmf_en"] for r in rows]

    mapped = [c for c in crop_names if c in JMF_CROP_MAP]
    unmapped = [c for c in crop_names if c not in JMF_CROP_MAP]
    total = len(crop_names)

    # Report for BUILD_REPORT evidence
    print(f"\nLive workbook: {total} crops total")
    print(f"Mapped:   {len(mapped)} — {sorted(mapped)}")
    print(f"Unmapped: {len(unmapped)} — {sorted(unmapped)}")

    assert len(mapped) >= 42, (
        f"Expected ≥ 42 mapped crops, got {len(mapped)}/{total}. "
        f"Unmapped: {sorted(unmapped)}"
    )
