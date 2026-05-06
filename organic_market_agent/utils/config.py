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

    # uPress FTPS (M7 — Go-Live)
    UPRESS_SFTP_HOST: str = os.getenv("UPRESS_SFTP_HOST", "")
    UPRESS_SFTP_PORT: int = int(os.getenv("UPRESS_SFTP_PORT", "21"))
    UPRESS_SFTP_USER: str = os.getenv("UPRESS_SFTP_USER", "")
    UPRESS_SFTP_PASS: str = os.getenv("UPRESS_SFTP_PASS", "")
    UPRESS_PUBLIC_BASE: str = os.getenv("UPRESS_PUBLIC_BASE", "https://nimrod.bio")
    UPRESS_UPLOAD_PATH: str = os.getenv("UPRESS_UPLOAD_PATH", "wp-content/uploads/market")
    UPRESS_PAGE_SLUG: str = os.getenv("UPRESS_PAGE_SLUG", "/SmallFarmsAgent")
    # WordPress REST API (WP007 — primary upload via HTTPS port 443; replaces FTPS port 21 as default)
    # Also used by ftps_upload.py for optional ezCache purge — see docs/UPRESS_WORDPRESS_STANDARD_v2.md
    UPRESS_WP_REST_BASE: str = os.getenv("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json")
    UPRESS_WP_APP_USER: str = os.getenv("UPRESS_WP_APP_USER", "")
    UPRESS_WP_APP_PASS: str = os.getenv("UPRESS_WP_APP_PASS", "")

    @classmethod
    def upress_configured(cls) -> bool:
        return bool(cls.UPRESS_SFTP_HOST and cls.UPRESS_SFTP_USER and cls.UPRESS_SFTP_PASS)

    @classmethod
    def wp_rest_configured(cls) -> bool:
        """True when WP REST API credentials are set (primary upload path, WP007)."""
        return bool(cls.UPRESS_WP_REST_BASE and cls.UPRESS_WP_APP_USER and cls.UPRESS_WP_APP_PASS)

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.RAW_FILES_ROOT.mkdir(parents=True, exist_ok=True)
        (cls.RAW_FILES_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


config = Config()
