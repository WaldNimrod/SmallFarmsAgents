"""Comprehensive tests for the reconcile_field() engine core — SFA-S003-P002-WP-A LOD400 §17 Step 10.

Covers: outlier gate (all branches), blend strategies, UC moderation gate,
multi_year_op_mean, confidence score, FieldConsensus structure.
"""

from __future__ import annotations

from decimal import Decimal


# ---------------------------------------------------------------------------
# FieldConsensus structure
# ---------------------------------------------------------------------------

def test_empty_candidates_returns_null_consensus() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_field

    c = reconcile_field("days_to_maturity", [])
    assert c.value_best is None
    assert c.source_count == 0
    assert c.winning_source_class is None
    assert c.confidence_score is None


def test_ex_override_confidence_is_one() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("days_to_maturity", [
        Candidate("team_00", Decimal("45")),
        Candidate("JMF", Decimal("60")),
    ])
    assert c.confidence_score == Decimal("1.0000")
    assert c.winning_source_class == "EX"
    assert c.source_count == 1
    assert c.value_best == c.value_min == c.value_max == Decimal("45")


# ---------------------------------------------------------------------------
# Outlier gate — standard MAD path
# ---------------------------------------------------------------------------

def test_mad_gate_flags_extreme_outlier() -> None:
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    mask = _outlier_mask([45.0, 46.0, 44.0, 200.0], z_threshold=3.5)
    assert mask == [False, False, False, True]


def test_mad_gate_no_outliers_in_tight_cluster() -> None:
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    mask = _outlier_mask([40.0, 42.0, 41.0, 43.0], z_threshold=3.5)
    assert all(m is False for m in mask)


def test_mad_gate_skipped_for_fewer_than_3_values() -> None:
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    assert _outlier_mask([1.0, 100.0], z_threshold=3.5) == [False, False]
    assert _outlier_mask([1.0], z_threshold=3.5) == [False]
    assert _outlier_mask([], z_threshold=3.5) == []


# ---------------------------------------------------------------------------
# Outlier gate — MAD=0 branches (F-190-WP-A-02)
# ---------------------------------------------------------------------------

def test_mad_zero_all_identical_no_outliers() -> None:
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    assert _outlier_mask([45.0, 45.0, 45.0], z_threshold=3.5) == [False, False, False]
    assert _outlier_mask([45.0, 45.0, 45.0, 45.0], z_threshold=3.5) == [False, False, False, False]


def test_mad_zero_iqr_fallback_flags_extreme() -> None:
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    # [45, 45, 45, 200] → MAD=0, not all identical → IQR fallback
    mask = _outlier_mask([45.0, 45.0, 45.0, 200.0], z_threshold=3.5)
    assert mask[3] is True
    assert mask[:3] == [False, False, False]


def test_mad_zero_iqr_zero_flags_non_median() -> None:
    """IQR=0 branch: mark every value that differs from the median."""
    from organic_market_agent.crop_book.importer.reconciler import _outlier_mask

    # Q1=Q3=10 → IQR=0; median=10; 100 differs from median
    mask = _outlier_mask([10.0, 10.0, 10.0, 100.0], z_threshold=3.5)
    # 100 is not equal to median (10) → flagged
    assert mask[3] is True


# ---------------------------------------------------------------------------
# Blend strategies
# ---------------------------------------------------------------------------

def test_weighted_mean_blends_pr_and_op() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("days_to_maturity", [
        Candidate("JMF", Decimal("60")),   # PR weight=0.70
        Candidate("Tend", Decimal("80")),  # OP weight=0.55
    ])
    expected = (60 * 0.70 + 80 * 0.55) / (0.70 + 0.55)
    assert abs(float(c.value_best) - expected) < 0.001
    assert c.winning_source_class == "PR"  # JMF=PR has higher rank


