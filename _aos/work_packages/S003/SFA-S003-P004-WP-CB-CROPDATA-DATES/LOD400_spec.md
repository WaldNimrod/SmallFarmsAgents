---
id: SFA-S003-P004-WP-CB-CROPDATA-DATES-LOD400
wp: SFA-S003-P004-WP-CB-CROPDATA-DATES — crop date-field classification (guided-entry tool + delivery plumbing)
gate: L-GATE_D (design) → ready for L-GATE_BUILD on team_00 go
status: SPEC (decision-complete; entry-tool visuals pending team_35 mockups, mandate §5)
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50
depends_on:
  - SFA-S003-P004-WP-CB-MOBILE (closed)
gates: SFA-S003-P004-WP-CB-CALC Phase B-later
refs:
  - _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
  - _COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md
  - organic_market_agent/crop_book/assumptions.py (HARDINESS_OFFSET classes)
---

# LOD400 — WP-CB-CROPDATA-DATES

> **Rescoped 2026-06-07** after a direct measurement of the PG SSoT (`oma-postgres`, 70 crops). The supposed "date-data gap" largely collapsed; what remains is two **categorical** classifications + a small conditional numeric + the server delivery plumbing. This WP **gates WP-CB-CALC Phase B-later only** (not B-now).

## 1. Measured baseline (2026-06-07, 70 crops, PG SSoT)
| Field | Home table | Coverage | Disposition |
|---|---|---|---|
| `days_to_maturity` | crop_field_enrichment (numeric) | 66/70 | ✅ already ~complete — out of scope |
| `harvest_window_max_days` | crop_field_enrichment (numeric) | 68/70 | ✅ already ~complete — out of scope |
| `succession_interval_weeks` | (was crop_field_enrichment) | 19/70 | ❌ **DROPPED** — now DERIVED in the calc engine `round(harvest_window_max_days/7)`; עידן's empirical cadence is operational (corr 0.10 with biology), not used |
| `planting_method` | crop_attribute (categorical) | 31/70 | 🎯 **classify** the remaining ~39 |
| `frost_tolerance_class` | crop_attribute (categorical) | 37/70 | 🎯 **classify** the remaining ~33 |
| `days_in_nursery` | crop_field_enrichment (numeric) | 8/9 of known transplants | 🎯 fill only for transplant/both crops revealed by planting_method |

**Schema note:** in the **PG SSoT** categoricals live in `crop_attribute (attribute_name, value_canonical, …)`, numerics in `crop_field_enrichment (field_name, value_best, …)`; **both key on `variety_id`** (join to crop via `crop_varieties`). Per-crop = the default variety (`name_en IS NULL`). **⚠ The MySQL delivery mirror exposes these as `attribute_key`/`crop_id`** (and `field_name`/`crop_id`) — the calc controller (`HubController::calc`) and `CropBookViewController` query `attribute_key` + `crop_id`, NOT the SSoT names. Keep both schemas straight when wiring SSoT writes vs mirror reads.

## 2. Scope
**In:** (a) a **guided classification tool** for team_00 to fill `planting_method` + `frost_tolerance_class` (+ conditional `days_in_nursery`); (b) add a **`both` (גם וגם)** canonical value to `planting_method`; (c) the **server-side delivery plumbing** so the categoricals reach the calculator client. **Out:** `days_to_maturity`/`harvest_window_max_days` (already complete); `succession_interval_weeks` (calc derivation); the broader provenance coverage (separate WP).

## 3. The guided-entry tool (owner-only)
A **per-crop question-sequence** optimized for **speed** (Nimrod fills ~40 crops in one sitting):
- For each crop (iterate the ~39 unclassified): ask
  1. `planting_method` ∈ { זריעה ישירה `direct_seed` · שתיל `transplant` · **גם וגם `both`** · פקעת `seed_tuber` · ייחור `slip` }.
  2. `frost_tolerance_class` ∈ the `HARDINESS_OFFSET` classes (very_hardy/hardy/semi_hardy/tender/very_tender/warm) — web-research-friendly; allow "skip/unknown".
  3. **If** planting_method ∈ {transplant, both} **and** `days_in_nursery` missing → ask it (number, days).
- Persist each answer to `crop_attribute` (categoricals) / `crop_field_enrichment` (days_in_nursery) with provenance `winning_source_class` = owner/expert tier; idempotent upsert (keyed on variety_id + attribute_name/field_name).
- Progress indicator (X/39), keyboard-first, one crop per screen.
- **Visual design = team_35** (mandate §5). This spec fixes the data model + flow; mockups fix the look.

> **Canonical-value change:** adding `both` to `planting_method` — confirm the calc `_is_transplant()` helper treats `both` as transplant-capable (it currently matches `transplant*`/`greenhouse*`, `calculators.py:132-135`); extend to include `both`.

## 4. Server delivery plumbing (shared with WP-CB-CALC §5)
The calculator client cannot consume these today:
1. `HubController::calc()` whitelist (`HubController.php:147-156`) is numeric-only → add the numeric date fields; **add a `crop_attribute` query** for `planting_method`+`frost_tolerance_class`.
2. Emit categoricals via a **non-numeric channel** (`window.SFA_CROP_BOOK_TXT[slug]`) — the JS flattener drops non-numerics (`crop-book-v1.js:635`).
3. Mirror parity: ensure the publisher (`sfa_ingest_push.py`) pushes the categorical attributes to the live MySQL mirror (verify against `IngestEnrichmentMirrorTest`).

## 5. Acceptance criteria
1. `planting_method` + `frost_tolerance_class` coverage materially raised (target: all crops the calculator exposes, or an explicit skip/unknown).
2. `both` value supported end-to-end (data → `_is_transplant` → calc branch).
3. `days_in_nursery` present for every transplant/both crop (or explicit unknown).
4. The categoricals + date numerics reach `window.SFA_CROP_BOOK(_TXT)` — proven by a route test (RICH payload).
5. Idempotent re-run (no dupes). PHP suite green; `validate_aos` 0 FAIL.
6. Entry tool matches the approved team_35 mockup; team_50 QA.

## 6. Risks
| Risk | Mitigation |
|---|---|
| Mis-classification by the owner | Allow edit/revisit; show the current value; web-research hints for frost class. |
| `both` not honored in calc branching | Extend `_is_transplant`; parity test for a `both` crop. |
| Categoricals still dropped client-side | Non-numeric channel + route-test assertion. |
| Writing to crop_attribute when DB online | API-only structured mutation (IR#7/ADR034) — the tool writes via the hub API, not direct SQL. |

## 7. Dependencies & sequencing
Independent of WP-CB-CALC Phase A + B-now. **Gates WP-CB-CALC Phase B-later.** Run the guided tool in parallel with CALC Phase A/B-now build. team_10 builds, team_50 validates.
