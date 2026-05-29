---
id: SFA-S003-P002-WP-UI-patch03-LOD400
wp: SFA-S003-P002-WP-UI-patch03 — Crop-book detail UX + agronomic data surfacing
gate: L-GATE_B (LOD400)
status: READY_FOR_BUILD
author: team_100 (Chief Architect)
date: 2026-05-29
version: v1.0.0
depends_on: [SFA-S003-P002-WP-UI-patch02]
activation: team_00 grant 2026-05-29 (crop-book detail review on live sfa.nimrod.bio)
orchestration:
  build: "team_10 (Claude Sonnet sub-agents) — frontend + ingest-data"
  qa: "team_50 (Claude Haiku)"
  validation: "team_190 (non-Claude — IR#1)"
evidence: _COMMUNICATION/team_100/SFA-S003-CROPBOOK-PROD-DATA-GAP/INCIDENT_v1.0.0.md
---

# LOD400 — WP-UI-patch03: Crop-book detail UX + agronomic data surfacing

## 0. Context (live findings 2026-05-29)
The crop-book IS populated on sfa.nimrod.bio (70 crops / 367 varieties — pushed
via the ingest API; `/crop-book/table/` renders all). But the **crop/variety
detail page** has three defects (team_00 review of `/crop-book/arugula`):
1. **Layout** — content hugs a narrow right column; the left ~third is empty; poor use of the central panel.
2. **Typography** — variety-grid labels/values too small to read.
3. **Variety data shows "—"** — two causes: (a) DTM key mismatch (ingest sends `days_to_maturity`, `variety_row.php` reads `dtm_days`); (b) the grid shows product fields (color/taste/shape/yield/resistance) that the **agronomic** data model does not have, while the rich C1–C6 enrichment (DTM, germination, spacing, soil pH, storage, NPK) is **not piped** to the detail.

## 1. Decisions (team_00 2026-05-29)
- **Surface the real agronomic data** in the crop/variety detail; drop the
  unsourced product fields (color/taste/shape).
- **Delta highlight**: color-mark each non-default variety's value where it
  **differs from the default variety's** value (the "delta" the user wants).
- Scope = **ALL**: layout + typography + variety-data + landing-shows-crops.

## 2. Agronomic field set to surface (from `crop_field_enrichment` vocab)
Per crop/variety, show (when present; omit/—-collapse when absent):
`days_to_maturity` (DTM), `germination_temp_c_min/opt/max`, `in_row_spacing_cm`,
`rows_per_bed`, `soil_ph_target`, `storage_temp_c_min/max`, `storage_life_days`,
`yield_per_m2_kg`, `nutrient_removal_n/p/k_kg_ha`, `harvest_window_max_days`,
`seeds_per_gram`. (Source of truth: oma-postgres `crop_field_enrichment` per variety_id.)

## 3. Scope of work
### 3.1 Data contract (ingest) — `organic_market_agent/publisher/sfa_ingest_push.py`
- Extend `_fetch_crop_varieties` to LEFT JOIN/pivot `crop_field_enrichment`
  (field_name → value_best) per variety into `payload_json` under an `agronomy`
  object (the §2 fields). Keep existing keys. Idempotent.
- Re-push `crop_varieties` (and `crops` if needed) from the Mac (head 057) to the
  live ingest API after the contract change.

### 3.2 Detail controller — `sfa_delivery/app/Controllers/CropBookViewController.php`
- In `detail()`, map `payload_json.agronomy` onto each variety; alias
  `days_to_maturity`→`dtm_days`. Compute per-variety **delta flags vs the default
  variety** (which fields differ) → pass `agronomy` + `delta` map to the template.

### 3.3 Variety row macro — `sfa_delivery/templates/macros/variety_row.php`
- Replace the color/taste/shape grid with the §2 agronomic fields (only those present).
- Add `.cb-var__val--delta` class on cells that differ from the default variety
  (CSS color highlight). Default variety shown as the baseline.

### 3.4 Detail layout — `sfa_delivery/templates/pages/book_crop.php` + `public_assets/css/hub.css`
- Use the central/main panel (full content width); remove the empty-left waste; sensible RTL hierarchy.
- Typography: readable sizes for variety-grid labels + values (CSS).
- Delta highlight CSS (`.cb-var__val--delta`).

### 3.5 Landing — `sfa_delivery/app/Controllers/CropBookViewController.php::entry` + `pages/book_entry.php`
- Surface crops on `/crop-book/` (e.g., featured / all crops grid via `gj-cropcard`),
  not only the nav hub. Query crops + render cards (reuse `crop_card.php`).

## 4. Acceptance Criteria
| AC | Check | Pass |
|----|-------|------|
| AC-U3-01 | ingest variety payload carries `agronomy` (DTM, germination, spacing, soil pH, storage, NPK, yield) | dry-run shows fields |
| AC-U3-02 | `/crop-book/arugula` variety rows show real agronomic values (≥3 non-empty for default) | live render |
| AC-U3-03 | DTM no longer "—" when data exists (key map) | live render |
| AC-U3-04 | non-default variety values differing from default are color-highlighted | render + CSS class present |
| AC-U3-05 | detail uses central panel; no large empty left column | visual/CSS rule |
| AC-U3-06 | variety-grid typography readable (computed font-size ≥ baseline) | CSS |
| AC-U3-07 | `/crop-book/` landing shows crop cards (≥1 crop) | live render |
| AC-U3-08 | unsourced product fields (color/taste/shape) removed (no perpetual "—") | grep template |
| AC-U3-09 | `php -l` clean; `composer test` 0 new failures (53+); render harness for variety_row | tests |
| AC-U3-10 | `validate_aos.sh` 0 FAIL; no engine/reconciler change; no www.nimrod.bio | run + diff |
| AC-U3-11 | deployed to sfa.nimrod.bio (server route); live smoke 200 + agronomy visible | curl |

## 5. Orchestration
- Sonnet A (data): §3.1 ingest contract + dry-run.
- Sonnet B (frontend): §3.2–§3.5 controller + macro + templates + CSS + tests.
- team_100: integrate, re-push data (Mac→ingest), deploy (waldhomeserver→s1240), verify.
- team_50 (Haiku) QA; team_190 (non-Claude) L-GATE_V; then ADR042 closure.

## 6. Out of scope / notes
- No engine/reconciler/schema change in oma-postgres (data already exists).
- **Durability caveat carried from the incident**: production server oma-postgres
  is at head 034 with no crop schema, so the daily cron cannot maintain crop data;
  this WP re-pushes from the Mac. Canonical pipeline alignment (server DB) remains
  a separate follow-up (tracked in INCIDENT_v1.0.0).
- Watercolor crop icons (WP-UI-patch02 Phase 2) remain separate.
