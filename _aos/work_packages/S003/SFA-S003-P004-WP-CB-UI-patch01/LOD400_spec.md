---
id: SFA-S003-P004-WP-CB-UI-patch01-LOD400
wp: SFA-S003-P004-WP-CB-UI-patch01 — UI polish: crop-book entry density + hub full-width / Field-Log tile
gate: L-GATE_S (delegated team_100 — delivery-tier-only cosmetic) → build
status: LOD400_LOCKED (delegated L-GATE_S)
author: team_100 (Claude Opus)
date: 2026-06-03
trigger: team_00 live feedback on sfa.nimrod.bio (/crop-book/ cards oversized; / hub tools not full-width)
branch: claude/ui-polish-hub-cropbook-2026-06-03 (off main 3bceeea/fdbc2c5)
orchestration: build=team_10 (Sonnet) · verify=team_100 (Opus) · deploy=team_99 · validate=team_190 (non-Claude)
scope: DELIVERY-TIER ONLY (sfa_delivery templates + CSS). No _aos/Python/migration/backend.
---

# LOD400 — WP-CB-UI-patch01: crop-book density + hub full-width / Field-Log

team_00 live feedback (2026-06-03), two delivery-tier UI fixes. Cosmetic, delivery-tier only → delegated
L-GATE_S (precedent: WP-CB-1-patch01). team_190 confirms live at L-GATE_V.

## WI-1 — `/crop-book/` entry page: compact, fit-to-screen (book_entry.php + crop-book-v1.css / crop-book-deep.css)
**Problem:** the crop index renders ~66 `.ccard` cards at `.cards-grid { minmax(168px,1fr) }` with a tall
`.ccard__art` (aspect-ratio 1.3/1) → the page is absurdly long; cards are oversized. Hero + entry-path block
add height.
**Goal:** a **dense** grid so many crops are visible per screen with minimal scrolling; cards visibly smaller.
- `.cards-grid` (crop-book-v1.css L33): reduce track min from `168px` → **~116–128px** (more columns); keep gap tight (~10px).
- `.ccard__art` (L41): reduce visual height — flatten aspect-ratio (e.g. `1.6/1` or fixed ~74px) and/or shrink `.veg` font (46px → ~30px) + img footprint; keep state dot.
- `.ccard__body` (L?) + `.ccard__name` (16px→~13px), tighten padding (`10px 12px`→~`6px 8px`) and gaps.
- `.cb-hero` (crop-book-deep.css): trim height/art so it doesn't dominate the fold (smaller hero on this page).
- Keep the entry-path block (`.cb-paths`) but it may be condensed; do not remove functionality (filters/search/audience toggle stay).
- **Acceptance:** at desktop ≥1280px, the crop grid shows **markedly more cards per row + per viewport** than today (target ≥5–6 columns vs ~current); cards are compact; no layout break, RTL intact, no horizontal overflow. Mobile still single/few-column + legible.
- NOTE (team_00): the page is considered partly redundant — this patch only **compacts** it (no removal/redirect; a deprecation decision is separate).

## WI-2 — `/` hub: full-width open-tools row + 4th "Field Log" in-development tile (hub_home.php + classb.css)
**Problem:** `.hub-grid { grid-template-columns: repeat(auto-fill, minmax(248px,1fr)) }` (classb.css L55) — with 3
open tools the `auto-fill` leaves an empty track, so the row doesn't fill the width.
**Fix (both):**
- Change `auto-fill` → **`auto-fit`** on `.hub-grid` so the tiles always stretch to fill the row width
  (applies to both the open-tools grid and the soon grid; verify the soon row still reads well).
- **Add a 4th tile to the OPEN-tools row** for the next feature **"יומן השדה" (Field Log)**, marked
  **"בפיתוח" (in development)** — non-clickable, styled like a disabled/teaser tile:
  - Append after the `$open_mods` loop in the open-tools `.hub-grid` (hub_home.php ~L130) a `.modtile.is-dev`
    (new modifier; mirror `.is-soon` non-interactive styling) with: glyph (e.g. field/journal icon — reuse an
    existing sprite or a 📒/🌾 fallback), title **יומן השדה** + small **FIELD-LOG**, desc e.g.
    *"תיעוד פעולות שדה — זריעה, השקיה, יבול ומשימות"*, and a foot badge **"בפיתוח"** (use tier_badge or a
    `.modtile__go` "בפיתוח"). `aria-disabled="true"`, no href.
  - Add `.modtile.is-dev` CSS (mirror `.is-soon`: no hover lift, muted bg `--gj-paper-2`, default cursor).
- Result: the open-tools row shows **4 tiles filling the full width** (3 live + Field-Log "בפיתוח").
- **Acceptance:** at desktop the open-tools row spans the full content width (no trailing empty gap); the 4th
  tile renders "יומן השדה / בפיתוח", is non-clickable, palette-consistent; existing 3 tiles unchanged in function.

## Tests + verification
- Extend `sfa_delivery/tests/` (ClassBRouteTest or a crop-book route test): assert the Field-Log tile markup
  is present on `/` (text "יומן השדה" + "בפיתוח", `is-dev`, no href) and `.hub-grid` uses `auto-fit`; assert
  `/crop-book/` still 200 and `.cards-grid`/`.ccard` present.
- `composer test` green; `php -l` clean on touched templates; `validate_aos.sh` 0 FAIL.
- Visual: builder checks the live-equivalent render (local PHP server) — crop grid dense, hub row full-width.

## Constraints
- Delivery tier ONLY. No `_aos/`, Python, migration, backend. IR#4 (no roadmap edits by builder). No git by builder.
- Palette/tokens unchanged (white-green); no new cream; classb.css stays last in load order.
- "יומן השדה / Field Log" is a **teaser only** (PLANNED, not built) — must read as "בפיתוח", never as available.
