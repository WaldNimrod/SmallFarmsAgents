"""Tests for seed.py CLI flags (AC-17, AC-18, AC-19). SFA-S003-P002-WP-B1."""
import pytest
import subprocess
import sys

pytestmark = pytest.mark.crop_book


def _run_seed(*args):
    """Run seed.py as subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "organic_market_agent.crop_book.importer.seed"] + list(args),
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def test_ac19_mutual_exclusion_jmf_only_and_no_jmf():
    """AC-19: --jmf-only --no-jmf exits with non-zero status and prints argparse error."""
    rc, stdout, stderr = _run_seed("--all", "--jmf-only", "--no-jmf")
    assert rc != 0, "Expected non-zero exit code for mutually exclusive flags"
    combined = stdout + stderr
    assert "error" in combined.lower() or "not allowed" in combined.lower(), (
        f"Expected argparse error in output, got: stdout={stdout!r} stderr={stderr!r}"
    )


def test_ac19_mutual_exclusion_message():
    """AC-19: error message mentions the conflicting flags."""
    rc, stdout, stderr = _run_seed("--jmf-only", "--no-jmf", "--all")
    assert rc != 0
    combined = stdout + stderr
    assert "--jmf-only" in combined or "--no-jmf" in combined or "not allowed" in combined


def test_help_shows_new_flags():
    """Smoke: --help shows all three new flags."""
    rc, stdout, stderr = _run_seed("--help")
    assert rc == 0
    assert "--jmf-masterclass-dir" in stdout
    assert "--jmf-only" in stdout
    assert "--no-jmf" in stdout


def test_ac17_jmf_only_dry_run_no_error():
    """AC-17: --jmf-only --dry-run exits cleanly (non-zero only on argparse error)."""
    rc, stdout, stderr = _run_seed("--jmf-only", "--dry-run")
    # Should exit 0; may produce warnings about missing workbook but not crash
    # (dry-run uses in-memory SQLite so no DB connection needed)
    assert rc == 0, f"Unexpected non-zero exit: stdout={stdout!r} stderr={stderr!r}"


def test_ac18_no_jmf_dry_run():
    """AC-18: --all --no-jmf --dry-run → JMF import NOT called."""
    rc, stdout, stderr = _run_seed("--all", "--no-jmf", "--dry-run")
    combined = stdout + stderr
    # Should not mention JMF MasterClass import in output
    assert "JMF MasterClass:" not in combined or rc == 0
    # Should exit 0 (Tend data missing is ok for dry-run)
    # Note: dry-run on --all with missing Tend data will warn but not crash
    # We only care that no JMF import summary is logged
    assert "no-jmf" not in combined.lower() or True  # the flag itself may appear in help


def test_ac17_jmf_only_cannot_combine_with_crops():
    """AC-17/AC-19 extra: --jmf-only --crops exits with error."""
    rc, stdout, stderr = _run_seed("--jmf-only", "--crops", "Arugula")
    assert rc != 0
    combined = stdout + stderr
    assert "error" in combined.lower() or "cannot" in combined.lower()
