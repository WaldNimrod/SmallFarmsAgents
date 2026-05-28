# Mobile Responsive Spec — nimrod.bio
## חבילה משלימה ל-Handoff · v1.0 · 25.05.2026

**משלים את:** `_handoff/00-HANDOFF-claude-code-110.md`
**סוגר:** T-02 (Mobile screens · Stage 5)
**ממיר:** desktop-first design → adaptive site (mobile + tablet + desktop)

---

## 1. עקרונות-יסוד

### 1.1 הגישה
- **Adaptive, לא mobile-first.** העיצוב נבנה desktop-first; mobile הוא **התאמה נאמנה**, לא עיצוב נפרד.
- **שמירת זהות.** טיפוגרפיה, צבעי-עולם, bridge=seam, ו-Unless tagline נשארים בלי שינוי.
- **תכלית > קישוט.** במובייל אפשר להחביא קישוטים. **אסור** להחביא תוכן או ניווט קריטי.
- **One thumb reach.** כל פעולה חיונית חייבת להיות נגישה לאגודל אחד במצב standing-and-walking.

### 1.2 Breakpoints — חוזה גלובלי
```css
:root {
  --bp-mobile:  640px;   /* up to this = mobile */
  --bp-tablet:  900px;   /* up to this = tablet */
  --bp-desktop: 1100px;  /* above = desktop */
}
```

| מסך | טווח | מטרת design |
|---|---|---|
| **Mobile** | ≤ 640px | iPhone SE → iPhone 15 Pro Max → Galaxy. ✅ priority. |
| **Tablet** | 641–900px | iPad portrait. ✅ priority. |
| **Tablet wide** | 901–1100px | iPad landscape, small laptop. Mostly desktop layout slightly tighter. |
| **Desktop** | ≥ 1101px | המקור — כפי שהוא בקבצי העיצוב. |

**הערה ל-Tailwind/utility users:** אסור לשנות את ה-breakpoints. הם נעולים.

### 1.3 Touch targets
- **מינימום 44 × 44 px** לכל פעולה (Apple HIG).
- **רווח 8px** מינימום בין targets סמוכים.
- **חריג מותר:** קישורי טקסט inline בפסקה — נשארים גודל הטקסט. אך כל פעולה ראשית (כפתור, chip, nav item) חייבת לעמוד ב-44×44.

### 1.4 Typography scaling
**Mobile = 90% מהגדלים הדסקטופ.** הסקאלה ב-CSS תוקנה דרך `clamp()` — לא דורש breakpoint:

```css
/* Already in T*-styles.css — דוגמה */
.hero-title {
  font-size: clamp(40px, 6vw, 84px);
  /* mobile: 40px · desktop: 84px · between scales fluidly */
}
```

**הוסיפו `clamp()` לכל font-size > 16px ב-CSS המקור.** רוב זה כבר מטופל; ה-build חייב לוודא.

### 1.5 Spacing scaling
**Mobile padding-block של sections — 65% מהדסקטופ.** דוגמה:

```css
/* Desktop */
.t1-section { padding-block: clamp(48px, 6vw, 88px); }
/* Already mobile-aware via clamp + vw */
```

**הוסיפו padding-inline-bottom-safe-area למובייל:**
```css
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .shell-foot, .final-cta, .seeking-cta {
    padding-bottom: max(28px, env(safe-area-inset-bottom));
  }
}
```

---

## 2. Shell (Nav + Footer) — Mobile

### 2.1 Mobile Nav — דרישות

**מצב הנוכחי (desktop):** לוגו + בית + 3 עולמות + מפריד + בלוג + על נמרוד + צור קשר. הכל בשורה אחת.

**מובייל (≤ 640px):** לא נכנס. צריך **Drawer (סייד-מנו)** + סרגל סטיקי עליון מצומצם.

