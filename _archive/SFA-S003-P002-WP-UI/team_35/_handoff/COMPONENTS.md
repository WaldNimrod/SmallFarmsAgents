# Component Catalog — canonical

Every reusable UI element with: purpose, DOM, class names, props/data-attrs, and the design canvas artboard where it's visible.

The naming convention is **strict** — class names prefixed `.gj-*` (mobile) and `.dt-*` (desktop). Components that work in both share a `.gj-*` name.

---

## 1. Shells

### 1.1 `.gj-shell` — mobile module shell

Wraps a single module page (or hub page) on mobile. Width 390px design, fluid in production.

```html
<div class="gj-shell">
  <header class="gj-header gj-header--plain">
    <div class="gj-header__row">
      <button class="gj-iconbtn" aria-label="חזרה">←</button>   <!-- optional -->
      <span class="gj-mark"><svg>...</svg></span>               <!-- 36×36 logo -->
      <div class="gj-header__title">
        <div class="gj-title">SFA</div>
        <div class="gj-sub">חקלאות קטנה</div>
      </div>
      <button class="gj-iconbtn" aria-label="חיפוש">⌕</button>
    </div>
    <nav class="gj-tabs" role="tablist">  <!-- optional, omit on detail pages -->
      <button class="gj-tab is-active">מחירון</button>
      <button class="gj-tab">ספר גידולים</button>
    </nav>
  </header>
  <main class="gj-body">…page content…</main>
  <footer class="gj-foot">
    <span class="gj-foot__dot"></span>
    <span>עודכן 14:32 · 14 מקורות</span>
  </footer>
</div>
```

**Behavior:**
- `dir="rtl"` is on `<html>` — shell relies on that.
- `gj-foot__dot` color comes from `--status-fresh/aging/stale/error` — pass `style="background: var(--status-stale)"` for older data.

### 1.2 `.dt-shell` — desktop shell

Two-column grid: 280px sidebar + 1fr main. The sidebar uses `<details>` accordions.

```html
<div class="dt-shell">
  <aside class="dt-side">
    <div class="dt-side__brand">
      <svg class="..."/>SFA</svg>
      <div class="dt-side__name">SFA</div>
    </div>

    <input class="dt-side__search" type="search" placeholder="חיפוש…"/>

    <nav class="dt-nav">
      <details class="dt-acc" open>
        <summary><span class="tier tier--leaf">●כלים לקהילה</span><span class="dt-acc__chev">▾</span></summary>
        <a class="is-active" href="/sfa/">דף הבית</a>
        <a href="/sfa/book/">ספר גידולים <span class="dt-nav__count">66</span></a>
        <a href="/sfa/market/">מחירון <span class="dt-nav__count">30</span></a>
        <a href="/sfa/calc/">מחשבון <span class="pill pill--code dt-nav__pill">β</span></a>
      </details>

      <details class="dt-acc">
        <summary><span class="tier tier--soil">★כלים מתקדמים</span><span class="dt-acc__chev">▾</span></summary>
        …
      </details>

      <details class="dt-acc">
        <summary><span class="tier tier--tomato">✎בדיוק לחווה שלך</span><span class="dt-acc__chev">▾</span></summary>
        …
        <a class="dt-nav__cta" href="https://wa.me/972547776770">+ הציעו כלי חדש</a>
      </details>

      <details class="dt-acc dt-acc--comm" open>
        <summary><span class="tier tier--sun">✺קהילה</span><span class="dt-acc__chev">▾</span></summary>
        <div class="dt-side__stats"><div><strong>247</strong><span>תיקונים</span></div>…</div>
        <div class="dt-side__contrib">
          <a class="dt-side__crow">✎ תרמו ידע</a>
          <a class="dt-side__crow">◐ דווחו על שגיאה</a>
          <a class="dt-side__crow">💡 הציעו פיצ׳ר</a>
        </div>
        <div class="dt-side__feedh">פעילות אחרונה</div>
        <article class="feed-item">…</article>
        <a class="dt-side__wa" href="https://wa.me/...">💬 WhatsApp · ‎צ׳אט פתוח</a>
      </details>
    </nav>
  </aside>

  <main class="dt-main">
    <header class="dt-topbar">
      <div>
        <h1 class="dt-topbar__h">…page title…</h1>
        <p class="dt-topbar__sub">…subtitle…</p>
      </div>
      <div class="dt-topbar__tools">
        <button class="dt-topbar__contrib">+ תרמו ידע</button>
        <button class="dt-topbar__login">היכנס / הירשם</button>
      </div>
    </header>
    <div class="dt-content">…page content…</div>
  </main>
</div>
```

