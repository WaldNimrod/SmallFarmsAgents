"""Read-only audit log pages."""
from __future__ import annotations

import json
from collections import Counter

from flask import Blueprint, g, render_template
from sqlalchemy import text

bp = Blueprint("audit_pages", __name__)


@bp.route("/audit")
def audit_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT al.created_at, al.actor_name, al.action, al.entity_type,
                   al.entity_id, al.before_state, al.after_state
            FROM audit_log al
            ORDER BY al.created_at DESC
            LIMIT 200
            """
        )
    ).all()
    items = []
    for r in rows:
        def _j(d):
            if d is None:
                return None
            try:
                return json.dumps(d, ensure_ascii=False, indent=2)
            except TypeError:
                return str(d)

        items.append(
            {
                "created_at": r[0],
                "actor_name": r[1],
                "action": r[2],
                "entity_type": r[3],
                "entity_id": r[4],
                "before_json": _j(r[5]),
                "after_json": _j(r[6]),
            }
        )
    total_audit = int(session.execute(text("SELECT COUNT(*) FROM audit_log")).scalar_one() or 0)
    act_counter = Counter(i["action"] for i in items)
    audit_action_segments = sorted(act_counter.items(), key=lambda x: (-x[1], x[0]))
    return render_template(
        "admin/audit.html",
        items=items,
        audit_total=total_audit,
        audit_action_segments=audit_action_segments,
    )
