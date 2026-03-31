"""018: Invalidate stale aggregates after PRD028/PRD029 merge (017).

017 moved normalized_observations to PRD026 and PRD027. Rows in
daily_aggregates / weekly_snapshots for those target products were computed
before the remap and are therefore wrong (sample_size, prices).

This revision deletes aggregates for PRD026 and PRD027 so the next
AggregatorEngine run rebuilds them solely from current observations.

Also removes any product_variants still attached to inactive merged products
(PRD028, PRD029) — defensive; baskets normally have none.

Downstream: run the pipeline aggregate step (or full AggregatorEngine) before
publishing.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    target_ids = conn.execute(
        text("SELECT id FROM products WHERE code IN ('PRD026', 'PRD027')")
    ).all()
    tids = [int(r[0]) for r in target_ids]
    if len(tids) != 2:
        raise RuntimeError("expected PRD026 and PRD027 in products table")

    for tid in tids:
        conn.execute(text("DELETE FROM daily_aggregates WHERE product_id = :tid"), {"tid": tid})
        conn.execute(text("DELETE FROM weekly_snapshots WHERE product_id = :tid"), {"tid": tid})

    merged_ids = conn.execute(
        text("SELECT id FROM products WHERE code IN ('PRD028', 'PRD029')")
    ).all()
    mids = [int(r[0]) for r in merged_ids]
    for mid in mids:
        conn.execute(
            text(
                "UPDATE normalized_observations SET product_variant_id = NULL "
                "WHERE product_variant_id IN (SELECT id FROM product_variants WHERE product_id = :mid)"
            ),
            {"mid": mid},
        )
        conn.execute(text("DELETE FROM product_variants WHERE product_id = :mid"), {"mid": mid})


def downgrade() -> None:
    pass
