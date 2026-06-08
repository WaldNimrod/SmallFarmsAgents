# SFA UI — UX Direction Brief (v0.1, DRAFT for visual approval)

**Author:** team_100 (Chief Architect) · **Date:** 2026-06-06 · **Status:** DRAFT — pending team_00 visual approval of mockups
**Trigger:** team_00 directive (2026-06-06) — "the UI is below criticism; rethink content structure, flow, clarity, readability."

> This is a **direction brief + mockup set for approval**, NOT a build LOD. No production templates are touched until team_00 approves the visual direction. Mockups are standalone HTML built on the LOCKED Design System v3 tokens (`tokens.css`).

---

## 1. Root diagnosis (one cause, many symptoms)

The UI is **organized around our data model and editorial provenance, not around the farmer's task.**

Evidence in the code:
- Crop detail is structured by **3 data-completeness depths** (`Simple/Full/Deep`) and **13 storage "topics"** (`crop_topics`) — an editorial taxonomy, not a journey. (`templates/pages/book_crop.php`)
- Every field drags its `field_state` (VALIDATED/UNVALIDATED/PROPOSED), `source_class` (EX/PR/WR) and `confidence_score` onto the surface. That is an internal trust model leaking into the public UI.
- Default container for every datum is a card/panel → "many stripes & cubes, little information."
- Listing cards render a DB row (name · latin · family · DTM) and the controller **computes `in_season` then discards it** instead of showing it. (`CropBookViewController` / `crop_card.php`)
- No shared width container: `.hub-home__inner{max-width:1100px}` is scoped to the home page only; `.sh__body` and `.sh__bar` run full-bleed → home is bounded, everything else isn't; logo only tuned for home. (`classb.css`, `_layout.php`)

**The fix is one move:** flip the organizing principle from *"how the data is stored & how trustworthy it is"* → *"what the farmer came to do."* Provenance becomes optional background, not the headline.

## 2. Design principles (proposed)

