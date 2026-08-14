"""Minimal machine-checkable health surface for the SFA admin service.

Purpose (DV-1): give the deploy hook one URL it can poll to answer
"which commit is the process that is actually serving traffic running?".

Design constraints, in order of importance:

1. **Process-snapshot semantics.** ``build_sha`` is resolved ONCE, when the
   Flask app object is built (``create_app`` stores it in ``app.config``), and
   never re-resolved per request. This is what makes the value meaningful to a
   deploy verifier: if the service was NOT restarted after a pull, the old
   process keeps reporting the OLD sha and the hook's comparison fails. A
   per-request ``git rev-parse`` would read the freshly-pulled working tree and
   report the new sha even from a stale process — a green light for a deploy
   that never took effect.
2. **No auth, no DB.** The endpoint must answer while the database is down,
   otherwise a DB outage is indistinguishable from a bad deploy. It touches
   neither ``g.db_session`` nor ``flask_login``.
3. **Never raises.** Every failure path degrades to ``UNKNOWN_SHA`` rather than
   a 500, so the hook always gets a parseable answer.

``status`` is deliberately a liveness signal ("this process is up and serving"),
not a full readiness/dependency check.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from flask import Blueprint, current_app, jsonify

bp = Blueprint("health", __name__)

#: organic_market_agent/admin/routes/health.py -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]

#: Reported when the build sha cannot be determined at all.
UNKNOWN_SHA = "unknown"

#: Env var the deploy path may set to pin the sha explicitly.
BUILD_SHA_ENV = "AOS_BUILD_SHA"

#: Flask config key holding the process-start snapshot.
BUILD_SHA_CONFIG_KEY = "BUILD_SHA"


def _git_head_sha(repo_root: Path) -> str:
    """``git rev-parse HEAD`` in *repo_root*, or ``UNKNOWN_SHA`` on any failure."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return UNKNOWN_SHA
    sha = proc.stdout.strip()
    if proc.returncode != 0 or not sha:
        return UNKNOWN_SHA
    return sha


def resolve_build_sha(repo_root: Path | None = None) -> str:
    """Build sha of the code this process is running.

    ``AOS_BUILD_SHA`` wins when set and non-empty; otherwise fall back to the
    checkout's ``git rev-parse HEAD``. Call once per process (see module
    docstring) — ``create_app`` does exactly that.
    """
    env_sha = os.environ.get(BUILD_SHA_ENV, "").strip()
    if env_sha:
        return env_sha
    return _git_head_sha(repo_root if repo_root is not None else _REPO_ROOT)


@bp.get("/api/health")
def health():
    """Liveness + build identity. Always 200, always JSON."""
    sha = current_app.config.get(BUILD_SHA_CONFIG_KEY) or UNKNOWN_SHA
    return jsonify(
        {
            "status": "ok",
            "service": "sfa-admin",
            "build_sha": sha,
        }
    )
