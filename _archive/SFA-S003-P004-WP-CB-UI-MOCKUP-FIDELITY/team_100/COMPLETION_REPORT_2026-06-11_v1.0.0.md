---
id: COMPLETION_REPORT_SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY_v1.0.0
wp: SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY
from: team_100 (Claude Code — builder)
to: team_100 (origin) → route L-GATE_VALIDATE to team_190 (cross-engine, validator ≠ Claude Code)
date: 2026-06-11
gate: L-GATE_BUILD COMPLETE → awaits cross-engine L-GATE_VALIDATE
branch: feat/wp-cb-ui-mockup-fidelity (worktree /private/tmp/sfa-wp-ui-fidelity) — NOT pushed/merged
deploy: LIVE on sfa.nimrod.bio (FTPS, 2026-06-11)
---

# WP-CB-UI-MOCKUP-FIDELITY — Build Completion + Validation Handoff

## Root cause (supersedes the handoff's framing)
The handoff premised that the list/market surfaces "never migrated from v1 → Step-2." **Inaccurate** —
production already served the Step-2 redesign markup. The true root cause of the live-vs-mockup divergence was a
**single CSS comment bug**: `redesign.css`'s header comment contained `--r-*/--sp-*/--sh-*`, whose embedded
`*/` **prematurely closed the `/* */` comment**. The parser then consumed the following text + the entire
`:root{}` token block as one invalid rule and **dropped it site-wide** — so `--shell-max`, `--sp-*`, `--r-*`,
`--sh-*`, `--fs-*` were undefined everywhere. Every redesign surface rendered **uncapped (full-width), gapless,
wrong radii/shadows**. Fixing the comment restored the whole token layer (e.g. market: 5 gapless full-width
columns → 3 spacious 1100px-capped columns at mockup parity). Confirmed no other stylesheet referenced the
short vars, so the fix's blast radius is exactly the redesign surfaces (intended).

## Delivered (commits a5ada1a · f23c589 · 00780a3 · db2d573 · d8bfdce; all under sfa_delivery/)
- **redesign.css:** comment-bug fix (restores tokens); `.pc__art img` sizing; `.hub-intro__collage`;
  `.pc__foot .fresh::before{content:none}` (kills classb dot-bleed on the market list).
- **Market grid → market.html parity:** watercolor `<img>` in `.pc__art` resolved via the **crop slug**
  (`CropArt`), icon fallback; 26/65 products link to a crop → watercolor, 39 have no crop link → honest icon
  (0 link-but-missing-art). Sparklines/freshness/trend/drill-down intact.
- **Crop-book list:** already at parity post-token-fix; **5 icon fallbacks fixed** (scallions/salad-mix/
  pac-choi/bush-pole/corn) → **70/70 arted**; `?view=table` preserved.
- **New `SFA\Lib\CropArt`:** single source for the crop→watercolor map (dedup of the controller const + the
  book_entry inline map + market).
- **Home:** hero watercolor crop collage. **Crop page:** related-crop watercolors + `–80` stray-dash glance fix.
- **calc / assumptions:** at parity automatically from the token fix (no code change).
- **Dead-code retirement:** removed unused macros `price_card.php` + `freshness_pill.php`; the dead old-card
  CSS systems (classb `.pcard*`; crop-book-v1 `.ccard*/.cards-grid/.seasonbar/.minibar/.cardviz`; mobile-fixes
  FIX1/FIX3 + scattered). Kept live `.fresh*`/`.spark*` (market detail), `.gj-cropcard*` (search), `.ptable*`
  (table view). Retired one obsolete `.cards-grid` test assertion.
- **Out of scope (DECISION):** `cropdata_entry` mockup — its route was retired (commit 4324403); not revived.
  Crop-list `.cc__stats` yield/difficulty omitted — intentional honesty (derived yield fails `test_ac05`).

## Verification
- Delivery **phpunit 232/232** green.
- **qa_probe** local sweep (12 surfaces × mobile+desktop = 24): 0 overflow, all render.
- **qa_probe** production sweep (8 surfaces × mobile+desktop = 16): verdict PASS, 0 overflow, all render.
- **validate_aos: 0 FAIL on the canonical spoke** (main checkout). The temp worktree shows 2 spurious FAILs
  (spec_ref / ADR043) because a `git worktree` lacks the gitignored `_aos` governance cache — not a real
  failure; all WP changes are scoped to `sfa_delivery/` (cannot affect governance).
- Production smoke confirmed: asset `?v=` bumped, comment-fix live (`--shell-max:1100px` resolves), home
  collage present, crop-book 0 icon fallbacks, market watercolors on crop-linked products.

## Open follow-up (out of scope, flagged)
The book↔market **₪ price-chip never renders on /crop-book/** (product/crop slugs don't align; `entry()` joins
products by slug only — needs the `hebrew_name` fallback `resolveCropSlug()` already uses). Lighting it up
closes the book→market price loop (the competitive-analysis #1 wedge). Backend/controller + test; no schema.

## Remaining gate
**Cross-engine L-GATE_VALIDATE (validator ≠ Claude Code, IR#1/#5).** Claude Code cannot self-produce the
team_190 verdict. Route to a non-Claude engine / team_190 with this report + the qa_probe artifacts. The
feature branch is not pushed/merged — push/PR is team_00's call.
