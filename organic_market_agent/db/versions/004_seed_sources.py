"""Seed 20 sources, fetch profiles, and one normalizer profile per source."""

from alembic import op
from sqlalchemy import text

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

SOURCES = [
    (
        "SRC001",
        "easyFarm platform",
        "https://www.easyfarm.co.il/",
        "discovery",
        "community",
        "discovery_only",
        "easyfarm",
        "simple_product_grid",
    ),
    (
        "SRC002",
        "סבתא יהודית",
        "https://sapta.easyfarm.co.il/manage/product/price_list/",
        "direct_price",
        "community",
        "community_direct",
        "easyfarm",
        "easyfarm_catalog",
    ),
    (
        "SRC003",
        "ח'ביזה",
        "https://chubeza.easyfarm.co.il/manage/customer/ano_custom_reg/HE/",
        "basket_csa",
        "community",
        "csa_basket",
        "easyfarm",
        "basket_only",
    ),
    (
        "SRC004",
        "קיימא בית זית",
        "https://kaima.easyfarm.co.il/shop/home/",
        "direct_price",
        "community",
        "community_direct",
        "easyfarm",
        "easyfarm_catalog",
    ),
    (
        "SRC005",
        "קיימא חוקוק",
        "https://kaima-hukuk.easyfarm.co.il/shop/",
        "direct_price",
        "community",
        "community_direct",
        "easyfarm",
        "easyfarm_catalog",
    ),
    (
        "SRC006",
        "עץ השדה",
        "https://etzhasade.easyfarm.co.il/shop/",
        "direct_price",
        "community",
        "community_direct",
        "easyfarm",
        "easyfarm_catalog",
    ),
    (
        "SRC007",
        "סלסילה",
        "https://www.salsila.co.il/",
        "basket_csa",
        "community",
        "csa_basket",
        None,
        "basket_only",
    ),
    (
        "SRC008",
        "שדה ירוק",
        "https://www.sadeyarok.co.il/",
        "direct_price",
        "community",
        "community_direct",
        None,
        "simple_product_grid",
    ),
    (
        "SRC009",
        "משק זינגר",
        "https://www.zinger-organic.com/cat/%D7%99%D7%A8%D7%A7%D7%95%D7%AA",
        "direct_price",
        "community",
        "community_direct",
        None,
        "simple_product_grid",
    ),
    (
        "SRC010",
        "Farmerim",
        "https://farmerim.com/organic",
        "direct_price",
        "community",
        "community_direct",
        None,
        "simple_product_grid",
    ),
    (
        "SRC011",
        "האורגני",
        "https://haorgani.co.il/",
        "direct_price",
        "community",
        "community_direct",
        None,
        "simple_product_grid",
    ),
    (
        "SRC012",
        "בידיים - מעגל העסקים",
        "https://www.bayadaim.org.il/",
        "discovery",
        "community",
        "discovery_only",
        None,
        "simple_product_grid",
    ),
    (
        "SRC013",
        "פרמקלצ'ר ישראל",
        "https://www.permaculture.org.il/",
        "discovery",
        "community",
        "discovery_only",
        None,
        "simple_product_grid",
    ),
    (
        "SRC014",
        "תנועת החוות הירוקות",
        "https://next.obudget.org/i/org/association/580652170",
        "discovery",
        "community",
        "discovery_only",
        None,
        "simple_product_grid",
    ),
    (
        "SRC015",
        "מחירי תוצרת הארץ - משרד החקלאות",
        "https://prices.moag.gov.il",
        "benchmark",
        "benchmark",
        "retail_chain_benchmark",
        None,
        "official_wholesale",
    ),
    (
        "SRC016",
        "דוחות שבועיים - משרד החקלאות",
        "https://www.gov.il/he/departments/dynamiccollectors/weekly-prices?skip=0&year=9",
        "benchmark",
        "benchmark",
        "retail_chain_benchmark",
        None,
        "official_wholesale",
    ),
    (
        "SRC017",
        "Pricez",
        "https://www.pricez.co.il/",
        "benchmark",
        "benchmark",
        "retail_chain_benchmark",
        None,
        "retail_benchmark",
    ),
    (
        "SRC018",
        "CHP",
        "https://chp.co.il/",
        "benchmark",
        "benchmark",
        "retail_chain_benchmark",
        None,
        "retail_benchmark",
    ),
    (
        "SRC019",
        "סקאל ישראל",
        "https://www.secal.co.il/",
        "verification",
        "verification",
        "verification_only",
        None,
        "retail_benchmark",
    ),
    (
        "SRC020",
        "IQC",
        "https://www.iqc.co.il/",
        "verification",
        "verification",
        "verification_only",
        None,
        "retail_benchmark",
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    for row in SOURCES:
        code, name, url, sgroup, mscope, schannel, platform, norm_type = row
        conn.execute(
            text(
                """
                INSERT INTO sources (
                    code, name, base_url, source_group, market_scope, sales_channel,
                    status, priority, legal_review_required, is_active
                ) VALUES (
                    :code, :name, :url, :sgroup, :mscope, :schannel,
                    'active', 5, false, true
                )
                """
            ),
            {
                "code": code,
                "name": name,
                "url": url,
                "sgroup": sgroup,
                "mscope": mscope,
                "schannel": schannel,
            },
        )
        pf_sql = (
            "INSERT INTO source_fetch_profiles ("
            "source_id, platform_family, fetch_mode, entry_url, http_method, is_active"
            ") SELECT id, :platform, 'html_page', base_url, 'GET', true "
            "FROM sources WHERE code = :code"
        )
        conn.execute(
            text(pf_sql),
            {"code": code, "platform": platform},
        )
        np_sql = (
            "INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active) "
            "SELECT id, :ntype, '1.0', true FROM sources WHERE code = :code"
        )
        conn.execute(
            text(np_sql),
            {"code": code, "ntype": norm_type},
        )


def downgrade() -> None:
    op.execute("DELETE FROM normalizer_profiles")
    op.execute("DELETE FROM source_fetch_profiles")
    op.execute("DELETE FROM sources")
