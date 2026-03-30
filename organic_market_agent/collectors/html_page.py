"""Generic HTML page collector."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class StandaloneHTMLCollector(BaseCollector):
    """Fetches a single HTML page."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"HTML fetch failed: {exc}") from exc

        self._last_http_status = response.status_code
        return response.content, "html"
