-- 005 — crop-level attribute mirror (categorical T2/T3 facts, keyed by crop_id + attribute_key)
-- WP-CB-DATA LOD400 §3 WI-2
-- Consumer: CropBookViewController L492

CREATE TABLE IF NOT EXISTS crop_attribute (
  crop_id         BIGINT        NOT NULL,
  attribute_key   VARCHAR(100)  NOT NULL,
  value_canonical VARCHAR(255)  NULL,
  value_list      JSON          NULL,
  field_state     VARCHAR(20)   NULL,
  last_pushed_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (crop_id, attribute_key),
  CONSTRAINT fk_ca_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