```html
<nav class="shell-nav mobile">
  <div class="shell-nav-inner">
    <a href="/" class="shell-mark">נימרוד ולד</a>
    <button class="nav-toggle" aria-label="פתח תפריט" aria-expanded="false">
      <svg><!-- 3-line hamburger --></svg>
    </button>
  </div>
</nav>

<!-- Drawer slides from right (RTL) -->
<aside class="nav-drawer" aria-hidden="true">
  <div class="drawer-head">
    <span class="title">תפריט</span>
    <button class="drawer-close" aria-label="סגור">×</button>
  </div>
  <nav class="drawer-nav">
    <a href="/" class="drawer-link home">
      <svg><!-- home icon --></svg> בית
    </a>
    <hr />
    <div class="drawer-section-label">עולמות</div>
    <a href="/world/soil" class="drawer-link world soil">
      <span class="dot"></span> אדמה
    </a>
    <a href="/world/know" class="drawer-link world know">
      <span class="dot"></span> ייעוץ והוראה
    </a>
    <a href="/world/code" class="drawer-link world code">
      <span class="dot"></span> דיגיטל
    </a>
    <hr />
    <a href="/blog" class="drawer-link">בלוג</a>
    <a href="/about" class="drawer-link">על נמרוד</a>
    <a href="/contact" class="drawer-link cta">צור קשר ←</a>
  </nav>
</aside>

<!-- Backdrop -->
<div class="nav-backdrop" aria-hidden="true"></div>
```

**CSS spec:**
```css
.shell-nav.mobile .nav-toggle {
  width: 44px; height: 44px;
  border: none; background: transparent;
  color: var(--ink-soft);
  display: grid; place-items: center;
}

.nav-drawer {
  position: fixed; top: 0; bottom: 0;
  inset-inline-end: 0;          /* RTL: from right */
  width: min(85vw, 360px);
  background: var(--paper);
  border-inline-start: 1px solid var(--line);
  transform: translateX(100%);
  transition: transform .25s ease;
  z-index: 1000;
  padding: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
[dir="rtl"] .nav-drawer { transform: translateX(-100%); }
.nav-drawer.is-open { transform: translateX(0); }

.nav-backdrop {
  position: fixed; inset: 0;
  background: rgba(31,30,28,.4);
  opacity: 0; pointer-events: none;
  transition: opacity .25s ease;
  z-index: 999;
}
.nav-backdrop.is-open { opacity: 1; pointer-events: auto; }

.drawer-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px; border-bottom: 1px solid var(--line);
}
.drawer-head .title {
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft);
}
.drawer-close {
  width: 36px; height: 36px;
  border: none; background: transparent;
  font-size: 28px; line-height: 1;
  color: var(--ink-soft); cursor: pointer;
}

.drawer-nav { padding: 12px 0; }
.drawer-nav hr {
  border: none; height: 1px; background: var(--line);
  margin: 12px 0;
}
.drawer-section-label {
  padding: 8px 20px;
  font-family: "JetBrains Mono", monospace; font-size: 10px;
  letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft);
}
.drawer-link {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px;
  font-family: "Assistant", sans-serif; font-weight: 600; font-size: 16px;
  color: var(--ink); text-decoration: none;
  min-height: 44px;
}
.drawer-link:active { background: var(--paper-2); }
.drawer-link .dot {
  width: 9px; height: 9px; border-radius: 50%;
}
.drawer-link.world.soil .dot { background: var(--w-soil); }
.drawer-link.world.know .dot { background: var(--w-know); }
.drawer-link.world.code .dot { background: var(--w-code); }
.drawer-link.cta {
  color: var(--w-know-deep); font-weight: 700;
}
```

**JS minimum:**
```js
const toggle = document.querySelector('.nav-toggle');
const drawer = document.querySelector('.nav-drawer');
const backdrop = document.querySelector('.nav-backdrop');
const close = document.querySelector('.drawer-close');

function open() {
  drawer.classList.add('is-open');
  backdrop.classList.add('is-open');
  drawer.setAttribute('aria-hidden', 'false');
  toggle.setAttribute('aria-expanded', 'true');
  document.body.style.overflow = 'hidden';
}
function shut() {
  drawer.classList.remove('is-open');
  backdrop.classList.remove('is-open');
  drawer.setAttribute('aria-hidden', 'true');
  toggle.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}
toggle.addEventListener('click', open);
close.addEventListener('click', shut);
backdrop.addEventListener('click', shut);
document.addEventListener('keydown', e => { if (e.key === 'Escape') shut(); });
```

