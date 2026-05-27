# SFA Delivery Tier — `sfa.nimrod.bio`

**Canonical architecture, locked 2026-05-23 (SFA-S003-P003).**
**Supersedes:** WordPress shortcode + mu-plugin delivery on `www.nimrod.bio/smallfarmsagent/`.

This document is the SSoT for the user-facing delivery layer of the SmallFarmsAgents (SFA) product. It is binding for all WPs in `SFA-S003-P003` and subsequent SFA work. Implementation specs (LOD400+) live under `_aos/work_packages/S003/SFA-S003-P003-WP-*/`; this file is the durable architectural reference.

---

## 1. Two-tier architecture (binding)

```
┌──────────────────────────────────────────────────────────────────────┐
│  END USER (browser, mobile)                                          │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ HTTPS (TLS via Cloudflare)
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  DELIVERY TIER — sfa.nimrod.bio (uPress shared LAMP)                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Cloudflare DNS + edge proxy (proxied; Universal SSL at edge)  │  │
│  └──────────────────────────────┬─────────────────────────────────┘  │
│                                 ▼                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  nginx (uPress) → PHP-FPM 8.x                                  │  │
│  │  ├─ Slim Framework 4 app at site root (no /app/ subdir)        │  │
│  │  ├─ MySQL 8 (uPress-provided, localhost from PHP)              │  │
│  │  └─ /public_assets/ static files (CSS/JS/fonts, CF-cached)     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Public surface (user):       Public API surface (publisher):        │
│    GET  /                      POST /api/v1/ingest  (HMAC-auth)     │
│    GET  /crop-book/           ↑ pushed by waldhomeserver only       │
│    GET  /crop-book/{slug}                                            │
│    GET  /market/                                                     │
│    GET  /market/{slug}                                               │
│    GET  /api/v1/{health,crops,products}                              │
└─────────────────────────────────▲────────────────────────────────────┘
                                  │ HTTPS POST  (X-SFA-Auth: sha256=…)
                                  │ pushed on data change
┌─────────────────────────────────┴────────────────────────────────────┐
│  BACKEND TIER — waldhomeserver (private, internal only)              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL (canonical SSoT — all writes)                      │  │
│  │  Scrapers, parsers, normalizer, aggregator (Python)            │  │
│  │  Publisher (Python) → sfa_ingest_push.py                       │  │
│  │  Reconciler (P002 WP-A) → audits Postgres↔MySQL drift          │  │
│  │  AOS infra, Team 60 admin, agent loops                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  NEVER serves end-user HTTP. Outbound HTTPS to delivery tier only.   │
└──────────────────────────────────────────────────────────────────────┘
```

### Tier responsibilities (non-overlapping)

| Concern | Backend tier (waldhomeserver) | Delivery tier (sfa.nimrod.bio) |
|---------|-------------------------------|----------------------------------|
| Canonical data ownership | ✅ Postgres SSoT | ❌ — MySQL is read-mirror only |
| Writes | ✅ all writes go here | ❌ — read-only except via ingest API |
| Scrapers / agents / pipeline | ✅ | ❌ |
| End-user HTTP serving | ❌ NEVER | ✅ only place |
| TLS termination | ❌ | ✅ via Cloudflare edge |
| Public IP exposure | ❌ private only | ✅ via uPress + CF |
| Schema authority | ✅ Postgres migrations (Alembic) | derived (numbered SQL files, ~4-6 tables) |
| Identity (S004 future) | issues JWTs | verifies JWTs |

---

## 2. Data flow

### 2a. Read (user → page render)

```
user clicks /crop-book/        → CF edge cache (TTL 5 min for index)
   ↓ cache miss
nginx → PHP-FPM → Slim router → CropsController::list
   ↓
PDO SELECT id, slug, hebrew_name, category, season, dtm_min, dtm_max, payload_json
   FROM crops WHERE category = ? ORDER BY hebrew_name
   ↓ (1 query, no joins; payload_json carries the rest)
JSON merge (top-level cols + payload_json) → Slim view (PHP template) → HTML
   ↓
nginx → CF edge cache → browser
```

Typical render: 1 SQL query, <50ms server-side, <200ms edge-to-browser.

### 2b. Write (waldhomeserver → delivery tier)

