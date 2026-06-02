"""068: Point basket aliases at merge targets, not inactive PRD028/PRD029.

Catalog merge 017 maps PRD028 (family vegetable basket) → PRD027 (large basket) and
PRD029 (weekly CSA box) → PRD026 (medium basket). Later migrations re-inserted
aliases against inactive codes; this moves any remaining rows to the same targets.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "068"
down_revision = "067"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def pid(code: str) -> int:
        row = conn.execute(text("SELECT id FROM products WHERE code = :c"), {"c": code}).one()
        return int(row[0])

    p26, p27, p28, p29 = pid("PRD026"), pid("PRD027"), pid("PRD028"), pid("PRD029")

    for src, tgt in ((p28, p27), (p29, p26)):
        conn.execute(
            text(
                """
                UPDATE product_aliases pa
                SET product_id = :tgt
                WHERE pa.product_id = :src
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa2
                    WHERE pa2.product_id = :tgt
                      AND pa2.alias_text_normalized = pa.alias_text_normalized
                      AND pa2.source_id IS NOT DISTINCT FROM pa.source_id
                  )
                """
            ),
            {"src": src, "tgt": tgt},
        )
        conn.execute(
            text("DELETE FROM product_aliases WHERE product_id = :src"),
            {"src": src},
        )


def downgrade() -> None:
    raise NotImplementedError(
        "068_remap_aliases_off_inactive_prd028_prd029: forward data fix only; restore from backup."
    )
