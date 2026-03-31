"""Normalizer / raw pipeline diagnostics for admin (English UI strings)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, Response, g, render_template, request
from flask_login import login_required
from sqlalchemy import text

bp = Blueprint("diagnostics", __name__)

_REASON_BUCKET_SQL = text(
    """
    SELECT
      CASE
        WHEN rei.unresolvable_reason IS NULL OR rei.unresolvable_reason = '' THEN '(empty)'
        WHEN rei.unresolvable_reason LIKE 'no alias match%%' THEN 'no_alias_match'
        WHEN rei.unresolvable_reason = 'empty raw_product_name' THEN 'empty raw_product_name'
        WHEN rei.unresolvable_reason LIKE 'cannot parse price%%' THEN 'cannot_parse_price'
        WHEN rei.unresolvable_reason = 'empty raw_price_text' THEN 'empty raw_price_text'
        WHEN rei.unresolvable_reason LIKE 'non-positive price%%' THEN 'non_positive_price'
        WHEN rei.unresolvable_reason LIKE 'missing product_id%%' THEN 'missing_after_stages'
        ELSE 'other'
      END AS reason_bucket,
      COUNT(*)::int AS cnt
    FROM raw_extracted_items rei
    WHERE rei.extraction_status = 'unresolvable'
      AND rei.is_quarantined IS NOT TRUE
    GROUP BY 1
    ORDER BY cnt DESC
    """
)

_TOP_RAW_SQL = text(
    """
    SELECT COALESCE(rei.raw_product_name, '') AS raw_product_name,
           COUNT(*)::int AS cnt,
           MAX(rei.unresolvable_reason) AS sample_reason
    FROM raw_extracted_items rei
    WHERE rei.extraction_status = 'unresolvable'
      AND rei.is_quarantined IS NOT TRUE
    GROUP BY rei.raw_product_name
    ORDER BY cnt DESC
    LIMIT :lim
    """
)

_BY_SOURCE_SQL = text(
    """
    SELECT s.id, s.code, s.name,
           COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable')::int AS unres_cnt,
           COUNT(*)::int AS total_cnt
    FROM raw_extracted_items rei
    JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
    JOIN sources s ON s.id = sfr.source_id
    WHERE rei.extracted_at >= now() - interval '30 days'
    GROUP BY s.id, s.code, s.name
    HAVING COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') > 0
    ORDER BY unres_cnt DESC
    LIMIT 25
    """
)


def _recommendations(reason_rows: list[tuple[str, int]]) -> list[str]:
    total = sum(r[1] for r in reason_rows) or 1
    out: list[str] = []
    by_bucket = {r[0]: r[1] for r in reason_rows}
    if by_bucket.get("no_alias_match", 0) / total >= 0.35:
        out.append(
            "no_alias_match dominates: add global or source-scoped product_aliases and "
            "re-run catalog_renormalize; use /unresolved for top raw strings."
        )
    if by_bucket.get("cannot_parse_price", 0) + by_bucket.get("empty_raw_price_text", 0) > total * 0.25:
        out.append(
            "Price parsing failures are high: review parser output per source (HTML selectors) "
            "and normalizer price rules for common ILS formats."
        )
    if by_bucket.get("empty raw_product_name", 0) > 0:
        out.append(
            "empty raw_product_name: fix parser mapping so product title is populated before normalize."
        )
    if not out:
        out.append(
            "Review top buckets and per-source rates below; prioritize the largest bucket with "
            "targeted aliases (product) or parser fixes (price/empty fields)."
        )
    return out


def _collect_payload(session, raw_limit: int) -> dict[str, Any]:
    reason_rows = session.execute(_REASON_BUCKET_SQL).all()
    total_unres = sum(int(r[1]) for r in reason_rows)
    recs = _recommendations([(str(r[0]), int(r[1])) for r in reason_rows])
    reason_out = [
        {
            "bucket": r[0],
            "count": int(r[1]),
            "pct": round(100.0 * int(r[1]) / total_unres, 1) if total_unres else 0.0,
        }
        for r in reason_rows
    ]
    top_raw = session.execute(_TOP_RAW_SQL, {"lim": raw_limit}).all()
    top_raw_out = [
        {
            "raw_product_name": r[0],
            "count": int(r[1]),
            "sample_reason": (r[2] or "")[:200],
        }
        for r in top_raw
    ]
    src_rows = session.execute(_BY_SOURCE_SQL).all()
    src_out = []
    for r in src_rows:
        tot = int(r[4] or 0)
        ur = int(r[3] or 0)
        src_out.append(
            {
                "source_id": int(r[0]),
                "code": r[1],
                "name": r[2] or "",
                "unresolvable_count": ur,
                "total_rows_30d": tot,
                "rate_pct": round(100.0 * ur / tot, 1) if tot else 0.0,
            }
        )
    return {
        "schema": "normalizer_diagnostics_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "unresolvable_total": total_unres,
        "reason_buckets": reason_out,
        "top_raw_product_names": top_raw_out,
        "sources_30d": src_out,
        "recommendations": recs,
    }


@bp.route("/diagnostics/normalizer")
def normalizer_diagnostics():
    session = g.db_session
    lim = request.args.get("raw_limit", default=40, type=int)
    lim = max(5, min(lim, 200))
    payload = _collect_payload(session, lim)
    return render_template(
        "admin/diagnostics_normalizer.html",
        payload=payload,
        raw_limit=lim,
    )


@bp.route("/diagnostics/normalizer/export.json")
@login_required
def normalizer_diagnostics_export():
    session = g.db_session
    lim = request.args.get("raw_limit", default=80, type=int)
    lim = max(5, min(lim, 500))
    payload = _collect_payload(session, lim)
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        mimetype="application/json; charset=utf-8",
    )
