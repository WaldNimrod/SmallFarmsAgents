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

CHILD_THEME_PATH = "wp-content/themes/flatsome-child"

SHORTCODE_MARKER = "sfagent_market_report_shortcode"
ENQUEUE_MARKER = "sfagent_enqueue_styles"

SHORTCODE_PHP = """
// SmallFarmsAgent market report shortcode (WP007 — WP REST media library via manifest-of-URLs)
// AC-04 Option A: fetches sfagent-manifest-of-urls.json from the media library, then
// dereferences the report_body URL to serve the current HTML fragment.
// The manifest-of-urls URL is stored in wp_option 'sfagent_manifest_of_urls_url' and
// updated by the Python publisher after each upload via wp_shortcode_install.py --set-mou-url.
function sfagent_market_report_shortcode($atts) {
    $mou_url = get_option('sfagent_manifest_of_urls_url', '');
    if (empty($mou_url)) {
        return '<p style="color:red;">Market report configuration missing (sfagent_manifest_of_urls_url option not set).</p>';
    }
    $response = wp_remote_get($mou_url, array('timeout' => 10, 'sslverify' => true));
    if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) {
        return '<p style="color:red;">Market report temporarily unavailable.</p>';
    }
    $manifest = json_decode(wp_remote_retrieve_body($response), true);
    if (!isset($manifest['artifacts']['report_body'])) {
        return '<p style="color:red;">Market report manifest format error.</p>';
    }
    $body_url = $manifest['artifacts']['report_body'];
    $body_response = wp_remote_get($body_url, array('timeout' => 15, 'sslverify' => true));
    if (is_wp_error($body_response) || wp_remote_retrieve_response_code($body_response) !== 200) {
        return '<p style="color:red;">Market report content temporarily unavailable.</p>';
    }
    return wp_remote_retrieve_body($body_response);
}
add_shortcode('sfagent_market_report', 'sfagent_market_report_shortcode');
"""

ENQUEUE_PHP = """
// SmallFarmsAgent shared CSS — loaded in <head> on pages with SFA shortcode
function sfagent_enqueue_styles() {
    global $post;
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'sfagent_market_report')) {
        $css_file = get_stylesheet_directory() . '/sfagent-base.css';
        if (file_exists($css_file)) {
            wp_enqueue_style(
                'sfagent-base',
                get_stylesheet_directory_uri() . '/sfagent-base.css',
                array(),
                filemtime($css_file)
            );
        }
    }
}
add_action('wp_enqueue_scripts', 'sfagent_enqueue_styles');
"""


def _connect_ftps() -> ReusedSessionFTP_TLS:
    ftp = ReusedSessionFTP_TLS()
    ftp.connect(config.UPRESS_SFTP_HOST, config.UPRESS_SFTP_PORT, timeout=15)
    ftp.login(config.UPRESS_SFTP_USER, config.UPRESS_SFTP_PASS)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def install_shortcode() -> bool:
    """Download functions.php from the active child theme, append shortcode + enqueue hook if missing, re-upload."""
    import io
    import ftplib

    remote_path = f"{CHILD_THEME_PATH}/functions.php"
    ftp = _connect_ftps()
    try:
        buf = io.BytesIO()
        ftp.retrbinary(f"RETR {remote_path}", buf.write)
        content = buf.getvalue().decode("utf-8")

        changed = False

        if SHORTCODE_MARKER not in content:
            content += "\n" + SHORTCODE_PHP.strip() + "\n"
            changed = True
            logger.info("Shortcode appended to %s", remote_path)
        else:
            print(f"[OK] Shortcode already installed in {remote_path}")

        if ENQUEUE_MARKER not in content:
            content += "\n" + ENQUEUE_PHP.strip() + "\n"
            changed = True
            logger.info("CSS enqueue hook appended to %s", remote_path)
        else:
            print(f"[OK] CSS enqueue hook already installed in {remote_path}")

        if changed:
            upload_buf = io.BytesIO(content.encode("utf-8"))
            ftp.storbinary(f"STOR {remote_path}", upload_buf)
            print(f"[OK] functions.php updated in {remote_path}")

        return True
    except ftplib.all_errors as exc:
        logger.error("Failed to install shortcode/enqueue: %s", exc)
        print(f"[FAIL] FTP error: {exc}", file=sys.stderr)
        return False
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def deploy_shared_css() -> bool:
    """Upload sfagent-base.css to the child theme directory via FTPS."""
    import io
    import ftplib

    local_css = Path(__file__).resolve().parents[1] / "organic_market_agent" / "publisher" / "static" / "sfagent-base.css"
    if not local_css.exists():
        print(f"[FAIL] Local CSS file not found: {local_css}", file=sys.stderr)
        return False

    remote_path = f"{CHILD_THEME_PATH}/sfagent-base.css"
    ftp = _connect_ftps()
    try:
        with open(local_css, "rb") as f:
            ftp.storbinary(f"STOR {remote_path}", f)
        logger.info("Shared CSS uploaded: %s → %s", local_css.name, remote_path)
        print(f"[OK] Shared CSS deployed to {remote_path}")
        return True
    except ftplib.all_errors as exc:
        logger.error("Failed to deploy shared CSS: %s", exc)
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


