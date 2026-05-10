"""WordPress REST API media upload — SFA artifact publisher.

Modeled after shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py (same uPress server).
Replaces FTPS (port 21, blocked by Bezeq egress) with HTTPS (port 443) as primary upload path.

Usage:
    from organic_market_agent.publisher.wp_upload import upload_artifact
    media_id, url = upload_artifact(
        Path("output/public/manifest.json"),
        "sfagent-manifest.json",
        "application/json",
    )

The canonical remote filename stays fixed so the URL never gets a numeric suffix (-1, -2 …).
The previous media_id is stored in ``data/.wp_media_id_<slug>`` and deleted before each upload,
ensuring the slug remains clean and the source_url is stable across runs.

Environment variables required:
    UPRESS_WP_APP_USER   — WordPress username (user_login, not email)
    UPRESS_WP_APP_PASS   — WordPress Application Password (spaces stripped before encoding)
    UPRESS_WP_REST_BASE  — WP REST root, default https://www.nimrod.bio/wp-json

Note on JSON uploads: uPress may restrict media library extensions. If application/json is
rejected, the DEPLOY_HANDOFF.md includes a mu-plugin snippet to allow .json uploads. The
Content-Disposition header forces the canonical filename regardless of uPress default behaviour.
"""
from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import requests

from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
BACKOFF_SECONDS = (5, 10, 20)
REQUEST_TIMEOUT_DELETE = 15
REQUEST_TIMEOUT_UPLOAD = 30

_DATA_DIR = Path("data")

# Canonical filenames for the 4 SFA artifacts
CANONICAL_MANIFEST = "sfagent-manifest.json"
CANONICAL_REPORT_JSON = "sfagent-public-report.json"
CANONICAL_REPORT_HTML = "sfagent-public-report.html"
CANONICAL_REPORT_BODY = "sfagent-public-report-body.html"

# Manifest-of-URLs pointer file (AC-04 Option A)
CANONICAL_MANIFEST_OF_URLS = "sfagent-manifest-of-urls.json"

# Crop book canonical filenames (WP004)
CANONICAL_CROP_BOOK_BODY     = "sfagent-crop-book-body.html"
CANONICAL_CROP_BOOK_DATA     = "sfagent-crop-book-data.json"
CANONICAL_CROP_BOOK_MANIFEST = "sfagent-crop-book-manifest.json"
CANONICAL_CROP_BOOK_MOU      = "sfagent-crop-book-manifest-of-urls.json"


class MissingCredentialsError(EnvironmentError):
    """Raised when WP REST API credentials are not configured."""


def _token() -> str:
    """Build HTTP Basic auth token from env vars. Strips spaces from app password (defensive)."""
    user = os.environ.get("UPRESS_WP_APP_USER", "").strip()
    pw = os.environ.get("UPRESS_WP_APP_PASS", "").replace(" ", "")
    if not (user and pw):
        raise MissingCredentialsError(
            "WP REST credentials not configured — set UPRESS_WP_APP_USER and "
            "UPRESS_WP_APP_PASS in .env (WordPress Application Password)"
        )
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def _rest_base() -> str:
    """Return the WP REST API base URL (no trailing slash)."""
    return os.environ.get("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json").rstrip("/")


def _media_id_file(canonical_filename: str) -> Path:
    """Derive a local media-ID tracking file from the canonical filename."""
    slug = canonical_filename.replace(".", "_").replace("-", "_")
    return _DATA_DIR / f".wp_media_id_{slug}"


