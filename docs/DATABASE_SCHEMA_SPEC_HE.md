> **LANGUAGE NOTICE:** This document is a legacy Hebrew specification (MyFarmAgents v1.1).
> Platform: **MyFarmAgents** | Agent: **OrganicMarketAgent**
> All new documents are written in English. See `docs/GLOSSARY.md` for canonical terminology.
> This file is pending English rewrite — scheduled per milestone.

---

# Database Schema Spec — SmallFarms Market Data System

גרסה: 1.0  
תאריך: 2026-03-29  
מערכת נתונים: PostgreSQL (ישירות על המכשיר המקומי, ללא Docker)  
ORM: SQLAlchemy 2.x (Python)  
Migrations: Alembic

---

## 1. עקרונות Schema

- כל טבלה כוללת `id` מסוג `BIGSERIAL PRIMARY KEY`
- כל טבלה כוללת `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- טבלאות שמתעדכנות כוללות `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- timestamps הם תמיד `TIMESTAMPTZ` (timezone-aware)
- מחרוזות מוגבלות ב-`VARCHAR(N)` עם N ריאלי
- `TEXT` לתוכן חופשי / JSON גדול
- `NUMERIC(12,4)` למחירים — דיוק מספרי בלי floating point errors
- `JSONB` לשדות config/metadata גמישים
- Soft deletes עם `is_active BOOLEAN` — לא מוחקים רשומות

---

## 2. ממשק PostgreSQL

```bash
# יצירת DB מקומי
createdb smallfarms_local

# משתמש ייעודי
createuser smallfarms_app
psql -c "GRANT ALL ON DATABASE smallfarms_local TO smallfarms_app;"

# connection string
postgresql://smallfarms_app@localhost/smallfarms_local
```

---

## 3. Schema מלא

### 3.1 measurement_units

יחידות מידה רשמיות. seed data קבוע.

```sql
CREATE TABLE measurement_units (
    id          BIGSERIAL PRIMARY KEY,
    code        VARCHAR(30)  NOT NULL UNIQUE,
    name_he     VARCHAR(60)  NOT NULL,
    unit_type   VARCHAR(20)  NOT NULL
                CHECK (unit_type IN ('weight','count','bundle','basket','pack')),
    is_normalizable BOOLEAN  NOT NULL DEFAULT false,
    -- האם ניתן להמיר ליחידת בסיס (kg)
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_measurement_units_code ON measurement_units(code);
```

**Seed data:**

```sql
INSERT INTO measurement_units (code, name_he, unit_type, is_normalizable) VALUES
('kg',           'קילוגרם',      'weight', true),
('g',            'גרם',           'weight', true),
('unit',         'יחידה',         'count',  false),
('bunch',        'צרור',          'bundle', false),
('basket_small', 'סל קטן',       'basket', false),
('basket_medium','סל בינוני',    'basket', false),
('basket_large', 'סל גדול',      'basket', false),
('basket_family','סל משפחתי',   'basket', false),
('pack_250g',    'מארז 250 גרם', 'pack',   true),
('pack_500g',    'מארז 500 גרם', 'pack',   true),
('pack_1kg',     'מארז ק"ג',     'pack',   true);
```

---

### 3.2 unit_conversions

המרות יחידות מוגדרות ומבוקרות.

```sql
CREATE TABLE unit_conversions (
    id               BIGSERIAL PRIMARY KEY,
    from_unit_id     BIGINT       NOT NULL REFERENCES measurement_units(id),
    to_unit_id       BIGINT       NOT NULL REFERENCES measurement_units(id),
    factor           NUMERIC(12,6) NOT NULL,
    conversion_type  VARCHAR(20)  NOT NULL
                     CHECK (conversion_type IN ('exact','heuristic','product_specific')),
    product_id       BIGINT       REFERENCES products(id),  -- NULL = כל המוצרים
    notes            TEXT,
    is_active        BOOLEAN      NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_unit_conversion UNIQUE (from_unit_id, to_unit_id, product_id)
);

CREATE INDEX idx_unit_conversions_from ON unit_conversions(from_unit_id);
CREATE INDEX idx_unit_conversions_product ON unit_conversions(product_id);
```

**Seed data:**

