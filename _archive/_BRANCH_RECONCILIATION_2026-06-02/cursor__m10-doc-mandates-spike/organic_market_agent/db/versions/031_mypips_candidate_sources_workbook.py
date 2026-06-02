"""031: Seed inactive MyPIPS candidate sources from onboarding workbook CSV."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None

_MYPIPS_SEED_NOTES = "mypips_candidate_031"


def _workbook_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "mypips_source_onboarding_workbook.csv"


def upgrade() -> None:
    path = _workbook_path()
    if not path.is_file():
        return
    conn = op.get_bind()
    existing = conn.execute(
        text("SELECT COUNT(*)::int FROM sources WHERE notes = :n"), {"n": _MYPIPS_SEED_NOTES}
    )
    if existing.scalar_one() > 0:
        return

    max_id = conn.execute(text("SELECT COALESCE(MAX(id), 1) FROM sources")).scalar_one()
    conn.execute(
        text("SELECT setval(pg_get_serial_sequence('sources', 'id'), :m, true)"),
        {"m": int(max_id)},
    )

    codes = conn.execute(text("SELECT code FROM sources")).scalars().all()
    pat = re.compile(r"^SRC(\d+)$")
    nums = [int(m.group(1)) for c in codes if (m := pat.match(c))]
    code_num = max(nums, default=0) + 1

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = (row.get("slug") or "").strip()
            if not slug:
                continue
            code = f"SRC{code_num:03d}"
            code_num += 1
            name = (row.get("display_name") or slug).strip()[:100]
            store_url = (row.get("store_url") or "").strip()
            products_url = (row.get("products_url") or "").strip()
            if not store_url:
                store_url = f"https://mypips.app/{slug}"
            if not products_url:
                products_url = f"https://mypips.app/{slug}/products"

            conn.execute(
                text(
                    """
                    INSERT INTO sources (
                        code, name, base_url, source_group, market_scope, sales_channel,
                        status, priority, legal_review_required, is_active, notes,
                        source_tier, display_bucket
                    ) VALUES (
                        :code, :name, :url, 'direct_price', 'community', 'community_direct',
                        'candidate', 5, false, false, :notes, 'discovery', 'grower'
                    )
                    """
                ),
                {"code": code, "name": name, "url": store_url, "notes": _MYPIPS_SEED_NOTES},
            )
            conn.execute(
                text(
                    """
                    INSERT INTO source_fetch_profiles (
                        source_id, platform_family, fetch_mode, entry_url, http_method, is_active
                    )
                    SELECT id, NULL, 'html_page', :entry, 'GET', false
                    FROM sources WHERE code = :code
                    """
                ),
                {"code": code, "entry": products_url},
            )
            conn.execute(
                text(
                    """
                    INSERT INTO normalizer_profiles (
                        source_id, normalizer_type, version, is_active, notes
                    )
                    SELECT id, 'simple_product_grid', '1.0', false, :nnote
                    FROM sources WHERE code = :code
                    """
                ),
                {
                    "code": code,
                    "nnote": "Placeholder until MyPIPS parser; keep inactive.",
                },
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            "DELETE FROM normalizer_profiles WHERE source_id IN "
            "(SELECT id FROM sources WHERE notes = :n)"
        ),
        {"n": _MYPIPS_SEED_NOTES},
    )
    conn.execute(
        text(
            "DELETE FROM source_fetch_profiles WHERE source_id IN "
            "(SELECT id FROM sources WHERE notes = :n)"
        ),
        {"n": _MYPIPS_SEED_NOTES},
    )
    conn.execute(text("DELETE FROM sources WHERE notes = :n"), {"n": _MYPIPS_SEED_NOTES})
