# M8 LOD400 Specification — UX Polish + Policy Formalization

**Date:** 2026-04-02
**From:** Team 100 (Architecture)
**To:** Team 80 (Product & Strategy) — for review
**Status:** PENDING TEAM 80 REVIEW
**Source template:** `organic_market_agent/publisher/templates/public_report_body.html`

---

## Scope

6 items — all changes confined to `public_report_body.html` (Jinja2 template).
Zero database, pipeline, or backend changes. Pure CSS + HTML + inline JS.

---

## Current Template Structure (reference)

```
Line 005  <div class="sfagent-market-report" dir="rtl" lang="he">
Line 006  <style> ... </style>                          ← all scoped CSS
Line 186  {# Disclaimer modal #}                        ← floating modal on load
Line 203  <div class="sf-container">
Line 205    <h1> מדד מחירי חקלאות אורגנית </h1>         ← centered title
Line 208    <div class="vision-block"> ... </div>        ← marketing/personal text
Line 231    <div class="report-update-line"> ... </div>  ← date + count
Line 235    {% if stale_banner %} ... {% endif %}
Line 273    <div class="price-table-wrap">               ← THE TABLE
Line 334    </div>                                       ← end table
Line 337    {% if data_quality %}
Line 338      <div class="dq-box"> ... </div>            ← transparency block
Line 359    {% endif %}
Line 361  </div>                                         ← end .sf-container
Line 363  </div>                                         ← end .sfagent-market-report
```

---

## Item 1 — Tooltip Layer for Statistical Terms

### 1.1 HTML Changes

Add `data-tooltip` attribute to each `<th>` in the table header (lines 277–283):

**Before:**
```html
<th>מוצר</th>
<th class="num">ממוצע ₪</th>
<th class="num">חציון ₪</th>
<th>טווח מחירים</th>
<th class="num hide-mobile">סטיית תקן</th>
<th class="num">תצפיות</th>
<th class="num">מקורות</th>
```

**After:**
```html
<th>מוצר</th>
<th class="num" data-tooltip="הממוצע החשבוני של כל התצפיות ב-7 הימים האחרונים">ממוצע ₪</th>
<th class="num" data-tooltip="הערך האמצעי — 50% מהתצפיות מעל, 50% מתחת">חציון ₪</th>
<th data-tooltip="המחיר הנמוך והגבוה ביותר שנצפו">טווח מחירים</th>
<th class="num hide-mobile" data-tooltip="מדד לפיזור המחירים — ערך נמוך = מחירים דומים">סטיית תקן</th>
<th class="num" data-tooltip="מספר דיווחי מחיר שנאספו עבור המוצר">תצפיות</th>
<th class="num" data-tooltip="מספר חוות שונות (ללא חשיפה של חווה ספציפית)">מקורות</th>
```

**Note:** "מקורות" tooltip updated per Team 80 feedback — reinforces privacy.

### 1.2 CSS Addition (inside `<style>` block)

```css
/* Tooltip layer */
.sfagent-market-report [data-tooltip] {
  position: relative;
  cursor: help;
}
.sfagent-market-report [data-tooltip]::after {
  content: ' ⓘ';
  font-size: 0.7rem;
  opacity: 0.7;
}
.sfagent-market-report .sf-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--green-dark);
  color: #fff;
  font-size: 0.78rem;
  font-weight: 400;
  line-height: 1.4;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  max-width: 250px;
  min-width: 160px;
  white-space: normal;
  text-align: center;
  z-index: 1000;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
  opacity: 0;
  transition: opacity 0.15s ease;
}
.sfagent-market-report .sf-tooltip.visible {
  opacity: 1;
}
```

### 1.3 JavaScript (inline `<script>` at end of template, before closing `</div>`)

