"""Stable prefixes for `pipeline_alerts.message` — every alert is logged; tags aid filtering and UX.

Convention: ``[CATEGORY:code]`` then a space, then human-readable English text.
SQL examples (PostgreSQL)::

    -- Simulation / pytest noise (safe to archive or delete after review)
    SELECT * FROM pipeline_alerts WHERE message LIKE '[SIMULATION:%';

    -- Expected admin/ops lifecycle (restart, stop-all)
    SELECT * FROM pipeline_alerts WHERE message LIKE '[OPS:%';
"""
from __future__ import annotations

# --- Operations (expected lifecycle; not application bugs)
TAG_OPS_PROCESS_RESTART = "[OPS:process_restart]"
TAG_OPS_ADMIN_STOP_ALL = "[OPS:admin_stop_all]"

# --- Automated scheduler summary (cron runner)
TAG_SCHEDULER_RUN_OUTCOME = "[SCHEDULER:run_outcome]"

# --- Pipeline worker
TAG_PIPELINE_MISSING_RUN = "[PIPELINE:missing_run]"
TAG_PIPELINE_NO_ACTIVE_SOURCES = "[PIPELINE:no_active_sources]"
TAG_PIPELINE_FAILURE = "[PIPELINE:failure]"
TAG_PIPELINE_UNFINISHED = "[PIPELINE:unfinished]"
TAG_PIPELINE_PUBLISH_ABORT = "[PIPELINE:publish_abort]"

# --- Tests / deliberate mocks (pytest with triggered_by=test)
TAG_SIMULATION_TEST = "[SIMULATION:test]"

# --- Aggregator (already used in engine)
# [AGG_PRICE_RULE:...] — kept in aggregator/engine.py

# --- Maintenance jobs (admin-triggered)
# [MAINTENANCE:...] — kept in admin/routes/maintenance.py

# --- FTPS upload to uPress (M7 Go-Live)
TAG_FTPS_UPLOAD_SUCCESS = "[FTPS:upload_ok]"
TAG_FTPS_UPLOAD_FAILURE = "[FTPS:upload_fail]"
TAG_FTPS_UPLOAD_PARTIAL = "[FTPS:upload_partial]"


def tagged_message(tag: str, body: str) -> str:
    """Prefix a single tag; body should not repeat the same bracket tag."""
    t = tag.strip()
    b = body.strip()
    if b.startswith(t):
        return b
    return f"{t} {b}"
