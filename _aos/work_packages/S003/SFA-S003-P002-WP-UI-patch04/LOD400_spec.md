---
id: SFA-S003-P002-WP-UI-patch04-LOD400
wp: SFA-S003-P002-WP-UI-patch04 — Crop-book completeness + global navigation overhaul
gate: L-GATE_B (LOD400)
status: READY_FOR_BUILD
author: team_100 (Chief Architect)
date: 2026-05-29
version: v1.0.0
depends_on: [SFA-S003-P002-WP-UI-patch03]
activation: team_00 live review 2026-05-29 (6 defects) + design decisions (nav model, detail IA)
orchestration:
  build: "team_10 (Claude Sonnet sub-agents) — A=ingest data, B=nav/links/landing, C=crop detail"
  qa: "team_50 (Claude Haiku)"
  validation: "team_190 (non-Claude — IR#1)"
---

# LOD400 — WP-UI-patch04: Crop-book completeness + global navigation

## 0. Context (team_00 live review 2026-05-29) — 6 defects
1. **Broken links everywhere** — 72 internal 404s. Dominant: market↔crop-book cross-links use the product code (`/crop-book/prdNNN`) instead of the crop slug; also `/clients/`, `/crop-book/family/variety`.
2. **Landing cards huge / illogical** — oversized cards on `/crop-book/`.
3. **Important info on the side** — detail content not in the central/main panel.
4. **Missing tons of fields** — "every crop must show ALL the data we have, clearly and fully — that is the whole purpose of the book." Rich tables exist but are unsurfaced.
5. **Navigation is a dead-end** — `_layout.php` has NO nav; the cuts (questions/family/table) are unreachable sub-menus.
6. **Varieties before species** — species general info must come FIRST, varieties AFTER.

## 1. Decisions (team_00 2026-05-29)
- **Nav:** persistent **top bar** on every page (`בית · ספר גידולים · שוק`, `קהילה` reserved) + a **crop-book secondary row** (`שאלות / משפחות / טבלה / כיסוי`) so cuts are always reachable. Breadcrumb + back retained.
- **Crop detail IA:** single **sectioned, anchored, scrollable** page, **species-first**, with sticky in-page section anchors; **varieties LAST**.
- **Data approach:** embed all rich per-crop data in `crops.payload_json` (additive — **NO MySQL schema migration**, per `documentation/02-architecture/sfa-delivery-tier.md` anti-pattern guidance). Delivery MySQL stays a faithful Postgres mirror.

## 2. Data available (oma-postgres) — what to surface
Per crop (`crop_id`), embed into `crops.payload_json`:
| Source table | Fields to embed | Render section |
|---|---|---|
| `crops` cols | category, growth_cycle, harvest_unit_default, first_fruit_year, description | §Identity |
| `crop_families` (via family_id) | name_he, scientific_name | §Identity (family link) |
| `crop_planting_calendar` | activity_type (`seed`/`transplant`), season, region, month_jan..month_dec (bool), notes | §Calendar (12-month strip per activity) |
| `crop_field_enrichment` (crop-level rollup) | representative agronomy (germination temp, spacing, rows_per_bed, soil_ph, seeds_per_gram, yield) — median across the crop's varieties | §Agronomy |
| `crop_harvest_stats` | season, year, first/peak/last_harvest_week, yield_per_bed_min/median/max, yield_unit | §Harvest & yield |
| `crop_postharvest_storage` | storage_temp_c_min/max, rh_pct_min/max, ethylene_production, ethylene_sensitivity, storage_life_days_min/max, notes | §Storage |
| `crop_companion_matrix` (crop_a_id OR crop_b_id) | partner crop (resolve id→name_he+slug), compatibility (`beneficial`/`antagonistic`), notes | §Companions |
| `crop_knowledge_notes` (+ `crop_knowledge_notes_crops`) | **public only** (`is_internal_farm_use_only = FALSE`), note_type, body_text, trust_tier | §Notes |

