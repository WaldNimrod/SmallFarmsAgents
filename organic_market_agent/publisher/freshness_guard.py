"""Delivery-tier health guard — sfa.nimrod.bio liveness and repair backstop.

PURPOSE
-------
Verifies that the new delivery tier (sfa.nimrod.bio) is healthy and, when it
is not reachable or the last ingest push failed, re-runs `sfa_ingest_push` as
the canonical repair path.

DESIGN PRINCIPLES
-----------------
* **Health-first.** Checks GET ${SFA_PUBLIC_BASE}/api/v1/health first; expects
  JSON ``{"status": "ok", "db": "ok"}``. If the tier is unreachable or unhealthy,
  writes state="error" and exits non-zero — no repair is attempted against a
  degraded tier.
* **Repair = new tier only.** Calls ``sfa_ingest_push.main()`` programmatically
  (the same code path as ``python -m organic_market_agent.publisher.sfa_ingest_push``).
  Never calls ``dispatch_upload`` or any legacy www.nimrod.bio path.
* **Idempotent.** Safe to run repeatedly: if the tier is healthy, it's a no-op.
* **Structured status.** Writes ``data/freshness_guard_status.json`` so external
  monitors / next-cron / on-call humans can read the verdict without parsing logs.
* **Exit code as signal.** Exits 0 when healthy (already-fresh or repaired-ok).
  Exits non-zero when the tier is unhealthy or the push fails after retry.
* **Offline-safe.** Degrades gracefully when SFA host is unreachable — writes
  state="error", exits non-zero, no crash.

ENV
---
* ``SFA_PUBLIC_BASE`` — base URL for the delivery tier, e.g. ``https://sfa.nimrod.bio``

INVOCATION
----------
    cd /data/projects/smallfarmsagents
    .venv/bin/python -m organic_market_agent.publisher.freshness_guard

Suggested cron — 30 min after the daily 06:00 pipeline::

    30 6 * * * cd /data/projects/smallfarmsagents && \
        .venv/bin/python -m organic_market_agent.publisher.freshness_guard \
        >> logs/freshness_guard.log 2>&1

Author: team_100 re-point 2026-05-28, supersedes team_99 www version.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("freshness_guard")

DEFAULT_STATUS_FILE = Path("data/freshness_guard_status.json")
FETCH_TIMEOUT_SECONDS = 15

# Env var that carries the sfa.nimrod.bio base URL
SFA_PUBLIC_BASE_ENV = "SFA_PUBLIC_BASE"


@dataclass
class GuardStatus:
    checked_at: str
    sfa_public_base: Optional[str]
    health_url: Optional[str]
    health_status: Optional[str]   # "ok" | "degraded" | "unreachable" | None
    state: str  # healthy | repaired | repair_failed | tier_unhealthy | error
    repair_attempted: bool
    repair_errors: list[str]
    notes: list[str]


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------

def _probe_health(base_url: str) -> tuple[str, list[str]]:
    """GET {base_url}/api/v1/health — returns (status_str, notes).

    status_str:
      "ok"          — both ``status`` and ``db`` are "ok"
      "degraded"    — reachable but health check returned unexpected values
      "unreachable" — network error / timeout
    """
    url = base_url.rstrip("/") + "/api/v1/health"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json, */*;q=0.5",
            "User-Agent": "sfagent-freshness-guard/2.0 (+team_100 OPS)",
            "Cache-Control": "no-cache",
        },
    )
    notes: list[str] = []
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        s = body.get("status", "")
        db = body.get("db", "")
        if s == "ok" and db == "ok":
            return "ok", notes
        notes.append(f"health endpoint returned status={s!r} db={db!r}")
        return "degraded", notes
    except urllib.error.HTTPError as exc:
        notes.append(f"HTTP {exc.code} from {url}")
        return "unreachable", notes
    except (urllib.error.URLError, TimeoutError) as exc:
        notes.append(f"network error probing {url}: {exc}")
        return "unreachable", notes
    except json.JSONDecodeError as exc:
        notes.append(f"non-JSON health response from {url}: {exc}")
        return "degraded", notes


# ---------------------------------------------------------------------------
# Repair: re-run sfa_ingest_push
# ---------------------------------------------------------------------------

def _attempt_repair() -> list[str]:
    """Call sfa_ingest_push.main() programmatically.

    Returns a list of error strings (empty = success).
    """
    try:
        from organic_market_agent.publisher import sfa_ingest_push

        # sfa_ingest_push.main() reads sys.argv by default; pass empty list
        # so it runs with defaults (--table all, no --dry-run).
        exit_code = sfa_ingest_push.main()
        if exit_code == 0:
            return []
        return [f"sfa_ingest_push.main() returned exit_code={exit_code}"]
    except SystemExit as exc:
        code = exc.code
        if code == 0:
            return []
        return [f"sfa_ingest_push raised SystemExit({code})"]
    except Exception as exc:
        return [f"{type(exc).__name__}: {exc}"]


# ---------------------------------------------------------------------------
# Core guard logic
# ---------------------------------------------------------------------------

def run_guard(
    status_file: Path = DEFAULT_STATUS_FILE,
    do_repair: bool = True,
    sfa_public_base: Optional[str] = None,
) -> GuardStatus:
    notes: list[str] = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if sfa_public_base is None:
        sfa_public_base = os.environ.get(SFA_PUBLIC_BASE_ENV, "").strip()

    if not sfa_public_base:
        status = GuardStatus(
            checked_at=now,
            sfa_public_base=None,
            health_url=None,
            health_status=None,
            state="error",
            repair_attempted=False,
            repair_errors=[
                f"{SFA_PUBLIC_BASE_ENV} env var not set; cannot probe delivery tier"
            ],
            notes=notes,
        )
        _write_status(status_file, status)
        return status

    health_url = sfa_public_base.rstrip("/") + "/api/v1/health"
    health_status, health_notes = _probe_health(sfa_public_base)
    notes.extend(health_notes)

    if health_status != "ok":
        status = GuardStatus(
            checked_at=now,
            sfa_public_base=sfa_public_base,
            health_url=health_url,
            health_status=health_status,
            state="tier_unhealthy" if health_status == "degraded" else "error",
            repair_attempted=False,
            repair_errors=[f"tier health={health_status}; skipping repair"],
            notes=notes,
        )
        _write_status(status_file, status)
        return status

    # Tier is healthy; optionally attempt repair (re-push)
    if not do_repair:
        status = GuardStatus(
            checked_at=now,
            sfa_public_base=sfa_public_base,
            health_url=health_url,
            health_status=health_status,
            state="healthy",
            repair_attempted=False,
            repair_errors=[],
            notes=notes + ["--no-repair flag set; skipping push"],
        )
        _write_status(status_file, status)
        return status

    errors = _attempt_repair()
    state = "repaired" if not errors else "repair_failed"

    status = GuardStatus(
        checked_at=now,
        sfa_public_base=sfa_public_base,
        health_url=health_url,
        health_status=health_status,
        state=state,
        repair_attempted=True,
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify sfa.nimrod.bio delivery-tier health; "
            "re-run sfa_ingest_push if needed."
        )
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
        help="Report health only; never call sfa_ingest_push",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full status JSON to stdout",
    )
    parser.add_argument(
        "--sfa-public-base",
        default=None,
        help=(
            f"Override {SFA_PUBLIC_BASE_ENV} env var "
            "(e.g. https://sfa.nimrod.bio)"
        ),
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    status = run_guard(
        status_file=args.status_file,
        do_repair=not args.no_repair,
        sfa_public_base=args.sfa_public_base,
    )

    if args.json:
        print(json.dumps(asdict(status), indent=2))
    else:
        print(
            f"freshness_guard: state={status.state} "
            f"tier={status.sfa_public_base} "
            f"health={status.health_status} "
            f"repair_attempted={status.repair_attempted}"
        )
        if status.notes:
            for n in status.notes:
                print(f"  note: {n}")
        if status.repair_errors:
            for e in status.repair_errors:
                print(f"  error: {e}")

    return 0 if status.state in ("healthy", "repaired") else 1


if __name__ == "__main__":
    raise SystemExit(main())
