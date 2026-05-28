"""054: crop_source_weights — DB-driven source weights table (WP-C5 Phase A).

Replaces the Python-constant SOURCE_REGISTRY for blend weights with a
DB-backed table so weights can be re-tuned system-wide via a single SQL
UPDATE — no code deployment needed.

Per DECISION_RECORD_SFA-S003-P002-WP-C5_v1.0.0 §Decision 5 (team_00
critical requirement, verbatim):

  "זה חייב להיות שמור בבסיס הנתונים בצורה נפרדת כך שיתאפשר שינוי משקלים
  באופן קל ופשוט לכלל המערכת בהמשך בהתאם לנסיון בשטח והתוצר הסופי שיתקבל
  והמשוב שנקבל מהחקלאים."

Translation: weights must be stored in the DB in a separate way that
allows easy system-wide weight changes later based on field experience,
final output, and farmer feedback.

Revision ID: 054
Revises: 053
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "054"
down_revision = "053"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    op.create_table(
        "crop_source_weights",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        # exact label (e.g. 'JMF', 'team_00') OR prefix pattern (e.g. 'WR:*')
        sa.Column("source_label", sa.String(100), nullable=False, unique=True),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        # weight is NULL when is_hard_override=TRUE OR requires_moderation=TRUE
        sa.Column("weight", sa.Numeric(5, 4), nullable=True),
        sa.Column(
            "is_hard_override",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "requires_moderation",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "trust_tier IN ('EX','NI','PR','OP','MK','WB','UC','WR')",
            name="ck_csw_tier",
        ),
        # Hard overrides have NULL weight; non-hard rows need a weight OR
        # require moderation (UC default).
        sa.CheckConstraint(
            "(is_hard_override = TRUE AND weight IS NULL) "
            "OR (is_hard_override = FALSE AND "
            "    (weight IS NOT NULL OR requires_moderation = TRUE))",
            name="ck_csw_weight_consistency",
        ),
    )
    op.create_index(
        "idx_csw_tier", "crop_source_weights", ["trust_tier"]
    )

    # Postgres-only: trigger to bump updated_at on UPDATE.  team_00 audit
    # trail per Decision #5 ("notes" + "updated_at" track the last-tune
    # rationale and timestamp).
    if not is_sqlite:
        op.execute("""
            CREATE OR REPLACE FUNCTION csw_touch_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
              NEW.updated_at := CURRENT_TIMESTAMP;
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        op.execute("""
            CREATE TRIGGER trg_csw_touch_updated_at
            BEFORE UPDATE ON crop_source_weights
            FOR EACH ROW EXECUTE FUNCTION csw_touch_updated_at();
        """)


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"
    if not is_sqlite:
        op.execute("DROP TRIGGER IF EXISTS trg_csw_touch_updated_at ON crop_source_weights;")
        op.execute("DROP FUNCTION IF EXISTS csw_touch_updated_at();")
    op.drop_index("idx_csw_tier", "crop_source_weights")
    op.drop_table("crop_source_weights")
