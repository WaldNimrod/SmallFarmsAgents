#!/usr/bin/env python3
"""Delete old sfagent-* entries from WordPress media library.

Reads media IDs from data/.wp_media_id_* tracking files (written by the old
wp_upload.py) and deletes each entry via WP REST API DELETE /wp/v2/media/{id}.
Safe to run multiple times (missing IDs are skipped gracefully).

Usage:
    python scripts/cleanup_wp_media.py
    python scripts/cleanup_wp_media.py --dry-run
"""
import argparse
import base64
import os
import sys
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] pip install requests python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.upress", override=False)

DATA_DIR = REPO_ROOT / "data"


def _token() -> str:
    user = os.environ.get("UPRESS_WP_APP_USER", "").strip()
    pw = os.environ.get("UPRESS_WP_APP_PASS", "").replace(" ", "")
    if not (user and pw):
        print("[ERROR] UPRESS_WP_APP_USER / UPRESS_WP_APP_PASS not set")
        sys.exit(1)
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def _rest_base() -> str:
    return os.environ.get("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json").rstrip("/")


def main(dry_run: bool) -> None:
    tracking_files = list(DATA_DIR.glob(".wp_media_id_*"))
    if not tracking_files:
        print("[OK] No .wp_media_id_* tracking files found — nothing to clean up.")
        return

    print(f"Found {len(tracking_files)} tracking file(s):")
    for f in tracking_files:
        media_id = f.read_text().strip()
        print(f"  {f.name}  →  media id={media_id}")

    if dry_run:
        print("[dry-run] No deletions performed.")
        return

    headers = {"Authorization": f"Basic {_token()}"}
    base = _rest_base()
    deleted = 0
    skipped = 0

    for f in tracking_files:
        media_id = f.read_text().strip()
        if not media_id:
            f.unlink(missing_ok=True)
            continue
        url = f"{base}/wp/v2/media/{media_id}?force=1"
        resp = requests.delete(url, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            print(f"  [DEL] media id={media_id}  ({f.name})")
            deleted += 1
        elif resp.status_code == 404:
            print(f"  [SKIP] media id={media_id} not found (already deleted?)")
            skipped += 1
        else:
            print(f"  [WARN] media id={media_id} → HTTP {resp.status_code}: {resp.text[:120]}")
        f.unlink(missing_ok=True)

    print(f"\n[OK] Deleted {deleted}, skipped {skipped}. Tracking files removed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up old sfagent-* WP media entries")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
