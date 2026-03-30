from organic_market_agent.db.base import Base

__all__ = ["get_session", "engine", "Base"]


def __getattr__(name: str):
    if name == "get_session":
        from organic_market_agent.db.session import get_session

        return get_session
    if name == "engine":
        from organic_market_agent.db.session import engine

        return engine
    raise AttributeError(name)
