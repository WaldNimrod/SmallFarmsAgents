---
id: UNMAPPED_CROPS_SFA-S003-P002-WP-C1_v1.0.0
wp: SFA-S003-P002-WP-C1
from: team_10 (sfa_build)
date: "2026-05-27"
status: INFORMATIONAL
---

# UNMAPPED_CROPS — WP-C1 v1.0.0

Hebrew labels from L01/L03/L04/L36 that could not be mapped via `IL_CROP_MAP`
(10 of 107 distinct names = 9.3% unmapped; **90.7% mapped**, AC-C1-05 PASS).

## Unmapped source labels (require team_00 if new baseline crops needed)

| Source label | Notes |
|--------------|-------|
| `1023` | L04 artifact row — skipped |
| `חזרת` | Horseradish — no baseline |
| `חרדל` | Mustard — no baseline |
| `יריחו` | Unknown label |
| `כרוב קאייל` | Collard — no baseline |
| `כרוב קולרד` | Collard spelling variant |
| `ניתן להוסיף` | Worksheet placeholder |
| `סה"כ שטח גידול` | Summary row |
| `ריבס` | Unknown / typo |
| `תלתן` | Clover (cover crop, not market veg baseline) |

## Mapped but no DB baseline (skipped at ingest — 21 labels)

These resolve through `IL_CROP_MAP` but target `crops.name_he` values not yet in the
57-crop baseline: e.g. `אבטיח`, `בטטה`, `כרובית`, `תפוח אדמה`, `תירס`, `פול`,
`ציקוריה`, `חיטה`, `חמניה`, `תבלינים`, `שומשום`, `סויה`, `אדממה`, `חומוס`, etc.

**Action:** No team_00 blockers for WP-C1 build. Future baseline expansion (Team 20)
can unlock additional planting-calendar rows without importer changes.
