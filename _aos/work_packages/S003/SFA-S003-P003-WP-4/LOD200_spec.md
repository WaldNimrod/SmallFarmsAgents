# LOD200 — SFA-S003-P003-WP-4 — Publisher Migration (waldhomeserver → ingest API) (STUB)

**Date:** 2026-05-23
**Status:** LOD200_DRAFT — **BLOCKED on WP-2 (ingest endpoint must exist + HMAC auth contract finalized)**. Full LOD400 authored when WP-2 LOD500_LOCKED.

## Scope summary

Replace the existing `organic_market_agent/publisher/upload_dispatch.py` codepath:

| Old | New |
|-----|-----|
| `dispatch_upload(profile="market")` → `static_upload.upload_all_artifacts()` → WP media library (WP009) | `sfa_ingest_push.push_market_delta()` → HTTPS POST `https://sfa.nimrod.bio/api/v1/ingest` with HMAC auth |
| `dispatch_upload(profile="crop_book")` → `wp_upload.upload_all_crop_book_artifacts()` → WP media library | `sfa_ingest_push.push_crop_book_delta()` → same endpoint |

## Push flow per WP

1. Publisher queries Postgres for changed rows since last push (`last_pushed_at` per table)
2. Builds JSON delta payload: `{table: 'crops', operation: 'upsert', rows: [...]}`
3. Computes HMAC signature: `HMAC-SHA256(shared_secret, body)`
4. `requests.post(INGEST_URL, json=payload, headers={'X-SFA-Auth': sig})`
5. On 200: update `last_pushed_at`. On retriable 5xx/network: exponential backoff + retry. On 4xx: error log, no retry (programmer error).

## Auth contract (proposed — finalized in WP-2)

- `Shared secret` provisioned at WP-2 (random 32 bytes, base64-encoded)
- Stored on waldhomeserver `.env` as `SFA_INGEST_HMAC_SECRET`
- Stored on uPress PHP app `.env` (or equivalent) as same
- Request header: `X-SFA-Auth: sha256=<hex_signature>`

## Effort estimate

~1-2 days post-unblock by WP-2. Mostly mechanical replacement of HTTP call + adding HMAC signing + delta tracking.

## Will be expanded to LOD400 when

- WP-2 ingest endpoint contract finalized (exact JSON schema, error codes, idempotency keys)

---

*Stub LOD200 — authored 2026-05-23 by team_100. To be expanded post-WP-2.*
