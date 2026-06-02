"""058: M10.5 QA remediation — Teva search entry + scroll; SRC036 packaged organic scope-skips."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "058"
down_revision = "057"
branch_labels = None
depends_on = None

# Organic-only search (titles include אורגני) — meets AC2 ≥20 rows without conventional leakage.
_TEVA_SEARCH_ENTRY = (
    "https://www.teva-shuk.co.il/search?q=%D7%90%D7%95%D7%A8%D7%92%D7%A0%D7%99"
)

# Original M10.5 category entry (056) — restore on downgrade.
_TEVA_ORGANIC_CAT_ENTRY = (
    "https://www.teva-shuk.co.il/cat/"
    "%D7%A7%D7%98%D7%A0%D7%99%D7%95%D7%AA-%D7%95%D7%A4%D7%A1%D7%98%D7%95%D7%AA-"
    "%D7%90%D7%95%D7%A8%D7%92%D7%A0%D7%99%D7%95%D7%AA"
)

_SELECTOR_EXTRAS = {
    "headless_scroll_passes": 4,
    "headless_scroll_pause_ms": 1500,
}

# Lines without "– השדה" on Teva organic search (prefix longest-first for חלב שקדים variants).
# Chia: apostrophe may vary — regex.
_SCOPE_EXTRAS: list[tuple[int, str, str, str, str]] = [
    (3502, "dry_grocery", "prefix", "חלב שקדים אורגני 0% סוכר", "M10.5 SRC036 Teva packaged (search)"),
    (3503, "dry_grocery", "prefix", "מחית בננה ותפוח אורגנית", "M10.5 SRC036 Teva packaged (search)"),
    (3504, "dry_grocery", "prefix", "חלב אורז עם שקדים אורגני", "M10.5 SRC036 Teva packaged (search)"),
    (3505, "dry_grocery", "prefix", "ערמונים אורגניים קלווים כרם", "M10.5 SRC036 Teva packaged (search)"),
    (3506, "dry_grocery", "prefix", "קוואקר עבה אורגני ללא גלוטן", "M10.5 SRC036 Teva packaged (search)"),
    (3507, "dry_grocery", "prefix", "סילאן לחיץ אורגני 350גרם", "M10.5 SRC036 Teva packaged (search)"),
    (3508, "dry_grocery", "prefix", "קינואה רויאל אורגנית", "M10.5 SRC036 Teva packaged (search)"),
    (3509, "dry_grocery", "prefix", "רסק תפוחי עץ אורגני", "M10.5 SRC036 Teva packaged (search)"),
    (3510, "dry_grocery", "prefix", "חומוס אורגני", "M10.5 SRC036 Teva packaged (search)"),
    (3511, "dry_grocery", "prefix", "חלב שקדים אורגני", "M10.5 SRC036 Teva packaged (search)"),
    (3512, "dry_grocery", "prefix", "חמאת גהי אורגנית", "M10.5 SRC036 Teva packaged (search)"),
    (3513, "dry_grocery", "prefix", "קוואקר דק אורגני", "M10.5 SRC036 Teva packaged (search)"),
    (
        3514,
        "dry_grocery",
        "regex",
        r"זרעי צ.יה אורגני",
        "M10.5 SRC036 Teva chia (apostrophe-tolerant)",
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = :entry,
                selector_profile = COALESCE(selector_profile, '{}'::jsonb) || CAST(:extra AS jsonb)
            WHERE source_id = 36
            """
        ),
        {"entry": _TEVA_SEARCH_ENTRY, "extra": json.dumps(_SELECTOR_EXTRAS)},
    )

    for display_order, cat, mtype, pattern, notes in _SCOPE_EXTRAS:
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


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = :entry,
                selector_profile = selector_profile::jsonb
                  - 'headless_scroll_passes'
                  - 'headless_scroll_pause_ms'
                  - 'headless_merge_urls'
            WHERE source_id = 36
            """
        ),
        {"entry": _TEVA_ORGANIC_CAT_ENTRY},
    )

    for display_order, *_ in _SCOPE_EXTRAS:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"),
            {"d": display_order},
        )
