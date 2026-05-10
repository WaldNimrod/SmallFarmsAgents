#!/usr/bin/env python3
"""Deploy SFA mu-plugins to uPress via FTPS.

Usage:
    python scripts/deploy_mu_plugin.py

Reads credentials from .env.upress.
Uploads wp-content/mu-plugins/sfagent-*.php to the remote mu-plugins directory.
Run from local Mac (port 21 accessible); NOT from waldhomeserver (Bezeq blocks port 21).
"""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv required: pip install python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.upress"
LOCAL_MU_DIR = REPO_ROOT / "wp-content" / "mu-plugins"
REMOTE_MU_DIR = "wp-content/mu-plugins"

load_dotenv(ENV_FILE)

sys.path.insert(0, str(REPO_ROOT))
from organic_market_agent.publisher.ftps_upload import ReusedSessionFTP_TLS


def connect_ftp() -> ReusedSessionFTP_TLS:
    host = os.getenv("UPRESS_SFTP_HOST", "")
    port = int(os.getenv("UPRESS_SFTP_PORT", "21"))
    user = os.getenv("UPRESS_SFTP_USER", "")
    passwd = os.getenv("UPRESS_SFTP_PASS", "")
    if not (host and user and passwd):
        print("[ERROR] UPRESS_SFTP_HOST / UPRESS_SFTP_USER / UPRESS_SFTP_PASS not set in .env.upress")
        sys.exit(1)
    ftp = ReusedSessionFTP_TLS()
    ftp.connect(host, port)
    ftp.auth()
    ftp.prot_p()
    ftp.login(user, passwd)
    return ftp


def ftp_ensure_dir(ftp, path: str) -> None:
    parts = path.strip("/").split("/")
    for i in range(len(parts)):
        sub = "/".join(parts[: i + 1])
        try:
            ftp.mkd(sub)
        except Exception:
            pass


def main(dry_run: bool = False) -> None:
    plugins = list(LOCAL_MU_DIR.glob("sfagent-*.php"))
    if not plugins:
        print(f"[WARN] No sfagent-*.php files found in {LOCAL_MU_DIR}")
        return

    print(f"Deploying {len(plugins)} mu-plugin(s) to {REMOTE_MU_DIR}/")
    for p in plugins:
        print(f"  {p.name}")

    if dry_run:
        print("[dry-run] No files uploaded.")
        return

    ftp = connect_ftp()
    try:
        ftp_ensure_dir(ftp, REMOTE_MU_DIR)
        ftp.cwd(REMOTE_MU_DIR)
        for p in plugins:
            with open(p, "rb") as f:
                ftp.storbinary(f"STOR {p.name}", f)
            print(f"  [UP] {REMOTE_MU_DIR}/{p.name}")
        public_base = os.getenv("UPRESS_PUBLIC_BASE", "https://nimrod.bio/Agents")
        print(f"\n[OK] Deployed {len(plugins)} mu-plugin(s).")
        print(f"     REST endpoint: {public_base.split('/Agents')[0]}/wp-json/sfagent/v1/upload")
    finally:
        ftp.quit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy SFA mu-plugins to uPress via FTPS")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