```sql
-- g -> kg
INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type)
SELECT f.id, t.id, 0.001, 'exact'
FROM measurement_units f, measurement_units t
WHERE f.code = 'g' AND t.code = 'kg';

-- pack_250g -> kg
INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type)
SELECT f.id, t.id, 0.25, 'exact'
FROM measurement_units f, measurement_units t
WHERE f.code = 'pack_250g' AND t.code = 'kg';

-- pack_500g -> kg
INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type)
SELECT f.id, t.id, 0.5, 'exact'
FROM measurement_units f, measurement_units t
WHERE f.code = 'pack_500g' AND t.code = 'kg';

-- pack_1kg -> kg
INSERT INTO unit_conversions (from_unit_id, to_unit_id, factor, conversion_type)
SELECT f.id, t.id, 1.0, 'exact'
FROM measurement_units f, measurement_units t
WHERE f.code = 'pack_1kg' AND t.code = 'kg';
```

---

### 3.3 products

קטלוג המוצרים הקנוני.

```sql
CREATE TABLE products (
    id                         BIGSERIAL PRIMARY KEY,
    code                       VARCHAR(20)  NOT NULL UNIQUE,  -- PRD001, PRD002...
    canonical_name_he          VARCHAR(100) NOT NULL,
    category                   VARCHAR(40)  NOT NULL
                               CHECK (category IN (
                                   'root_vegetables','fruiting_vegetables',
                                   'leafy_greens','brassicas','alliums',
                                   'cucurbits','legumes_fresh','baskets'
                               )),
    default_measurement_unit_id BIGINT      NOT NULL REFERENCES measurement_units(id),
    is_organic_required        BOOLEAN      NOT NULL DEFAULT true,
    is_basket_product          BOOLEAN      NOT NULL DEFAULT false,
    -- סלים וCSA אינם נכנסים לאגרגציית מחיר ק"ג
    seasonality_notes          VARCHAR(100),
    display_order              INTEGER      NOT NULL DEFAULT 100,
    is_active                  BOOLEAN      NOT NULL DEFAULT true,
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_active ON products(is_active);
CREATE UNIQUE INDEX idx_products_code ON products(code);
```

---

### 3.4 product_aliases

מיפוי שמות גולמיים לשם קנוני. לב המנגנון.

```sql
CREATE TABLE product_aliases (
    id                   BIGSERIAL PRIMARY KEY,
    product_id           BIGINT       NOT NULL REFERENCES products(id),
    alias_text           VARCHAR(200) NOT NULL,
    alias_text_normalized VARCHAR(200) NOT NULL,
    -- גרסה מנורמלת: lowercase, trim, הסרת ניקוד
    source_id            BIGINT       REFERENCES sources(id),
    -- NULL = alias גלובלי, not-NULL = ספציפי למקור
    normalizer_profile_id BIGINT      REFERENCES normalizer_profiles(id),
    confidence           NUMERIC(3,2) NOT NULL DEFAULT 1.0
                         CHECK (confidence BETWEEN 0 AND 1),
    is_active            BOOLEAN      NOT NULL DEFAULT true,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_alias_text_source UNIQUE (alias_text_normalized, source_id)
);

CREATE INDEX idx_product_aliases_product ON product_aliases(product_id);
CREATE INDEX idx_product_aliases_text ON product_aliases(alias_text_normalized);
CREATE INDEX idx_product_aliases_source ON product_aliases(source_id);
```

---

### 3.5 product_variants

גרסאות מסחר שונות של אותו מוצר.

```sql
CREATE TABLE product_variants (
    id                    BIGSERIAL PRIMARY KEY,
    product_id            BIGINT       NOT NULL REFERENCES products(id),
    variant_name          VARCHAR(100) NOT NULL,
    quantity_value        NUMERIC(10,3),
    quantity_unit_id      BIGINT       REFERENCES measurement_units(id),
    normalized_base_unit_id BIGINT     REFERENCES measurement_units(id),
    normalized_factor     NUMERIC(12,6),
    -- factor להמרה ל-base unit
    is_composite          BOOLEAN      NOT NULL DEFAULT false,
    notes                 TEXT,
    is_active             BOOLEAN      NOT NULL DEFAULT true,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_product_variants_product ON product_variants(product_id);
```

---

### 3.6 product_merges

איחוד שני מוצרים שהתגלו כזהים. מנגנון normalizer קריטי.