```javascript
<script>
(function() {
  var report = document.querySelector('.sfagent-market-report');
  if (!report) return;
  var headers = report.querySelectorAll('[data-tooltip]');
  var activeTooltip = null;

  function showTooltip(th) {
    hideTooltip();
    var tip = document.createElement('div');
    tip.className = 'sf-tooltip';
    tip.textContent = th.getAttribute('data-tooltip');
    th.style.position = 'relative';
    th.appendChild(tip);
    /* Prevent viewport overflow */
    requestAnimationFrame(function() {
      var rect = tip.getBoundingClientRect();
      if (rect.left < 8) tip.style.transform = 'translateX(0)';
      if (rect.right > window.innerWidth - 8)
        tip.style.transform = 'translateX(-100%)';
      tip.classList.add('visible');
    });
    activeTooltip = { el: tip, th: th };
  }

  function hideTooltip() {
    if (activeTooltip) {
      activeTooltip.el.remove();
      activeTooltip = null;
    }
  }

  var isTouchDevice = 'ontouchstart' in window;

  headers.forEach(function(th) {
    if (!isTouchDevice) {
      th.addEventListener('mouseenter', function() { showTooltip(th); });
      th.addEventListener('mouseleave', hideTooltip);
    }
    th.addEventListener('click', function(e) {
      e.stopPropagation();
      if (activeTooltip && activeTooltip.th === th) {
        hideTooltip();
      } else {
        showTooltip(th);
      }
    });
  });

  document.addEventListener('click', hideTooltip);
})();
</script>
```

### 1.4 Acceptance Criteria

- [ ] All 6 statistical `<th>` elements have `data-tooltip` attribute
- [ ] Each `<th>` shows a small ⓘ indicator
- [ ] Desktop: tooltip appears on hover below the header, hides on mouse-leave
- [ ] Mobile: tooltip toggles on tap; dismissed by tapping elsewhere
- [ ] Tooltip does not overflow viewport (left/right boundary check)
- [ ] No external JS dependencies
- [ ] "מקורות" tooltip explicitly states no farm identification

---

## Item 2 — Community CTA Banner

### 2.1 Insertion Point

Between `</div>{# end price-table-wrap #}` (line 334) and `{% if data_quality %}` (line 337).

### 2.2 HTML

```html
{# ── Community CTA ── #}
<div class="community-cta">
  <p>יש לך נתונים מדויקים יותר? עזור לשפר את המדד — זה משרת את כל הקהילה.</p>
  <a class="cta-btn" href="https://wa.me/972547776770?text=היי, אני רוצה לשתף נתוני מחירים למדד">שלח בוואטסאפ</a>
</div>
```

**Note:** CTA text updated per Team 80 feedback — "זה משרת את כל הקהילה" replaces "שתף את המחירים שלך".

### 2.3 CSS Addition

```css
/* Community CTA banner */
.sfagent-market-report .community-cta {
  background: var(--sand);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-top: 1.25rem;
  text-align: center;
}
.sfagent-market-report .community-cta p {
  margin: 0 0 0.75rem;
  font-size: 0.92rem;
  color: var(--green-dark);
  font-weight: 500;
}
.sfagent-market-report .community-cta .cta-btn {
  display: inline-block;
  background: var(--green-dark);
  color: #fff;
  text-decoration: none;
  padding: 0.55rem 1.5rem;
  border-radius: 6px;
  font-family: 'Heebo', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}
.sfagent-market-report .community-cta .cta-btn:hover {
  background: var(--green-mid);
}
@media (max-width: 640px) {
  .sfagent-market-report .community-cta .cta-btn {
    display: block;
    text-align: center;
  }
}
```

### 2.4 Acceptance Criteria

- [ ] Banner renders between table and transparency block
- [ ] Text matches approved Hebrew copy exactly
- [ ] WhatsApp link opens with pre-filled Hebrew message
- [ ] Button full-width on mobile, inline on desktop
- [ ] Sand background consistent with design system

---

## Item 3 — Visual Hierarchy Enhancement

### 3.1 CSS Modifications (existing selectors)

**`.price-main` — line 91 current:**
```css
.sfagent-market-report .price-main { font-size: 1.05rem; font-weight: 700; color: var(--green-dark); }
```
**Replace with:**
```css
.sfagent-market-report .price-main { font-size: 1.15rem; font-weight: 800; color: var(--green-dark); }
```

**`.price-secondary` — line 92 current:**
```css
.sfagent-market-report .price-secondary { color: var(--muted); font-size: 0.88rem; }
```
**Replace with:**
```css
.sfagent-market-report .price-secondary { color: #9ca3af; font-size: 0.8rem; }
```

**`.range-text` — line 102 current:**
```css
.sfagent-market-report .range-text { font-size: 0.78rem; color: var(--muted); direction: ltr; }
```
**Replace with:**
```css
.sfagent-market-report .range-text { font-size: 0.75rem; color: var(--muted); direction: ltr; }
```

### 3.2 HTML Modification — Average Price Cell Border

In the `<td>` that contains `.price-main` (line 296–298), add an inline style for the left border:

