---
id: URL_AUDIT_SFA-S003-P002-WP-C4_v1.0.0
from: team_10 (sfa_build)
date: 2026-05-27
wp: SFA-S003-P002-WP-C4
---

# URL Audit — WP-C4 Web Sources

Download harness: `scripts/download_web_sources.py` (run 2026-05-27).

**Result: 10 / 14 sources cached successfully (71%)** — meets AC-C4-02 (≥70%).

| Source key | URL | HTTP | Cached path | Notes |
|------------|-----|------|-------------|-------|
| uc_anr_germination | https://ucanr.edu/sites/default/files/2017-11/164220.pdf | 200 | `data/external_sources/web/uc_anr_germination/source.pdf` | OK |
| purdue_germination | https://ag.purdue.edu/.../ho-186-w.html | 200 | `.../purdue_germination/source.html` | OK (cross-val) |
| osu_frost_tolerance | https://extension.oregonstate.edu/news/plant-cold-hardy-vegetables-now-spring-harvest | 200 | `.../osu_frost_tolerance/source.html` | Alt URL (original chart 404) |
| csu_planting_guide | https://extension.colostate.edu/resource/vegetable-planting-guide/ | 200 | `.../csu_planting_guide/source.html` | OK (cross-val) |
| umn_field_planning | https://extension.umn.edu/vegetable-growing-guides-farmers/... | 200 | `.../umn_field_planning/source.html` | OK (cross-val) |
| umd_soil_ph | https://extension.umd.edu/.../B-1.pdf | 200 | `.../umd_soil_ph/source.pdf` | OK |
| ne_veg_guide_nutrients | https://nevegetable.org/cultural-practices/removal-nutrients-soil | 200 | `.../ne_veg_guide_nutrients/source.html` | OK |
| fao_fertilizer_use | https://www.fao.org/3/i0058e/i0058e.pdf | 200 | `.../fao_fertilizer_use/source.pdf` | Redirect chain OK |
| il_moa_garden_guide | https://www.moag.gov.il/vic/tochniyot/DocLib/gan.pdf | 403 | — | Gov.il blocks bot; **JSON extract fallback** |
| shaham_extension | https://www.moag.gov.il/vic/shaham/Pages/default.aspx | 403 | — | DNS/403; **JSON extract fallback** |
| vital_seeds_count | https://vitalseeds.co.uk/.../seeds-per-gram/ | 200 | `.../vital_seeds_count/source.html` | OK |
| osborne_seed_count | https://www.johnnyseeds.com/growers-library/seed-planting-schedule.html | 404 | — | **Vital-only + JSON fallback** |
| uf_ifas_companion | https://edis.ifas.ufl.edu/publication/HS389 | 410 | — | **JSON extract fallback** |
| uc_davis_postharvest | https://extension.k-state.edu/.../storage-guidelines-UCDavis.pdf | 200 | `.../uc_davis_postharvest/source.pdf` | OK |

Machine-readable summary: `download_run_summary.json` (same directory).
