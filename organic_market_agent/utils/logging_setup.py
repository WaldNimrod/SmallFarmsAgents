"""
Structured logging setup.
All modules import get_logger from here.
"""
import logging
import sys

from organic_market_agent.utils.config import config


def get_logger(module_name: str) -> logging.Logger:
    """Returns a configured logger for the given module name."""
    logger = logging.getLogger(f"organic_market_agent.{module_name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        logger.propagate = False
    return logger
