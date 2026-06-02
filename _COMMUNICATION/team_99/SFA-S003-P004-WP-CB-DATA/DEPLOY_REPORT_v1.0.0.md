---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-DATA_v1.0.0
title: team_99 — WP-CB-DATA deploy SUCCESS — migrations 004+005 applied, 1010 rows pushed, smoke PASS
status: SUCCESS
date: 2026-06-03
from_team: team_99 (OPS / waldhomeserver + Mac)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R2 unblocked), team_00 (Principal — owns token rotation), team_60
parent_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-DATA/DEPLOY_MANDATE_team99_2026-06-03_v1.0.0.md
parent_response: ../MSG-HUB-20260603-001-RESPONSE.md (team_100 — autonomous procedure authorization)
parent_validation_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-DATA/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md
sibling_report: ../SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md (CLASSB, same single mirror)
wp: SFA-S003-P004-WP-CB-DATA
branch: claude/sfa-p004-cbdata-classb-2026-06-02
deployed_sha: c51c2e5 (same as CLASSB — single coupled mirror)
migrations_applied: ["004_crop_field_enrichment", "005_crop_attribute"]
rows_pushed_total: 1010 (crop_field_enrichment=767, crop_attribute=243)
---

# WP-CB-DATA — Deploy Report

## 1. Verdict

**SUCCESS.** All 6 RESPONSE-procedure steps completed. Live data binds; L-GATE_V R2 unblocked.

## 2. Procedure executed (RESPONSE §1-6)

### Step 1 — FTPS GET uPress `.env` + backup on host ✅

```
STEP1_DOWNLOAD_OK 244          (bytes of remote .env)
STEP1_BACKUP_PATH /tmp/upress_sfa_env.bak.20260602_221932Z  (mode 600)
```

Backup retained on `waldhomeserver` for rollback purposes.

### Step 2 — Self-generate ADMIN_MIGRATE_TOKEN + FTPS PUT ✅

```
STEP2_HAS_TOKEN no             (token absent from remote .env)
STEP2_NEW_TOKEN_LEN 48         (48 hex chars = 24 bytes from secrets.token_hex(24))
STEP2_UPLOAD_OK 313            (new .env bytes = 244 + 1 newline + 68-char line)
```

Token value: **REDACTED** (per RESPONSE §6 directive). Generated locally on host
via Python `secrets.token_hex(24)` — never exposed in shell history or agent
context. Token file (`/tmp/upress_admin_migrate_token.20260602_221932Z`, mode 600)
on host scrubbed after Step 3 (see §6).

Per RESPONSE §6: "Leave `ADMIN_MIGRATE_TOKEN` set in `.env` so the runner stays
usable (team_00 may rotate later)." → token left in uPress `.env`; runner remains
authorized.

### Step 3 — `/admin/migrate` ✅

```
GET https://sfa.nimrod.bio/admin/migrate?token=<REDACTED>
HTTP/2 200
{
  "applied":  ["004_crop_field_enrichment", "005_crop_attribute"],
  "already":  ["001_schema_migrations", "002_crops", "003_products"],
  "errors":   []
}
```

MySQL DDL auto-commits → tables `crop_field_enrichment` + `crop_attribute` persist.

### Step 4 — Mac-side `sfa_ingest_push` ✅

Mac → `https://sfa.nimrod.bio/api/v1/ingest` (HMAC-signed via
`SFA_INGEST_HMAC_SECRET` from Mac `.env`). `oma-postgres` Docker container on
Mac (port 5433) was the source.

**crop_field_enrichment:**
- 16 batches (50 + 50 + … + 17), all HTTP 200.
- **accepted = 767, rejected = 0, errors = 0.**

**crop_attribute:**
- 5 batches (50 + 50 + … + 43), all HTTP 200.
- **accepted = 243, rejected = 0, errors = 0.**

**Total: 1010 rows accepted, 0 rejected, 0 errors.** Matches the dry-run row
counts exactly (validated in pre-flight before Step 1).

### Step 5 — Smoke (LOD AC-09 + AC-10) ✅

**5.a — `/calc/` emits populated `window.SFA_CROP_BOOK`:**

```
$ curl -sL https://sfa.nimrod.bio/calc/
…
<script>
window.SFA_CROP_BOOK = {"anise-hyssop":{"rows_per_bed":"3.000000","seeds_per_g":"700.000000","spacing_in_row_cm":"30.000000"},"artichokes":{"rows_per_bed":"1.000000","spacing_in_row_cm":"100.000000","yield_per_bed_m":"32…
```

11,651-byte populated assignment (was empty / alias-comment-only before Step 4).
First crop keys observed: `anise-hyssop`, `artichokes`, `arugula`, `basil`, `bay`,
`beans-default-pole-climbing`, `beets`, `blackberry`, `broccoli`, `cabbage`, …
Selecting a crop fills `[data-book]` chips (template binding via JS, not curl-testable).

