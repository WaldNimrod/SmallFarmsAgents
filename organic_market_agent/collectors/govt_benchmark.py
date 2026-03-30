"""Government / official benchmark source collector."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class GovtBenchmarkCollector(BaseCollector):
    """Fetches official wholesale price data from government endpoints."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        fetch_mode = self.profile.get("fetch_mode", "json_endpoint")
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"GovtBenchmark fetch failed: {exc}") from exc

        self._last_http_status = response.status_code
        if fetch_mode == "json_endpoint":
            return response.content, "json"
        return response.content, "text"
