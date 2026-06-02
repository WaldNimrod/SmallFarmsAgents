"""Tests for WP-CB-DATA WI-4 fetchers in sfa_ingest_push.py.

Covers:
- AC-04: representative-variety selection (default variety; no-default → first-by-name)
- AC-05: unit attached == FIELD_REGISTRY[field_name].unit (None → NULL)
- AC-06: field_state truth table (VALIDATED/UNVALIDATED/MISSING) via τ/high-trust constants
- AC-07: attribute mapping (attribute_name → attribute_key; value_list → JSON; else value_canonical)
- One-row-per-(crop_id, field_name) / (crop_id, attribute_key)

All tests mock the DB cursor; no live PG required.

Fetcher query structure:
  _fetch_crop_field_enrichment:
    1. fetchone()  — COUNT of crops with no default variety (data-hygiene log)
    2. fetchall()  — window CTE → enrichment rows for rn=1 variety
  _fetch_crop_attribute:
    1. fetchall()  — window CTE → attribute rows for rn=1 variety
"""

from __future__ import annotations

import json
import logging
from unittest.mock import MagicMock

import pytest

from organic_market_agent.crop_book.canon.field_registry import FIELD_REGISTRY
from organic_market_agent.publisher.sfa_ingest_push import (
    _AGRONOMY_FIELD_WHITELIST,
    _CATEGORICAL_ATTRS_WHITELIST,
    _FIELD_STATE_TAU,
    _HIGH_TRUST_CLASSES,
    _fetch_crop_attribute,
    _fetch_crop_field_enrichment,
)

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


def _rd(d: dict) -> MagicMock:
    """Create a MagicMock that behaves like a psycopg2 RealDictRow."""
    row = MagicMock()
    row.__getitem__ = lambda self, k: d[k]
    row.get = lambda k, default=None: d.get(k, default)
    return row


def _make_cfe_conn(
    *,
    no_default_count: int = 0,
    enrichment_rows: list[MagicMock] | None = None,
) -> MagicMock:
    """Build a mock connection for _fetch_crop_field_enrichment.

    The fetcher calls:
      1. cur.fetchone()  → {"no_default_count": <int>}
      2. cur.fetchall() → list of enrichment rows
    """
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur

    count_row = _rd({"no_default_count": no_default_count})
    cur.fetchone.return_value = count_row
    cur.fetchall.return_value = enrichment_rows if enrichment_rows is not None else []
    return conn


def _make_attr_conn(
    *,
    attr_rows: list[MagicMock] | None = None,
) -> MagicMock:
    """Build a mock connection for _fetch_crop_attribute.

    The fetcher calls:
      1. cur.fetchall() → list of attribute rows
    """
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchall.return_value = attr_rows if attr_rows is not None else []
    return conn


# ---------------------------------------------------------------------------
# AC-04a/b: representative-variety selection
# ---------------------------------------------------------------------------


