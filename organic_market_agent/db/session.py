"""DB engine and session factory."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from organic_market_agent.utils.config import config

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionFactory = sessionmaker(engine, expire_on_commit=False)


@contextmanager
def get_session() -> Session:
    """Context manager for DB sessions with automatic commit/rollback."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
