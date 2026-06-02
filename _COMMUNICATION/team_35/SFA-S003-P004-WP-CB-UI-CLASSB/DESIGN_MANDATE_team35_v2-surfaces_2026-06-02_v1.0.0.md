# DESIGN MANDATE — SFA-S003-P004-WP-CB-UI-CLASSB — team_100 → team_35 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect)
**To:** team_35 (Design Studio)
**WP:** SFA-S003-P004-WP-CB-UI-CLASSB
**Type:** DESIGN_MANDATE (extend your v2 LOD300 to the remaining product surfaces)
**Design SSoT to extend:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/`
**Return to:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/`

---

## 0. TL;DR
Your LOD300 designed the **v2 white-green** system for **2 surfaces** (Crop Book + Calculator) — your README
says the rest are "stable nav hooks for future modules." Those other surfaces are now LIVE but still wear the
**old cream "Cool Stone" WP-UI skin**, which your v2 explicitly retired. team_00's directive: the **whole
interface** must be faithful to your v2 design. We implement the screens you already designed (Class A). For the
**6 surfaces below you have NOT designed in v2**, we need your templates — we will NOT guess (guessing is what
created the drift). Design **layout/style/structure/states**; we wire content/fields from code.

## 1. Anchors (binding — keep it ONE system)
- Build on your existing **`tokens.css`** (`--gj-*` white-green: `--gj-paper #f8fbf8`, `--gj-leaf/sun/tomato/
  soil/code`, type Assistant / Frank Ruhl Libre / JetBrains Mono / **Carmela** wordmark). **No new palette. No cream.**
- The **app-shell** is `.sh` + `.sh__nav` (▤ ספר גידולים [leaf] · ∑ מחשבון [sun] · ₪ מחירון [tomato] + `.sh__acct`
  "החשבון שלי") + `.sh__nav--mobile` 4-item bottom bar + `#sfa-logo` symbol — per your `spec/COMPONENTS-delta.md`
  §24 + Brand note. **team_100 is building this shell now (Class A).** Your Class B frames must sit inside it —
  design the **content** of each surface, assuming the shell is already there.
- RTL Hebrew production copy; English only as design annotations. Slim4/PHP + light vanilla JS (no SPA).
- Board conventions identical to your LOD300: frames carry `data-screen-label`; spec chrome is review-only.
- Reuse the **watercolor masters** where a surface shows a crop/product (28 crop masters + 3 module heroes already
  exist in `…/HANDOFF_PACKAGE/CROP_ART_MASTERS/` / `sfa_delivery/public_assets/img/`); glyph/icon otherwise.

## 2. Live references (see the current cream state you are replacing)
All on the live tier — open each and compare to your v2 intent:

| Surface | LIVE URL | Current template (we re-skin to your v2) | Current controller | team_50 screenshot (current cream state) |
|---|---|---|---|---|
| Hub / Home | https://sfa.nimrod.bio/ | `sfa_delivery/templates/pages/hub_home.php` | `HubController::home` | `_COMMUNICATION/TEAM_50/SFA-S003-P004/e2e_evidence_2026-06-02/desktop__home.png` + `mobile__home.png` |
| Market list | https://sfa.nimrod.bio/market/ | `templates/pages/market_list.php` | `MarketViewController::index` | `desktop__market.png` · `mobile__market.png` |
| Market detail | https://sfa.nimrod.bio/market/{slug} | `templates/pages/market_product.php` | `MarketViewController::detail` | `desktop__market-product.png` · `mobile__market-product.png` |
| Search | https://sfa.nimrod.bio/search?q=עגבני | `templates/pages/search_results.php` | `HubController::search` | `desktop__search.png` · `mobile__search.png` |
| Community | https://sfa.nimrod.bio/community | `templates/pages/community.php` | `HubController::community` | `desktop__community.png` · `mobile__community.png` |
| About / Tiers | https://sfa.nimrod.bio/about | `templates/pages/hub_tiers.php` | `HubController::tiers` | `desktop__about.png` · `mobile__about.png` |
| Account (hook) | (nav item, no page yet) | — (to create) | — | — |

The cream skin you are replacing lives in: `public_assets/css/{hub,community,desktop,gj}.css` + the legacy shells
`templates/shell/{desktop,mobile}.php`. Your v2 reference (for tone/components) is the LOD300 board:
`…/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` (open it; the book + calc frames are the style target).

## 3. Deliverables (per surface — same artifacts as your LOD300)
For each surface: a **board frame** (the `.sh` shell + real product UI only — no spec chrome), the **component
classes**, and any **token/CSS delta**. Priority order (deliver top-down; 3.1–3.3 unblock the most build):

