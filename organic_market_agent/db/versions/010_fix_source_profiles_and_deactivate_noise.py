"""010: Fix EasyFarm selector_profile and entry_url; deactivate noise sources."""

import json

import sqlalchemy as sa
from alembic import op

revision = "010"
down_revision = "008"
branch_labels = None
depends_on = None

# Correct selector that matches the actual EasyFarm price-list DOM
# (verified by inspecting stored SRC002 HTML: div.prod_row structure)
CORRECT_SELECTOR = {
    "product_row": "div.prod_row",
    "name": ".form-prod-title",
    "price": ".price",
    "unit": None,
    "quantity": None,
}

# EasyFarm price-list URLs — flat server-rendered HTML, no JS required
EASYFARM_PRICE_LIST_URLS = {
    "SRC004": "https://kaima.easyfarm.co.il/manage/product/price_list/",
    "SRC005": "https://kaima-hukuk.easyfarm.co.il/manage/product/price_list/",
    "SRC006": "https://etzhasade.easyfarm.co.il/manage/product/price_list/",
}

# Sources that cannot contribute clean normalized data — deactivate
DEACTIVATE_CODES = [
    "SRC001",  # easyFarm portal — discovery site, was generating phantom normalized rows
    "SRC008",  # שדה ירוק — JS-rendered shop, static HTML has no product data
    "SRC009",  # משק זינגר — same JS-rendering issue as SRC008
    "SRC010",  # Farmerim — only 1 row extracted (a delivery-fee notice, not a product)
    "SRC011",  # האורגני — login-required membership site, no public price page
    "SRC012",  # בידיים — business directory portal, not a price source
    "SRC013",  # פרמקלצ'ר ישראל — permaculture portal, 663 garbage rows in DB
    "SRC014",  # תנועת החוות הירוקות — NGO portal, no prices
    "SRC019",  # סקאל ישראל — quality verification body, not a price source
    "SRC020",  # IQC — quality certification body, not a price source
]


def upgrade() -> None:
    conn = op.get_bind()
    selector_json = json.dumps(CORRECT_SELECTOR)

    # 1. Update selector_profile for all 4 EasyFarm price-list sources
    for code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles "
                "SET selector_profile = CAST(:sel AS jsonb) "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"sel": selector_json, "code": code},
        )

    # 2. Fix entry_url (and base_url) for SRC004–006 to the price-list endpoint
    for code, new_url in EASYFARM_PRICE_LIST_URLS.items():
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles "
                "SET entry_url = :url "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"url": new_url, "code": code},
        )
        conn.execute(
            sa.text(
                "UPDATE sources SET base_url = :url WHERE code = :code"
            ),
            {"url": new_url, "code": code},
        )

    # 3. Deactivate noisy / broken sources
    for code in DEACTIVATE_CODES:
        conn.execute(
            sa.text(
                "UPDATE sources SET is_active = false WHERE code = :code"
            ),
            {"code": code},
        )
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles SET is_active = false "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": code},
        )


def downgrade() -> None:
    conn = op.get_bind()

    # Restore old generic selector for EasyFarm sources
    old_selector = json.dumps(
        {
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
    )
    for code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles "
                "SET selector_profile = CAST(:sel AS jsonb) "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"sel": old_selector, "code": code},
        )

    # Restore original entry_url / base_url for SRC004–006
    old_urls = {
        "SRC004": "https://kaima.easyfarm.co.il/shop/home/",
        "SRC005": "https://kaima-hukuk.easyfarm.co.il/shop/",
        "SRC006": "https://etzhasade.easyfarm.co.il/shop/",
    }
    for code, old_url in old_urls.items():
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles SET entry_url = :url "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"url": old_url, "code": code},
        )
        conn.execute(
            sa.text("UPDATE sources SET base_url = :url WHERE code = :code"),
            {"url": old_url, "code": code},
        )

    # Re-activate all sources that were deactivated
    for code in DEACTIVATE_CODES:
        conn.execute(
            sa.text("UPDATE sources SET is_active = true WHERE code = :code"),
            {"code": code},
        )
        conn.execute(
            sa.text(
                "UPDATE source_fetch_profiles SET is_active = true "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": code},
        )
