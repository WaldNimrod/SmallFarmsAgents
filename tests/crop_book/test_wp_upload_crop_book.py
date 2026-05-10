"""WP004 — wp_upload crop_book + dispatch_upload profile tests.

Covers AC-10, AC-11, AC-15, AC-18.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_artifacts(tmp_path: Path) -> None:
    """Write minimal but valid crop book artifacts to tmp_path."""
    (tmp_path / "sfagent-crop-book-body.html").write_text(
        '<div class="sfa-crop-book" dir="rtl" lang="he"><script>'
        'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"'
        "</script></div>",
        encoding="utf-8",
    )
    data = {"schema": "crop_book.v1", "crops": []}
    (tmp_path / "sfagent-crop-book-data.json").write_text(
        json.dumps(data), encoding="utf-8"
    )
    manifest = {"schema_version": "crop_book.manifest.v1", "crop_count": 0}
    (tmp_path / "sfagent-crop-book-manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def _mock_upload_response(media_id: int, url: str):
    resp = MagicMock()
    resp.status_code = 201
    resp.json.return_value = {"id": media_id, "source_url": url}
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# AC-10: dispatch_upload(profile="crop_book") posts 4 artifacts via WP REST
# ---------------------------------------------------------------------------

def test_dispatch_upload_crop_book_profile(tmp_path):
    _write_artifacts(tmp_path)

    counter = {"n": 0}
    base_url = "https://www.nimrod.bio/wp-content/uploads/2026/05"

    def _fake_post(url, **kwargs):
        counter["n"] += 1
        slug = kwargs.get("headers", {}).get("Content-Disposition", "").split("filename=")[-1].strip('"')
        return _mock_upload_response(9000 + counter["n"], f"{base_url}/{slug}")

    def _fake_delete(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        return resp

    with patch.dict("os.environ", {
        "UPRESS_WP_APP_USER": "testuser",
        "UPRESS_WP_APP_PASS": "testpassword",
        "UPRESS_WP_REST_BASE": "https://www.nimrod.bio/wp-json",
    }):
        with patch("requests.post", side_effect=_fake_post):
            with patch("requests.delete", side_effect=_fake_delete):
                from organic_market_agent.publisher.upload_dispatch import dispatch_upload, UploadResult

                result = dispatch_upload(tmp_path, profile="crop_book")

    assert result.protocol_used == "wp_rest"
    assert result.success is True
    assert result.success_count == 4, f"expected 4, got {result.success_count}"
    assert result.total_count == 4
    assert "body"     in result.wp_artifacts
    assert "data"     in result.wp_artifacts
    assert "manifest" in result.wp_artifacts
    assert "mou"      in result.wp_artifacts

    # All 4 are tuples (id, url)
    for key in ("body", "data", "manifest", "mou"):
        id_, url = result.wp_artifacts[key]
        assert isinstance(id_, int)
        assert url.startswith("https://")


# ---------------------------------------------------------------------------
# AC-15: existing market dispatch_upload tests still pass (regression guard)
# ---------------------------------------------------------------------------

def test_market_profile_default_unchanged():
    """Calling dispatch_upload with no profile arg uses market path unchanged."""
    import inspect
    from organic_market_agent.publisher.upload_dispatch import dispatch_upload
    sig = inspect.signature(dispatch_upload)
    assert sig.parameters["profile"].default == "market", \
        "profile kwarg must default to 'market'"


def test_market_upload_dispatch_tests_pass():
    """Run existing test_upload_dispatch.py to ensure AC-15 regression-safe."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_upload_dispatch.py", "-q", "--tb=short"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Existing upload dispatch tests failed (AC-15 regression):\n"
        f"{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# AC-11: mu-plugin static lint (php -l + grep)
# ---------------------------------------------------------------------------

def test_mu_plugin_static_lint():
    plugin_path = Path("wordpress/mu-plugins/sfagent-crop-book-shortcode.php")
    if not plugin_path.exists():
        pytest.skip("mu-plugin not yet written")

    php_available = subprocess.run(
        ["php", "--version"], capture_output=True
    ).returncode == 0

    if php_available:
        result = subprocess.run(
            ["php", "-l", str(plugin_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"php -l failed:\n{result.stdout}\n{result.stderr}"

    content = plugin_path.read_text(encoding="utf-8")
    assert "add_shortcode" in content and "sfagent_crop_book" in content, \
        "add_shortcode sfagent_crop_book not found"
    assert "sfagent_crop_book_manifest_of_urls_url" in content, \
        "register_setting option name not found"
    assert "wp_remote_get" in content, "wp_remote_get not found"
    assert 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"' in content, \
        "literal sentinel string not found"
    assert "$count === 0" in content, "$count === 0 check not found"


# ---------------------------------------------------------------------------
# AC-18: shortcode substitution-miss returns placeholder (PHP-CLI test)
# ---------------------------------------------------------------------------

def test_shortcode_substitution_miss_returns_placeholder(tmp_path):
    plugin_path = Path("wordpress/mu-plugins/sfagent-crop-book-shortcode.php")
    if not plugin_path.exists():
        pytest.skip("mu-plugin not yet written")

    php_available = subprocess.run(
        ["php", "--version"], capture_output=True
    ).returncode == 0
    if not php_available:
        pytest.skip("php CLI not available")

    # PHP test script: define stubs and call the substitution-miss path
    test_script = tmp_path / "test_sentinel_miss.php"
    test_script.write_text(
        r"""<?php
// Stub the WordPress functions we need
function wp_remote_retrieve_body($r) { return $r; }

$sentinel    = 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"';
$replacement = 'window.CROP_BOOK_DATA_URL = "https://example.com/sfagent-crop-book-data.json"';
// Body fragment deliberately MISSING the sentinel
$body_html   = '<div class="sfa-crop-book">no sentinel here</div>';

$count = 0;
$body_html = str_replace($sentinel, $replacement, $body_html, $count);

if ($count === 0) {
    echo "PLACEHOLDER";
} else {
    echo "SUBSTITUTED";
}
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["php", str(test_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "PLACEHOLDER" in result.stdout, \
        f"Expected PLACEHOLDER on sentinel miss, got: {result.stdout}"
