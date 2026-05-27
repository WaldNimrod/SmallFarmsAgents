# SFA Delivery Tier — MySQL Mirror Schema (canonical)

**Host:** `sfa.nimrod.bio` (uPress, `localhost` from PHP-FPM)
**DB:** `sfanms2u_SFAUserUiDB`
**Strategy:** Option B — Hybrid minimal top-level columns + `payload_json` blob ([decision](../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md), APPROVED 2026-05-23 by team_00).
**Authority:** This document is binding. Migrations in `sfa_delivery/migrations/*.sql` MUST match. Postgres (canonical SSoT on waldhomeserver) is upstream — see [`README.md`](README.md).
**Versioning:** Each `payload_json` carries `schema_version`; bumped on breaking shape changes.

---

## 1. Why this schema looks the way it does

Postgres on waldhomeserver has ~30 tables (canonical SSoT). The delivery tier serves only the user-facing read-only subset: crop book (~66 crops with varieties + economics + care + equipment + timelines + source attribution) and market (~32 products with daily prices + source attribution + freshness signals).

Mirroring all ~30 tables would mean: ~25 MySQL tables, a migration per Postgres schema change (~weekly), a complex per-table publisher push (WP-4), and elaborate insert-order handling on the ingest side. The user-facing subset doesn't need most of that fidelity — the user never filters by `raw_extracted_items.confidence_score` or joins through `source_fetch_profiles`.

**Option B (this doc)** keeps only fields used for filter/sort/index as MySQL columns; everything else flows in a `payload_json` blob per row. Trade-off summary in the [DECIDE artifact](../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md).

---

## 2. Table inventory (4 data tables + 2 plumbing)

| Table | Type | Row count (steady-state) | Top-level cols | Has `payload_json`? |
|-------|------|--------------------------|----------------|---|
| `crops` | data | ~66 | 10 | yes |
| `crop_varieties` | data | ~200 | 3 | yes |
| `products` | data | ~32 | 9 | yes |
| `product_prices` | data | ~10k (rolling 90d) | 4 | no (thin time-series) |
| `schema_migrations` | plumbing | (1 per migration) | 2 | no |
| `ingest_log` | plumbing | (rolling 30d) | 5 | no |

**6 tables total.** Compare with Postgres user-facing subset (~10 conceptual tables, ~20 with joins).

---

## 3. Table definitions (binding DDL)

> These are the canonical CREATE statements. `sfa_delivery/migrations/002_crops.sql` and `003_products.sql` MUST match byte-for-byte. Schema changes require:
> 1. Update this doc
> 2. Add new numbered migration file (do NOT edit existing migrations)
> 3. Bump `schema_version` in publisher (WP-4) payload if the change affects `payload_json` shape
> 4. Update `IngestController` if column whitelist changes

### 3.1 `schema_migrations` (plumbing)

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version    VARCHAR(64) PRIMARY KEY,
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Populated by `migrations/migrate.php` after each migration is applied successfully.

### 3.2 `crops` (data)

