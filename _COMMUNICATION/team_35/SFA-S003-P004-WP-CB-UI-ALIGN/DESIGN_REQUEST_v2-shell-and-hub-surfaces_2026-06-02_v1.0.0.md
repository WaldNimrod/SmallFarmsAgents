# DESIGN REQUEST — SFA-S003-P004-WP-CB-UI-ALIGN — team_100 → team_35 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect)
**To:** team_35 (Design Studio)
**WP:** SFA-S003-P004-WP-CB-UI-ALIGN
**Type:** DESIGN_REQUEST (extend the LOD300 design package)
**Design SSoT:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/` (your v2 package — extend it)

---

## Why this request

Your LOD300 package (Crop Book v1) designed the **v2 white-green** system for **two surfaces only** — by your
own README: *"This WP builds the Crop Book and Calculator surfaces; the others are stable nav hooks for future
modules."* We implemented those two.

But the **live product has more surfaces** — hub/home, market, search, community, about, account — and they are
still rendered in the **earlier cream "Cool Stone" WP-UI style**, which your v2 package explicitly retired
(*"do not revert to cream/brown"*). The result: the site is visually inconsistent — crop-book/calculator look
v2, everything else looks like the old kit. team_00's directive: **the whole interface must be faithful to the
team_35 v2 design.**

We can implement the look ourselves for screens you already designed. For the surfaces you have **not** designed
in v2, we need your templates — otherwise the build team will guess (which is how the drift started). This is
that request.

## What we ALREADY have from you (no action needed — we will implement to these)
- `tokens.css` (v2 white-green palette, type, spacing, radii, shadows, Carmela).
- `cropbook-v1.css` + `cropbook-v1.js` (component + behavior layer).
- App-shell contract: `.sh` + `.sh__nav` (desktop nav ספר/מחשבון/מחירון/חשבון) + `.sh__nav--mobile` (bottom
  tab bar) + `#sfa-logo` symbol — described in `spec/COMPONENTS-delta.md`.
- Screens designed: book-entry, crop page (simple/full/drill), calculator dashboard.

## What we NEED from you (the gap — please design in the SAME v2 board format)

For each, deliver the same artifacts as the LOD300 package: a board frame (`.sh` shell, real product UI only —
no spec chrome), the component classes, and any token/CSS deltas. **Hebrew RTL, white-green v2, Carmela
wordmark, watercolor where relevant.** Content/fields are wired by us from code — you own **layout, style,
structure, states**.

### 1. App-shell — the canonical v2 frame (HIGHEST priority)
You specified `.sh__nav` in COMPONENTS-delta but there is no rendered reference frame for the **global shell as
it wraps a NON-crop-book page**. Please provide the definitive shell: header (logo + wordmark + `.sh__nav`
ספר/מחשבון/מחירון/חשבון + account + search affordance), the desktop layout, and the mobile bottom tab bar —
shown wrapping a generic content area. This is the frame every page below sits inside.

### 2. Hub / Home (`/`) — module grid landing
The product's front door: a grid of module cards (ספר גידולים, מחשבון, מחירון, + "coming soon" modules:
מתכנן, לקוחות, מלאי, Tend, יומן-שדה). Each card: watercolor/icon hero, title, tier badge (open/beta/coming/
paid/custom), one-line description, stat. We have watercolor module heroes for calc/market/crop-book already.
Show: default grid, a "coming soon" (disabled) card state, hover state.

### 3. Market / Pricelist (`/market/` + `/market/{slug}`)
- **List:** price cards (product, current price, range, source count, freshness) + the mandatory market
  disclaimer. This is the OrganicMarketAgent community price index.
- **Detail:** big current price, price-history table, stats, source breakdown, disclaimer, cross-link to the
  crop in the book.

### 4. Search (`/search?q=`)
Unified results across crops + market products: result rows/cards, empty state, no-match state.

### 5. Community (`/community`)
Lightweight: contact card + an activity/feed surface + the "request info / suggest" CTA (per your Q5 — a
low-friction marketing/feature-idea capture, not a live community-management UI).

### 6. About / Tiers (`/about`)
The 5-tier explainer (open / beta / coming / paid / custom) with tier badges.

### 7. Account (`/account` — nav hook)
At minimum a v2 placeholder/landing for the account nav item (login/profile shell) so the 4th nav item isn't a
dead end. Full account flows can be a later module — we just need the shell + empty state.

## Constraints / anchors (so it stays one system)
- Build on your **existing `tokens.css`** — same `--gj-*` palette, type stack (Assistant / Frank Ruhl Libre /
  JetBrains Mono / Carmela), spacing, radii, shadows. No new palette.
- RTL Hebrew production copy; English only as design annotations.
- Reuse the watercolor masters where a surface shows a crop/product; glyph/icon fallback otherwise.
- Same delivery tier: **Slim4 / PHP + light vanilla JS** — server-rendered, no SPA. Keep JS light.
- Same board conventions as the LOD300 (frames carry `data-screen-label`; spec chrome is review-only).

## Deliverable + return path
Drop an extended package (board HTML + any CSS/token deltas + a short COMPONENTS/TEMPLATES delta for the new
surfaces) into `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-ALIGN/HANDOFF/`. We will embed it into the
WP-CB-UI-ALIGN LOD400 and implement. If any surface is lower priority for you, deliver the **app-shell (#1) +
hub (#2) + market (#3) first** — those unblock the most of the build.

## What we do NOT need
- No data/field design (we wire content from code).
- No backend / calculator math (already built + tested).
- No re-design of the crop-book/calculator screens you already delivered — only the missing surfaces + the
  definitive shell frame.

*Issued by team_100 · 2026-06-02 · pending team_00 approval of WP-CB-UI-ALIGN LOD200 (this request can run in parallel — design lead-time).*
