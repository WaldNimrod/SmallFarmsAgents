# M8–M10 Detailed Specification — Team 80 Recommendations Integration

**Date:** 2026-04-02
**From:** Team 100 (Architecture)
**Status:** APPROVED BY NIMROD — ready for mandate issuance
**Source:** Team 80 handoff packages (`sfa_handoff_v2/`, `smallfarms_agent_handoff/`)

---

## Overview

This document provides the detailed specification for milestones M8–M10, derived from
Team 80's product recommendations, filtered through Team 100's architectural review,
and approved by Nimrod.

All items reference the approved plan: `M8+ Roadmap from T80`.

---

## M8 — UX Polish + Policy Formalization

**Scope:** Quick wins that improve the existing public page without new infrastructure.
**Teams:** Team 10 (template changes), Team 80 (SEO guidance, privacy text)
**Gate:** G8 — Team 50 QA + Nimrod visual sign-off

### Item 1 — Tooltip Layer for Statistical Terms

**Approved option:** (B) Custom JS tooltips with mobile tap support.

**Specification:**
- Add a lightweight inline `<script>` at the end of `public_report_body.html`
- Target elements: all `<th>` cells in the table header that contain statistical terms
- Terms and Hebrew explanations:
  | Term | Tooltip text |
  |------|-------------|
  | ממוצע ₪ | הממוצע החשבוני של כל התצפיות ב-7 הימים האחרונים |
  | חציון ₪ | הערך האמצעי — 50% מהתצפיות מעל, 50% מתחת |
  | טווח מחירים | המחיר הנמוך והגבוה ביותר שנצפו |
  | סטיית תקן | מדד לפיזור המחירים — ערך נמוך = מחירים דומים |
  | תצפיות | מספר דיווחי מחיר שנאספו עבור המוצר |
  | מקורות | מספר חוות/מגדלים שונים שמהם נאסף המידע |
- Behavior: hover on desktop, tap on mobile (toggle on/off)
- Style: dark background (`var(--green-dark)`), white text, rounded, max-width 250px
- Position: below the header cell, centered
- Dismiss: click/tap anywhere else, or mouse-leave

**Acceptance criteria:**
- All 6 tooltips render correctly on desktop (hover) and mobile (tap)
- Tooltips do not overflow the viewport
- No external JS dependencies

---

### Item 2 — Community CTA Banner Below Table

**Approved option:** (B) Separate banner below table, before transparency block.

**Specification:**
- Add a styled `<div>` between `price-table-wrap` and `dq-box`
- Content (Hebrew):
  ```
  יש לך נתונים מדויקים יותר? עזור לנו לשפר את המדד — שתף את המחירים שלך.
  [כפתור: שלח בוואטסאפ]
  ```
- Button links to `https://wa.me/972547776770?text=היי, אני רוצה לשתף נתוני מחירים למדד`
- Style: light sand background (`var(--sand)`), green-dark text, green button
- Layout: centered text, button aligned to start (right in RTL)
- Mobile: full-width, stacked

**Acceptance criteria:**
- Banner renders between table and transparency block
- WhatsApp link opens with pre-filled message
- Responsive on mobile

---

### Item 3 — Visual Hierarchy Enhancement

**Approved option:** (A) CSS-only adjustments.

**Specification:**
- Increase `price-main` (average price) font-size to 1.15rem, weight 800
- Reduce `price-secondary` (median) to 0.82rem, lighter color
- Add subtle left border (green-light) to the average price column
- On mobile: hide stddev column (already done), increase product name size
- Ensure the average price column is the visual anchor of each row

**Acceptance criteria:**
- Average price is clearly the dominant number in each row
- Median and range are visually subordinate
- No layout breakage on mobile

---

### Item 4 — SEO and Meta Data

**Approved option:** (A) WordPress admin only — no code changes.

**Specification:**
- Update WordPress page title to: `מדד מחירי חקלאות אורגנית — SmallFarmsAgent`
- Meta description: `מדד מחירים עדכני לתוצרת אורגנית מחוות קטנות בישראל. נתונים אוטומטיים מעודכנים שבועית.`
- Open Graph tags: title, description, image (use site logo or nimrod.bio og:image)
- This is a manual WordPress admin task — no code deployment needed

**Acceptance criteria:**
- Page title and meta description appear correctly in search results preview
- Sharing the URL on WhatsApp/Facebook shows correct title, description, and image

