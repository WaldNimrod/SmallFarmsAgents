"""033: Extend raw_extracted_items extraction_status for pending_manual; seed SRC_WA + profiles.

Per ARCH-20260408-TEAM20-RESPONSE-V1-1 §3.6–3.7. Fetch/normalizer stubs follow
2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md (operational parity); sources row
uses ARCH canonical name and priority.

Renumbered from branch migration 073 (cursor/m10-doc-mandates-spike@bb981ed).
down_revision updated to point to migration 032 (cq_p01_alias_batch).
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "033"
down_revision = "032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE raw_extracted_items DROP CONSTRAINT chk_rei_extraction_status")
    op.execute(
        """
        ALTER TABLE raw_extracted_items ADD CONSTRAINT chk_rei_extraction_status
        CHECK (extraction_status IN (
            'extracted','normalized','unresolvable','ignored','pending_manual'
        ))
        """
    )

    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO sources (
                code, name, base_url, source_group, market_scope, sales_channel,
                status, priority, is_active, source_tier
            ) VALUES (
                'SRC_WA',
                'WhatsApp Community Submissions',
                NULL,
                'direct_price',
                'community',
                'community_direct',
                'active',
                3,
                true,
                'price_grid'
            )
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        text(
            """
            INSERT INTO source_fetch_profiles (
                source_id, platform_family, fetch_mode, entry_url, http_method,
                schedule_kind, is_active
            )
            SELECT
                s.id,
                NULL,
                'html_page',
                'https://nimrod.bio/',
                'GET',
                'manual_check',
                false
            FROM sources s
            WHERE s.code = 'SRC_WA'
              AND NOT EXISTS (
                  SELECT 1 FROM source_fetch_profiles sfp WHERE sfp.source_id = s.id
              )
            """
        )
    )

    conn.execute(
        text(
            """
            INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active)
            SELECT s.id, 'simple_product_grid', '1.0', true
            FROM sources s
            WHERE s.code = 'SRC_WA'
              AND NOT EXISTS (
                  SELECT 1 FROM normalizer_profiles np WHERE np.source_id = s.id
              )
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            DELETE FROM normalizer_rules
            WHERE normalizer_profile_id IN (
                SELECT np.id FROM normalizer_profiles np
                JOIN sources s ON s.id = np.source_id
                WHERE s.code = 'SRC_WA'
            )
            """
        )
    )
    conn.execute(
        text(
            """
            DELETE FROM normalizer_profiles np
            USING sources s
            WHERE np.source_id = s.id AND s.code = 'SRC_WA'
            """
        )
    )
    conn.execute(
        text(
            """
            DELETE FROM source_fetch_profiles sfp
            USING sources s
            WHERE sfp.source_id = s.id AND s.code = 'SRC_WA'
            """
        )
    )
    conn.execute(text("DELETE FROM sources WHERE code = 'SRC_WA'"))

    op.execute("ALTER TABLE raw_extracted_items DROP CONSTRAINT IF EXISTS chk_rei_extraction_status")
    op.execute(
        """
        ALTER TABLE raw_extracted_items ADD CONSTRAINT chk_rei_extraction_status
        CHECK (extraction_status IN ('extracted','normalized','unresolvable','ignored'))
        """
    )
