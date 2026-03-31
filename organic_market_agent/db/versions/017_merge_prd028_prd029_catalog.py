"""017: Merge PRD028 → PRD027 and PRD029 → PRD026 (catalog_change_requests_v1).

Source: Nimrod export from tools/catalog_review.html (2026-03-30).
- PRD028 (סל ירקות משפחתי) → map to PRD027 (סל ירקות גדול)
- PRD029 (ארגז CSA שבועי) → map to PRD026 (סל ירקות בינוני)

Deletes daily_aggregates / weekly_snapshots for the source product ids so unique
constraints are not violated after normalized_observations.product_id is updated.

Follow-up: revision **018** deletes aggregates for merge targets PRD026/PRD027 and
cleans stray product_variants on PRD028/PRD029. Then run AggregatorEngine before
publishing.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def pid(code: str) -> int:
        row = conn.execute(text("SELECT id FROM products WHERE code = :c"), {"c": code}).one()
        return int(row[0])

    p26, p27, p28, p29 = pid("PRD026"), pid("PRD027"), pid("PRD028"), pid("PRD029")

    # Drop aggregate rows for merged-away products (avoid uq clash after observation remap).
    conn.execute(
        text("DELETE FROM daily_aggregates WHERE product_id IN (:p28, :p29)"),
        {"p28": p28, "p29": p29},
    )
    conn.execute(
        text("DELETE FROM weekly_snapshots WHERE product_id IN (:p28, :p29)"),
        {"p28": p28, "p29": p29},
    )

    conn.execute(
        text("UPDATE observation_flags SET product_id = :t WHERE product_id = :s"),
        {"t": p27, "s": p28},
    )
    conn.execute(
        text("UPDATE observation_flags SET product_id = :t WHERE product_id = :s"),
        {"t": p26, "s": p29},
    )

    conn.execute(
        text("UPDATE normalized_observations SET product_id = :t WHERE product_id = :s"),
        {"t": p27, "s": p28},
    )
    conn.execute(
        text("UPDATE normalized_observations SET product_id = :t WHERE product_id = :s"),
        {"t": p26, "s": p29},
    )

    # product_aliases: move rows to target when (alias_text_normalized, source_id) is free.
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

    reason = "catalog_change_requests_v1 (017): PRD028→PRD027, PRD029→PRD026"
    for src_code, tgt_code in (("PRD028", "PRD027"), ("PRD029", "PRD026")):
        conn.execute(
            text(
                """
                INSERT INTO product_merges (source_product_id, target_product_id, reason, merged_by)
                SELECT s.id, t.id, :reason, 'alembic_017'
                FROM products s
                CROSS JOIN products t
                WHERE s.code = :sc AND t.code = :tc
                  AND NOT EXISTS (
                    SELECT 1 FROM product_merges pm WHERE pm.source_product_id = s.id
                  )
                """
            ),
            {"reason": reason, "sc": src_code, "tc": tgt_code},
        )

    conn.execute(
        text("UPDATE products SET is_active = false WHERE code IN ('PRD028', 'PRD029')")
    )


def downgrade() -> None:
    raise NotImplementedError(
        "017_merge_prd028_prd029: irreversible — observation and alias remapping cannot "
        "be split safely; restore from backup if needed."
    )
