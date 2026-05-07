# Pre-publish review checklist (OrganicMarketAgent)

Run this after **material** changes: new or changed `product_aliases`, parser / selector fixes, new `catalog_scope_skip_rules`, or maintenance replays (`full_data_refresh`, `catalog_renormalize`) that affect community observations.

## 1. Local artifacts

- [ ] Open `output/public/public_report.html` — spot-check Hebrew copy, stale banner, **data_quality** transparency block.
- [ ] Open `output/public/public_report.json` — confirm `products` length, `index` window, `data_quality.raw_extracted_items` counts.
- [ ] Open `output/public/manifest.json` — `staleness_level`, `product_count`, `data_quality` present.

## 2. Index integrity

- [ ] At least **two distinct community sources** in the rolling window (publish aborts otherwise — confirm pipeline log).
- [ ] Compare a few product lines against admin **dashboard** / **diagnostics** for obvious drift.

## 3. Scope and catalog policy

- [ ] If scope rules changed: confirm new rows appear on **`/catalog/scope-skip`** and category breakdown on **`/diagnostics/normalizer`**.
- [ ] If aliases changed: confirm **`/catalog/pending-aliases`** queue is drained or intentional, then `catalog_renormalize` was run.

## 4. External publish — WP REST API primary, FTPS opt-in fallback (WP007)

**Primary upload path (waldhomeserver, port 443 HTTPS):** WP REST API via Application Password.
**Fallback path (non-blocked networks only):** FTPS port 21 — enable with `UPRESS_FALLBACK_FTPS=1`.

### 4a. WP REST API (primary — set by default on waldhomeserver)

- [ ] Verify `.env` has `UPRESS_WP_REST_BASE`, `UPRESS_WP_APP_USER`, `UPRESS_WP_APP_PASS` set (team_00 supplies credentials).
- [ ] Run publish with upload: `python -m organic_market_agent run_publisher --upload`
  — OR run standalone: `python -m organic_market_agent run_upload --output-dir output/public`
- [ ] Confirm 5 artifacts uploaded (4 canonical + manifest-of-URLs pointer):
  - `sfagent-manifest.json`
  - `sfagent-public-report.json`
  - `sfagent-public-report.html`
  - `sfagent-public-report-body.html`
  - `sfagent-manifest-of-urls.json` (AC-04 Option A pointer — shortcode reads this first)
- [ ] After first upload: run `python scripts/wp_shortcode_install.py --set-mou-url <pointer-url>` to set `sfagent_manifest_of_urls_url` WP option. Required once (or after pointer URL changes month-boundary).
- [ ] Verify WordPress page renders: `curl -s "https://www.nimrod.bio/SmallFarmsAgent" | grep -c sfagent` — positive count.
- [ ] Verify manifest is fresh: `curl -s "<sfagent-manifest-url>" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['artifact_version'])"` — shows today's version.
- [ ] If uPress rejects `.json` uploads (HTTP 415): install `wp-content/mu-plugins/sfagent-allow-json.php` — see `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`.
- [ ] Per-artifact media_id tracking files are written to `data/.wp_media_id_*` — do not delete; they enable delete-before-overwrite (keeps artifact URLs clean, no `-1`/`-2` suffix).
- [ ] If publish aborts (rolling-window gate), upload is skipped — see pipeline log / `pipeline_alerts`.
- [ ] If automated: confirm `upload_enabled=true` in `scheduler_config` (admin UI → Scheduler page).

### 4b. FTPS fallback (opt-in only — NOT the default; Bezeq port 21 is blocked from waldhomeserver)

- [ ] Set `UPRESS_FALLBACK_FTPS=1` in `.env` to force FTPS path.
- [ ] Verify `.env` has `UPRESS_SFTP_HOST`, `UPRESS_SFTP_USER`, `UPRESS_SFTP_PASS` set.
- [ ] **FTPS path parity:** `UPRESS_UPLOAD_PATH` must be `wp-content/uploads/market`. `UPRESS_PUBLIC_BASE` must be site origin only (e.g. `https://www.nimrod.bio`).
- [ ] Optional: set `UPRESS_VERIFY_PUBLIC_MANIFEST=1` to log a warning when public JSON lags behind local manifest.
- [ ] FTPS is only usable from networks where port 21 is NOT blocked. waldhomeserver on Bezeq network CANNOT use FTPS.

## 5. Sign-off

- [ ] **Lead review** (Nimrod) after changes that alter community-visible prices or coverage — per project governance.

---

*Linked from [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md).*
