# M10.3 Task 1 — HTML analysis notes (SRC027 / SRC028)

**Date:** 2026-04-04  
**Team:** 10  

## SRC027 — eranorgani.co.il

- **Assumption:** WooCommerce or similar product loop with `div.product` / `article.product`, titles in `h2`/`h3`, prices in `.price` / `.woocommerce-Price-amount`.
- **Parser default:** [`organic_market_agent/parsers/eranorgani.py`](../../../organic_market_agent/parsers/eranorgani.py) with overrides from `source_fetch_profiles.selector_profile`.
- **Follow-up:** Validate pagination and category URLs on live site; extend `entry_url` or add secondary fetch profiles if catalog is split.

## SRC028 — shop.tamari-farm.co.il

- **Assumption:** WooCommerce listing: `li.product`, `h2.woocommerce-loop-product__title`, `span.price`.
- **Parser default:** [`organic_market_agent/parsers/tamari.py`](../../../organic_market_agent/parsers/tamari.py).
- **Follow-up:** Confirm theme-specific classes after first successful `run_ingestion`; tune `selector_profile` JSON in DB without code deploy if possible.
