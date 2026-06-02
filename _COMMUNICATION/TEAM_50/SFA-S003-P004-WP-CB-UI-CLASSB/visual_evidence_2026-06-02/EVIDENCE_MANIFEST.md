# Visual Evidence Manifest — WP-CB-UI-CLASSB Visual QA 2026-06-02

## Environment
- Local PHP server: http://127.0.0.1:8099 (SQLite empty-state DB)
- Design board: http://127.0.0.1:8097/Board-B-Hub-Market-Search-Community-About-Account.html
- QA session: Claude Code (team_50), 2026-06-02

## Screenshot IDs (captured via Claude-in-Chrome browser tool)
All screenshots captured at desktop viewport (1456×835) unless noted.

| ID | Surface | Type |
|----|---------|------|
| ss_9085575f4 | Hub / (`/`) | live desktop |
| ss_2649lh89d | Hub / Design Board hub-home frame | design reference |
| ss_3324rzoj3 | Market list (`/market/`) | live desktop |
| ss_97198oqo7 | Market detail (`/market/tomato`) | live desktop |
| ss_7472vmvkj | Search results match (`/search?q=עגב`) | live desktop |
| ss_9321dvv4m | Search no-match (`/search?q=xyz`) | live desktop |
| ss_93047j491 | Community (`/community`) | live desktop |
| ss_1253fplvt | About / Tiers (`/about`) | live desktop |
| ss_34676o3qj | Account (`/account`) | live desktop |
| ss_6451kea0y | Design Board — shell/desktop + overview | design reference |

## Data status
Pages QA'd with SQLite in-memory DB (empty-state). 
Test product "עגבנייה" (slug: tomato, 0 prices) added for market detail QA.
No crops in DB for search crop results.
