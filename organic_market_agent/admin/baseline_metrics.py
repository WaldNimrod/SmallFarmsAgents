"""Normalizer baseline snapshot JSON for before/after improvement tracking."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

SCHEMA = "normalizer_baseline_snapshot_v1"


def compute_normalizer_snapshot(session: Session) -> dict[str, Any]:
    """Aggregate counts for baseline / comparison (English keys)."""
    res = session.execute(
        text(
            """
            SELECT
              COUNT(*) FILTER (WHERE extraction_status = 'normalized') AS norm_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unres_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'extracted') AS ext_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'ignored') AS ign_cnt
            FROM raw_extracted_items
            """
        )
    ).one()
    norm_cnt, unres_cnt, ext_cnt, ign_cnt = (
        int(res[0] or 0),
        int(res[1] or 0),
        int(res[2] or 0),
        int(res[3] or 0),
    )
    denom = norm_cnt + unres_cnt
    resolution_pct = round(100.0 * norm_cnt / denom, 2) if denom else 0.0

    distinct_unresolved = int(
        session.execute(
            text(
                """
                SELECT COUNT(*) FROM (
                  SELECT 1
                  FROM raw_extracted_items rei
                  WHERE rei.extraction_status = 'unresolvable'
                    AND rei.is_quarantined IS NOT TRUE
                  GROUP BY rei.raw_product_name
                ) x
                """
            )
        ).scalar_one()
        or 0
    )

    return {
        "schema": SCHEMA,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "raw_extracted_items": {
            "normalized": norm_cnt,
            "unresolvable": unres_cnt,
            "extracted": ext_cnt,
            "ignored": ign_cnt,
        },
        "resolution_pct_norm_vs_unres": resolution_pct,
        "distinct_unresolved_raw_names": distinct_unresolved,
    }


def default_baseline_path() -> Path:
    """Default file path under project root (SmallFarmsAgents/data/)."""
    root = Path(__file__).resolve().parents[2]
    return root / "data" / "normalizer_baseline.json"


def resolve_baseline_path() -> Path:
    env = os.environ.get("NORMALIZER_BASELINE_JSON")
    if env:
        return Path(env)
    return default_baseline_path()


def write_baseline_snapshot_file(session: Session, path: Path | None = None) -> Path:
    """Write current DB snapshot to disk (same JSON as CLI `baseline_snapshot`)."""
    p = path or resolve_baseline_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    snap = compute_normalizer_snapshot(session)
    p.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def load_baseline_json(path: Path | None) -> dict[str, Any] | None:
    p = path or resolve_baseline_path()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def diff_against_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    """Human-oriented deltas for dashboard."""
    if baseline.get("schema") != SCHEMA:
        return {}
    b_raw = baseline.get("raw_extracted_items") or {}
    c_raw = current.get("raw_extracted_items") or {}
    b_pct = float(baseline.get("resolution_pct_norm_vs_unres") or 0)
    c_pct = float(current.get("resolution_pct_norm_vs_unres") or 0)
    b_dist = int(baseline.get("distinct_unresolved_raw_names") or 0)
    c_dist = int(current.get("distinct_unresolved_raw_names") or 0)
    return {
        "resolution_pct_delta": round(c_pct - b_pct, 2),
        "unresolvable_count_delta": int(c_raw.get("unresolvable", 0)) - int(b_raw.get("unresolvable", 0)),
        "distinct_unresolved_delta": c_dist - b_dist,
        "baseline_captured_at": baseline.get("captured_at"),
    }