```
Postgres row change (publisher detects via last_pushed_at delta)
   ↓
sfa_ingest_push.py:
    payload = {
      table: 'crops',
      operation: 'upsert',
      rows: [{...top-level cols, payload_json: {...rest}}],
      idempotency_key: 'crops_2026-05-23_007',
      schema_version: 1
    }
    sig = HMAC-SHA256(SFA_INGEST_HMAC_SECRET, json_body)
    POST https://sfa.nimrod.bio/api/v1/ingest
         X-SFA-Auth: sha256=<sig>
         Content-Type: application/json
   ↓
Slim → HmacAuthMiddleware (constant-time compare)
   ↓ if OK
IngestController::receive
   ↓
INSERT INTO ingest_log (idempotency_key, ...)  — dedup check first
   ↓ if new
per row: INSERT INTO {table} ... ON DUPLICATE KEY UPDATE
   ↓
return 200 {accepted: N, idempotency_match: false}
   ↓
publisher updates Postgres `last_pushed_at` only after 200
```

### 2c. Reconciler (drift audit — WP-A team_110, runs nightly)

```
For each user-facing entity:
  Postgres canonical row → render expected delivery-tier shape
  GET https://sfa.nimrod.bio/api/v1/crops/{slug}
  diff = jq compare(expected, actual)
  if drift > tolerance:
     queue corrective re-push + log alert (pipeline_alerts table on waldhomeserver)
```

---

## 3. Stack canon

| Layer | Choice | Why |
|-------|--------|-----|
| DNS | Cloudflare (existing zone `nimrod.bio`) | Already in use; edge cache for free |
| Edge proxy / TLS | Cloudflare proxied (orange cloud) | Universal SSL auto, DDoS shield |
| Origin host | uPress shared LAMP | Existing relationship, FTPS works, MySQL provided |
| Web server | nginx (uPress-managed) | Provided, no config needed beyond `.htaccess` rewrites |
| PHP | 8.1+ (uPress default) | Slim 4 requirement |
| Framework | Slim 4 (micro) | ~5 MB, just routing + middleware; trivially swappable |
| DB access | PDO (PHP-native) | No ORM overhead; portable |
| MySQL | uPress-provided (`localhost` from PHP-FPM) | Standard offering |
| Migrations | Numbered SQL files + 60-line PHP runner | No Phinx/Doctrine; portable, auditable |
| Templating | Plain PHP includes (Plates if needed later) | No build step, no framework lockin |
| Frontend | Vanilla HTML/CSS/JS (continues current `crop_book` SPA pattern) | No build step, fast |
| Auth (S004+) | JWT (50-line helper) | Deferred; not needed for S003 read-only delivery |
| Deploy | FTPS port 21 + explicit TLS + `prot_c` + `lftp mirror` | Verified WP-1; uPress only path |
| Secrets transport | None — `.env` composed locally, FTPS-uploaded, `chmod 600` server-side | No KMS available on shared host |

---

## 4. Portability claim (binding)

The delivery tier is **a standard LAMP application**. Migrating off uPress to any LAMP-capable host (DigitalOcean droplet, Hetzner, A2 Hosting, etc.) is:

```bash
# 1. Snapshot
mysqldump -u $SFA_DB_USER -p $SFA_DB_NAME > snapshot.sql
tar czf code.tgz index.php .htaccess composer.json composer.lock vendor app migrations public_assets

# 2. Upload + restore
scp snapshot.sql code.tgz new-host:/var/www/sfa/
ssh new-host "cd /var/www/sfa && tar xzf code.tgz && mysql ... < snapshot.sql"

# 3. Point DNS
# Cloudflare → CNAME sfa → new-host
```

No uPress-specific bindings exist. No proprietary file formats. No closed-source dependencies. This is a hard architectural invariant: **no code on the delivery tier may depend on uPress-specific facilities** (e.g., uPress control panel API, uPress backup format, uPress monitoring API). If such a dependency would speed development, add it on the backend tier instead.

---

## 5. Public URL contract (frozen)

