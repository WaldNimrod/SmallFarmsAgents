# Design Tokens — canonical

> Copy verbatim into `wp-content/themes/sfa-child/assets/tokens.css` or equivalent.
> These are the **contract** — if you need to change a value, update this doc first.

---

## 1. CSS custom properties

```css
:root {
  /* ─── Paper / ink ─── */
  --gj-paper:     #f6f1e3;   /* warm cream — base background */
  --gj-paper-2:   #ece5d2;   /* recessed surfaces, cards on background */
  --gj-paper-3:   #ddd2b2;   /* track / disabled / empty bar */
  --gj-ink:       #2a2418;   /* primary text & icons */
  --gj-ink-soft:  #776a4d;   /* secondary text, labels, captions */
  --gj-line:      #d8ccae;   /* dividers, borders, dashed outlines */

  /* ─── Worlds (from Nimrod DS v3.3) ─── */
  --gj-leaf:        #6f8a45;  /* book / open community */
  --gj-leaf-deep:   #4d6a2c;  /* book emphasis, active states */
  --gj-leaf-soft:   #9bb172;  /* book backgrounds, wash */
  --gj-tomato:      #c24f2c;  /* market / community attention */
  --gj-tomato-deep: #8e3018;  /* market emphasis */
  --gj-sun:         #d39a32;  /* beta / sunshine accents / warnings */
  --gj-soil:        #8b5d2f;  /* paid tier / earth depth */
  --gj-soil-deep:   #5a3c1a;  /* paid emphasis, dark stripes */

  /* ─── Status (overlay onto worlds) ─── */
  --status-fresh:  var(--gj-leaf);
  --status-aging:  var(--gj-sun);
  --status-stale:  var(--gj-tomato);
  --status-error:  #c43a2e;

  /* ─── Typography ─── */
  --gj-font-body: "Assistant", "Heebo", system-ui, sans-serif;
  --gj-font-head: "Frank Ruhl Libre", "David Libre", "Times New Roman", serif;
  --gj-font-mono: "JetBrains Mono", "SF Mono", Menlo, monospace;

  /* ─── Radii ─── */
  --gj-r-s:    8px;
  --gj-r-m:    12px;
  --gj-r-l:    14px;
  --gj-r-xl:   18px;
  --gj-r-pill: 99px;

  /* ─── Shadows ─── */
  --gj-shadow-s: 0 1px 3px rgba(40, 25, 12, .06);
  --gj-shadow-m: 0 4px 14px rgba(80, 50, 20, .08);
  --gj-shadow-l: 0 8px 28px rgba(80, 50, 20, .14);

  /* ─── Spacing (4-pt grid) ─── */
  --gj-sp-1: 4px;
  --gj-sp-2: 8px;
  --gj-sp-3: 12px;
  --gj-sp-4: 16px;
  --gj-sp-5: 24px;
  --gj-sp-6: 32px;
  --gj-sp-7: 48px;
}
```

---

## 2. Typography scale

| Token | Size | Weight | Family | Use |
|-------|------|--------|--------|-----|
| `h1`  | 32px mobile / 46px desktop | 900 | head | page hero (book/crop name) |
| `h1-xl` | 44px / 64px | 900 | head | market detail big-number block |
| `h2`  | 26px / 32px | 700 | head | section heads |
| `h3`  | 17–22px | 700 | head | sub-heads |
| `h4`  | 15–17px | 700 | head | card titles, KV labels |
| `body`| 13–15px | 400 | body | paragraphs |
| `lede`| 14–15px | 400 | body | hero blurbs (color: ink-soft) |
| `meta`| 11–12px | 400 | body | captions, meta |
| `eyebrow` | 10px | 700 | mono | uppercase, letter-spacing .08em — section labels |
| `numeric` | 18–60px | 700–900 | head | tabular-nums for prices/dtm/yield |
| `code` | 10–11px | 400 | mono | freshness, version, technical |

```css
.gj-eyebrow {
  font-family: var(--gj-font-mono);
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--gj-tomato-deep);
}

.gj-h1 {
  font-family: var(--gj-font-head);
  font-weight: 900;
  font-size: 32px;
  line-height: 1.05;
  letter-spacing: -.015em;
  margin: 0 0 10px;
}
@media (min-width: 900px) { .gj-h1 { font-size: 46px; } }

.gj-h2 {
  font-family: var(--gj-font-head);
  font-weight: 700;
  font-size: 26px;
  line-height: 1.1;
  letter-spacing: -.01em;
}

.gj-lede {
  font-size: 14px;
  line-height: 1.6;
  color: var(--gj-ink-soft);
  max-width: 32ch;
}
```

---

## 3. Underline accent

The signature "hand-drawn" underline for hero words. Inline SVG background:

```css
.gj-underline {
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 10'><path d='M2 6 Q 30 1 70 4 T 140 5 T 198 4' stroke='%23c24f2c' stroke-width='2.4' fill='none' stroke-linecap='round'/></svg>");
  background-repeat: no-repeat;
  background-position: 0 100%;
  background-size: 100% 10px;
  padding-bottom: 6px;
}
```

**Use sparingly** — 1 instance per hero, never inside body copy.

---

## 4. Module color mapping

Modules are categorized into color worlds for visual recognition:

| Module | tier | color | accent on |
|--------|------|-------|-----------|
| ספר גידולים | open | leaf | book card, crop pages |
| מחירון | open | tomato | market card, price big-numbers |
| מחשבון | beta | sun | calculator card |
| תכנון עונה | coming | leaf | dimmed |
| ניהול לקוחות | paid | soil | paid tier |
| מעקב יבול | paid | tomato | paid tier |
| חיבור Tend | custom | soil | tailored tier |
| יומן שדה | custom | leaf | tailored tier |

Maintained in `MODULES_REGISTRY.yaml`. Adding a module = add a row to that file.

---

## 5. Tier color mapping

| Tier | Hebrew label | color | meaning |
|------|--------------|-------|---------|
| `open`   | כלים לקהילה  | leaf   | community gift |
| `beta`   | בטא · ניסיוני | sun   | in development |
| `coming` | בקרוב         | paper | placeholder |
| `paid`   | כלים מתקדמים  | soil  | paid track |
| `custom` | בדיוק לחווה שלך | tomato | tailored build |

---

## 6. Breakpoints

```css
/* Mobile-first. Default = mobile. */
@media (min-width: 900px)  { /* desktop shell (.dt-shell) activates */ }
@media (min-width: 1280px) { /* wider — show 3-up module grids; market grid 3-up */ }
```

Below 900px, only `.gj-shell` (mobile) renders. Above, the page-template should
swap to `.dt-shell` (desktop) — see `TEMPLATES.md §2`.

---

## 7. Z-index map

```
0   — background, washes
1   — content
5   — floating feedback button (.fb-fab), sticky strips
10  — sticky header
20  — modals, drawer
100 — toast / snackbar
```

---

## 8. Animation

Minimal motion. Only:

- Fade-in (skeletons): `dt-skel` keyframe, 1.4s linear infinite
- Hover lift (.mod-card:hover): `transform: translateY(-1px)`, 150ms
- Chevron rotate (details summary): 150ms

No parallax, no hero-scroll-effects. The brand is calm.
