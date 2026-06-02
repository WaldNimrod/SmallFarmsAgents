"""053: M10.4 R2 — aliases + scope-skip for SRC060/SRC070 T04 (≥90% resolution)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "053"
down_revision = "052"
branch_labels = None
depends_on = None

# Global scope-skip (display_order unique). Longer / more specific patterns first where relevant.
_SCOPE: list[tuple[int, str, str, str, str]] = [
    (3403, "other", "contains", "סלסלת עלים גדולה", "M10.4 R2 SRC060 leaf basket retail"),
    (3404, "other", "contains", "סל ליל הסדר", "M10.4 R2 holiday basket"),
    (3405, "other", "contains", "סל השף (M)", "M10.4 R2 chef basket"),
    (3406, "other", "contains", "סל הבית", "M10.4 R2 home basket"),
    (3407, "other", "contains", "סלסלת עלים", "M10.4 R2 leaf basket retail"),
    (3408, "other", "contains", "חובזה", "M10.4 R2 herb retail line"),
    (3409, "other", "contains", "לימונית", "M10.4 R2 herb retail line"),
    (3410, "other", "contains", "פאפאיה", "M10.4 R2 papaya no V1 product"),
    (3411, "other", "contains", "תרומת מזון", "M10.4 R2 SRC070 donation box"),
    (3412, "grocery", "contains", "Yoo Egg", "M10.4 R2 SRC070 processed egg"),
    (3413, "dry_grocery", "contains", "לוז טבעי", "M10.4 R2 SRC070 nuts pack"),
    (3414, "grocery", "contains", "אצבעות פאי תפוחי עץ", "M10.4 R2 SRC070 bakery"),
    (3415, "grocery", "contains", "טורטיות מכוסמת", "M10.4 R2 SRC070 frozen flatbread"),
    (3416, "other", "contains", "מארז הפתעה של ירקות", "M10.4 R2 SRC070 surprise box"),
    (3417, "other", "contains", "מארז ירוקים (יכול להשתנות", "M10.4 R2 SRC070 greens box"),
    (3418, "grocery", "contains", "נקניק סלמי מעושן", "M10.4 R2 SRC070 vegan deli"),
    (3419, "grocery", "contains", "נקניקיות טבעוניות", "M10.4 R2 SRC070 vegan deli"),
    (3420, "grocery", "contains", "פרמז'ן שקדים", "M10.4 R2 SRC070 cheese pack"),
    (3421, "other", "contains", "רשמו לי האם הופרשו תרומות", "M10.4 R2 SRC070 instruction text"),
    (3422, "dry_grocery", "contains", "שקד טבעי ישראלי", "M10.4 R2 SRC070 nuts pack"),
    (3423, "other", "contains", "שקיל! לקט ירקות", "M10.4 R2 SRC070 conditional box"),
    (3424, "other", "contains", "זרעי ליפה", "M10.4 R2 SRC070 seeds pack"),
    (3425, "other", "contains", "זרעים של כובע הנזיר", "M10.4 R2 SRC070 seeds pack"),
    (3426, "other", "contains", "2 ארזו לי כל מוצר בנפרד", "M10.4 R2 SRC070 checkout note"),
]

# Per-source aliases: (source_code, alias_text, product_code)
_ALIASES: list[tuple[str, str, str]] = [
    ("SRC060", "אפונת שלג", "PRD043"),
    ("SRC060", "בוקצוי עלים", "PRD062"),
    ("SRC060", "תפוח עץ גרני סמית", "PRD042"),
    (
        "SRC070",
        'ארטישוק סגול קטנים/בינונים אורגני | כ-1 ק"ג',
        "PRD035",
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    for display_order, cat, mtype, pattern, notes in _SCOPE:
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

    for src_code, alias_text, pcode in _ALIASES:
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
    for display_order, *_ in _SCOPE:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"),
            {"d": display_order},
        )
    for src_code, alias_text, _ in _ALIASES:
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