| Path | Method | Auth | Purpose |
|------|--------|------|---------|
| `/` | GET | none | Landing — intro + nav |
| `/crop-book/` | GET | none | Crop book grid (66 crops, filters: category, season, DTM) |
| `/crop-book/{slug}` | GET | none | Single crop detail (8 tabs per existing UI) |
| `/market/` | GET | none | Market index (32 products, daily prices) |
| `/market/{slug}` | GET | none | Single product detail + price history |
| `/api/v1/health` | GET | none | `{status, php_version, db: ok|fail, ts}` — for monitoring |
| `/api/v1/crops` | GET | none | JSON list (pagination, filter params) |
| `/api/v1/crops/{slug}` | GET | none | JSON single crop (merged columns + payload_json) |
| `/api/v1/products` | GET | none | JSON list |
| `/api/v1/products/{slug}` | GET | none | JSON single product |
| `/api/v1/ingest` | POST | **HMAC-SHA256** (`X-SFA-Auth: sha256=…`) | Push delta from waldhomeserver publisher |
| `/admin/migrate?token=…` | GET | **one-time token** | First-deploy migration runner; removed after use |

**Frozen as of 2026-05-23.** Changes require a new DECISION artifact.

---

## 6. Security posture

- All HTTP forced to HTTPS by `.htaccess` rewrite (defense-in-depth; CF also enforces)
- `/.env`, `/composer.{json,lock}`, `/migrations/`, `/app/`, `/tests/`, `/vendor/`, `/logs/` blocked via `.htaccess` (`F` = 403)
- `.env` permission `chmod 600` server-side (PHP-FPM user reads; web server cannot serve)
- HMAC secret: 32 bytes (256 bits) from `openssl rand -base64 32`, identical on waldhomeserver and uPress; rotated annually or on suspected leak
- HMAC verified by `hash_equals()` (constant-time)
- Ingest idempotency via `idempotency_key` (replay → `{duplicate: true}`, no double-apply)
- FTPS IP allowlist enforced at uPress firewall (Mac dev IP + waldhomeserver IP only)
- No user write paths anywhere (S003 is read-only; S004 will introduce JWT-gated writes via separate POST routes)
- No PII in MySQL (S003); S004 user data design will be a separate decision

---

## 7. What NOT to do (binding anti-patterns)

| Anti-pattern | Why forbidden | Use this instead |
|--------------|---------------|------------------|
| Direct MySQL writes from waldhomeserver (bypass ingest API) | Bypasses HMAC + idempotency + audit log | Always go through `POST /api/v1/ingest` |
| WordPress, plugins, themes on delivery tier | Reintroduces the friction P003 escaped | Pure Slim + PDO |
| Cron jobs on delivery tier doing heavy work | Shared host = capped CPU; risks throttling | Cron on waldhomeserver; push results |
| Storing secrets in code, git, or PHP `define()` | Leak risk; non-rotatable | `.env` only; `chmod 600` |
| ORM (Doctrine, Eloquent) | Pulls in heavy deps; obscures SQL | PDO direct |
| Frontend build step (webpack, vite, npm) | Requires Node on uPress (not available) | Vanilla HTML/CSS/JS |
| `payload_json` field expansion that creates new top-level columns | Schema migrations on delivery tier should be rare | Add new fields inside `payload_json` (additive, no migration) |
| Public write endpoints without HMAC or JWT | Trivially abused | Either HMAC (machine) or JWT (user, S004+) |
| Long-lived MySQL connections | Shared host has connection caps | Short PDO per request (Slim default) |
| Reading from `payload_json` for filters/sorts | Slow vs indexed column | If filter is needed often, add a top-level column + migrate |

---

## 8. Cross-references

- **Schema spec (binding):** [`../03-data-and-schema/sfa-mysql-mirror.md`](../03-data-and-schema/sfa-mysql-mirror.md)
- **Parent decision:** `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- **Schema strategy decision:** `_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md` (Option B APPROVED)
- **WP-1 provisioning results:** `_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_2026-05-23_v1.0.0.md`
- **WP-2 implementation spec:** `_aos/work_packages/S003/SFA-S003-P003-WP-2/LOD400_spec.md`
- **Reconciler (WP-A):** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-A/HANDOFF_CONTEXT_v1.0.0.md`
- **Backend pipeline architecture:** [`README.md`](README.md) §"Normalizer pipeline"

---

*Locked 2026-05-23 by team_100. Changes require team_00 approval via new DECISION artifact.*
