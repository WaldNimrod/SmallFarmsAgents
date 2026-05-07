"""Unit tests for organic_market_agent.publisher.upload_dispatch (AC-06 / WP008).

Covers:
- WP REST configured → calls wp_upload.upload_all_artifacts, returns success UploadResult
- WP REST configured but raises → if UPRESS_FALLBACK_FTPS=1 falls back to FTPS
- WP REST configured but raises → if no fallback flag, exception propagates
- Neither configured → raises NoUploadConfigured
- FTPS-only path (wp_rest not configured, fallback flag set, FTPS creds present)
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from organic_market_agent.publisher.upload_dispatch import (
    NoUploadConfigured,
    UploadResult,
    dispatch_upload,
)

# Patch targets: lazy imports inside dispatch_upload resolve through the source module
_WP_UPLOAD_ALL = "organic_market_agent.publisher.wp_upload.upload_all_artifacts"
_FTPS_UPLOAD_ARTS = "organic_market_agent.publisher.ftps_upload.upload_artifacts"
_CONFIG_WP_REST = "organic_market_agent.publisher.upload_dispatch.Config.wp_rest_configured"
_CONFIG_FTPS = "organic_market_agent.publisher.upload_dispatch.Config.ftps_configured"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Minimal publish output directory with a manifest.json."""
    manifest = {
        "artifact_version": "20260507_060000",
        "artifacts": {"json": "public_report_20260507_060000.json"},
        "fixed_names": {"json": "public_report.json"},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "public_report_20260507_060000.json").write_text("{}", encoding="utf-8")
    (tmp_path / "public_report.json").write_text("{}", encoding="utf-8")
    return tmp_path


def _wp_ok_results() -> dict:
    return {
        "sfagent-manifest.json": (10, "https://example.com/sfagent-manifest.json"),
        "sfagent-public-report.json": (11, "https://example.com/sfagent-public-report.json"),
    }


def _ftps_ok_result():
    from organic_market_agent.publisher.ftps_upload import FtpsUploadResult
    return FtpsUploadResult(
        success=True,
        files_uploaded=["public_report.json", "manifest.json"],
        files_failed=[],
        remote_base="wp-content/uploads/market",
    )


def _ftps_fail_result():
    from organic_market_agent.publisher.ftps_upload import FtpsUploadResult
    return FtpsUploadResult(
        success=False,
        files_uploaded=[],
        files_failed=["public_report.json", "manifest.json"],
        remote_base="",
        error="connection refused",
    )


# ---------------------------------------------------------------------------
# AC-06.1 — WP REST configured → happy path
# ---------------------------------------------------------------------------

class TestWpRestHappyPath:
    def test_returns_wp_rest_protocol(self, tmp_output):
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=False),
            patch(_WP_UPLOAD_ALL, return_value=_wp_ok_results()) as mock_wp,
        ):
            result = dispatch_upload(tmp_output)

        assert result.protocol_used == "wp_rest"
        assert result.success is True
        assert result.success_count == 2
        assert result.total_count == 2
        assert result.errors == []
        mock_wp.assert_called_once_with(tmp_output)

    def test_wp_artifacts_in_result(self, tmp_output):
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=False),
            patch(_WP_UPLOAD_ALL, return_value=_wp_ok_results()),
        ):
            result = dispatch_upload(tmp_output)

        assert "sfagent-manifest.json" in result.wp_artifacts
        assert result.wp_artifacts["sfagent-manifest.json"] == (
            10,
            "https://example.com/sfagent-manifest.json",
        )

    def test_ftps_not_called_when_wp_rest_succeeds(self, tmp_output):
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=True),
            patch(_WP_UPLOAD_ALL, return_value=_wp_ok_results()),
            patch(_FTPS_UPLOAD_ARTS) as mock_ftps,
        ):
            result = dispatch_upload(tmp_output)

        mock_ftps.assert_not_called()
        assert result.protocol_used == "wp_rest"


# ---------------------------------------------------------------------------
# AC-06.2 — WP REST raises + UPRESS_FALLBACK_FTPS=1 → FTPS fallback
# ---------------------------------------------------------------------------