def _delete_previous(canonical_filename: str, headers_auth: dict) -> None:
    """Delete the previously uploaded media entry (if any) so the URL slug stays clean."""
    id_file = _media_id_file(canonical_filename)
    if not id_file.exists():
        return
    old_id = id_file.read_text().strip()
    if not old_id:
        return
    base = _rest_base()
    try:
        resp = requests.delete(
            f"{base}/wp/v2/media/{old_id}?force=1",
            headers=headers_auth,
            timeout=REQUEST_TIMEOUT_DELETE,
        )
        if resp.status_code in (200, 201):
            logger.info("WP REST: deleted previous media id=%s for %s", old_id, canonical_filename)
        else:
            logger.warning(
                "WP REST: delete of media id=%s returned HTTP %s (continuing upload)",
                old_id,
                resp.status_code,
            )
    except Exception as exc:
        logger.warning(
            "WP REST: delete of media id=%s failed: %s (continuing upload)", old_id, exc
        )
    # Always remove the tracking file so a failed delete doesn't block the next upload
    id_file.unlink(missing_ok=True)


def upload_artifact(
    local_path: Path,
    canonical_filename: str,
    content_type: str,
) -> tuple[int, str]:
    """Upload *local_path* to WP media library under *canonical_filename*.

    Deletes the previous version first (delete-before-overwrite) so the URL stays stable.
    Retries up to MAX_RETRIES times with exponential backoff on transient errors.

    Args:
        local_path: Local file to upload.
        canonical_filename: Remote filename in WP media library (e.g. ``sfagent-manifest.json``).
        content_type: MIME type (e.g. ``application/json`` or ``text/html; charset=utf-8``).

    Returns:
        (media_id, public_url) on success.

    Raises:
        MissingCredentialsError: UPRESS_WP_APP_USER / UPRESS_WP_APP_PASS not set.
        requests.HTTPError: Non-2xx response after all retries exhausted.
        FileNotFoundError: local_path does not exist.
    """
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"WP REST upload: local file not found: {local_path}")

    headers_auth = {"Authorization": f"Basic {_token()}"}
    base = _rest_base()

    # Ensure data/ dir exists for tracking files
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Delete previous version so the URL slug stays clean (no -1/-2 suffix)
    _delete_previous(canonical_filename, headers_auth)

    # Upload with retry/backoff
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                f"{base}/wp/v2/media",
                headers={
                    **headers_auth,
                    "Content-Disposition": f'attachment; filename="{canonical_filename}"',
                    "Content-Type": content_type,
                },
                data=local_path.read_bytes(),
                timeout=REQUEST_TIMEOUT_UPLOAD,
            )
            if resp.status_code in (401, 403):
                raise MissingCredentialsError(
                    f"WP REST upload: HTTP {resp.status_code} — check UPRESS_WP_APP_USER / "
                    f"UPRESS_WP_APP_PASS (Application Password)"
                )
            resp.raise_for_status()

            j = resp.json()
            media_id: int = j["id"]
            url: str = j["source_url"]

            # Persist media_id for delete-before-overwrite on the next run
            id_file = _media_id_file(canonical_filename)
            id_file.write_text(str(media_id))

            logger.info(
                "WP REST: uploaded %s → media_id=%s url=%s",
                canonical_filename,
                media_id,
                url,
            )
            return media_id, url

        except MissingCredentialsError:
            raise  # Never retry auth failures
        except Exception as exc:
            last_exc = exc
            wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
            logger.warning(
                "WP REST upload attempt %d/%d failed for %s: %s — retry in %ds",
                attempt + 1,
                MAX_RETRIES,
                canonical_filename,
                exc,
                wait,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)

    raise RuntimeError(
        f"WP REST upload failed after {MAX_RETRIES} attempts for {canonical_filename}: {last_exc}"
    ) from last_exc


