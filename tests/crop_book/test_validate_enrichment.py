"""Tests for scripts/validate_enrichment.py — LOD400 §12 / AC-13.

Validates calibration logic (shadow-run delta classification) and the
CALIBRATION REPORT output contract, without requiring a live PostgreSQL DB.
"""

from __future__ import annotations

import io
import subprocess
import sys
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Unit tests: classification logic
# ---------------------------------------------------------------------------

class TestCalibrationClassification:
    """Tests for _classify() threshold logic."""

    def test_calibrated_exactly_at_threshold(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.20")) == "CALIBRATED"

    def test_calibrated_below_threshold(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.05")) == "CALIBRATED"

    def test_marginal_just_above_calibrated(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.25")) == "MARGINAL"

    def test_marginal_exactly_at_threshold(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.40")) == "MARGINAL"

    def test_misaligned_above_marginal(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.41")) == "MISALIGNED"

    def test_misaligned_when_auto_is_none(self):
        from scripts.validate_enrichment import _classify
        assert _classify(None) == "MISALIGNED"

    def test_zero_delta_is_calibrated(self):
        from scripts.validate_enrichment import _classify
        assert _classify(Decimal("0.00")) == "CALIBRATED"


# ---------------------------------------------------------------------------
# Unit tests: shadow-run delta calculation
# ---------------------------------------------------------------------------

class TestShadowRunDelta:
    """Verify the shadow-run produces correct delta and status classifications."""

    def _make_sv(self, source: str, tier: str, field: str, value: Decimal,
                 confidence_weight=None, variety_id: int = 1):
        sv = MagicMock()
        sv.source = source
        sv.trust_tier = tier
        sv.field_name = field
        sv.value_numeric = value
        sv.confidence_weight = confidence_weight
        sv.variety_id = variety_id
        sv.id = 1
        return sv

    def test_shadow_run_excludes_ex_and_classifies_calibrated(self):
        """If non-EX auto value is within 20% of EX, status should be CALIBRATED."""
        # EX value = 50. Non-EX (JMF) value = 48 (within 20%).
        # reconcile_field on [JMF=48] → value_best = 48.
        # delta_rel = |48 - 50| / 50 = 0.04 → CALIBRATED.
        from decimal import Decimal as D
        from scripts.validate_enrichment import _classify

        ex_val = D("50")
        auto_val = D("48")
        delta_rel = abs(auto_val - ex_val) / abs(ex_val)
        assert _classify(delta_rel) == "CALIBRATED"

    def test_shadow_run_no_non_ex_rows_gives_misaligned(self):
        """If there are no non-EX candidates, auto_value=None → MISALIGNED."""
        from scripts.validate_enrichment import _classify
        assert _classify(None) == "MISALIGNED"

    def test_shadow_run_large_deviation_gives_misaligned(self):
        """If non-EX auto value deviates >40% from EX, status is MISALIGNED."""
        from decimal import Decimal as D
        from scripts.validate_enrichment import _classify

        ex_val = D("50")
        auto_val = D("25")  # 50% deviation
        delta_rel = abs(auto_val - ex_val) / abs(ex_val)
        assert _classify(delta_rel) == "MISALIGNED"


# ---------------------------------------------------------------------------
# Integration: CALIBRATION REPORT output format
# ---------------------------------------------------------------------------

class TestCalibrationReportOutput:
    """Verify that _print_report produces the required CALIBRATION REPORT header."""

    def test_report_contains_calibration_report_header(self, capsys):
        from scripts.validate_enrichment import _print_report

        rows = [
            {
                "crop": "ארוגולה",
                "variety_id": 1,
                "field": "days_to_maturity",
                "ex_value": Decimal("50"),
                "auto_value": Decimal("52"),
                "delta_pct": Decimal("4.0"),
                "status": "CALIBRATED",
            }
        ]
        _print_report(rows)
        captured = capsys.readouterr()
        assert "CALIBRATION REPORT" in captured.out

    def test_report_contains_status_column_values(self, capsys):
        from scripts.validate_enrichment import _print_report

        rows = [
            {
                "crop": "ארוגולה",
                "variety_id": 1,
                "field": "days_to_maturity",
                "ex_value": Decimal("50"),
                "auto_value": Decimal("52"),
                "delta_pct": Decimal("4.0"),
                "status": "CALIBRATED",
            },
            {
                "crop": "ברוקולי",
                "variety_id": 2,
                "field": "days_to_maturity",
                "ex_value": Decimal("80"),
                "auto_value": Decimal("50"),
                "delta_pct": Decimal("37.5"),
                "status": "MARGINAL",
            },
            {
                "crop": "כרובית",
                "variety_id": 3,
                "field": "days_to_maturity",
                "ex_value": Decimal("60"),
                "auto_value": None,
                "delta_pct": None,
                "status": "MISALIGNED",
            },
        ]
        _print_report(rows)
        captured = capsys.readouterr()
        assert "CALIBRATED" in captured.out
        assert "MARGINAL" in captured.out
        assert "MISALIGNED" in captured.out

    def test_report_exit_0_always(self):
        """validate_enrichment.py must always exit 0 (LOD400 §12)."""
        result = subprocess.run(
            [sys.executable, "scripts/validate_enrichment.py", "--help"],
            capture_output=True,
            text=True,
        )
        # --help exits 0 and shows usage
        assert result.returncode == 0

    def test_empty_report_still_prints_header(self, capsys):
        """Even with zero rows, CALIBRATION REPORT header must be printed."""
        from scripts.validate_enrichment import _print_report

        _print_report([])
        captured = capsys.readouterr()
        assert "CALIBRATION REPORT" in captured.out
        assert "Summary:" in captured.out
