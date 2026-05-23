"""Tests for enrichment_publisher.py — SFA-S003-P002-WP-A LOD400 §14 / AC-17.

Validates the locked JSON schema and F-01 compliance (no dispatch_upload).

AC-17 locked top-level keys: generated_at, schema_version, enriched_fields, varieties
AC-17 per-field keys inside varieties: best, min, max, confidence, source_count, winning_class
"""

from __future__ import annotations

import ast
import json
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# F-01 gate (AST — no DB required)
# ---------------------------------------------------------------------------

def test_dispatch_upload_not_called_in_publisher() -> None:
    """F-01 gate: publish_enrichment must never call dispatch_upload (AST check)."""
    with open("organic_market_agent/crop_book/publisher/enrichment_publisher.py") as f:
        src = f.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fname = ""
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = node.func.attr
            assert fname != "dispatch_upload", (
                "F-01 violation: dispatch_upload is called from enrichment_publisher"
            )


# ---------------------------------------------------------------------------
# AC-17 schema tests (require db_session fixture from conftest)
# ---------------------------------------------------------------------------

def test_publish_enrichment_ac17_top_level_keys(db_session) -> None:
    """AC-17: JSON must contain schema_version, enriched_fields, varieties."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "test_enrichment.json"
        result_path = publish_enrichment(db_session, output_path=out)

        assert result_path.exists(), "publish_enrichment must return path to existing file"
        with result_path.open() as f:
            data = json.load(f)

    # AC-17 locked top-level keys
    required_keys = {"generated_at", "schema_version", "enriched_fields", "varieties"}
    assert required_keys <= set(data.keys()), (
        f"Missing AC-17 top-level keys: {required_keys - set(data.keys())}"
    )
    # Stale keys from pre-AC-17 schema must NOT be present
    assert "variety_count" not in data, "Old 'variety_count' key must not be in AC-17 schema"
    assert "fields" not in data, "Old 'fields' flat-list key must not be in AC-17 schema"


def test_publish_enrichment_ac17_schema_version(db_session) -> None:
    """AC-17: schema_version must be '1.0'."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sv_test.json"
        publish_enrichment(db_session, output_path=out)
        with out.open() as f:
            data = json.load(f)

    assert data["schema_version"] == "1.0", (
        f"schema_version must be '1.0', got {data['schema_version']!r}"
    )
    assert isinstance(data["enriched_fields"], list), "enriched_fields must be a list"
    assert isinstance(data["varieties"], dict), "varieties must be a dict"


def test_publish_enrichment_ac17_per_field_keys(db_session) -> None:
    """AC-17: each per-field entry inside varieties must have locked keys."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "field_schema_test.json"
        publish_enrichment(db_session, output_path=out)
        with out.open() as f:
            data = json.load(f)

    varieties = data["varieties"]
    if not varieties:
        pytest.skip("No enrichment rows in test DB — schema test skipped")

    # Pick any variety and any field to check per-field structure
    sample_vid = next(iter(varieties))
    sample_fields = varieties[sample_vid]
    assert sample_fields, f"variety {sample_vid} has no field entries"

    sample_field_name = next(iter(sample_fields))
    field_entry = sample_fields[sample_field_name]

    required_field_keys = {"best", "min", "max", "confidence", "source_count", "winning_class"}
    assert required_field_keys <= set(field_entry.keys()), (
        f"Missing AC-17 per-field keys: {required_field_keys - set(field_entry.keys())}"
    )
    # Old per-field keys must not be present
    for stale_key in ("value_best", "value_min", "value_max", "confidence_score",
                      "winning_source_class", "computed_at"):
        assert stale_key not in field_entry, (
            f"Stale key '{stale_key}' must not appear in AC-17 field entry"
        )


def test_publish_enrichment_creates_output_dir(db_session) -> None:
    """publish_enrichment must create nested output directories."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        nested = Path(tmpdir) / "a" / "b" / "c" / "out.json"
        result_path = publish_enrichment(db_session, output_path=nested)
        assert result_path.exists()


def test_publish_enrichment_valid_json_always(db_session) -> None:
    """publish_enrichment must always produce parseable JSON."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "valid_json.json"
        publish_enrichment(db_session, output_path=out)
        raw = out.read_text(encoding="utf-8")

    # Must parse without exception
    data = json.loads(raw)
    assert isinstance(data, dict), "Top-level JSON must be an object"
