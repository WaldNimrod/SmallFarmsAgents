# INBOX — nimrod-bio AssumptionField posts response (received 2026-05-30)

**From:** team_100 (nimrod-bio spoke) · **Re:** ROUTING_PROMPT_nimrod-bio_ASSUMPTION_POSTS_v1.0.0

Both placeholder posts CREATED + published (Hebrew/RTL, placeholder body + "תוכן מלא בקרוב").

| | germination_rate | bed_width |
|---|---|---|
| **Canonical URL (hard-coded in assumptions.py)** | `https://nimrod.bio/blog/seed-germination-rate/` | `https://nimrod.bio/blog/garden-bed-width-80cm/` |
| Temp preview URL | `http://nimrod-bio-2026.s887.upress.link/blog/seed-germination-rate/` | `http://nimrod-bio-2026.s887.upress.link/blog/garden-bed-width-80cm/` |
| Slug (permanent) | `seed-germination-rate` | `garden-bed-width-80cm` |
| Post ID | 1051 | 1052 |

**Key correction:** nimrod-bio permalinks are `/blog/%postname%/` — URLs carry a **`/blog/`** prefix (my routing prompt omitted it). `assumptions.py` updated accordingly.

**Slug permanence CONFIRMED:** temp→main is an in-place domain swap on the same WP install; `/blog/<slug>/` is identical before/after — no slug change, no redirect affects these. nimrod-bio will flag SFA before any manual rename of post 1051/1052.

**Status now:** the canonical `nimrod.bio/blog/...` form goes live at the domain cutover (nimrod-bio P005-WP002, deferred per team_00). Until then, preview via the temp URLs. Content is placeholder; real content is a later content-precision task. No URL rewrite needed on cutover.

**Action taken (SFA):** `organic_market_agent/crop_book/assumptions.py` post_urls set to the `/blog/` canonical form for germination_rate + bed_width.
