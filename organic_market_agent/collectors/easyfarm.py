"""Collector for sources with platform_family='easyfarm'."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class EasyFarmCollector(BaseCollector):
    """Fetches EasyFarm-platform catalog pages (HTML or JSON)."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        fetch_mode = self.profile.get("fetch_mode", "html_page")
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"EasyFarm fetch failed: {exc}") from exc

        self._last_http_status = response.status_code
        if fetch_mode == "json_endpoint":
            return response.content, "json"
        return response.content, "html"
