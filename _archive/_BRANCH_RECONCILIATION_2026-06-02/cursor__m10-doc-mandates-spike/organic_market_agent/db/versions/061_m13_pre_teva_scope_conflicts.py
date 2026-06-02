"""061: M13-PRE — deactivate global scope rules that block SRC036 pantry aliases."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "061"
down_revision = "060"
branch_labels = None
depends_on = None

# Rules that substring-match Teva organic search titles after 059 aliases are applied.
_RULE_IDS = (6, 359, 375, 469, 614)


def upgrade() -> None:
    conn = op.get_bind()
    for rid in _RULE_IDS:
        conn.execute(
            text(
                """
                UPDATE catalog_scope_skip_rules
                SET is_active = false,
                    notes = COALESCE(notes, '') || ' [deactivated 061 M13-PRE Teva conflicts]'
                WHERE id = :rid
                """
            ),
            {"rid": rid},
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
              AND rei.extraction_status = 'ignored'
              AND rei.ignore_reason_code = 'approved_scope_skip'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    for rid in _RULE_IDS:
        conn.execute(
            text(
                """
                UPDATE catalog_scope_skip_rules
                SET is_active = true,
                    notes = regexp_replace(
                        COALESCE(notes, ''),
                        ' \\[deactivated 061 M13-PRE Teva conflicts\\]',
                        ''
                    )
                WHERE id = :rid
                """
            ),
            {"rid": rid},
        )
