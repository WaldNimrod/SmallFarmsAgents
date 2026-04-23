# Verification & sign-off — Public market page (nimrod.bio)

```yaml
from: Team 30 (Frontend Implementation) + build verification
date: 2026-04-17
scope: Responsive UI + live artifact checks (post-deploy)
canonical_url: https://www.nimrod.bio/smallfarmsagent/
```

## Executive summary

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Final page loads (HTTP) | **PASS** | `curl -sI` → 200 on `/smallfarmsagent/` |
| WordPress embeds `public_report_body.html` with responsive markup | **PASS** | `sfa-product-card` present on page (cache-busted URL); source fragment contains `sfa-report-mobile-cards` |
| Shared CSS deployed and reachable | **PASS** | `sfagent-base.css` → HTTP 200, `last-modified` aligned with deploy |
| `manifest.json` / `public_report.json` consistent | **PASS** | Schema 2.0, `staleness_level` `current`, counts match |
| **Business “current market” prices/dates** | **NOT VERIFIED (data source)** | Live `report_date` is **2099-08-12** — this matches the **Docker-seeded publish** used when `.env` `DATABASE_URL` did not satisfy the publish gate, not necessarily the production pipeline’s latest window. Re-publish from the **authoritative DB host** after a successful ingest for real-world currency. |

**Conclusion:** We **approve the responsive/UI fix** as correctly deployed and visible on the final URL **with proof below**. We **do not** certify that the **numeric report content** reflects live farm-market reality until publish is run against the **production pipeline database** meeting `PublishEngine` community-source rules.

---

## 1. Live manifest (`manifest.json`)

Fetched: `https://www.nimrod.bio/wp-content/uploads/market/manifest.json`

Observed (material fields):

- `schema_version`: `2.0`
- `last_published_at`: `2026-04-17T00:48:22.913920+00:00` (UTC)
- `report_date`: `2099-08-12`
- `product_count`: `1`
- `staleness_level`: `current`
- `community_sources`: `2`
- `window_start_date` / `window_end_date`: `2099-08-06` … `2099-08-12`

**Interpretation:** Internal consistency is **PASS** (staleness vs `last_published_at`). The **2099** window indicates **test/seed data** from the publish path documented in `CHANGELOG.md`, not an assertion about today’s agricultural season.

---

## 2. Live `public_report.json` (sample)

Fetched: `https://www.nimrod.bio/wp-content/uploads/market/public_report.json`

- `generated_at`: matches manifest generation time (same publish run).
- `products[0]`: e.g. `canonical_name_he` עגבנייה, `avg_price` 12.0, `sample_size` 2 (illustrative of seeded run).

---

## 3. Responsive markup (final user page)

**Source file (CDN):** `https://www.nimrod.bio/wp-content/uploads/market/public_report_body.html`

- Contains `sfa-report-mobile-cards` (mobile card layout).
- Contains multiple `sfa-product-card` nodes (expected for product rows + structure).

**Themed page:** `https://www.nimrod.bio/smallfarmsagent/?v=<cache-bust>`

- `sfa-product-card` count **> 0** (verified via `grep -c` after cache-bust).  
- **Note:** Full-page caching may serve an older HTML without query string; use cache-bust or ezCache purge after deploy when validating.

---

## 4. Child theme CSS

`https://www.nimrod.bio/wp-content/themes/flatsome-child/sfagent-base.css`

- HTTP **200**, `content-type: text/css`, `last-modified` present.

---

## 5. System “running correctly” (scope clarification)

- **Public static artifacts + WP shortcode path:** Verified end-to-end (files on host, page renders, CSS loads).
- **Full OrganicMarketAgent stack** (ingestion, scheduler on server, admin UI): **Out of scope** for this sign-off; no remote health endpoint was asserted on `nimrod.bio` for the Python hub.

---

## Required follow-up for “real” data (operator)

1. On the machine with **production** `DATABASE_URL` and a **valid rolling window** (≥ 2 community sources):  
   `python -m organic_market_agent run_publisher --output-dir output/public`
2. `python -m organic_market_agent run_upload --output-dir output/public`
3. Re-check `manifest.json` for `report_date` / `window_*` aligned with real operations.

---

*This document is evidence-backed; commands were run from the development environment against public URLs on 2026-04-17.*
