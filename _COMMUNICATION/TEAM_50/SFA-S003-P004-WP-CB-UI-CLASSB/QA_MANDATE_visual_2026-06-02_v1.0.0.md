# QA MANDATE (VISUAL) — SFA-S003-P004-WP-CB-UI-CLASSB → team_50 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_50 (QA & Functional Acceptance) · **Gate:** pre-L-GATE_V QA
**Branch:** `claude/wp-cb-ui-align-2026-06-02` (build tip `4695fc7`)

## Why this mandate exists
WP-CB-1 shipped twice through functional QA (200-OK / 0-console-errors) yet did NOT match the team_35 design — the
gap that triggered the whole UI-ALIGN program. **This QA's job is the standard that was missing: per-screen
design-vs-live visual fidelity**, not just "does it load."

## Scope — 7 Class B surfaces × {desktop, mobile} = 14 captures
For each surface, capture a **design-vs-live pair** and compare against the team_35 Board-B frame:

| Surface | Route | Board-B frame (`data-screen-label`) |
|---|---|---|
| Hub / Home | `/` | `hub-home` / `hub-home-mobile` |
| Market list | `/market/` | `market-list` |
| Market detail | `/market/{slug}` | `market-detail` |
| Search | `/search?q=…` + no-match | `search-results` / `search-nomatch` |
| Community | `/community` | `community` |
| About / Tiers | `/about` | `about-tiers` |
| Account | `/account` | `account` / `account-profile` |
+ App-shell (header nav + mobile bottom tab + footer) on every page.

## Reference (the visual truth)
- Design board: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html` — open each frame, screenshot the `.sh` shell (ignore review chrome `.board/.sec/.frame/.notes/.patref`).
- Tokens: white-green v2 (`--gj-paper #f8fbf8`, no cream), Carmela wordmark, Assistant/Frank-Ruhl type.

## Environment
- LOCAL build at `4695fc7`: `cd sfa_delivery && composer install && php -S localhost:8080 -t .` (needs a seeded MySQL; without it pages render empty-states — still valid for shell/layout/palette checks).
- OR LIVE `https://sfa.nimrod.bio` **only if** the Class B build has been deployed (check deploy status first — it may not be live yet; if not, QA local). Read-only.

## Per-surface checks (report PASS / PASS_WITH_FINDINGS / FAIL each)
1. **Visual fidelity vs Board-B**: palette (white-green, no cream), type, spacing, component look — does the live screen match the frame? Attach the design-vs-live pair.
2. **Computed palette** (the WP-CB-1 lesson): `body` background computes to `#f8fbf8` (verify via inspector/computed style, not eyeball). No cream `#f5f3ec` anywhere.
3. **App-shell**: `.sh__nav` desktop (ספר/מחשבון/מחירון active colors) + `.sh__nav--mobile` 4-tab + `.sh__search` + footer present + correct.
4. **The 7 minors actually rendered**: `.mkt-disc` disclaimer always-on w/ locked 4-bullet copy; graph range labels **7י/28י** + **90י/שנה disabled**; community **feed-less** (manifesto + reqcard, no feed); search rows show **no fake min/max/source counts**; reqchips present; classb assets loaded.
5. **Honest-data**: 0-report market product → `.pcard.is-empty` (— + תרמו מחיר), not a fake price; empty market history → `.emptybox`; no-match search → `.srch-nomatch` + request CTA.
6. **States**: hub coming-soon (`.is-soon`) cards; account "בקרוב" labels; cards⇄table toggle on market; freshness pill 3-state.
7. **RTL legibility**; no raw DB keys / "Array" / stray "—" where a value should be.

## Scenario matrix (GCR-002) where applicable
market filter (happy/empty), search (match/no-match), community reqchip select, market cards⇄table toggle, graph range select (7/28 active, 90/year disabled).

## Out of scope
The 1 known suite failure `CropBookV1RouteTest::testCalcExportPdfReturnsPrintHtml` is a **Class A** stale test
(already flagged to WP-CB-UI-ALIGN) — not Class B. Crop-book/calculator screens (Class A). Backend/data population.

## Deliverable
`_COMMUNICATION/team_50/SFA-S003-P004-WP-CB-UI-CLASSB/VISUAL_QA_REPORT_2026-06-02_v1.0.0.md` — per-surface table
(surface | desktop fidelity | mobile fidelity | findings) + the 14 design-vs-live screenshot pairs in an evidence
dir + overall verdict (PASS / PASS_WITH_FINDINGS / FAIL) + findings by severity. Real bugs → team_100 routes a
build fix to team_10; cosmetic → batch for team_00. On QA PASS → team_100 routes team_190 L-GATE_V (non-Claude).

*Issued by team_100 · 2026-06-02.*