**Before:**
```html
<td class="num">
  {% if p.avg_price is not none %}
    <span class="price-main">{{ "%.2f"|format(p.avg_price) }}</span>
  {% else %}—{% endif %}
</td>
```

**After:**
```html
<td class="num" style="border-inline-start: 3px solid var(--green-light);">
  {% if p.avg_price is not none %}
    <span class="price-main">{{ "%.2f"|format(p.avg_price) }}</span>
  {% else %}—{% endif %}
</td>
```

### 3.3 Acceptance Criteria

- [ ] Average price (`price-main`) is visually dominant: larger, bolder than all other numbers
- [ ] Median (`price-secondary`) is clearly secondary: smaller, lighter gray
- [ ] Range text slightly reduced
- [ ] Green left border on average column creates a visual anchor
- [ ] No layout breakage on any viewport

---

## Item 4 — Privacy Block in Transparency Section

### 4.1 Insertion Point

Inside `<div class="dq-box">`, after the second `<p class="dq-lead">` (line 348) and before `<ul class="dq-grid">` (line 349).

### 4.2 HTML

```html
<div class="dq-privacy">
  <strong>🔒 פרטיות:</strong>
  <ul>
    <li>המערכת מציגה נתונים מצרפיים בלבד.</li>
    <li>אין חשיפה של מחירים ברמת חווה בודדת.</li>
    <li>לא ניתן לזהות מגדל ספציפי.</li>
  </ul>
</div>
```

**Note:** Format upgraded per Team 80 feedback — lock icon + bullet list instead of plain paragraph. Privacy as a trust asset, not a limitation.

### 4.3 CSS Addition

```css
/* Privacy block inside dq-box */
.sfagent-market-report .dq-privacy {
  background: #f0faf4;
  border-radius: 8px;
  padding: 0.65rem 1rem;
  margin: 0.6rem 0;
  font-size: 0.82rem;
  color: var(--green-dark);
  line-height: 1.5;
}
.sfagent-market-report .dq-privacy strong {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.88rem;
}
.sfagent-market-report .dq-privacy ul {
  margin: 0;
  padding: 0 1.2rem 0 0;
  list-style: disc;
}
.sfagent-market-report .dq-privacy li {
  margin-bottom: 0.15rem;
}
```

### 4.4 Acceptance Criteria

- [ ] Privacy block appears inside `dq-box`, between disclaimer text and stats grid
- [ ] Lock icon (🔒) visible as a visual anchor
- [ ] Three bullet points with exact Hebrew text
- [ ] Light green background differentiates it from surrounding content
- [ ] Readable on mobile without overflow

---

## Item 5 — Transparency Bridge (above table ↔ dq-box)

### 5.1 Part A — Bridge Line Above Table

**Insertion point:** After `<div class="report-update-line">` (line 231–233) and before `{% if stale_banner %}` (line 235).

**HTML:**
```html
<div class="transparency-bridge">
  איך הנתונים נוצרים? <a href="#sfagent-dq-box">↓ ראה פירוט מתחת לטבלה</a>
</div>
```

### 5.2 Part B — Opening Line Inside dq-box

**Insertion point:** Inside `<div class="dq-box">`, as the first child before `<h2 class="dq-title">` (line 339).

**Modification to line 338:**
```html
<div class="dq-box" id="sfagent-dq-box" aria-label="שקיפות צינור נירמול">
  <p class="dq-bridge-target">הטבלה מעל מבוססת על תהליך זה:</p>
  <h2 class="dq-title">שקיפות — מצב צינור הנירמול</h2>
```

### 5.3 CSS Addition

```css
/* Transparency bridge (above table) */
.sfagent-market-report .transparency-bridge {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0.25rem 0 0.75rem;
  text-align: left;
}
.sfagent-market-report .transparency-bridge a {
  color: var(--green-mid);
  text-decoration: none;
  font-weight: 500;
}
.sfagent-market-report .transparency-bridge a:hover {
  text-decoration: underline;
}
/* Bridge target inside dq-box */
.sfagent-market-report .dq-bridge-target {
  font-size: 0.82rem;
  color: var(--green-mid);
  font-weight: 600;
  margin: 0 0 0.3rem;
}
```

### 5.4 Behavior

The `<a href="#sfagent-dq-box">` uses native anchor scroll — clicking the bridge line smoothly scrolls to the transparency block. The `id="sfagent-dq-box"` on the `dq-box` div enables this.

### 5.5 Acceptance Criteria

