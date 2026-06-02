"""070: Fix PRD087–PRD100 default unit after 069 pantry code typo.

069 used ``PRD87`` … ``PRD100`` instead of zero-padded ``PRD087`` … ``PRD100``.
Sets pantry defaults to ``retail_pack`` and relabels matching observations.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "070"
down_revision = "069"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def uid(code: str) -> int:
        row = conn.execute(text("SELECT id FROM measurement_units WHERE code = :c"), {"c": code}).one()
        return int(row[0])

    rpack = uid("retail_pack")
    unit_id = uid("unit")

    pantry_codes = [f"PRD{n:03d}" for n in range(87, 101)]
    for pcode in pantry_codes:
        conn.execute(
            text(
                """
                UPDATE products p
                SET default_measurement_unit_id = :mu
                WHERE p.code = :code
                """
            ),
            {"mu": rpack, "code": pcode},
        )

    for pcode in pantry_codes:
        conn.execute(
            text(
                """
                UPDATE normalized_observations no
                SET display_unit_id = :new_mu,
                    normalized_unit_id = CASE
                      WHEN no.normalized_unit_id = :old_mu THEN :new_mu
                      ELSE no.normalized_unit_id
                    END
                FROM products p
                WHERE no.product_id = p.id
                  AND p.code = :pcode
                  AND no.display_unit_id = :old_mu
                """
            ),
            {"new_mu": rpack, "old_mu": unit_id, "pcode": pcode},
        )


def downgrade() -> None:
    raise NotImplementedError("070_fix_pantry_default_units: forward fix only.")
