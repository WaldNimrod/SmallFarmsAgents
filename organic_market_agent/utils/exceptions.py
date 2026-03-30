"""Exception hierarchy for organic_market_agent."""


class MyFarmAgentsError(Exception):
    """Base exception for all organic_market_agent errors."""


class CollectorError(MyFarmAgentsError):
    """Raised when HTTP fetch fails unrecoverably."""


class ParserError(MyFarmAgentsError):
    """Raised when a parser cannot extract items from a raw asset."""


class DuplicateAssetError(MyFarmAgentsError):
    """Raised when the same checksum already exists in raw_assets."""


class PublishAbortError(MyFarmAgentsError):
    """Raised when local publish preconditions fail (e.g. insufficient community sources)."""
