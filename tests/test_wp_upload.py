"""Unit tests for organic_market_agent.publisher.wp_upload (mocked HTTP).

AC-05 acceptance criteria:
 - happy-path upload returns (media_id, public_url)
 - delete-before-overwrite when media_id tracking file exists
 - 401/403 raises MissingCredentialsError
 - HTTP timeout retry behavior (MAX_RETRIES + BACKOFF_SECONDS)
 - Content-Type per file extension
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from organic_market_agent.publisher.wp_upload import (
    BACKOFF_SECONDS,
    CANONICAL_MANIFEST,
    CANONICAL_MANIFEST_OF_URLS,
    CANONICAL_REPORT_BODY,
    CANONICAL_REPORT_HTML,
    CANONICAL_REPORT_JSON,
    MAX_RETRIES,
    MissingCredentialsError,
    _media_id_file,
    _rest_base,
    upload_all_artifacts,
    upload_artifact,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_FAKE_MEDIA_ID = 42
_FAKE_URL = "https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-manifest.json"

_ENV_PATCH = {
    "UPRESS_WP_APP_USER": "testuser",
    "UPRESS_WP_APP_PASS": "testpass",
    "UPRESS_WP_REST_BASE": "https://www.nimrod.bio/wp-json",
}


@pytest.fixture
def env(monkeypatch):
    """Patch required env vars for all tests."""
    for k, v in _ENV_PATCH.items():
        monkeypatch.setenv(k, v)


@pytest.fixture
def tmp_artifacts(tmp_path: Path) -> Path:
    """Create a temporary directory with fake SFA publish artifacts."""
    (tmp_path / "manifest.json").write_text('{"artifact_version": "20260507_120000"}')
    (tmp_path / "public_report.json").write_text('{"products": []}')
    (tmp_path / "public_report.html").write_text("<html><body>report</body></html>")
    (tmp_path / "public_report_body.html").write_text("<div>body fragment</div>")
    return tmp_path


def _ok_response(media_id: int = _FAKE_MEDIA_ID, url: str = _FAKE_URL) -> MagicMock:
    """Return a mock requests.Response for a successful media upload."""
    resp = MagicMock()
    resp.status_code = 201
    resp.json.return_value = {"id": media_id, "source_url": url}
    resp.raise_for_status.return_value = None
    return resp


def _error_response(status_code: int) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


# ---------------------------------------------------------------------------
# AC-05.1 — Happy path: upload returns (media_id, public_url)
# ---------------------------------------------------------------------------

class TestHappyPath:
    def test_upload_artifact_returns_media_id_and_url(self, env, tmp_artifacts, tmp_path):
        local = tmp_artifacts / "manifest.json"

        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):

            mid, url = upload_artifact(local, CANONICAL_MANIFEST, "application/json")

        assert mid == _FAKE_MEDIA_ID
        assert url == _FAKE_URL
        mock_post.assert_called_once()
        # Verify Content-Disposition header
        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs.get("headers", {}) if call_kwargs.kwargs else call_kwargs[1].get("headers", {})
        assert f'filename="{CANONICAL_MANIFEST}"' in headers["Content-Disposition"]

    def test_upload_artifact_content_type_json(self, env, tmp_artifacts, tmp_path):
        local = tmp_artifacts / "manifest.json"
        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(local, CANONICAL_MANIFEST, "application/json")

        headers = mock_post.call_args.kwargs.get("headers", {}) or mock_post.call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"

    def test_upload_artifact_content_type_html(self, env, tmp_artifacts, tmp_path):
        local = tmp_artifacts / "public_report_body.html"
        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(local, CANONICAL_REPORT_BODY, "text/html; charset=utf-8")

        headers = mock_post.call_args.kwargs.get("headers", {}) or mock_post.call_args[1]["headers"]
        assert headers["Content-Type"] == "text/html; charset=utf-8"

    def test_tracking_file_written_after_upload(self, env, tmp_artifacts, tmp_path):
        local = tmp_artifacts / "manifest.json"
        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response(media_id=99)), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(local, CANONICAL_MANIFEST, "application/json")

        id_file = tmp_path / ".wp_media_id_sfagent_manifest_json"
        assert id_file.exists()
        assert id_file.read_text().strip() == "99"


# ---------------------------------------------------------------------------
# AC-05.2 — Delete-before-overwrite when tracking file exists
# ---------------------------------------------------------------------------

class TestDeleteBeforeOverwrite:
    def test_delete_called_when_tracking_file_exists(self, env, tmp_artifacts, tmp_path):
        # Pre-seed tracking file with a previous media_id
        id_file = tmp_path / ".wp_media_id_sfagent_manifest_json"
        id_file.write_text("77")

        delete_resp = MagicMock()
        delete_resp.status_code = 200

        with patch("organic_market_agent.publisher.wp_upload.requests.delete", return_value=delete_resp) as mock_del, \
             patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        # DELETE must be called with the old media_id
        mock_del.assert_called_once()
        delete_url = mock_del.call_args.args[0] if mock_del.call_args.args else mock_del.call_args[0][0]
        assert "/wp/v2/media/77" in delete_url
        assert "force=1" in delete_url

    def test_delete_not_called_when_no_tracking_file(self, env, tmp_artifacts, tmp_path):
        with patch("organic_market_agent.publisher.wp_upload.requests.delete") as mock_del, \
             patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        mock_del.assert_not_called()

    def test_tracking_file_cleared_before_delete(self, env, tmp_artifacts, tmp_path):
        """Tracking file is removed so a failed delete won't block the next run."""
        id_file = tmp_path / ".wp_media_id_sfagent_manifest_json"
        id_file.write_text("77")

        delete_resp = MagicMock()
        delete_resp.status_code = 404  # simulate already-gone media

        with patch("organic_market_agent.publisher.wp_upload.requests.delete", return_value=delete_resp), \
             patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=_ok_response()), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        # id_file should be gone after delete (cleared by _delete_previous)
        assert not id_file.exists() or id_file.read_text().strip() != "77"


