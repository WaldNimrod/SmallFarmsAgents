"""040: M10.4 — extend normalizer_type for mypips; activate 9 priority mypips sources."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "040"
down_revision = "039"
branch_labels = None
depends_on = None

_PRIORITY_CODES = (
    "SRC041",
    "SRC042",
    "SRC053",
    "SRC055",
    "SRC060",
    "SRC061",
    "SRC062",
    "SRC069",
    "SRC070",
)

_DEFAULT_SELECTOR = {
    "wait_for": "div.pips-card-content",
    "wait_for_state": "attached",
    "post_load_delay_ms": 8000,
    "dismiss_ok_button_name": "אוקיי",
    "click_category_tabs": False,
}

_LARGE_CATALOG_SELECTOR = {
    "wait_for": "div.pips-card-content",
    "wait_for_state": "attached",
    "post_load_delay_ms": 8000,
    "dismiss_ok_button_name": "אוקיי",
    "click_category_tabs": True,
}


def upgrade() -> None:
    op.drop_constraint("chk_np_normalizer_type", "normalizer_profiles", type_="check")
    op.create_check_constraint(
        "chk_np_normalizer_type",
        "normalizer_profiles",
        "normalizer_type IN ("
        "'easyfarm_catalog','simple_product_grid','basket_only',"
        "'retail_benchmark','official_wholesale','farmerim',"
        "'nizat','rexail','eranorgani','tamari','mypips'"
        ")",
    )

    conn = op.get_bind()
    for code in _PRIORITY_CODES:
        sel = _LARGE_CATALOG_SELECTOR if code == "SRC053" else _DEFAULT_SELECTOR
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET platform_family = 'mypips',
                    is_active = true,
                    timeout_seconds = 120,
                    selector_profile = CAST(:sp AS jsonb),
                    updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code
                """
            ),
            {"code": code, "sp": json.dumps(sel)},
        )
        conn.execute(
            text(
                """
                UPDATE normalizer_profiles np
                SET normalizer_type = 'mypips',
                    is_active = true,
                    notes = 'M10.4 mypips Playwright pipeline',
                    updated_at = NOW()
                FROM sources s
                WHERE np.source_id = s.id AND s.code = :code
                """
            ),
            {"code": code},
        )
        conn.execute(
            text(
                """
                UPDATE sources
                SET is_active = true, status = 'active', updated_at = NOW()
                WHERE code = :code
                """
            ),
            {"code": code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code in _PRIORITY_CODES:
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET platform_family = NULL,
                    is_active = false,
                    timeout_seconds = 30,
                    selector_profile = NULL,
                    updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code
                """
            ),
            {"code": code},
        )
        conn.execute(
            text(
                """
                UPDATE normalizer_profiles np
                SET normalizer_type = 'simple_product_grid',
                    is_active = false,
                    notes = 'Placeholder until MyPIPS parser; keep inactive.',
                    updated_at = NOW()
                FROM sources s
                WHERE np.source_id = s.id AND s.code = :code
                """
            ),
            {"code": code},
        )
        conn.execute(
            text(
                """
                UPDATE sources
                SET is_active = false, status = 'candidate', updated_at = NOW()
                WHERE code = :code
                """
            ),
            {"code": code},
        )

    op.drop_constraint("chk_np_normalizer_type", "normalizer_profiles", type_="check")
    op.create_check_constraint(
        "chk_np_normalizer_type",
        "normalizer_profiles",
        "normalizer_type IN ("
        "'easyfarm_catalog','simple_product_grid','basket_only',"
        "'retail_benchmark','official_wholesale','farmerim',"
        "'nizat','rexail','eranorgani','tamari'"
        ")",
    )