```sql
CREATE TABLE product_merges (
    id               BIGSERIAL PRIMARY KEY,
    source_product_id BIGINT      NOT NULL REFERENCES products(id),
    -- המוצר "הישן" שמאוחד לתוך המוצר הקנוני
    target_product_id BIGINT      NOT NULL REFERENCES products(id),
    reason           TEXT,
    merged_by        VARCHAR(100),  -- 'admin' / 'agent' / username
    is_active        BOOLEAN      NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_product_merge UNIQUE (source_product_id),
    CONSTRAINT chk_no_self_merge CHECK (source_product_id != target_product_id)
);

CREATE INDEX idx_product_merges_source ON product_merges(source_product_id);
CREATE INDEX idx_product_merges_target ON product_merges(target_product_id);
```

---

### 3.7 sources

מקורות מידע לוגיים.

```sql
CREATE TABLE sources (
    id              BIGSERIAL PRIMARY KEY,
    code            VARCHAR(10)  NOT NULL UNIQUE,  -- SRC001, SRC002...
    name            VARCHAR(100) NOT NULL,
    base_url        VARCHAR(500),
    source_group    VARCHAR(30)  NOT NULL
                    CHECK (source_group IN (
                        'direct_price','basket_csa','discovery',
                        'benchmark','verification'
                    )),
    market_scope    VARCHAR(20)  NOT NULL
                    CHECK (market_scope IN ('community','benchmark','verification')),
    sales_channel   VARCHAR(30)  NOT NULL
                    CHECK (sales_channel IN (
                        'community_direct','csa_basket','farm_shop',
                        'farmers_market','retail_chain_benchmark',
                        'discovery_only','verification_only'
                    )),
    status          VARCHAR(20)  NOT NULL DEFAULT 'candidate'
                    CHECK (status IN ('active','candidate','deprecated','discovery_only')),
    priority        INTEGER      NOT NULL DEFAULT 5
                    CHECK (priority BETWEEN 1 AND 10),
    legal_review_required BOOLEAN NOT NULL DEFAULT false,
    legal_review_notes    TEXT,
    notes           TEXT,
    is_active       BOOLEAN      NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sources_market_scope ON sources(market_scope);
CREATE INDEX idx_sources_status ON sources(status);
CREATE INDEX idx_sources_active ON sources(is_active);
```

---

### 3.8 source_fetch_profiles

הגדרת כיצד ניגשים למקור בפועל.

```sql
CREATE TABLE source_fetch_profiles (
    id                    BIGSERIAL PRIMARY KEY,
    source_id             BIGINT      NOT NULL REFERENCES sources(id),
    platform_family       VARCHAR(30),
    -- 'easyfarm', 'standalone', 'govt', 'aggregator', null
    fetch_mode            VARCHAR(20) NOT NULL
                          CHECK (fetch_mode IN (
                              'html_page','json_endpoint','pdf_download',
                              'rss','directory_page'
                          )),
    entry_url             VARCHAR(500) NOT NULL,
    http_method           VARCHAR(10)  NOT NULL DEFAULT 'GET',
    request_headers_json  JSONB,
    schedule_kind         VARCHAR(20)  NOT NULL DEFAULT 'daily'
                          CHECK (schedule_kind IN ('daily','weekly','manual_check')),
    timeout_seconds       INTEGER      NOT NULL DEFAULT 30,
    retry_policy_json     JSONB        NOT NULL DEFAULT '{"max_retries": 2, "backoff_seconds": 60}',
    is_public_access      BOOLEAN      NOT NULL DEFAULT true,
    charset_hint          VARCHAR(20),
    selector_profile      JSONB,
    -- CSS/XPath selectors ספציפיים לאתר
    is_active             BOOLEAN      NOT NULL DEFAULT true,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fetch_profiles_source ON source_fetch_profiles(source_id);
CREATE INDEX idx_fetch_profiles_platform ON source_fetch_profiles(platform_family);
```

---

### 3.9 normalizer_profiles

מגדיר איזה normalizer חל על מקור.

```sql
CREATE TABLE normalizer_profiles (
    id               BIGSERIAL PRIMARY KEY,
    source_id        BIGINT      NOT NULL REFERENCES sources(id),
    normalizer_type  VARCHAR(40) NOT NULL
                     CHECK (normalizer_type IN (
                         'easyfarm_catalog','simple_product_grid',
                         'basket_only','retail_benchmark','official_wholesale'
                     )),
    version          VARCHAR(20)  NOT NULL DEFAULT '1.0',
    config_json      JSONB,
    -- config ספציפי לsource שלא מתאים ל-rules גנרי
    is_active        BOOLEAN      NOT NULL DEFAULT true,
    notes            TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_normalizer_profiles_source ON normalizer_profiles(source_id);
```

