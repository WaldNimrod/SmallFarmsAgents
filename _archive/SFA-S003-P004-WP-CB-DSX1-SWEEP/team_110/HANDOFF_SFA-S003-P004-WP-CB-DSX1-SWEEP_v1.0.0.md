---
id: HANDOFF_SFA-S003-P004-WP-CB-DSX1-SWEEP_v1.0.0
from: team_100 (Chief Architect · the session that shipped WP-CB-UI-REDESIGN)
to: team_110 (Domain IDE Architect / execution)
date: 2026-06-08
type: session-handoff (aos_handoff full 110)
wp: SFA-S003-P004-WP-CB-DSX1-SWEEP
project: SFA-S003-P004
gate: L-GATE_E → build
status: REGISTERED — ready to build
engine: Claude Code (builder) — validator MUST differ (IR#1/#5)
---

# HANDOFF — SFA-S003-P004-WP-CB-DSX1-SWEEP — team_100 → team_110

**DSX-1 emoji fold for the surfaces NOT covered by WP-CB-UI-REDESIGN.**
**Track:** A · **Effort:** SMALL · **Risk:** LOW (presentational, light polish)

## 0. ⚠ Branch discipline + reporting (team_00 directive — mandatory)

- **Work on an ISOLATED branch** (e.g. `feat/wp-cb-dsx1-sweep`) off `main`. Do NOT commit to `main`.
- **Report to team_100 on completion** — write a COMPLETION_REPORT to `_COMMUNICATION/team_110/SFA-S003-P004-WP-CB-DSX1-SWEEP/` and notify team_100; team_100 owns the merge + deploy decision.
- Commit defensively (explicit paths — the AOS auto-syncer touches `_aos/`).

## 1. Task

team_190's L-GATE_V advisory on WP-CB-UI-REDESIGN flagged that **untouched** surfaces still carry OS color-emoji (locked principle #6 — no emoji). Replace every OS emoji with a `.gi` line-glyph from the **already-shipped** sprite `public_assets/img/ui-icons.svg` (26 IDs: `i-sprout i-seedling i-drop i-shield i-companions i-box i-tractor i-bulb i-journal i-receipt i-scale i-leaf i-snow i-calendar i-repeat i-basket i-chart i-compost i-grid i-rows i-book i-cap i-gear i-download i-shekel i-info i-flame`). Crop watercolors + the `#icon-*` crop sprite stay.

## 2. Scope — 12 files (exact)

**pages:** `search_results.php` · `community.php` · `account_landing.php` · `book_variety.php` · `hub_calc.php` · `hub_tiers.php`
**macros:** `crop_calendar.php` · `calc_panel.php` · `contrib_strip.php` · `feed_item.php` · `tier_badge.php` · `variety_row.php`
**+** the WhatsApp `✆` glyph in `templates/_layout.php` / `hub_home.php` contribute CTA (decide: drop or map).

> **EXCLUDE `market_product.php`** — it is owned by **WP-CB-MARKET-DETAIL** (full redesign, not an emoji-only fold). Touching it here = conflict.

## 3. Pattern (reference — already done)

Mirror the WI-2 / WI-7 folds from WP-CB-UI-REDESIGN:
- `hub_home.php`: `🌱🌾💡📒` → `<svg class="gi" aria-hidden="true"><use href="#i-sprout"/></svg>` etc.
- `calc_dash.php`: emoji map → sprite IDs, rendered as `<svg class="gi"><use href="#...">`.
- Sizing: add per-context rules in `redesign.css` (e.g. `.feed_item .gi{...}`) — keep monochrome dingbats (`✎ ◇ ‹ › ← ⌕ ◔ ▾`) as-is (they are NOT emoji).

## 4. Verify (same harness)

- `cd sfa_delivery && composer install && APP_ENV_FILE=.env.test php vendor/bin/phpunit` → green.
- `qa_probe.mjs` on the affected routes (`/search`, `/community`, `/account`, `/crop-book/{slug}/variety/{v}`, `/about`, the calc/tier pages) → no overflow, no remaining emoji.
- Emoji sweep: `grep -rlP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{26FF}]' templates/` → only `market_product.php` should remain (excluded).

## 5. Startup + cautions

Read `CLAUDE.md` → `_aos/governance/team_110.md` → this handoff. Delivery-tier UI only (no engine, no backend). Cross-engine L-GATE_V at the end (validator ≠ Claude Code). On completion → COMPLETION_REPORT to team_100; team_100 merges + deploys (the `ui-icons.svg` sprite is already live, so no asset dependency).

## 6. Done

All 12 files emoji-free (DSX-1 glyphs); `market_product` untouched; tests + qa_probe green; isolated branch; COMPLETION_REPORT filed to team_100.
