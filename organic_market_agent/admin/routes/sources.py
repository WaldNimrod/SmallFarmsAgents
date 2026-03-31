"""Sources list and detail — GET /sources, GET /sources/<code>"""
from __future__ import annotations

from collections import Counter

import sqlalchemy as sa
from flask import Blueprint, abort, g, render_template
from sqlalchemy import text

from organic_market_agent.models import Source

bp = Blueprint("sources", __name__)

_RUN_ROW_STATUS_HE = {
    "success": "הצלחה",
    "failed": "נכשל",
    "running": "רץ",
    "partial": "חלקי",
    "completed": "הושלם",
}


@bp.route("/sources")
def source_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT s.id, s.code, s.name, s.source_tier, s.is_active, s.base_url,
                   lr.last_run,
                   COALESCE(agg.total_items, 0)::bigint AS items_extracted,
                   COALESCE(agg.resolved, 0)::bigint    AS resolved,
                   COALESCE(agg.unresolvable, 0)::bigint AS unresolvable
            FROM sources s
            LEFT JOIN (
              SELECT sfr.source_id, MAX(ir.finished_at) AS last_run
              FROM source_fetch_runs sfr
              JOIN ingestion_runs ir ON ir.id = sfr.ingestion_run_id
              GROUP BY sfr.source_id
            ) lr ON lr.source_id = s.id
            LEFT JOIN (
              SELECT sfr.source_id,
                     COUNT(rei.id) AS total_items,
                     COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized')   AS resolved,
                     COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unresolvable
              FROM raw_extracted_items rei
              JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
              GROUP BY sfr.source_id
            ) agg ON agg.source_id = s.id
            ORDER BY s.is_active DESC, s.code
            LIMIT 200
            """
        )
    ).all()
    out = []
    for r in rows:
        items = int(r[7] or 0)
        res, unres = int(r[8] or 0), int(r[9] or 0)
        den = res + unres
        pct = round(100.0 * res / den, 1) if den else None
        last_run = r[6]
        out.append(
            {
                "code": r[1],
                "name": r[2],
                "tier": r[3],
                "is_active": r[4],
                "url": r[5],
                "last_run": last_run.strftime("%Y-%m-%d %H:%M") if last_run else None,
                "items_extracted": items,
                "resolved": res,
                "unresolvable": unres,
                "resolution_pct": pct,
            }
        )
    total_sources = int(session.execute(text("SELECT COUNT(*) FROM sources")).scalar_one() or 0)
    sources_db_active = int(
        session.execute(text("SELECT COUNT(*) FROM sources WHERE is_active = true")).scalar_one()
        or 0
    )
    sources_db_inactive = int(
        session.execute(text("SELECT COUNT(*) FROM sources WHERE is_active = false")).scalar_one()
        or 0
    )
    return render_template(
        "admin/sources.html",
        sources=out,
        sources_total=total_sources,
        sources_db_active=sources_db_active,
        sources_db_inactive=sources_db_inactive,
    )


@bp.route("/sources/<code>")
def source_detail(code: str):
    session = g.db_session
    src = session.execute(sa.select(Source).where(Source.code == code)).scalar_one_or_none()
    if not src:
        abort(404)

    # Recent 5 ingestion runs for this source
    recent_runs = session.execute(
        text(
            """
            SELECT ir.id, ir.started_at, sfr.status,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized')   AS resolved,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unresolvable,
                   COUNT(rei.id) AS total
            FROM source_fetch_runs sfr
            JOIN ingestion_runs ir ON ir.id = sfr.ingestion_run_id
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE sfr.source_id = :sid
            GROUP BY ir.id, ir.started_at, sfr.status
            ORDER BY ir.started_at DESC
            LIMIT 5
            """
        ),
        {"sid": src.id},
    ).all()

    runs_out = [
        {
            "run_id": r[0],
            "started_at": r[1].strftime("%Y-%m-%d %H:%M") if r[1] else "—",
            "status": r[2],
            "resolved": int(r[3] or 0),
            "unresolvable": int(r[4] or 0),
            "total": int(r[5] or 0),
        }
        for r in recent_runs
    ]

    # Products observed from this source
    products_seen = session.execute(
        text(
            """
            SELECT p.canonical_name_he, p.code,
                   COUNT(no.id) AS obs_count,
                   AVG(COALESCE(no.normalized_price_value, no.price_amount)) AS avg_price,
                   MAX(no.observed_at) AS last_seen,
                   mu.name_he AS unit
            FROM normalized_observations no
            JOIN products p ON p.id = no.product_id
            LEFT JOIN measurement_units mu ON mu.id = no.display_unit_id
            WHERE no.source_id = :sid
            GROUP BY p.id, p.canonical_name_he, p.code, mu.name_he
            ORDER BY obs_count DESC
            """
        ),
        {"sid": src.id},
    ).all()

    prods_out = [
        {
            "name": r[0],
            "code": r[1],
            "obs_count": int(r[2] or 0),
            "avg_price": round(float(r[3]), 2) if r[3] else None,
            "last_seen": r[4].strftime("%Y-%m-%d") if r[4] else "—",
            "unit": r[5] or "—",
        }
        for r in products_seen
    ]

    # Top-50 unresolvable raw names
    unres_rows = session.execute(
        text(
            """
            SELECT raw_product_name, COUNT(*) AS cnt
            FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            WHERE sfr.source_id = :sid AND rei.extraction_status = 'unresolvable'
            GROUP BY raw_product_name
            ORDER BY cnt DESC
            LIMIT 50
            """
        ),
        {"sid": src.id},
    ).all()
    unresolved = [{"name": r[0] or "", "count": int(r[1])} for r in unres_rows]

    rsc = Counter(r["status"] for r in runs_out)
    source_recent_run_segments = [
        (_RUN_ROW_STATUS_HE.get(st, st), rsc[st]) for st in sorted(rsc.keys())
    ]

    return render_template(
        "admin/source_detail.html",
        source=src,
        recent_runs=runs_out,
        products_seen=prods_out,
        unresolved=unresolved,
        source_recent_run_segments=source_recent_run_segments,
    )