---

### 3.10 normalizer_rules

חוקי normalizer data-driven. כל שינוי ב-DB — ללא deploy.

```sql
CREATE TABLE normalizer_rules (
    id                    BIGSERIAL PRIMARY KEY,
    normalizer_profile_id BIGINT       NOT NULL REFERENCES normalizer_profiles(id),
    rule_kind             VARCHAR(30)  NOT NULL
                          CHECK (rule_kind IN (
                              'product_alias','unit_map','quantity_parse',
                              'organic_flag','ignore_pattern','benchmark_tag',
                              'basket_parse','price_correction'
                          )),
    match_pattern         VARCHAR(500) NOT NULL,
    -- regex או exact match
    match_type            VARCHAR(10)  NOT NULL DEFAULT 'exact'
                          CHECK (match_type IN ('exact','regex','contains','prefix')),
    replacement_value     VARCHAR(500),
    -- תלוי ב-rule_kind
    extra_params_json     JSONB,
    priority              INTEGER      NOT NULL DEFAULT 100,
    -- סדר הפעלה — נמוך = ראשון
    is_active             BOOLEAN      NOT NULL DEFAULT true,
    created_by            VARCHAR(100) DEFAULT 'system',
    -- 'system' / 'admin' / 'agent'
    notes                 TEXT,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_normalizer_rules_profile ON normalizer_rules(normalizer_profile_id);
CREATE INDEX idx_normalizer_rules_kind ON normalizer_rules(rule_kind);
CREATE INDEX idx_normalizer_rules_priority ON normalizer_rules(normalizer_profile_id, priority);
```

---

### 3.11 ingestion_runs

ריצה מערכתית אחת (כלל המקורות).

```sql
CREATE TABLE ingestion_runs (
    id               BIGSERIAL PRIMARY KEY,
    run_type         VARCHAR(20)  NOT NULL DEFAULT 'daily'
                     CHECK (run_type IN ('daily','manual','retry')),
    started_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    finished_at      TIMESTAMPTZ,
    status           VARCHAR(20)  NOT NULL DEFAULT 'running'
                     CHECK (status IN ('running','completed','partial','failed')),
    sources_total    INTEGER      NOT NULL DEFAULT 0,
    sources_succeeded INTEGER     NOT NULL DEFAULT 0,
    sources_failed   INTEGER      NOT NULL DEFAULT 0,
    community_sources_succeeded INTEGER NOT NULL DEFAULT 0,
    -- ספירה נפרדת לthreshold של publish
    triggered_by     VARCHAR(100) NOT NULL DEFAULT 'cron',
    -- 'cron' / 'admin' / 'agent'
    notes            TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ingestion_runs_status ON ingestion_runs(status);
CREATE INDEX idx_ingestion_runs_started ON ingestion_runs(started_at DESC);
```

---

### 3.12 source_fetch_runs

ריצה אחת לכל מקור בתוך ingestion_run.

```sql
CREATE TABLE source_fetch_runs (
    id                BIGSERIAL PRIMARY KEY,
    ingestion_run_id  BIGINT      NOT NULL REFERENCES ingestion_runs(id),
    source_id         BIGINT      NOT NULL REFERENCES sources(id),
    fetch_profile_id  BIGINT      REFERENCES source_fetch_profiles(id),
    started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at       TIMESTAMPTZ,
    status            VARCHAR(20) NOT NULL DEFAULT 'running'
                      CHECK (status IN ('running','success','failed','skipped','timeout')),
    http_status       INTEGER,
    bytes_fetched     INTEGER,
    error_message     TEXT,
    raw_asset_id      BIGINT,
    -- foreign key נוסף אחרי יצירת raw_assets
    retry_count       INTEGER     NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sfr_ingestion_run ON source_fetch_runs(ingestion_run_id);
CREATE INDEX idx_sfr_source ON source_fetch_runs(source_id);
CREATE INDEX idx_sfr_status ON source_fetch_runs(status);
```

---

### 3.13 raw_assets

מטה-דאטה על קבצי raw (הקבצים עצמם על filesystem).

