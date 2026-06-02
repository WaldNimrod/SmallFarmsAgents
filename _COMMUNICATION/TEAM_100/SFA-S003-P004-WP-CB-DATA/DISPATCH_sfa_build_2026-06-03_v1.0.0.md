# BUILD DISPATCH — SFA-S003-P004-WP-CB-DATA — team_100 → team_10 — v1.0.0

**Date:** 2026-06-03
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_10 (sfa_build, Claude **Sonnet** sub-agent)
**Gate:** L-GATE_B
**Authority:** team_190 L-GATE_S PASS_WITH_FINDINGS (non-Claude, authorize_build:true); 2 INFO addressed inline → LOD400_LOCKED v0.2.0.
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02` (working tree; **do NOT run any git command** — team_100 owns git).
**Spec:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-DATA/LOD400_spec.md` (v0.2.0 — read it fully; it is authoritative).

## 0. Cross-engine + scope
- IR#1: you are **Claude Sonnet**; team_100 (Opus) verifies L-GATE_B + owns git; team_190 (non-Claude) gates L-GATE_V.
- **Scope:** `sfa_delivery/migrations/**`, `sfa_delivery/app/Controllers/IngestController.php`,
  `organic_market_agent/publisher/sfa_ingest_push.py`, and new tests only. **Do NOT** touch `_aos/`, the LOCKED
  enrichment-computation layer (reconciler, `enrichment_runner`, `field_policy.py`, crop_book ORM models, alembic
  migrations 035–060), or any other tree.
- **Do NOT run git. Do NOT run a live migration or push data** (that is the deploy step — team_99 + Mac push). Build + unit-test only.

## 1. Work items (per LOD v0.2.0 §3)
- **WI-1** `sfa_delivery/migrations/004_crop_field_enrichment.sql` — crop-level table, columns + composite PK
  `(crop_id, field_name)` + FK to `crops(id)` ON DELETE CASCADE, per LOD §3 WI-1 (verbatim DDL there).
- **WI-2** `sfa_delivery/migrations/005_crop_attribute.sql` — crop-level, PK `(crop_id, attribute_key)`, FK to crops,
  per LOD §3 WI-2. (migrate.php auto-globs `[0-9][0-9][0-9]_*.sql` — no runner edit.)
- **WI-3** `IngestController::TABLE_COLUMNS` — add the two entries (exact column lists in LOD §3 WI-3).
- **WI-4** `sfa_ingest_push.py`:
  - Extend `--table` choices to include `crop_field_enrichment` + `crop_attribute`; wire both into `all` and the
    `{table → fetcher}` dispatch.
  - `_fetch_crop_field_enrichment(conn)`: pick each crop's representative variety via
    `ROW_NUMBER() OVER (PARTITION BY crop_id ORDER BY is_default DESC, COALESCE(name_he,name_en,'variety-'||id) ASC, id ASC) = 1`
    (matches the consumer — LOD §2.1, addresses INFO-2; **NOT** MIN(id)); read that variety's
    `crop_field_enrichment` rows for `field_name IN _AGRONOMY_FIELD_WHITELIST`; per row emit
    `{crop_id, field_name, value_best(float|None), unit (=FIELD_REGISTRY[field_name].unit, None→NULL),
    field_state (stamp via existing _FIELD_STATE_TAU/_HIGH_TRUST_CLASSES), winning_source_class, confidence_score}`.
    Skip fields with no row (absence = MISSING). **Log the count of no-default crops.**
  - `_fetch_crop_attribute(conn)`: same representative-variety selection; read `attribute_name IN _CATEGORICAL_ATTRS_WHITELIST`;
    emit `{crop_id, attribute_key(=attribute_name), value_canonical, value_list (JSON when present else None),
    field_state ('VALIDATED' if a value present else 'MISSING')}`.
  - Reuse the existing push/envelope helper (idempotency key, schema_version=1, operation=upsert). Import
    `FIELD_REGISTRY` from `organic_market_agent.crop_book.canon.field_registry`.
- **WI-5** Tests:
  - Publisher pytest (`tests/crop_book/test_ingest_enrichment_mirror.py` or extend an existing ingest test): default-variety
    selection incl. **no-default → first-by-name** (AC-04), unit attach == FIELD_REGISTRY (AC-05), field_state truth
    table (AC-06), `value_list`→JSON + `attribute_name`→`attribute_key` (AC-07), one-row-per-(crop,field). Mock the DB
    cursor/rows where practical so tests don't need a live PG.
  - Delivery PHPUnit (extend the ingest test): the two new tables are accepted by `TABLE_COLUMNS`; unknown-table still 400.
    Use whatever DB the harness uses; if the test DB is sqlite, assert the whitelist/validation path rather than the
    MySQL-specific DDL (the `.sql` files are MySQL — they run on uPress at deploy, not in the sqlite test).

## 2. Self-verification (report the outputs)
- `cd <repo> && python -m pytest tests/crop_book/ -q` → green (the 2 known pre-existing fails are OK; no NEW fails).
- `cd sfa_delivery && composer test` → green.
- `php -l sfa_delivery/app/Controllers/IngestController.php` clean; sanity-check the two `.sql` files parse (e.g. via a
  MySQL-syntax linter if available, else careful review — they are not executed by the sqlite test harness).
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL (ignore Check-32 uncommitted-drift).

## 3. Report
Write `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-DATA/BUILD_REPORT_v1.0.0.md`: per-WI implementation (file:line),
AC-by-AC evidence (esp. AC-04 no-default→first-by-name, AC-05 unit, AC-06 field_state, AC-07 attribute mapping),
test outputs, validate_aos result, full file list. Then return a concise summary. **Do NOT commit** — hand the tree to team_100.
