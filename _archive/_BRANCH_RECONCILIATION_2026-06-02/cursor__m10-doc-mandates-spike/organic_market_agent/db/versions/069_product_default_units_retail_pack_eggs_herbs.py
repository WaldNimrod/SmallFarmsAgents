"""069: Default units — eggs (dozen carton), retail packs, herbs as bunch.

Aligns catalog with Nimrod review: eggs priced per ~12 pack; asparagus / berries /
passion fruit (fallback) not single-count where applicable; oregano / endive as bunch;
pantry SKUs as pack not generic יחידה. Existing observations that used the old
``unit`` default for these products are relabeled (price amounts unchanged).

Follow-up (not in this migration): per-source pack weights (e.g. silan 350g), passion
fruit kg vs pack disambiguation from raw text, Gadi basket line-count → basket tier.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "069"
down_revision = "068"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO measurement_units (code, name_he, unit_type, is_normalizable)
            VALUES
              ('egg_carton_12', 'אריזת 12 ביצים', 'pack', false),
              ('retail_pack', 'חבילה / אריזה', 'pack', false)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    def uid(code: str) -> int:
        row = conn.execute(text("SELECT id FROM measurement_units WHERE code = :c"), {"c": code}).one()
        return int(row[0])

    egg = uid("egg_carton_12")
    rpack = uid("retail_pack")
    bunch = uid("bunch")
    kg = uid("kg")
    unit_id = uid("unit")

    # (product_code, new_default_unit_id)
    product_unit_updates: list[tuple[str, int]] = [
        ("PRD067", egg),
        ("PRD071", rpack),
        ("PRD072", kg),
        ("PRD077", bunch),
        ("PRD083", rpack),
        ("PRD085", bunch),
        ("PRD086", rpack),
    ]
    for pcode, mu_id in product_unit_updates:
        conn.execute(
            text(
                """
                UPDATE products p
                SET default_measurement_unit_id = :mu
                WHERE p.code = :code
                """
            ),
            {"mu": mu_id, "code": pcode},
        )

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

    # Relabel observations that inherited the wrong generic ``unit`` default (no price math).
    def reunit(pcodes: list[str], new_mu: int) -> None:
        for pcode in pcodes:
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
                {"new_mu": new_mu, "old_mu": unit_id, "pcode": pcode},
            )

    reunit(["PRD067"], egg)
    reunit(["PRD071", "PRD083", "PRD086"], rpack)
    reunit(["PRD077", "PRD085"], bunch)
    reunit(pantry_codes, rpack)
    # PRD072: do not bulk-change observations (kg vs pack varies by source).


def downgrade() -> None:
    raise NotImplementedError(
        "069_product_default_units: forward relabel of observations; restore from backup if needed."
    )