```sql
CREATE TABLE raw_assets (
    id                  BIGSERIAL PRIMARY KEY,
    source_id           BIGINT      NOT NULL REFERENCES sources(id),
    source_fetch_run_id BIGINT      NOT NULL REFERENCES source_fetch_runs(id),
    storage_path        VARCHAR(500) NOT NULL,
    -- נתיב יחסי ל-RAW_FILES_ROOT, למשל: 2026/03/29/SRC002_143022.html
    file_type           VARCHAR(20) NOT NULL
                        CHECK (file_type IN ('html','json','pdf','rss','text','other')),
    checksum_sha256     CHAR(64)    NOT NULL,
    bytes_size          INTEGER     NOT NULL,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_raw_assets_source ON raw_assets(source_id);
CREATE INDEX idx_raw_assets_captured ON raw_assets(captured_at DESC);
CREATE INDEX idx_raw_assets_checksum ON raw_assets(checksum_sha256);

-- עדכון foreign key ב-source_fetch_runs
ALTER TABLE source_fetch_runs
    ADD CONSTRAINT fk_sfr_raw_asset
    FOREIGN KEY (raw_asset_id) REFERENCES raw_assets(id);
```

---

### 3.14 raw_extracted_items

פריטים גולמיים אחרי parser, לפני normalization.

```sql
CREATE TABLE raw_extracted_items (
    id                    BIGSERIAL PRIMARY KEY,
    source_fetch_run_id   BIGINT      NOT NULL REFERENCES source_fetch_runs(id),
    raw_asset_id          BIGINT      NOT NULL REFERENCES raw_assets(id),
    normalizer_profile_id BIGINT      REFERENCES normalizer_profiles(id),
    raw_product_name      VARCHAR(300),
    raw_price_text        VARCHAR(100),
    raw_unit_text         VARCHAR(100),
    raw_quantity_text     VARCHAR(100),
    raw_payload_json      JSONB,
    -- כל השדות הגולמיים כפי שנחצבו
    extraction_status     VARCHAR(20) NOT NULL DEFAULT 'extracted'
                          CHECK (extraction_status IN (
                              'extracted','normalized','unresolvable','ignored'
                          )),
    unresolvable_reason   VARCHAR(200),
    -- 'no_unit', 'no_price', 'basket_composite', 'pattern_mismatch'...
    extracted_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rei_fetch_run ON raw_extracted_items(source_fetch_run_id);
CREATE INDEX idx_rei_status ON raw_extracted_items(extraction_status);
```

---

### 3.15 normalized_observations

תצפית מנורמלת — יחידת האמת המרכזית לאגרגציה.

```sql
CREATE TABLE normalized_observations (
    id                    BIGSERIAL PRIMARY KEY,
    source_id             BIGINT      NOT NULL REFERENCES sources(id),
    source_fetch_run_id   BIGINT      NOT NULL REFERENCES source_fetch_runs(id),
    raw_extracted_item_id BIGINT      REFERENCES raw_extracted_items(id),
    product_id            BIGINT      NOT NULL REFERENCES products(id),
    product_variant_id    BIGINT      REFERENCES product_variants(id),
    market_scope          VARCHAR(20) NOT NULL
                          CHECK (market_scope IN ('community','benchmark','verification')),
    sales_channel         VARCHAR(30) NOT NULL
                          CHECK (sales_channel IN (
                              'community_direct','csa_basket','farm_shop',
                              'farmers_market','retail_chain_benchmark',
                              'discovery_only','verification_only'
                          )),
    is_benchmark          BOOLEAN     NOT NULL DEFAULT false,
    is_basket_product     BOOLEAN     NOT NULL DEFAULT false,
    is_organic_claimed    BOOLEAN     NOT NULL DEFAULT false,
    price_amount          NUMERIC(12,4) NOT NULL,
    currency_code         CHAR(3)     NOT NULL DEFAULT 'ILS',
    display_unit_id       BIGINT      NOT NULL REFERENCES measurement_units(id),
    normalized_price_value NUMERIC(12,4),
    -- מחיר לק"ג לאחר המרה (NULL אם לא ניתן להמרה)
    normalized_unit_id    BIGINT      REFERENCES measurement_units(id),
    normalization_method  VARCHAR(30)
                          CHECK (normalization_method IN (
                              'direct','unit_conversion_exact',
                              'unit_conversion_heuristic','basket_composite',
                              'unresolvable'
                          )),
    confidence_score      NUMERIC(3,2) NOT NULL DEFAULT 1.0
                          CHECK (confidence_score BETWEEN 0 AND 1),
    flag_status           VARCHAR(20) NOT NULL DEFAULT 'ok'
                          CHECK (flag_status IN ('ok','review','ignored','hidden')),
    flag_reason           VARCHAR(200),
    observed_at           TIMESTAMPTZ NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_obs_product ON normalized_observations(product_id);
CREATE INDEX idx_obs_source ON normalized_observations(source_id);
CREATE INDEX idx_obs_observed_at ON normalized_observations(observed_at DESC);
CREATE INDEX idx_obs_market_scope ON normalized_observations(market_scope);
CREATE INDEX idx_obs_flag_status ON normalized_observations(flag_status);
CREATE INDEX idx_obs_benchmark ON normalized_observations(is_benchmark);
-- index לאגרגציה
CREATE INDEX idx_obs_agg ON normalized_observations(
    product_id, market_scope, is_benchmark, flag_status, observed_at DESC
);
```

