"""WordPress integration helper: install shortcode + create page via FTPS + WP REST API.

Usage: python scripts/wp_shortcode_install.py
Requires .env with UPRESS_* credentials.
"""
from __future__ import annotations

import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from organic_market_agent.publisher.ftps_upload import ReusedSessionFTP_TLS
from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

SHORTCODE_MARKER = "sfagent_market_report_shortcode"
SHORTCODE_PHP = """
// SmallFarmsAgent market report shortcode (M7 Go-Live)
function sfagent_market_report_shortcode($atts) {
    $upload_dir = wp_upload_dir();
    $file = $upload_dir['basedir'] . '/market/public_report_body.html';
    if (!file_exists($file)) {
        return '<p style="color:red;">Market report not available.</p>';
    }
    return file_get_contents($file);
}
add_shortcode('sfagent_market_report', 'sfagent_market_report_shortcode');
"""


def _connect_ftps() -> ReusedSessionFTP_TLS:
    ftp = ReusedSessionFTP_TLS()
    ftp.connect(config.UPRESS_SFTP_HOST, config.UPRESS_SFTP_PORT, timeout=15)
    ftp.login(config.UPRESS_SFTP_USER, config.UPRESS_SFTP_PASS)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def install_shortcode() -> bool:
    """Download functions.php from the active child theme, append shortcode if missing, re-upload."""
    import io
    import ftplib

    remote_path = "wp-content/themes/flatsome-child/functions.php"
    ftp = _connect_ftps()
    try:
        buf = io.BytesIO()
        ftp.retrbinary(f"RETR {remote_path}", buf.write)
        content = buf.getvalue().decode("utf-8")

        if SHORTCODE_MARKER in content:
            logger.info("Shortcode already present in %s — skipping", remote_path)
            print(f"[OK] Shortcode already installed in {remote_path}")
            return True

        content += "\n" + SHORTCODE_PHP.strip() + "\n"

        upload_buf = io.BytesIO(content.encode("utf-8"))
        ftp.storbinary(f"STOR {remote_path}", upload_buf)
        logger.info("Shortcode appended to %s", remote_path)
        print(f"[OK] Shortcode installed in {remote_path}")
        return True
    except ftplib.all_errors as exc:
        logger.error("Failed to install shortcode: %s", exc)
        print(f"[FAIL] FTP error: {exc}", file=sys.stderr)
        return False
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def create_wp_page() -> bool:
    """Create the SmallFarmsAgent page via WP REST API if it doesn't exist."""
    import os

    wp_user = os.getenv("UPRESS_WP_ADMIN_USER", "")
    wp_pass = os.getenv("UPRESS_WP_ADMIN_PASS", "")
    base = config.UPRESS_PUBLIC_BASE.rstrip("/")
    slug = config.UPRESS_PAGE_SLUG.strip("/")

    if not (wp_user and wp_pass):
        print("[SKIP] WordPress admin credentials not set — create page manually.", file=sys.stderr)
        print(f"  Page slug: /{slug}")
        print(f"  Content: [sfagent_market_report]")
        return False

    api = f"{base}/wp-json/wp/v2/pages"

    # Discover final API URL (handle 301 redirects like nimrod.bio → www.nimrod.bio)
    discovery = httpx.get(f"{api}?per_page=1", timeout=15, follow_redirects=True)
    final_api = str(discovery.url).split("?")[0]
    if final_api != api:
        print(f"  [info] WP REST API redirected to: {final_api}")
        api = final_api

    existing = httpx.get(f"{api}?slug={slug}", timeout=15, follow_redirects=True)
    if existing.status_code == 200 and existing.json():
        page = existing.json()[0]
        print(f"[OK] Page already exists: {base}/{slug} (id={page['id']})")
        return True

    resp = httpx.post(
        api,
        json={
            "title": "MyFarmAgents — Market Report",
            "slug": slug,
            "content": "[sfagent_market_report]",
            "status": "publish",
        },
        auth=(wp_user, wp_pass),
        timeout=15,
    )
    if resp.status_code in (200, 201):
        resp_data = resp.json()
        page_id = resp_data["id"] if isinstance(resp_data, dict) else resp_data[0].get("id") if resp_data else None
        print(f"[OK] Page created: {base}/{slug} (id={page_id})")
        return True
    else:
        print(f"[FAIL] WP REST API returned {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        return False


def main():
    print("=== WordPress Shortcode & Page Install ===")
    print()

    if not config.upress_configured():
        print("[FAIL] FTPS credentials not configured. Set UPRESS_* in .env", file=sys.stderr)
        sys.exit(1)

    ok1 = install_shortcode()
    ok2 = create_wp_page()

    if ok1 and ok2:
        print()
        print("All done. Visit:", config.UPRESS_PUBLIC_BASE.rstrip("/") + "/" + config.UPRESS_PAGE_SLUG.strip("/"))
    else:
        print()
        print("Some steps failed or were skipped — see output above.", file=sys.stderr)
        sys.exit(1 if not ok1 else 0)


if __name__ == "__main__":
    main()
