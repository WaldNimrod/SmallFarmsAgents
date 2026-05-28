"""Upload freshness guard — resilience backstop for WP003 publish gap.

PURPOSE
-------
A transient DNS / NAT64 / endpoint blip in the 06:00 daily cron can leave the
public market manifest stale for a full day, even though the on-host artifact
generated successfully. This module compares on-host artifact_version against
the public manifest's artifact_version and re-attempts the upload pipeline
when they diverge.

DESIGN PRINCIPLES
-----------------
* **Additive only.** This module never modifies `upload_dispatch.py` or the
  collector / scheduler / static_upload code paths. It calls `dispatch_upload`
  as a black box (the same code path the daily cron uses).
* **Idempotent.** Safe to run repeatedly: if versions already match, it's a
  no-op.
* **Structured status.** Writes a JSON status file (`data/freshness_guard_status.json`)
  so external monitors / next-cron / on-call humans can read the verdict
  without parsing log lines.
* **Exit code as signal.** Exits 0 when the public manifest is fresh
  (already-fresh OR repaired-fresh). Exits non-zero when the gap persists
  after re-upload — this is the signal for human attention.

INVOCATION
----------
    cd /data/projects/smallfarmsagents
    .venv/bin/python -m organic_market_agent.publisher.freshness_guard

Suggested cron — 30 min after the daily 06:00 pipeline::

    30 6 * * * cd /data/projects/smallfarmsagents && \
        .venv/bin/python -m organic_market_agent.publisher.freshness_guard \
        >> logs/freshness_guard.log 2>&1

Author: team_99 (Home Server Team) — WP003 Pass-3 remediation, 2026-05-28.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("freshness_guard")

DEFAULT_OUTPUT_DIR = Path("output/public")
DEFAULT_STATUS_FILE = Path("data/freshness_guard_status.json")
FETCH_TIMEOUT_SECONDS = 15

LEGACY_PUBLIC_MANIFEST_URL = (
    "https://www.nimrod.bio/wp-content/uploads/market/manifest.json"
)


@dataclass
class GuardStatus:
    checked_at: str
    on_host_version: Optional[str]
    public_version: Optional[str]
    public_url: Optional[str]
    legacy_public_version: Optional[str]
    state: str  # fresh | stale | repaired | repair_failed | missing_local | error
    repair_attempted: bool
    repair_protocol_used: Optional[str]
    repair_errors: list[str]
    notes: list[str]


def _read_local_manifest(output_dir: Path) -> dict:
    path = output_dir / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"local manifest missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _fetch_remote_manifest(url: str) -> Optional[dict]:
    req = urllib.request.Request(
        url,
        headers={
            "Cache-Control": "no-cache",
            "User-Agent": "sfagent-freshness-guard/1.0 (+team_99 OPS)",
            "Accept": "application/json, */*;q=0.5",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        logger.warning("HTTPError fetching %s: %s", url, exc)
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Could not fetch %s: %s", url, exc)
        return None


def _public_manifest_url(local_manifest: dict) -> str:
    base = (local_manifest.get("upload_base") or "").rstrip("/")
    if not base:
        return LEGACY_PUBLIC_MANIFEST_URL
    return f"{base}/manifest.json"


def _attempt_repair(output_dir: Path) -> tuple[Optional[str], list[str]]:
    """Run the canonical dispatch_upload — same code path as daily cron."""
    from organic_market_agent.publisher.upload_dispatch import (
        NoUploadConfigured,
        dispatch_upload,
    )

    try:
        result = dispatch_upload(output_dir=output_dir)
        if result.success:
            return result.protocol_used, []
        return result.protocol_used, list(result.errors) or ["dispatch reported success=False with no errors"]
    except NoUploadConfigured as exc:
        return None, [f"NoUploadConfigured: {exc}"]
    except Exception as exc:
        return None, [f"{type(exc).__name__}: {exc}"]


def run_guard(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    status_file: Path = DEFAULT_STATUS_FILE,
    do_repair: bool = True,
) -> GuardStatus:
    notes: list[str] = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    try:
        local = _read_local_manifest(output_dir)
    except FileNotFoundError as exc:
        status = GuardStatus(
            checked_at=now,
            on_host_version=None,
            public_version=None,
            public_url=None,
            legacy_public_version=None,
            state="missing_local",
            repair_attempted=False,
            repair_protocol_used=None,
            repair_errors=[str(exc)],
            notes=["no local manifest — pipeline never produced one"],
        )
        _write_status(status_file, status)
        return status

    on_host_version = local.get("artifact_version")
    public_url = _public_manifest_url(local)

    remote = _fetch_remote_manifest(public_url)
    public_version = remote.get("artifact_version") if remote else None
    if remote is None:
        notes.append(f"public manifest absent or unparseable at {public_url}")

    legacy = _fetch_remote_manifest(LEGACY_PUBLIC_MANIFEST_URL)
    legacy_public_version = legacy.get("artifact_version") if legacy else None
    if legacy and legacy_public_version != public_version:
        notes.append(
            f"legacy URL still serves a different version "
            f"({legacy_public_version!r} at {LEGACY_PUBLIC_MANIFEST_URL})"
        )

    if public_version == on_host_version and public_version is not None:
        status = GuardStatus(
            checked_at=now,
            on_host_version=on_host_version,
            public_version=public_version,
            public_url=public_url,
            legacy_public_version=legacy_public_version,
            state="fresh",
            repair_attempted=False,
            repair_protocol_used=None,
            repair_errors=[],
            notes=notes,
        )
        _write_status(status_file, status)
        return status

    if not do_repair:
        status = GuardStatus(
            checked_at=now,
            on_host_version=on_host_version,
            public_version=public_version,
            public_url=public_url,
            legacy_public_version=legacy_public_version,
            state="stale",
            repair_attempted=False,
            repair_protocol_used=None,
            repair_errors=[],
            notes=notes + ["--no-repair flag set; skipping retry"],
        )
        _write_status(status_file, status)
        return status

    protocol, errors = _attempt_repair(output_dir)

    # Re-probe to confirm
    remote_after = _fetch_remote_manifest(public_url)
    public_version_after = (
        remote_after.get("artifact_version") if remote_after else None
    )
    if public_version_after == on_host_version and on_host_version is not None:
        final_state = "repaired"
    else:
        final_state = "repair_failed"
        notes.append(
            f"post-repair public_version={public_version_after!r} != "
            f"on_host_version={on_host_version!r}"
        )

    status = GuardStatus(
        checked_at=now,
        on_host_version=on_host_version,
        public_version=public_version_after,
        public_url=public_url,
        legacy_public_version=legacy_public_version,
        state=final_state,
        repair_attempted=True,
        repair_protocol_used=protocol,
        repair_errors=errors,
        notes=notes,
    )
    _write_status(status_file, status)
    return status


def _write_status(path: Path, status: GuardStatus) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(status), indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        logger.warning("could not write status file %s: %s", path, exc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare on-host vs public manifest; re-upload if behind."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory containing the local manifest.json (default: output/public)",
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        default=DEFAULT_STATUS_FILE,
        help="Where to write the structured status JSON (default: data/freshness_guard_status.json)",
    )
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Report state only; never call dispatch_upload",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full status JSON to stdout",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    status = run_guard(
        output_dir=args.output_dir,
        status_file=args.status_file,
        do_repair=not args.no_repair,
    )

    if args.json:
        print(json.dumps(asdict(status), indent=2))
    else:
        print(
            f"freshness_guard: state={status.state} "
            f"on_host={status.on_host_version} public={status.public_version} "
            f"repaired={status.repair_attempted} protocol={status.repair_protocol_used}"
        )
        if status.notes:
            for n in status.notes:
                print(f"  note: {n}")
        if status.repair_errors:
            for e in status.repair_errors:
                print(f"  error: {e}")

    return 0 if status.state in ("fresh", "repaired") else 1


if __name__ == "__main__":
    raise SystemExit(main())
