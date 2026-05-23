-- 001 — plumbing tables (migrations tracker + ingest idempotency log)
-- SFA-S003-P003-WP-2

CREATE TABLE IF NOT EXISTS schema_migrations (
  version    VARCHAR(64) PRIMARY KEY,
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ingest_log (
  idempotency_key VARCHAR(120) NOT NULL,
  table_name      VARCHAR(40)  NOT NULL,
  applied_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  row_count       INT          NOT NULL,
  status          VARCHAR(20)  NOT NULL,
  PRIMARY KEY (idempotency_key),
  KEY idx_log_applied (applied_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