```sql
CREATE TABLE crops (
  id                  BIGINT       NOT NULL,                  -- matches Postgres crops.id
  slug                VARCHAR(80)  NOT NULL,                  -- URL-safe identifier
  hebrew_name         VARCHAR(200) NOT NULL,
  scientific_name     VARCHAR(200) NULL,
  family_id           BIGINT       NULL,                      -- denormalized; no FK (parent table not mirrored)
  family_name_he      VARCHAR(200) NULL,                      -- denormalized for grid display
  category            VARCHAR(40)  NULL,                      -- enum-like ("vegetable", "herb", "fruit", ...)
  season              VARCHAR(40)  NULL,                      -- "spring", "fall", "year-round"
  dtm_min             INT          NULL,                      -- days to maturity
  dtm_max             INT          NULL,
  last_pushed_at      DATETIME     NOT NULL,                  -- publisher sets each push; used for freshness signal
  payload_json        JSON         NOT NULL,                  -- see §4.1 for contract
  PRIMARY KEY (id),
  UNIQUE KEY uq_crops_slug (slug),
  KEY idx_crops_category (category),
  KEY idx_crops_season (season),
  KEY idx_crops_dtm (dtm_min, dtm_max)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Key choices:**
- `id` is **not** AUTO_INCREMENT — publisher pushes Postgres-side ID so reconciler can correlate.
- `family_id` carried as int but **no foreign key** — we don't mirror `crop_families` (saved 1 table; family display name denormalized into `family_name_he`).
- `dtm_min`/`dtm_max` are top-level (indexed) because the crop-book grid has a "fast crops" filter.

### 3.3 `crop_varieties` (data)

```sql
CREATE TABLE crop_varieties (
  id           BIGINT       NOT NULL,                         -- matches Postgres crop_varieties.id
  crop_id      BIGINT       NOT NULL,
  name         VARCHAR(200) NOT NULL,
  payload_json JSON         NOT NULL,                         -- see §4.2 for contract
  PRIMARY KEY (id),
  KEY idx_varieties_crop (crop_id),
  CONSTRAINT fk_varieties_crop FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Varieties are always loaded by `crop_id` (never queried standalone), so only that one index.

### 3.4 `products` (data)

```sql
CREATE TABLE products (
  id               BIGINT       NOT NULL,                    -- matches Postgres products.id
  slug             VARCHAR(80)  NOT NULL,
  hebrew_name      VARCHAR(200) NOT NULL,
  category         VARCHAR(40)  NULL,
  unit             VARCHAR(20)  NULL,                        -- display unit ("kg", "bundle", "head")
  last_price       DECIMAL(10,2) NULL,                       -- latest published price (NIS)
  last_price_date  DATE         NULL,
  freshness_days   INT          NULL,                        -- days since last_price_date; computed at push
  last_pushed_at   DATETIME     NOT NULL,
  payload_json     JSON         NOT NULL,                    -- see §4.3 for contract
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_slug (slug),
  KEY idx_products_category (category),
  KEY idx_products_freshness (freshness_days),
  KEY idx_products_price_date (last_price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

`freshness_days` is materialized at push (publisher computes it) rather than at read time — keeps the read endpoint simple and lets us index on it for "fresh today" filters.

### 3.5 `product_prices` (data, thin time-series)

```sql
CREATE TABLE product_prices (
  id          BIGINT AUTO_INCREMENT,
  product_id  BIGINT       NOT NULL,
  price_date  DATE         NOT NULL,
  price       DECIMAL(10,2) NOT NULL,
  source      VARCHAR(120) NULL,                              -- source name (denormalized; we don't mirror `sources` table)
  PRIMARY KEY (id),
  UNIQUE KEY uq_product_date_source (product_id, price_date, source),
  KEY idx_prices_date (price_date),
  CONSTRAINT fk_prices_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

No `payload_json` — this table is intentionally narrow + dense. UI may show "price last 30 days" sparkline; data fits one row per day-source.

**Retention:** publisher prunes >90 days on push. Reconciler audits retention boundary.

### 3.6 `ingest_log` (plumbing — idempotency)

```sql
CREATE TABLE ingest_log (
  idempotency_key VARCHAR(120) NOT NULL,                      -- "{table}_{YYYY-MM-DD}_{seq}"
  table_name      VARCHAR(40)  NOT NULL,
  applied_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  row_count       INT          NOT NULL,
  status          VARCHAR(20)  NOT NULL,                      -- "ok" | "partial" | "fail"
  PRIMARY KEY (idempotency_key),
  KEY idx_log_applied (applied_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Retention:** rows older than 30 days pruned by a separate cron (deferred to WP-4 — publisher owns delta semantics).

---

## 4. `payload_json` contracts (binding)

Each `payload_json` MUST be an object with `schema_version` at the top level. Publisher (WP-4) MUST set this. IngestController MUST reject (`HTTP 400`) any payload missing `schema_version`.

### 4.1 `crops.payload_json` — `schema_version: 1`

```jsonc
{
  "schema_version": 1,
  "description_md":       "Markdown description (Hebrew, mobile-first, RTL).",
  "economics": {
    "yield_per_dunam_kg":  1200,
    "price_window_nis":    [4.5, 7.0],            // [low, high] for the season
    "labor_hours_per_dunam": 80,
    "notes_md":            "..."
  },
  "care": {
    "sowing_md":   "...",
    "watering_md": "...",
    "fertilizing_md": "...",
    "pests_md":    "..."
  },
  "equipment": [                                  // ordered list
    {"name": "מקלע מים", "purpose_md": "..."}
  ],
  "timeline": {
    "weeks_total": 12,
    "phases": [
      {"week_start": 0, "week_end": 2, "label_md": "נביטה"},
      {"week_start": 2, "week_end": 8, "label_md": "צמיחה"},
      {"week_start": 8, "week_end": 12, "label_md": "קציר"}
    ]
  },
  "source_attribution": [                         // chain — denormalized from Postgres source tables
    {
      "source_id":   17,
      "source_name": "המועצה לצמחי נוי",
      "field":       "dtm_min",                  // which field this source supports
      "confidence":  0.92,
      "url":         "https://..."
    }
  ],
  "varieties_summary": [                          // duplicated for grid display (full data in crop_varieties)
    {"id": 401, "name": "סלינה", "is_default": true}
  ]
}
```

### 4.2 `crop_varieties.payload_json` — `schema_version: 1`

```jsonc
{
  "schema_version": 1,
  "description_md": "...",
  "characteristics": {
    "dtm_offset": -5,                             // vs parent crop
    "color":      "אדום",
    "size":       "בינוני",
    "use":        "קציר ירוק"
  },
  "source_attribution": [
    {"source_id": 12, "source_name": "...", "field": "dtm_offset", "confidence": 0.8}
  ]
}
```

### 4.3 `products.payload_json` — `schema_version: 1`

```jsonc
{
  "schema_version": 1,
  "description_md":     "...",
  "aliases":            ["שם נוסף 1", "..."],     // for client-side free-text search
  "basket_tiers":       [                          // if product is sold as basket
    {"label": "סל קטן", "items": ["..."], "price_nis": 80}
  ],
  "source_attribution": [
    {
      "source_id":   3,
      "source_name": "שוק הכרמל",
      "url":         "https://...",
      "freshness":   "daily"                      // "daily" | "weekly" | "irregular"
    }
  ],
  "price_history_summary": {                       // pre-aggregated; full series via product_prices
    "min_30d":    3.5,
    "max_30d":    8.0,
    "avg_30d":    5.2,
    "trend":      "stable"                        // "rising" | "falling" | "stable"
  }
}
```

---

## 5. Schema evolution rules (binding)

| Change kind | What to do |
|------------|------------|
| Add a **filter/sort** field (needed in WHERE/ORDER BY) | Add a top-level column → new numbered migration → bump `payload_json schema_version` if denormalized from JSON |
| Add a **display-only** field | Add inside `payload_json` → **no migration**, just publisher (WP-4) starts including it |
| Remove a top-level column | Add a new migration that drops it; bump publisher payload schema; keep `payload_json` shape backward-compatible for one release cycle |
| Rename a top-level column | New migration adds new column + backfill from old; new publisher writes both for one cycle; later migration drops old |
| Breaking `payload_json` shape change | Bump `schema_version` (e.g., 1 → 2). `CropsController` MUST handle both for one release. Reconciler (WP-A) validates all rows migrated. |
| Add an entire new table | New numbered migration; new controller endpoint; document here |

**Never edit an existing migration file once committed.** Sequence numbers are immutable history.

---

## 6. Postgres ↔ MySQL field mapping (excerpt)

Full mapping is implicit in publisher (WP-4 `sfa_ingest_push.py`). This table shows the canonical correspondences for `crops`:

| Postgres (`crops` table) | MySQL (`crops` column) | Notes |
|---|---|---|
| `id` (BIGSERIAL) | `id` (BIGINT) | Same value; publisher pushes |
| `slug` | `slug` | Direct |
| `hebrew_name` | `hebrew_name` | Direct |
| `scientific_name` | `scientific_name` | Direct |
| `family_id` (FK → `crop_families.id`) | `family_id` (denormalized) | No FK on MySQL |
| (`crop_families.hebrew_name` via JOIN) | `family_name_he` | Denormalized by publisher |
| `category` | `category` | Direct |
| `season` | `season` | Direct |
| `dtm_min`, `dtm_max` | same | Direct |
| `description_md` | → `payload_json.description_md` | Moved to JSON |
| `economics_*` columns | → `payload_json.economics.*` | Nested in JSON |
| `care_*` columns | → `payload_json.care.*` | Nested in JSON |
| `equipment` (related table) | → `payload_json.equipment[]` | Inlined as array |
| `timeline_*` columns | → `payload_json.timeline.*` | Nested in JSON |
| (`crop_variety_source_values` via JOIN) | → `payload_json.source_attribution[]` | Inlined as array |

`crop_varieties` and `products` follow the same pattern.

---

## 7. Read query examples (canonical patterns)

### Grid list (crop book index)

```sql
SELECT id, slug, hebrew_name, family_name_he, category, season, dtm_min, dtm_max
FROM crops
WHERE (? IS NULL OR category = ?)
  AND (? IS NULL OR season = ?)
  AND (? IS NULL OR dtm_max <= ?)
ORDER BY hebrew_name;
```

One query, all-indexed. `payload_json` NOT selected here (saves bandwidth on grid render).

### Detail page (single crop + varieties)

```sql
SELECT id, slug, hebrew_name, scientific_name, family_id, family_name_he,
       category, season, dtm_min, dtm_max, last_pushed_at, payload_json
FROM crops WHERE slug = ?;

SELECT id, name, payload_json
FROM crop_varieties WHERE crop_id = ?
ORDER BY name;
```

Two queries. PHP merges `payload_json` into the response object.

### Market index (with freshness signal)

```sql
SELECT id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days
FROM products
WHERE freshness_days <= 7  -- "fresh this week"
ORDER BY category, hebrew_name;
```

### Price history sparkline (single product, 30 days)

```sql
SELECT price_date, price, source
FROM product_prices
WHERE product_id = ? AND price_date >= CURDATE() - INTERVAL 30 DAY
ORDER BY price_date;
```

---

## 8. Operational facts

- **Backups:** uPress takes automatic nightly backups of the whole site (per their service). For belt-and-suspenders, `mysqldump` periodic export from waldhomeserver via SSH cron (deferred to WP-5 or post-cutover ops doc).
- **Connection pool:** PDO opens per-request; uPress shared host has connection caps (~50). With ~3 queries per page and short-lived connections, well within budget. Monitor in WP-3 load test.
- **`payload_json` size:** budgeted ≤8 KB per crops row, ≤4 KB per varieties/products. MySQL JSON column hard limit is much higher; staying small for CF cache efficiency.
- **Indices:** all `KEY` declarations are intentional. Adding new ones requires updating this doc.
- **Charset:** `utf8mb4` everywhere (Hebrew + emoji safe).
- **Collation:** `utf8mb4_unicode_ci` (case-insensitive, locale-aware ordering).
- **Engine:** InnoDB everywhere (FK support, transactional integrity for ingest).

---

## 9. Out of scope (will be in S004)

- Per-user state tables (`user_favorites`, `user_calculator_inputs`, etc.) — separate decision, separate migrations
- Comments/community tables — separate decision
- Admin write endpoints — separate auth scheme

Until S004, the delivery tier is read-only from any user's perspective; writes only via HMAC'd publisher push.

---

## 10. Cross-references

- **Architecture overview:** [`../02-architecture/sfa-delivery-tier.md`](../02-architecture/sfa-delivery-tier.md)
- **DECIDE artifact (this strategy's approval):** [`../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md`](../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md)
- **Postgres SSoT (upstream):** [`README.md`](README.md), `organic_market_agent/crop_book/models.py`, `organic_market_agent/models/`
- **Implementation spec (DDL files):** `_aos/work_packages/S003/SFA-S003-P003-WP-2/LOD400_spec.md` §7
- **Publisher push contract:** `_aos/work_packages/S003/SFA-S003-P003-WP-4/LOD200_spec.md` (will become LOD400 post-WP-2)

---

*Locked 2026-05-23 by team_100. Schema changes require team_00 approval via new DECISION artifact + new numbered migration file.*