# ---------------------------------------------------------------------------
# AC-05.3 — 401 / 403 raises MissingCredentialsError (no retry)
# ---------------------------------------------------------------------------

class TestAuthErrors:
    @pytest.mark.parametrize("status_code", [401, 403])
    def test_auth_error_raises_missing_credentials(self, env, tmp_artifacts, tmp_path, status_code):
        resp = MagicMock()
        resp.status_code = status_code
        resp.raise_for_status.return_value = None

        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=resp), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            with pytest.raises(MissingCredentialsError, match="HTTP"):
                upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

    @pytest.mark.parametrize("status_code", [401, 403])
    def test_auth_error_no_retry(self, env, tmp_artifacts, tmp_path, status_code):
        """Auth errors must never be retried."""
        resp = MagicMock()
        resp.status_code = status_code

        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=resp) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path), \
             patch("organic_market_agent.publisher.wp_upload.time.sleep") as mock_sleep:
            with pytest.raises(MissingCredentialsError):
                upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        # Called exactly once — no retry
        assert mock_post.call_count == 1
        mock_sleep.assert_not_called()

    def test_missing_env_vars_raises(self, tmp_artifacts, tmp_path, monkeypatch):
        monkeypatch.delenv("UPRESS_WP_APP_USER", raising=False)
        monkeypatch.delenv("UPRESS_WP_APP_PASS", raising=False)
        with patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            with pytest.raises(MissingCredentialsError, match="WP REST credentials not configured"):
                upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")


# ---------------------------------------------------------------------------
# AC-05.4 — Retry behavior on transient errors
# ---------------------------------------------------------------------------

