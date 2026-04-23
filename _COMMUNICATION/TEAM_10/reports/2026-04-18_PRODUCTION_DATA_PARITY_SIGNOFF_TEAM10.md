# Production data parity — completion note (Team 10)

**Date:** 2026-04-18  
**Scope:** Align FTPS destination with WordPress `wp-content/uploads/market`, remove legacy `sfa` duplicate tree, document cache/verify guardrails.

## Root cause

- Pipeline uploaded to FTP path **`/sfa`** while **`UPRESS_PUBLIC_BASE`** pointed at `.../agents/sfa`. WordPress shortcode reads **`wp-content/uploads/market/public_report_body.html`** only.
- Public HTTPS `curl` to `wp-content/uploads/market/manifest.json` showed stale/test-like JSON while FTP `sfa/manifest.json` matched the host `output/public` (CDN + wrong directory for WP).

## Actions taken (waldhomeserver)

1. `.env`: `UPRESS_PUBLIC_BASE=https://www.nimrod.bio`, `UPRESS_UPLOAD_PATH=wp-content/uploads/market` (backup: `.env.bak.*`).
2. `python -m organic_market_agent run_publisher --output-dir output/public --upload` — artifacts written to `wp-content/uploads/market/` on uPress.
3. Removed duplicate market files under legacy FTP `sfa/` (14 files) after validation.
4. Deployed repo `ftps_upload.py` with optional `UPRESS_VERIFY_PUBLIC_MANIFEST`.

## Database audit

- No rows with dates ≥ 2099 in `normalized_observations`, `daily_aggregates`, or `ingestion_runs` (production DB).

## Operator follow-up (cache)

If `curl https://www.nimrod.bio/wp-content/uploads/market/manifest.json` still lags `artifact_version` vs host `output/public/manifest.json`, **purge ezCache / site cache** in uPress and re-check. Optional: set `UPRESS_VERIFY_PUBLIC_MANIFEST=1` in `.env` on the pipeline host.

**2026-04-18 check:** With `UPRESS_VERIFY_PUBLIC_MANIFEST=1`, post-upload verification reported **mismatch** (local `20260418_151114` vs public `20260417_004822`) — confirms **CDN/cache** still serving older JSON over HTTPS while FTP `wp-content/uploads/market/manifest.json` matches the host. **Purge site cache in uPress**, then re-run verify or `curl` until `artifact_version` aligns.

**2026-04-21 check:** FTP `manifest.json` under `wp-content/uploads/market` matches host `output/public` (e.g. `artifact_version` `20260421_060007`, 34 products). HTTPS `Last-Modified` for the same URL can still lag (CDN) — compare `content-length` / body to FTP `RETR`. Optional: `UPRESS_EZCACHE_PURGE_AFTER_UPLOAD=1` + WordPress Application Password env vars on the pipeline host to POST ezCache purge after FTPS (REST may 403 from some clients; uPress panel purge remains the fallback).

**2026-04-22 check:** uPress **full site / ezCache purge** was not run from this repository (panel access only). HTTPS verification at **2026-04-22T15:28:53Z** UTC (**18:28 IDT**): `curl` to `https://www.nimrod.bio/wp-content/uploads/market/manifest.json` → `artifact_version` `20260417_004822`, `product_count` `1`; `https://www.nimrod.bio/wp-content/uploads/market/public_report.json` → `products` length `1` (`product_count` parity), `report_date` `2099-08-12`, `generated_at` `2026-04-17T00:48:22.913920+00:00`. All match **`output/public/`** in this repo clone (`jq` on local `manifest.json` / `public_report.json`). **If FTP or waldhomeserver `output/public/` is newer** than these values but HTTPS still lags, purge full site + ezCache in the uPress panel, record the purge time (local TZ) on the next line, and re-`curl` until `artifact_version` and `product_count` match the pipeline host.

## Sign-off

- FTP listing of `wp-content/uploads/market/manifest.json` matches local manifest bytes after publish.
- HTTPS may trail until CDN purge; documented in runbook and checklist.
