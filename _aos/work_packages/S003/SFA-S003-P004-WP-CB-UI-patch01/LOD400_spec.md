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

## WI-3 — Hub copy + system-wide terminology (team_00 round 2)
Customer-facing copy fixes (delivery-tier templates):
- **Typo:** `hub_home.php:177` audience card label **"גינאי ביתי" → "גנן"** (GARDENER). ("there is no 'home gardening', there is a gardener.")
- **One-line tagline:** the hub-intro tagline at `hub_home.php:77` is ALREADY the correct text
  *"ספר גידולים קהילתי, מחירון שוק בזמן-אמת, ומחשבון שדה — בנויים על ניסיון שדה ומחקר AI."* — the requirement is it must render on **ONE line (no wrap)** on desktop. Remove/raise the `.hub-intro p { max-width: 52ch }` cap (classb.css ~L41) and prevent the break at desktop width (e.g. `white-space:nowrap` at ≥760px with a responsive/clamped font-size); allow graceful wrap ONLY on small mobile — **no horizontal overflow** anywhere.
- **System-wide term — "small" → "local":** replace the positioning term across CUSTOMER-FACING templates:
  "חקלאות קטנה" → "חקלאות מקומית", "חקלאי קטן" → "חקלאי מקומי", "השוק החקלאי הקטן" → "השוק החקלאי המקומי".
  Targets: `_layout.php:6` (`$page_sub`), `hub_home.php:65` (`$page_sub`), `:76` (`<h1>כלים פתוחים לחקלאות <em>קטנה</em>`→`<em>מקומית</em>`), `:151` (`<h2>… לחקלאות <em>קטנה</em>`→`מקומית`), `:183` (`חקלאי קטן`→`חקלאי מקומי`), `community.php:53` (`חקלאות קטנה`→`חקלאות מקומית`), `macros/market_disclaimer.php:22` (`השוק החקלאי הקטן`→`המקומי`).
  **Do NOT** change unrelated "קטן/קטנה" (e.g. `hub_home.php:178` "לגינה הקטנה", `community.php:60` "תרומה קטנה", and the internal AI-art-generation prompt strings in `modules.php` — not rendered as positioning copy).
- **Remove Tend mentions (customer-facing):** team_00 — "the Tend connection is not in the plan and shouldn't be shown to customers." Read each occurrence in `hub_tiers.php`, `book_variety.php`, `book_entry.php` and: remove any **Tend integration/connection** teaser/tier copy entirely; where "Tend" appears as a **data-source brand label** shown to users, neutralize it to a generic term (e.g. "נתוני שדה" / "מקור תפעולי") — keep the underlying data, drop the brand name. (Internal `modules.php` art-prompt strings may stay — not user-rendered.)

## WI-4 — Hub CTA section (the page's primary call-to-action)
Add a prominent CTA section on the hub (`hub_home.php`, near the bottom — after the manifest band / soon-grid), `.hub-cta`, with **two offers** (this is the page's main CTA per team_00):
1. **"שתפו אותנו במידע והשלמות לספר"** — links to the dedicated contribution form: route to **`/community`** (which hosts the reqcard → `/api/v1/contribute`). Secondary emphasis.
2. **"ספרו לנו מה תרצו שנפתח לחווה שלכם — בקשות לפיצ'רים, רעיונות ופיתוחים ייעודיים"** — the **PRIMARY** CTA; link to the contact channel used on `/community` (WhatsApp `wa_num` 972547776770 via `Modules::all()['contact']`). Visually primary (filled button/card).
Style `.hub-cta` palette-consistent (white-green), RTL, responsive; reuse `.reqinfo`/button patterns where sensible; the second offer is the prominent action. No new backend/endpoint (reuse existing contribute + contact).

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

## WI-5 — FIX: compact `/crop-book/` entry-path cards (post-R1 live finding)
team_00 live screenshot showed the `/crop-book/` **entry-path cards** (`.cb-paths .mod-card` — "שאלות מובילות"
/ "משפחות בוטניות" / table / search) rendering **giant** (full-width single-column × `.mod-card__art`
`aspect-ratio:2/1` → ~550px-tall cards with a blown-up leaf icon). WI-1 had densified the wrong cards (the
`.ccard` crops grid). FIX (team_100, crop-book-v1.css, scoped to `.cb-paths`): make `.cb-paths` a tight
responsive grid `repeat(auto-fit, minmax(190px,1fr))`; cap `.mod-card__art` to `height:54px` (aspect-ratio
auto); shrink the no-image icon svg to ≤28px; tighten body padding; 2-col on ≤600px. Result: the
"איך תרצו להיכנס?" entry section reads as 4 compact cards in one band — fits screen, no giant box.
