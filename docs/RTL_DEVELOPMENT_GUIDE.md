# RTL Development Guide — MyFarmAgents / OrganicMarketAgent

**Version:** 1.0  
**Date:** 2026-03-31  
**Author:** Team 100 (Architecture)  
**Scope:** All HTML/CSS templates in `organic_market_agent/admin/templates/` and `organic_market_agent/publisher/templates/`

> This guide is **binding** for all Team 10 work that produces HTML. Any pull request that introduces `float: right`, `text-align: right`, or `margin-left`/`margin-right` in custom CSS will be rejected.

---

## 1. Why a special RTL guide?

Right-to-left (RTL) languages like Hebrew lay text out from the right edge of the screen. CSS and HTML have two mental models for this:

| Model | Example | Problem |
|-------|---------|---------|
| **Physical** ("old way") | `margin-left: 8px` | Hard-coded to screen direction — breaks in RTL |
| **Logical** ("correct way") | `margin-inline-start: 8px` | Relative to writing direction — works in both LTR and RTL |

The key rule: **always write logical, never physical.**

---

## 2. Document-level setup

Every HTML page in this project must open with:

```html
<!DOCTYPE html>
<html dir="rtl" lang="he">
```

- `dir="rtl"` tells the browser the document is right-to-left. The browser mirrors flexbox row direction, table column order (visually), and inline text flow automatically.
- `lang="he"` enables correct hyphenation and screen-reader pronunciation.

### Bootstrap 5 RTL

Load the RTL variant of Bootstrap — **not** the default:

```html
<!-- CORRECT -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">

<!-- WRONG — do not use -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

Bootstrap 5 ships two separate distributions. The RTL one (`bootstrap.rtl.min.css`) is built with [RTLCSS](https://rtlcss.com/) which automatically mirrors margins, paddings, borders, and floats. Using the LTR version with `dir="rtl"` produces a broken "half-mirrored" layout — exactly the problem this guide is meant to prevent.

---

## 3. CSS logical properties — the core rule

Replace every physical directional property with its logical equivalent:

| Physical (FORBIDDEN in custom CSS) | Logical (USE THIS) |
|------------------------------------|-------------------|
| `margin-left` | `margin-inline-start` |
| `margin-right` | `margin-inline-end` |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left: 0` (positioning) | `inset-inline-start: 0` |
| `right: 0` (positioning) | `inset-inline-end: 0` |
| `text-align: left` | `text-align: start` |
| `text-align: right` | `text-align: end` |
| `float: left` | Do not use floats at all — use flexbox |
| `float: right` | Do not use floats at all — use flexbox |
| `width` (when meaning inline size) | `inline-size` |
| `height` (when meaning block size) | `block-size` |

**Browser support:** All major browsers (Chrome 89+, Firefox 66+, Safari 15+) support CSS logical properties. There is no polyfill needed.

### Example

```css
/* WRONG */
.card-header {
  padding-left: 16px;
  text-align: left;
  border-left: 4px solid green;
}

/* CORRECT */
.card-header {
  padding-inline-start: 16px;
  text-align: start;
  border-inline-start: 4px solid green;
}
```

In a Hebrew (`dir="rtl"`) page, `start` maps to the right side of the screen. In an English (`dir="ltr"`) page, it maps to the left. The code is the same — the browser does the work.

---

## 4. Flexbox and grid

Flexbox respects `dir` automatically when you use logical values:

```css
/* CORRECT — works in both LTR and RTL */
.toolbar {
  display: flex;
  flex-direction: row;          /* In RTL, "row" starts from the right */
  justify-content: flex-start;  /* In RTL, flex-start = right side of container */
  gap: 8px;
}
```

Do **not** use `margin-left: auto` to push an element to the end of a flex row. Use `margin-inline-start: auto` instead.

```css
/* WRONG */
.action-btn { margin-left: auto; }

/* CORRECT */
.action-btn { margin-inline-start: auto; }
```

---

## 5. Numbers and mixed-direction content (bidi isolation)

Hebrew text mixed with numbers, prices, or English words requires **bidi isolation** to render correctly.

### Rule: wrap LTR content in `<span dir="ltr">`

