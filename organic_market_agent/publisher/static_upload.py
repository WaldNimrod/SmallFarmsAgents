"""SFA static file upload — writes to canonical fixed path via custom REST endpoint.

Replaces wp_upload.py (WordPress media library) with a direct write to:
  Agents/smallfarmsagents/{subdir}/{filename}
  Public URL: {UPRESS_PUBLIC_BASE}/smallfarmsagents/{subdir}/{filename}

Requires the sfagent-file-upload mu-plugin deployed to uPress
  (wp-content/mu-plugins/sfagent-file-upload.php).

REST endpoint:
  POST /wp-json/sfagent/v1/upload
  Auth: HTTP Basic (UPRESS_WP_APP_USER / UPRESS_WP_APP_PASS)
  Body JSON: { filename, subdir, content (base64) }
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import requests

from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
BACKOFF_SECONDS = (5, 10, 20)
REQUEST_TIMEOUT = 45

# Canonical filenames — identical to wp_upload.py so upload_dispatch.py imports either
CANONICAL_MANIFEST = "sfagent-manifest.json"
CANONICAL_REPORT_JSON = "sfagent-public-report.json"
CANONICAL_REPORT_HTML = "sfagent-public-report.html"
CANONICAL_REPORT_BODY = "sfagent-public-report-body.html"
CANONICAL_MANIFEST_OF_URLS = "sfagent-manifest-of-urls.json"

MARKET_SUBDIR = "market"
CROP_BOOK_SUBDIR = "crop-book"


class MissingCredentialsError(EnvironmentError):
    """Raised when WP REST credentials are not configured."""


def _token() -> str:
    user = os.environ.get("UPRESS_WP_APP_USER", "").strip()
    pw = os.environ.get("UPRESS_WP_APP_PASS", "").replace(" ", "")
    if not (user and pw):
        raise MissingCredentialsError(
            "WP REST credentials not configured — set UPRESS_WP_APP_USER and "
            "UPRESS_WP_APP_PASS in .env"
        )
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def _endpoint() -> str:
    return config.UPRESS_WP_REST_BASE.rstrip("/") + "/sfagent/v1/upload"


def _public_url(subdir: str, filename: str) -> str:
    root = config.UPRESS_SFA_STATIC_ROOT.strip("/")
    return f"{config.UPRESS_PUBLIC_BASE.rstrip('/')}/{root}/{subdir}/{filename}"


def upload_artifact(
    local_path: Path,
    canonical_filename: str,
    subdir: str = MARKET_SUBDIR,
) -> tuple[str, str]:
    """Upload *local_path* to the canonical static path under *subdir*.

    Returns:
        (canonical_filename, public_url)

    Raises:
        MissingCredentialsError: credentials not set.
        requests.HTTPError: non-2xx after all retries.
        FileNotFoundError: local_path does not exist.
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"static_upload: file not found: {local_path}")

    content_b64 = base64.b64encode(local_path.read_bytes()).decode()
    headers = {
        "Authorization": f"Basic {_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "filename": canonical_filename,
        "subdir": subdir,
        "content": content_b64,
    }

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                _endpoint(),
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code in (401, 403):
                raise MissingCredentialsError(
                    f"static_upload: HTTP {resp.status_code} — check credentials"
                )
            resp.raise_for_status()
            url = _public_url(subdir, canonical_filename)
            logger.info(
                "static_upload: %s → %s/%s/%s (%d bytes)",
                canonical_filename, config.UPRESS_SFA_STATIC_ROOT, subdir, canonical_filename,
                len(local_path.read_bytes()),
            )
            return canonical_filename, url

        except MissingCredentialsError:
            raise
        except Exception as exc:
            last_exc = exc
            wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            logger.warning(
                "static_upload attempt %d/%d failed for %s: %s — retry in %ds",
                attempt + 1, MAX_RETRIES, canonical_filename, exc, wait,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)

    raise RuntimeError(
        f"static_upload failed after {MAX_RETRIES} attempts for {canonical_filename}: {last_exc}"
    ) from last_exc


def upload_all_artifacts(
    output_dir: Path,
    subdir: str = MARKET_SUBDIR,
) -> dict[str, str]:
    """Upload the 4 canonical SFA market artifacts plus the manifest-of-URLs.

    Args:
        output_dir: Local directory containing publish artifacts.
        subdir: Target subdirectory on server (default: 'market').

    Returns:
        Dict mapping canonical_filename → public_url.
    """
    output_dir = Path(output_dir)
    artifacts = [
        (output_dir / "manifest.json",          CANONICAL_MANIFEST,     subdir),
        (output_dir / "public_report.json",      CANONICAL_REPORT_JSON,  subdir),
        (output_dir / "public_report.html",      CANONICAL_REPORT_HTML,  subdir),
        (output_dir / "public_report_body.html", CANONICAL_REPORT_BODY,  subdir),
    ]

    results: dict[str, str] = {}
    for local_path, canonical_filename, sd in artifacts:
        _, url = upload_artifact(local_path, canonical_filename, sd)
        results[canonical_filename] = url

    # Write and upload manifest-of-URLs pointer
    manifest_of_urls = {
        "schema_version": "1.0",
        "generated_by": "sfagent-static-upload",
        "artifacts": {
            "manifest":    results[CANONICAL_MANIFEST],
            "report_json": results[CANONICAL_REPORT_JSON],
            "report_html": results[CANONICAL_REPORT_HTML],
            "report_body": results[CANONICAL_REPORT_BODY],
        },
    }
    mou_path = output_dir / "sfagent-manifest-of-urls.json"
    mou_path.write_text(json.dumps(manifest_of_urls, ensure_ascii=False, indent=2), encoding="utf-8")

    _, mou_url = upload_artifact(mou_path, CANONICAL_MANIFEST_OF_URLS, subdir)
    results[CANONICAL_MANIFEST_OF_URLS] = mou_url

    logger.info(
        "static_upload: all 5 artifacts → %s/%s/. MOU: %s",
        config.UPRESS_SFA_STATIC_ROOT, subdir, mou_url,
    )
    return results