**Behavior:**
- All `<details>` start open or closed per the design (book = open by default).
- The active link gets `.is-active` (background var(--gj-ink), color var(--gj-paper)).

---

## 2. Tier badge — `<TierBadge tier="open|beta|coming|paid|custom" size="sm|lg" />`

```html
<span class="tier tier--leaf"><span class="tier__glyph">●</span>כלים לקהילה</span>
<span class="tier tier--lg tier--sun"><span class="tier__glyph">β</span>בטא · ניסיוני</span>
```

| tier | glyph | color | label (he) |
|------|-------|-------|------------|
| open   | ●  | leaf   | כלים לקהילה |
| beta   | β  | sun    | בטא · ניסיוני |
| coming | ⏳ | paper  | בקרוב |
| paid   | ★  | soil   | כלים מתקדמים |
| custom | ✎  | tomato | בדיוק לחווה שלך |

---

## 3. Module card — `<ModuleThumb m="..." />`

Used in the Hub home grid (mobile + desktop). Square 1:1 art on top, title + tier + meta below.

```html
<a class="mod-card mod-card--leaf mod-card--open" href="/sfa/book/" data-tier="open">
  <div class="mod-card__art">
    <!-- ImagePrompt slot OR real <img src=".../thumb.webp"> -->
    <div class="mod-card__icon"><svg>…tomato…</svg></div>
  </div>
  <div class="mod-card__body">
    <div class="mod-card__head">
      <h3 class="mod-card__name">ספר גידולים</h3>
      <span class="tier tier--leaf">●פתוח</span>
    </div>
    <p class="mod-card__sub">אינדקס פתוח של גידולים, זנים, מחזורי גידול</p>
    <p class="mod-card__stat">66 גידולים · 242 זנים</p>
  </div>
</a>
```

`data-tier="coming"` dims the card (`opacity: .65`). `data-tier="custom"` adds the warm gradient backdrop.

---

## 4. Cross-link card — book ↔ market

Used in crop detail (links to market price) and market detail (links to crop book entry).

```html
<a href="/sfa/market/?product=tomato" class="gj-crosslink">
  <div class="gj-crosslink__art"><!-- icon or thumb --></div>
  <div class="gj-crosslink__body">
    <div class="gj-crosslink__big">12.40 <small>₪/ק״ג</small></div>
    <div class="gj-crosslink__sub">מחיר שוק נוכחי · 6 מקורות · −4% משבוע</div>
  </div>
  <span class="gj-crosslink__cta">פתח →</span>
</a>
```

Modifier `.gj-crosslink--soil` flips palette to leaf/green for market → book direction.

---

## 5. Price card — `.pcard` (mobile) / `.dt-mkt-card` (desktop)

Three regions: glyph + name/unit | price + median | distribution bar + meta.

```html
<div class="pcard">
  <div class="pcard__head">
    <div class="pcard__glyph">ע</div>
    <div>
      <div class="pcard__name">עגבנייה</div>
      <div class="pcard__unit">ק"ג · ‎Tomato</div>
    </div>
  </div>
  <div class="pcard__price">
    <span class="big">12.40</span>
    <span class="cur">₪</span>
    <span class="med">חציון 12.00</span>
  </div>
  <div class="pcard__range">
    <div class="fill" style="inset-inline-end: 25%; inline-size: 30%"></div>
  </div>
  <div class="pcard__range-text">
    <span>9.50</span>
    <span>16.00 ₪</span>
  </div>
  <div class="pcard__meta">
    <span><span class="sources"><span></span>…</span> 6</span>
    <span>24 תצפיות</span>
    <span style="margin-inline-start:auto; color:var(--gj-soil-deep)">↗ ספר</span>
  </div>
</div>
```

---

## 6. Crop card grid — `.gj-cropcard`

Square art block on top, name + en italic + tier pill + DTM badge below.

