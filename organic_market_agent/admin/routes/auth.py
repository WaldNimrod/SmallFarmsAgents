"""Admin login / logout."""
from __future__ import annotations

from datetime import datetime, timezone

import bcrypt
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from sqlalchemy import select

from organic_market_agent.admin.auth import AdminUser
from organic_market_agent.models.users import User as UserModel

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        session = g.db_session
        user = session.execute(select(UserModel).where(UserModel.email == email)).scalar_one_or_none()
        if user is None or not user.is_active:
            flash("אימייל או סיסמה שגויים.", "danger")
            return render_template("admin/login.html", email=email or "admin@local"), 200
        try:
            ok = bcrypt.checkpw(
                password.encode("utf-8"),
                user.password_hash.encode("utf-8"),
            )
        except (ValueError, TypeError):
            ok = False
        if not ok:
            flash("אימייל או סיסמה שגויים.", "danger")
            return render_template("admin/login.html", email=email), 200

        user.last_login_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        login_user(AdminUser(user.id, user.email, user.display_name), remember=True)
        next_url = request.args.get("next") or url_for("dashboard.index")
        return redirect(next_url)

    return render_template("admin/login.html", email="admin@local")


@bp.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash("יצאת מהמערכת.", "info")
    return redirect(url_for("auth.login"))
