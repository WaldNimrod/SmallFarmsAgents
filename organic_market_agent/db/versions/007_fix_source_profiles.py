"""007: Fix source profiles — normalizer_type alignment + selector overrides."""

from alembic import op
from sqlalchemy import text
import json

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


# Updated selector profiles for EasyFarm sources based on live DOM inspection.
# These are broader selectors that catch more product rows.
EASYFARM_SELECTOR = {
    "product_row": (
        "div.product-item, li.product, tr.product-row, "
        "div[class*='product'], li[class*='product'], "
        "div.shop-item, div.item"
    ),
    "name": (
        ".product-name, .item-title, h3, h4, "
        ".product-title, [class*='name'], [class*='title']"
    ),
    "price": (
        ".product-price, .price, .item-price, "
        "[class*='price'], span[class*='cost']"
    ),
    "unit": (
        ".product-unit, .unit, .item-unit, "
        "[class*='unit'], [class*='weight']"
    ),
    "quantity": None,
}


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Fix SRC018–SRC020: normalizer_type html → simple_product_grid
    for src_code in ("SRC018", "SRC019", "SRC020"):
        conn.execute(
            text(
                "UPDATE normalizer_profiles SET normalizer_type = 'simple_product_grid' "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )

    # 2. Deactivate SRC015, SRC016 (HTTP 403 — no working endpoint confirmed)
    for src_code in ("SRC015", "SRC016"):
        conn.execute(
            text(
                "UPDATE sources SET status = 'candidate', is_active = false "
                "WHERE code = :code"
            ),
            {"code": src_code},
        )
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET is_active = false "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )

    # 3. Update EasyFarm selector profiles (SRC002, SRC004, SRC005, SRC006)
    selector_json = json.dumps(EASYFARM_SELECTOR)
    for src_code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            text(
                "UPDATE source_fetch_profiles "
                "SET selector_profile = CAST(:sel AS jsonb) "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"sel": selector_json, "code": src_code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for src_code in ("SRC018", "SRC019", "SRC020"):
        conn.execute(
            text(
                "UPDATE normalizer_profiles SET normalizer_type = 'retail_benchmark' "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
    for src_code in ("SRC015", "SRC016"):
        conn.execute(
            text(
                "UPDATE sources SET status = 'active', is_active = true "
                "WHERE code = :code"
            ),
            {"code": src_code},
        )
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET is_active = true "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
    for src_code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET selector_profile = NULL "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
