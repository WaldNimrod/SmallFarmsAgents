---
document_type: MANDATE
version: "1.0"
---

# Mandate — M8 UX Polish + Policy Formalization

**Mandate ID:** MANDATE-20260402-M8-UX-POLISH
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-02
**Priority:** MEDIUM
**Gate dependency:** Blocks G8
**Status:** ACTIVE

---

## 1. Context

M7 Go-Live is complete. The public page is live at `nimrod.bio/SmallFarmsAgent`.
Team 80 (Product & Strategy) delivered UX improvement recommendations that have
been reviewed by Team 100 and approved by Nimrod.

This mandate covers all code changes for M8: template modifications to the public
page that improve usability, accessibility, and policy compliance.

**Triggered by:** Team 80 handoff packages + Team 100 architectural review
**Related documents:**
- `_COMMUNICATION/TEAM_100/reports/2026-04-02_M8_M10_DETAILED_SPEC_TEAM100.md`
- `_COMMUNICATION/TEAM_80/sfa_handoff_v2/02_ux_adjustments.md`
- `_COMMUNICATION/TEAM_80/sfa_handoff_v2/01_privacy_spec.md`
- `docs/PRIVACY_POLICY.md`

---

## 2. Requirements

### Task 1 — Tooltip Layer for Statistical Terms

Add custom JavaScript tooltips to the 6 statistical column headers in the price
table within `organic_market_agent/publisher/templates/public_report_body.html`.

**Terms and tooltips (Hebrew):**

| Header | Tooltip |
|--------|---------|
| ממוצע ₪ | הממוצע החשבוני של כל התצפיות ב-7 הימים האחרונים |
| חציון ₪ | הערך האמצעי — 50% מהתצפיות מעל, 50% מתחת |
| טווח מחירים | המחיר הנמוך והגבוה ביותר שנצפו |
| סטיית תקן | מדד לפיזור המחירים — ערך נמוך = מחירים דומים |
| תצפיות | מספר דיווחי מחיר שנאספו עבור המוצר |
| מקורות | מספר חוות/מגדלים שונים שמהם נאסף המידע |

**Implementation:**
- Inline `<script>` at the end of the template (no external dependencies)
- `data-tooltip` attribute on each `<th>` element
- Desktop: show on hover, hide on mouse-leave
- Mobile: show on tap, dismiss on tap-elsewhere
- Style: `var(--green-dark)` background, white text, rounded corners, max-width 250px
- Position: below the header cell, centered horizontally

**Acceptance criterion:** All 6 tooltips render on desktop (hover) and mobile (tap) without viewport overflow.

---

### Task 2 — Community CTA Banner

Add a styled banner between the price table (`price-table-wrap`) and the
transparency block (`dq-box`) in `public_report_body.html`.

**HTML content:**
```html
<div class="community-cta">
  <p>יש לך נתונים מדויקים יותר? עזור לנו לשפר את המדד — שתף את המחירים שלך.</p>
  <a class="cta-btn" href="https://wa.me/972547776770?text=היי, אני רוצה לשתף נתוני מחירים למדד">שלח בוואטסאפ</a>
</div>
```

**Style:**
- Background: `var(--sand)`
- Text: `var(--green-dark)`, centered
- Button: `var(--green-dark)` background, white text, rounded, aligned to start (right in RTL)
- Responsive: full-width on mobile, stacked layout

**Acceptance criterion:** Banner renders between table and transparency block. WhatsApp link opens with pre-filled message.

---

### Task 3 — Visual Hierarchy Enhancement

Adjust CSS in `public_report_body.html` to strengthen the visual hierarchy:

- `.price-main` (average price): increase to `font-size: 1.15rem; font-weight: 800`
- `.price-secondary` (median): reduce to `font-size: 0.8rem; color: #9ca3af`
- `.range-text`: reduce to `font-size: 0.75rem`
- Add `border-inline-start: 3px solid var(--green-light)` to the average price `<td>` cells

**Acceptance criterion:** Average price is clearly the dominant number in each row. Median and range are visually subordinate.

---

### Task 4 — Privacy Paragraph in Transparency Block

Add a privacy statement paragraph to the `dq-box` section, after the existing
disclaimer text and before the statistics grid:

```html
<p class="dq-lead">
  פרטיות: המערכת מציגה נתונים מצרפיים בלבד. אין חשיפה של מחירים ברמת חווה
  בודדת, ולא ניתן לזהות מגדל ספציפי מהנתונים המוצגים.
</p>
```

**Acceptance criterion:** Privacy paragraph appears in the transparency block on the live page.

---

## 3. Out of Scope

- WordPress admin SEO settings (Team 80 / Nimrod — no code change)
- Blog post content (M9 — Team 80)
- New database tables or migrations
- Authentication or user roles
- Any changes to the admin interface

---

## 4. Verification Checklist

```bash
python3.11 -m pytest tests/ -q                    # all tests pass
python3.11 -m organic_market_agent run_publisher --output-dir output/public --upload
```

Expected results:
- [ ] All 6 tooltips functional on desktop and mobile
- [ ] CTA banner renders correctly with WhatsApp link
- [ ] Average price visually dominant in table rows
- [ ] Privacy paragraph appears in transparency block
- [ ] All existing tests still pass (no regression)
- [ ] Live page updated and verified

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save at:
`_COMMUNICATION/TEAM_10/reports/2026-XX-XX_M8_UX_POLISH_COMPLETE_TEAM10.md`

Then file a **QA Review Request** for G8 using:
`_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md`

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
*Authorized by: Team 100 (Architecture)*