```html
<a class="gj-cropcard" href="/sfa/book/crop/tomato/">
  <div class="gj-cropcard__art">
    <div class="gj-cropcard__icon"><svg>…</svg></div>
  </div>
  <div class="gj-cropcard__body">
    <div class="gj-cropcard__name">עגבנייה</div>
    <div class="gj-cropcard__en">Tomato</div>
    <div class="gj-cropcard__meta">
      <span class="gj-tag">ירקות</span>
      <span class="gj-cropcard__dtm">70<small>ימים</small></span>
    </div>
  </div>
</a>
```

---

## 7. Variety card — `.cb-var` (mobile) / `.dt-var` (desktop)

The 6-field hierarchy under each crop. Star marks default variety. F1 vs heirloom pill.

```html
<a class="cb-var" href="/sfa/book/crop/tomato/variety/tamar-f1/">
  <div class="cb-var__head">
    <span class="cb-var__star">★</span>
    <h4>תמר F1</h4>
    <span class="pill pill--code">F1 · מורכב</span>
  </div>
  <div class="cb-var__grid">
    <span><small>DTM</small>68</span>
    <span><small>יבול</small>9.2 ק״ג/מ״ר</span>
    <span><small>צבע</small>אדום</span>
    <span><small>צורה</small>אשכולי</span>
    <span><small>טעם</small>★★★★</span>
    <span><small>עמידות</small>TYLCV</span>
  </div>
</a>
```

---

## 8. Contribute Strip — `.contrib-strip` (drop into any module page)

The most important community surface — appears in market list, crop detail, market detail.

```html
<form class="contrib-strip" action="/wp-json/sfa/v1/contribute" method="post">
  <input type="hidden" name="context" value="market.tomato"/>

  <div class="contrib-strip__head">
    <span class="contrib-strip__icon">✎</span>
    <div>
      <div class="contrib-strip__h">תורמים נתונים? לא חייבים להירשם.</div>
      <div class="contrib-strip__sub">מחירון · ‎עגבנייה — כל תרומה נסקרת ידנית.</div>
    </div>
  </div>

  <div class="contrib-strip__input">
    <input type="text" name="text" placeholder="אצלי 10.80, יום ראשון…"/>
    <button type="submit">שלחו</button>
  </div>

  <div class="contrib-strip__quick" role="group">
    <button type="button" data-kind="price-correction">מחיר שונה</button>
    <button type="button" data-kind="missing-variety">זן חסר</button>
    <button type="button" data-kind="error">שגיאה</button>
    <button type="button" data-kind="suggestion">הצעה</button>
  </div>
</form>
```

**Endpoint contract** (LOD400 to spec):
- `POST /wp-json/sfa/v1/contribute`
- Body: `{ context, text, kind?, name?, email?, phone? }`
- Response: `{ id, queued: true }`
- Rate: 5 per IP per hour; auth-less.

---

## 9. Community feed item — `<FeedItem />`

```html
<article class="feed-item">
  <div class="feed-item__kind feed-item__kind--leaf">
    <span>✎</span>
    <small>תרומה</small>
  </div>
  <div class="feed-item__body">
    <div class="feed-item__head">
      <strong>רחל ש. · ‎שרון</strong>
      <span class="feed-item__date">3 ימים</span>
    </div>
    <p class="feed-item__text">הוספתי 4 זנים של חסה לספר…</p>
    <div class="feed-item__meta">
      <span class="pill pill--muted feed-item__tag">ספר · חסה</span>
      <span class="feed-item__upvotes">▲ 18</span>
    </div>
  </div>
</article>
```

Kinds: `suggest` (sun, 💡), `correction` (tomato, ◐), `data` (leaf, ✎).

---

## 10. Market disclaimer block — `.mk-disclaimer`

**Mandatory** at the top of every market view. Two variants:

### Mobile: `<MarketDisclaimer />`

4 bullet points: what / from / why / NOT. ~7 lines.

### Desktop: `<MarketDisclaimerFull />`

2-column, 8 bullets. Emphasizes "this is primarily a community marketing tool."

