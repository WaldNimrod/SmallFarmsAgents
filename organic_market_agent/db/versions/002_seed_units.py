"""Seed measurement_units and unit_conversions."""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO measurement_units (code, name_he, unit_type, is_normalizable) VALUES
        ('kg', 'קילוגרם', 'weight', true),
        ('g', 'גרם', 'weight', true),
        ('unit', 'יחידה', 'count', false),
        ('bunch', 'צרור', 'bundle', false),
        ('basket_small', 'סל קטן', 'basket', false),
        ('basket_medium', 'סל בינוני', 'basket', false),
        ('basket_large', 'סל גדול', 'basket', false),
        ('basket_family', 'סל משפחתי', 'basket', false),
        ('pack_250g', 'מארז 250 גרם', 'pack', true),
        ('pack_500g', 'מארז 500 גרם', 'pack', true),
        ('pack_1kg', 'מארז ק"ג', 'pack', true)
        """
    )
    op.execute(
        """
        INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type, product_id)
        SELECT f.id, t.id, 0.001, 'exact', NULL
        FROM measurement_units f, measurement_units t
        WHERE f.code = 'g' AND t.code = 'kg'
        """
    )
    op.execute(
        """
        INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type, product_id)
        SELECT f.id, t.id, 0.25, 'exact', NULL
        FROM measurement_units f, measurement_units t
        WHERE f.code = 'pack_250g' AND t.code = 'kg'
        """
    )
    op.execute(
        """
        INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type, product_id)
        SELECT f.id, t.id, 0.5, 'exact', NULL
        FROM measurement_units f, measurement_units t
        WHERE f.code = 'pack_500g' AND t.code = 'kg'
        """
    )
    op.execute(
        """
        INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type, product_id)
        SELECT f.id, t.id, 1.0, 'exact', NULL
        FROM measurement_units f, measurement_units t
        WHERE f.code = 'pack_1kg' AND t.code = 'kg'
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM unit_conversions")
    op.execute("DELETE FROM measurement_units")
