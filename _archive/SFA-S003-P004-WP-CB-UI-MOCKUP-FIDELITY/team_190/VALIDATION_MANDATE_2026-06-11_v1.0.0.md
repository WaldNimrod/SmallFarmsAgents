# VALIDATION_MANDATE — SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY — team_100 → team_190 — v1.0.0

**Date:** 2026-06-11
**From:** team_100 (Claude Code, builder)
**To:** team_190 (constitutional validator) — **MUST run on a non-Claude engine** (Cursor / Codex / Desktop) per Iron Rule #1/#5
**Gate:** L-GATE_VALIDATE
**Branch / HEAD:** `feat/wp-cb-ui-mockup-fidelity` @ `29b6847` (pushed to `origin`). A **clean fast-forward over `origin/main`** (origin/main is the build base `be6c8d7`; 0 divergence). **Build commits `a5ada1a..154c89d`** (6 UI commits); validate at the branch tip. On PASS the closure fast-forwards `main`.
**Deploy:** LIVE on `https://sfa.nimrod.bio` (FTPS, 2026-06-11). Tier: delivery (Slim4/PHP + CSS), `sfa_delivery/` only.

## Why this mandate
team_100 (Claude Code) is the builder and CANNOT issue the constitutional L-GATE_VALIDATE verdict for its own
work (IR#1/#5). Build + deploy + production smoke are complete; the only remaining canonical step is an
independent cross-engine PASS → then archive + roadmap `LOD500_LOCKED`.

## Scope
Bring the live delivery UI to fidelity with the team_35 Step-2 hi-fi mockups (`mockups/` in the WP dir),
surface by surface. All changes are confined to `sfa_delivery/` (no schema, no pipeline, no governance).

## ⚠ History (root cause + two issues found & fixed — context for the validator)
1. **Root cause (corrected the handoff premise).** The handoff assumed list/market "never migrated v1 → Step-2";
   in fact production already served Step-2 markup. The real defect was a **CSS comment bug**: `redesign.css`'s
   header comment contained `--r-*/--sp-*/--sh-*`, whose embedded `*/` **closed the `/* */` comment early**, so
   the parser dropped the entire `:root{}` token block (`--shell-max`, `--sp-*`, `--r-*`, `--sh-*`, `--fs-*`)
   site-wide → every redesign surface rendered uncapped/gapless/wrong-radii. Fixed by rewording the comment
   (commit `a5ada1a`). Confirmed no other stylesheet references those short vars (fix blast-radius = redesign
   surfaces only).
2. **Market watercolor slug (caught by prod smoke).** `wc_art` was first resolved from the product's own slug
   (an OMA namespace not in the art map); local seed used product-slug == crop-slug, masking it. Fixed to
   resolve via the resolved **crop slug** (`resolveCropSlug` → `CropArt`), product-slug then icon fallback
   (commit `d8bfdce`). On prod: 26/65 products link to a crop → watercolor; 39 have no crop link → honest icon
   (0 link-but-missing-art).

## Verification cases (re-execute independently at the build tip)

**Build / integrity**
1. **VC-1** `cd sfa_delivery && composer install && vendor/bin/phpunit` (copied/real vendor) → **232 pass / 0 fail**
   (1 PHPUnit deprecation notice, non-blocking). Note: a prior `composer install --no-dev` (the deploy step)
   prunes phpunit — run a dev `composer install` first.
2. **VC-2** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **0 FAIL** on the spoke
   checkout. (A throwaway `git worktree` shows 2 spurious FAILs — Check 4 spec_ref / Check 38 ADR043 — because
   it lacks the gitignored `_aos` governance cache; run on the real checkout.)
3. **VC-3** All build commits touch **only `sfa_delivery/`** (`git diff --name-only be6c8d7..154c89d`).

**CSS token-layer (the core fix)**
4. **VC-4** Served `redesign.css` has NO `*/`-bearing `--r-*/--sp-*` comment; `:root` resolves `--shell-max:1100px`,
   `--sp-4:16px`, `--r-l:16px`. On `/market/` the `main .shell` computes `max-width:1100px` (capped, centered),
   `.pgrid` = 3 columns with 16px gap (was 5 gapless full-width columns).

**Market grid → market.html**
5. **VC-5** `/market/` cards: `.pc__art` renders the watercolor `<img>` for crop-linked products (resolved via
   `book_slug`), line-glyph icon otherwise; prices/trend/`.fresh`/`.spark`/drill-down (range/median/28-day
   `.bigspark`/links) intact. Freshness-pill has NO stray leading dot (classb `.fresh::before` suppressed via
   `.pc__foot .fresh::before{content:none}`); the market DETAIL `.fresh--*` dot is preserved.

**Crop-book list → book_list.html**
6. **VC-6** `/crop-book/` renders the `.cc` watercolor grid (capped, gapped); **0 `.cc__icon` fallbacks** (the
   5 prod slugs scallions/salad-mix/pac-choi/bush-pole/corn now resolve via `SFA\Lib\CropArt`). `?view=table`
   (`.ptable`) still renders. Honest 2-stat card (yield/difficulty intentionally omitted — derived yield fails
   `test_ac05`).

**Home / crop page / calc / assumptions**
7. **VC-7** `/` hero shows the `.hub-intro__collage` watercolor strip beside the manifesto.
8. **VC-8** `/crop-book/{slug}` related-crops render watercolors (`.relcard .ph img`, was a hardcoded leaf);
   the `.glance` row shows no stray `–80` (range helper now requires both ends).
9. **VC-9** `/calc/` and `/assumptions` at mockup parity (came right from the token fix; no code change).

**Dead-code retirement (no regression)**
10. **VC-10** Deleted unused macros `price_card.php` + `freshness_pill.php`; removed dead old-card CSS (classb
    `.pcard*`; crop-book-v1 `.ccard*/.cards-grid/.seasonbar/.minibar/.cardviz`; mobile-fixes FIX1/FIX3 + scattered).
    Kept live `.fresh*`/`.spark*` (market detail), `.gj-cropcard*` (search), `.ptable*` (table). `ClassBRouteTest`
    + full qa_probe sweep confirm market-detail / search / community / about / account unaffected.

**Browser-QA (per CLAUDE.md — never validate layout with curl alone)**
11. **VC-11** `qa_probe.mjs --shots` on the 7 mockup surfaces + Class-B routes at mobile(375)+desktop(1440):
    `overflow=false`, all `http_rendered`, visual parity vs `mockups/`. Production sweep (8 surfaces × 2) = PASS.

## Out of scope (DECISION — not blockers)
- `cropdata_entry` mockup — its route was retired (commit `4324403`); not revived.
- Book↔market **₪ price-chip** never renders on `/crop-book/` (product/crop slugs don't align; `entry()` joins
  by slug only). Needs the `hebrew_name` fallback `resolveCropSlug()` already uses — flagged as a follow-up
  (closes the book→market price loop, the competitive #1 wedge). Backend + test; no schema.

## On PASS
team_100 closure protocol: archive mandate (team_191 `ARCHIVE_MANIFEST.md`) → roadmap `LOD500_LOCKED`.