```html
<div class="mk-disclaimer">
  <div class="mk-disclaimer__head">
    <span class="mk-disclaimer__icon">ⓘ</span>
    <h4 class="mk-disclaimer__h">מה זה? מאיפה זה? למה זה?</h4>
  </div>
  <ul class="mk-disclaimer__list">
    <li><strong>מה:</strong> ממוצעים מתגלגלים של מחירי תוצרת חקלאית טרייה — 7 ימים אחרונים.</li>
    <li><strong>מאיפה:</strong> סוכני סריקה ציבוריים של mezoo + תרומות חקלאים. ‎מצרפי, אנונימי.</li>
    <li><strong>למה:</strong> כלי שיווקי קהילתי. הוכחה שאפשר ידע פתוח גם בשוק החקלאי הקטן.</li>
    <li><strong>לא:</strong> לא הצעה מסחרית, לא קביעת מחיר, לא חוות-דעת. הקשר אינדיקטיבי בלבד.</li>
  </ul>
  <a href="/sfa/market/methodology" class="mk-disclaimer__cta">קראו עוד על המתודולוגיה →</a>
</div>
```

Copy is **fixed** — do not paraphrase without team_00 approval.

---

## 11. Calculator field — `<CalcField />`

```html
<fieldset class="dt-calc-field">
  <legend>יבול צפוי (מהספר)</legend>
  <div class="dt-calc-row">
    <input type="number" value="9.2" step="0.1"/>
    <span class="dt-calc-unit">ק״ג/מ״ר</span>
    <button type="button" class="dt-calc-help">↗ ספר</button>
  </div>
  <small>טווח בספר: 5.5–11.4 ק״ג/מ״ר. ‎ערך ברירת מחדל = ממוצע זן.</small>
</fieldset>
```

The `↗ ספר` button cross-links to the book entry (data source for the default value).

---

## 12. Timeline — `.gj-timeline` (mobile) / `.dt-timeline` (desktop)

3-segment bar: prep (soil) / grow (leaf) / harvest (tomato).

```html
<section class="gj-timeline">
  <h4>חיי הגידול</h4>
  <div class="gj-timeline__bar">
    <div class="gj-timeline__seg gj-timeline__seg--prep" style="width: 14%">הכנה</div>
    <div class="gj-timeline__seg gj-timeline__seg--grow" style="width: 56%">גידול</div>
    <div class="gj-timeline__seg gj-timeline__seg--harv" style="width: 30%">קציר · 28 ימים</div>
  </div>
  <div class="gj-timeline__ruler">
    <span>שבוע 1</span>
    <span>שבוע 6</span>
    <span>שבוע 12</span>
  </div>
</section>
```

---

## 13. Status / freshness dot — `.gj-foot__dot`

Single-rule indicator at the bottom of every shell. Pass `style="background: var(--status-*)"`.

| State | Color | Footer copy |
|-------|-------|-------------|
| fresh   | leaf   | "עודכן לפני N דקות/שעות" |
| aging   | sun    | "עודכן לפני יום" |
| stale   | tomato | "עשוי שלא להיות עדכני" + stale banner above content |
| error   | red    | "שגיאת טעינה" + error block in content |

---

## 14. Stale banner — top of content

```html
<div class="mk-disclaimer" style="border-inline-start: 4px solid var(--status-stale); background: #fde9d4;">
  <div class="mk-disclaimer__head">
    <span class="mk-disclaimer__icon">⚠</span>
    <h4 class="mk-disclaimer__h">הנתונים עשויים שלא להיות עדכניים</h4>
  </div>
  <p style="margin: 0; font-size: 13px;">מעל 3 ימים מאז העדכון האחרון.</p>
</div>
```

---

## 15. ImagePrompt slot — `<ImagePrompt id="..." prompt="..." />`

Placeholder for AI-generated background images. Renders a tinted gradient + the prompt text + "copy prompt" button. Optionally wraps `<image-slot>` for user-drop replacement.

For production, the placeholder is **replaced** by a real `<img loading="lazy" src="...">` once the AI-rendered image is sourced and placed under `wp-content/uploads/sfa/images/`. The prompt catalog (`art-prompts.jsx::PROMPTS`) maps slot id → prompt string and is mirrored in `MODULES_REGISTRY.yaml`.

---

## 16. Pills — `.pill.pill--{tone}`

Generic small label. Tones: `soil`, `know` (mapped to tomato), `code` (mapped to sun), `muted`, `warn`, `spark`.

```html
<span class="pill pill--soil">ירקות</span>
<span class="pill pill--code">F1 · מורכב</span>
<span class="pill pill--muted">70 ימים</span>
```

---

## 17. Tabs — `.gj-tabs` (module switcher) / `.cb-deep-tabs` (within-page) / `.dt-path-tabs` (within-page desktop)

All use `<button class="…">` with `.is-active` modifier. No ARIA roles required for now — LOD400 should add when needed.
