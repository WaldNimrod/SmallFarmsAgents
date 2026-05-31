---
id: SFA-S003-P004-WP-CB-MIG2-LOD200
wp: SFA-S003-P004-WP-CB-MIG2 — Crop Data Model Expansion (13-topic taxonomy + 7 JMF field groups)
gate: L-GATE_E PASS → L-GATE_S (LOD200 → LOD400 pending)
status: DRAFT (LOD200) — opened 2026-05-31
author: team_100 (Claude Code, Chief Architect)
date: 2026-05-31
version: v0.1.0
canon_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
origin_ref: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/spec/OPEN_ISSUES.md
depends_on: SFA-S003-P004-WP-CB-MIG
---

# LOD200 — SFA-S003-P004-WP-CB-MIG2: Crop Data Model Expansion

> **Status: DRAFT / direction only.** Opened 2026-05-31 (team_00 directive, FULL adoption of the
> team_35 OPEN_ISSUES gap-analysis). This LOD200 fixes scope + intent; the executable LOD400 (Canon
> amendment v1.3.0 + Alembic migration + wiring) follows and routes to team_190 L-GATE_S (non-Claude, IR#1).
> The UI (WP-CB-1) is NOT blocked on this — it renders the new fields as "מוצע/proposed" until this lands,
> then lights them up automatically.

## 1. Why

The team_35 LOD300 study of the JMF MasterClass originals (גזר / מנגולד / חסה) surfaced a **canonical
13-topic structure** every sheet follows and **7 field groups the schema does not yet carry**. team_00
directed FULL adoption. Because the crop data layer is LOCKED (WP-CB-0 Canon + WP-CB-MIG LOD500_LOCKED),
this is a separate gated WP rather than an inline edit.

## 2. Scope

### 2.1 Adopt the 13-topic taxonomy (`CROP_TOPICS`) as canonical ordering
`זנים · מרווח ופריסה · ציוד וכיוונון · קרקע ודישון · הכנת ערוגה · זריעה/שתילה · השקיה · טיפוח ועישוב ·
מזיקים ומחלות · קציר · שטיפה ואחסון · רצף וחברה` (+ יבול/הכנסה for calc-facing values). Drives schema
ordering + UI section order in all depths.

### 2.2 Add 7 field groups
| # | Field(s) | Topic | Type / layer |
|---|----------|-------|--------------|
| 1 | `seeder_model` + `seeder_settings` | ציוד וכיוונון | identity cols (mostly exist — formalize) |
| 2 | `irrigation_type` (+ `drip_lines_per_bed`) | השקיה | T2 enum + int (crop_attribute) |
| 3 | `root_depth_class` | השקיה | T2 enum {shallow/medium/deep} |
| 4 | `common_pests` + `foliar_feeding_program` | מזיקים ומחלות (NEW) | text |
| 5 | `sale_unit` + `unit_size` | קציר | T2 enum + spec (also resolves design Q7 price-unit) |
| 6 | `labor_rate_harvest` + `labor_rate_wash` | קציר / שטיפה | int (units/hr; unlocks future labor-cost calc) |
| 7 | `plantings_per_season` + `harvest_weeks_span` | רצף וחברה | int |

### 2.3 Ratify `needs_summer_shade`
Israel-specific, 3 levels (30% / 40% / 50%) + "ללא הצללה". Already approved by team_00 (design ratification).

### 2.4 Fold in carried findings
- **F-CB1-UI-01:** align `field_policy.py` keys to canon for the 4 drifted fields
  (`avg_yield_per_bed_m`→`yield_per_bed_m`, `documented_price`→`price_documented`,
  `in_row_spacing_cm`→`spacing_in_row_cm`, `planting_season`→`season_window`/`sowing_months`) so the
  reconciler writes enrichment rows under canonical keys.
- **season_window data gap** (WP-CB-MIG L-GATE_V): 0 `crop_attribute` rows because `planting_season` was
  NULL for all varieties — backfill from JMF/PR sources.

## 3. Execution shape (for the LOD400)
Canon amendment v1.3.0 → Alembic head→next (new columns + enum domains) → `crop_attribute`/enrichment +
`field_policy` entries → `sfa_ingest_push` whitelist → PR backfill from the 37 MasterClass MDs
(`load_masterclass_sheets.py`). Builder: team_10 (Claude); validator: team_190 (non-Claude, IR#1).

## 4. Out of scope
UI rendering of these fields (owned by WP-CB-1 — already renders "מוצע" slots). The future labor-cost
calculator (`labor_rate_*` only unlocks it; not built here).
