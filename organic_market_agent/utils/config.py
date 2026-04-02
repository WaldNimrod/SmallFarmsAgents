"""
Central config loader.
All settings come from environment variables loaded from .env at project root.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


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

    @classmethod
    def upress_configured(cls) -> bool:
        return bool(cls.UPRESS_SFTP_HOST and cls.UPRESS_SFTP_USER and cls.UPRESS_SFTP_PASS)

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.RAW_FILES_ROOT.mkdir(parents=True, exist_ok=True)
        (cls.RAW_FILES_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


config = Config()
