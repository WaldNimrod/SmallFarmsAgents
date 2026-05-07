"""Shared upload dispatch helper — WP REST primary, optional FTPS fallback.

Single source of truth for all upload entrypoints:
  - organic_market_agent/__main__.py::_do_upload (CLI)
  - organic_market_agent/scheduler/pipeline.py (daily cron)
  - organic_market_agent/admin/routes/runs.py::runs_upload_now (Admin UI)

WP008 / F-190-01 remediation: extracted from __main__._do_upload so all
entrypoints share identical upload-policy semantics.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from organic_market_agent.utils.config import Config

logger = logging.getLogger(__name__)


class NoUploadConfigured(Exception):
    """Raised when neither WP REST nor FTPS fallback is configured."""


@dataclass
class UploadResult:
    """Structured result returned by dispatch_upload."""

    protocol_used: str  # "wp_rest" | "ftps" | "none"
    success: bool
    success_count: int
    total_count: int
    errors: list[str] = field(default_factory=list)
    # WP REST path: canonical_name -> (media_id, url)
    wp_artifacts: dict[str, tuple[int, str]] = field(default_factory=dict)
    # FTPS path
    files_uploaded: list[str] = field(default_factory=list)
    files_failed: list[str] = field(default_factory=list)
    remote_base: str = ""


def dispatch_upload(
    output_dir: Path,
    *,
    allow_fallback_ftps_env: str = "UPRESS_FALLBACK_FTPS",
) -> UploadResult:
    """WP REST primary, optional FTPS fallback. Single policy for all upload entrypoints.

    Steps:
    1. If WP REST is configured → call wp_upload.upload_all_artifacts(output_dir).
    2. If WP REST attempt raises AND os.environ.get(allow_fallback_ftps_env) == "1"
       → call ftps_upload.upload_artifacts(output_dir).
    3. If neither configured → raise NoUploadConfigured.

    Args:
        output_dir: Directory containing publish artifacts.
        allow_fallback_ftps_env: Name of the env var that gates FTPS fallback.
            Set to "1" to allow FTPS when WP REST is unavailable.

    Returns:
        UploadResult with protocol_used, success, counts, and any errors.

    Raises:
        NoUploadConfigured: When neither WP REST nor FTPS fallback is configured.
    """
    fallback_allowed = os.environ.get(allow_fallback_ftps_env, "").strip() == "1"
    wp_rest_ok = Config.wp_rest_configured()
    ftps_ok = Config.ftps_configured()  # FTPS keys present (not OR'd with WP REST here)

    if not wp_rest_ok and not (fallback_allowed and ftps_ok):
        raise NoUploadConfigured(
            "No upload method configured. "
            "Set UPRESS_WP_APP_USER + UPRESS_WP_APP_PASS for WP REST, "
            f"or {allow_fallback_ftps_env}=1 + FTPS credentials for FTPS fallback."
        )

    # --- Primary: WP REST ---
    if wp_rest_ok:
        from organic_market_agent.publisher.wp_upload import (
            MissingCredentialsError as WpMissingCredentialsError,
            upload_all_artifacts,
        )

        try:
            results = upload_all_artifacts(output_dir)
            logger.info(
                "dispatch_upload: WP REST upload OK — %d artifacts uploaded", len(results)
            )
            return UploadResult(
                protocol_used="wp_rest",
                success=True,
                success_count=len(results),
                total_count=len(results),
                wp_artifacts=results,
            )
        except WpMissingCredentialsError as exc:
            logger.error("dispatch_upload: WP REST credentials error — %s", exc)
            if not (fallback_allowed and ftps_ok):
                raise
            logger.warning(
                "dispatch_upload: WP REST creds error; %s=1 → attempting FTPS fallback",
                allow_fallback_ftps_env,
            )
        except Exception as exc:
            logger.error("dispatch_upload: WP REST upload failed — %s", exc)
            if not (fallback_allowed and ftps_ok):
                raise
            logger.warning(
                "dispatch_upload: WP REST failed; %s=1 → attempting FTPS fallback",
                allow_fallback_ftps_env,
            )

    # --- Fallback: FTPS (only reached when WP REST failed and fallback is gated on) ---
    logger.info("dispatch_upload: using FTPS fallback")
    from organic_market_agent.publisher.ftps_upload import upload_artifacts as ftps_upload_artifacts

    # Build file list from manifest
    import json

    manifest_path = output_dir / "manifest.json"
    ftps_files: list[str] = []
    if manifest_path.exists():
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in ("json", "html", "body"):
            versioned = manifest_data.get("artifacts", {}).get(key)
            if versioned:
                ftps_files.append(versioned)
        for key in ("json", "html", "body"):
            fixed = manifest_data.get("fixed_names", {}).get(key)
            if fixed:
                ftps_files.append(fixed)
        if (output_dir / "manifest_last_good.json").exists():
            ftps_files.append("manifest_last_good.json")
        ftps_files.append("manifest.json")

    result = ftps_upload_artifacts(output_dir, ftps_files)
    errors = list(result.files_failed) if result.files_failed else []
    if result.error:
        errors.append(result.error)

    return UploadResult(
        protocol_used="ftps",
        success=result.success,
        success_count=len(result.files_uploaded),
        total_count=len(ftps_files),
        errors=errors,
        files_uploaded=list(result.files_uploaded),
        files_failed=list(result.files_failed),
        remote_base=result.remote_base or "",
    )
