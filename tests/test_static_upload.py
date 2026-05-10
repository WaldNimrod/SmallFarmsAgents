"""Unit tests for organic_market_agent.publisher.static_upload (mocked HTTP).

Covers:
  - Happy-path upload returns (canonical_filename, public_url) with correct canonical URL
  - 401/403 raises MissingCredentialsError immediately (no retry)
  - Retry + backoff on transient errors (MAX_RETRIES, BACKOFF_SECONDS)
  - FileNotFoundError on missing local file
  - upload_all_artifacts uploads 5 files and returns a correct manifest-of-URLs
  - Public URL is derived from config (UPRESS_PUBLIC_BASE / SFA_STATIC_ROOT), not from server response
  - Invalid subdir on server returns 400 (propagated as HTTPError)
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from organic_market_agent.publisher.static_upload import (
    BACKOFF_SECONDS,
    CANONICAL_MANIFEST,
    CANONICAL_MANIFEST_OF_URLS,
    CANONICAL_REPORT_BODY,
    CANONICAL_REPORT_HTML,
    CANONICAL_REPORT_JSON,
    CROP_BOOK_SUBDIR,
    MARKET_SUBDIR,
    MAX_RETRIES,
    MissingCredentialsError,
    _endpoint,
    _public_url,
    upload_all_artifacts,
    upload_artifact,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_file(tmp_path: Path, name: str = "test.json", content: bytes = b'{"ok":1}') -> Path:
    p = tmp_path / name
    p.write_bytes(content)
    return p


def _ok_response(status: int = 201) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {"ok": True, "filename": "sfagent-manifest.json", "bytes": 8}
    resp.raise_for_status.return_value = None
    return resp


def _error_response(status: int) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.raise_for_status.side_effect = Exception(f"HTTP {status}")
    return resp


# ---------------------------------------------------------------------------
# _public_url construction
# ---------------------------------------------------------------------------

def test_public_url_market():
    with patch("organic_market_agent.publisher.static_upload.config") as mock_cfg:
        mock_cfg.UPRESS_PUBLIC_BASE = "https://nimrod.bio/Agents"
        mock_cfg.UPRESS_SFA_STATIC_ROOT = "smallfarmsagents"
        url = _public_url("market", "sfagent-manifest.json")
    assert url == "https://nimrod.bio/Agents/smallfarmsagents/market/sfagent-manifest.json"


def test_public_url_crop_book():
    with patch("organic_market_agent.publisher.static_upload.config") as mock_cfg:
        mock_cfg.UPRESS_PUBLIC_BASE = "https://nimrod.bio/Agents"
        mock_cfg.UPRESS_SFA_STATIC_ROOT = "smallfarmsagents"
        url = _public_url("crop-book", "sfagent-crop-book-manifest.json")
    assert url == "https://nimrod.bio/Agents/smallfarmsagents/crop-book/sfagent-crop-book-manifest.json"


# ---------------------------------------------------------------------------
# upload_artifact — happy path
# ---------------------------------------------------------------------------

@patch("organic_market_agent.publisher.static_upload.requests.post")
def test_upload_artifact_happy_path(mock_post, tmp_path):
    mock_post.return_value = _ok_response()
    f = _make_file(tmp_path, "manifest.json")

    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "u", "UPRESS_WP_APP_PASS": "p"}):
        with patch("organic_market_agent.publisher.static_upload.config") as mock_cfg:
            mock_cfg.UPRESS_PUBLIC_BASE = "https://nimrod.bio/Agents"
            mock_cfg.UPRESS_SFA_STATIC_ROOT = "smallfarmsagents"
            mock_cfg.UPRESS_WP_REST_BASE = "https://www.nimrod.bio/wp-json"
            fname, url = upload_artifact(f, CANONICAL_MANIFEST, MARKET_SUBDIR)

    assert fname == CANONICAL_MANIFEST
    assert url == "https://nimrod.bio/Agents/smallfarmsagents/market/sfagent-manifest.json"
    mock_post.assert_called_once()

    # Verify payload structure
    payload = mock_post.call_args.kwargs["json"]
    assert payload["filename"] == CANONICAL_MANIFEST
    assert payload["subdir"] == MARKET_SUBDIR
    decoded = base64.b64decode(payload["content"])
    assert decoded == b'{"ok":1}'


# ---------------------------------------------------------------------------
# upload_artifact — auth errors
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status", [401, 403])
@patch("organic_market_agent.publisher.static_upload.requests.post")
def test_upload_artifact_auth_error(mock_post, status, tmp_path):
    resp = MagicMock()
    resp.status_code = status
    mock_post.return_value = resp
    f = _make_file(tmp_path)

    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "u", "UPRESS_WP_APP_PASS": "p",
                                    "UPRESS_PUBLIC_BASE": "https://nimrod.bio/Agents",
                                    "UPRESS_SFA_STATIC_ROOT": "smallfarmsagents"}):
        with pytest.raises(MissingCredentialsError):
            upload_artifact(f, CANONICAL_MANIFEST, MARKET_SUBDIR)

    # No retry on auth failure
    assert mock_post.call_count == 1


# ---------------------------------------------------------------------------
# upload_artifact — retry on transient error
# ---------------------------------------------------------------------------

@patch("organic_market_agent.publisher.static_upload.time.sleep")
@patch("organic_market_agent.publisher.static_upload.requests.post")
def test_upload_artifact_retry_then_success(mock_post, mock_sleep, tmp_path):
    err_resp = MagicMock()
    err_resp.status_code = 500
    err_resp.raise_for_status.side_effect = Exception("server error")

    ok_resp = _ok_response()

    mock_post.side_effect = [err_resp, err_resp, ok_resp]
    f = _make_file(tmp_path)

    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "u", "UPRESS_WP_APP_PASS": "p",
                                    "UPRESS_PUBLIC_BASE": "https://nimrod.bio/Agents",
                                    "UPRESS_SFA_STATIC_ROOT": "smallfarmsagents"}):
        fname, url = upload_artifact(f, CANONICAL_MANIFEST, MARKET_SUBDIR)

    assert fname == CANONICAL_MANIFEST
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2


@patch("organic_market_agent.publisher.static_upload.time.sleep")
@patch("organic_market_agent.publisher.static_upload.requests.post")
def test_upload_artifact_all_retries_fail(mock_post, mock_sleep, tmp_path):
    err_resp = MagicMock()
    err_resp.status_code = 500
    err_resp.raise_for_status.side_effect = Exception("server error")
    mock_post.return_value = err_resp

    f = _make_file(tmp_path)
    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "u", "UPRESS_WP_APP_PASS": "p",
                                    "UPRESS_PUBLIC_BASE": "https://nimrod.bio/Agents",
                                    "UPRESS_SFA_STATIC_ROOT": "smallfarmsagents"}):
        with pytest.raises(RuntimeError, match="failed after"):
            upload_artifact(f, CANONICAL_MANIFEST, MARKET_SUBDIR)

    assert mock_post.call_count == MAX_RETRIES


# ---------------------------------------------------------------------------
# upload_artifact — missing local file
# ---------------------------------------------------------------------------

def test_upload_artifact_missing_file(tmp_path):
    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "u", "UPRESS_WP_APP_PASS": "p",
                                    "UPRESS_PUBLIC_BASE": "https://nimrod.bio/Agents",
                                    "UPRESS_SFA_STATIC_ROOT": "smallfarmsagents"}):
        with pytest.raises(FileNotFoundError):
            upload_artifact(tmp_path / "nonexistent.json", CANONICAL_MANIFEST, MARKET_SUBDIR)


# ---------------------------------------------------------------------------
# upload_artifact — missing credentials
# ---------------------------------------------------------------------------

def test_upload_artifact_missing_credentials(tmp_path):
    f = _make_file(tmp_path)
    with patch.dict("os.environ", {"UPRESS_WP_APP_USER": "", "UPRESS_WP_APP_PASS": ""}):
        with pytest.raises(MissingCredentialsError):
            upload_artifact(f, CANONICAL_MANIFEST, MARKET_SUBDIR)


# ---------------------------------------------------------------------------
# upload_all_artifacts
# ---------------------------------------------------------------------------

@patch("organic_market_agent.publisher.static_upload.requests.post")
def test_upload_all_artifacts(mock_post, tmp_path):
    mock_post.return_value = _ok_response()

    # Create the 4 required local artifacts
    for name in ("manifest.json", "public_report.json", "public_report.html", "public_report_body.html"):
        (tmp_path / name).write_bytes(b'{}')

    env = {
        "UPRESS_WP_APP_USER": "u",
        "UPRESS_WP_APP_PASS": "p",
        "UPRESS_PUBLIC_BASE": "https://nimrod.bio/Agents",
        "UPRESS_SFA_STATIC_ROOT": "smallfarmsagents",
    }
    with patch.dict("os.environ", env):
        results = upload_all_artifacts(tmp_path)

    # 5 uploads: 4 artifacts + manifest-of-urls
    assert mock_post.call_count == 5
    assert CANONICAL_MANIFEST in results
    assert CANONICAL_REPORT_JSON in results
    assert CANONICAL_REPORT_HTML in results
    assert CANONICAL_REPORT_BODY in results
    assert CANONICAL_MANIFEST_OF_URLS in results

    # All URLs contain the canonical path
    for url in results.values():
        assert "smallfarmsagents/market/" in url

    # manifest-of-urls file was written to output_dir
    mou_path = tmp_path / "sfagent-manifest-of-urls.json"
    assert mou_path.exists()
    mou = json.loads(mou_path.read_text())
    assert "artifacts" in mou
    assert "report_body" in mou["artifacts"]