**Data-governance gate (binding):** `crop_knowledge_notes.is_internal_farm_use_only = TRUE` notes MUST NEVER be embedded or rendered. As of 2026-05-29, **0** notes are public → §Notes renders an empty-state and embeds nothing until public notes exist. Do not override the flag.

**General reference (NOT per-crop):** `crop_cover_crops` has no `crop_id` — it is a global list (name_he/en, category, sow_window, total_days_garden, survives_winter, notes). Surface as a standalone reference page `/crop-book/cover-crops` (linked from the crop-book sub-nav), not on crop detail.

## 3. Scope of work

### 3.1 Ingest data contract — `organic_market_agent/publisher/sfa_ingest_push.py`
- Extend `_fetch_crops` to embed, per crop in `payload_json`: `identity` (category, growth_cycle, harvest_unit_default, first_fruit_year, family {name_he, scientific_name}), `calendar` (list of {activity_type, season, region, months:[12 bools], notes}), `agronomy` (crop-level median rollup of the §2 enrichment fields), `harvest` (list of {season, year, weeks:{first,peak,last}, yield_per_bed:{min,median,max}, unit}), `storage` ({temp:{min,max}, rh:{min,max}, ethylene_production, ethylene_sensitivity, life_days:{min,max}, notes}), `companions` (list of {slug, name_he, compatibility, notes}), `notes` (public-only list of {note_type, body_text, trust_tier} — empty until public notes exist). Keep existing keys (name_en, description_md, variety_count, dtm_min/max, oma_product_id). Use efficient bulk queries (one per table, grouped in Python) — no per-crop N+1.
- Add a new fetcher `_fetch_cover_crops` + a `cover_crops` table in the ingest contract (or embed as a single synthetic row) so `/crop-book/cover-crops` has data. **Decision:** add `cover_crops` to `TABLE_FETCHERS` + `--table` choices + `all`.
- Re-push `crops` (and `cover_crops`) from the Mac to the live ingest API after the change. Idempotent.

### 3.2 Global navigation — `sfa_delivery/templates/_layout.php` (+ a `nav.php` partial) + `hub.css`
- Persistent top bar on EVERY page: `בית` (`/`), `ספר גידולים` (`/crop-book/`), `שוק` (`/market/`); `קהילה` placeholder (disabled/hidden until ready). Mark the active section.
- Crop-book secondary row (rendered when `$active === 'crop-book'`): `שאלות` (`/crop-book/questions`), `משפחות` (`/crop-book/family`), `טבלה` (`/crop-book/table`), `כיסוי` (`/crop-book/cover-crops`). None are dead-ends — every page reaches the others.
- RTL, mobile-responsive (collapses to a menu on narrow screens). Keep breadcrumb/back where present.

### 3.3 Broken-link fixes
- Market↔crop-book cross-links: map by **crop slug**, never product code. Where a product/crop relationship exists, resolve to the crop slug (`crops.slug`/`oma_product_id` join), and only emit the link when the target route exists. Audit `CropBookViewController` + `MarketViewController` (or equivalent) + `crosslink.php` + `market_link`.
- Remove/fix `/clients/`, `/crop-book/family/variety`, and any other non-200 internal link. AC requires 0 internal 404s on a crawl of the main pages.

### 3.4 Crop detail — `sfa_delivery/templates/pages/book_crop.php` + section macros + `CropBookViewController::detail` + `hub.css`
- Full-width central panel (fix "info on the side"). Sticky in-page section nav (anchors).
- **Section order (species-first):** (1) Hero + Identity (name_he, scientific, family link, category, growth_cycle, harvest_unit, first_fruit_year, description, DTM range); (2) Planting calendar (12-month strip per activity_type seed/transplant); (3) Agronomy (crop-level rollup); (4) Harvest & yield; (5) Storage; (6) Companions (beneficial/antagonistic, linked to partner crops); (7) Notes (public only — empty-state when none); (8) **Varieties** (the existing patch03 agronomic grid + delta) — LAST.
- Controller `detail()` maps the new payload sections; each section renders only when it has data (no perpetual "—"); preserve the patch03 variety agronomy + delta logic.
- New section macros under `templates/macros/` (e.g. `crop_calendar.php`, `crop_harvest.php`, `crop_storage.php`, `crop_companions.php`, `crop_section.php` wrapper). Beautiful, readable, RTL.

