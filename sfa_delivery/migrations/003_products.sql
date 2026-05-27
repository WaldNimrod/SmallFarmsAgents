-- 003 — products + product_prices
-- Canonical schema: documentation/03-data-and-schema/sfa-mysql-mirror.md §3.4 / §3.5

CREATE TABLE IF NOT EXISTS products (
  id              BIGINT        NOT NULL,
  slug            VARCHAR(80)   NOT NULL,
  hebrew_name     VARCHAR(200)  NOT NULL,
  category        VARCHAR(40)   NULL,
  unit            VARCHAR(20)   NULL,
  last_price      DECIMAL(10,2) NULL,
  last_price_date DATE          NULL,
  freshness_days  INT           NULL,
  last_pushed_at  DATETIME      NOT NULL,
  payload_json    JSON          NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_slug (slug),
  KEY idx_products_category (category),
  KEY idx_products_freshness (freshness_days),
  KEY idx_products_price_date (last_price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS product_prices (
  id         BIGINT AUTO_INCREMENT,
  product_id BIGINT        NOT NULL,
  price_date DATE          NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  source     VARCHAR(120)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_product_date_source (product_id, price_date, source),
  KEY idx_prices_date (price_date),
  CONSTRAINT fk_prices_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
