#!/usr/bin/env python3
"""Publish SmallFarmsAgents client hub to uPress via FTPS.

Usage:
    python scripts/ftp_publish_sfa_client_hub.py
    python scripts/ftp_publish_sfa_client_hub.py --dry-run

Reads credentials from .env.upress (at repo root).
Uploads hub/dist/ contents to UPRESS_SFA_HUB_PATH (default: sfa-hub).
"""

import ftplib
import os
import ssl
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv required: pip install python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "hub" / "dist"
ENV_FILE = REPO_ROOT / ".env.upress"

DEFAULT_HUB_PATH = "sfa-hub"


class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass that reuses the control-channel TLS session on data channels.
    Required by uPress (and many managed hosts) to prevent 425/450 errors."""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn, server_hostname=self.host,
                session=self.sock.session,
            )
        return conn, size


def connect_ftp() -> ReusedSessionFTP_TLS:
    host = os.getenv("UPRESS_SFTP_HOST", "")
    port = int(os.getenv("UPRESS_SFTP_PORT", "21"))
    user = os.getenv("UPRESS_SFTP_USER", "")
    passwd = os.getenv("UPRESS_SFTP_PASS", "")

    if not all([host, user, passwd]):
        print("[ERROR] FTPS credentials missing in .env.upress")
        sys.exit(1)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    ftp = ReusedSessionFTP_TLS(context=ctx)
    ftp.connect(host, port, timeout=30)
    ftp.login(user, passwd)
    ftp.prot_p()
    ftp.set_pasv(True)
    print(f"[OK] Connected to {host}:{port} as {user}")
    return ftp


def ftp_ensure_dir(ftp: ReusedSessionFTP_TLS, path: str) -> None:
    parts = path.strip("/").split("/")
    for part in parts:
        try:
            ftp.cwd(part)
        except ftplib.error_perm:
            ftp.mkd(part)
            ftp.cwd(part)


def ftp_upload_file(ftp: ReusedSessionFTP_TLS, local_path: Path, remote_name: str) -> None:
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_name}", f)


def publish(dry_run: bool = False) -> None:
    if not DIST_DIR.exists():
        print(f"[ERROR] dist/ not found at {DIST_DIR}")
        print("        Run first: python scripts/build_sfa_client_hub.py")
        sys.exit(1)

    hub_path = os.getenv("UPRESS_SFA_HUB_PATH", DEFAULT_HUB_PATH).strip("/")
    print(f"[INFO] Hub remote path: /{hub_path}/")

    files = sorted(f for f in DIST_DIR.rglob("*") if f.is_file())
    print(f"[INFO] Files to upload: {len(files)}")

    if dry_run:
        for f in files:
            rel = f.relative_to(DIST_DIR)
            print(f"  [DRY] /{hub_path}/{rel}")
        print("[DRY] Done — no files uploaded.")
        return

    ftp = connect_ftp()
    try:
        ftp.cwd("/")
        ftp_ensure_dir(ftp, hub_path)
        hub_root = ftp.pwd()

        for f in files:
            rel = f.relative_to(DIST_DIR)
            ftp.cwd(hub_root)

            parent = str(rel.parent)
            if parent and parent != ".":
                ftp_ensure_dir(ftp, parent)

            ftp_upload_file(ftp, f, rel.name)
            print(f"  [UP] /{hub_path}/{rel}")

        public_base = os.getenv("UPRESS_PUBLIC_BASE", "https://nimrod.bio")
        print(f"\n[OK] Published {len(files)} files to {public_base}/{hub_path}/")
    finally:
        ftp.quit()


if __name__ == "__main__":
    import argparse

    load_dotenv(ENV_FILE)

    parser = argparse.ArgumentParser(description="Publish SFA client hub via FTPS")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded")
    args = parser.parse_args()

    publish(dry_run=args.dry_run)
