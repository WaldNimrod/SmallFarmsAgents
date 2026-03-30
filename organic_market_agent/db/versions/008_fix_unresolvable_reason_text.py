"""008: Widen unresolvable_reason from VARCHAR(200) to TEXT."""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "raw_extracted_items",
        "unresolvable_reason",
        type_=sa.Text(),
        existing_type=sa.VARCHAR(200),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Truncate existing values before downgrade to avoid data loss errors.
    op.execute(
        "UPDATE raw_extracted_items "
        "SET unresolvable_reason = LEFT(unresolvable_reason, 200) "
        "WHERE LENGTH(unresolvable_reason) > 200"
    )
    op.alter_column(
        "raw_extracted_items",
        "unresolvable_reason",
        type_=sa.VARCHAR(200),
        existing_type=sa.Text(),
        existing_nullable=True,
    )
