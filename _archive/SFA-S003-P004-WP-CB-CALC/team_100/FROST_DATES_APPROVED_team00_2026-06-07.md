---
id: SFA-S003-P004-WP-CB-CALC-FROST-APPROVED
from: team_35 (relaying team_00)
to: team_100 (calc engine)
re: team_00 APPROVED the interim frost-date table — ship frost_regions.json
in_reply_to: SFA-S003-P004-WP-CB-CALC-FROST-REGIONS
created: 2026-06-07
status: APPROVED (interim) — refinement registered separately
---

# Frost dates APPROVED (interim) — you may ship `frost_regions.json`

**team_00 approved (2026-06-07)** the DRAFT frost-region date table **as-is for ship**. The keys/labels/dates in your `FROST_REGIONS_AND_SPEC_LOCK` are GO — emit `sfa_delivery/public_assets/data/frost_regions.json` with those values; no change needed.

- The mockup region picker is wired to your frozen keys (`coastal`⭐ default … `upper_galilee`) and reads the JSON shape you specified (`default` + `regions[]`, `DD-MM`). frost_free regions render an honest open-window (no fake date).
- **Data quality is acknowledged as interim.** team_00 directed that refinement be tracked for the future, not done now → registered as **`SFA-S003-P004-WP-CB-FROST-DATA`** (`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-FROST-DATA/REGISTER.md`): validate dates vs. agronomic/meteorological sources, finer granularity, per-region provenance. Not for execution until team_00 prioritizes.

**Net:** no design or data blockers remain on frost. Presentation residuals are all closed (see `MOCKUP_ITERATION_team35_2026-06-07_v1.1.0.md`).
