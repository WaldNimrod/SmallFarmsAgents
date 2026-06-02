"""062: M13-PRE — last Teva conflicts (wakame noodle line) + spiralina pasta alias variant."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "062"
down_revision = "061"
branch_labels = None
depends_on = None

# Superseded by 063 (U+2019 apostrophe). Placeholder kept for downgrade pairing.
_SPIRAL_PASTA = "פסטה כוסמין אורגנית עם ספירולינה פטוצ\u2019יני – השדה"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE catalog_scope_skip_rules
            SET is_active = false,
                notes = COALESCE(notes, '') || ' [deactivated 062 M13-PRE wakame noodle]'
            WHERE id = 486
            """
        )
    )

    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
            )
            SELECT p.id, :at,
              lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
              0.97, true, s.id
            FROM products p
            CROSS JOIN sources s
            WHERE p.code = 'PRD096' AND s.code = 'SRC036'
              AND NOT EXISTS (
                SELECT 1 FROM product_aliases pa
                WHERE pa.alias_text_normalized =
                  lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                  AND pa.source_id = s.id
              )
            """
        ),
        {"at": _SPIRAL_PASTA, "at2": _SPIRAL_PASTA, "at3": _SPIRAL_PASTA},
    )

    conn.execute(
        text(
            """
            UPDATE raw_extracted_items rei
            SET extraction_status = 'extracted',
                unresolvable_reason = NULL,
                ignore_reason_code = NULL
            FROM source_fetch_runs sfr
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.source_fetch_run_id = sfr.id
              AND s.code = 'SRC036'
              AND (
                (rei.extraction_status = 'unresolvable' AND rei.raw_product_name LIKE '%ספירולינה%')
                OR (rei.extraction_status = 'ignored' AND rei.raw_product_name LIKE '%ואצות וואקמה%')
              )
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE catalog_scope_skip_rules
            SET is_active = true,
                notes = regexp_replace(
                    COALESCE(notes, ''),
                    ' \\[deactivated 062 M13-PRE wakame noodle\\]',
                    ''
                )
            WHERE id = 486
            """
        )
    )
    conn.execute(
        text(
            """
            DELETE FROM product_aliases pa
            USING sources s
            WHERE pa.source_id = s.id AND s.code = 'SRC036' AND pa.alias_text = :t
            """
        ),
        {"t": _SPIRAL_PASTA},
    )
