---
id: SFA-S003-P004-WP-CB-FROST-DATA
gate: L-GATE_E (registered — future / pipeline idea)
status: REGISTERED — not for execution now; team_00 approved interim values 2026-06-07
author: team_100
created: 2026-06-07
relates_to:
  - SFA-S003-P004-WP-CB-CALC (frost #11 region picker consumes this data)
  - SFA-S003-P004-WP-CB-WATER (reuses the region axis)
trigger: "team_00 approved the interim Israel frost-region date table for ship; flagged the data itself for future refinement."
---

# REGISTER — WP-CB-FROST-DATA (Israel frost-region data refinement)

**Idea (pipeline / future implementation).** The calculator's frost window (#11) ships on an **interim, team_00-approved** Israel region → frost-date table (`frost_regions.json`, 5 regions). The *data quality* is acknowledged as coarse and is registered here for a future refinement pass.

## Interim values approved by team_00 (2026-06-07) — ship as-is
| key | label_he | frost_free | last_spring_frost | first_autumn_frost |
|---|---|---|---|---|
| `coastal` ⭐ | שפלת החוף | yes | — | — |
| `judean_hills` | הרי ירושלים | no | 25-03 | 25-11 |
| `jordan_valley` | עמק הירדן | yes | — | — |
| `northern_negev` | הנגב הצפוני | no | 10-03 | 05-12 |
| `upper_galilee` | הגליל העליון | no | 05-04 | 15-11 |

## Future refinement scope (when prioritized)
- Validate last/first-frost dates against agronomic / meteorological sources (IMS climate normals, extension data) — replace the round interim dates with sourced percentiles (e.g. 10%/90% frost-risk dates).
- Consider finer granularity (more regions / micro-climates) and an elevation factor.
- Add provenance per region (source + confidence), consistent with the crop-book provenance model.
- Revisit `frost_free` classification per region against records.

## Status
**Not for execution now.** Frost #11 is Phase B-later; the interim table unblocks its ship. This refinement is a separate, lower-priority data-quality WP — activate on team_00 priority. No code/data change in registering it.
