"""015: M5 — seed local admin user + observation_flags index.

MANDATE-M5-SCHEMA-TEAM20

audit_log already has idx_audit_log_entity (entity_type, entity_id) and
idx_audit_log_created (created_at) from 001_initial_schema. The mandate names
ix_audit_log_* would duplicate those columns; we do not add second indexes.
db.check asserts the 001 indexes are present.

users.email is already unique via uq_users_email (001); no extra constraint.
"""

import bcrypt
from alembic import op
from sqlalchemy import text

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None

ADMIN_EMAIL = "admin@local"
ADMIN_PASSWORD = "admin"
ADMIN_NAME = "Administrator"


def upgrade() -> None:
    conn = op.get_bind()
    pw_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    conn.execute(
        text(
            """
            INSERT INTO users (email, password_hash, display_name, role, is_active)
            VALUES (:email, :hash, :name, 'admin', true)
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {"email": ADMIN_EMAIL, "hash": pw_hash, "name": ADMIN_NAME},
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_observation_flags_product_id "
        "ON observation_flags (product_id)"
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM users WHERE email = :e"), {"e": ADMIN_EMAIL})
    op.execute("DROP INDEX IF EXISTS ix_observation_flags_product_id")
