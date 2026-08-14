"""Deploy-verification health surface for the Flask admin app (DV-1 leg).

New file justification (R5): `grep -rln 'health' --include='*.py' organic_market_agent`
returned no route module and no build-SHA surface (only unrelated DB/freshness
helpers), and `grep -rn 'AOS_BUILD_SHA\\|build_sha'` over the repo returned zero —
there was no existing file to extend. One blueprint per concern is the established
convention in `organic_market_agent/admin/routes/`.

The build SHA is resolved ONCE, at import time, i.e. when the serving process
starts. That is deliberate and load-bearing: a per-request `git rev-parse HEAD`
would report the SHA of the *working tree* rather than of the *running code*, so a
deploy whose `git pull` succeeded but whose service restart silently failed would
still answer with the new SHA — a false green. Resolving at process start makes a
stale process report its stale SHA, which is exactly what the post-receive hook
(`scripts/deploy/sfa_post_receive.sh`) compares against the pushed SHA (R4).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)

# Repo root = .../organic_market_agent/admin/routes/health.py -> up 3 levels.
_REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_build_sha() -> tuple[str, str]:
    """Return (build_sha, sha_source).

    Order: env `AOS_BUILD_SHA` (stamped by the deploy path — authoritative), then
    `git rev-parse HEAD` in the repo root (weaker: only equals the running code
    because it is read at process start), then `("unknown", "unavailable")`.
    """
    env_sha = (os.environ.get("AOS_BUILD_SHA") or "").strip()
    if env_sha:
        return env_sha, "env"

    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown", "unavailable"

    sha = out.stdout.strip()
    if out.returncode == 0 and sha:
        return sha, "git"
    return "unknown", "unavailable"


# Captured at import time == process start. See module docstring.
BUILD_SHA, BUILD_SHA_SOURCE = resolve_build_sha()


@bp.route("/api/health")
def health():
    """Unauthenticated, dependency-free liveness + build identity.

    Deliberately touches no database: this endpoint answers "which code is this
    process running", which must stay answerable even when a dependency is down.
    Bound to 127.0.0.1 by the systemd unit, and exposes no secret.
    """
    return jsonify(
        status="ok",
        build_sha=BUILD_SHA,
        sha_source=BUILD_SHA_SOURCE,
    )