def test_hard_winner_picks_highest_class() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("in_row_spacing_cm", [
        Candidate("Tend", Decimal("25")),    # OP
        Candidate("JMF", Decimal("30")),     # PR — wins hard_winner
        Candidate("WB:ext", Decimal("20")),  # WB
    ])
    assert c.value_best == Decimal("30")
    assert c.winning_source_class == "PR"


def test_latest_op_picks_lexicographically_latest() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("documented_price", [
        Candidate("Tend_2020", Decimal("10.0")),
        Candidate("Tend_2022", Decimal("12.5")),
        Candidate("Tend_2021", Decimal("11.0")),
    ])
    assert c.value_best == Decimal("12.5")  # Tend_2022 is lexicographically latest
    assert c.winning_source_class == "OP"


def test_latest_op_falls_back_to_hard_winner_if_no_op() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("documented_price", [
        Candidate("JMF", Decimal("9.0")),
    ])
    assert c.value_best == Decimal("9.0")
    assert c.winning_source_class == "PR"


# ---------------------------------------------------------------------------
# UC moderation gate
# ---------------------------------------------------------------------------

def test_uc_unmoderated_excluded_from_blend() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("days_to_maturity", [
        Candidate("JMF", Decimal("60")),
        Candidate("UC:user1", Decimal("120"), moderation_weight=None),
    ])
    # UC is excluded → only JMF contributes
    assert c.source_count == 1
    assert c.winning_source_class == "PR"  # JMF = PR class
    # value_best should be close to 60 (JMF wins as sole contributor)
    assert c.value_best is not None
    assert abs(float(c.value_best) - 60.0) < 0.01


def test_uc_moderated_included_in_blend() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("days_to_maturity", [
        Candidate("JMF", Decimal("60")),
        Candidate("UC:user1", Decimal("65"), moderation_weight=0.15),
    ])
    assert c.source_count == 2
    assert c.value_best is not None


# ---------------------------------------------------------------------------
# multi_year_op_mean
# ---------------------------------------------------------------------------

def test_multi_year_op_mean_collapses_op_values() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("avg_yield_per_bed_m", [
        Candidate("Tend_2020", Decimal("4.0")),  # OP
        Candidate("Tend_2022", Decimal("6.0")),  # OP → mean = 5.0
        Candidate("JMF", Decimal("7.0")),        # PR
    ])
    # OP values collapsed to mean=5.0 (Tend_2022 representative),
    # then blended with JMF=7.0 (weighted_mean): (5.0*0.55 + 7.0*0.70) / (0.55+0.70)
    expected = (5.0 * 0.55 + 7.0 * 0.70) / (0.55 + 0.70)
    assert abs(float(c.value_best) - expected) < 0.01


# ---------------------------------------------------------------------------
# Range values (min/max)
# ---------------------------------------------------------------------------

def test_min_max_set_from_valid_candidates() -> None:
    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field

    c = reconcile_field("days_to_maturity", [
        Candidate("JMF", Decimal("60")),
        Candidate("Tend", Decimal("80")),
    ])
    assert c.value_min == Decimal("60")
    assert c.value_max == Decimal("80")


# ---------------------------------------------------------------------------
# GCR_1 back-population in reconcile_dtm
# ---------------------------------------------------------------------------

def test_reconcile_dtm_populates_gcr1_fields() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, rows = reconcile_dtm("עגבניה", tend_values=[60, 65], jmf_value=70)
    for row in rows:
        assert "trust_tier" in row, f"trust_tier missing from row: {row}"
        assert "is_outlier_rejected" in row
        assert "confidence_weight" in row


def test_reconcile_dtm_single_outlier_by_value() -> None:
    """Only the specific Tend=200 should be flagged, not Tend=55 or Tend=60."""
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm
    from decimal import Decimal

    unified, rows = reconcile_dtm("עגבניה", tend_values=[55, 60, 200], jmf_value=65)
    rejected = [r for r in rows if r["is_outlier_rejected"]]
    assert len(rejected) == 1
    assert rejected[0]["value_numeric"] == Decimal("200")
