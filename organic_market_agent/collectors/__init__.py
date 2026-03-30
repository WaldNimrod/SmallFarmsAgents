from organic_market_agent.collectors.base import BaseCollector, FetchResult
from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.engine import CollectorEngine
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector

__all__ = [
    "BaseCollector",
    "CollectorEngine",
    "EasyFarmCollector",
    "FetchResult",
    "GovtBenchmarkCollector",
    "StandaloneHTMLCollector",
]