class TestWpRestFailureFtpsFallback:
    def test_falls_back_to_ftps_on_wp_rest_exception(self, tmp_output, monkeypatch):
        monkeypatch.setenv("UPRESS_FALLBACK_FTPS", "1")
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=True),
            patch(_WP_UPLOAD_ALL, side_effect=RuntimeError("WP REST connection timeout")),
            patch(_FTPS_UPLOAD_ARTS, return_value=_ftps_ok_result()) as mock_ftps,
        ):
            result = dispatch_upload(tmp_output)

        assert result.protocol_used == "ftps"
        assert result.success is True
        mock_ftps.assert_called_once()

    def test_ftps_result_protocol_shown_as_ftps(self, tmp_output, monkeypatch):
        monkeypatch.setenv("UPRESS_FALLBACK_FTPS", "1")
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=True),
            patch(_WP_UPLOAD_ALL, side_effect=RuntimeError("wp rest down")),
            patch(_FTPS_UPLOAD_ARTS, return_value=_ftps_ok_result()),
        ):
            result = dispatch_upload(tmp_output)

        assert result.protocol_used == "ftps"
        assert result.success_count == 2

    def test_no_fallback_without_env_flag(self, tmp_output, monkeypatch):
        """Without UPRESS_FALLBACK_FTPS=1, WP REST failure should propagate."""
        monkeypatch.delenv("UPRESS_FALLBACK_FTPS", raising=False)
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=True),
            patch(_WP_UPLOAD_ALL, side_effect=RuntimeError("WP REST down")),
        ):
            with pytest.raises(RuntimeError, match="WP REST down"):
                dispatch_upload(tmp_output)


# ---------------------------------------------------------------------------
# AC-06.3 — Neither configured → raises NoUploadConfigured
# ---------------------------------------------------------------------------

class TestNoUploadConfigured:
    def test_raises_when_nothing_configured(self, tmp_output, monkeypatch):
        monkeypatch.delenv("UPRESS_FALLBACK_FTPS", raising=False)
        with (
            patch(_CONFIG_WP_REST, return_value=False),
            patch(_CONFIG_FTPS, return_value=False),
        ):
            with pytest.raises(NoUploadConfigured):
                dispatch_upload(tmp_output)

    def test_raises_when_fallback_flag_set_but_no_ftps_creds(self, tmp_output, monkeypatch):
        monkeypatch.setenv("UPRESS_FALLBACK_FTPS", "1")
        with (
            patch(_CONFIG_WP_REST, return_value=False),
            patch(_CONFIG_FTPS, return_value=False),
        ):
            with pytest.raises(NoUploadConfigured):
                dispatch_upload(tmp_output)

    def test_error_message_is_helpful(self, tmp_output, monkeypatch):
        monkeypatch.delenv("UPRESS_FALLBACK_FTPS", raising=False)
        with (
            patch(_CONFIG_WP_REST, return_value=False),
            patch(_CONFIG_FTPS, return_value=False),
        ):
            with pytest.raises(NoUploadConfigured, match="UPRESS_WP_APP_USER"):
                dispatch_upload(tmp_output)


# ---------------------------------------------------------------------------
# AC-06.4 — UploadResult structure is correct
# ---------------------------------------------------------------------------

class TestUploadResultStructure:
    def test_result_is_dataclass_with_expected_fields(self, tmp_output):
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=False),
            patch(_WP_UPLOAD_ALL, return_value=_wp_ok_results()),
        ):
            result = dispatch_upload(tmp_output)

        assert hasattr(result, "protocol_used")
        assert hasattr(result, "success")
        assert hasattr(result, "success_count")
        assert hasattr(result, "total_count")
        assert hasattr(result, "errors")
        assert isinstance(result.errors, list)

    def test_custom_fallback_env_var_name(self, tmp_output, monkeypatch):
        """allow_fallback_ftps_env parameter is respected."""
        monkeypatch.setenv("MY_CUSTOM_FALLBACK", "1")
        monkeypatch.delenv("UPRESS_FALLBACK_FTPS", raising=False)
        with (
            patch(_CONFIG_WP_REST, return_value=True),
            patch(_CONFIG_FTPS, return_value=True),
            patch(_WP_UPLOAD_ALL, side_effect=RuntimeError("wp down")),
            patch(_FTPS_UPLOAD_ARTS, return_value=_ftps_ok_result()),
        ):
            result = dispatch_upload(tmp_output, allow_fallback_ftps_env="MY_CUSTOM_FALLBACK")

        assert result.protocol_used == "ftps"
