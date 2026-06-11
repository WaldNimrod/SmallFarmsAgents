# BUILD MANDATE — WP-CB-UI-WI7 — team_100 → team_10 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 · **To:** team_10 (Sonnet) · branch `claude/ui-polish-hub-cropbook-2026-06-03`
**Depends on:** team_35 `DESIGN_DECISIONS_v1.0.0.md` (for Part A). **Part B (cleanups) can start immediately.**

## Hard constraints
- **ZERO git operations** (team_100 commits + verifies ancestry). **Scope = `sfa_delivery/` ONLY** (no `_aos/`). Render-layer; no DB/data mutation. composer + `php -l` green; report counts.

## Part A — implement team_35 WI-7 decisions (AFTER their artifact lands)
Apply verbatim from `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-WI7/DESIGN_DECISIONS_v1.0.0.md`:
- **Q2** category wording → `FieldRegistry::ENUM_LABELS['category']` (`app/Lib/FieldRegistry.php`).
- **Q3** yield/removal unit → `FieldRegistry::unitLabel()` **only if** team_100 confirms the stored value's basis matches (do NOT relabel ק״ג/הקטר→ק״ג/דונם without the data-basis confirmation; a 10× error is worse than a hectare label).
- **Q4** leading-question set → `CropBookViewController::questions()` (`href`/copy/sub per the design); ensure each link lands on a non-empty result. If the entry-card count (`book_entry.php $question_total`) is referenced, keep it consistent with the actual count.
- **Q5** eyebrows → the hub/audience templates (per-element Hebraize/keep per the decision).

## Part B — 2 INFO cleanups (independent; start now)
1. **Dead legacy route `/crop-book/table?category=summer|winter|fast|beginner|small-space`.** The UI now routes leading-questions to `/crop-book/?season=…`/`?dtm_max=…`; the old `tableView()` `category=` semantic tokens are dead (they match the botanical `category` column → always 0). **Either** strip those tokens' handling / **or** 301-redirect them to the live equivalent. Do not leave a 0-result reachable URL.
2. **Calc-page JSON embed English field keys.** Investigate the calc page's embedded JSON (the `data-*`/JSON the calc JS consumes). The L-GATE_V noted English keys there. **Confirm whether they are machine-only** (consumed by `crop-book-v1.js`/calc JS): if changing them would break the JS contract, **LEAVE them** (machine payload, not user-visible) and document that in the BUILD_REPORT; only change if genuinely user-visible.

## Verify + handback
composer (was 192/192) + `php -l` clean; if Part A touches filters/labels, add/extend a test. Write `_COMMUNICATION/team_10/SFA-S003-P004-WP-CB-UI-WI7/BUILD_REPORT_v1.0.0.md` (files+lines, per-item status, INFO-2 disposition). **Do NOT commit.** team_100 reviews + commits, dispatches team_99 deploy, then routes **team_50 VISUAL QA**.
