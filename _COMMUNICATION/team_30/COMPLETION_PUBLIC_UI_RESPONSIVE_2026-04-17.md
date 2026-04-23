# Team 30 — Public market report responsive UI

```yaml
from: Team 30 (Frontend Implementation)
gate: (post-implementation — submit to Team 50 for QA)
work_package: Public UI responsiveness (SFA)
date: 2026-04-17
```

## Canonical URL (what users actually open)

The **end-user public page** is the **WordPress page** at **`https://www.nimrod.bio/smallfarmsagent/`** (path matches site slug; `www` may redirect). It is **not** primarily `public_report.html` served alone.

**How it is built:** `functions.php` shortcode `[sfagent_market_report]` outputs the contents of **`wp-content/uploads/market/public_report_body.html`**. [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py) enqueues [`sfagent-base.css`](../../organic_market_agent/publisher/static/sfagent-base.css) from the Flatsome child theme on that page. So **responsive UX for `/smallfarmsagent/`** = **body fragment + `sfagent-base.css`**, deployed via FTPS (uploads + child theme when CSS changes).

**Standalone** `public_report.html` is still generated for a direct static URL under `uploads/market/`; same table/card logic for parity, but the **themed** experience is the WP page above.

---

## Scope

- **WordPress body fragment (primary):** [`organic_market_agent/publisher/templates/public_report_body.html`](../../organic_market_agent/publisher/templates/public_report_body.html) — mobile **product cards** with full metrics (including standard deviation); desktop keeps the full **table**.
- **Standalone static report (secondary):** [`organic_market_agent/publisher/templates/public_report.html`](../../organic_market_agent/publisher/templates/public_report.html) — same responsive pattern; styles remain in the page `<style>` block (self-contained upload to `uploads/market/`).
- **Shared theme CSS:** [`organic_market_agent/publisher/static/sfagent-base.css`](../../organic_market_agent/publisher/static/sfagent-base.css) — new `.sfa-report-desktop` / `.sfa-report-mobile-cards` / `.sfa-product-card*` rules; removed global `.sfa-hide-mobile` suppression (was hiding the std dev column on narrow viewports).

## Governance note (inline CSS / script)

Team 30 contract prefers no inline `<style>` / `<script>`. SFA **M8** allows page-specific inline styles in the publisher fragment; tooltip behavior remains inline script. Standalone `public_report.html` does not load the child theme — **scoped exception:** embedded stylesheet in one file for FTPS-only deployment. New layout rules for WP are in **Layer 2** (`sfagent-base.css`) where possible.

## Production deploy checklist

1. Regenerate artifacts: `python -m organic_market_agent run_publisher [--output-dir output/public]`
2. Upload market files: `python -m organic_market_agent run_publisher --upload` or `run_upload` (requires `.env` FTPS credentials).
3. **If `sfagent-base.css` changed:** deploy to child theme, e.g. `python3 scripts/wp_shortcode_install.py` (uploads `sfagent-base.css` to `flatsome-child/`).
4. **Verify the real page:** open **`https://www.nimrod.bio/smallfarmsagent/`** (or your `UPRESS_PUBLIC_BASE` + slug) and confirm mobile cards / table (hard-refresh; CDN may cache). Optionally `curl` the page and grep for `sfa-report-mobile-cards` after deploy.

## Verification evidence

Local checks may use `run_viewer` on `output/public/public_report.html` for quick iteration; **acceptance** is the **WordPress page** after upload.

Local static viewer (optional): `python3 -m organic_market_agent run_viewer --dir output/public --port 8870 --host 127.0.0.1` → `http://127.0.0.1:8870/public_report.html`.

| Viewport | File |
|----------|------|
| ~390×844 CSS px (mobile) | [`screenshots/team30-public-report-390w.png`](screenshots/team30-public-report-390w.png) |
| 1024×768 (desktop table) | [`screenshots/team30-public-report-1024w.png`](screenshots/team30-public-report-1024w.png) |

**Production deploy (2026-04-17):** Full cycle: `run_upload` (8 files → `wp-content/uploads/market/`) + `scripts/wp_shortcode_install.py` (FTPS `sfagent-base.css`, shortcode/enqueue verified, **WP REST** confirmed page exists — e.g. id 91325). [`config.py`](../../organic_market_agent/utils/config.py) now loads `.env.upress` so `UPRESS_WP_ADMIN_*` are visible to the script (previously only in `.env`).

**Publish data caveat:** `run_publisher` used **seeded Docker** when `.env` `DATABASE_URL` does not meet the 2-community-source gate. For live prices/dates, run publish+upload on the pipeline host after a valid ingest window.

## Handoff

- Submit **QA review request** to Team 50 per `_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md` when ready.
