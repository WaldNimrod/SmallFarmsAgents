"""032: CQ-P01 — catalog_scope_skip_rules + product_aliases (ARCH §3.1–3.2 templates).

A2 triage rows: populate SCOPE_SKIP_RULES, GLOBAL_ALIASES, SCOPED_ALIASES when Team 10
files an H1 with display_order band and tuples. Empty lists = no-op upgrade (chain only).

Renumbered from branch migration 072 (cursor/m10-doc-mandates-spike@bb981ed).
down_revision updated to point to main's 031 (deactivate_src017_pricez).
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None

# (display_order, category_code, pattern, match_type, notes)
SCOPE_SKIP_RULES: list[tuple[int, str, str, str, str]] = []

# (product_code, alias_text, confidence str e.g. "0.9")
GLOBAL_ALIASES: list[tuple[str, str, str]] = []

# (product_code, source_code, alias_text, confidence)
SCOPED_ALIASES: list[tuple[str, str, str, str]] = []


def _insert_scope_skip(conn, row: tuple[int, str, str, str, str]) -> None:
    display_order, category_code, pattern, match_type, notes = row
    conn.execute(
        text(
            """
            INSERT INTO catalog_scope_skip_rules
              (display_order, category_code, pattern, match_type, is_active, notes, created_at, updated_at)
            VALUES
              (:display_order, :category_code, :pattern, :match_type, true, :notes, now(), now())
            ON CONFLICT (display_order) DO NOTHING
            """
        ),
        {
            "display_order": display_order,
            "category_code": category_code,
            "pattern": pattern,
            "match_type": match_type,
            "notes": notes,
        },
    )


def _insert_global_alias(conn, product_code: str, alias_text: str, confidence: str) -> None:
    conn.execute(
        text(
            """
            INSERT INTO product_aliases
              (alias_text, alias_text_normalized, product_id, source_id,
               is_active, confidence, created_at)
            SELECT
              :alias_text,
              lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
              p.id, NULL, true, CAST(:confidence AS NUMERIC(3,2)), now()
            FROM products p
            WHERE p.code = :product_code
            ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
            """
        ),
        {
            "alias_text": alias_text,
            "confidence": confidence,
            "product_code": product_code,
        },
    )


def _insert_scoped_alias(
    conn, product_code: str, source_code: str, alias_text: str, confidence: str
) -> None:
    conn.execute(
        text(
            """
            INSERT INTO product_aliases
              (alias_text, alias_text_normalized, product_id, source_id,
               is_active, confidence, created_at)
            SELECT
              :alias_text,
              lower(regexp_replace(:alias_text, '\\s+', ' ', 'g')),
              p.id, s.id, true, CAST(:confidence AS NUMERIC(3,2)), now()
            FROM products p, sources s
            WHERE p.code = :product_code AND s.code = :source_code
            ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
            """
        ),
        {
            "alias_text": alias_text,
            "confidence": confidence,
            "product_code": product_code,
            "source_code": source_code,
        },
    )


def upgrade() -> None:
    conn = op.get_bind()
    for row in SCOPE_SKIP_RULES:
        _insert_scope_skip(conn, row)
    for pcode, alias_text, conf in GLOBAL_ALIASES:
        _insert_global_alias(conn, pcode, alias_text, conf)
    for pcode, scode, alias_text, conf in SCOPED_ALIASES:
        _insert_scoped_alias(conn, pcode, scode, alias_text, conf)


def downgrade() -> None:
    """No-op when upgrade inserted nothing; Team 10 may request targeted deletes if rows exist."""
    pass
