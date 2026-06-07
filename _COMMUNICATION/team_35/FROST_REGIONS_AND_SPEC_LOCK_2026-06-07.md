---
id: SFA-S003-P004-WP-CB-CALC-FROST-REGIONS
from: team_100 (calc engine)
to: team_35 (design/mockups)
re: canonical frost-region list + JSON asset spec; presentation spec LOCKED (1 residual)
created: 2026-06-07
status: frost regions = DRAFT pending team_00 approval; everything else LOCKED
---

# Frost regions + spec-lock — for team_35

## 1. Presentation spec is LOCKED (engine side), with ONE residual
All result shapes, badges, anchor behavior, no-data, channel (`SFA_CROP_BOOK_TXT`), relabels — **locked** to your delivered mockups and integrated into the LOD400.
**Residual: #13 `compare` → please iterate to a SELECTED-CROP BASKET** (team_00 decision): step-2 becomes a multi-select basket (2–6 crops) + chips; result ranks only the basket; copy "בחרו גידולים להשוואה". The "all crops" version is superseded.

## 2. Canonical frost-region list (frozen keys) — for the picker
Use these **keys** so the picker `<option>`s match the engine. **Labels final; dates are DRAFT pending team_00 approval** (frost #11 is B-later, not blocking).

| key (frozen) | label_he | frost_free | last_spring_frost (DRAFT) | first_autumn_frost (DRAFT) |
|---|---|---|---|---|
| `coastal` ⭐default | שפלת החוף | yes | 01-02 | 31-12 |
| `judean_hills` | הרי ירושלים | no | 25-03 | 25-11 |
| `jordan_valley` | עמק הירדן | yes | 01-02 | 31-12 |
| `northern_negev` | הנגב הצפוני | no | 10-03 | 05-12 |
| `upper_galilee` | הגליל העליון | no | 05-04 | 15-11 |

(`frost_free` regions ⇒ the calculator shows an effectively unconstrained window — honest, not a fake date.)

## 3. JSON asset spec (engine will ship this)
Path: `sfa_delivery/public_assets/data/frost_regions.json` (loaded by the picker; keys above frozen):
```json
{
  "default": "coastal",
  "regions": [
    {"key":"coastal","label_he":"שפלת החוף","frost_free":true,"last_spring_frost":"01-02","first_autumn_frost":"31-12"},
    {"key":"judean_hills","label_he":"הרי ירושלים","frost_free":false,"last_spring_frost":"25-03","first_autumn_frost":"25-11"}
  ]
}
```
Dates are `DD-MM` (year-agnostic; the engine applies them to the planning year). The picker reads `label_he`; the engine reads `key` + the two dates.

## 4. Net
Iterate **#13 basket** only. Wire the region picker against the keys above. Engine ships `frost_regions.json` once team_00 approves the dates. Route iterations via `_COMMUNICATION/team_100/`.