### 3.1 App-shell reference frame (CONFIRM/REFINE)
We are building `.sh`/`.sh__nav`/`.sh__nav--mobile`/`#sfa-logo` from your §24 contract. Please provide the
**definitive rendered frame** of the shell wrapping a generic (non-crop-book) page, so our build matches your
intent exactly (header composition, nav spacing, active-state colors, account button, search affordance, mobile
tab bar). If §24 as written is sufficient, reply "shell as specced — no change."

### 3.2 Hub / Home (`/`)
Module-grid landing: cards for ספר גידולים · מחשבון · מחירון + coming-soon modules (מתכנן · לקוחות · מלאי · Tend ·
יומן-שדה). Each card: watercolor/icon hero, title, **tier badge** (open/beta/coming/paid/custom), one-line
description, stat. States: default grid · coming-soon (disabled) card · hover. (3 module heroes already exist:
calc/market/crop-book.)

### 3.3 Market / Pricelist (`/market/` + `/market/{slug}`)
This is the OrganicMarketAgent community price index.
- **List:** price cards (product · current price · range · #sources · freshness) + the **mandatory market
  disclaimer** (keep its 4 bullets). Empty/stale states.
- **Detail:** big current price · price-history table · stats · source breakdown · disclaimer · cross-link to the
  crop in the book.

### 3.4 Search (`/search?q=`)
Unified results across crops + market products: result rows/cards, empty state, no-match state, query echo.

### 3.5 Community (`/community`)
Lightweight per your Q5: contact card + activity/feed surface + the **"request / suggest" CTA** (low-friction
capture, NOT a live community-management UI).

### 3.6 About / Tiers (`/about`)
The 5-tier explainer (open · beta · coming · paid · custom) with your tier badges + descriptions.

### 3.7 Account (`/account` — nav hook)
At minimum a v2 placeholder/landing for the 4th nav item (login/profile shell + empty state) so it isn't a dead
end. Full account flows can be a later module.

## 3.8 Reference patterns (Mobbin) — borrow the UX PATTERN, not the skin
team_00 asked which existing apps to use as references while you design. Use **Mobbin** to study the
**interaction/layout pattern** of each surface — then dress it in **our locked v2 system** (`tokens.css`,
white-green, Carmela, watercolor). ⚠ Reference = pattern/structure/flow only. Do NOT borrow another app's
palette, type, or chrome — that would re-introduce the exact drift this WP exists to fix.

**Primary whole-product anchor: Planta** (plant-care app) — closest DNA to SFA: light/white ground, botanical
illustration, a plant **library (cards → detail → depth)** + **planning** surfaces. One app that mirrors most of
our structure. Secondary: **Greg** (plant hub + per-item state, ~ our complete/partial cues).

| Surface | Mobbin reference pattern | What to take (pattern only) |
|---|---|---|
| 3.1 App-shell | Planta / Notion / Arc — top bar + section nav; mobile bottom tab bar | nav composition, active-state, RTL bottom-tab ergonomics |
| 3.2 Hub / Home | Notion / Arc / Flighty home launchers; Planta home | module-card grid, hero+badge+stat, coming-soon (disabled) card |
| 3.3 Market list+detail | Copilot Money / Delta (price + history) ; Blinkit/Zepto price views | big current price, range, history table, source breakdown |
| 3.4 Search | Planta / NYT Cooking unified search | result cards across types, empty + no-match states |
| 3.5 Community | Strava/Duolingo light feed + a simple "suggest" CTA | low-friction feed + capture (NOT a management console) |
| 3.6 About / Tiers | Pricing/tier screens (Notion, Linear) | 5-tier explainer cards + badges |
| 3.7 Account | Any settings/profile shell (Planta, Wolt) | login/profile shell + empty state |
| **RTL anchor (all)** | **Wolt · Bit (בנק הפועלים) · Riseup** — native Hebrew RTL | correct RTL nav, bottom-tab, forms, number/price direction |

Rule of thumb to give the team: *"Take the **UX pattern** from {Planta / Notion / YNAB / Copilot / Wolt-RTL},
apply **our v2 tokens** to it."* If a pattern conflicts with the v2 token system, the token system wins.

## 4. Constraints / out of scope
- Do NOT redesign the crop-book/calculator screens you already delivered, nor the data/fields (we wire content).
- No backend/calculator math.
- If a surface is lower priority for you, deliver **3.1 shell + 3.2 hub + 3.3 market first** — they unblock the
  largest share of the Class B build.

## 5. Return path + what happens next
Drop the extended package into `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/` (board HTML +
CSS/token deltas + a short COMPONENTS/TEMPLATES delta for the new surfaces). On receipt: team_100 embeds it into
the WP-CB-UI-CLASSB LOD400 → team_190 L-GATE_S → team_10 build (reusing the Class A app-shell) → team_50 **visual**
QA (design-vs-live per screen) → team_190 L-GATE_V (non-Claude). WP-CB-UI-CLASSB is currently **BLOCKED on this
delivery** + team_00 approval.

*Issued by team_100 · 2026-06-02*
