"""Shared raw-pipeline counts for publish artifacts and admin (English keys)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def compute_raw_pipeline_counts(session: Session) -> dict[str, Any]:
    """Single-query snapshot of raw_extracted_items + active scope-skip rule count."""
    row = session.execute(
        text(
            """
            SELECT
              COUNT(*) FILTER (WHERE extraction_status = 'normalized')::int AS normalized,
              COUNT(*) FILTER (WHERE extraction_status = 'unresolvable')::int AS unresolvable,
              COUNT(*) FILTER (WHERE extraction_status = 'extracted')::int AS extracted_pending,
              COUNT(*) FILTER (WHERE extraction_status = 'ignored')::int AS ignored,
              COUNT(*) FILTER (
                WHERE extraction_status = 'ignored'
                  AND ignore_reason_code = 'approved_scope_skip'
              )::int AS ignored_approved_scope_skip
            FROM raw_extracted_items
            """
        )
    ).one()
    n_norm = int(row[0] or 0)
    n_unres = int(row[1] or 0)
    n_ext = int(row[2] or 0)
    n_ign = int(row[3] or 0)
    n_ign_apr = int(row[4] or 0)
    denom = n_norm + n_unres
    resolution_pct = round(100.0 * n_norm / denom, 2) if denom else 0.0

    n_rules = int(
        session.execute(
            text("SELECT COUNT(*)::int FROM catalog_scope_skip_rules WHERE is_active = true")
        ).scalar_one()
        or 0
    )

    return {
        "raw_extracted_items": {
            "normalized": n_norm,
            "unresolvable": n_unres,
            "extracted_pending": n_ext,
            "ignored": n_ign,
            "ignored_approved_scope_skip": n_ign_apr,
        },
        "resolution_pct_norm_vs_unres": resolution_pct,
        "active_scope_skip_rules": n_rules,
    }