---

### 3.16 observation_flags

סימון/הסתרה של תצפיות — data-driven, ניתן לניהול admin/agent.

```sql
CREATE TABLE observation_flags (
    id                    BIGSERIAL PRIMARY KEY,
    observation_id        BIGINT      REFERENCES normalized_observations(id),
    -- NULL = rule-based (לא תצפית ספציפית)
    source_id             BIGINT      REFERENCES sources(id),
    product_id            BIGINT      REFERENCES products(id),
    flag_type             VARCHAR(20) NOT NULL
                          CHECK (flag_type IN ('hide','review','price_outlier','wrong_product')),
    scope                 VARCHAR(20) NOT NULL DEFAULT 'single'
                          CHECK (scope IN ('single','source_product','all_from_source')),
    reason                TEXT        NOT NULL,
    created_by            VARCHAR(100) NOT NULL DEFAULT 'admin',
    is_active             BOOLEAN     NOT NULL DEFAULT true,
    expires_at            TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_obs_flags_observation ON observation_flags(observation_id);
CREATE INDEX idx_obs_flags_source ON observation_flags(source_id);
CREATE INDEX idx_obs_flags_active ON observation_flags(is_active);
```

---

### 3.17 daily_aggregates

אגרגט יומי לפי מוצר, scope וערוץ.

```sql
CREATE TABLE daily_aggregates (
    id                   BIGSERIAL PRIMARY KEY,
    aggregate_date       DATE        NOT NULL,
    product_id           BIGINT      NOT NULL REFERENCES products(id),
    market_scope         VARCHAR(20) NOT NULL
                         CHECK (market_scope IN ('community','benchmark')),
    sales_channel        VARCHAR(30),
    -- NULL = אגרגט על כלל הערוצים
    is_basket_aggregate  BOOLEAN     NOT NULL DEFAULT false,
    sample_size          INTEGER     NOT NULL,
    distinct_sources     INTEGER     NOT NULL,
    -- כמה מקורות שונים תרמו
    min_price            NUMERIC(12,4),
    max_price            NUMERIC(12,4),
    unweighted_avg_price NUMERIC(12,4),
    weighted_avg_price   NUMERIC(12,4),
    -- שקלול לפי confidence_score
    median_price         NUMERIC(12,4),
    stddev_price         NUMERIC(12,4),
    normalized_unit_id   BIGINT      REFERENCES measurement_units(id),
    meets_publish_threshold BOOLEAN  NOT NULL DEFAULT false,
    -- sample_size >= 2 AND distinct_sources >= 2
    last_observed_at     TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_daily_aggregate UNIQUE (aggregate_date, product_id, market_scope, sales_channel)
);

CREATE INDEX idx_daily_agg_date ON daily_aggregates(aggregate_date DESC);
CREATE INDEX idx_daily_agg_product ON daily_aggregates(product_id);
CREATE INDEX idx_daily_agg_publish ON daily_aggregates(meets_publish_threshold, aggregate_date DESC);
```

---

### 3.18 weekly_snapshots

Freeze של מצב השוק לשבוע. לא raw — aggregate בלבד.

