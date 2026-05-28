"""FTPS upload to uPress — push local publish artifacts to the remote server.

⚠️ RETIRED 2026-05-28 (team_100 re-point, sever-www-legacy) ⚠️
Superseded by `sfa_ingest_push.py` (DB→API push to sfa.nimrod.bio).
FTPS uploads to /smallfarmsagents/ on www.nimrod.bio are no longer the
user-facing path (target host DEAD). Kept for archaeological reference;
do NOT invoke. Port 21 is also blocked on waldhomeserver (Bezeq egress).



Transport: FTPS (FTP over TLS) on port 21.
CRITICAL: uPress requires TLS session reuse on data connections — standard
ftplib.FTP_TLS fails with 425 without the ReusedSessionFTP_TLS subclass below.
"""
from __future__ import annotations

import base64
import ftplib
import io
import json
import os
import time
import urllib.error
import urllib.request
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

    if result.success:
        # After FTPS closes: purge CDN (optional) then verify public URL (optional).
        _maybe_purge_ezcache_after_upload()
        _maybe_verify_public_manifest(local_dir)

    return result


def _maybe_purge_ezcache_after_upload() -> None:
    """If UPRESS_EZCACHE_PURGE_AFTER_UPLOAD=1|true|yes and WP app password is set, POST ezCache purge."""
    flag = os.getenv("UPRESS_EZCACHE_PURGE_AFTER_UPLOAD", "").lower()
    if flag not in ("1", "true", "yes"):
        return
    rest = (config.UPRESS_WP_REST_BASE or "").strip().rstrip("/")
    user = (config.UPRESS_WP_APP_USER or "").strip()
    pw = (config.UPRESS_WP_APP_PASS or "").strip()
    if not (rest and user and pw):
        logger.info(
            "ezCache purge skipped: set UPRESS_WP_REST_BASE, UPRESS_WP_APP_USER, UPRESS_WP_APP_PASS "
            "(Application Password in WordPress)"
        )
        return
    url = f"{rest}/ezcache/v1/cache"
    auth = base64.b64encode(f"{user}:{pw}".encode()).decode()
    req = urllib.request.Request(
        url,
        data=json.dumps({"action": "purge"}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            status = resp.status
            _ = resp.read()
        logger.info("ezCache purge requested OK (HTTP %s)", status)
    except urllib.error.HTTPError as exc:
        logger.warning(
            "ezCache purge failed HTTP %s — purge manually in uPress panel if uploads/market is stale over HTTPS",
            exc.code,
        )
    except Exception as exc:
        logger.warning("ezCache purge error: %s — manual panel purge may be needed", exc)


def _maybe_verify_public_manifest(local_dir: Path) -> None:
    """If UPRESS_VERIFY_PUBLIC_MANIFEST=1|true|yes, GET public manifest.json and compare artifact_version."""
    flag = os.getenv("UPRESS_VERIFY_PUBLIC_MANIFEST", "").lower()
    if flag not in ("1", "true", "yes"):
        return
    manifest_path = local_dir / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        local_av = json.loads(manifest_path.read_text(encoding="utf-8")).get("artifact_version")
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("FTPS verify: could not read local manifest: %s", exc)
        return
    base = config.UPRESS_PUBLIC_BASE.rstrip("/")
    path = config.UPRESS_UPLOAD_PATH.strip("/")
    url = f"{base}/{path}/manifest.json"
    req = urllib.request.Request(
        url,
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": (
                "Mozilla/5.0 (compatible; OrganicMarketAgent/1.0; +https://www.nimrod.bio/) "
                "FTPS-post-verify"
            ),
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            remote = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning(
            "FTPS verify: could not fetch or parse public manifest %s — %s "
            "(CDN may still be warming; purge ezCache if this persists)",
            url,
            exc,
        )
        return
    remote_av = remote.get("artifact_version")
    if local_av and remote_av == local_av:
        logger.info("FTPS verify: public manifest artifact_version matches (%s)", local_av)
    else:
        logger.warning(
            "FTPS verify: public manifest mismatch — local artifact_version=%s remote=%s URL=%s "
            "(purge site cache in uPress / ezCache)",
            local_av,
            remote_av,
            url,
        )


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
