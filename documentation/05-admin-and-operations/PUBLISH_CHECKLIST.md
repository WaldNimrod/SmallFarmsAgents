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

## 4. External publish (when applicable)

- [ ] FTPS upload of versioned artifacts + `manifest.json` per ops runbook (M7 / uPress when gated).
- [ ] WordPress or static consumer still reads the expected paths.

## 5. Sign-off

- [ ] **Lead review** (Nimrod) after changes that alter community-visible prices or coverage — per project governance.

---

*Linked from [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md).*
