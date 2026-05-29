---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief Architect — orchestrator)
to: team_190 (cross-engine validator — MUST be non-Claude per IR#1)
cc: team_00, team_10, team_50, team_99
date: 2026-05-29
type: validation_mandate
wp: SFA-S003-P002-WP-UI-patch02
gate: L-GATE_V
build_commit: "08a0f9e"
status: AWAITING_VALIDATION
---

# L-GATE_V Mandate — WP-UI-patch02 Media Integration Completion

## Cross-engine (IR#1)
Built by Claude Sonnet sub-agents + team_100; QA by Claude Haiku. Validator MUST
be **non-Claude** (GPT-5.x / Gemini / Cursor). builder ≠ QA ≠ validator.

## Scope built (Phase 1)
1. Per-crop icon system: migration `057` `crops.icon_url` (nullable, reversible);
   `Crop` model; `crop_card.php` + `book_crop.php` render watercolor `<img>` when
   `icon_url` set, else SVG sprite, else `#icon-leaf`.
2. Brand media on main (e8cd4ce): 8 module heroes + hub-hero + og-default +
   favicon-32 + apple-touch-icon; wired `modules.php` (8 hero_url) + `_layout.php`.
3. 70 slug-exact watercolor crop-art generation prompts (external gen = Phase 2).

## Verify (independently)
1. `crops.icon_url` exists/nullable + migration 057 reversible: `docker exec oma-postgres psql -U oma -d organic_market_agent -c "\d crops"` | grep icon_url.
2. Full PHP suite green: `cd sfa_delivery && composer test` → 53 tests, **0 failures** (deprecations OK). NOTE: a sub-agent test-isolation bug (CropCardIconTest eval-stub leaked → spurious /crop-book/ 500) was fixed by team_100 (process isolation) — confirm the suite passes as a whole.
3. pytest icon tests: `.venv/bin/python -m pytest tests/crop_book/test_icon_url.py -q`.
4. Fallback correctness: read `sfa_delivery/templates/macros/crop_card.php` — img when icon_url set, else sprite/leaf.
5. Brand media present + wired: 12 assets under `sfa_delivery/public_assets/img/` (+heroes/), `grep -c hero_url sfa_delivery/modules.php` == 8, `_layout.php` og/favicon refs.
6. 70 prompts: `_COMMUNICATION/team_100/SFA-S003-P002-WP-UI-patch02/MEDIA_PROMPT_crop_icons_v1.0.0.md`.
7. `validate_aos.sh .` 0 FAIL. Data/UI-only scope; no engine change; no www.nimrod.bio reintroduced.

## Disclosed (non-defects)
- `icon_url` is null for all 70 crops → SVG fallback renders now; watercolors are
  Phase-2 (external image-gen per the 70 prompts) + ingest/MySQL plumbing.
- **Live deploy (AC-U2-06)** to sfa.nimrod.bio is mandated to **team_99** (uPress
  FTPS IP-allowlist blocks team_100's machine). Validate the build/repo now; the
  live-deploy re-check folds in with team_99's deploy report. This also folds in
  the already-PASSED WP-UI-patch01 media R2.

## Verdict
→ `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI-patch02/L-GATE_V_VERDICT_v1.0.0.md`
(name your engine). On PASS → team_100 ADR042 closure → LOD500_LOCKED.

— team_100 (Claude Opus 4.7) 2026-05-29