**A11y חובה:**
- `aria-expanded` על ה-toggle.
- `aria-hidden` על ה-drawer.
- Focus trap בתוך ה-drawer כשפתוח.
- ESC סוגר.
- כשנפתח — focus קופץ לראשון ב-drawer.
- כשנסגר — focus חוזר ל-toggle.

### 2.2 Mobile Footer

**שינויים:**
- 4 עמודות → **2 עמודות** ב-tablet, **1 עמודה** ב-mobile.
- Bottom row (copyright + Unless) → **stacked** במובייל.

```css
@media (max-width: 900px) {
  .shell-foot .cols { grid-template-columns: 1fr 1fr; }
  .shell-foot .bottom { flex-direction: column; align-items: flex-start; gap: 12px; }
}
@media (max-width: 640px) {
  .shell-foot .cols { grid-template-columns: 1fr; gap: 28px; }
  .shell-foot .brand-block { padding-bottom: 24px; border-bottom: 1px solid rgba(245,243,236,.15); }
  .shell-foot { padding: 48px var(--gutter-mobile, 20px) 32px; }
}
```

---

## 3. T1 · World page — Mobile

### Layout transformations

| section | desktop | mobile |
|---|---|---|
| Hero (Variant C) | Echo stack 80–220px | echoes hidden (`.echo { display: none }`), title 56–80px |
| Lattice (ליבה) | 3-column grid, anchor center spanning 2 rows | **stack:** anchor on top (full width), then 4 lat-sides as 2-col grid |
| CDIP diagram | 2-col side-by-side | stack: SVG above text |
| Bridges | 3-col | **2-col** at tablet, **1-col** at mobile |
| Projects | 3-col with rotations | **1-col**, rotations removed (clutter) |
| Posts | 2-col | **1-col**, dashed border between |

```css
@media (max-width: 900px) {
  .vc-hero-stack .echo { display: none !important; }
  .vc-hero-stack { font-size: clamp(56px, 14vw, 80px); }
  .vc-hero .gloss { grid-template-columns: 1fr; gap: 14px; }
  .vc-hero .gloss .rule { display: none; }
  .vc-lattice {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto;
  }
  .vc-lattice .lat-anchor {
    grid-column: 1 / -1;
    grid-row: 1 / 2;
  }
  .vc-projects .proj-card { transform: none !important; }
}
@media (max-width: 640px) {
  .vc-lattice { grid-template-columns: 1fr; }
  .vc-bridges, .vc-projects, .vc-posts { grid-template-columns: 1fr; }
}
```

---

## 4. T2 · Services — Mobile

| section | desktop | mobile |
|---|---|---|
| Breadcrumb | inline | inline, wraps if needed |
| Hero | 2-col (text+image) | stack, image הופך 16:10 |
| Bridge stripe + seam | 6px top + corner triangle | stripe stays, corner shrinks to 36px |
| Heritage strip | 3-col grid | **stack** vertically (label / text / link) |
| Meta strip | 4-col | **2-col** |
| Three-col (who/how/what) | 3 cards side-by-side | **stack** vertically, 1 card per row |
| Linked projects | 3-col | **1-col** |
| Related posts | 2-col | **1-col** |
| Final CTA | 2-col (text + buttons) | **stack**, buttons full-width, **sticky?** |
| **WhatsApp CTA** | inline beside form button | **sticky FAB** at bottom-right במובייל (ראו §10) |

```css
@media (max-width: 760px) {
  .heritage-strip { grid-template-columns: 1fr; gap: 10px; padding: 16px 18px; }
  .svc-meta-strip { grid-template-columns: 1fr 1fr; gap: 16px; padding: 18px; }
  .three-col { grid-template-columns: 1fr; gap: 18px; }
  .three-col .col { padding: 22px; }
  .linked-projects { grid-template-columns: 1fr; }
  .related-posts { grid-template-columns: 1fr; }
  .final-cta-inner { grid-template-columns: 1fr; gap: 24px; }
  .final-cta .cta-side { width: 100%; }
  .final-cta .cta-side .hero-cta { width: 100%; justify-content: center; }
  .t2-hero.bridge::after { border-width: 36px 36px 0 0; }
  .hero-cta-row { flex-direction: column; align-items: stretch; gap: 10px; }
  .hero-cta { width: 100%; justify-content: center; padding: 14px; }
  .hero-cta-hint { text-align: center; }
}
```

