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

## 5. Sign-off

- [ ] **Lead review** (Nimrod) after changes that alter community-visible prices or coverage — per project governance.

---

*Linked from [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md).*