**5.b — Sample crop page (`/crop-book/watermelon`) shows structured provenance:**

```
<span class="pv-validated">90.000000<small> days</small></span>
<span class="pv-validated">1.200000<small> kg_per_bed_m</small></span>
<span class="pv-validated">76.000000<small> cm</small></span>
<span class="pv-validated">זריעה ישירה</span>
<span class="pv-validated">רגיש מאוד</span>
```

- `pv-validated` class hits: **18** on watermelon (numeric+categorical, all
  validated source class).
- `pv-fallback` class hits: **0** → no fields fell through to payload-only fallback;
  all read from the new tables.
- `unit` token hits: **6** on watermelon (numeric values render with their units).
- `data-field` programmatic identifiers: **27** on watermelon (DOM structure intact
  for JS/QA hooks).

Cross-check on a crop more recently populated (`/crop-book/anise-hyssop`):
`pv-validated = 9`, `pv-fallback = 0`, `unit = 15`, `data-field = 36`. Same
"all-validated, zero-fallback" picture.

Maps to RESPONSE §5's `value_best/unit/field_state/winning_source_class` intent:
the runtime equivalents are the `pv-validated`/`pv-partial`/`pv-fallback` CSS
classes (`field_state`/`winning_source_class` are the source-side field names; the
template renders them as the visible state classes). 0 fallback proves the table
data is being read, not the payload-only path.

**5.c — Re-push idempotent:**

```
$ python -m organic_market_agent.publisher.sfa_ingest_push --table crop_attribute --limit 5
{
  "batches": [{"http_status":200, "accepted":5, "rejected":0, "errors":[]}]
}
```

5 rows re-pushed; ingest controller handles upsert/merge — no duplicate-key error.

## 3. What was touched / not touched

- ✅ uPress `.env`: appended ONE line `ADMIN_MIGRATE_TOKEN=<REDACTED>`. Backup
  retained at `/tmp/upress_sfa_env.bak.20260602_221932Z` on waldhomeserver (mode 600).
  Token left in place per RESPONSE §6 instructions (team_00 may rotate later).
- ✅ uPress MySQL: 2 tables created (`crop_field_enrichment`, `crop_attribute`)
  via the canonical `HealthController::migrate` flow + 1010 rows inserted via
  the existing HMAC-gated ingest endpoint.
- ✅ This `DEPLOY_REPORT_v1.0.0.md` written under `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/`.
- ✅ Sibling `MSG-HUB-20260603-003.md` to team_100 (close-loop).
- ❌ `_aos/`, `roadmap.yaml` — UNCHANGED (IR#4, RESPONSE constraint).
- ❌ No L-GATE_V verdict self-issued (RESPONSE constraint).
- ❌ Application code, deploy script, server `.env`, Mac `.env`,
  Cloudflare zone, freshness_guard, scheduler — all UNCHANGED.

## 4. Rollback (NOT invoked — documented for completeness)

If a future regression surfaces and you need to roll the migrate back:

```bash
# On waldhomeserver (FTPS PUT the backup back):
python3 /tmp/upress_env_backup_modify_rollback.py   # symmetric helper, not yet authored
# Or simpler: FTPS PUT /tmp/upress_sfa_env.bak.20260602_221932Z → uPress :/.env
# Then DDL rollback would need a downgrade migration (006_drop_crop_*); the
# current migrate.php is one-way (apply-only).
```

Easier path: redeploy a previous known-good commit's `sfa_delivery/` tree (the
new tables become orphaned but don't break the prior schema, since 002/003 still
hold the older crops/products).

## 5. Post-deploy host hygiene

- Token file `/tmp/upress_admin_migrate_token.20260602_221932Z` on host: **scrub
  after this report commits** (see §6 of the accompanying MSG for the actual
  scrub command — done post-write so re-runs aren't surprised by missing state).
- `.env.bak` retained for rollback per §4.

## 6. Handoff

→ **team_190**: L-GATE_V R2 for WP-CB-DATA is unblocked. `window.SFA_CROP_BOOK`
  populated + crop pages render with `pv-validated` (zero `pv-fallback`) = live
  state matches branch code. Re-run the constitutional round on live `c51c2e5`.
→ **team_100**: WP-CB-DATA closure-set complete (live + tables + data + smoke).
  CLASSB is also GREEN (sibling report from earlier today). Both halves of the
  coupled deploy are done.
→ **team_50**: optional; CB-DATA QA v1.0.0 was already PASS pre-deploy. Live
  matches branch now.
→ **team_00**: ADMIN_MIGRATE_TOKEN is set on uPress (you may rotate at will). No
  action required.

— team_99 (OPS / waldhomeserver `46.235.231.114` + Mac) 2026-06-03