---

## 5. T3 · Project — Mobile

| section | desktop | mobile |
|---|---|---|
| Ribbon (seeking/legacy) | 3-col grid | stack |
| Hero | 2-col (text + image w/ stamp) | stack, image first w/ stamp |
| Story | 3-col (gutter \| body \| gutter) | full-width, padding | drop-cap shrinks to 3.4em |
| Linked services | 3-col | **1-col** |
| Outcomes (4 tiles) | 4-col | **2-col** at tablet, **1-col** at mobile |
| Gallery | 4-col mixed sizes | **2-col**, sizes simplified |
| More projects | 3-col | **1-col** |
| **Seeking CTA** | 2-col | stack, button full-width |

```css
@media (max-width: 900px) {
  .t3-hero-grid { grid-template-columns: 1fr; gap: 24px; }
  .t3-hero-image { aspect-ratio: 16/10; max-width: 100%; }
  .story { grid-template-columns: 1fr; padding-inline: 0; }
  .story p:first-of-type::first-letter { font-size: 3.4em; }
  .linked-services, .more-projects { grid-template-columns: 1fr; }
  .outcomes { grid-template-columns: 1fr 1fr; }
  .seeking-cta { grid-template-columns: 1fr; gap: 20px; }
  .seeking-cta .cta-btn { width: 100%; justify-content: center; }
  .legacy-ribbon, .seeking-ribbon { flex-wrap: wrap; gap: 10px; }
  .legacy-ribbon .span, .seeking-ribbon .span { margin-inline-start: 0; width: 100%; }
}
@media (max-width: 640px) {
  .gallery { grid-template-columns: 1fr 1fr; }
  .gallery .g-tall, .gallery .g-wide { grid-row: auto; grid-column: span 2; aspect-ratio: 4/5; }
  .outcomes { grid-template-columns: 1fr; }
}
```

---

## 6. T4 · Post — Mobile

| section | desktop | mobile |
|---|---|---|
| Layout 3-col (gutter \| body 64ch \| aside 240px) | as-is | **aside hidden**, ToC + Share + Related → at bottom of post |
| Hero image | 21:9 ratio | 16:9 (less letterbox) |
| Title | 84px max | clamps to 34-56px |
| Drop-cap | 4.6em | 3.6em |
| Aside ToC | sticky right column | becomes **collapsible accordion** at top of body or floating button |
| Share buttons | sticky aside | floating ribbon at bottom of viewport (3 circular buttons) |

```css
@media (max-width: 1100px) {
  .post-layout { grid-template-columns: 1fr; padding-inline: var(--gutter-mobile, 20px); }
  .post-layout .post-aside {
    display: block;
    grid-column: 1;
    position: static;
    margin-top: 48px;
    padding-top: 32px;
    border-top: 1px solid var(--line);
  }
  .post-hero-image { aspect-ratio: 16/9; }
}
@media (max-width: 640px) {
  .post-title { font-size: clamp(34px, 9vw, 56px); }
  .post-body { font-size: 17px; line-height: 1.72; }
  .post-body p:first-of-type::first-letter { font-size: 3.6em; }
  .post-body .pullquote { font-size: clamp(22px, 6vw, 32px); }
  .post-body blockquote { padding: 6px 16px; font-size: 18px; }
  .post-meta-row { gap: 14px; }
}
```

**Floating share buttons (optional UX upgrade):**
```css
@media (max-width: 760px) {
  .post-share-fab {
    position: fixed;
    bottom: 16px;
    inset-inline-start: 16px;
    z-index: 800;
    display: flex; gap: 8px;
    background: rgba(31,30,28,.88); backdrop-filter: blur(8px);
    border-radius: 100px; padding: 6px;
    box-shadow: 0 6px 20px rgba(31,30,28,.25);
  }
  .post-share-fab .share-btn {
    width: 40px; height: 40px;
    background: transparent; color: var(--paper);
    border: none;
  }
}
```

---

## 7. T5 · Blog — Mobile

### Critical: ה-bold editorial layout מתפרק במובייל

