# Shortcode Integration Decision — SFA-S002-P001-WP007

**Date:** 2026-05-07
**Author:** sfa_build (Team 10, Sonnet)
**WP:** SFA-S002-P001-WP007
**AC:** AC-04

---

## Decision: Option A — Manifest URL Pointer

**Choice:** Option A — the pipeline writes a single `sfagent-manifest-of-urls.json` file to the WP media library. The shortcode fetches this pointer file and dereferences the `report_body` URL to serve the current HTML fragment.

---

## Options Considered

### Option A — Manifest URL Pointer (CHOSEN)
Pipeline uploads `sfagent-manifest-of-urls.json` to `/wp/v2/media`. The URL of this pointer file is stored in WP option `sfagent_manifest_of_urls_url` (set post-upload via `scripts/wp_shortcode_install.py --set-mou-url <url>`). The shortcode reads that option on each request, fetches the pointer JSON, then fetches and returns `artifacts.report_body`.

**Pros:**
- The option `sfagent_manifest_of_urls_url` only changes when the manifest-of-URLs pointer file itself moves (i.e., almost never under the delete-before-overwrite scheme). The pointer file's URL is stable.
- No change to WP infrastructure beyond updating functions.php.
- Fully decoupled: the shortcode doesn't need to know about individual artifact URLs.
- Works with the delete-before-overwrite pattern: pointer URL is stable because we reuse the same canonical filename `sfagent-manifest-of-urls.json`.

**Cons:**
- Adds one HTTP request per page render (pointer file fetch). Acceptable given WP's own caching, and the pointer file is tiny (<300 bytes).
- Requires `sfagent_manifest_of_urls_url` to be set once after the first upload. Documented in DEPLOY_HANDOFF.md.

### Option B — WP Option Storage
Pipeline would POST artifact URLs directly to a WP option via `/wp/v2/settings`. This requires the option to be pre-registered with `register_setting()` in WordPress — an additional PHP step. The REST endpoint `/wp/v2/settings` only exposes explicitly registered settings.

**Rejected:** More WordPress side-setup; no meaningful advantage over Option A.

### Option C — Filename Slug Pinning
If uPress WP always returns a stable URL when re-uploading with the same canonical filename after delete-before-overwrite, the shortcode could hard-code the URL. The shaked-wg-agent pattern uses this approach successfully.

However, uPress/WordPress constructs `/wp/v2/media` URLs as `wp-content/uploads/YYYY/MM/slug.ext`. While the slug is controlled by `Content-Disposition`, the date-prefix path (`YYYY/MM`) changes each calendar month. This means a hard-coded URL in the shortcode becomes stale at the start of each new month.

**Rejected:** Monthly URL staleness is a production risk. Option A is safer.

---

## Implementation Summary

**`organic_market_agent/publisher/wp_upload.py`** — `upload_all_artifacts()`:
1. Uploads 4 canonical artifacts.
2. Builds `sfagent-manifest-of-urls.json` with the 4 returned `source_url` values.
3. Uploads the pointer file under `sfagent-manifest-of-urls.json`.

**`scripts/wp_shortcode_install.py`** — updated `SHORTCODE_PHP`:
- Uses `get_option('sfagent_manifest_of_urls_url')` to find the pointer file.
- Fetches pointer JSON, dereferences `artifacts.report_body`, returns that HTML.
- Falls back to red error paragraph on any failure.

**`scripts/wp_shortcode_install.py --set-mou-url <url>`**:
- POSTs the manifest-of-URLs URL to `/wp/v2/settings` (requires `sfagent_manifest_of_urls_url` to be registered).
- If registration is absent, prints the value for manual WP admin entry.
- Run once after first deploy; re-run whenever the pointer URL changes (only when its media_id is deleted and re-uploaded in a different month, i.e., very rarely).

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| sfagent_manifest_of_urls_url option not registered in WP | DEPLOY_HANDOFF.md includes a `register_setting` PHP snippet for functions.php |
| Extra HTTP round-trip per page render | WP object cache + CDN reduces this to near-zero in production |
| Report body URL changes monthly | Handled: pointer file is always fetched fresh; URL in manifest-of-URLs is updated by publisher every run |

---

*Decision locked. Implement complete as described.*