```sql
CREATE TABLE weekly_snapshots (
    id                   BIGSERIAL PRIMARY KEY,
    week_start_date      DATE        NOT NULL,
    week_end_date        DATE        NOT NULL,
    product_id           BIGINT      NOT NULL REFERENCES products(id),
    market_scope         VARCHAR(20) NOT NULL,
    sales_channel        VARCHAR(30),
    sample_size          INTEGER     NOT NULL,
    distinct_sources     INTEGER     NOT NULL,
    data_completeness_pct NUMERIC(5,2),
    -- כמה ימים בשבוע הייתה תצפית (מתוך 7)
    week_avg_price       NUMERIC(12,4),
    week_weighted_avg_price NUMERIC(12,4),
    week_median_price    NUMERIC(12,4),
    week_stddev_price    NUMERIC(12,4),
    week_min_price       NUMERIC(12,4),
    week_max_price       NUMERIC(12,4),
    normalized_unit_id   BIGINT      REFERENCES measurement_units(id),
    snapshot_created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_weekly_snapshot UNIQUE (week_start_date, product_id, market_scope, sales_channel)
);

CREATE INDEX idx_weekly_snap_product ON weekly_snapshots(product_id);
CREATE INDEX idx_weekly_snap_week ON weekly_snapshots(week_start_date DESC);
```

---

### 3.19 publish_runs

כל ריצת publish.

```sql
CREATE TABLE publish_runs (
    id                BIGSERIAL PRIMARY KEY,
    ingestion_run_id  BIGINT      REFERENCES ingestion_runs(id),
    run_type          VARCHAR(20) NOT NULL DEFAULT 'auto'
                      CHECK (run_type IN ('auto','manual','retry')),
    build_started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    build_finished_at TIMESTAMPTZ,
    upload_started_at TIMESTAMPTZ,
    upload_finished_at TIMESTAMPTZ,
    status            VARCHAR(20) NOT NULL DEFAULT 'building'
                      CHECK (status IN (
                          'building','build_failed','uploading',
                          'upload_failed','published','aborted'
                      )),
    artifact_version  VARCHAR(40),
    -- timestamp-based: 20260329-060000
    published_at      TIMESTAMPTZ,
    is_last_good      BOOLEAN     NOT NULL DEFAULT false,
    products_included INTEGER,
    community_products INTEGER,
    benchmark_products INTEGER,
    error_message     TEXT,
    triggered_by      VARCHAR(100) NOT NULL DEFAULT 'auto',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_publish_runs_status ON publish_runs(status);
CREATE INDEX idx_publish_runs_last_good ON publish_runs(is_last_good);
CREATE INDEX idx_publish_runs_published ON publish_runs(published_at DESC NULLS LAST);
```

---

### 3.20 publish_artifacts

קבצים שנוצרו בכל publish run.

```sql
CREATE TABLE publish_artifacts (
    id               BIGSERIAL PRIMARY KEY,
    publish_run_id   BIGINT      NOT NULL REFERENCES publish_runs(id),
    artifact_type    VARCHAR(20) NOT NULL
                     CHECK (artifact_type IN (
                         'public_json','public_html','manifest_json',
                         'manifest_last_good_json'
                     )),
    local_path       VARCHAR(500) NOT NULL,
    checksum_sha256  CHAR(64)    NOT NULL,
    bytes_size       INTEGER     NOT NULL,
    remote_path      VARCHAR(500),
    upload_status    VARCHAR(20) DEFAULT 'pending'
                     CHECK (upload_status IN ('pending','uploaded','failed','skipped')),
    uploaded_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_publish_artifacts_run ON publish_artifacts(publish_run_id);
CREATE INDEX idx_publish_artifacts_type ON publish_artifacts(artifact_type);
```

---

### 3.21 users

טבלת משתמשים. Phase A — ריקה. Phase B — admin יחיד.

