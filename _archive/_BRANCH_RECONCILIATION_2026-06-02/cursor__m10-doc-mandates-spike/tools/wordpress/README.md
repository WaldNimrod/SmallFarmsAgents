# WordPress snippets (reference)

| File | Purpose |
|------|---------|
| [`sfagent_market_report_shortcode.php`](sfagent_market_report_shortcode.php) | `[sfagent_market_report]` + `sfagent_market_icon_url()` for IconPark SVGs under `uploads/market/icons/iconpark/` |

**Install / upgrade:** run from repo root (FTPS + credentials):

```bash
python3 scripts/wp_shortcode_install.py
```

The installer merges this snippet into `flatsome-child/functions.php` and deploys `sfagent-base.css`.

For manual installs, copy the PHP **without** the leading `<?php` if your `functions.php` already opens with it.
