# Product icons — publish standard (OrganicMarketAgent)

**Language:** English (project documentation policy).  
**Status:** Normative for public HTML + JSON publish artifacts.  
**Last updated:** 2026-04-05

---

## Goal

Public product rows and channel filter buttons use **one visual system**: consistent stroke weight, corners, and scale. Legacy per-row Unicode emoji are **removed** from publisher templates.

---

## Icon family

| Item | Value |
|------|--------|
| **Set** | [IconPark](https://iconpark.oceanengine.com/official) **Outline** |
| **License** | **Apache-2.0** (commercial use allowed; retain `NOTICE` / attribution as required by Apache-2.0 when redistributing modified SVGs) |
| **Source of SVG files** | Fetched via [Iconify API](https://iconify.design/) and vendored in-repo (no runtime CDN dependency) |
| **Stroke color** | `#1b4332` (aligned with `--sfa-green-dark` in `sfagent-base.css`) baked into files at fetch time |

---

## Repository layout

| Path | Role |
|------|------|
| `organic_market_agent/publisher/static/icons/iconpark/*.svg` | Vendored assets (committed) |
| `organic_market_agent/publisher/product_icons.py` | `PRODUCT_CODE_TO_SLUG`, `FILTER_ICONS`, `augment_publish_product()`, defaults |
| `scripts/fetch_iconpark_outline_icons.py` | Regenerate / extend SVGs from Iconify (requires network + `User-Agent`) |

---

## Publish output layout

After `PublishEngine.run()`, each artifact directory contains:

- `icons/iconpark/<slug>.svg` — copies of the vendored files (full set, not only rows in the table).

HTML and JSON reference products with:

- `icon_path`: relative URL `icons/iconpark/<slug>.svg` (resolved from the same directory as `public_report.html` / uploaded `market/` folder).
- `icon_slug`: string key for debugging and future tooling.

**WordPress body embed:** If the body fragment is injected into a normal page (URL **not** under `…/wp-content/uploads/market/`), relative `src="icons/iconpark/…"` will 404. **Canonical fix (implemented):** the child-theme shortcode in [`tools/wordpress/sfagent_market_report_shortcode.php`](../../tools/wordpress/sfagent_market_report_shortcode.php) rewrites those `src` values to absolute URLs under `wp_upload_dir()['baseurl']/market/` when rendering `[sfagent_market_report]`. Merge it via [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py) (FTPS).

**Site-wide PHP helper:** `sfagent_market_icon_url( 'tomato' )` returns the public URL for any IconPark slug under `uploads/market/icons/iconpark/` (sanitized slug). Use in theme templates for consistent icons outside the published body fragment.

**FTPS upload (belt-and-suspenders):** [`ftps_upload.rewrite_body_html_icon_src_for_wp`](../../organic_market_agent/publisher/ftps_upload.py) rewrites `src="icons/iconpark/…"` to absolute URLs using `UPRESS_PUBLIC_BASE` + `UPRESS_UPLOAD_PATH` when uploading `public_report_body.html` (and versioned body files). Set `UPRESS_PUBLIC_BASE` to the **canonical** site origin visitors use (e.g. `https://www.nimrod.bio` if the live site is always `www`).

See also [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md) §3.

---

## Product mapping

- **Primary key:** `Product.code` (e.g. `PRD001`) — same as `product_id` in `public_report.json` products[].
- **Fallback slug:** `leaf` when code is unknown.
- **Do not** map by `canonical_name_he` in templates; Hebrew strings drift with catalog edits.

To add a **new** catalog product: add a row to `PRODUCT_CODE_TO_SLUG` and ensure the slug SVG exists under `static/icons/iconpark/` (run the fetch script after adding the slug to its lists, or copy an existing SVG under a new name only if license and style match).

---

## Channel filter buttons

Filter keys: `all`, `grower`, `baskets`, `store`, `chain` → slugs in `FILTER_ICONS` (same IconPark outline family).

---

## Manifest

`manifest.json` includes:

```json
"product_icons": {
  "family": "icon-park-outline",
  "license": "Apache-2.0",
  "relative_dir": "icons/iconpark",
  "file_count": <n>
}
```

---

## FTPS upload

Nested paths (`icons/iconpark/*.svg`) require remote subdirectory creation. `ftps_upload._ensure_remote_parent` creates parent paths before `STOR`.

`build_standard_upload_file_list()` mirrors the file order used by `PublishEngine` so manual `run_upload` and Admin “upload now” stay consistent.

---

## Related

- Stakeholder preview (Hebrew UI): `documentation/demos/product_icons_iconpark_preview.html`
- Publisher engine: `organic_market_agent/publisher/engine.py`
