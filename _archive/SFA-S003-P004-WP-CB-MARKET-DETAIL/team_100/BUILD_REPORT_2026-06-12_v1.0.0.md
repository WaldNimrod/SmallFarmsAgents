# BUILD REPORT — SFA-S003-P004-WP-CB-MARKET-DETAIL — team_10 (Claude Opus) — v1.0.0

**Date:** 2026-06-12 · **Builder:** team_10 (Claude Opus 4.8) · **Gate next:** L-GATE_VALIDATE (external, non-Claude)
**Branch / HEAD:** `feat/wp-cb-market-detail` @ **`58a2023`** (pushed to origin; off `origin/main` 609a8d5)
**Spec built to:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MARKET-DETAIL/SPEC_2026-06-12_v1.0.0.md` (incl. §8 + §9 remediation)
**L-GATE_S:** PASS_WITH_FINDINGS (team_190 / GPT-5.2 Cursor) — AC-5 locked + AC-7 scoped per §9.

## What was built (render-layer only, `sfa_delivery/`)
| AC | Delivered | Evidence |
|----|-----------|----------|
| **AC-1** DS re-skin | `market_product.php` rebuilt from Class-B v2 (`.pbig`/`.pgraph`/`.pstats`/`.pdetail` + inline styles) to the redesign DS — capped `.shell`, `.pcard` price hero, DS graph card, history table, stats grid, sidebar; new `.md*` section in `redesign.css` (reuses `.pcard`/`.pc__*`/`.fresh.f-a-s`/`.bigspark`) | screenshots desktop+375; `mdetail/mdhero/mdgraph/mdtable` present |
| **AC-2** emoji-fold | `📦/📭/📊/📖/◐` → DSX-1 `.gi` glyphs (`#i-box`/`#i-chart`/`#i-scale`/`#i-book` + sprite) | `testMarketDetailNoEmojiAndWatercolorHero` asserts zero raw emoji |
| **AC-3** watercolor hero | consumes the **already-present** `$product['wc_art']` via `.pc__art` (the §8 correction — **no controller change**); line-glyph fallback | test asserts `pc__art` + `wc-tomato.png`; screenshot |
| **AC-4** freshness | switched to redesign `.fresh.f/.a/.s` (consistent with the list) | template + screenshot |
| **AC-5** range buttons | `7י`/`28י` active; `90י`/`שנה` honestly disabled `בקרוב` (`.is-soon` + `disabled` attr) — **team_00 LOCKED** | `testMarketDetailDisabledRanges` |
| **AC-6** empty state | no-price / no-history render cleanly with `.gi` glyphs | verified live on `:8095` (seeded empty product) |
| **AC-7** cross-links | crop-book `.xlink` + LOCKED disclaimer preserved; no calc link (none existed — §9.2) | `testMarketDisclaimerClassBClass` + template |

## Verification (VC hooks)
- **VC-1 phpunit:** `233 / 233` pass (origin/main 232 + 1 new), 0 fail; the 6 `ClassBRouteTest` market-detail tests updated to the new DS classes (mdgraph/mdtable/mdtable-wrap/mdcard__top) + WI-7 overflow guards re-pointed to `redesign.css`.
- **VC-2 validate_aos:** **0 FAIL** (31 PASS / 21 SKIP).
- **VC-3 scope:** 3 files, all `sfa_delivery/` (market_product.php, redesign.css, ClassBRouteTest). Data contract unchanged.
- **VC-6 AC-6 qa_probe:** `/market/tomato` **overflow=false** at 375 **and** 1440; visual parity to the redesign DS confirmed by screenshot (both viewports).
- **VC-7 no regression:** market list unaffected (untouched); the retired-block usage check confirmed `.pbig/.pgraph/.pstats/.pdetail/.phist/.emptybox/.fresh--*` are used by **no** template after the re-skin.

## Fix applied during build (regression caught)
The first cut inverted the trend colors. Corrected to the established **SFA price-index convention**: rising price =
**red** (`--gj-tomato-deep`), falling = **green** (`--gj-leaf-deep`) — matching `redesign.css .trend.up` (L395) and the
old `.pgraph__chg`/`.phist`. Applied to `.pc__trend--up/--dn` + `.delta-up/-dn`; re-verified by screenshot.

## Deferred (the spec's gated "higher-risk" step)
The now-dead Class-B blocks (`.pbig/.pgraph/.pstats/.pdetail/.phist/.emptybox/.fresh--*`) remain in `classb.css` as
**harmless unused CSS** — confirmed used ONLY by this (re-skinned) page. AC-1's "no Class-B v2 blocks in the primary
content" is met at the **markup** layer (the template has none). Their **physical retirement** from `classb.css` is
deferred to a scoped follow-up (keep the shared `.spark`; re-run all Class-B routes through `qa_probe` after — VC-7
guardrail). Flagged as a background task.
