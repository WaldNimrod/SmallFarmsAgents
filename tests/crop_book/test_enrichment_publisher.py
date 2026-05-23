"""Tests for enrichment_publisher.py — SFA-S003-P002-WP-A LOD400 §17 Step 10.

Validates JSON output structure and F-01 compliance (no dispatch_upload).
"""

from __future__ import annotations

import ast
import json
import tempfile
from pathlib import Path

import pytest


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


def test_publish_enrichment_produces_valid_json(db_session) -> None:
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "test_enrichment.json"
        result_path = publish_enrichment(db_session, output_path=out)

        assert result_path.exists()
        with result_path.open() as f:
            data = json.load(f)

    assert "generated_at" in data
    assert "variety_count" in data
    assert "fields" in data
    assert isinstance(data["fields"], list)
    assert isinstance(data["variety_count"], int)


def test_publish_enrichment_field_schema(db_session) -> None:
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "schema_test.json"
        publish_enrichment(db_session, output_path=out)
        with out.open() as f:
            data = json.load(f)

    required_top_keys = {"generated_at", "variety_count", "fields"}
    assert required_top_keys <= set(data.keys())

    if data["fields"]:
        required_field_keys = {
            "variety_id", "crop_name_he", "crop_name_en", "variety_name_en",
            "field_name", "value_best", "value_min", "value_max",
            "confidence_score", "source_count", "winning_source_class", "computed_at",
        }
        field = data["fields"][0]
        assert required_field_keys <= set(field.keys()), (
            f"Missing keys in field entry: {required_field_keys - set(field.keys())}"
        )


def test_publish_enrichment_creates_output_dir(db_session) -> None:
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        nested = Path(tmpdir) / "a" / "b" / "c" / "out.json"
        result_path = publish_enrichment(db_session, output_path=nested)
        assert result_path.exists()


def test_publish_enrichment_hebrew_crop_names_preserved(db_session) -> None:
    """ensure_ascii=False must preserve Hebrew characters in output."""
    from organic_market_agent.crop_book.publisher.enrichment_publisher import publish_enrichment

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "he_test.json"
        publish_enrichment(db_session, output_path=out)
        raw = out.read_text(encoding="utf-8")

    # If ensure_ascii=True was accidentally used, Hebrew would be escaped as \uXXXX
    # The JSON should contain actual Hebrew characters, not unicode escapes for those chars
    if any(f["crop_name_he"] for f in json.loads(raw)["fields"]):
        assert "\\u05" not in raw, (
            "Hebrew characters are unicode-escaped — ensure_ascii should be False"
        )
