"""
Central config loader.
All settings come from environment variables loaded from .env at project root.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")
# uPress / WP secrets often live in `.env.upress` (see docs/UPRESS_WORDPRESS_STANDARD_v2.md)
load_dotenv(_PROJECT_ROOT / ".env.upress", override=False)


class Config:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    RAW_FILES_ROOT: Path = Path(os.getenv("RAW_FILES_ROOT", "/tmp/organic_market_agent_raw"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    EMAIL_SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST", "")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    # uPress FTPS (fallback only — port 21 blocked on waldhomeserver/Bezeq)
    UPRESS_SFTP_HOST: str = os.getenv("UPRESS_SFTP_HOST", "")
    UPRESS_SFTP_PORT: int = int(os.getenv("UPRESS_SFTP_PORT", "21"))
    UPRESS_SFTP_USER: str = os.getenv("UPRESS_SFTP_USER", "")
    UPRESS_SFTP_PASS: str = os.getenv("UPRESS_SFTP_PASS", "")
    # Canonical public base — legacy www.nimrod.bio path RETIRED (2026-05-28).
    # Must be set explicitly via env; empty default ensures upress_configured()
    # returns False rather than silently targeting the dead main domain.
    UPRESS_PUBLIC_BASE: str = os.getenv("UPRESS_PUBLIC_BASE", "")
    # Canonical static root for all SFA artifacts (relative to WordPress root / ABSPATH)
    # Structure: {UPRESS_PUBLIC_BASE}/{UPRESS_SFA_STATIC_ROOT}/{subdir}/filename
    UPRESS_SFA_STATIC_ROOT: str = os.getenv("UPRESS_SFA_STATIC_ROOT", "smallfarmsagents")
    # FTPS fallback upload path (kept in sync with static root; port 21 fallback only)
    UPRESS_UPLOAD_PATH: str = os.getenv("UPRESS_UPLOAD_PATH", "smallfarmsagents/market")
    UPRESS_PAGE_SLUG: str = os.getenv("UPRESS_PAGE_SLUG", "/SmallFarmsAgent")
    # WordPress REST API — legacy www.nimrod.bio REST namespace RETIRED (2026-05-28).
    # Must be set explicitly; empty default prevents silent use of dead endpoint.
    UPRESS_WP_REST_BASE: str = os.getenv("UPRESS_WP_REST_BASE", "")
    UPRESS_WP_APP_USER: str = os.getenv("UPRESS_WP_APP_USER", "")
    UPRESS_WP_APP_PASS: str = os.getenv("UPRESS_WP_APP_PASS", "")

    # Playwright (M10.4 — mypips SPA)
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    PLAYWRIGHT_TIMEOUT_MS: int = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))

    @classmethod
    def ftps_configured(cls) -> bool:
        """True when FTPS credentials are set (legacy fallback path)."""
        return bool(cls.UPRESS_SFTP_HOST and cls.UPRESS_SFTP_USER and cls.UPRESS_SFTP_PASS)

    @classmethod
    def upress_configured(cls) -> bool:
        """True when any upload method is configured (WP REST primary OR FTPS fallback).

        WP008: updated from FTPS-only check to OR of both methods so the scheduler
        upload gate correctly fires when WP REST keys are present (F-190-01 fix).
        """
        return cls.wp_rest_configured() or cls.ftps_configured()

    @classmethod
    def wp_rest_configured(cls) -> bool:
        """True when WP REST API credentials are set (primary upload path, WP007)."""
        return bool(cls.UPRESS_WP_REST_BASE and cls.UPRESS_WP_APP_USER and cls.UPRESS_WP_APP_PASS)

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.RAW_FILES_ROOT.mkdir(parents=True, exist_ok=True)
        (cls.RAW_FILES_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


config = Config()
