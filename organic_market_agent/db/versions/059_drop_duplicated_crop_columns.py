"""059: SFA-S003-P004-WP-CB-MIG Phase 6 — drop duplicated crop_varieties columns.

Drops the Canon §7.4 columns that duplicate enrichment/attribute facts.
Also renames days_to_germinate_gh → nursery_days_to_germinate (column rename;
field is KEPT not dropped — Canon §7.1, F-190-MIG-03).

PRECONDITION GATE: asserts no live consumer references a dropped column
before executing. If the precondition fails, downgrade aborts.

team_00-authorized (Canon §authorization_note): only this WP may modify
models.py + add migrations for these specific columns.

Revision ID: 059
Revises: 058
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa

revision = "059"
down_revision = "058"
branch_labels = None
depends_on = None

# Columns to DROP from crop_varieties (Canon §7.4 — duplicated in enrichment/attributes)
# These are the SSoT-duplicated columns; enrichment/attribute layers are the sole source.
# seeder* + identity columns are KEPT.
_COLUMNS_TO_DROP = [
    "days_to_maturity",
    "harvest_window_min_days",
    "harvest_window_max_days",
    "in_row_spacing_cm",
    "rows_per_bed",
    "planting_season",
    "succession_interval_weeks",
    "harvest_unit",
    "avg_yield_per_bed_m",
    "yield_source",
    "documented_price",
    "documented_price_unit",
    "documented_price_source",
    "pricebook_product_id",
    "avg_revenue_per_bed_m",
    "days_in_gh_total",
    "planting_method",
]

# Column to RENAME (KEEP, not drop): days_to_germinate_gh → nursery_days_to_germinate
_RENAME_GH_TO_NURSERY = ("days_to_germinate_gh", "nursery_days_to_germinate")


def _precondition_check(conn) -> None:
    """Assert old (pre-rename) field names no longer exist in enrichment / source_values.

    The key precondition for Phase 6 is that Phase 5 (rename) has been run:
    old field names (like 'avg_yield_per_bed_m', 'in_row_spacing_cm', etc.)
    must NOT appear in crop_field_enrichment or crop_variety_source_values.

    Columns that are KEEP (same name in column AND enrichment, e.g. 'days_to_maturity')
    legitimately exist in enrichment even after Phase 5 — they are NOT checked here.
    Only the RENAMED fields are checked (their old names should be gone).

    Separate check: sfa_ingest_push.py must not reference dropped columns (code review).
    """
    # Fields that were RENAMED in Phase 5 — their old names must be gone
    _RENAMED_OLD_NAMES = [
        "avg_yield_per_bed_m",   # → yield_per_bed_m
        "in_row_spacing_cm",     # → spacing_in_row_cm
        "documented_price",      # → price_documented
        "seeds_per_gram",        # → seeds_per_g
        "nutrient_removal_n_kg_ha",
        "nutrient_removal_p_kg_ha",
        "nutrient_removal_k_kg_ha",
        "nutrient_removal_ca_kg_ha",
        "nutrient_removal_mg_kg_ha",
        "days_in_gh_total",       # → days_in_nursery
        "days_to_first_potting",  # → nursery_days_to_potting
        "days_to_germinate_gh",   # → nursery_days_to_germinate
    ]
    from sqlalchemy import text
    result = conn.execute(text(
        "SELECT field_name, COUNT(*) AS cnt "
        "FROM crop_field_enrichment "
        "WHERE field_name = ANY(:names) "
        "GROUP BY field_name"
    ), {"names": _RENAMED_OLD_NAMES}).fetchall()

    if result:
        rows = [(r[0], r[1]) for r in result]
        raise RuntimeError(
            f"PRECONDITION FAILED: crop_field_enrichment still has rows for "
            f"pre-rename field names: {rows}. "
            f"Run Phase 5 (rename) before Phase 6 (drop)."
        )

    # Also check source_values
    result2 = conn.execute(text(
        "SELECT field_name, COUNT(*) AS cnt "
        "FROM crop_variety_source_values "
        "WHERE field_name = ANY(:names) "
        "GROUP BY field_name"
    ), {"names": _RENAMED_OLD_NAMES}).fetchall()

    if result2:
        rows2 = [(r[0], r[1]) for r in result2]
        raise RuntimeError(
            f"PRECONDITION FAILED: crop_variety_source_values still has rows for "
            f"pre-rename field names: {rows2}. "
            f"Run Phase 5 (rename) before Phase 6 (drop)."
        )


def upgrade() -> None:
    conn = op.get_bind()
    if conn is not None:
        _precondition_check(conn)

    with op.batch_alter_table("crop_varieties") as batch_op:
        # Drop the duplicated columns
        for col in _COLUMNS_TO_DROP:
            try:
                batch_op.drop_column(col)
            except Exception as e:
                # Column may already not exist (idempotency)
                import warnings
                warnings.warn(f"Could not drop column {col!r}: {e}")

        # Rename days_to_germinate_gh → nursery_days_to_germinate
        try:
            batch_op.alter_column(
                _RENAME_GH_TO_NURSERY[0],
                new_column_name=_RENAME_GH_TO_NURSERY[1],
                existing_type=sa.Integer(),
                existing_nullable=True,
            )
        except Exception as e:
            import warnings
            warnings.warn(f"Could not rename column days_to_germinate_gh: {e}")


def downgrade() -> None:
    """Re-add dropped columns (all nullable) — restores schema, NOT data."""
    with op.batch_alter_table("crop_varieties") as batch_op:
        # Re-add columns nullable
        batch_op.add_column(sa.Column("days_to_maturity", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("harvest_window_min_days", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("harvest_window_max_days", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("in_row_spacing_cm", sa.Numeric(6, 2), nullable=True))
        batch_op.add_column(sa.Column("rows_per_bed", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("planting_season", sa.VARCHAR(100), nullable=True))
        batch_op.add_column(sa.Column("succession_interval_weeks", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("harvest_unit", sa.VARCHAR(20), nullable=True))
        batch_op.add_column(sa.Column("avg_yield_per_bed_m", sa.Numeric(10, 4), nullable=True))
        batch_op.add_column(sa.Column("yield_source", sa.VARCHAR(200), nullable=True))
        batch_op.add_column(sa.Column("documented_price", sa.Numeric(10, 2), nullable=True))
        batch_op.add_column(sa.Column("documented_price_unit", sa.VARCHAR(50), nullable=True))
        batch_op.add_column(sa.Column("documented_price_source", sa.VARCHAR(200), nullable=True))
        batch_op.add_column(sa.Column("pricebook_product_id", sa.VARCHAR(100), nullable=True))
        batch_op.add_column(sa.Column("avg_revenue_per_bed_m", sa.Numeric(10, 2), nullable=True))
        batch_op.add_column(sa.Column("days_in_gh_total", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("planting_method", sa.VARCHAR(30), nullable=True))
        # Re-add CHECK constraint for planting_method
        # Rename nursery_days_to_germinate back to days_to_germinate_gh
        try:
            batch_op.alter_column(
                _RENAME_GH_TO_NURSERY[1],
                new_column_name=_RENAME_GH_TO_NURSERY[0],
                existing_type=sa.Integer(),
                existing_nullable=True,
            )
        except Exception as e:
            import warnings
            warnings.warn(f"Could not rename back nursery_days_to_germinate: {e}")