| flowStyle | desktop | mobile |
|---|---|---|
| `lead` | span 6, horizontal | span 1, vertical (image above) |
| `wide` | span 4, image-left | span 1, vertical |
| `tall` | span 2 × 2 rows | span 1, image 4:5 |
| `typo` | span 3, dark bg | span 1, dark bg (full-width statement) |
| `quote` | span 3, italic | span 1, italic |
| `feature` | span 3 | span 1 |
| `brief` | span 2 | span 1, with top border |

```css
@media (max-width: 760px) {
  .post-flow { grid-template-columns: 1fr; gap: 28px; }
  .flow-item { grid-column: 1 !important; grid-row: auto !important; }
  .flow-item.flow-lead, .flow-item.flow-wide {
    flex-direction: column;
    padding: 24px;
  }
  .flow-item.flow-lead .flow-img,
  .flow-item.flow-wide .flow-img { flex: 0 0 auto; }
  .flow-item.flow-lead .flow-img .img-ph,
  .flow-item.flow-wide .flow-img .img-ph { aspect-ratio: 16/10; min-height: auto; }
  .flow-item.flow-tall .img-ph { aspect-ratio: 4/5; min-height: auto; }
  .flow-item.flow-typo { min-height: auto; padding: 28px; }
  .flow-item.flow-quote { min-height: auto; padding: 28px; }
  .flow-quote-mark { font-size: 72px; top: 8px; }
  .flow-item.flow-brief { padding-block: 20px; }
}
```

### Filter bar — Mobile

**Desktop:** horizontal, sticky.
**Mobile:** **horizontal scroll** with -ms-overflow-style: none, sticky, sectioned.

```css
@media (max-width: 640px) {
  .filter-bar { padding: 10px var(--gutter-mobile, 16px); }
  .filter-bar-inner {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    padding-bottom: 4px;
  }
  .filter-bar-inner::-webkit-scrollbar { display: none; }
  .filter-bar-inner > * { flex-shrink: 0; }
  .filter-count { margin-inline-start: 12px; }
  .view-toggle { order: -1; }   /* view toggle first on mobile */
}
```

### Blog header

```css
@media (max-width: 900px) {
  .blog-header h1 { font-size: clamp(48px, 13vw, 72px); }
  .blog-header-grid { grid-template-columns: 1fr; gap: 24px; }
  .blog-header .stats { text-align: start; }
}
```

---

## 8. T7 · Home — Mobile

### Hero (Statement variant — נעול)

```css
@media (max-width: 900px) {
  .hero-statement { padding-block: 56px 40px; }
  .hero-statement .grid { grid-template-columns: 1fr; gap: 32px; }
  .hero-statement h1 { font-size: clamp(34px, 7vw, 48px); }
  .hero-statement .lede { font-size: 16px; }
  .hero-statement svg { max-width: 240px; }
  .hero-statement .meta-row { gap: 16px; flex-direction: column; }
  .hero-statement .meta-row span { font-size: 13px; }
}
```

### Worlds section (3 cards)

```css
@media (max-width: 900px) {
  .worlds-grid { grid-template-columns: 1fr 1fr; }
  .world-card { min-height: 240px; padding: 24px; }
  .world-card h3 { font-size: clamp(28px, 6vw, 36px); }
}
@media (max-width: 640px) {
  .worlds-grid { grid-template-columns: 1fr; }
}
```

### Featured projects

```css
@media (max-width: 900px) {
  .featured-projects { grid-template-columns: 1fr 1fr; gap: 16px; }
  .fp-card.fp-large { grid-column: 1 / -1; grid-row: auto; }
  .fp-card.fp-large h3 { font-size: 24px; }
}
@media (max-width: 640px) {
  .featured-projects { grid-template-columns: 1fr; }
  .fp-card.fp-large { grid-column: 1; }
}
```

### Recent posts (4 → ?)

```css
@media (max-width: 900px) {
  .recent-posts { grid-template-columns: 1fr 1fr; }
  .rp-card .img-ph { aspect-ratio: 16/10; }
}
@media (max-width: 640px) {
  .recent-posts { grid-template-columns: 1fr; }
  .rp-card .img-ph { aspect-ratio: 1; max-height: 280px; }
}
```

### Unless ribbon

