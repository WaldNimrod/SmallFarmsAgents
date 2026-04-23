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

## 4. External publish (M7 — FTPS to uPress)

- [ ] Verify `.env` has `UPRESS_SFTP_HOST`, `UPRESS_SFTP_USER`, `UPRESS_SFTP_PASS` set (from `.env.upress`).
- [ ] Run publish with upload: `python -m organic_market_agent run_publisher --upload`
  — OR run standalone: `python -m organic_market_agent run_upload --output-dir output/public`
- [ ] Confirm versioned artifacts uploaded: `public_report-{ts}.json`, `public_report-{ts}.html`, `public_report_body-{ts}.html`
- [ ] Confirm fixed-name copies uploaded: `public_report.json`, `public_report.html`, `public_report_body.html`
- [ ] Confirm `manifest_last_good.json` uploaded before `manifest.json` (atomic upload order).
- [ ] Verify public access: `curl -s -o /dev/null -w "%{http_code}" https://nimrod.bio/wp-content/uploads/market/public_report.json` → 200
- [ ] Verify WordPress page: `curl -s -o /dev/null -w "%{http_code}" https://nimrod.bio/SmallFarmsAgent` → 200
- [ ] If automated: confirm `upload_enabled=true` in `scheduler_config` (admin UI → Scheduler page).
- [ ] **Production pipeline host (waldhomeserver):** The machine that runs the daily cron must keep **`upload_enabled=true`** so a successful publish triggers FTPS to `wp-content/uploads/market/` without a manual `run_upload`. Confirm `UPRESS_SFTP_*` in `/data/projects/smallfarmsagents/.env`.
- [ ] **FTPS path parity (critical):** `UPRESS_UPLOAD_PATH` must be **`wp-content/uploads/market`** (same tree the WordPress shortcode reads — see [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py)). **`UPRESS_PUBLIC_BASE`** must be the **site origin only** (e.g. `https://www.nimrod.bio`), not a subdirectory such as `/agents/sfa`, or manifest `upload_base` and public URLs will not match the real file layout.
- [ ] **Post-upload HTTP check:** `curl` `https://www.nimrod.bio/wp-content/uploads/market/manifest.json` and confirm `artifact_version` matches `output/public/manifest.json` on the pipeline host. If it does not (stale `product_count` / old `artifact_version` while FTP shows the new file), **purge site cache** in uPress (ezCache) and re-check. Optional: set `UPRESS_VERIFY_PUBLIC_MANIFEST=1` in `.env` to log a warning from [`ftps_upload.py`](../../organic_market_agent/publisher/ftps_upload.py) when public JSON lags behind the local manifest after upload.
- [ ] If publish aborts (e.g. rolling-window gate), upload is skipped — see pipeline log / `pipeline_alerts`.

## 5. Sign-off

- [ ] **Lead review** (Nimrod) after changes that alter community-visible prices or coverage — per project governance.

---

*Linked from [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md).*