def upload_all_artifacts(
    output_dir: Path,
) -> dict[str, tuple[int, str]]:
    """Upload the 4 canonical SFA artifacts plus the manifest-of-URLs pointer file.

    Args:
        output_dir: Local directory containing publish artifacts (e.g. ``output/public``).

    Returns:
        Dict mapping canonical_filename → (media_id, public_url).

    Raises:
        MissingCredentialsError: credentials not configured.
        FileNotFoundError: a required artifact is missing from output_dir.
        RuntimeError: upload failed after all retries.
    """
    output_dir = Path(output_dir)

    artifacts = [
        (output_dir / "manifest.json",            CANONICAL_MANIFEST,     "application/json"),
        (output_dir / "public_report.json",        CANONICAL_REPORT_JSON,  "application/json"),
        (output_dir / "public_report.html",        CANONICAL_REPORT_HTML,  "text/html; charset=utf-8"),
        (output_dir / "public_report_body.html",   CANONICAL_REPORT_BODY,  "text/html; charset=utf-8"),
    ]

    results: dict[str, tuple[int, str]] = {}
    for local_path, canonical_filename, content_type in artifacts:
        media_id, url = upload_artifact(local_path, canonical_filename, content_type)
        results[canonical_filename] = (media_id, url)

    # AC-04 Option A: write and upload the manifest-of-URLs pointer file
    import json as _json
    manifest_of_urls = {
        "schema_version": "1.0",
        "generated_by": "sfagent-wp-upload",
        "artifacts": {
            "manifest":     results[CANONICAL_MANIFEST][1],
            "report_json":  results[CANONICAL_REPORT_JSON][1],
            "report_html":  results[CANONICAL_REPORT_HTML][1],
            "report_body":  results[CANONICAL_REPORT_BODY][1],
        },
    }
    pointer_path = output_dir / "sfagent-manifest-of-urls.json"
    pointer_path.write_text(_json.dumps(manifest_of_urls, ensure_ascii=False, indent=2), encoding="utf-8")

    mou_id, mou_url = upload_artifact(pointer_path, CANONICAL_MANIFEST_OF_URLS, "application/json")
    results[CANONICAL_MANIFEST_OF_URLS] = (mou_id, mou_url)

    logger.info(
        "WP REST: all 5 SFA artifacts uploaded. Manifest-of-URLs: %s", mou_url
    )
    return results


def upload_all_crop_book_artifacts(
    output_dir: Path,
) -> dict[str, tuple[int, str]]:
    """Upload 3 crop book artifacts + manifest-of-URLs pointer (WP004).

    Mirrors upload_all_artifacts for the crop book profile.
    FTPS fallback intentionally absent — Bezeq blocks port 21 outbound.

    Args:
        output_dir: Directory containing sfagent-crop-book-*.{html,json} files.

    Returns:
        Dict: "body" | "data" | "manifest" | "mou" → (media_id, public_url).
    """
    import json as _json
    from datetime import datetime, timezone

    output_dir = Path(output_dir)

    artifacts = [
        (output_dir / "sfagent-crop-book-body.html",     CANONICAL_CROP_BOOK_BODY,     "text/html; charset=utf-8"),
        (output_dir / "sfagent-crop-book-data.json",     CANONICAL_CROP_BOOK_DATA,     "application/json"),
        (output_dir / "sfagent-crop-book-manifest.json", CANONICAL_CROP_BOOK_MANIFEST, "application/json"),
    ]

    results: dict[str, tuple[int, str]] = {}
    key_map = {
        CANONICAL_CROP_BOOK_BODY:     "body",
        CANONICAL_CROP_BOOK_DATA:     "data",
        CANONICAL_CROP_BOOK_MANIFEST: "manifest",
    }
    for local_path, canonical_filename, content_type in artifacts:
        media_id, url = upload_artifact(local_path, canonical_filename, content_type)
        results[key_map[canonical_filename]] = (media_id, url)

    # Build and upload the manifest-of-URLs pointer
    mou_payload = {
        "schema":       "crop_book.mou.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "body":     results["body"][1],
            "data":     results["data"][1],
            "manifest": results["manifest"][1],
        },
    }
    mou_path = output_dir / "sfagent-crop-book-manifest-of-urls.json"
    mou_path.write_text(_json.dumps(mou_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    mou_id, mou_url = upload_artifact(mou_path, CANONICAL_CROP_BOOK_MOU, "application/json")
    results["mou"] = (mou_id, mou_url)

    logger.info(
        "WP REST: all 4 crop book artifacts uploaded. MoU: %s", mou_url
    )
    return results
