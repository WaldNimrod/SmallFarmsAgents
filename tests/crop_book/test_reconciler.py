"""AC-07 — Reconciler unit tests. No DB required."""

from __future__ import annotations

from decimal import Decimal


def test_team00_wins_over_jmf_and_tend() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, sv_rows = reconcile_dtm("ארוגולה", tend_values=[8, 30], jmf_value=35)

    assert unified == 21, "team_00 override (21) must win over JMF (35) and Tend"
    team00_rows = [r for r in sv_rows if r["source"] == "team_00"]
    assert len(team00_rows) == 1
    assert team00_rows[0]["value_numeric"] == Decimal(21)


def test_jmf_fallback_when_no_team00_override() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, sv_rows = reconcile_dtm("ברוקולי", tend_values=[], jmf_value=70)

    assert unified == 70
    jmf_rows = [r for r in sv_rows if r["source"] == "JMF"]
    assert len(jmf_rows) == 1


def test_tend_outlier_rejected_for_leaf_crop() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, sv_rows = reconcile_dtm("ארוגולה", tend_values=[8], jmf_value=None)

    tend_rows = [r for r in sv_rows if r["source"] == "Tend"]
    assert len(tend_rows) == 1
    assert tend_rows[0]["note"] is not None
    assert "OUTLIER_REJECTED" in tend_rows[0]["note"]

    # Tend outlier rejected; team_00 = 21 wins
    assert unified == 21


def test_tend_outlier_not_rejected_for_non_leaf_crop() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, sv_rows = reconcile_dtm("עגבנייה", tend_values=[14], jmf_value=None)

    tend_rows = [r for r in sv_rows if r["source"] == "Tend"]
    assert len(tend_rows) == 1
    assert tend_rows[0].get("note") is None or "OUTLIER" not in str(tend_rows[0]["note"])
    assert unified == 14


def test_all_none_sources_returns_none() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_dtm

    unified, sv_rows = reconcile_dtm("גזר", tend_values=[], jmf_value=None)

    assert unified is None
    assert sv_rows == []


def test_reconcile_variety_picks_jmf_spacing() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_variety

    source_rows = [
        {"field_name": "in_row_spacing_cm", "source": "JMF", "value_numeric": Decimal("0.15"), "value_text": "0.15"},
        {"field_name": "in_row_spacing_cm", "source": "Tend", "value_numeric": Decimal("0.20"), "value_text": "0.20"},
    ]
    result = reconcile_variety(source_rows)

    assert result.get("in_row_spacing_cm") == Decimal("0.15"), "JMF spacing must beat Tend"


def test_reconcile_variety_documented_price_from_tend() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_variety

    source_rows = [
        {"field_name": "documented_price", "source": "Tend_2022", "value_numeric": Decimal("8.00"), "value_text": "8.00", "unit": "ILS/case"},
    ]
    result = reconcile_variety(source_rows)

    assert result.get("documented_price") == Decimal("8.00")
    assert result.get("documented_price_source") == "Tend_2022"


def test_reconcile_variety_rootstock_sets_is_grafted() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_variety

    source_rows = [
        {"field_name": "rootstock_variety", "source": "Tend", "value_text": "Beaufort", "value_numeric": None},
    ]
    result = reconcile_variety(source_rows)

    assert result.get("is_grafted") is True
    assert result.get("rootstock_variety") == "Beaufort"


def test_reconcile_variety_yield_multi_year_mean() -> None:
    from organic_market_agent.crop_book.importer.reconciler import reconcile_variety

    source_rows = [
        {"field_name": "avg_yield_per_bed_m", "source": "Tend_2021", "value_numeric": Decimal("0.15"), "value_text": "0.15"},
        {"field_name": "avg_yield_per_bed_m", "source": "Tend_2022", "value_numeric": Decimal("0.20"), "value_text": "0.20"},
    ]
    result = reconcile_variety(source_rows)

    expected_mean = (Decimal("0.15") + Decimal("0.20")) / 2
    assert result.get("avg_yield_per_bed_m") == expected_mean
    assert result.get("yield_source") == "Tend"