### 3.5 Landing — `sfa_delivery/templates/pages/book_entry.php` + `hub.css` + `CropBookViewController::entry`
- Fix oversized cards: sensible card grid (responsive columns; reasonable card height). The crop-card grid links must use crop slugs (no prd 404s).
- Keep the entry nav cards but right-sized and logical.

### 3.6 Cover-crops reference page (new) — route + `CropBookViewController::coverCrops` + `pages/book_cover_crops.php`
- Route `/crop-book/cover-crops`; render the `cover_crops` data as a readable table/cards.

## 4. Acceptance Criteria
| AC | Check | Pass |
|----|-------|------|
| AC-U4-01 | ingest `crops` payload embeds identity+calendar+agronomy+harvest+storage+companions+notes(public-only) | dry-run sample |
| AC-U4-02 | `cover_crops` pushed; `/crop-book/cover-crops` renders ≥1 | live |
| AC-U4-03 | crop detail shows species sections in order; **varieties LAST** | live render |
| AC-U4-04 | every populated section renders real data (≥4 species-level data points for a typical crop e.g. arugula: calendar, harvest, storage, companions) | live arugula |
| AC-U4-05 | internal-only knowledge notes NEVER rendered (is_internal_farm_use_only filter) | grep + live |
| AC-U4-06 | persistent top-bar nav on every page (home/market/crop-book) + crop-book sub-nav; active state | live all routes |
| AC-U4-07 | **0 internal 404s** on a crawl of /, /crop-book/, /crop-book/{slug}, /crop-book/table, /crop-book/family, /crop-book/questions, /crop-book/cover-crops, /market/ | crawl |
| AC-U4-08 | detail content full-width central panel (no large empty side) | CSS/live |
| AC-U4-09 | landing cards right-sized (responsive grid; not oversized); crop cards link to valid crop slugs | live |
| AC-U4-10 | `php -l` clean; `composer test` 0 new failures; render tests for new section macros | tests |
| AC-U4-11 | `validate_aos.sh` 0 FAIL; no reconciler/schema change; no `www.nimrod.bio`; MySQL stays faithful mirror (no derived-only data pushed except documented rollups) | run + diff |
| AC-U4-12 | deployed to uPress `sfa.nimrod.bio` (NOT home server); live smoke 200 across all routes | curl |

## 5. Orchestration
- **Sonnet A (data):** §3.1 ingest contract (crops rich embed + cover_crops) + dry-run.
- **Sonnet B (nav/links/landing):** §3.2 global nav + §3.3 broken-link fixes + §3.5 landing + §3.6 cover-crops page.
- **Sonnet C (crop detail):** §3.4 sectioned species-first detail + section macros + CSS.
- team_100: integrate, re-push (Mac→ingest), deploy (waldhomeserver relay→uPress), smoke. team_50 QA; team_190 (non-Claude) L-GATE_V; ADR042 closure.

## 6. Out of scope / notes
- No oma-postgres schema/engine/reconciler change (data exists; rides in payload_json).
- Knowledge notes are 100% internal-gated today → §Notes is an empty-state until public notes exist (do NOT override the flag).
- Durability caveat carried (server DB head 034 — crop data re-pushed manually from Mac).
- Hosting canon: `documentation/02-architecture/sfa-delivery-tier.md` (uPress serves; home server is backend + deploy relay only).
