"""Normalizer rules list / create / disable (M5)."""
from __future__ import annotations

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import text

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import NormalizerRule

bp = Blueprint("rules", __name__)

# Mandate UI labels -> DB CHECK values (NormalizerRule.rule_kind)
UI_TO_DB_RULE_KIND = {
    "unit_map": "unit_map",
    "organic_flag": "organic_flag",
    "price_multiplier": "price_correction",
    "exclusion": "ignore_pattern",
    "product_alias": "product_alias",
    "quantity_parse": "quantity_parse",
    "benchmark_tag": "benchmark_tag",
    "basket_parse": "basket_parse",
}


@bp.route("/rules")
def rules_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT nr.id, nr.normalizer_profile_id, s.code AS src_code,
                   nr.rule_kind, nr.match_pattern, nr.match_type, nr.replacement_value,
                   nr.priority, nr.is_active, nr.notes
            FROM normalizer_rules nr
            JOIN normalizer_profiles np ON np.id = nr.normalizer_profile_id
            JOIN sources s ON s.id = np.source_id
            ORDER BY nr.normalizer_profile_id, nr.priority, nr.id
            """
        )
    ).all()
    grouped: dict[int, list[dict]] = {}
    for r in rows:
        pid = int(r[1])
        grouped.setdefault(pid, []).append(
            {
                "id": r[0],
                "profile_id": r[1],
                "src_code": r[2],
                "rule_kind": r[3],
                "match_pattern": r[4],
                "match_type": r[5],
                "replacement_value": r[6],
                "priority": r[7],
                "is_active": r[8],
                "notes": r[9],
            }
        )
    rules_active = rules_inactive = 0
    for rows in grouped.values():
        for row in rows:
            if row["is_active"]:
                rules_active += 1
            else:
                rules_inactive += 1
    return render_template(
        "admin/rules.html",
        grouped=grouped,
        rules_total=rules_active + rules_inactive,
        rules_active=rules_active,
        rules_inactive=rules_inactive,
    )


@bp.route("/rules/new", methods=["GET", "POST"])
@login_required
def rule_new():
    session = g.db_session
    profiles = session.execute(
        text(
            """
            SELECT np.id, s.code, s.name, np.normalizer_type
            FROM normalizer_profiles np
            JOIN sources s ON s.id = np.source_id
            WHERE np.is_active = true
            ORDER BY s.code
            """
        )
    ).all()
    profile_opts = [
        {"id": r[0], "label": f"{r[1]} — {r[2]} ({r[3]})"} for r in profiles
    ]

    if request.method == "POST":
        pid = request.form.get("profile_id")
        ui_kind = (request.form.get("rule_kind") or "").strip()
        match_pattern = (request.form.get("match_pattern") or "").strip()
        match_type = (request.form.get("match_type") or "exact").strip()
        replacement = (request.form.get("replacement_value") or "").strip() or None
        priority_raw = request.form.get("priority") or "100"
        notes = (request.form.get("notes") or "").strip() or None
        try:
            profile_id = int(pid)
            priority = int(priority_raw)
        except (TypeError, ValueError):
            flash("פרופיל או עדיפות לא תקינים.", "danger")
            return render_template("admin/rule_new.html", profiles=profile_opts, ui_kinds=UI_TO_DB_RULE_KIND)
        db_kind = UI_TO_DB_RULE_KIND.get(ui_kind)
        if not db_kind or not match_pattern:
            flash("סוג כלל או תבנית חסרים.", "danger")
            return render_template("admin/rule_new.html", profiles=profile_opts, ui_kinds=UI_TO_DB_RULE_KIND)
        actor = getattr(current_user, "display_name", None) or getattr(current_user, "email", None) or "admin"
        rule = NormalizerRule(
            normalizer_profile_id=profile_id,
            rule_kind=db_kind,
            match_pattern=match_pattern[:500],
            match_type=match_type if match_type in ("exact", "regex", "contains", "prefix") else "exact",
            replacement_value=replacement[:500] if replacement else None,
            priority=priority,
            is_active=True,
            created_by=str(actor)[:100],
            notes=notes,
        )
        session.add(rule)
        session.flush()
        audit_write(
            session,
            "create_rule",
            "normalizer_rule",
            entity_id=rule.id,
            after={
                "profile_id": profile_id,
                "rule_kind": db_kind,
                "match_pattern": match_pattern,
            },
        )
        session.commit()
        flash("כלל נוצר.", "success")
        return redirect(url_for("rules.rules_list"))

    return render_template(
        "admin/rule_new.html", profiles=profile_opts, ui_kinds=UI_TO_DB_RULE_KIND
    )


@bp.route("/rules/<int:rule_id>/disable", methods=["POST"])
@login_required
def rule_disable(rule_id: int):
    session = g.db_session
    rule = session.get(NormalizerRule, rule_id)
    if not rule:
        flash("כלל לא נמצא.", "danger")
        return redirect(url_for("rules.rules_list"))
    before = {"is_active": rule.is_active}
    rule.is_active = False
    audit_write(
        session,
        "disable_rule",
        "normalizer_rule",
        entity_id=rule.id,
        before=before,
        after={"is_active": False},
    )
    session.commit()
    flash("הכלל הושבת.", "success")
    return redirect(url_for("rules.rules_list"))
