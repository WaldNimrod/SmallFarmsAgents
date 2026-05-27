-- 002 — crops + crop_varieties
-- Canonical schema: documentation/03-data-and-schema/sfa-mysql-mirror.md §3.2 / §3.3

CREATE TABLE IF NOT EXISTS crops (
  id              BIGINT       NOT NULL,
  slug            VARCHAR(80)  NOT NULL,
  hebrew_name     VARCHAR(200) NOT NULL,
  scientific_name VARCHAR(200) NULL,
  family_id       BIGINT       NULL,
  family_name_he  VARCHAR(200) NULL,
  category        VARCHAR(40)  NULL,
  season          VARCHAR(40)  NULL,
  dtm_min         INT          NULL,
  dtm_max         INT          NULL,
  last_pushed_at  DATETIME     NOT NULL,
  payload_json    JSON         NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_crops_slug (slug),
  KEY idx_crops_category (category),
  KEY idx_crops_season (season),
  KEY idx_crops_dtm (dtm_min, dtm_max)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crop_varieties (
  id           BIGINT       NOT NULL,
  crop_id      BIGINT       NOT NULL,
  name         VARCHAR(200) NOT NULL,
  payload_json JSON         NOT NULL,
  PRIMARY KEY (id),
  KEY idx_varieties_crop (crop_id),
  CONSTRAINT fk_varieties_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
