-- 006 — crop-level narrative content mirror (WP-CB-CONTENT)
-- Two tables: crop_content (canonical, Normal mode) + crop_content_source (per-source, Deep mode).
-- Keyed crop-scoped (not the Postgres surrogate content_id) so the FK + cascade stay crop-local.
-- Consumer: CropBookViewController::detail (Normal=canonical / Deep=per-source + attribution pills)

CREATE TABLE IF NOT EXISTS crop_content (
  crop_id              BIGINT       NOT NULL,
  content_type         VARCHAR(40)  NOT NULL,
  text_md              MEDIUMTEXT   NULL,
  winning_source_class VARCHAR(20)  NULL,
  confidence_score     DECIMAL(5,4) NULL,
  field_state          VARCHAR(20)  NULL,
  last_pushed_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (crop_id, content_type),
  CONSTRAINT fk_cc_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crop_content_source (
  crop_id        BIGINT       NOT NULL,
  content_type   VARCHAR(40)  NOT NULL,
  source_label   VARCHAR(100) NOT NULL,
  source_class   VARCHAR(20)  NOT NULL,
  raw_text_md    MEDIUMTEXT   NOT NULL,
  source_url     VARCHAR(500) NULL,
  display_order  INT          NOT NULL DEFAULT 0,
  last_pushed_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (crop_id, content_type, source_label),
  KEY idx_ccs_unit (crop_id, content_type),
  CONSTRAINT fk_ccs_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