def set_manifest_of_urls_option(mou_url: str) -> bool:
    """Store the manifest-of-URLs URL in WP option 'sfagent_manifest_of_urls_url' via REST API.

    The shortcode reads this option to find the pointer file (AC-04 Option A).
    Requires UPRESS_WP_APP_USER / UPRESS_WP_APP_PASS in .env.
    """
    import base64
    import os

    wp_user = os.getenv("UPRESS_WP_APP_USER", "").strip()
    wp_pass = os.getenv("UPRESS_WP_APP_PASS", "").replace(" ", "")
    if not (wp_user and wp_pass):
        print("[SKIP] WP REST credentials not set — cannot set sfagent_manifest_of_urls_url option.", file=sys.stderr)
        print(f"  Set it manually in WP admin Options or provide UPRESS_WP_APP_USER/PASS.")
        return False

    base = config.UPRESS_WP_REST_BASE.rstrip("/")
    auth = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
    }

    # WP REST /wp/v2/settings maps to registered settings only.
    # Use the custom endpoint pattern via httpx POST to /wp/v2/settings if registered,
    # or fall back to informing the user about manual setup.
    # The shortcode reads get_option('sfagent_manifest_of_urls_url') — set via REST settings.
    try:
        resp = httpx.post(
            f"{base}/wp/v2/settings",
            headers=headers,
            json={"sfagent_manifest_of_urls_url": mou_url},
            timeout=15,
            follow_redirects=True,
        )
        if resp.status_code in (200, 201):
            print(f"[OK] sfagent_manifest_of_urls_url set to: {mou_url}")
            return True
        else:
            # /wp/v2/settings requires the option to be registered with register_setting()
            # If not registered yet, provide the manual step
            print(
                f"[WARN] WP REST /settings returned {resp.status_code}. "
                f"Set sfagent_manifest_of_urls_url manually in WP admin > Options or via functions.php.",
                file=sys.stderr,
            )
            print(f"  Value to set: {mou_url}")
            return False
    except Exception as exc:
        print(f"[FAIL] Could not set WP option: {exc}", file=sys.stderr)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="WordPress Shortcode & Page Install (SFA)")
    parser.add_argument(
        "--set-mou-url",
        metavar="URL",
        default=None,
        help="Set sfagent_manifest_of_urls_url WP option to URL (AC-04 Option A pointer)",
    )
    args = parser.parse_args()

    if args.set_mou_url:
        print("=== Setting manifest-of-URLs WP option ===")
        ok = set_manifest_of_urls_option(args.set_mou_url)
        sys.exit(0 if ok else 1)

    print("=== WordPress Shortcode & Page Install ===")
    print()

    ok1 = install_shortcode()
    ok2 = deploy_shared_css()
    ok3 = create_wp_page()

    if ok1 and ok2 and ok3:
        print()
        print("All done. Visit:", config.UPRESS_PUBLIC_BASE.rstrip("/") + "/" + config.UPRESS_PAGE_SLUG.strip("/"))
    else:
        print()
        print("Some steps failed or were skipped — see output above.", file=sys.stderr)
        sys.exit(1 if not ok1 else 0)


if __name__ == "__main__":
    main()
