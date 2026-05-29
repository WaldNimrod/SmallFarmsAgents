---
id: BUILD_REPORT_iconsys_v1.0.0
from: team_10 (Claude Sonnet)
date: 2026-05-29
wp: SFA-S003-P002-WP-UI-patch02
phase: Phase 1 — Icon System (§3.1 + §3.2 + tests)
branch: wp/ui-patch02-icons
migration_revision: 057
---

# Build Report — WP-UI-patch02 Phase 1: Per-Crop Icon System

## Scope

Sub-agent A (team_10) deliverables per LOD400 §6:
- §3.1: Alembic migration + SQLAlchemy model update
- §3.2: UI render in crop listing card + crop detail page
- AC-U2-01..04, AC-U2-08, AC-U2-09, AC-U2-10

## AC Verification Table

| AC | Check | Result | Evidence |
|----|-------|--------|---------|
| AC-U2-01 | migration adds nullable `crops.icon_url`; `alembic upgrade head` clean; downgrade drops it | **PASS** | `alembic upgrade head` + `alembic downgrade 056` both clean; `\d crops` confirmed column; column absent after downgrade |
| AC-U2-02 | `Crop` model exposes `icon_url` | **PASS** | `Crop.__table__.c["icon_url"]` present, nullable=True, VARCHAR(255); 4 pytest tests pass |
| AC-U2-03 | crop card renders `<img class="crop-card__art">` when icon_url set | **PASS** | PHPUnit `testCardRendersImgWhenIconUrlSet` + `testDetailPageRendersImgWhenIconUrlSet` + pytest PHP-CLI render test — all pass |
| AC-U2-04 | crop card falls back to SVG sprite / leaf when icon_url null | **PASS** | PHPUnit `testCardFallsBackToSvgWhenIconUrlEmpty` + `testCardFallsBackToLeafWhenBothAbsent` + `testDetailPageFallsBackToSvgWhenIconUrlEmpty` + pytest fallback tests — all pass |
| AC-U2-05 | brand media wired | **N/A** | Phase 1 scope only (§3.1 + §3.2); brand media is team_100 §3.3 |
| AC-U2-06 | deploy to sfa.nimrod.bio | **N/A** | Phase 1 scope only; deploy is team_100 §3.3 |
| AC-U2-07 | 70 crop-art prompts | **N/A** | Phase 1 scope only; prompts are Sub-agent B §3.4 |
| AC-U2-08 | `php -l` clean on changed templates; `composer test` no new failures | **PASS** | `php -l` passes on both changed PHP files. `composer test` 52/53 pass; 1 pre-existing failure (`RouteSmokeTest /crop-book/ => 500`) not introduced by this changeset |
| AC-U2-09 | `validate_aos.sh .` 0 FAIL | **PASS** | 29 PASS / 19 SKIP / 0 FAIL |
| AC-U2-10 | data-only + UI; no engine/reconciler change; no www.nimrod.bio coupling reintroduced | **PASS** | `git diff` scope: migration file, models.py, crop_card.php, book_crop.php, test files only — no engine/reconciler touched; no www.nimrod.bio reference added |

## Migration Details

| Field | Value |
|-------|-------|
| Revision ID | `057` |
| Down-revision | `056` |
| DDL | `ALTER TABLE crops ADD COLUMN icon_url VARCHAR(255) NULL` |
| Reversible | Yes — `drop_column("crops", "icon_url")` |
| File | `organic_market_agent/db/versions/057_crop_icon_url.py` |

## Files Changed

| File | Change | Notes |
|------|--------|-------|
| `organic_market_agent/db/versions/057_crop_icon_url.py` | **NEW** | Alembic migration 057 |
| `organic_market_agent/crop_book/models.py` | **MODIFIED** | Added `icon_url: Mapped[Optional[str]]` to `Crop` model |
| `sfa_delivery/templates/macros/crop_card.php` | **MODIFIED** | Reads `$crop['icon_url']`; renders watercolor `<img class="crop-card__art">` when set; falls back to `$icon_svg` or `#icon-leaf` |
| `sfa_delivery/templates/pages/book_crop.php` | **MODIFIED** | Reads `$icon_url`; renders watercolor `<img class="crop-card__art cb-crop-hero__art">` in hero when set; else SVG sprite |
| `tests/crop_book/test_icon_url.py` | **NEW** | 7 pytest tests: model column checks + PHP CLI render harness (AC-U2-02, AC-U2-03, AC-U2-04) |
| `sfa_delivery/tests/CropCardIconTest.php` | **NEW** | 6 PHPUnit tests: crop_card + book_crop render harness (AC-U2-03, AC-U2-04) |

## Test Run Summary

**Python (pytest):**
```
7 passed in 0.18s
```

**PHP (composer test):**
```
53 tests, 165 assertions, 1 pre-existing failure (RouteSmokeTest /crop-book/ 500 — not introduced by this change)
```

**AOS Validation:**
```
29 PASS / 19 SKIP / 0 FAIL — L-GATE_BUILD EXIT CRITERION: SATISFIED
```

## Render Logic (crop_card.php + book_crop.php)

```
if $icon_url !== '' :
    → <img class="crop-card__art" src="$icon_url" loading="lazy" decoding="async" alt="$name_he">
else if $icon_svg !== '' :
    → <div class="gj-cropcard__icon">$icon_svg</div>  (trusted SVG)
else:
    → <div class="gj-cropcard__icon"><svg viewBox="0 0 24 24"><use href="#icon-leaf"></use></svg></div>
```

## Constraints Verification

- No engine/reconciler/enrichment files touched (AC-U2-10: PASS)
- No www.nimrod.bio references introduced (AC-U2-10: PASS)
- `_aos/` directory not modified (Iron Rule compliance)
- Other teams' `_COMMUNICATION/` not touched
- No `module_card.php` hero behaviour changed (spec §3.2 requirement)

## Handoff Notes

Phase 1 deliverables complete. Remaining work for other agents:
- **team_100 (§3.3)**: merge branch `claude/sfa-ui-patch01` watercolor heroes → main, wire `modules.php` hero_url, deploy to sfa.nimrod.bio
- **Sub-agent B (§3.4)**: 70 slug-exact watercolor crop-art generation prompts
- **Phase 2**: populate `crops.icon_url` for 70 crops as external art lands; deploy
- **team_50**: QA AC matrix
- **team_190**: L-GATE_V cross-engine validation