- [ ] Bridge line appears below the update line, above any stale banner and the table
- [ ] Clicking the link scrolls to the transparency block
- [ ] Opening line "הטבלה מעל מבוססת על תהליך זה:" appears at the top of dq-box
- [ ] Creates a cognitive loop: user sees "how?" → scrolls to explanation → reads "the table above is based on..."
- [ ] Visually subtle — does not compete with the table or marketing block

---

## Item 6 — Table Perception Framing

### 6.1 Insertion Point

Immediately before `<div class="price-table-wrap">` (line 273).

### 6.2 HTML

```html
<h2 class="table-framing">מדד מחירים מבוסס נתונים אמיתיים מהשטח</h2>
```

### 6.3 CSS Addition

```css
/* Table perception framing title */
.sfagent-market-report .table-framing {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--green-dark);
  margin: 0.75rem 0 0.35rem;
}
```

### 6.4 Acceptance Criteria

- [ ] Title appears immediately above the table container
- [ ] Font size subordinate to the H1 page title (0.95rem vs implicit H1 size)
- [ ] Shifts user perception from "price list" to "data-driven pricing index"
- [ ] No visual clutter — single clean line

---

## Final Template Structure After M8

```
<div class="sfagent-market-report" dir="rtl" lang="he">
  <style> ... (original + new CSS) ... </style>

  {# Disclaimer modal #}
  <div class="disclaimer-overlay"> ... </div>

  <div class="sf-container">
    <h1> מדד מחירי חקלאות אורגנית </h1>           ← centered title
    <div class="vision-block"> ... </div>            ← marketing/personal text
    <div class="report-update-line"> ... </div>      ← date + count
    <div class="transparency-bridge"> ... </div>     ← NEW: "how?" link to dq-box
    {% if stale_banner %} ... {% endif %}

    <h2 class="table-framing"> ... </h2>             ← NEW: perception framing
    <div class="price-table-wrap">
      <table>
        <thead>
          <tr>
            <th>מוצר</th>
            <th data-tooltip="...">ממוצע ₪</th>     ← UPDATED: tooltip attr
            <th data-tooltip="...">חציון ₪</th>      ← UPDATED: tooltip attr
            <th data-tooltip="...">טווח מחירים</th>   ← UPDATED: tooltip attr
            <th data-tooltip="...">סטיית תקן</th>     ← UPDATED: tooltip attr
            <th data-tooltip="...">תצפיות</th>        ← UPDATED: tooltip attr
            <th data-tooltip="...">מקורות</th>        ← UPDATED: tooltip (T80 text)
          </tr>
        </thead>
        <tbody> ... (avg td with border) ... </tbody> ← UPDATED: visual hierarchy
      </table>
    </div>

    <div class="community-cta"> ... </div>           ← NEW: CTA banner (T80 copy)

    {% if data_quality %}
    <div class="dq-box" id="sfagent-dq-box">
      <p class="dq-bridge-target"> ... </p>          ← NEW: "table above based on..."
      <h2 class="dq-title"> ... </h2>
      <p class="dq-lead"> ... </p>
      <p class="dq-lead"> ... </p>
      <div class="dq-privacy"> 🔒 ... </div>         ← NEW: privacy block (T80 format)
      <ul class="dq-grid"> ... </ul>
    </div>
    {% endif %}
  </div>

  <script> ... tooltip JS ... </script>              ← NEW: tooltip behavior
</div>
```

---

## Constraints (confirmed)

- ❌ No authentication (M10)
- ❌ No calculator (future)
- ❌ No pipeline / schema changes
- ❌ No admin UI changes
- ❌ No external JS/CSS dependencies
- ✅ All changes in a single template file
- ✅ All CSS scoped under `.sfagent-market-report`

---

## Review Request

Team 80 — please review this LOD400 specification and confirm:

1. **Item 1** — Tooltip texts accurate? "מקורות" privacy phrasing sufficient?
2. **Item 2** — CTA copy final? "זה משרת את כל הקהילה" approved?
3. **Item 4** — Privacy bullet format and text approved?
4. **Item 5** — Bridge text "איך הנתונים נוצרים?" and "הטבלה מעל מבוססת על תהליך זה:" — tone and wording?
5. **Item 6** — "מדד מחירים מבוסס נתונים אמיתיים מהשטח" as table framing — approved?
6. **Overall flow** — Does the template structure below maintain the intended cognitive flow: trust → value → engagement?

Awaiting Team 80 sign-off before implementation begins.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