---

### Item 5 — Privacy Policy Formalization

**Approved option:** (B) Internal spec document + paragraph in transparency block.

**Specification:**
- Create `docs/PRIVACY_POLICY.md` — formal privacy spec (source of truth)
- Add a short paragraph to the `dq-box` in `public_report_body.html`:
  ```
  פרטיות: המערכת מציגה נתונים מצרפיים בלבד. אין חשיפה של מחירים ברמת חווה
  בודדת, ולא ניתן לזהות מגדל ספציפי מהנתונים המוצגים.
  ```
- Position: after the existing disclaimer text, before the grid

**Acceptance criteria:**
- `docs/PRIVACY_POLICY.md` exists with complete rules
- Privacy paragraph appears in the transparency block on the live page
- No identifiable farm-level data exposed anywhere in the public output

---

## M9 — Content + Community Engagement

**Scope:** Content that drives traffic and begins community participation.
**Teams:** Team 80 (blog post draft), Team 10 (integration), Nimrod (approval)
**Gate:** G9 — Nimrod approval on published content

### Item 6 — Blog Post: "Why My Farm Wasn't Profitable"

**Approved option:** (C) Team 80 drafts in Hebrew with Nimrod's guidance.

**Specification:**
- Team 80 receives briefing from Nimrod with:
  - Key talking points (what to include, what to omit)
  - Tone guidance (personal but not oversharing)
  - Link targets (SmallFarmsAgent page, contact)
- Blog post structure (per Team 80's outline):
  1. The Reality — farming experience, what worked
  2. The Problem — pricing opacity, hidden costs, no tools
  3. The Shift — from farm to systems, using AI
  4. The Solution — shared data, simple tools, community
  5. Closing — invitation to participate
- Length: 800–1200 words
- Language: Hebrew
- Publish on: nimrod.bio blog
- Cross-link: from SmallFarmsAgent page (in vision block)

**Acceptance criteria:**
- Blog post published on nimrod.bio
- Link added from SmallFarmsAgent page to blog post
- Content approved by Nimrod

---

### Item 7 — WhatsApp Data Submission Flow (Phase A — Manual)

**Approved option:** (A) WhatsApp link + manual processing.

**Specification:**
- The CTA from M8 Item 2 already provides the WhatsApp link
- Create a simple intake protocol for Nimrod:
  1. Farmer sends prices via WhatsApp
  2. Nimrod reviews and enters into admin UI (manual)
  3. Pipeline processes on next run
- Future: if volume justifies, escalate to Item 8B (in-page form)

**Acceptance criteria:**
- WhatsApp link is live (already from M8 Item 2)
- Intake protocol documented in `documentation/05-admin-and-operations/`
- At least one test submission processed end-to-end

---

## M10 — Advanced Interaction (Deferred — Specification Only)

**Scope:** Features requiring new infrastructure. Spec only — no implementation.
**Teams:** Team 100 (spec), Team 80 (product input)
**Gate:** None — this is a planning milestone

### Item 8 — WordPress Farmer Roles (Spec Only)

**Deliverable:** Architecture decision document defining roles, approval flow,
and feature gating. Implementation deferred until a feature requires it.

### Item 9 — Editable Fields / Cost Calculator (Concept Brief)

**Deliverable:** Concept brief for FarmCostAgent as a separate product under
MyFarmAgents umbrella. Defines scope boundary with OrganicMarketAgent.

### Item 10 — In-Page Data Submission Form (Spec Only)

**Deliverable:** Technical spec for replacing WhatsApp manual flow with an
in-page submission form. Requires Items 8 (roles) as dependency.

**All M10 items produce documents only — no code changes.**

---

## Dependency Graph

```
M8 (all items independent, can be parallelized)
  ├── Item 1: Tooltips
  ├── Item 2: CTA Banner
  ├── Item 3: Visual Hierarchy
  ├── Item 4: SEO (WordPress admin)
  └── Item 5: Privacy Policy

M9 (depends on M8 gate)
  ├── Item 6: Blog Post (depends on Nimrod briefing)
  └── Item 7: WhatsApp Flow (depends on M8 Item 2)

M10 (deferred — spec only)
  ├── Item 8: Farmer Roles spec
  ├── Item 9: FarmCostAgent concept
  └── Item 10: Submission Form spec
```
