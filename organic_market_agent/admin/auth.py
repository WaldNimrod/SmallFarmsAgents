"""Flask-Login setup and admin user wrapper."""
from __future__ import annotations

from flask_login import LoginManager, UserMixin

from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models.users import User as UserModel

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "יש להתחבר כדי לגשת לעמוד זה."


class AdminUser(UserMixin):
    """Lightweight user for Flask-Login (no bound SQLAlchemy session)."""

    def __init__(self, uid: int, email: str, display_name: str | None) -> None:
        self._uid = uid
        self.email = email
        self.display_name = display_name

    def get_id(self) -> str:
        return str(self._uid)


@login_manager.user_loader
def load_user(user_id: str) -> AdminUser | None:
    with SessionFactory() as session:
        u = session.get(UserModel, int(user_id))
        if u is None or not u.is_active:
            return None
        return AdminUser(u.id, u.email, u.display_name)