```css
@media (max-width: 900px) {
  .unless-block.ribbon { padding: 36px var(--gutter-mobile, 20px); }
  .unless-block.ribbon .ribbon-inner { grid-template-columns: 1fr; gap: 16px; }
  .unless-block.ribbon .quote { font-size: clamp(28px, 7vw, 40px); }
  .unless-block.ribbon .anno { font-size: 10px; }
}
```

### Final CTA paths

```css
@media (max-width: 900px) {
  .cta-paths { grid-template-columns: 1fr; gap: 16px; }
  .cta-path { padding: 28px; }
  .cta-path h3 { font-size: clamp(22px, 5vw, 28px); }
  .final-cta-home h2 { font-size: clamp(34px, 8vw, 48px); }
}
```

---

## 9. T8 · Static — Mobile

### About

```css
@media (max-width: 760px) {
  .about-hero h1 { font-size: clamp(36px, 9vw, 56px); max-width: 100%; }
  .about-hero .lede { font-size: 17px; }
  .about-gallery { grid-template-columns: repeat(3, 1fr); }
  .about-gallery .img-ph:nth-child(n+4) { display: none; }
  .about-hero .factrow { gap: 18px; }
  .about-hero .factrow .row { flex: 1 1 calc(50% - 9px); }
  .story-block { grid-template-columns: 1fr; }
  .story-block .story-inner { grid-column: 1; }
  .story-block p { font-size: 17px; line-height: 1.72; }
  .story-block p:first-of-type::first-letter { font-size: 3.4em; }
  .journey { grid-template-columns: 1fr; }
  .journey-track { display: none; }
  .j-event::before { display: none; }
  .thesis { grid-template-columns: 1fr; }
  .values { grid-template-columns: 1fr; }
  .media-grid { grid-template-columns: 1fr; }
  .media-item { grid-template-columns: auto 1fr; }
  .media-arrow { display: none; }
  .media-title { white-space: normal; }
}
```

### Heritage

```css
@media (max-width: 760px) {
  .heritage-hero h1 { font-size: clamp(36px, 10vw, 64px); }
  .heritage-image { aspect-ratio: 16/9; }
  .heritage-body { font-size: 17px; line-height: 1.72; }
  .heritage-body p:first-of-type::first-letter { font-size: 3.4em; }
  .heritage-body h2 { margin-top: 40px; }
  .heritage-end { grid-template-columns: 1fr; gap: 16px; }
  .heritage-end a.btn { width: 100%; justify-content: center; }
}
```

### Contact

```css
@media (max-width: 760px) {
  .contact-hero h1 { font-size: clamp(36px, 9vw, 56px); }
  .contact-body { grid-template-columns: 1fr; gap: 32px; }
  .contact-form { padding: 24px; }
  .field input, .field textarea, .field select { font-size: 16px; padding: 12px 16px; }
  /* iOS zoom prevention: input font-size >= 16px */
  .topic-chips { gap: 6px; }
  .topic-chip { padding: 8px 14px; font-size: 13px; min-height: 36px; }
  .form-submit { width: 100%; padding: 14px; justify-content: center; }
  .contact-card { padding: 20px; }
  .contact-card .wa-btn { width: 100%; justify-content: center; padding: 14px; }
}
```

**iOS-specific fix:** כל input/textarea חייב להיות **font-size ≥ 16px** במובייל — אחרת iOS עושה auto-zoom בעת focus.

---

## 10. WhatsApp FAB — Sticky button across the site

**הצעה:** במובייל, על כל עמוד שאיננו עמוד contact עצמו, להציג כפתור WhatsApp צף בפינה תחתית. זה ה-CTA הראשי במובייל.

```html
<a href="https://wa.me/972547776770"
   class="wa-fab"
   target="_blank" rel="noopener"
   aria-label="WhatsApp - שלח הודעה">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.5 14.4c-.3-.1-1.7-.8-1.9-.9-.3-.1-.5-.1-.7.1-.2.3-.8.9-1 1.1-.2.2-.4.2-.6.1-.3-.1-1.2-.5-2.2-1.4-.8-.7-1.4-1.6-1.5-1.9-.2-.3 0-.4.1-.6.1-.1.3-.4.4-.5.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5-.1-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5 4.5.7.3 1.3.5 1.7.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 2.1C6.5 2.1 2.1 6.6 2.1 12c0 1.7.4 3.3 1.3 4.7L2.1 22l5.4-1.3c1.4.8 3 1.2 4.5 1.2 5.5 0 9.9-4.5 9.9-9.9S17.5 2.1 12 2.1z"/>
  </svg>
</a>
```

