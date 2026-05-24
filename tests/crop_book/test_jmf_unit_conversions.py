"""Tests for JMF unit conversions (AC-08, AC-09, AC-10). SFA-S003-P002-WP-B1."""
import pytest
from decimal import Decimal

pytestmark = pytest.mark.crop_book


@pytest.fixture
def yield_fn():
    from organic_market_agent.crop_book.importer.jmf_masterclass import _yield_to_per_meter
    return _yield_to_per_meter


@pytest.fixture
def inches_fn():
    from organic_market_agent.crop_book.importer.jmf_masterclass import _inches_to_cm
    return _inches_to_cm


# ---- AC-08: yield conversions ----

def test_yield_lbs_100ft_example1(yield_fn):
    """AC-08: 200 lbs/100ft → ~2.9763 kg/m (LOD400 §7.1 example 1, 4 dp)."""
    result = yield_fn(200, "lbs/100ft")
    # Exact Decimal: 200 * (0.453592 / 30.48) = 2.9763... quantized to 4dp
    expected = (Decimal("200") * Decimal("0.453592") / Decimal("30.48")).quantize(Decimal("0.0001"))
    assert result == expected, f"Got {result}, expected {expected}"


def test_yield_kg_100m_example2(yield_fn):
    """AC-08: 500 kg/100m → 5.0000 kg/m (LOD400 §7.1 example 2)."""
    result = yield_fn(500, "kg/100m")
    assert result == Decimal("5.0000"), f"Got {result}"


def test_yield_kg_100ft_example3(yield_fn):
    """AC-08: 300 kg/100ft → ~9.8425 kg/m (LOD400 §7.1 example 3, 4 dp)."""
    result = yield_fn(300, "kg/100ft")
    expected = (Decimal("300") / Decimal("30.48")).quantize(Decimal("0.0001"))
    assert result == expected, f"Got {result}, expected {expected}"


def test_yield_unknown_unit_returns_none(yield_fn):
    """AC-08 / R-03: unknown yield unit → None, not exception."""
    result = yield_fn(100, "bushels/acre")
    assert result is None


def test_yield_none_value_returns_none(yield_fn):
    """AC-10: None value → None (no NULL source_value row emitted)."""
    result = yield_fn(None, "lbs/100ft")
    assert result is None


def test_yield_empty_string_returns_none(yield_fn):
    """AC-10: empty string → None."""
    result = yield_fn("", "lbs/100ft")
    assert result is None


# ---- AC-09: inch → cm conversions ----

def test_inches_to_cm_2inch(inches_fn):
    """AC-09: 2" → 5.08 cm (LOD400 §7.2 example 1)."""
    result = inches_fn('2"')
    assert result == Decimal("5.08"), f"Got {result}"


def test_inches_to_cm_4inch(inches_fn):
    """AC-09: 4" → 10.16 cm (LOD400 §7.2 example 2)."""
    result = inches_fn('4"')
    assert result == Decimal("10.16"), f"Got {result}"


def test_inches_to_cm_12inch(inches_fn):
    """AC-09: 12" → 30.48 cm (LOD400 §7.2 example 3)."""
    result = inches_fn('12"')
    assert result == Decimal("30.48"), f"Got {result}"


def test_inches_to_cm_none(inches_fn):
    """AC-10: None → None."""
    assert inches_fn(None) is None


def test_inches_to_cm_empty(inches_fn):
    """AC-10: empty string → None."""
    assert inches_fn("") is None


def test_inches_to_cm_comma_decimal(inches_fn):
    """European comma-decimal notation: 1,5 → 3.81 cm."""
    result = inches_fn('1,5"')
    assert result == Decimal("3.81"), f"Got {result}"
