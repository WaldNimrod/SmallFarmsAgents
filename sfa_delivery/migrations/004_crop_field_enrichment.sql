-- 004 — crop-level enrichment mirror (numeric T1 facts, keyed by crop_id + field_name)
-- WP-CB-DATA LOD400 §3 WI-1
-- Consumer: HubController::calc() L142-164, CropBookViewController L477

CREATE TABLE IF NOT EXISTS crop_field_enrichment (
  crop_id              BIGINT        NOT NULL,
  field_name           VARCHAR(100)  NOT NULL,
  value_best           DECIMAL(14,6) NULL,
  unit                 VARCHAR(40)   NULL,
  field_state          VARCHAR(20)   NOT NULL DEFAULT 'UNVALIDATED',
  winning_source_class VARCHAR(20)   NULL,
  confidence_score     DECIMAL(5,4)  NULL,
  last_pushed_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (crop_id, field_name),
  CONSTRAINT fk_cfe_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
