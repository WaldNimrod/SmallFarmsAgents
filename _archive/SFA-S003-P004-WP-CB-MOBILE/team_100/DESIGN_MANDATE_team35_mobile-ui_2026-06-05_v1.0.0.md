# DESIGN MANDATE — Mobile interface remediation (crop-book + market + /about) — team_100 → team_35 — v1.0.0

**Date:** 2026-06-05 · **From:** team_100 (Chief Architect) · **To:** team_35 (Design — Claude Design env, UI/interface authority) · **Routed by:** team_00
**WP:** SFA-S003-P004-WP-CB-MOBILE (mobile launch-blocker remediation)

## You are
team_35 — the UI/interface **design authority** for the SFA spoke, working in the **Claude Design** environment. You produce the **design** (mobile layouts/specs/mockups) that team_10 implements. **You do NOT run visual QA on the live site** (no screenshot/compare capability — that is team_50's job after build, per team_00). Deliver design decisions + layout specs that a builder can implement verbatim.

## Where the system is (context — read first)
- **Product:** SFA — "מערכת ההפעלה של החווה הקטנה". Live at **https://sfa.nimrod.bio** (uPress; Hebrew/RTL; white-green brand `#f8fbf8`, hand-painted **watercolor** illustration system).
- **Recently shipped + LOCKED (desktop is launch-quality):** WP-CB-UI-FIDELITY + WI7 — number formatting, Hebrew units/category-chips, single crop hero, working season/dtm filters, **70 crop watercolor icons** (full set, transparent, in the Devora style), centered crop page, dunam units. Desktop passed the launch gate (team_190 L-GATE_V) + a full-system visual QA (team_50 + team_100, GO-WITH-FIXES, fixes shipped).
- **THE BLOCKER (team_00):** *"גם הספר וגם המחירון עוד לא מספיק טובים — בעיקר במובייל. זה חוסם את הפרסום."* The **mobile (375px)** experience of the crop-book and the price-list is not launch-ready. **This WP fixes mobile.** Desktop is fine — do not regress it.
- **Design SSoT:** Board-A (crop-book + calculator) / Board-B (hub/market/search/community/about/account) — HTML at `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/.../HANDOFF/design/`. The existing CSS lives in `sfa_delivery/public_assets/css/` (crop-book-v1.css, classb.css, etc.); the watercolor masters are at `…/CROP_ART_MASTERS/`.

## The concrete mobile defects (team_100 CDP audit @375, evidence on request)
1. **Crop page hero — overlaps/crams on mobile.** The app-shell logo blob + the crop title (חסה) + the crop watercolor stack and overlap at the top. Needs a clean mobile hero.
2. **Crop page planting calendar — unreadable on mobile.** 12 month-chips × ~6 repeated rows, tiny; and it **leaks raw region codes (`IL_general`)** as labels. Needs a mobile-legible calendar (and the raw token gone).
3. **Market list — one card per row → ~12,500px scroll** for 65 products; each card is mostly empty space (big price, empty glyph box). Needs a compact, dense, scannable mobile product row/card.
4. **Crop-book entry cards — the DTM number dominates the crop name**; 2-col, ~8,800px scroll for 70 crops with no effective pagination. Needs a clearer card hierarchy (crop identity first) + a length/pagination strategy.
5. **General:** card content hierarchy, type scale, tap targets, spacing at 375.

## Also in scope — /about clarity (team_00)
`/about` currently has **5 tiers** (כלים לקהילה/OPEN · בטא ניסיוני/BETA · בקרוב/COMING · כלים מתקדמים/PAID · בדיוק לחווה שלך/CUSTOM) — *"יותר מדי אלמנטים, לא מספיק ברור מה פעיל ומה לא."* **Redesign for instant clarity of what's available NOW vs in development** — collapse/simplify; the user must understand at a glance.

## Deliverable
`_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-MOBILE/MOBILE_DESIGN_v1.0.0.md` (+ any mockup frames). For each surface give: the mobile layout (structure, what shows, hierarchy, sizes/spacing in CSS terms), the card/component design, and the /about simplification. Use the existing brand + the 70-watercolor system. Specs must be implementable by team_10 verbatim. Notify team_100.

## Flow
team_35 DESIGN → team_100 review → team_10 BUILD → team_99 deploy → **team_50 VISUAL QA @375** (team_35 does not screenshot) → team_100 record. The `IL_general` raw-token leak (defect #2) team_100 may fix immediately as a quick win independent of this design pass.