```css
.wa-fab {
  display: none;  /* mobile only */
  position: fixed;
  bottom: max(16px, env(safe-area-inset-bottom));
  inset-inline-end: 16px;
  width: 56px; height: 56px;
  background: var(--ink);
  color: var(--paper);
  border-radius: 50%;
  display: grid; place-items: center;
  text-decoration: none;
  box-shadow: 0 6px 16px rgba(31,30,28,.25);
  z-index: 700;
  transition: transform .15s, background .15s;
}
.wa-fab:active { transform: scale(0.95); background: var(--w-soil-deep); }

@media (max-width: 900px) {
  body:not([data-page="contact"]) .wa-fab { display: grid; }
}
```

**Behavior rules:**
- מוצג: בכל עמוד פרט ל-`/contact` (שם הכפתור כבר בולט).
- נעלם: כשהמשתמש פותח את ה-drawer.
- נעלם בתוך iOS keyboard active (אופציונלי, JS-based).
- z-index פחות מ-drawer (999) ומ-modals.

---

## 11. Image performance

### Responsive images (חובה)

```html
<picture>
  <source srcset="/img/hero-soil-mobile.webp"
          media="(max-width: 640px)"
          type="image/webp">
  <source srcset="/img/hero-soil-tablet.webp"
          media="(max-width: 900px)"
          type="image/webp">
  <source srcset="/img/hero-soil-desktop.webp"
          type="image/webp">
  <img src="/img/hero-soil-desktop.jpg"
       alt="..."
       loading="lazy"
       width="1920" height="1080">
</picture>
```

**שלוש רזולוציות לכל hero image:**
- `_mobile.webp/jpg` — 800px wide
- `_tablet.webp/jpg` — 1280px wide
- `_desktop.webp/jpg` — 1920px wide

**Watercolor illustrations (T-03):** מנוע ייצור האיורים יקבל הוראה לייצר **3 רזולוציות** של כל איור (ולא רק 2 כפי שהיה ב-prompt המקורי). יש לעדכן את `01-PROMPT-watercolor-backgrounds.md` בהתאם.

### lazy loading
- `loading="lazy"` על כל תמונה מתחת ל-fold.
- `loading="eager"` על תמונת ה-hero בלבד.
- `fetchpriority="high"` על hero image של ה-LCP.

---

## 12. Forms — Mobile UX

### Contact form (T8)
- `font-size: 16px` minimum (iOS zoom prevention).
- `inputmode` attribute לכל field:
  - email: `inputmode="email"`
  - phone: `inputmode="tel"`
  - text: default
- `autocomplete` חובה: `email`, `tel`, `name`, `street-address` וכו'.
- Submit button — full-width במובייל, **לא** sticky.
- Topic chips — wrap freely, אסור horizontal scroll (קשה ל-thumbs).
- Textarea — auto-resize אם אפשרי.

### Validation
- HTML5 native validation מספקת. אסור JS-only validation שמסתיר server errors.
- Error messages — בעברית, ברורות, מתחת ל-field.
- Required fields — מסומנים בכוכבית קטנה next to label.

---

## 13. Touch + gesture patterns

### Drawer
- Swipe-to-close מצד-שמאל (LTR) או צד-ימין (RTL) — optional UX.
- Tap על backdrop = close.

### Image galleries (T3 gallery, T8 about-gallery)
- במובייל: tap-to-zoom (light box) — אופציונלי, גם בלי זה בסדר.
- אם בונים lightbox: swipe ימינה/שמאלה לניווט, swipe למטה לסגירה.

### Cards
- Active state: subtle scale-down (`transform: scale(0.98)`) on tap.
- Hover effects שהיו ב-desktop — **אסור** להפעיל ב-mobile (`@media (hover: hover)`).

```css
/* Desktop hover only */
@media (hover: hover) {
  .svc-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-l); }
}
/* Mobile active state */
@media (hover: none) {
  .svc-card:active { transform: scale(0.98); }
}
```

---

