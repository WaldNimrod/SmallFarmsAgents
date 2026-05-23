"""043: ספר גידולים — backfill trust metadata on crop_variety_source_values.

Migration 042 added the columns (trust_tier, confidence_weight, is_outlier_rejected)
without the required backfill (LOD400 AC-15 / F-190-WP-A-LV-01 remediation).
This migration performs the backfill on the already-deployed live DB.

The backfill is idempotent — re-running will not corrupt data.
Skipped on SQLite (test dialect).

LOD400 AC-15 contract:
  - All source='team_00' rows → trust_tier='EX', confidence_weight=NULL
  - All source='JMF' rows → trust_tier='PR', confidence_weight=0.70
  - All source LIKE 'Tend%' rows → trust_tier='OP', confidence_weight=0.55
  - Rows with note LIKE '%OUTLIER_REJECTED%' → is_outlier_rejected=TRUE
"""

from __future__ import annotations

from alembic import op

revision = "043"
down_revision = "042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return  # backfill not needed for SQLite test databases

    # Step 1: backfill trust_tier from source label
    op.execute("""
        UPDATE crop_variety_source_values SET trust_tier = CASE
            WHEN source = 'team_00'    THEN 'EX'
            WHEN source LIKE 'NI%'     THEN 'NI'
            WHEN source = 'JMF'        THEN 'PR'
            WHEN source LIKE 'Tend%'   THEN 'OP'
            WHEN source LIKE 'OMA%'    THEN 'MK'
            WHEN source LIKE 'WB%'     THEN 'WB'
            WHEN source LIKE 'UC%'     THEN 'UC'
            ELSE 'PR'
        END
        WHERE trust_tier IS NULL
    """)

    # Step 2: backfill confidence_weight from class defaults
    # EX and NI are hard overrides → NULL (never blended)
    # UC rows start with NULL until moderator approves
    op.execute("""
        UPDATE crop_variety_source_values SET confidence_weight = CASE
            WHEN trust_tier = 'EX' THEN NULL
            WHEN trust_tier = 'NI' THEN NULL
            WHEN trust_tier = 'PR' THEN 0.70
            WHEN trust_tier = 'OP' THEN 0.55
            WHEN trust_tier = 'MK' THEN 0.40
            WHEN trust_tier = 'WB' THEN 0.30
            WHEN trust_tier = 'UC' THEN NULL
            ELSE 0.50
        END
        WHERE confidence_weight IS NULL AND trust_tier NOT IN ('EX', 'NI', 'UC')
    """)

    # Step 3: back-populate is_outlier_rejected from existing OUTLIER_REJECTED note marker
    op.execute("""
        UPDATE crop_variety_source_values
        SET is_outlier_rejected = TRUE
        WHERE note LIKE '%OUTLIER_REJECTED%'
          AND is_outlier_rejected = FALSE
    """)


def downgrade() -> None:
    # Cannot meaningfully un-backfill — this is a data migration only.
    # The columns themselves remain (downgrade 042 removes them).
    pass
