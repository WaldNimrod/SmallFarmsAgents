---
id: SFA-S003-P002-WP-UI-patch02-LOD400
wp: SFA-S003-P002-WP-UI-patch02 — Media Integration Completion
gate: L-GATE_B (LOD400)
status: READY_FOR_BUILD
author: team_100 (Chief Architect)
date: 2026-05-29
version: v1.0.0
depends_on: [SFA-S003-P002-WP-UI-patch01]
activation: team_00 grant 2026-05-29 ("מאשר ... אורקסטרציה ... כולל בדיקות ופריסה")
orchestration:
  build: "team_10 (Claude Sonnet) sub-agents"
  qa: "team_50 (Claude Haiku)"
  validation: "team_190 (non-Claude — IR#1)"
evidence: _COMMUNICATION/team_100/SFA-S003-P002-WP-UI-patch02/MEDIA_COMPLETION_MAP_v1.0.0.md
---

# LOD400 — WP-UI-patch02: Media Integration Completion

## 1. Mission
Finish the media topic end-to-end: (A) consolidate + deploy the brand media
(8 module heroes + hub-hero + og-default + favicon), and (B) stand up a
per-crop **watercolor** icon system for all **70 crops** with graceful SVG
fallback. Phase 1 (this WP, in-session) delivers the full SYSTEM + brand media
deployed; Phase 2 backfills the 70 watercolor rasters as external art lands.

## 2. Decisions (team_00 / team_100)
- Per-crop art style = **watercolor raster** (brand-consistent).
- Crop→art mapping = **DB column `crops.icon_url`** (nullable; SSOT; fallback to SVG sprite when null). Recommended by team_100; team_00 deferred to recommendation.
- Watercolor generation = **external image-gen** (team_00 / ChatGPT-Devora pipeline) per team_100 prompts. The only non-in-session step.
- Brand media = team_100 consolidates branch `claude/sfa-ui-patch01` → main + deploys.

## 3. Scope — Phase 1 (build now)
### 3.1 Data model (additive)
- Alembic migration: `ALTER TABLE crops ADD COLUMN icon_url VARCHAR(255) NULL`.
  Reversible (drop_column). Update the `Crop` SQLAlchemy model.

### 3.2 UI render (sfa_delivery)
- Crop cards (crop-book listing + crop detail) render `crops.icon_url` as a
  watercolor `<img>` when present; else fall back to the existing SVG sprite
  (`<use href="#icon-...">`) → else generic `icon-leaf`. Lazy-load, alt text.
- Keep `module_card.php` hero behaviour intact (heroes are module-level).

### 3.3 Brand media consolidation + deploy
- Bring the watercolor heroes/og/favicon from `claude/sfa-ui-patch01` onto main
  (assets under `sfa_delivery/public_assets/img/`), wire `modules.php` `hero_url`
  per module (8 modules + hub-home), place `og-default.webp` + favicon, update
  `scripts/ftp_deploy_sfa_ui.sh` if needed, deploy to **sfa.nimrod.bio**.

### 3.4 Generation prompts
- 70 slug-exact watercolor crop-art prompts (one per crop), brand-consistent,
  filed as `_COMMUNICATION/team_100/SFA-S003-P002-WP-UI-patch02/MEDIA_PROMPT_crop_icons_v1.0.0.md`.

## 4. Out of scope (Phase 2 / future)
- Actual watercolor raster generation (external) + `icon_url` backfill for all 70.
- New crop-art beyond the 70 current crops.

## 5. Acceptance Criteria (Phase 1)
| AC | Check | Pass |
|----|-------|------|
| AC-U2-01 | migration adds nullable `crops.icon_url`; `alembic upgrade head` clean; downgrade drops it | applied + reversible |
| AC-U2-02 | `Crop` model exposes `icon_url` | attribute present |
| AC-U2-03 | crop card renders `<img>` when icon_url set | render harness |
| AC-U2-04 | crop card falls back to SVG sprite / leaf when icon_url null | render harness (no broken img) |
| AC-U2-05 | brand media (8 heroes + hub-hero + og + favicon) present in public_assets + wired in modules.php | grep + file check |
| AC-U2-06 | deploy to sfa.nimrod.bio succeeds; /market & module pages 200; og/favicon resolve | live curl 200 |
| AC-U2-07 | 70 crop-art prompts exist, slug-exact, 1:1 with crops | count == 70 |
| AC-U2-08 | `php -l` clean on changed templates; `composer test` no new failures | lint + test |
| AC-U2-09 | `validate_aos.sh .` 0 FAIL | run |
| AC-U2-10 | data-only + UI; no engine/reconciler change; no www.nimrod.bio coupling reintroduced | git diff scope |

## 6. Orchestration (team_00 directive 2026-05-29)
- Sub-agent A (Sonnet): §3.1 + §3.2 + tests (icon system code).
- Sub-agent B (Sonnet): §3.4 (70 prompts).
- team_100: §3.3 brand media consolidation + DB migration apply + deploy + integration.
- team_50 (Haiku): QA the integrated result (AC matrix).
- team_190 (non-Claude): L-GATE_V (incl. the UI-patch01 media R2, folded in).

## 7. GCR / migrations
One additive migration (crops.icon_url). No governance change.