```html
<!-- WRONG — price may render garbled -->
<td>₪ 14.50</td>

<!-- CORRECT — price is isolated as LTR -->
<td><span dir="ltr">₪&nbsp;14.50</span></td>

<!-- CORRECT — source code is isolated -->
<td><span dir="ltr">SRC002</span></td>

<!-- CORRECT — date is isolated -->
<td><span dir="ltr">2026-03-30 14:22</span></td>
```

Bidi isolation prevents the Unicode bidirectional algorithm from reordering characters in unexpected ways. It is especially important for:
- Prices: `₪ 14.50` (shekel sign is RTL-neutral, digit sequence is LTR)
- Codes: `SRC002`, `PRD013`
- Dates: `2026-03-30`
- URLs

In Jinja2 templates, use a macro:

```html
{% macro ltr(val) %}<span dir="ltr">{{ val }}</span>{% endmacro %}

<!-- usage -->
<td>{{ ltr("₪ " ~ ("%.2f"|format(p.avg_price))) }}</td>
```

---

## 6. Tables

When the document is `dir="rtl"`, the browser visually mirrors the table: the first column appears on the right, the last column on the left. **HTML column order in source stays the same** — write columns in logical order (most important first). The browser does the mirroring.

Do not add `dir="ltr"` to a `<table>` element unless the table contains purely English/numeric content with no Hebrew.

Column headers and cell content should use `text-align: start` (not `right`).

---

## 7. Icons and directional arrows

Chevrons, arrows, and "back" indicators are directional. In RTL they point the opposite way.

```css
/* Flip directional icons in RTL */
[dir="rtl"] .icon-arrow-forward,
[dir="rtl"] .icon-chevron-right {
  transform: scaleX(-1);
}
```

Do not add a separate RTL icon asset — the CSS transform is sufficient for inline SVG and icon fonts.

---

## 8. `text-align` reference card

| Desired visual result in Hebrew | CSS value to write |
|---------------------------------|-------------------|
| Align to reading start (right in Hebrew) | `text-align: start` |
| Align to reading end (left in Hebrew) | `text-align: end` |
| Center | `text-align: center` |
| Justify | `text-align: justify` |
| **Never write** | `text-align: right` or `text-align: left` in custom CSS |

Bootstrap 5 RTL re-maps its utility classes: `.text-start` = right side in Hebrew, `.text-end` = left side. This is correct and expected — use Bootstrap utilities freely.

---

## 9. Bootstrap RTL utility classes

Bootstrap 5 RTL ships mirrored utility classes. These work correctly without any extra CSS:

| Utility | Meaning in RTL (Hebrew) |
|---------|------------------------|
| `ms-2` (margin-start) | Margin on the RIGHT side (inline-start) |
| `me-2` (margin-end) | Margin on the LEFT side (inline-end) |
| `ps-3` (padding-start) | Padding on the RIGHT side |
| `pe-3` (padding-end) | Padding on the LEFT side |
| `text-start` | Align text to the RIGHT |
| `text-end` | Align text to the LEFT |
| `float-start` | Float to the RIGHT |
| `float-end` | Float to the LEFT |

The physical Bootstrap utilities (`ml-*`, `mr-*`, `pl-*`, `pr-*`) were removed in Bootstrap 5. The logical variants (`ms-*`, `me-*`, `ps-*`, `pe-*`) are the only ones available.

---

## 10. Checklist before committing an HTML template

- [ ] `<html dir="rtl" lang="he">` is present
- [ ] `bootstrap.rtl.min.css` is loaded (not `bootstrap.min.css`)
- [ ] No custom CSS uses `margin-left`, `margin-right`, `padding-left`, `padding-right`
- [ ] No custom CSS uses `text-align: left` or `text-align: right`
- [ ] No `float: left` or `float: right`
- [ ] Prices, codes, and dates are wrapped in `<span dir="ltr">`
- [ ] Directional icons have `[dir="rtl"] { transform: scaleX(-1) }` if needed
- [ ] All UI labels are in Hebrew

---

## 11. References

- [CSS Logical Properties — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values)
- [Bootstrap 5 RTL — Official Docs](https://getbootstrap.com/docs/5.3/getting-started/rtl/)
- [RTLCSS — the tool Bootstrap uses internally](https://rtlcss.com/)
- [Unicode Bidirectional Algorithm (bidi isolation)](https://www.w3.org/International/articles/inline-bidi-markup/)