```sql
CREATE TABLE users (
    id            BIGSERIAL PRIMARY KEY,
    email         VARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name  VARCHAR(100),
    role          VARCHAR(20)  NOT NULL DEFAULT 'admin'
                  CHECK (role IN ('admin','viewer')),
    is_active     BOOLEAN      NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

---

### 3.22 audit_log

רישום פעולות מנהל/agent.

```sql
CREATE TABLE audit_log (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT      REFERENCES users(id),
    -- NULL = פעולת מערכת / agent
    actor_name    VARCHAR(100) NOT NULL DEFAULT 'system',
    -- 'admin', 'agent', 'cron', username
    action        VARCHAR(100) NOT NULL,
    -- 'product.merge', 'observation.hide', 'publish.trigger', ...
    entity_type   VARCHAR(50),
    entity_id     BIGINT,
    before_state  JSONB,
    after_state   JSONB,
    ip_address    VARCHAR(50),
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_actor ON audit_log(actor_name);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
```

---

### 3.23 log_entries

לוגים מובנים של המערכת.

```sql
CREATE TABLE log_entries (
    id               BIGSERIAL PRIMARY KEY,
    level            VARCHAR(10)  NOT NULL
                     CHECK (level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    module           VARCHAR(60)  NOT NULL,
    -- 'collector.SRC002', 'normalizer', 'aggregator', 'publisher'...
    message          TEXT         NOT NULL,
    entity_type      VARCHAR(50),
    entity_id        BIGINT,
    extra_json       JSONB,
    ingestion_run_id BIGINT       REFERENCES ingestion_runs(id),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_log_entries_level ON log_entries(level);
CREATE INDEX idx_log_entries_module ON log_entries(module);
CREATE INDEX idx_log_entries_created ON log_entries(created_at DESC);
CREATE INDEX idx_log_entries_run ON log_entries(ingestion_run_id);

-- auto-cleanup: שמירת לוגים 90 יום
-- יש להגדיר pg_partman או cron job לניקוי
```

---

## 4. Views

### 4.1 public_market_view

View ציבורי — ללא source internals.

```sql
CREATE VIEW public_market_view AS
SELECT
    p.code                   AS product_code,
    p.canonical_name_he      AS product_name,
    p.category,
    p.is_basket_product,
    da.aggregate_date,
    da.market_scope,
    da.sales_channel,
    da.sample_size,
    da.distinct_sources,
    da.weighted_avg_price     AS avg_price,
    da.median_price,
    da.stddev_price,
    da.min_price,
    da.max_price,
    mu.code                   AS price_unit,
    da.meets_publish_threshold
FROM daily_aggregates da
JOIN products p ON p.id = da.product_id
JOIN measurement_units mu ON mu.id = da.normalized_unit_id
WHERE da.meets_publish_threshold = true
  AND p.is_active = true;
```

---

### 4.2 admin_observations_view

View admin — עם source details.

```sql
CREATE VIEW admin_observations_view AS
SELECT
    no.id,
    no.observed_at,
    s.code                    AS source_code,
    s.name                    AS source_name,
    p.canonical_name_he       AS product_name,
    no.price_amount,
    no.currency_code,
    mu_display.code           AS display_unit,
    no.normalized_price_value,
    mu_norm.code              AS normalized_unit,
    no.normalization_method,
    no.confidence_score,
    no.flag_status,
    no.flag_reason,
    no.is_benchmark,
    no.is_basket_product,
    no.is_organic_claimed,
    sfr.status                AS fetch_status
FROM normalized_observations no
JOIN sources s ON s.id = no.source_id
JOIN products p ON p.id = no.product_id
JOIN measurement_units mu_display ON mu_display.id = no.display_unit_id
LEFT JOIN measurement_units mu_norm ON mu_norm.id = no.normalized_unit_id
JOIN source_fetch_runs sfr ON sfr.id = no.source_fetch_run_id;
```

---

## 5. Alembic Setup

```
db/
  alembic.ini
  env.py
  versions/
    001_initial_schema.py
    002_seed_units.py
    003_seed_products.py
    004_seed_sources.py
    005_seed_aliases.py
```

---

## 6. SQLAlchemy Models — מבנה מומלץ

```python
# models/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import BigInteger, TIMESTAMP, func
from sqlalchemy.orm import mapped_column, Mapped
import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

class FullTimestampMixin(TimestampMixin):
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
```

---

## 7. manifest.json Schema

```json
{
    "schema_version": "1.0",
    "artifact_version": "20260329-060000",
    "published_at": "2026-03-29T06:15:00+02:00",
    "json_path": "market/public_report-20260329-060000.json",
    "html_path": "market/public_report-20260329-060000.html",
    "staleness_level": "ok",
    "staleness_days": 0,
    "community_products": 18,
    "benchmark_products": 12,
    "status": "published"
}
```

**staleness_level values:**
- `ok` — פורסם לפני פחות מ-3 ימים
- `warning` — 3–8 ימים
- `stale` — מעל 8 ימים

---

## 8. filesystem Layout

```
/data/smallfarms/
  raw/
    2026/
      03/
        29/
          SRC002_143022.html
          SRC003_143145.html
          ...
  artifacts/
    market/
      public_report-20260329-060000.json
      public_report-20260329-060000.html
      manifest.json
      manifest_last_good.json
  logs/
    app_2026-03-29.log
    fetch_2026-03-29.log
    publish_2026-03-29.log
```