class TestRetryBehavior:
    def test_constants_match_spec(self):
        assert MAX_RETRIES == 3
        assert BACKOFF_SECONDS == (5, 10, 20)

    def test_retries_on_transient_error(self, env, tmp_artifacts, tmp_path):
        """Transient failures trigger MAX_RETRIES attempts."""
        fail_resp = MagicMock()
        fail_resp.status_code = 500
        fail_resp.raise_for_status.side_effect = Exception("500 server error")

        sleep_calls = []
        with patch("organic_market_agent.publisher.wp_upload.requests.post", return_value=fail_resp) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path), \
             patch("organic_market_agent.publisher.wp_upload.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            with pytest.raises(RuntimeError, match="WP REST upload failed after"):
                upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        assert mock_post.call_count == MAX_RETRIES
        assert len(sleep_calls) == MAX_RETRIES - 1
        assert sleep_calls[0] == BACKOFF_SECONDS[0]
        assert sleep_calls[1] == BACKOFF_SECONDS[1]

    def test_succeeds_on_second_attempt(self, env, tmp_artifacts, tmp_path):
        """Upload succeeds after one transient failure."""
        fail_resp = MagicMock()
        fail_resp.status_code = 503
        fail_resp.raise_for_status.side_effect = Exception("503 service unavailable")

        responses = [fail_resp, _ok_response()]

        with patch("organic_market_agent.publisher.wp_upload.requests.post", side_effect=responses) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path), \
             patch("organic_market_agent.publisher.wp_upload.time.sleep"):
            mid, url = upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        assert mid == _FAKE_MEDIA_ID
        assert mock_post.call_count == 2

    def test_network_timeout_triggers_retry(self, env, tmp_artifacts, tmp_path):
        """requests.Timeout is a transient error — should retry."""
        import requests as req_lib

        sleep_calls = []
        with patch("organic_market_agent.publisher.wp_upload.requests.post",
                   side_effect=req_lib.Timeout("timed out")) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path), \
             patch("organic_market_agent.publisher.wp_upload.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            with pytest.raises(RuntimeError):
                upload_artifact(tmp_artifacts / "manifest.json", CANONICAL_MANIFEST, "application/json")

        assert mock_post.call_count == MAX_RETRIES
        assert len(sleep_calls) == MAX_RETRIES - 1


# ---------------------------------------------------------------------------
# AC-05.5 — upload_all_artifacts: 4 canonical artifacts + manifest-of-URLs
# ---------------------------------------------------------------------------

class TestUploadAllArtifacts:
    def _make_ok_response(self, media_id: int, url_suffix: str) -> MagicMock:
        resp = MagicMock()
        resp.status_code = 201
        resp.json.return_value = {
            "id": media_id,
            "source_url": f"https://www.nimrod.bio/wp-content/uploads/2026/05/{url_suffix}",
        }
        resp.raise_for_status.return_value = None
        return resp

    def test_all_five_artifacts_uploaded(self, env, tmp_artifacts, tmp_path):
        """upload_all_artifacts uploads 4 artifacts + 1 manifest-of-URLs = 5 calls."""
        responses = [
            self._make_ok_response(1, "sfagent-manifest.json"),
            self._make_ok_response(2, "sfagent-public-report.json"),
            self._make_ok_response(3, "sfagent-public-report.html"),
            self._make_ok_response(4, "sfagent-public-report-body.html"),
            self._make_ok_response(5, "sfagent-manifest-of-urls.json"),
        ]
        with patch("organic_market_agent.publisher.wp_upload.requests.post", side_effect=responses) as mock_post, \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            results = upload_all_artifacts(tmp_artifacts)

        assert mock_post.call_count == 5
        assert CANONICAL_MANIFEST in results
        assert CANONICAL_REPORT_JSON in results
        assert CANONICAL_REPORT_HTML in results
        assert CANONICAL_REPORT_BODY in results
        assert CANONICAL_MANIFEST_OF_URLS in results

    def test_manifest_of_urls_written_locally(self, env, tmp_artifacts, tmp_path):
        """The manifest-of-URLs JSON file is written to output_dir before upload."""
        responses = [
            self._make_ok_response(i + 1, f"file-{i}.json")
            for i in range(5)
        ]
        with patch("organic_market_agent.publisher.wp_upload.requests.post", side_effect=responses), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            upload_all_artifacts(tmp_artifacts)

        pointer_path = tmp_artifacts / "sfagent-manifest-of-urls.json"
        assert pointer_path.exists()
        data = json.loads(pointer_path.read_text())
        assert "artifacts" in data
        assert "report_body" in data["artifacts"]

    def test_returns_dict_with_media_ids_and_urls(self, env, tmp_artifacts, tmp_path):
        responses = [
            self._make_ok_response(10 + i, f"artifact-{i}")
            for i in range(5)
        ]
        with patch("organic_market_agent.publisher.wp_upload.requests.post", side_effect=responses), \
             patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            results = upload_all_artifacts(tmp_artifacts)

        for key, (mid, url) in results.items():
            assert isinstance(mid, int)
            assert url.startswith("https://")


# ---------------------------------------------------------------------------
# AC-05 — FileNotFoundError for missing local file
# ---------------------------------------------------------------------------

class TestMissingLocalFile:
    def test_raises_file_not_found(self, env, tmp_path):
        missing = tmp_path / "nonexistent.json"
        with patch("organic_market_agent.publisher.wp_upload._DATA_DIR", tmp_path):
            with pytest.raises(FileNotFoundError, match="local file not found"):
                upload_artifact(missing, CANONICAL_MANIFEST, "application/json")