class TestRepresentativeVariety:
    """AC-04: variety selection uses is_default DESC, then first-by-name ASC."""

    def test_default_variety_selected_via_sql_window(self):
        """When the window query returns rn=1 for the is_default variety,
        only that variety's enrichment rows appear in the output."""
        enrich_rows = [
            _rd({
                "crop_id": 1,
                "field_name": "days_to_maturity",
                "value_best": 75.0,
                "confidence_score": 0.85,
                "winning_source_class": "EX",
            })
        ]
        conn = _make_cfe_conn(no_default_count=0, enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)
        assert len(rows) == 1
        assert rows[0]["crop_id"] == 1
        assert rows[0]["field_name"] == "days_to_maturity"

    def test_no_default_crop_logged(self, caplog):
        """AC-04b: when no_default_count > 0, the fetcher logs a message."""
        enrich_rows = [
            _rd({
                "crop_id": 2,
                "field_name": "spacing_in_row_cm",
                "value_best": 20.0,
                "confidence_score": 0.30,
                "winning_source_class": "NI",
            })
        ]
        conn = _make_cfe_conn(no_default_count=1, enrichment_rows=enrich_rows)

        with caplog.at_level(logging.INFO, logger="sfa_ingest_push"):
            rows = _fetch_crop_field_enrichment(conn)

        assert len(rows) == 1
        assert rows[0]["crop_id"] == 2
        # Verify the log message appears when no_default_count > 0
        assert any("no default variety" in record.message for record in caplog.records), (
            "Expected log message about no-default crops"
        )

    def test_no_default_not_logged_when_zero(self, caplog):
        """When all crops have a default variety, no log is emitted."""
        conn = _make_cfe_conn(no_default_count=0, enrichment_rows=[])
        with caplog.at_level(logging.INFO, logger="sfa_ingest_push"):
            _fetch_crop_field_enrichment(conn)
        assert not any("no default variety" in record.message for record in caplog.records)

    def test_one_row_per_crop_field(self):
        """AC-04: exactly one row per (crop_id, field_name)."""
        enrich_rows = [
            _rd({"crop_id": 1, "field_name": "days_to_maturity",
                 "value_best": 60.0, "confidence_score": 0.9, "winning_source_class": "EX"}),
            _rd({"crop_id": 1, "field_name": "rows_per_bed",
                 "value_best": 4.0, "confidence_score": 0.7, "winning_source_class": "NI"}),
            _rd({"crop_id": 2, "field_name": "days_to_maturity",
                 "value_best": 45.0, "confidence_score": 0.5, "winning_source_class": ""}),
        ]
        conn = _make_cfe_conn(enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)
        keys = [(r["crop_id"], r["field_name"]) for r in rows]
        assert len(keys) == len(set(keys)), "duplicate (crop_id, field_name) pairs found"

    def test_one_row_per_crop_attribute(self):
        """AC-04: exactly one row per (crop_id, attribute_key)."""
        attr_rows = [
            _rd({"crop_id": 1, "attribute_name": "planting_method",
                 "value_canonical": "direct_seed", "value_list": None}),
            _rd({"crop_id": 1, "attribute_name": "harvest_unit",
                 "value_canonical": "kg", "value_list": None}),
            _rd({"crop_id": 2, "attribute_name": "planting_method",
                 "value_canonical": "transplant", "value_list": None}),
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        keys = [(r["crop_id"], r["attribute_key"]) for r in rows]
        assert len(keys) == len(set(keys)), "duplicate (crop_id, attribute_key) pairs found"


# ---------------------------------------------------------------------------
# AC-05: unit == FIELD_REGISTRY[field_name].unit (None → NULL)
# ---------------------------------------------------------------------------


class TestUnitAttach:
    """AC-05: every emitted enrichment row's unit == FIELD_REGISTRY[field_name].unit."""

    def test_unit_matches_field_registry_for_known_fields(self):
        """For all fields in _AGRONOMY_FIELD_WHITELIST that appear in the mock
        result, the emitted unit must equal FIELD_REGISTRY[field_name].unit."""
        fields_to_test = [f for f in _AGRONOMY_FIELD_WHITELIST if f in FIELD_REGISTRY][:5]

        enrich_rows = [
            _rd({
                "crop_id": 1,
                "field_name": fname,
                "value_best": 10.0,
                "confidence_score": 0.9,
                "winning_source_class": "EX",
            })
            for fname in fields_to_test
        ]
        conn = _make_cfe_conn(enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)

        assert len(rows) == len(fields_to_test)
        for row in rows:
            fname = row["field_name"]
            expected_unit = FIELD_REGISTRY[fname].unit if fname in FIELD_REGISTRY else None
            assert row["unit"] == expected_unit, (
                f"field '{fname}': expected unit={expected_unit!r}, got {row['unit']!r}"
            )

    def test_unit_none_for_field_with_no_unit_in_registry(self):
        """price_documented has unit=None in FIELD_REGISTRY → emitted unit is None."""
        enrich_rows = [
            _rd({
                "crop_id": 1,
                "field_name": "price_documented",
                "value_best": 5.5,
                "confidence_score": 0.9,
                "winning_source_class": "EX",
            })
        ]
        conn = _make_cfe_conn(enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)
        assert len(rows) == 1
        assert rows[0]["unit"] is None, (
            f"price_documented should have unit=None, got {rows[0]['unit']!r}"
        )

    def test_unit_for_days_to_maturity_is_days(self):
        """days_to_maturity unit == 'days' per FIELD_REGISTRY."""
        assert FIELD_REGISTRY["days_to_maturity"].unit == "days"
        enrich_rows = [
            _rd({
                "crop_id": 5,
                "field_name": "days_to_maturity",
                "value_best": 80.0,
                "confidence_score": 0.95,
                "winning_source_class": "EX",
            })
        ]
        conn = _make_cfe_conn(enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)
        assert rows[0]["unit"] == "days"


# ---------------------------------------------------------------------------
# AC-06: field_state truth table (τ=0.40, HIGH_TRUST={EX, NI})
# ---------------------------------------------------------------------------


class TestFieldStateTruthTable:
    """AC-06: field_state = VALIDATED iff source_class ∈ {EX,NI} OR score ≥ τ."""

    def _make_enrich_row(self, src_class: str | None, score: float | None) -> MagicMock:
        return _rd({
            "crop_id": 1,
            "field_name": "days_to_maturity",
            "value_best": 60.0,
            "confidence_score": score,
            "winning_source_class": src_class,
        })

    def _run(self, src_class: str | None, score: float | None) -> str:
        conn = _make_cfe_conn(enrichment_rows=[self._make_enrich_row(src_class, score)])
        rows = _fetch_crop_field_enrichment(conn)
        return rows[0]["field_state"]

    def test_validated_by_high_trust_class_ex(self):
        assert self._run("EX", 0.10) == "VALIDATED"

    def test_validated_by_high_trust_class_ni(self):
        assert self._run("NI", 0.05) == "VALIDATED"

    def test_validated_by_score_at_tau(self):
        assert self._run("C3", _FIELD_STATE_TAU) == "VALIDATED"

    def test_validated_by_score_above_tau(self):
        assert self._run("C3", 0.75) == "VALIDATED"

    def test_unvalidated_low_score_low_trust(self):
        assert self._run("C3", 0.20) == "UNVALIDATED"

    def test_unvalidated_none_score_low_trust(self):
        assert self._run("C4", None) == "UNVALIDATED"

    def test_unvalidated_empty_class_score_below_tau(self):
        assert self._run("", 0.39) == "UNVALIDATED"

    def test_validated_score_just_above_tau(self):
        assert self._run("", 0.41) == "VALIDATED"

    def test_field_state_tau_constant_value(self):
        """Confirm the constant hasn't drifted from spec (τ=0.40)."""
        assert _FIELD_STATE_TAU == 0.40

    def test_high_trust_classes_constant_value(self):
        """Confirm HIGH_TRUST_CLASSES == {EX, NI}."""
        assert _HIGH_TRUST_CLASSES == {"EX", "NI"}


# ---------------------------------------------------------------------------
# AC-07: crop_attribute mapping + value_list → JSON
# ---------------------------------------------------------------------------


class TestCropAttributeMapping:
    """AC-07: attribute_name → attribute_key; value_list → JSON; else value_canonical."""

    def test_attribute_name_mapped_to_attribute_key(self):
        """The output dict uses 'attribute_key', not 'attribute_name'."""
        attr_rows = [
            _rd({
                "crop_id": 1,
                "attribute_name": "planting_method",
                "value_canonical": "direct_seed",
                "value_list": None,
            })
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert len(rows) == 1
        assert "attribute_key" in rows[0], "attribute_key missing from output"
        assert "attribute_name" not in rows[0], "attribute_name must not appear in output"
        assert rows[0]["attribute_key"] == "planting_method"

    def test_value_list_present_delivered_as_json_string(self):
        """value_list (jsonb → Python list) is JSON-encoded in the output."""
        raw_list = ["Jan", "Feb", "Mar"]
        attr_rows = [
            _rd({
                "crop_id": 1,
                "attribute_name": "sowing_months",
                "value_canonical": None,
                "value_list": raw_list,
            })
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert len(rows) == 1
        vl = rows[0]["value_list"]
        assert vl is not None, "value_list should be non-None when DB has a list"
        # Must be a JSON-parseable string
        decoded = json.loads(vl)
        assert decoded == raw_list

    def test_value_list_none_uses_value_canonical(self):
        """When value_list is None, value_canonical is used and value_list stays None."""
        attr_rows = [
            _rd({
                "crop_id": 2,
                "attribute_name": "harvest_unit",
                "value_canonical": "kg",
                "value_list": None,
            })
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert rows[0]["value_canonical"] == "kg"
        assert rows[0]["value_list"] is None

    def test_field_state_validated_when_value_canonical_present(self):
        """field_state='VALIDATED' when value_canonical is present."""
        attr_rows = [
            _rd({"crop_id": 1, "attribute_name": "harvest_stage",
                 "value_canonical": "full_size", "value_list": None})
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert rows[0]["field_state"] == "VALIDATED"

    def test_field_state_validated_when_value_list_present(self):
        """field_state='VALIDATED' when value_list is present."""
        attr_rows = [
            _rd({"crop_id": 1, "attribute_name": "sowing_months",
                 "value_canonical": None, "value_list": ["Jan"]})
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert rows[0]["field_state"] == "VALIDATED"

    def test_field_state_missing_when_no_value(self):
        """field_state='MISSING' when both value_canonical and value_list are None/empty."""
        attr_rows = [
            _rd({"crop_id": 1, "attribute_name": "frost_tolerance_class",
                 "value_canonical": None, "value_list": None})
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert rows[0]["field_state"] == "MISSING"

    def test_value_list_takes_precedence_over_value_canonical(self):
        """When both value_list and value_canonical are set, value_list wins."""
        raw_list = ["A", "B"]
        attr_rows = [
            _rd({
                "crop_id": 3,
                "attribute_name": "common_pests",
                "value_canonical": "aphids",
                "value_list": raw_list,
            })
        ]
        conn = _make_attr_conn(attr_rows=attr_rows)
        rows = _fetch_crop_attribute(conn)
        assert rows[0]["value_list"] is not None
        decoded = json.loads(rows[0]["value_list"])
        assert decoded == raw_list
        assert rows[0]["field_state"] == "VALIDATED"

    def test_empty_result_when_no_attributes(self):
        """If no attribute rows exist for the crop, output is empty."""
        conn = _make_attr_conn(attr_rows=[])
        rows = _fetch_crop_attribute(conn)
        assert rows == []


# ---------------------------------------------------------------------------
# AC-05/AC-07 combined: whitelist fields all have entries in FIELD_REGISTRY
# ---------------------------------------------------------------------------


class TestFieldRegistryCompleteness:
    """Verify that all _AGRONOMY_FIELD_WHITELIST entries are in FIELD_REGISTRY."""

    def test_all_whitelist_fields_in_field_registry(self):
        """Every field in _AGRONOMY_FIELD_WHITELIST must have a FIELD_REGISTRY entry
        so that unit lookup is always defined (AC-05)."""
        missing = [f for f in _AGRONOMY_FIELD_WHITELIST if f not in FIELD_REGISTRY]
        assert missing == [], (
            f"Fields in _AGRONOMY_FIELD_WHITELIST missing from FIELD_REGISTRY: {missing}"
        )


# ---------------------------------------------------------------------------
# Structural: value_best=None is preserved (NULL in DB → None in output)
# ---------------------------------------------------------------------------


class TestValueBestNone:
    def test_value_best_none_preserved(self):
        """value_best=None (NULL in DB) is passed through as None (→ SQL NULL)."""
        enrich_rows = [
            _rd({
                "crop_id": 1,
                "field_name": "rows_per_bed",
                "value_best": None,
                "confidence_score": 0.0,
                "winning_source_class": None,
            })
        ]
        conn = _make_cfe_conn(enrichment_rows=enrich_rows)
        rows = _fetch_crop_field_enrichment(conn)
        assert rows[0]["value_best"] is None
