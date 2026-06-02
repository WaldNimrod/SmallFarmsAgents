---
id: SFA-S003-P004-WP-CB-DATA-LOD400
wp: SFA-S003-P004-WP-CB-DATA — Crop Book Enrichment Mirror (populate crop_field_enrichment + crop_attribute on the uPress MySQL delivery tier)
gate: L-GATE_S PASS_WITH_FINDINGS (team_190 Cursor/Composer 2.5 GPT, non-Claude, IR#1/#5; 14/14; authorize_build:true) — 2 INFO addressed inline (v0.2.0)
status: LOD400_LOCKED — team_10 L-GATE_B build authorized
author: team_100 (Claude Code, Chief Architect)
date: 2026-06-03
version: v0.2.0
lgate_s_verdict_ref: _COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-S_VERDICT_v1.0.0.md
findings_addressed_inline: "INFO-1 (L101 dtm-join is aggregate, not variety-selection — citation corrected §2.1); INFO-2 (no-default fallback aligned to consumer ORDER BY name first-variety, supersedes MIN(id) — §2.1/AC-04). Validator pre-authorized build; no R2."
canon_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md (v1.3.0, LOD200_LOCKED)
depends_on: SFA-S003-P004-WP-CB-MIG2 (LOD500_LOCKED, head 060), SFA-S003-P004-WP-CB-UI-ALIGN (DONE — calc book-chip + crop-page reads live, degrade-gracefully)
interface_map_ref: _archive/SFA-S003-P004-WP-CB-1/TEAM_100/FIELD_INTERFACE_MAP_v1.0.0.md
branch: claude/sfa-p004-cbdata-classb-2026-06-02 (off main be0e04f)
orchestration:
  build: team_10 (Claude Sonnet sub-agent)
  qa: team_50 (Claude Haiku)
  l-gate-b-verify: team_100 (Claude Opus, independent)
  deploy: team_99 (waldhomeserver FTPS relay → uPress) + Mac-side ingest push
  validation: team_190 (non-Claude — IR#1/#5 cross-engine)
---

# LOD400 — WP-CB-DATA: Crop Book Enrichment Mirror

Executable spec. Builder: **team_10** (Claude Sonnet). External validator: **team_190** (non-Claude, IR#1/#5).
team_100 (Opus) never self-issues L-GATE_S/L-GATE_V.

## 0. Problem & goal

The live crop book (sfa.nimrod.bio) renders from the uPress **MySQL** mirror. Two consumer code paths
already exist and **degrade gracefully when their backing tables are absent**:

- **`/calc` book-chip bind** — [`HubController::calc()`](../../../../sfa_delivery/app/Controllers/HubController.php) lines 142–164:
  `SELECT c.slug, e.field_name, e.value_best FROM crops c JOIN crop_field_enrichment e ON e.crop_id = c.id`
  for 7 calc-bound numeric fields (canonical **and** legacy alias names, L146–155). The `try/catch` at L161
  swallows the missing-table error → `crop_book_values` empty → calc JS falls back to manual input.
- **Crop-page structured provenance + COMPLETE/PARTIAL state** —
  [`CropBookViewController`](../../../../sfa_delivery/app/Controllers/CropBookViewController.php) L477:
  `SELECT field_name, value_best, unit, field_state, winning_source_class, confidence_score FROM crop_field_enrichment WHERE crop_id = ?`
  and L492 `SELECT attribute_key, value_canonical, value_list FROM crop_attribute WHERE crop_id = ?`.
  Both `try/catch`-degrade (L484, L499); today crop pages light up only via the **F-UI-01 payload fallback**
  (L503–508 — reads the per-field value + field_state embedded in the default-variety `payload_json`).

**The MySQL mirror has neither `crop_field_enrichment` nor `crop_attribute`** (migrations only define
`crops`, `crop_varieties`, `products`, `product_prices`, `schema_migrations`, `ingest_log` —
`sfa_delivery/migrations/00{1,2,3}_*.sql`). `sfa_ingest_push.py --table` only accepts
`crops|crop_varieties|products|cover_crops|all` ([:732](../../../../organic_market_agent/publisher/sfa_ingest_push.py)).

**Goal:** create the two crop-level MySQL mirror tables, extend the ingest (publisher + endpoint
whitelist) to populate them from the canonical Mac Postgres, and push the data — so the live `/calc`
book-chips and crop-page structured reads bind from the **tables** (the F-UI-01 payload fallback becomes
redundant, not removed). **Full scope** per team_00: both `crop_field_enrichment` **and** `crop_attribute`.

This closes the WP-CB-UI-ALIGN L-GATE_V R3 non-blocking follow-up:
*"SFA_CROP_BOOK book-chip bind awaits crop_field_enrichment mirror (WP-CB-DATA)."*

## 1. Grounded preconditions (verified 2026-06-02 @ be0e04f)

- **Canonical source = Mac `oma-postgres` (alembic head 060)**, variety-level:
  - `crop_field_enrichment` (`organic_market_agent/crop_book/enrichment_models.py`): keyed by `variety_id`+`field_name`;
    cols `value_best/value_min/value_max/confidence_score(Numeric 5,4)/source_count/winning_source_class/computed_at`.
    **No `unit` column.**
  - `crop_attribute` (`organic_market_agent/crop_book/attribute_models.py`): keyed by `variety_id`+`attribute_name`;
    cols `value_canonical(VARCHAR)`/`value_list(jsonb)`/`confidence_score`. T2=`value_canonical`, T3=`value_list`.
- **Canon unit registry** — `organic_market_agent/crop_book/canon/field_registry.py` `FIELD_REGISTRY[field_name].unit`
  (str | None) is the canonical unit per field. `canon/units.py` `UNIT_REGISTRY` holds the dimension strings.
- **field_state policy** (`sfa_ingest_push.py` L375–381): `_FIELD_STATE_TAU = 0.40`; `_HIGH_TRUST_CLASSES = {"EX","NI"}`;
  **VALIDATED iff `winning_source_class ∈ {EX,NI}` OR `confidence_score ≥ τ`, else UNVALIDATED; MISSING = no row.**
  This is **backend-stamped** — the UI renders state verbatim, no UI threshold math (the WP-CB-1 L-GATE_V lesson).
- **Field whitelists** (`sfa_ingest_push.py` L324–373): `_AGRONOMY_FIELD_WHITELIST` (25 T1 numeric fields, canonical
  post-MIG names) + `_CATEGORICAL_ATTRS_WHITELIST` (13 T2/T3 attribute names).
- **MySQL ingest endpoint** — `sfa_delivery/app/Controllers/IngestController.php`: generic
  `INSERT … ON DUPLICATE KEY UPDATE col = VALUES(col)` upsert over a per-table `TABLE_COLUMNS` allowlist (L28–45),
  idempotency-keyed (envelope: `schema_version=1, table, operation=upsert, idempotency_key, rows[]`).
- **MySQL migration runner** — `sfa_delivery/migrations/migrate.php` globs `[0-9][0-9][0-9]_*.sql`, applies in
  sort order, tracks in `schema_migrations`. **Adding numbered SQL files is sufficient** (no runner edit).
- **DB topology:** crop data is pushed **from the Mac** (server `oma-postgres` is at head 034, no crop-book schema;
  server cron only handles the market-index product). Hosting canon: uPress serves + holds live MySQL.

## 2. Design decisions (LOCKED for build)

1. **Crop-level aggregation via the default variety.** The MySQL mirror is keyed by `crop_id` (both consumer
   queries join/filter on `crop_id`). Postgres enrichment/attributes are variety-level. The fetchers select each
   crop's representative variety with the SAME rule the crop-page consumer uses
   (`CropBookViewController.php` L289–300): **the `crop_varieties.is_default = TRUE` variety; if none, the first
   variety by mirror-`name` ascending** (the consumer reads varieties `ORDER BY name` at L264 and falls back to
   `$varieties[0]`). Implement as
   `ROW_NUMBER() OVER (PARTITION BY crop_id ORDER BY is_default DESC, COALESCE(name_he,name_en,'variety-'||id) ASC, id ASC) = 1`
   — `COALESCE(name_he,name_en,'variety-'||id)` is exactly what the publisher pushes as the mirror `name`
   (`_fetch_crop_varieties` L511). This **supersedes the earlier MIN(id) fallback** so the mirror's chosen variety
   matches the page's default for no-default crops (addresses L-GATE_S INFO-2). Exactly **one row per
   `(crop_id, field_name)`** and per `(crop_id, attribute_key)`. The fetcher **logs the count of no-default crops**
   (data-hygiene signal; the name-collation tiebreak is best-effort across PG/MySQL and only matters for that minority).
   NOTE (INFO-1): the existing `dtm` read at `sfa_ingest_push.py` L101 is a per-crop **aggregate join**, not the
   variety-selection rule — the SSoT default-variety rule is `crop_varieties.is_default` per the consumer above.
2. **`unit` attached at ingest** from `FIELD_REGISTRY[field_name].unit` (Postgres enrichment carries no unit).
   `None` → SQL `NULL`.
3. **`crop_attribute` name mapping:** Postgres `attribute_name` → MySQL `attribute_key` (identical string).
   `value_list` (jsonb list) takes precedence and is delivered as a JSON array; otherwise `value_canonical`.
4. **field_state stamped at ingest** for crop-level rows, reusing the **existing** `_FIELD_STATE_TAU` /
   `_HIGH_TRUST_CLASSES` constants verbatim. No new threshold, no UI math.

## 3. Work items

### WI-1 — MySQL migration `004_crop_field_enrichment.sql` (delivery tier)
`sfa_delivery/migrations/004_crop_field_enrichment.sql`:
```sql
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
```
Composite PK `(crop_id, field_name)` is the upsert key. Matches both consumer SELECTs (value_best/unit/
field_state/winning_source_class/confidence_score).

### WI-2 — MySQL migration `005_crop_attribute.sql` (delivery tier)
`sfa_delivery/migrations/005_crop_attribute.sql`:
```sql
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
```
Consumer reads `attribute_key, value_canonical, value_list WHERE crop_id = ?` (CropBookViewController L492).
`field_state` additive (helps future structured reads; harmless to the current explicit-column SELECT).
No runner edit (migrate.php auto-globs).

### WI-3 — `IngestController::TABLE_COLUMNS` whitelist (delivery tier)
`sfa_delivery/app/Controllers/IngestController.php` — add two entries to the `TABLE_COLUMNS` const:
```php
'crop_field_enrichment' => [
    'crop_id', 'field_name', 'value_best', 'unit',
    'field_state', 'winning_source_class', 'confidence_score', 'last_pushed_at',
],
'crop_attribute' => [
    'crop_id', 'attribute_key', 'value_canonical', 'value_list',
    'field_state', 'last_pushed_at',
],
```
No other endpoint change — the generic upsert + idempotency handler already cover new tables once whitelisted.

### WI-4 — Publisher fetchers + `--table` choices (`sfa_ingest_push.py`)
- Extend `--table` choices to `("crops","crop_varieties","products","cover_crops","crop_field_enrichment","crop_attribute","all")`.
- Add `_fetch_crop_field_enrichment(conn)`:
  1. Resolve each crop's default variety: `SELECT crop_id, id, is_default FROM crop_varieties` → pick
     `is_default = TRUE`; fallback `MIN(id)` per crop when none. (One SQL + Python reduce, or a window query.)
  2. For those default `variety_id`s, read `crop_field_enrichment` rows where `field_name IN _AGRONOMY_FIELD_WHITELIST`
     (`SELECT variety_id, field_name, value_best, confidence_score, winning_source_class`).
  3. Per row emit `{crop_id, field_name, value_best (float|None), unit (FIELD_REGISTRY[field_name].unit),
     field_state (stamp via τ/high-trust), winning_source_class, confidence_score}`. Skip fields with no row
     (absence = MISSING at the consumer). `unit` resolved through the canon field registry import.
- Add `_fetch_crop_attribute(conn)`:
  1. Same default-variety resolution.
  2. Read `crop_attribute` rows where `attribute_name IN _CATEGORICAL_ATTRS_WHITELIST`
     (`SELECT variety_id, attribute_name, value_canonical, value_list`).
  3. Per row emit `{crop_id, attribute_key (=attribute_name), value_canonical, value_list (JSON when present,
     else None), field_state ('VALIDATED' when a value is present else 'MISSING')}`.
- Wire both into the `--table all` dispatch and the `{table → fetcher}` mapping next to the existing fetchers.
- Reuse the existing push/envelope helper (idempotency key, schema_version=1, operation=upsert).

### WI-5 — Tests (publisher + delivery)
- **Publisher (pytest):** `tests/crop_book/test_ingest_enrichment_mirror.py` (or extend the ingest test module):
  default-variety selection (incl. no-default fallback to MIN id), unit attach == FIELD_REGISTRY,
  field_state stamp matches τ/high-trust truth table, one-row-per-(crop,field), value_list→JSON path,
  attribute_name→attribute_key mapping.
- **Delivery (composer/PHPUnit):** an IngestController test asserting `crop_field_enrichment` + `crop_attribute`
  upsert + idempotency (duplicate key → no double count); unknown-table rejection still fires for a bogus table.

## 4. Acceptance criteria

- **AC-01** `004_*`/`005_*` SQL created; `php migrations/migrate.php` applies both, idempotent on re-run
  (`[skip]`); tables exist with the WI-1/WI-2 columns + composite PK + FK to `crops`.
- **AC-02** `TABLE_COLUMNS` includes both tables with exactly the WI-3 columns; unknown-table 400 unchanged.
- **AC-03** `--table` choices include both; `_fetch_crop_field_enrichment` + `_fetch_crop_attribute` exist and
  are wired into `all`.
- **AC-04** Default-variety aggregation: exactly one row per `(crop_id, field_name)` / `(crop_id, attribute_key)`;
  selection = `is_default DESC, COALESCE(name_he,name_en,'variety-'||id) ASC, id ASC` (matches the consumer's
  `is_default` then first-by-`name`). Tests cover: (a) a crop WITH a default variety, (b) a multi-variety crop
  with NO default → picks the first by name (NOT MIN id); fetcher logs the no-default count.
- **AC-05** Every emitted enrichment row's `unit == FIELD_REGISTRY[field_name].unit` (None→NULL).
- **AC-06** field_state stamp matches the τ/high-trust truth table, using the existing constants (no new threshold,
  no UI math).
- **AC-07** `crop_attribute`: `attribute_name`→`attribute_key`; `value_list` delivered as JSON when present, else
  `value_canonical`.
- **AC-08** Idempotency: same-key re-push → `duplicate=true`; fresh-data re-push upserts in place (stable row count
  per crop).
- **AC-09** (post-deploy, live) `/calc`: after the push, `crop_book_values` is non-empty for enriched crops;
  `calc_dash` emits a populated `SFA_CROP_BOOK`; selecting a crop populates `[data-book]` chips.
- **AC-10** (post-deploy, live) A sample crop page renders numeric provenance + categorical attributes +
  COMPLETE/PARTIAL state derived from the **tables** (confirm the structured read path, not only the payload
  fallback).
- **AC-11** `validate_aos.sh` 0 FAIL; pytest `tests/crop_book/` green (the 2 known pre-existing fails OK);
  delivery `composer test` green; no LOCKED file touched (reconciler, `enrichment_runner`, crop_book models,
  migrations 035–060, locked LODs).
- **AC-12** Constitutional: builder makes **no `_aos/` edits**, **no `roadmap.yaml` edits** (IR#4); changes confined
  to `sfa_delivery/` + `organic_market_agent/publisher/sfa_ingest_push.py` + new tests.

## 5. Risks

- **R-1 crop-level loses variety granularity.** Accepted — the default variety is the SSoT representative the crop
  page already centers on; consistent with the shipped `dtm` aggregation. Variety-level mirror is explicitly out of
  scope (no consumer needs it).
- **R-2 precision drift.** MySQL `DECIMAL(14,6)`/`DECIMAL(5,4)` mirror Postgres `Numeric(14,6)`/`Numeric(5,4)`.
- **R-3 value_list JSON round-trip.** Python list → JSON-encoded in the push payload → MySQL `JSON` column.
  Test the encode/store path.
- **R-4 crops with no default variety.** Fallback MIN(id); the fetcher logs the count of fallback crops.

## 6. Out of scope / guards

- No change to enrichment computation (`reconciler`, `enrichment_runner`, `field_policy.py`, crop_book models,
  migrations) — all LOCKED. This WP is mirror + transport only.
- No variety-level MySQL mirror; no server-side feature (search/rank/auth/new endpoints) — those go to
  `WP-SRV-IDEAS/REGISTER.md` (PROPOSED).
- The F-UI-01 payload fallback is left in place as defensive degrade — not removed.
- team_100 never self-issues L-GATE_S/L-GATE_V; team_190 (non-Claude) owns both.

## 7. Operational sequence (post-L-GATE_S PASS → build → QA)

1. team_99 deploy delivery-tier PHP to uPress (FTPS) + run `php migrations/migrate.php` (applies 004/005).
2. From the **Mac**: `python -m organic_market_agent.publisher.sfa_ingest_push --table crop_field_enrichment`
   then `--table crop_attribute` (or `--table all`) → HMAC `POST /api/v1/ingest`.
3. Smoke: `/calc` book-chips populate on crop select (AC-09); a sample crop page shows structured prov + state (AC-10).
4. team_100 prepares the L-GATE_V mandate → team_190 (non-Claude). On PASS: LOD500_LOCKED + ADR042 archive.
