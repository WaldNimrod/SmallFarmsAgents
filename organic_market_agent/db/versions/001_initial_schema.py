"""001_initial_schema: 23 tables, indexes, deferred FK, 2 views."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "measurement_units",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("code", sa.VARCHAR(30), nullable=False),
        sa.Column("name_he", sa.VARCHAR(60), nullable=False),
        sa.Column("unit_type", sa.VARCHAR(20), nullable=False),
        sa.Column("is_normalizable", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "unit_type IN ('weight','count','bundle','basket','pack')",
            name="chk_mu_unit_type",
        ),
    )
    op.create_index("idx_measurement_units_code", "measurement_units", ["code"], unique=True)

    op.create_table(
        "sources",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("code", sa.VARCHAR(10), nullable=False),
        sa.Column("name", sa.VARCHAR(100), nullable=False),
        sa.Column("base_url", sa.VARCHAR(500), nullable=True),
        sa.Column("source_group", sa.VARCHAR(30), nullable=False),
        sa.Column("market_scope", sa.VARCHAR(20), nullable=False),
        sa.Column("sales_channel", sa.VARCHAR(30), nullable=False),
        sa.Column("status", sa.VARCHAR(20), nullable=False, server_default="candidate"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("legal_review_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("legal_review_notes", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "source_group IN ('direct_price','basket_csa','discovery','benchmark','verification')",
            name="chk_src_source_group",
        ),
        sa.CheckConstraint(
            "market_scope IN ('community','benchmark','verification')",
            name="chk_src_market_scope",
        ),
        sa.CheckConstraint(
            "sales_channel IN ("
            "'community_direct','csa_basket','farm_shop','farmers_market',"
            "'retail_chain_benchmark','discovery_only','verification_only')",
            name="chk_src_sales_channel",
        ),
        sa.CheckConstraint(
            "status IN ('active','candidate','deprecated','discovery_only')",
            name="chk_src_status",
        ),
        sa.CheckConstraint("priority BETWEEN 1 AND 10", name="chk_src_priority"),
    )
    op.create_index("idx_sources_market_scope", "sources", ["market_scope"])
    op.create_index("idx_sources_status", "sources", ["status"])
    op.create_index("idx_sources_active", "sources", ["is_active"])
    op.create_index("uq_sources_code", "sources", ["code"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("code", sa.VARCHAR(20), nullable=False),
        sa.Column("canonical_name_he", sa.VARCHAR(100), nullable=False),
        sa.Column("category", sa.VARCHAR(40), nullable=False),
        sa.Column("default_measurement_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("is_organic_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_basket_product", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("seasonality_notes", sa.VARCHAR(100), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "category IN ("
            "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
            "'alliums','cucurbits','legumes_fresh','baskets')",
            name="chk_p_category",
        ),
        sa.ForeignKeyConstraint(["default_measurement_unit_id"], ["measurement_units.id"]),
    )
    op.create_index("idx_products_category", "products", ["category"])
    op.create_index("idx_products_active", "products", ["is_active"])
    op.create_index("idx_products_code", "products", ["code"], unique=True)

    op.create_table(
        "product_variants",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("variant_name", sa.VARCHAR(100), nullable=False),
        sa.Column("quantity_value", sa.Numeric(10, 3), nullable=True),
        sa.Column("quantity_unit_id", sa.BigInteger(), nullable=True),
        sa.Column("normalized_base_unit_id", sa.BigInteger(), nullable=True),
        sa.Column("normalized_factor", sa.Numeric(12, 6), nullable=True),
        sa.Column("is_composite", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["quantity_unit_id"], ["measurement_units.id"]),
        sa.ForeignKeyConstraint(["normalized_base_unit_id"], ["measurement_units.id"]),
    )
    op.create_index("idx_product_variants_product", "product_variants", ["product_id"])

    op.create_table(
        "product_merges",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_product_id", sa.BigInteger(), nullable=False),
        sa.Column("target_product_id", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("merged_by", sa.VARCHAR(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["target_product_id"], ["products.id"]),
        sa.CheckConstraint("source_product_id != target_product_id", name="chk_pm_no_self_merge"),
        sa.UniqueConstraint("source_product_id", name="uq_product_merge"),
    )
    op.create_index("idx_product_merges_source", "product_merges", ["source_product_id"])
    op.create_index("idx_product_merges_target", "product_merges", ["target_product_id"])

    op.create_table(
        "source_fetch_profiles",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("platform_family", sa.VARCHAR(30), nullable=True),
        sa.Column("fetch_mode", sa.VARCHAR(20), nullable=False),
        sa.Column("entry_url", sa.VARCHAR(500), nullable=False),
        sa.Column("http_method", sa.VARCHAR(10), nullable=False, server_default="GET"),
        sa.Column("request_headers_json", postgresql.JSONB(), nullable=True),
        sa.Column("schedule_kind", sa.VARCHAR(20), nullable=False, server_default="daily"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column(
            "retry_policy_json",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{\"max_retries\": 2, \"backoff_seconds\": 60}'::jsonb"),
        ),
        sa.Column("is_public_access", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("charset_hint", sa.VARCHAR(20), nullable=True),
        sa.Column("selector_profile", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.CheckConstraint(
            "fetch_mode IN ('html_page','json_endpoint','pdf_download','rss','directory_page')",
            name="chk_sfp_fetch_mode",
        ),
        sa.CheckConstraint(
            "schedule_kind IN ('daily','weekly','manual_check')",
            name="chk_sfp_schedule_kind",
        ),
    )
    op.create_index("idx_fetch_profiles_source", "source_fetch_profiles", ["source_id"])
    op.create_index("idx_fetch_profiles_platform", "source_fetch_profiles", ["platform_family"])

    op.create_table(
        "normalizer_profiles",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("normalizer_type", sa.VARCHAR(40), nullable=False),
        sa.Column("version", sa.VARCHAR(20), nullable=False, server_default="1.0"),
        sa.Column("config_json", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.CheckConstraint(
            "normalizer_type IN ("
            "'easyfarm_catalog','simple_product_grid','basket_only',"
            "'retail_benchmark','official_wholesale')",
            name="chk_np_normalizer_type",
        ),
    )
    op.create_index("idx_normalizer_profiles_source", "normalizer_profiles", ["source_id"])

    op.create_table(
        "product_aliases",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("alias_text", sa.VARCHAR(200), nullable=False),
        sa.Column("alias_text_normalized", sa.VARCHAR(200), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column("normalizer_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["normalizer_profile_id"], ["normalizer_profiles.id"]),
        sa.UniqueConstraint("alias_text_normalized", "source_id", name="uq_alias_text_source"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="chk_pa_confidence"),
    )
    op.create_index("idx_product_aliases_product", "product_aliases", ["product_id"])
    op.create_index("idx_product_aliases_text", "product_aliases", ["alias_text_normalized"])
    op.create_index("idx_product_aliases_source", "product_aliases", ["source_id"])

    op.create_table(
        "normalizer_rules",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("normalizer_profile_id", sa.BigInteger(), nullable=False),
        sa.Column("rule_kind", sa.VARCHAR(30), nullable=False),
        sa.Column("match_pattern", sa.VARCHAR(500), nullable=False),
        sa.Column("match_type", sa.VARCHAR(10), nullable=False, server_default="exact"),
        sa.Column("replacement_value", sa.VARCHAR(500), nullable=True),
        sa.Column("extra_params_json", postgresql.JSONB(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.VARCHAR(100), nullable=False, server_default="system"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["normalizer_profile_id"], ["normalizer_profiles.id"]),
        sa.CheckConstraint(
            "rule_kind IN ("
            "'product_alias','unit_map','quantity_parse','organic_flag',"
            "'ignore_pattern','benchmark_tag','basket_parse','price_correction')",
            name="chk_nr_rule_kind",
        ),
        sa.CheckConstraint(
            "match_type IN ('exact','regex','contains','prefix')",
            name="chk_nr_match_type",
        ),
    )
    op.create_index("idx_normalizer_rules_profile", "normalizer_rules", ["normalizer_profile_id"])
    op.create_index("idx_normalizer_rules_kind", "normalizer_rules", ["rule_kind"])
    op.create_index(
        "idx_normalizer_rules_priority",
        "normalizer_rules",
        ["normalizer_profile_id", "priority"],
    )

    op.create_table(
        "unit_conversions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("from_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("to_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("factor", sa.Numeric(12, 6), nullable=False),
        sa.Column("conversion_type", sa.VARCHAR(20), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["from_unit_id"], ["measurement_units.id"]),
        sa.ForeignKeyConstraint(["to_unit_id"], ["measurement_units.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.UniqueConstraint("from_unit_id", "to_unit_id", "product_id", name="uq_unit_conversion"),
        sa.CheckConstraint(
            "conversion_type IN ('exact','heuristic','product_specific')",
            name="chk_uc_conversion_type",
        ),
    )
    op.create_index("idx_unit_conversions_from", "unit_conversions", ["from_unit_id"])
    op.create_index("idx_unit_conversions_product", "unit_conversions", ["product_id"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("run_type", sa.VARCHAR(20), nullable=False, server_default="daily"),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.VARCHAR(20), nullable=False, server_default="running"),
        sa.Column("sources_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sources_succeeded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sources_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("community_sources_succeeded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("triggered_by", sa.VARCHAR(100), nullable=False, server_default="cron"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("run_type IN ('daily','manual','retry')", name="chk_ir_run_type"),
        sa.CheckConstraint(
            "status IN ('running','completed','partial','failed')",
            name="chk_ir_status",
        ),
    )
    op.create_index("idx_ingestion_runs_status", "ingestion_runs", ["status"])
    op.create_index("idx_ingestion_runs_started", "ingestion_runs", ["started_at"])

    op.create_table(
        "source_fetch_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("ingestion_run_id", sa.BigInteger(), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("fetch_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.VARCHAR(20), nullable=False, server_default="running"),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("bytes_fetched", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_asset_id", sa.BigInteger(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["fetch_profile_id"], ["source_fetch_profiles.id"]),
        sa.CheckConstraint(
            "status IN ('running','success','failed','skipped','timeout')",
            name="chk_sfr_status",
        ),
    )
    op.create_index("idx_sfr_ingestion_run", "source_fetch_runs", ["ingestion_run_id"])
    op.create_index("idx_sfr_source", "source_fetch_runs", ["source_id"])
    op.create_index("idx_sfr_status", "source_fetch_runs", ["status"])

    op.create_table(
        "raw_assets",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("source_fetch_run_id", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.VARCHAR(500), nullable=False),
        sa.Column("file_type", sa.VARCHAR(20), nullable=False),
        sa.Column("checksum_sha256", sa.CHAR(64), nullable=False),
        sa.Column("bytes_size", sa.Integer(), nullable=False),
        sa.Column("captured_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["source_fetch_run_id"], ["source_fetch_runs.id"]),
        sa.CheckConstraint(
            "file_type IN ('html','json','pdf','rss','text','other')",
            name="chk_ra_file_type",
        ),
    )
    op.create_index("idx_raw_assets_source", "raw_assets", ["source_id"])
    op.create_index("idx_raw_assets_captured", "raw_assets", ["captured_at"])
    op.create_index("idx_raw_assets_checksum", "raw_assets", ["checksum_sha256"])

    op.create_foreign_key(
        "fk_sfr_raw_asset",
        "source_fetch_runs",
        "raw_assets",
        ["raw_asset_id"],
        ["id"],
    )

    op.create_table(
        "raw_extracted_items",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_fetch_run_id", sa.BigInteger(), nullable=False),
        sa.Column("raw_asset_id", sa.BigInteger(), nullable=False),
        sa.Column("normalizer_profile_id", sa.BigInteger(), nullable=True),
        sa.Column("raw_product_name", sa.VARCHAR(300), nullable=True),
        sa.Column("raw_price_text", sa.VARCHAR(100), nullable=True),
        sa.Column("raw_unit_text", sa.VARCHAR(100), nullable=True),
        sa.Column("raw_quantity_text", sa.VARCHAR(100), nullable=True),
        sa.Column("raw_payload_json", postgresql.JSONB(), nullable=True),
        sa.Column("extraction_status", sa.VARCHAR(20), nullable=False, server_default="extracted"),
        sa.Column("unresolvable_reason", sa.VARCHAR(200), nullable=True),
        sa.Column("extracted_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_fetch_run_id"], ["source_fetch_runs.id"]),
        sa.ForeignKeyConstraint(["raw_asset_id"], ["raw_assets.id"]),
        sa.ForeignKeyConstraint(["normalizer_profile_id"], ["normalizer_profiles.id"]),
        sa.CheckConstraint(
            "extraction_status IN ('extracted','normalized','unresolvable','ignored')",
            name="chk_rei_extraction_status",
        ),
    )
    op.create_index("idx_rei_fetch_run", "raw_extracted_items", ["source_fetch_run_id"])
    op.create_index("idx_rei_status", "raw_extracted_items", ["extraction_status"])

    op.create_table(
        "normalized_observations",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("source_fetch_run_id", sa.BigInteger(), nullable=False),
        sa.Column("raw_extracted_item_id", sa.BigInteger(), nullable=True),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("product_variant_id", sa.BigInteger(), nullable=True),
        sa.Column("market_scope", sa.VARCHAR(20), nullable=False),
        sa.Column("sales_channel", sa.VARCHAR(30), nullable=False),
        sa.Column("is_benchmark", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_basket_product", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_organic_claimed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("price_amount", sa.Numeric(12, 4), nullable=False),
        sa.Column("currency_code", sa.CHAR(3), nullable=False, server_default="ILS"),
        sa.Column("display_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("normalized_price_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("normalized_unit_id", sa.BigInteger(), nullable=True),
        sa.Column("normalization_method", sa.VARCHAR(30), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, server_default="1.0"),
        sa.Column("flag_status", sa.VARCHAR(20), nullable=False, server_default="ok"),
        sa.Column("flag_reason", sa.VARCHAR(200), nullable=True),
        sa.Column("observed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["source_fetch_run_id"], ["source_fetch_runs.id"]),
        sa.ForeignKeyConstraint(["raw_extracted_item_id"], ["raw_extracted_items.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["product_variant_id"], ["product_variants.id"]),
        sa.ForeignKeyConstraint(["display_unit_id"], ["measurement_units.id"]),
        sa.ForeignKeyConstraint(["normalized_unit_id"], ["measurement_units.id"]),
        sa.CheckConstraint(
            "market_scope IN ('community','benchmark','verification')",
            name="chk_no_market_scope",
        ),
        sa.CheckConstraint(
            "sales_channel IN ("
            "'community_direct','csa_basket','farm_shop','farmers_market',"
            "'retail_chain_benchmark','discovery_only','verification_only')",
            name="chk_no_sales_channel",
        ),
        sa.CheckConstraint(
            "normalization_method IS NULL OR normalization_method IN ("
            "'direct','unit_conversion_exact','unit_conversion_heuristic',"
            "'basket_composite','unresolvable')",
            name="chk_no_norm_method",
        ),
        sa.CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="chk_no_confidence",
        ),
        sa.CheckConstraint(
            "flag_status IN ('ok','review','ignored','hidden')",
            name="chk_no_flag_status",
        ),
    )
    op.create_index("idx_obs_product", "normalized_observations", ["product_id"])
    op.create_index("idx_obs_source", "normalized_observations", ["source_id"])
    op.create_index("idx_obs_observed_at", "normalized_observations", ["observed_at"])
    op.create_index("idx_obs_market_scope", "normalized_observations", ["market_scope"])
    op.create_index("idx_obs_flag_status", "normalized_observations", ["flag_status"])
    op.create_index("idx_obs_benchmark", "normalized_observations", ["is_benchmark"])
    op.create_index(
        "idx_obs_agg",
        "normalized_observations",
        ["product_id", "market_scope", "is_benchmark", "flag_status", "observed_at"],
    )

    op.create_table(
        "observation_flags",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("observation_id", sa.BigInteger(), nullable=True),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("flag_type", sa.VARCHAR(20), nullable=False),
        sa.Column("scope", sa.VARCHAR(20), nullable=False, server_default="single"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.VARCHAR(100), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["observation_id"], ["normalized_observations.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.CheckConstraint(
            "flag_type IN ('hide','review','price_outlier','wrong_product')",
            name="chk_of_flag_type",
        ),
        sa.CheckConstraint(
            "scope IN ('single','source_product','all_from_source')",
            name="chk_of_scope",
        ),
    )
    op.create_index("idx_obs_flags_observation", "observation_flags", ["observation_id"])
    op.create_index("idx_obs_flags_source", "observation_flags", ["source_id"])
    op.create_index("idx_obs_flags_active", "observation_flags", ["is_active"])

    op.create_table(
        "daily_aggregates",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("aggregate_date", sa.Date(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("market_scope", sa.VARCHAR(20), nullable=False),
        sa.Column("sales_channel", sa.VARCHAR(30), nullable=True),
        sa.Column("is_basket_aggregate", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("distinct_sources", sa.Integer(), nullable=False),
        sa.Column("min_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("max_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("unweighted_avg_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("weighted_avg_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("median_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("stddev_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("normalized_unit_id", sa.BigInteger(), nullable=True),
        sa.Column("meets_publish_threshold", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_observed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["normalized_unit_id"], ["measurement_units.id"]),
        sa.UniqueConstraint(
            "aggregate_date",
            "product_id",
            "market_scope",
            "sales_channel",
            name="uq_daily_aggregate",
        ),
        sa.CheckConstraint(
            "market_scope IN ('community','benchmark')",
            name="chk_da_market_scope",
        ),
    )
    op.create_index("idx_daily_agg_date", "daily_aggregates", ["aggregate_date"])
    op.create_index("idx_daily_agg_product", "daily_aggregates", ["product_id"])
    op.create_index(
        "idx_daily_agg_publish",
        "daily_aggregates",
        ["meets_publish_threshold", "aggregate_date"],
    )

    op.create_table(
        "weekly_snapshots",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("week_end_date", sa.Date(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("market_scope", sa.VARCHAR(20), nullable=False),
        sa.Column("sales_channel", sa.VARCHAR(30), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("distinct_sources", sa.Integer(), nullable=False),
        sa.Column("data_completeness_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("week_avg_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_weighted_avg_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_median_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_stddev_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_min_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_max_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("normalized_unit_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "snapshot_created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["normalized_unit_id"], ["measurement_units.id"]),
        sa.UniqueConstraint(
            "week_start_date",
            "product_id",
            "market_scope",
            "sales_channel",
            name="uq_weekly_snapshot",
        ),
    )
    op.create_index("idx_weekly_snap_product", "weekly_snapshots", ["product_id"])
    op.create_index("idx_weekly_snap_week", "weekly_snapshots", ["week_start_date"])

    op.create_table(
        "publish_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("ingestion_run_id", sa.BigInteger(), nullable=True),
        sa.Column("run_type", sa.VARCHAR(20), nullable=False, server_default="auto"),
        sa.Column("build_started_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("build_finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("upload_started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("upload_finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.VARCHAR(20), nullable=False, server_default="building"),
        sa.Column("artifact_version", sa.VARCHAR(40), nullable=True),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_last_good", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("products_included", sa.Integer(), nullable=True),
        sa.Column("community_products", sa.Integer(), nullable=True),
        sa.Column("benchmark_products", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("triggered_by", sa.VARCHAR(100), nullable=False, server_default="auto"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"]),
        sa.CheckConstraint("run_type IN ('auto','manual','retry')", name="chk_pr_run_type"),
        sa.CheckConstraint(
            "status IN ("
            "'building','build_failed','uploading','upload_failed',"
            "'published','aborted')",
            name="chk_pr_status",
        ),
    )
    op.create_index("idx_publish_runs_status", "publish_runs", ["status"])
    op.create_index("idx_publish_runs_last_good", "publish_runs", ["is_last_good"])
    op.create_index("idx_publish_runs_published", "publish_runs", ["published_at"])

    op.create_table(
        "publish_artifacts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("publish_run_id", sa.BigInteger(), nullable=False),
        sa.Column("artifact_type", sa.VARCHAR(20), nullable=False),
        sa.Column("local_path", sa.VARCHAR(500), nullable=False),
        sa.Column("checksum_sha256", sa.CHAR(64), nullable=False),
        sa.Column("bytes_size", sa.Integer(), nullable=False),
        sa.Column("remote_path", sa.VARCHAR(500), nullable=True),
        sa.Column("upload_status", sa.VARCHAR(20), nullable=True, server_default="pending"),
        sa.Column("uploaded_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["publish_run_id"], ["publish_runs.id"]),
        sa.CheckConstraint(
            "artifact_type IN ("
            "'public_json','public_html','manifest_json','manifest_last_good_json')",
            name="chk_pa_artifact_type",
        ),
        sa.CheckConstraint(
            "upload_status IS NULL OR upload_status IN ('pending','uploaded','failed','skipped')",
            name="chk_pa_upload_status",
        ),
    )
    op.create_index("idx_publish_artifacts_run", "publish_artifacts", ["publish_run_id"])
    op.create_index("idx_publish_artifacts_type", "publish_artifacts", ["artifact_type"])

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("email", sa.VARCHAR(200), nullable=False),
        sa.Column("password_hash", sa.VARCHAR(255), nullable=False),
        sa.Column("display_name", sa.VARCHAR(100), nullable=True),
        sa.Column("role", sa.VARCHAR(20), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('admin','viewer')", name="chk_u_role"),
    )
    op.create_index("uq_users_email", "users", ["email"], unique=True)

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("actor_name", sa.VARCHAR(100), nullable=False, server_default="system"),
        sa.Column("action", sa.VARCHAR(100), nullable=False),
        sa.Column("entity_type", sa.VARCHAR(50), nullable=True),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("before_state", postgresql.JSONB(), nullable=True),
        sa.Column("after_state", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.VARCHAR(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("idx_audit_log_actor", "audit_log", ["actor_name"])
    op.create_index("idx_audit_log_entity", "audit_log", ["entity_type", "entity_id"])
    op.create_index("idx_audit_log_created", "audit_log", ["created_at"])

    op.create_table(
        "log_entries",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("level", sa.VARCHAR(10), nullable=False),
        sa.Column("module", sa.VARCHAR(60), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.VARCHAR(50), nullable=True),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("extra_json", postgresql.JSONB(), nullable=True),
        sa.Column("ingestion_run_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_run_id"], ["ingestion_runs.id"]),
        sa.CheckConstraint(
            "level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')",
            name="chk_le_level",
        ),
    )
    op.create_index("idx_log_entries_level", "log_entries", ["level"])
    op.create_index("idx_log_entries_module", "log_entries", ["module"])
    op.create_index("idx_log_entries_created", "log_entries", ["created_at"])
    op.create_index("idx_log_entries_run", "log_entries", ["ingestion_run_id"])

    op.execute(
        """
        CREATE VIEW public_market_view AS
        SELECT
            p.code AS product_code,
            p.canonical_name_he AS product_name,
            p.category,
            p.is_basket_product,
            da.aggregate_date,
            da.market_scope,
            da.sales_channel,
            da.sample_size,
            da.distinct_sources,
            da.weighted_avg_price AS avg_price,
            da.median_price,
            da.stddev_price,
            da.min_price,
            da.max_price,
            mu.code AS price_unit,
            da.meets_publish_threshold
        FROM daily_aggregates da
        JOIN products p ON p.id = da.product_id
        JOIN measurement_units mu ON mu.id = da.normalized_unit_id
        WHERE da.meets_publish_threshold = true
          AND p.is_active = true
        """
    )
    op.execute(
        """
        CREATE VIEW admin_observations_view AS
        SELECT
            no.id,
            no.observed_at,
            s.code AS source_code,
            s.name AS source_name,
            p.canonical_name_he AS product_name,
            no.price_amount,
            no.currency_code,
            mu_display.code AS display_unit,
            no.normalized_price_value,
            mu_norm.code AS normalized_unit,
            no.normalization_method,
            no.confidence_score,
            no.flag_status,
            no.flag_reason,
            no.is_benchmark,
            no.is_basket_product,
            no.is_organic_claimed,
            sfr.status AS fetch_status
        FROM normalized_observations no
        JOIN sources s ON s.id = no.source_id
        JOIN products p ON p.id = no.product_id
        JOIN measurement_units mu_display ON mu_display.id = no.display_unit_id
        LEFT JOIN measurement_units mu_norm ON mu_norm.id = no.normalized_unit_id
        JOIN source_fetch_runs sfr ON sfr.id = no.source_fetch_run_id
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS admin_observations_view")
    op.execute("DROP VIEW IF EXISTS public_market_view")

    op.drop_table("log_entries")
    op.drop_table("audit_log")
    op.drop_table("users")
    op.drop_table("publish_artifacts")
    op.drop_table("publish_runs")
    op.drop_table("weekly_snapshots")
    op.drop_table("daily_aggregates")
    op.drop_table("observation_flags")
    op.drop_table("normalized_observations")
    op.drop_table("raw_extracted_items")
    op.drop_constraint("fk_sfr_raw_asset", "source_fetch_runs", type_="foreignkey")
    op.drop_table("raw_assets")
    op.drop_table("source_fetch_runs")
    op.drop_table("ingestion_runs")
    op.drop_table("unit_conversions")
    op.drop_table("normalizer_rules")
    op.drop_table("product_aliases")
    op.drop_table("normalizer_profiles")
    op.drop_table("source_fetch_profiles")
    op.drop_table("product_merges")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("sources")
    op.drop_table("measurement_units")