1. **Journey over taxonomy.** The crop page is a lifecycle: *when → how → care → yield.* Not 13 topics × 3 depths.
2. **Every surface answers a decision.** A listing card answers "should I grow this / can I plant it now." A calc answers one question with one number.
3. **Provenance is progressive disclosure.** One quiet "show sources & variety ranges" toggle — never a parallel page.
4. **Density via tables/`dl`, not boxes.** Reserve cards for genuinely card-like objects.
5. **One shell, one width, everywhere.** Header + body share a single max-width container token. Readable baseline type.
6. **Close the production→profit loop** (our #1 competitive wedge): yield → beds-for-target → revenue, reachable in-context from the crop page.
7. **Our illustration set is the visual identity.** Use the existing ~70 watercolor crops (`sfa_delivery/public_assets/img/crops/wc-*.png`) everywhere — hero, listing cards, related crops. No emoji, no new/invented art.
8. **Every crop has a story.** A prose narrative ("the story of the vegetable") + the full in-season care/treatment regime are first-class page content, not afterthoughts.
9. **Universal drill-down replaces a separate "farmer mode"** (team_00, 2026-06-07 — supersedes the gardener/farmer toggle). Every section is a card that **shows the central data when closed and reveals the depth when opened** (ranges, sources, formulas, technical fields). One general level + clear per-topic drill-down serves both the curious gardener and the data-hungry farmer — no parallel interface. This is the building block of the *whole* UI, not just the care section.
   - **Two-level knowledge ⓘ on every field:** hover = short definition tooltip with a "expand" link → click opens a **knowledge module above the page** (definition + how-it's-computed formula + source + "contribute a correction"). This builds SFA as a knowledge brand.
10. **Interlink everything.** Each crop links to its **market price** (מחירון), its **calculator** (pre-filled), **complementary content** on nimrod.bio (guides, workshops), and sibling crops — and reciprocally. Close the loops between the three modules.
11. **Assumptions are a managed, scalable surface.** Base parameters (bed width, germination %, …) live in a dedicated **"הנחות היסוד שלי"** screen: collapsible groups, search, per-row "used-in" chips, community default + reset, advanced group collapsed. Built to grow to hundreds of parameters without overwhelming. They flow into every calculator and every derived number in the book.

## 3. Per-screen decisions

| Screen | Now | Proposed |
|---|---|---|
| **Crop card** | 13 topics × 3 depth pages; provenance everywhere; no narrative; emoji art | real watercolor hero; **story section** (prose narrative); lifecycle spine סיפור→מתי→איך→**טיפול לאורך העונה** (full in-season regime: irrigation/feeding/training/pests+disease/companions)→**יבול צפוי**; sticky stage-nav; one sources toggle; yield→revenue callout + calc handoff |
| **Book listing** | sparse cards (drawing+name); 5 filters hidden behind "advanced"; `in_season` discarded | decision cards (now/next badge + days + yield + difficulty); always-visible filters + sort + view toggle; "23 available to sow this month" |
| **Calculator** | 14 buttons, 8 are "coming soon"; assumptions hidden until first result | only the 6 working calcs prominent; 8 pending demoted to a quiet "in development" list; assumptions panel always visible; auto-filled from the originating crop |
| **Shell** | home bounded, rest full-bleed; logo only good on home | single `--shell-max` container on header+body across all pages; consistent logo lockup |

## 4. Mockups (open in a browser)

Standalone, on-brand, responsive (verified desktop + mobile). **Full set — all surfaces now at the same level/style:**
- `mockups/home.html` — hub home (entry → 3 tools → audiences → manifest → contribute)
- `mockups/book_list.html` — crop index
- `mockups/crop_card.html` — the centerpiece (universal drill-down + knowledge ⓘ)
- `mockups/calc.html` — planning calculator: **15-goal builder** + live time-anchor + frost region picker + **all 5 result shapes** (scalar / DATE / DATE RANGE / DATE LIST / RANKED LIST) + honest no-data state + session + export (serves WP-CB-CALC; see `SFA-S003-P004-WP-CB-CALC/MOCKUP_RETURN_team35_*.md`)
- `mockups/cropdata_entry.html` — internal guided-entry tool (fast `planting_method` + `frost_class` classification; WP-CB-CROPDATA-DATES)
- `mockups/market.html` — community price index (drill-down cards: range/median/sources/28-day trend + book & calc cross-links)
- `mockups/assumptions.html` — "הנחות היסוד שלי" management screen (scalable)
- `mockups/mock.css` — shared shell + tokens
- `mockups/wc/` — real watercolor crop illustrations + module art

Local serve: `ui-redesign-mockups` launch config (php -S :8097).

## 5. Open questions for team_00

1. Is the **lifecycle spine** the right organizing model for the crop page? (the biggest bet)
2. Difficulty/"can plant now"/expected-income shown publicly — agronomy comfortable with these as headline facts?
3. Scope of first build WP: all-screens shell+listing+crop, or crop-card-first?

## 5a. Round-2 refinements (team_00, 2026-06-07) — folded into mockups v4

**Crop page:**
- Audience switch moved to **top, first element** (primary control).
- "סיפור" → concise **תקציר** merged into the hero (dignified, short); **complementary content** (nimrod.bio guides/workshops) linked there at the top, not at the bottom.
- **Treatments are expand-to-detail** (collapsible per topic, teaser when closed).
- **Companions link to their crop pages** in the book.
- **Contribute CTA** per crop ("found a missing/wrong value?") → tailored form.
- **Organic angle:** fertilizer shown also as **compost equivalent** (we target organic farming).
- **Every field carries a ⓘ** → "what it is + how it's computed" explanation.
- **Nursery vs. field data separated** into two sub-blocks (גידול שתילים במשתלה ⇄ שתילה בשדה).
- **Lead with in-row spacing + rows → plants per running meter / per 100 m**; plants/m² demoted to a secondary (farmer) stat.

**Calculator:**
- **Editable calc variables** (in-row spacing, rows, bed length) pulled from the crop + defaults; **bed length set → compute per bed**.
- Farmer-relevant fields + ⓘ explanations, consistent with the crop page; audience switch present.
- **File export** (PDF / CSV) of the result, with a visible computation breakdown.

## 5a-2. Round-3 refinements (team_00, 2026-06-07) — folded into mockups v5

- **Dropped the gardener/farmer toggle** → **universal drill-down** (closed card = key data for everyone, open = depth). Applied to stages 2/3/4. This is now the core interaction model for the whole UI.
- **Two-level field ⓘ:** hover tooltip → **knowledge modal above the page** (definition + formula + source + "contribute a correction"). Knowledge-brand play.
- **Calculator button** moved to the **top header row, left end** (not bottom).
- **"איך לשתול" reworked** so it reads cleanly: collapsible "במשתלה" / "בשדה" cards; field planting **leads with a spacing×rows = plants/meter visual equation**.
- Contribute CTA kept on-page with a **code comment** marking it links to a tailored per-crop form.

## 5b. Content & data gap (IMPORTANT — surfaced 2026-06-07)

The redesign exposes a real **content gap**, not just a UI gap:
- **Story prose:** today only a single `description_he` paragraph exists. The schema contract defines `description_md` but the publisher does **not** deliver it yet → the rich "story of the vegetable" must be **authored + published** per crop.
- **In-season treatments:** the contract defines `care.{watering,fertilizing,pests}_md` (not yet delivered). Meanwhile **real treatment data already sits unused in fixtures** — e.g. `tests/crop_book/fixtures/ni/jmf_ft_phytoprotection/Tomatoes.json` (copper hydroxide / neem / kaolin spray schedule). The mockup's care section is populated from this real data to show intent.
- **Implication:** a full crop page needs a **content/data WP** (author story + wire `*_md` + surface the phytoprotection fixtures) alongside the UI WP. The UI can ship with graceful empty-states until content lands.

## 6. Next step

On visual approval → team_100 issues a LOD400 build mandate (UI-only, client-side per the standing Class B constraint) and a design handoff to team_35. No server/schema work implied.