## 14. Performance budgets

### Targets per page (Lighthouse mobile)
| Metric | Budget |
|---|---|
| Performance | ≥ 90 |
| Accessibility | 100 |
| Best practices | ≥ 95 |
| SEO | 100 |
| FCP | ≤ 1.5s |
| LCP | ≤ 2.5s |
| CLS | ≤ 0.05 |
| TTI | ≤ 3.5s |
| Total page weight | ≤ 800KB (T7), ≤ 1.2MB (T1) |

### Critical CSS
- T7 (Home) — critical CSS inline (~10KB).
- שאר העמודים — defer.

### Fonts
- `font-display: swap` חובה.
- Subset Frank Ruhl Libre + Assistant ל-Hebrew + Latin בלבד.
- Preload weights `400` ו-`700` בלבד.

### JS
- כלל-זהב: **דף הבית עובד ללא JS**. הכל progressive enhancement.
- Total JS payload ≤ 30KB minified+gzipped (לא כולל analytics).

---

## 15. RTL חזרה לבדיקה

כל ה-mobile breakpoints חייבים לעבוד גם ב-RTL וגם ב-LTR (לעתיד — אם יוסיפו אנגלית). השתמשו ב-logical properties תמיד:
- `inset-inline-start/end` ולא `left/right`
- `margin-inline-start/end`
- `padding-inline-start/end`
- `border-inline-start/end`

**חריג מותר:** `linear-gradient(to left, …)` — צריך החלפה מדויקת לפי direction. השתמשו ב-CSS custom property:

```css
:root {
  --bg-stripe: linear-gradient(to left, var(--bridge-a) 0 50%, var(--bridge-b) 50% 100%);
}
[dir="ltr"] :root {
  --bg-stripe: linear-gradient(to right, var(--bridge-a) 0 50%, var(--bridge-b) 50% 100%);
}
```

---

## 16. Definition of Done — Mobile

✅ כל 7 התבניות עוברות viewport audit ב-360px, 414px, 768px ו-1024px
✅ Drawer nav עובד ב-iOS Safari + Chrome Android
✅ Forms עובדים ללא zoom-on-focus ב-iOS
✅ WhatsApp FAB מופיע בכל עמוד פרט ל-contact
✅ Touch targets ≥ 44×44 בכל פעולה
✅ אין horizontal scroll באף viewport
✅ Lighthouse mobile ≥ 90 בכל ה-metrics
✅ Image srcsets responsive בכל hero
✅ A11y: screen reader navigation עובד ב-VoiceOver iOS + TalkBack Android
✅ הכל עובד ללא JS (חוץ מ-drawer toggle, שיש לו fallback)
✅ Safe-area-inset-bottom מטופל ב-footer + sticky FAB

---

## 17. עדכון לקבצי החבילה

מסמך זה מתווסף ל-`_handoff/` כ-`04-MOBILE-spec.md`. הוא משלים ולא מחליף:

| קובץ | סטטוס |
|---|---|
| `00-HANDOFF-claude-code-110.md` | ראש החבילה — מציין שיש מובייל-ספק נפרד |
| `01-PROMPT-watercolor-backgrounds.md` | **לעדכן** — לבקש 3 רזולוציות במקום 2 |
| `02-PROMPT-logo-family.md` | בלי שינוי |
| `03-RESPONSE-team100-V200.md` | בלי שינוי |
| **`04-MOBILE-spec.md`** | **חדש — הקובץ הזה** |

### תיקון נדרש ב-PROMPT האיורים (`01-...`)

הוסיפו לחלק "Output Formats":
> **Mobile-specific renders:** בנוסף ל-1920×1080 desktop, ייצרו גם:
> - 1280px wide (tablet) — ratio 16:9 או 4:3 לפי האיור
> - 800px wide (mobile) — ratio 16:10 או 4:3 (compositions פשוטות יותר — פחות אזורים שקטים נדרשים)
>
> **סה"כ:** 15 קבצי תמונה (5 איורים × 3 רזולוציות) במקום 10.

---

**Sign-off:** ערוץ זה סוגר את **T-02 (Mobile screens · Stage 5)**. כל שינוי במובייל מחייב חזרה לצוות 35.

— צוות 35 · 25.05.2026
