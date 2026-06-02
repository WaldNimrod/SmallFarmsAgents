"""036: M10.3 — extend normalizer_type CHECK; activate SRC025–SRC028 with fetch + normalizer profiles."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None

_SPECS: list[tuple[int, str, str, str, str, dict]] = [
    (
        25,
        "SRC025",
        "nizat",
        "nizat",
        "https://www.nizat.com/ירקות-אורגניים-c28",
        {
            "product_card": ".productcubecontainer",
            "name": ".productcubepname",
            "price": ".productcubeprice",
        },
    ),
    (
        26,
        "SRC026",
        "rexail",
        "rexail",
        "https://www.bensfarm.co.il/",
        {},
    ),
    (
        27,
        "SRC027",
        "eranorgani",
        "eranorgani",
        "https://www.eranorgani.co.il/",
        {},
    ),
    (
        28,
        "SRC028",
        "tamari",
        "tamari",
        "https://shop.tamari-farm.co.il/",
        {},
    ),
]


def upgrade() -> None:
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

    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM normalizer_profiles WHERE source_id IN (25, 26, 27, 28)")
    )
    conn.execute(
        text("DELETE FROM source_fetch_profiles WHERE source_id IN (25, 26, 27, 28)")
    )

    for sid, _code, platform, ntype, entry, sel in _SPECS:
        conn.execute(
            text(
                """
                INSERT INTO source_fetch_profiles (
                    source_id, platform_family, fetch_mode, entry_url, http_method,
                    is_active, selector_profile
                ) VALUES (
                    :sid, :pf, 'html_page', :entry, 'GET', true, CAST(:sp AS jsonb)
                )
                """
            ),
            {"sid": sid, "pf": platform, "entry": entry, "sp": json.dumps(sel)},
        )
        conn.execute(
            text(
                """
                INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active)
                VALUES (:sid, :nt, '1.0', true)
                """
            ),
            {"sid": sid, "nt": ntype},
        )

    conn.execute(
        text(
            """
            UPDATE sources
            SET is_active = true, status = 'active', updated_at = NOW()
            WHERE id IN (25, 26, 27, 28)
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM normalizer_profiles WHERE source_id IN (25, 26, 27, 28)")
    )
    conn.execute(
        text("DELETE FROM source_fetch_profiles WHERE source_id IN (25, 26, 27, 28)")
    )
    conn.execute(
        text(
            """
            UPDATE sources
            SET is_active = false, status = 'candidate', updated_at = NOW()
            WHERE id IN (25, 26, 27, 28)
            """
        )
    )

    op.drop_constraint("chk_np_normalizer_type", "normalizer_profiles", type_="check")
    op.create_check_constraint(
        "chk_np_normalizer_type",
        "normalizer_profiles",
        "normalizer_type IN ("
        "'easyfarm_catalog','simple_product_grid','basket_only',"
        "'retail_benchmark','official_wholesale','farmerim'"
        ")",
    )
