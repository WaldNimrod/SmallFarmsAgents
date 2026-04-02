"""FTPS upload to uPress — push local publish artifacts to the remote server.

Transport: FTPS (FTP over TLS) on port 21.
CRITICAL: uPress requires TLS session reuse on data connections — standard
ftplib.FTP_TLS fails with 425 without the ReusedSessionFTP_TLS subclass below.
"""
from __future__ import annotations

import ftplib
import io
import time
from dataclasses import dataclass, field
from pathlib import Path

from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
BACKOFF_SECONDS = (5, 10, 20)
CONNECT_TIMEOUT = 15
UPLOAD_TIMEOUT = 60


class MissingCredentialsError(EnvironmentError):
    """Raised when FTPS credentials are not configured."""


class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass that reuses the control TLS session for data connections.

    Without this, uPress returns ``425 Unable to build data connection``
    because its FTP server requires the data connection to present the same
    TLS session ticket as the control connection.
    """

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session,
            )
        return conn, size


@dataclass
class FtpsUploadResult:
    success: bool
    files_uploaded: list[str] = field(default_factory=list)
    files_failed: list[str] = field(default_factory=list)
    remote_base: str = ""
    error: str | None = None


def _connect() -> ReusedSessionFTP_TLS:
    """Open an authenticated FTPS connection to uPress."""
    host = config.UPRESS_SFTP_HOST
    port = config.UPRESS_SFTP_PORT
    user = config.UPRESS_SFTP_USER
    passwd = config.UPRESS_SFTP_PASS

    if not (host and user and passwd):
        raise MissingCredentialsError(
            "FTPS credentials not configured — set UPRESS_SFTP_HOST, "
            "UPRESS_SFTP_USER, UPRESS_SFTP_PASS in .env"
        )

    ftp = ReusedSessionFTP_TLS()
    ftp.connect(host, port, timeout=CONNECT_TIMEOUT)
    ftp.login(user, passwd)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def _ensure_remote_dir(ftp: ReusedSessionFTP_TLS, remote_path: str) -> None:
    """Create the remote directory tree if it doesn't exist (idempotent)."""
    parts = remote_path.split("/")
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass  # already exists


def _upload_single(
    ftp: ReusedSessionFTP_TLS,
    local_path: Path,
    remote_name: str,
) -> bool:
    """Upload one file with retry logic. Returns True on success."""
    for attempt in range(MAX_RETRIES):
        try:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_name}", f)
            return True
        except Exception as exc:
            wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            logger.warning(
                "FTPS upload attempt %d/%d failed for %s: %s — retry in %ds",
                attempt + 1,
                MAX_RETRIES,
                remote_name,
                exc,
                wait,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)
    return False


def upload_artifacts(
    local_dir: Path,
    file_names: list[str],
    *,
    dry_run: bool = False,
) -> FtpsUploadResult:
    """Upload listed files from *local_dir* to the remote ``UPRESS_UPLOAD_PATH``.

    Caller is responsible for ordering *file_names* so that artifacts come
    before ``manifest.json`` (see upload protocol §6.3 in the M7 work plan).

    Never raises on FTP errors — returns a ``FtpsUploadResult`` with details.
    Raises ``EnvironmentError`` if credentials are missing.
    """
    remote_base = config.UPRESS_UPLOAD_PATH
    result = FtpsUploadResult(success=False, remote_base=remote_base)

    if dry_run:
        logger.info("FTPS dry-run: would upload %d files to %s", len(file_names), remote_base)
        result.success = True
        result.files_uploaded = list(file_names)
        return result

    ftp: ReusedSessionFTP_TLS | None = None
    try:
        ftp = _connect()
        _ensure_remote_dir(ftp, remote_base)

        for fname in file_names:
            local_path = local_dir / fname
            if not local_path.exists():
                logger.error("FTPS upload: local file missing: %s", local_path)
                result.files_failed.append(fname)
                continue

            remote_name = f"{remote_base}/{fname}"
            if _upload_single(ftp, local_path, remote_name):
                result.files_uploaded.append(fname)
                logger.info("FTPS uploaded: %s → %s", fname, remote_name)
            else:
                result.files_failed.append(fname)
                logger.error("FTPS upload FAILED after %d retries: %s", MAX_RETRIES, fname)

        result.success = len(result.files_failed) == 0

        if result.success:
            _rotate_old_reports(ftp, remote_base)

    except MissingCredentialsError:
        raise
    except Exception as exc:
        result.error = str(exc)
        logger.error("FTPS upload error: %s", exc)
    finally:
        if ftp is not None:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass

    return result


KEEP_REPORTS = 3


def _rotate_old_reports(
    ftp: ReusedSessionFTP_TLS,
    remote_base: str,
    keep: int = KEEP_REPORTS,
) -> None:
    """Delete old timestamped report versions, keeping the most recent *keep* of each type."""
    from collections import defaultdict

    try:
        ftp.cwd(remote_base)
        all_files = ftp.nlst()

        by_type: dict[str, list[str]] = defaultdict(list)
        for f in all_files:
            if f in (".", ".."):
                continue
            if "-2" in f and "public_report" in f:
                base = f.split("-2")[0]
                suffix = f.rsplit(".", 1)[-1]
                by_type[f"{base}.{suffix}"].append(f)

        deleted = 0
        for _key, files in by_type.items():
            files_sorted = sorted(files)
            for old in files_sorted[:-keep]:
                try:
                    ftp.delete(f"{remote_base}/{old}")
                    deleted += 1
                except Exception:
                    pass

        if deleted:
            logger.info(
                "Report rotation: deleted %d old versions (kept %d per type)",
                deleted,
                keep,
            )
    except Exception as exc:
        logger.debug("Report rotation skipped: %s", exc)
