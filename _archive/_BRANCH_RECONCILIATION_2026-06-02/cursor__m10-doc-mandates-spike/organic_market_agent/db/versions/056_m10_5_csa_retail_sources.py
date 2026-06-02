"""056: M10.5 — CSA basket parsers (SRC033–035), Sellio retail (SRC036), normalizer types, profiles, aliases."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "056"
down_revision = "055"
branch_labels = None
depends_on = None

_SEL_SHORASHIM = {"csa_site": "havat_shorashim"}
_SEL_ORGANI = {"csa_site": "meshek_organi"}
_SEL_YOSEF = {"csa_site": "meshek_yosef"}
_SEL_TEVA = {
    "wait_for": "span.main_price",
    "post_load_delay_ms": 6000,
    "goto_wait_until": "load",
    "sellio_organic_only": True,
}

_TEVA_ORGANIC_CAT = (
    "https://www.teva-shuk.co.il/cat/"
    "%D7%A7%D7%98%D7%A0%D7%99%D7%95%D7%AA-%D7%95%D7%A4%D7%A1%D7%98%D7%95%D7%AA-"
    "%D7%90%D7%95%D7%A8%D7%92%D7%A0%D7%99%D7%95%D7%AA"
)
_YOSEF_BASKET_URL = (
    "https://meshek-yosef.co.il/"
    "%D7%A1%D7%9C-%D7%90%D7%95%D7%A8%D7%92%D7%A0%D7%99-"
    "%D7%A2%D7%93-%D7%94%D7%91%D7%99%D7%AA/"
)


def upgrade() -> None:
    op.drop_constraint("chk_np_normalizer_type", "normalizer_profiles", type_="check")
    op.create_check_constraint(
        "chk_np_normalizer_type",
        "normalizer_profiles",
        "normalizer_type IN ("
        "'easyfarm_catalog','simple_product_grid','basket_only',"
        "'retail_benchmark','official_wholesale','farmerim',"
        "'nizat','rexail','eranorgani','tamari','mypips',"
        "'csa_basket','sellio'"
        ")",
    )

    conn = op.get_bind()

    specs = [
        (33, "html_page", None, "https://www.havatshorashim.co.il/organic-basket", _SEL_SHORASHIM, "csa_basket", 30),
        (34, "html_page", None, "https://www.meshekorgani.co.il/basket", _SEL_ORGANI, "csa_basket", 30),
        (35, "html_page", None, _YOSEF_BASKET_URL, _SEL_YOSEF, "csa_basket", 30),
        (36, "html_page", "sellio", _TEVA_ORGANIC_CAT, _SEL_TEVA, "sellio", 120),
    ]

    for sid, fmode, pfam, entry, sel, ntype, to in specs:
        conn.execute(
            text(
                """
                INSERT INTO source_fetch_profiles (
                    source_id, platform_family, fetch_mode, entry_url, http_method,
                    is_active, selector_profile, timeout_seconds
                ) VALUES (
                    :sid, :pf, :fm, :entry, 'GET', true, CAST(:sp AS jsonb), :to
                )
                """
            ),
            {
                "sid": sid,
                "pf": pfam,
                "fm": fmode,
                "entry": entry,
                "sp": json.dumps(sel),
                "to": to,
            },
        )

    for sid, ntype in (
        (33, "csa_basket"),
        (34, "csa_basket"),
        (35, "csa_basket"),
        (36, "sellio"),
    ):
        conn.execute(
            text(
                """
                INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active, notes)
                VALUES (:sid, :nt, '1.0', true, 'M10.5 CSA / Sellio')
                """
            ),
            {"sid": sid, "nt": ntype},
        )

    conn.execute(
        text(
            """
            UPDATE sources
            SET is_active = true,
                status = 'active',
                updated_at = NOW()
            WHERE id IN (33, 34, 35, 36)
            """
        )
    )

    # Packaged dry goods sold on Teva organic aisle (supplier suffix — no V1 fresh SKU)
    _scope: list[tuple[int, str, str, str, str]] = [
        (3501, "dry_grocery", "contains", "– השדה", "M10.5 SRC036 HaSadeh packaged lines on Teva"),
    ]
    for display_order, cat, mtype, pattern, notes in _scope:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (
                    :d, :cat, :mtype, :pat, :notes, NULL, true
                )
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"d": display_order, "cat": cat, "mtype": mtype, "pat": pattern, "notes": notes},
        )

    alias_rows: list[tuple[str, str, str]] = [
        ("SRC033", "סל קטן", "PRD025"),
        ("SRC033", "סל גדול", "PRD027"),
        ("SRC033", "סל סטודנטים", "PRD025"),
        ("SRC034", "סל ירקות אורגני משפחתי", "PRD027"),
        ("SRC034", "סל ירקות אורגני בסיסי", "PRD025"),
    ]
    for src_code, alias_text, pcode in alias_rows:
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
                )
                SELECT p.id, :at,
                  lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
                  0.95, true, s.id
                FROM products p
                CROSS JOIN sources s
                WHERE p.code = :pcode AND s.code = :src
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa
                    WHERE pa.alias_text_normalized =
                      lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                      AND pa.source_id = s.id
                  )
                """
            ),
            {"at": alias_text, "at2": alias_text, "at3": alias_text, "pcode": pcode, "src": src_code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM normalizer_profiles WHERE source_id IN (33,34,35,36)"))
    conn.execute(text("DELETE FROM source_fetch_profiles WHERE source_id IN (33,34,35,36)"))
    conn.execute(
        text(
            """
            UPDATE sources
            SET is_active = false, status = 'candidate', updated_at = NOW()
            WHERE id IN (33, 34, 35, 36)
            """
        )
    )

    conn.execute(
        text("DELETE FROM catalog_scope_skip_rules WHERE display_order = 3501"),
    )

    for src_code, alias_text, _ in [
        ("SRC033", "סל קטן", "PRD025"),
        ("SRC033", "סל גדול", "PRD027"),
        ("SRC033", "סל סטודנטים", "PRD025"),
        ("SRC034", "סל ירקות אורגני משפחתי", "PRD027"),
        ("SRC034", "סל ירקות אורגני בסיסי", "PRD025"),
    ]:
        conn.execute(
            text(
                """
                DELETE FROM product_aliases pa
                USING sources s
                WHERE pa.source_id = s.id AND s.code = :sc AND pa.alias_text = :at
                """
            ),
            {"sc": src_code, "at": alias_text},
        )

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
