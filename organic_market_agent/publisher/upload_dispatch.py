"""Shared upload dispatch helper — static endpoint primary, optional FTPS fallback.

Single source of truth for all upload entrypoints:
  - organic_market_agent/__main__.py::_do_upload (CLI)
  - organic_market_agent/scheduler/pipeline.py (daily cron)
  - organic_market_agent/admin/routes/runs.py::runs_upload_now (Admin UI)

Primary path (WP009): static_upload.upload_all_artifacts() → custom REST endpoint
  POST /wp-json/sfagent/v1/upload → writes to Agents/smallfarmsagents/{subdir}/
  Fixed canonical URLs, no date-based path, no media-library accumulation.

Fallback: FTPS (gated on UPRESS_FALLBACK_FTPS=1, port 21 blocked on waldhomeserver).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from organic_market_agent.utils.config import Config

logger = logging.getLogger(__name__)


class NoUploadConfigured(Exception):
    """Raised when no upload method is configured."""


@dataclass
class UploadResult:
    """Structured result returned by dispatch_upload."""

    protocol_used: str  # "static" | "ftps" | "none"
    success: bool
    success_count: int
    total_count: int
    errors: list[str] = field(default_factory=list)
    # static upload path: canonical_name -> public_url
    static_artifacts: dict[str, str] = field(default_factory=dict)
    # FTPS path
    files_uploaded: list[str] = field(default_factory=list)
    files_failed: list[str] = field(default_factory=list)
    remote_base: str = ""

    # Legacy compat: callers that read .wp_artifacts still get something sensible
    @property
    def wp_artifacts(self) -> dict[str, tuple[int, str]]:
        return {k: (0, v) for k, v in self.static_artifacts.items()}


def dispatch_upload(
    output_dir: Path,
    *,
    profile: Literal["market", "crop_book"] = "market",
    allow_fallback_ftps_env: str = "UPRESS_FALLBACK_FTPS",
) -> UploadResult:
    """Static endpoint primary, optional FTPS fallback.

    Two profiles, each with its own upload path:

    profile="market" (default — WP009 behavior):
      1. If WP REST credentials configured → call static_upload.upload_all_artifacts().
      2. If that fails AND os.environ.get(allow_fallback_ftps_env) == "1" → FTPS fallback.
      3. Neither configured → raise NoUploadConfigured.

    profile="crop_book" (WP004):
      WP REST only via wp_upload.upload_all_crop_book_artifacts(). FTPS fallback
      intentionally disabled (Bezeq blocks port 21 outbound from waldhomeserver).
      Raises NoUploadConfigured if WP REST not configured.

    Args:
        output_dir: Directory containing publish artifacts.
        profile: "market" (default, WP009 static_upload + FTPS fallback) or
                 "crop_book" (WP REST only, no fallback).
        allow_fallback_ftps_env: Env var that gates FTPS fallback (market profile only).

    Returns:
        UploadResult with protocol_used, success, counts, artifacts.

    Raises:
        NoUploadConfigured: When no upload method is configured.
    """
    # --- Crop book profile: WP REST only, no FTPS fallback ---
    if profile == "crop_book":
        if not Config.wp_rest_configured():
            raise NoUploadConfigured(
                "WP REST not configured; FTPS disabled for crop_book profile. "
                "Set UPRESS_WP_APP_USER + UPRESS_WP_APP_PASS."
            )
        from organic_market_agent.publisher.wp_upload import upload_all_crop_book_artifacts

        artifacts = upload_all_crop_book_artifacts(output_dir)
        logger.info(
            "dispatch_upload(crop_book): WP REST upload OK — %d artifacts uploaded",
            len(artifacts),
        )
        # WP009 (commit d2d3426) refactored UploadResult: removed `wp_artifacts`
        # init kwarg in favor of `static_artifacts: dict[str, str]` (url-only)
        # plus a `wp_artifacts` @property that reconstructs (0, url) tuples
        # for legacy callers. This call site was not updated → production
        # TypeError on crop_book profile uploads (uploads succeeded, then
        # result construction crashed). Surface remained masked because the
        # test was treated as out-of-scope across patch02-patch08 cycles.
        #
        # Minimal fix: extract URL from each (media_id, url) tuple and store
        # in static_artifacts. The wp_artifacts property reconstructs
        # (0, url) tuples for callers — media_id is lost in this conversion,
        # acceptable because the IDs were already consumed by upload+delete
        # operations before this return statement.
        return UploadResult(
            protocol_used="wp_rest",
            success=True,
            success_count=len(artifacts),
            total_count=len(artifacts),
            static_artifacts={k: url for k, (_media_id, url) in artifacts.items()},
        )

    # --- Market profile (default): existing behavior unchanged (AC-15) ---
    fallback_allowed = os.environ.get(allow_fallback_ftps_env, "").strip() == "1"
    wp_rest_ok = Config.wp_rest_configured()
    ftps_ok = Config.ftps_configured()

    if not wp_rest_ok and not (fallback_allowed and ftps_ok):
        raise NoUploadConfigured(
            "No upload method configured. "
            "Set UPRESS_WP_APP_USER + UPRESS_WP_APP_PASS for static upload, "
            f"or {allow_fallback_ftps_env}=1 + FTPS credentials for FTPS fallback."
        )

    # --- Primary: static upload via sfagent/v1/upload REST endpoint ---
    if wp_rest_ok:
        from organic_market_agent.publisher.static_upload import (
            MissingCredentialsError as StaticMissingCredentialsError,
            upload_all_artifacts,
        )

        try:
            results = upload_all_artifacts(output_dir)
            logger.info(
                "dispatch_upload: static upload OK — %d artifacts → %s",
                len(results), Config.UPRESS_SFA_STATIC_ROOT,
            )
            return UploadResult(
                protocol_used="static",
                success=True,
                success_count=len(results),
                total_count=len(results),
                static_artifacts=results,
            )
        except StaticMissingCredentialsError as exc:
            logger.error("dispatch_upload: static upload credentials error — %s", exc)
            if not (fallback_allowed and ftps_ok):
                raise
            logger.warning(
                "dispatch_upload: static creds error; %s=1 → FTPS fallback",
                allow_fallback_ftps_env,
            )
        except Exception as exc:
            logger.error("dispatch_upload: static upload failed — %s", exc)
            if not (fallback_allowed and ftps_ok):
                raise
            logger.warning(
                "dispatch_upload: static upload failed; %s=1 → FTPS fallback",
                allow_fallback_ftps_env,
            )

    # --- Fallback: FTPS ---
    logger.info("dispatch_upload: using FTPS fallback")
    from organic_market_agent.publisher.ftps_upload import upload_artifacts as ftps_upload_artifacts

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
