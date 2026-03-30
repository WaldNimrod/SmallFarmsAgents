"""Unit tests for collectors (no live HTTP — use httpx mock)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.engine import CollectorEngine, _select_collector
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector
from organic_market_agent.models import SourceFetchRun
from organic_market_agent.utils.exceptions import CollectorError, DuplicateAssetError


def _make_profile(fetch_mode="html_page", platform_family=None):
    return {
        "entry_url": "http://example.com/catalog",
        "fetch_mode": fetch_mode,
        "platform_family": platform_family,
        "timeout_seconds": 10,
        "retry_policy_json": {"max_retries": 0, "backoff_seconds": 0},
        "request_headers_json": None,
    }


def test_select_collector_easyfarm():
    profile = MagicMock(platform_family="easyfarm", fetch_mode="html_page")
    assert _select_collector(profile) is EasyFarmCollector


def test_select_collector_json_endpoint():
    profile = MagicMock(platform_family=None, fetch_mode="json_endpoint")
    assert _select_collector(profile) is GovtBenchmarkCollector


def test_select_collector_html_default():
    profile = MagicMock(platform_family=None, fetch_mode="html_page")
    assert _select_collector(profile) is StandaloneHTMLCollector


def test_select_collector_directory_page():
    profile = MagicMock(platform_family=None, fetch_mode="directory_page")
    assert _select_collector(profile) is StandaloneHTMLCollector


def test_easyfarm_fetch_html_success():
    collector = EasyFarmCollector(1, "SRC002", _make_profile("html_page", "easyfarm"))
    mock_response = MagicMock(content=b"<html>ok</html>", status_code=200)
    mock_response.raise_for_status = MagicMock()
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    collector._client = mock_http
    content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "html"
    assert content == b"<html>ok</html>"
    assert collector._last_http_status == 200


def test_easyfarm_fetch_raises_on_http_error():
    collector = EasyFarmCollector(1, "SRC002", _make_profile("html_page", "easyfarm"))
    mock_http = MagicMock()
    mock_http.get.side_effect = httpx.ConnectError("timeout")
    collector._client = mock_http
    with pytest.raises(CollectorError):
        collector.fetch_content("http://example.com")


def test_html_collector_returns_html():
    collector = StandaloneHTMLCollector(2, "SRC008", _make_profile())
    mock_response = MagicMock(content=b"<html>page</html>", status_code=200)
    mock_response.raise_for_status = MagicMock()
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    collector._client = mock_http
    content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "html"
    assert collector._last_http_status == 200


def test_govt_collector_returns_json():
    collector = GovtBenchmarkCollector(3, "SRC015", _make_profile("json_endpoint"))
    mock_response = MagicMock(content=b'[{"name":"tomato"}]', status_code=200)
    mock_response.raise_for_status = MagicMock()
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    collector._client = mock_http
    content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "json"


def test_govt_collector_returns_text_for_non_json_mode():
    profile = _make_profile("html_page")
    profile["fetch_mode"] = "html_page"
    collector = GovtBenchmarkCollector(3, "SRC015", profile)
    mock_response = MagicMock(content=b"plain", status_code=200)
    mock_response.raise_for_status = MagicMock()
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    collector._client = mock_http
    content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "text"
    assert content == b"plain"


def test_collector_engine_duplicate_marks_skipped():
    engine = CollectorEngine()
    session = MagicMock()

    def add_impl(obj):
        if isinstance(obj, SourceFetchRun):
            obj.id = 999

    session.add.side_effect = add_impl
    session.flush = MagicMock()

    source = MagicMock()
    source.id = 1
    source.code = "SRC001"
    profile = MagicMock(
        id=10,
        entry_url="http://example.com",
        fetch_mode="html_page",
        platform_family=None,
        timeout_seconds=30,
        retry_policy_json={"max_retries": 0, "backoff_seconds": 0},
        request_headers_json=None,
    )

    mock_collector_class = MagicMock()
    instance = MagicMock()
    mock_collector_class.return_value = instance

    def duplicate_fetch(session, ingestion_run_id, fetch_run):
        fetch_run.status = "skipped"
        raise DuplicateAssetError("dup")

    instance.fetch.side_effect = duplicate_fetch
    instance.close = MagicMock()

    with patch(
        "organic_market_agent.collectors.engine._select_collector",
        return_value=mock_collector_class,
    ):
        raw_asset, status = engine.run(session, 1, source, profile)

    assert raw_asset is None
    assert status == "skipped"
    instance.close.assert_called_once()
