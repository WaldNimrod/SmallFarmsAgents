---
id: RESEARCH_team35_design_digest_2026-05-27_v1.0.0
from_team: team_100 (research sub-agent — read-only)
for_team: team_100 (build agent — SFA-S003-P002-WP-UI re-build)
date: 2026-05-27
source_pkg: SFA-S003-P002-WP-UI-handoff-v1.2.0 (team_35, 2026-05-26)
source_root: .claude/worktrees/gallant-elbakyan-727a60/_archive/SFA-S003-P002-WP-UI/team_35/_handoff/
status: REFERENCE
purpose: Single condensed digest of team_35 LOD300 design contract for the WP-UI re-build.
note: Mandate states the deliverable is a WordPress page-template (per the v1 build context).
      HANDOFF_LOD300 §2 from team_35 originally specified a Flask Blueprint at sfa.nimrod.bio,
      but the live re-build context (MANDATE_WP-UI-RE-BUILD_v1.0.0.md) operates on PHP
      templates (_layout.php / shell/mobile.php / *.php pages + macros). The design contract
      below is stack-neutral — BEM classes + DOM + tokens — and applies identically.
---

# Team 35 LOD300 Design-Contract Digest — for WP-UI Re-Build

This is the design-contract reference for re-building the standalone SFA UI shell. It condenses
~120 KB of team_35 source across 7 handoff docs + ~9 CSS/JSX design files into the load-bearing
contract surface team_100 needs to BUILD against. Source files are linked, not duplicated.

---

## 1. Shells (mobile + desktop + mark SVG)

### 1.1 Mobile shell — `.gj-shell` (`<900px`)

Source: `COMPONENTS.md §1.1`, `TEMPLATES.md §4`, `design/gj.css`.

```
.gj-shell                                  ← root container (column flex)
└── header.gj-header.gj-header--plain      ← always paper bg, 1px border bottom
    ├── div.gj-header__row                 ← flex row, gap 10px, padding 12px 16px 10px
    │   ├── a.gj-iconbtn[aria-label="חזרה"]   ← OPTIONAL back-button when back_url set
    │   ├── span.gj-mark                   ← 28-36px logo slot (inline SVG, see §1.4)
    │   ├── div.gj-header__title
    │   │   ├── div.gj-title              ← Frank Ruhl Libre, 17px, page_title
    │   │   └── div.gj-sub                ← JetBrains Mono 10px uppercase, page_sub
    │   └── a.gj-iconbtn[aria-label="חיפוש"] ← search ⌕ icon → /search
    └── nav.gj-tabs[role="tablist"]        ← OPTIONAL only when show_module_tabs=true
        ├── a.gj-tab.is-active             ← מחירון / ספר גידולים
        └── a.gj-tab
├── main.gj-body                           ← {% block body %}, padding 14px 16px 80px, scrolls
└── footer.gj-foot                         ← 1px border top, paper-2 bg, mono 11px
    ├── span.gj-foot__dot                  ← inline style: background: var(--status-{state})
    ├── span (label_he)
    └── span (sources count, opt.)
```

**Width:** 390px design, fluid in production. **Direction:** `<html dir="rtl">` required.

**Footer dot states** (drives `--status-*` token):
- `fresh` → leaf | `aging` → sun | `stale` → tomato | `error` → red

### 1.2 Desktop shell — `.dt-shell` (`≥900px`)

Source: `COMPONENTS.md §1.2`, `TEMPLATES.md §5`, `design/desktop.css`, `design/desktop.jsx::DesktopShell`.

Two-column grid: **280px sidebar + 1fr main**.

```
.dt-shell
├── aside.dt-side                            ← left sidebar (in RTL = right edge)
│   ├── div.dt-side__brand                   ← logo + .dt-side__name "SFA" + .dt-side__tag
│   ├── form > input.dt-side__search[type=search name=q] → /search
│   ├── nav.dt-nav[data-stateful-accordion]
│   │   ├── details.dt-acc[data-tier="open" open]
│   │   │   ├── summary > {tier_badge('open')} + span.dt-acc__chev "▾"
│   │   │   └── a[.is-active]            ← per-module link
│   │   │       (+ span.dt-nav__count or span.pill.pill--code.dt-nav__pill)
│   │   ├── details.dt-acc[data-tier="paid"]
│   │   │   └── a + span.pill.pill--soil.dt-nav__pill "₪" / pill--muted "בקרוב"
│   │   ├── details.dt-acc[data-tier="custom"]
│   │   │   ├── a (custom modules)
│   │   │   └── a.dt-nav__cta href="https://wa.me/972547776770" "+ הציעו כלי חדש"
│   │   └── details.dt-acc.dt-acc--comm[open]    ← Community section
│   │       ├── div.dt-side__stats > div > strong + span    (3 metric tiles)
│   │       ├── div.dt-side__contrib > a.dt-side__crow×4    (contribute rows)
│   │       ├── div.dt-side__feedh "פעילות אחרונה"
│   │       ├── article.feed-item × 3
│   │       ├── a.dt-side__more "כל ההצעות →"
│   │       └── a.dt-side__wa "💬 WhatsApp · ‎צ׳אט פתוח"
│   └── footer.dt-side__foot
│       ├── div.hub-foot__motto "קטן זה יפה"
│       └── div (mono 10px, "SFA · nimrod.bio")
└── main.dt-main
    ├── header.dt-topbar
    │   ├── div > h1.dt-topbar__h + p.dt-topbar__sub
    │   └── div.dt-topbar__tools
    │       ├── a.dt-topbar__contrib "+ תרמו ידע"
    │       └── a.dt-topbar__login "היכנס / הירשם"
    └── div.dt-content                    ← {% block body %}
```

**Active link:** `.is-active` → `background: var(--gj-ink); color: var(--gj-paper)`.
**Accordion state:** persisted via `localStorage.sfaSidebarState`; book accordion `open` by default.

### 1.3 Breakpoint swap — `900px`

Source: `TEMPLATES.md §3`, `IMPLEMENTATION_PLAN.md §3.1`, `DESIGN_TOKENS.md §6`.

`base.html` includes **both** shells; the swap is **pure CSS**:

```css
.sfa-mobile-only  { display: block; }
.sfa-desktop-only { display: none; }
@media (min-width: 900px) {
  .sfa-mobile-only  { display: none; }
  .sfa-desktop-only { display: block; }
}
```

No server-side device detection. Page content is rendered identically inside both shells via
the shared `{% block body %}` — layout deltas are CSS-only. Second breakpoint at **1280px**
upgrades module/market grids to 3-up.

### 1.4 Mark SVG — `<span class="gj-mark">` / sidebar brand

Source: `TEMPLATES.md §4-5`, included as `shell/_mark_svg.html` partial.

- 28–36px square inline SVG of the SFA logomark.
- Used in mobile header (`.gj-mark`, 28×28) and desktop sidebar brand (`.dt-side__brand`, ~36×36).
- No external image dependency. Single shared partial.

---

## 2. Macros (the 10 reusable Jinja2/PHP partials)

Source: `COMPONENTS.md §2-§12`, `TEMPLATES.md §2`, `IMPLEMENTATION_PLAN.md §4`.

### 2.1 `tier_badge(tier, size='sm', override_glyph=None, override_label=None)`

| Input | Type | Notes |
|---|---|---|
| `tier` | `'open' \| 'beta' \| 'coming' \| 'paid' \| 'custom'` | required |
| `size` | `'sm' \| 'lg'` | adds `.tier--lg` modifier |

**Emits:** `<span class="tier tier--{color} [tier--lg]"><span class="tier__glyph">{glyph}</span>{label_he}</span>`

**Mapping (LOCKED):**

| tier | glyph | color modifier | label_he |
|---|---|---|---|
| open | ● | `tier--leaf` | כלים לקהילה |
| beta | β | `tier--sun` | בטא · ניסיוני |
| coming | ⏳ | `tier--paper` | בקרוב |
| paid | ★ | `tier--soil` | כלים מתקדמים |
| custom | ✎ | `tier--tomato` | בדיוק לחווה שלך |

**Required classes:** `tier`, `tier__glyph`, `tier--{color}`, optional `tier--lg`.

### 2.2 `module_card(m)` — hub home grid

Inputs: a module dict (id, name_he, sub, tier, icon, thumb_prompt, stat, color, route).

```html
<a class="mod-card mod-card--{m.color} mod-card--{m.tier}" href="{m.route}" data-tier="{m.tier}">
  <div class="mod-card__art">
    <img src="{m.thumb_url}"> OR <div class="mod-card__placeholder mod-card__placeholder--{color}">
    <div class="mod-card__icon"> {CropIcon kind=m.icon} </div>
  </div>
  <div class="mod-card__body">
    <div class="mod-card__head">
      <h3 class="mod-card__name">{m.name_he}</h3>
      {tier_badge(m.tier)}
    </div>
    <p class="mod-card__sub">{m.sub}</p>
    <p class="mod-card__stat">{m.stat}</p>
  </div>
</a>
```

**Required classes (per mandate §3):** `module-card` (note: mandate uses singular `module-card` —
team_35 source uses `mod-card`; ensure the macro emits **both** or the mandate's required name).
Sub-elements: `module-card__h` (or `mod-card__head`/`__name`), `module-card__sub`, `module-card__stat`, `module-card__icon`.
**Modifier rules:** `data-tier="coming"` → `opacity:.65`; `data-tier="custom"` → warm gradient backdrop.

> **AMBIGUITY** — mandate §3 calls for `module-card` BEM stem; team_35 design CSS uses `mod-card`.
> Build must emit **both** stems (alias) or pick `module-card` to match mandate ACs.

### 2.3 `price_card(p)` — `.pcard` (mobile)

Inputs: product dict (glyph, name, en, unit, big_price, currency, median, range_min, range_max, fill_inset, fill_size, sources_count, observations_count).

DOM regions (3): head (glyph+name/unit) | price (big+cur+median) | range bar + meta.
Required classes: `pcard`, `pcard__head`, `pcard__glyph`, `pcard__name`, `pcard__unit`,
`pcard__price` (children `.big`, `.cur`, `.med`), `pcard__range` (child `.fill`), `pcard__range-text`,
`pcard__meta` (children `.sources > span`).

Desktop counterpart: `.dt-mkt-card` (same regions, different layout). See §1 of this digest for
`.dt-mkt-card__*` BEM family.

### 2.4 `crop_card(c)` — `.gj-cropcard`

Inputs: crop dict (slug, name_he, name_en, tag, dtm).

```
.gj-cropcard (a, href=/book/{slug}/)
├── .gj-cropcard__art > .gj-cropcard__icon (CropIcon)
└── .gj-cropcard__body
    ├── .gj-cropcard__name
    ├── .gj-cropcard__en (italic)
    └── .gj-cropcard__meta
        ├── span.gj-tag (family)
        └── span.gj-cropcard__dtm + <small>ימים</small>
```

### 2.5 `variety_row(v)` — `.cb-var` mobile / `.dt-var` desktop (CB5 expanded — see §7)

Inputs: variety dict (slug, name, is_default, hybrid, dtm, yield, color, shape, taste(1-5), resistance).

```
.cb-var (a)
├── .cb-var__head
│   ├── .cb-var__star "★" (if is_default)
│   ├── h4 {v.name}
│   └── .pill.pill--code "F1 · מורכב" OR .pill.pill--muted "מורשת"
└── .cb-var__grid (6 spans, each: <small>label</small>value)
```

Desktop version uses `.dt-var` + `.dt-var__head` + `.dt-var__rows`.

### 2.6 `contrib_strip(context, placeholder)` — `.contrib-strip`

Source: `COMPONENTS.md §8`, `design/community.css`.

```html
<form class="contrib-strip" action="/api/v1/contribute" method="post">
  <input type="hidden" name="context" value="{context}">
  <div class="contrib-strip__head">
    <span class="contrib-strip__icon">✎</span>
    <div>
      <div class="contrib-strip__h">תורמים נתונים? לא חייבים להירשם.</div>
      <div class="contrib-strip__sub">{module} · {entity}</div>
    </div>
  </div>
  <div class="contrib-strip__input">
    <input type="text" name="text" placeholder="{placeholder}">
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

> **NOTE** — mandate §3 explicitly says `/community` route uses **NO form** per L-GATE_S binding
> (use `.contact-card` + WhatsApp link instead). The contrib-strip macro is for inline use on
> market list / market detail / crop detail per design — **not** on the dedicated community page.

### 2.7 `crosslink(direction, big, sub, href, palette)` — `.gj-crosslink`

Inputs: direction ∈ {`book→market`, `market→book`}, big (price/value), sub (caption), href, palette.

```
.gj-crosslink (a)
├── .gj-crosslink__art (icon/thumb)
├── .gj-crosslink__body
│   ├── .gj-crosslink__big  "12.40 <small>₪/ק״ג</small>"
│   └── .gj-crosslink__sub   "מחיר שוק נוכחי · 6 מקורות · −4% משבוע"
└── .gj-crosslink__cta       "פתח →"
```

Modifier `.gj-crosslink--soil` flips palette to leaf/green for **market → book** direction.

### 2.8 `market_disclaimer(full=false)` — `.mk-disclaimer`

Source: `COMPONENTS.md §10`, `design/crop-book-deep.css`.

**Mandatory at top of every market view.** Copy is **fixed** — do not paraphrase without
team_00 approval.

```
.mk-disclaimer
├── .mk-disclaimer__head
│   ├── .mk-disclaimer__icon "ⓘ"
│   └── h4.mk-disclaimer__h "מה זה? מאיפה זה? למה זה?"
├── ul.mk-disclaimer__list  (4 <li><strong>:</strong>copy</li> bullets — see below)
└── a.mk-disclaimer__cta "קראו עוד על המתודולוגיה →"
```

**The 4 mandatory bullets (verbatim):**

1. **מה:** ממוצעים מתגלגלים של מחירי תוצרת חקלאית טרייה — 7 ימים אחרונים.
2. **מאיפה:** סוכני סריקה ציבוריים של mezoo + תרומות חקלאים. ‎מצרפי, אנונימי.
3. **למה:** כלי שיווקי קהילתי. הוכחה שאפשר ידע פתוח גם בשוק החקלאי הקטן.
4. **לא:** לא הצעה מסחרית, לא קביעת מחיר, לא חוות-דעת. הקשר אינדיקטיבי בלבד.

Desktop `full=true` variant: 2-column, 8 bullets — emphasizes "primarily a community marketing tool."

### 2.9 `feed_item(item)` — `.feed-item`

Source: `COMPONENTS.md §9`, `design/community.css`.

```
article.feed-item
├── .feed-item__kind.feed-item__kind--{kind_color}
│   ├── span (glyph: 💡 / ◐ / ✎)
│   └── small (label_he: "תרומה" / "תיקון" / "הצעה")
└── .feed-item__body
    ├── .feed-item__head > strong (name·region) + .feed-item__date
    ├── p.feed-item__text
    └── .feed-item__meta
        ├── span.pill.pill--muted.feed-item__tag
        └── span.feed-item__upvotes "▲ N"
```

**Kinds → color:** `suggest` → sun (💡) | `correction` → tomato (◐) | `data` → leaf (✎).

### 2.10 `market_disclaimer` is one of two; the 10th macro is `timeline_bar(prep, grow, harv)` — `.gj-timeline` / `.dt-timeline`

Source: `COMPONENTS.md §12`.

```
.gj-timeline (or .dt-timeline)
├── h4
├── .gj-timeline__bar (3 segments, inline style width:%)
│   ├── .gj-timeline__seg.gj-timeline__seg--prep "הכנה"
│   ├── .gj-timeline__seg.gj-timeline__seg--grow "גידול"
│   └── .gj-timeline__seg.gj-timeline__seg--harv "קציר · N ימים"
└── .gj-timeline__ruler > span × N (week markers)
```

Colors: prep = soil/blue-grey | grow = leaf | harv = tomato.

---

## 3. Per-route DOM contract (14 routes)

> Cross-reference: mandate §3 (re-build canonical class list) + COMPONENTS.md (full DOM) +
> TEMPLATES.md §1 (route map / artboards) + `_handoff/design/*.jsx` (visual ground truth).

For each route below: **mandate required classes** (BUILD must emit ≥1 each) + **macros to compose** + COMPONENTS.md anchor.

### 3.1 `/` — Hub home (H1 mobile / D1 desktop)

- **Shell:** `.gj-shell` (mobile) + `.dt-shell` (desktop).
- **Required BEM (mandate §3):** `gj-shell`, `gj-header`, `gj-header__row`, `gj-mark`, `gj-title`, `gj-sub`, `gj-body`, `gj-foot`, `gj-foot__dot`, `module-card`, `module-card__h`, `module-card__sub`, `module-card__stat`, `module-card__icon`, `tier`, `tier--leaf`/`--sun`/`--soil`/`--tomato`/`--paper`, `tier__glyph`.
- **Macros:** `module_card` × 8 (one per module from `MODULES_REGISTRY.yaml`), `tier_badge`.
- **Structure:** hero greeting + 3 tier sections (Open/Paid/Custom) each containing a module grid; community feed strip on desktop sidebar.
- **Page kwargs:** `active='hub'`, `show_module_tabs=false`, `page_title='SFA'`, `page_sub='כלים גדולים לחוות קטנות'`.

### 3.2 `/about` — Tiers explainer (H2/D2)

- **Required BEM (mandate §3):** `gj-shell`, `gj-header`, `gj-body`, `hub-tiers-intro`, `hub-tier-list`, `tier tier--lg`.
- **Macros:** `tier_badge(tier, size='lg')` × 5 tiers.
- **Structure:** `.hub-tiers-intro` intro card + `.hub-tier-list` containing `.hub-tier-row` per tier with `.hub-tier-row__num`, `.hub-tier-row__desc`, `.hub-tier-row__count`.

### 3.3 `/search?q=…` — Global search (D8)

- **Required BEM:** `gj-shell`, `gj-topbar` (mobile) **or** `dt-search` (desktop).
- **Macros:** —
- **Structure:** `.dt-search__bar` + `.dt-search__chips` (filter by section: crops/products/community) + `.dt-search__group` repeated per kind, each with `.dt-search__row`, `.dt-search__name`, `.dt-search__meta`, `.dt-search__icon`, `.dt-search__more`.

### 3.4 `/calc` — Calculator β (H3/D7)

- **Required BEM:** `gj-shell`, `tier tier--sun` (β badge), `gj-crosslink` (the "↗ ספר" cross-link pattern).
- **Macros:** `tier_badge('beta', size='lg')`, `crosslink`.
- **Structure:** form with `.calc-field` (label, input, hint), `.calc-form`, `.calc-result` block. Desktop variant uses `.dt-calc-*` (see `design/desktop-extras.css`): `.dt-calc__form`, `.dt-calc-field`, `.dt-calc-row`, `.dt-calc-unit`, `.dt-calc-help`, `.dt-calc__resultcard`, `.dt-calc__resultbig`, `.dt-calc__sensitivity`.

### 3.5 `/crop-book/` — Book entry (CB0)

- **Required BEM:** `gj-shell` + 4 entry-cards using `module-card` pattern.
- **Macros:** reuse `module_card` shape (or `.cb-path` from `crop-book-deep.css`).
- **Structure:** `.cb-paths` grid with `.cb-path` × 4: `.cb-path--ask`, `.cb-path--family`, `.cb-path--table`, `.cb-path--search`. Each: `.cb-path__icon`, `.cb-path__name`, `.cb-path__sub`, `.cb-path__arrow`.

### 3.6 `/crop-book/questions` — Questions view (CB1)

- **Required BEM:** `gj-shell`, `gj-row__big` (question cards — note: mandate uses `gj-row__big`; design uses `.cb-qcard`).
- **Structure:** `.cb-qgrid` of `.cb-qcard` × 8, each with `.cb-qcard__num`, `.cb-qcard__q`, `.cb-qcard__sub`, `.cb-qcard__count`. `.cb-qhint` at bottom.

### 3.7 `/crop-book/family` — Family tree (CB2)

- **Required BEM:** `gj-shell` + family taxonomy list.
- **Structure:** `.cb-fam-list` of `.cb-fam.cb-fam--{leaf|tomato|soil|sun}` family cards, each with `.cb-fam__head`, `.cb-fam__he`, `.cb-fam__en`, `.cb-fam__count`, `.cb-fam__crops`.

### 3.8 `/crop-book/table` — Pro table (CB3/D3)

- **Required BEM:** `gj-shell` (mobile) + `dt-shell` `dt-table` (desktop); `<th scope="col">` per column.
- **Structure (mobile):** `.cb-table` (vertical stack of `.cb-table__row` with `.cb-table__name`, `.cb-table__fam`, `.cb-table__num`, `.cb-table__num--accent`).
- **Structure (desktop):** real `<table class="dt-table">` with sticky header, sortable columns (`button data-sort="dtm"` etc.). Client-side sort via `sfa.js`.

### 3.9 `/crop-book/search` — Advanced search (CB4)

- **Required BEM:** `gj-shell`, `gj-search`.
- **Structure:** `.cb-search-form` with filter chips (`.cb-chip-row`), `.cb-search-submit`, `.cb-search-tip`. Range inputs use `.cb-range` (`.cb-range__bar`, `.cb-range__fill`, `.cb-range__current`, `.cb-range__labels`).

### 3.10 `/crop-book/{slug}` — Crop detail (CB5/D4)

- **Required BEM (mandate §3):** `gj-shell`, `crop-detail__head`, `crop-detail__h1`, `crop-detail__sci`, `crop-vars__list`, `crop-vars__row` (per variety).
- **Macros:** `variety_row` × N, `crosslink` (market price), `timeline_bar`, `contrib_strip`.
- **Structure (mobile):** `.cb-crop-hero` (`__breadcrumb`, `__h`, `__meta`) + `.cb-deep-tabs` (סקירה/זנים/גידול/מחלות/קציר/שיווק/מקורות) + `.cb-deep-section` per tab content + `.cb-spec-grid` (`<dl><dt><dd>` quick-facts: משפחה/DTM/יבול/עונה/מרווח/חממה).
- **Structure (desktop, from `desktop-extras.jsx::Desktop_CropDetail`):** `.dt-crop` 2-col with `.dt-crop__side` (image, market crosslink, `.dt-crop__quickfacts`) and `.dt-crop__main` (`.dt-crop__head`, `.cb-deep-tabs`, sections, `.dt-vars-grid` of `.dt-var` cards, `.dt-timeline`, contrib strip).
- **Varieties section:** `.cb-vars-head` with `.cb-vars-sort` buttons (ברירת מחדל / טעם / יבול / DTM) → `.dt-vars-grid` (desktop) or `.crop-vars__list` (mobile) → `.cb-var` / `.dt-var` rows → `.cb-vars-more` "+N זנים נוספים" link.

> **NAMING ALIGNMENT** — mandate requires `crop-detail__*` and `crop-vars__*` BEM stems. Design source uses `.cb-crop-hero` + `.cb-var`. Build must emit the **mandate-named** classes (or alias both) to pass the curl-grep ACs in §5.2 of the mandate.

### 3.11 `/crop-book/{slug}/variety/{vslug}` — Variety detail (CB5 expanded)

- **Required BEM:** extends CB5 with `crop-vars__row--expanded` + field grid (`variety-fields` `<dl><dt><dd>`).
- **Macros:** extended `variety_row` with full payload_json rendering — see §7 below.

### 3.12 `/market/` — Market list (MK1/D5)

- **Required BEM:** `gj-shell`, `market-disclaimer` (with all 4 sub-bullets) + `gj-row` per product with `gj-row__big` (price) + `gj-row__sub` (date+source).
- **Macros:** `market_disclaimer(full=false)` (mobile) / `market_disclaimer(full=true)` (desktop), `price_card` per product, `contrib_strip(context='market.list', ...)`.
- **Structure (mobile):** disclaimer block → `.gj-grid` of `.pcard` (or `.gj-row` per mandate spelling). `.gj-row` family: `.gj-row__art`, `.gj-row__name`, `.gj-row__big`, `.gj-row__cur`, `.gj-row__delta`, `.gj-row__bar`, `.gj-row__bar-fill`, `.gj-row__meta`.
- **Structure (desktop):** `.dt-mkt-grid` of `.dt-mkt-card` (3-up at ≥1280px).

### 3.13 `/market/{slug}` — Market detail (MK2/D6)

- **Required BEM:** `gj-shell`, `gj-pricebig`, `gj-pricebig__big`, `gj-pricebig__unit` + price history table.
- **Macros:** `market_disclaimer(full=true)`, `crosslink('market→book')`, `contrib_strip`.
- **Structure (desktop, from `desktop-extras.jsx::Desktop_MarketDetail`):** `.dt-mkdetail` with `.dt-mkdetail__hero` (`.dt-mkdetail__art` (Tomato SVG), `.dt-mkdetail__head` w/ eyebrow + h2 + `.dt-mkdetail__crosslink`), `.dt-mkdetail__bignumber` (`.dt-mkdetail__big`, `.dt-mkdetail__cur`, `.dt-mkdetail__lbl`, `.dt-mkdetail__delta`), full disclaimer, `.dt-mkdetail__stats` with `.dt-statgrid` of `.dt-stat` tiles (חציון/טווח/סטיית-תקן/מקורות/תצפיות/עדכון-אחרון), `.dt-mkdetail__chart` with `.dt-mkdetail__chartfoot`.
- **Stats keys per design:** `חציון`, `טווח`, `סטיית תקן`, `מקורות`, `תצפיות`, `עדכון אחרון`.

### 3.14 `/community` — Community page (H4/D9)

- **Required BEM:** `gj-shell`, `contact-card`, `contact-card__h`, `contact-card__lede`, `contact-card__cta` (WhatsApp link, **NO form** per L-GATE_S binding).
- **Macros:** `feed_item` × N for recent activity.
- **Structure:** `.contact-card` with body + WhatsApp CTA → `https://wa.me/972547776770`. Optionally render `.comm-stats` grid + `.comm-feed` list (read-only). **Do NOT emit `<form>` on this route.**

---

## 4. Design tokens

Source: `DESIGN_TOKENS.md` (canonical) + `design/system.css` (live).

> **Token-namespace drift detected.** Two parallel namespaces coexist:
> - **`--gj-*`** (DESIGN_TOKENS.md canonical) → `--gj-paper`, `--gj-leaf`, `--gj-tomato`, `--gj-sun`, `--gj-soil`, `--gj-ink`, `--gj-line`, etc.
> - **`--w-*` / `--paper` / `--ink`** (live `system.css` v3.3 from Nimrod DS) → `--w-soil`, `--w-know`, `--w-code`, `--paper`, `--paper-2`, `--ink`, `--ink-soft`.
> Per `DESIGN_TOKENS.md` line 4: "Copy verbatim into `tokens.css`. These are the **contract**."
> The CSS in `design/gj.css`, `design/community.css` etc. **uses `--gj-*` tokens**, but `system.css` defines `--w-*`. **Build must declare both** (or alias `--gj-* → --w-*`) in `tokens.css`.

### 4.1 CSS custom properties (canonical — `--gj-*`)

```css
:root {
  /* Paper / ink */
  --gj-paper:    #f6f1e3;  --gj-paper-2:  #ece5d2;  --gj-paper-3:  #ddd2b2;
  --gj-ink:      #2a2418;  --gj-ink-soft: #776a4d;  --gj-line:     #d8ccae;

  /* Worlds */
  --gj-leaf:        #6f8a45;  --gj-leaf-deep:   #4d6a2c;  --gj-leaf-soft: #9bb172;
  --gj-tomato:      #c24f2c;  --gj-tomato-deep: #8e3018;
  --gj-sun:         #d39a32;
  --gj-soil:        #8b5d2f;  --gj-soil-deep:   #5a3c1a;

  /* Status (alias onto worlds) */
  --status-fresh: var(--gj-leaf);  --status-aging: var(--gj-sun);
  --status-stale: var(--gj-tomato); --status-error: #c43a2e;

  /* Typography */
  --gj-font-body: "Assistant", "Heebo", system-ui, sans-serif;
  --gj-font-head: "Frank Ruhl Libre", "David Libre", "Times New Roman", serif;
  --gj-font-mono: "JetBrains Mono", "SF Mono", Menlo, monospace;

  /* Radii */
  --gj-r-s: 8px;  --gj-r-m: 12px;  --gj-r-l: 14px;  --gj-r-xl: 18px;  --gj-r-pill: 99px;

  /* Shadows */
  --gj-shadow-s: 0 1px 3px rgba(40,25,12,.06);
  --gj-shadow-m: 0 4px 14px rgba(80,50,20,.08);
  --gj-shadow-l: 0 8px 28px rgba(80,50,20,.14);

  /* Spacing (4-pt grid) */
  --gj-sp-1: 4px;  --gj-sp-2: 8px;  --gj-sp-3: 12px;  --gj-sp-4: 16px;
  --gj-sp-5: 24px; --gj-sp-6: 32px; --gj-sp-7: 48px;
}
```

### 4.2 Color palette (5 worlds + 1 paper)

| World | Light | Deep | Use |
|---|---|---|---|
| **leaf** | `#6f8a45` | `#4d6a2c` | book module, open community, status-fresh |
| **tomato** | `#c24f2c` | `#8e3018` | market module, status-stale, spark accents |
| **sun** | `#d39a32` | — | beta tier, status-aging, sunshine |
| **soil** | `#8b5d2f` | `#5a3c1a` | paid tier, depth, dark stripes |
| **paper** | `#f6f1e3` (`--gj-paper`) | `#ece5d2` / `#ddd2b2` | bg, recessed surfaces, tracks |

### 4.3 Typography stack

| Family | Weights loaded | Use |
|---|---|---|
| **Frank Ruhl Libre** (serif) | 400/500/700/900 | h1–h4, prices, hero numbers, hand-drawn vibe |
| **Assistant** (sans, Hebrew) | 400/500/600/700/800 | body, UI, captions; fallback `Heebo`, `system-ui` |
| **JetBrains Mono** | 400/500/700 | eyebrows, freshness, version markers, technical |

### 4.4 Type scale

| Token | Mobile | Desktop | Weight | Family | Use |
|---|---|---|---|---|---|
| h1 | 32px | 46px | 900 | head | page hero |
| h1-xl | 44px | 64px | 900 | head | market detail big number |
| h2 | 26px | 32px | 700 | head | section heads |
| h3 | 17–22px | — | 700 | head | sub-heads |
| h4 | 15–17px | — | 700 | head | card titles, KV labels |
| body | 13–15px | — | 400 | body | paragraphs |
| lede | 14–15px | — | 400 (ink-soft) | body | hero blurbs |
| meta | 11–12px | — | 400 | body | captions |
| eyebrow | 10px | — | 700 mono, .12em, UPPER | mono | section labels |
| numeric | 18–60px | — | 700–900, tabular-nums | head | prices/dtm/yield |
| code | 10–11px | — | 400 | mono | freshness, version |

### 4.5 Spacing scale (4-pt grid)

`--gj-sp-1=4px`, `2=8`, `3=12`, `4=16`, `5=24`, `6=32`, `7=48`. Plus `--s-1..--s-8` legacy
from `system.css` v3.3 (16/24/32/48/64/96/128/160).

### 4.6 Breakpoints

```css
@media (min-width: 900px)  { /* desktop shell activates */ }
@media (min-width: 1280px) { /* 3-up module/market grids */ }
```

### 4.7 Z-index map

`0`=background, `1`=content, `5`=floating feedback button + sticky strips, `10`=sticky header, `20`=modal/drawer, `100`=toast.

### 4.8 Hand-drawn underline accent

`.gj-underline` — inline-SVG background-image of a wavy stroke (`#c24f2c`). Use sparingly,
1 per hero. See `DESIGN_TOKENS.md §3`.

---

## 5. CSS file inventory

Source: `IMPLEMENTATION_PLAN.md §3.1`, `TEMPLATES.md §3`, `design/*.css`.

Load order in `base.html` is fixed:

1. `tokens.css` — copied from `design/system.css` (curated). Must declare both `--gj-*` and `--w-*` token sets.
2. `gj.css` — mobile primitives.
3. `hub.css` — hub home + tiers + community CTAs.
4. `community.css` — feedback, contribute, suggest module.
5. `crop-book-deep.css` — book entry, family tree, pro table, search, crop+variety.
6. `desktop.css` — desktop shell.
7. `desktop-extras.css` — desktop crop/market detail, calc, states.

Plus Google Fonts (`Assistant`, `Frank Ruhl Libre`, `JetBrains Mono`).

### 5.1 `tokens.css` (from `design/system.css`)

**Owns:** root custom properties. **Declares roots:** `:root`, base resets (`*`, `html`, `body`), type utilities (`.mono`, `.serif`, `.t-display`, `.t-h1`, `.t-h2`, `.t-h3`, `.t-quote`, `.t-body`, `.t-body-sm`, `.t-ui`), `.grid-6`, `.card`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-spark`, `.under` (legacy underline).

### 5.2 `gj.css`

**Owns:** mobile shell + universal primitives.
**Declares roots:** `.gj-shell`, `.gj-header`, `.gj-header--plain`, `.gj-header__row`, `.gj-header__title`, `.gj-header__wash`, `.gj-mark`, `.gj-iconbtn`, `.gj-tabs` (note: also `.gj-ctabs`), `.gj-tab`, `.gj-body`, `.gj-foot`, `.gj-foot__dot`, `.gj-foot__sep`, `.gj-title`, `.gj-sub`, `.gj-h1`/`__xl`/`__accent`, `.gj-h2`, `.gj-lede`, `.gj-eyebrow`, `.gj-underline`, `.gj-card` (+ `--book`/`--market`), `.gj-cropcard` (+ `__art`/`__body`/`__icon`/`__name`/`__en`/`__meta`/`__dtm`/`__wash`), `.gj-crosslink` (+ `__art`/`__body`/`__big`/`__sub`/`__cta`, `--soil`), `.gj-pricebig` (+ `__big`/`__cur`/`__lbl`/`__med`), `.gj-row` (+ `__art`/`__name`/`__big`/`__cur`/`__delta`/`__bar`/`__bar-fill`/`__meta`/`__sub`), `.gj-grid`, `.gj-list`, `.gj-kv`, `.gj-chip`/`.gj-chips`, `.gj-tag`, `.gj-glance` (+ `__art`/`__big`/`__item`/`__name`/`__sub`), `.gj-article` (+ `__art`/`__head`), `.gj-hero` (+ `--single`/`__art`/`__copy`), `.gj-corner` (+ `--bl`), `.gj-morelink`, `.gj-page-head`, `.gj-privacy`.

### 5.3 `hub.css`

**Owns:** hub home page + module cards + tier UI.
**Declares roots:** `.hub-shell`, `.hub-hero` (+ `__art`/`__copy`), `.hub-h1`, `.hub-lede`, `.hub-bar` (+ `__icon`/`__mark`/`__name`/`__sub`/`__title`), `.hub-section` (+ `__head`/`__lede`/`__title`), `.hub-tiers-intro`, `.hub-tier-list`, `.hub-tier-row` (+ `__count`/`__desc`/`__num`), `.hub-foot` (+ `__dot`/`__motto`/`__row`), `.mod-card` (+ `__art`/`__body`/`__head`/`__icon`/`__name`/`__stat`/`__sub`), `.contact-card` (+ `__art`/`__body`/`__cta`/`__h`/`__lede`), `.calc-field` (+ `__hint`/`__label`/`__value`), `.calc-form`, `.calc-result` (+ `__big`/`__label`/`__sub`), `.calc-feedback`.

### 5.4 `community.css`

**Owns:** community/feedback surfaces.
**Declares roots:** `.comm-section`, `.comm-grid`, `.comm-card` (+ `--leaf`/`--tomato`/`--sun`/`--soil`, `__icon`/`__title`/`__lede`/`__cta`), `.comm-feed` (+ `__head`), `.comm-stats`, `.comm-stat` (+ `__big`/`__sub`), `.comm-cta` (+ `__icon`/`__h`/`__sub`/`__arrow`), `.feed-item` (+ `__kind`/`--leaf`/`--tomato`/`--sun`, `__head`/`__date`/`__text`/`__meta`/`__tag`/`__upvotes`), `.contrib-strip` (+ `__head`/`__icon`/`__h`/`__sub`/`__input`/`__quick`), `.fb-fab` (+ `__icon`) — floating feedback button, `.suggest-mod` (+ `__head`/`__row`/`__hint`).

### 5.5 `crop-book-deep.css`

**Owns:** book entry/family/table/search + crop+variety pages + market disclaimer.
**Declares roots:** `.cb-entry`, `.cb-paths`, `.cb-path` (+ `--ask`/`--family`/`--search`/`--table`, `__arrow`/`__icon`/`__name`/`__sub`), `.cb-qgrid`, `.cb-qcard` (+ `__count`/`__num`/`__q`/`__sub`), `.cb-qhint`, `.cb-fam-list`, `.cb-fam` (+ `--leaf`/`--soil`/`--sun`/`--tomato`, `__count`/`__crops`/`__en`/`__he`/`__head`), `.cb-table` (+ `__fam`/`__head`/`__name`/`__num`/`--accent`/`__row`), `.cb-trend`, `.cb-trending`, `.cb-search-form`, `.cb-search-submit`, `.cb-search-tip`, `.cb-chip-row`, `.cb-range` (+ `__bar`/`__current`/`__fill`/`__labels`), `.cb-section-h`, `.cb-crop-hero` (+ `__breadcrumb`/`__h`/`__meta`), `.cb-deep-section`, `.cb-deep-tabs`, `.cb-spec-grid`, `.cb-vars-head`, `.cb-vars-more`, `.cb-vars-sort`, `.cb-var` (+ `__grid`/`__head`/`__star`), `.mk-disclaimer` (+ `__cta`/`__h`/`__head`/`__icon`/`__list`).

### 5.6 `desktop.css`

**Owns:** desktop shell (sidebar accordion + main + topbar).
**Declares roots:** `.dt-shell`, `.dt-side` (+ `__brand`/`__contrib`/`__crow`/`__feedh`/`__foot`/`__more`/`__name`/`__search`/`__stats`/`__tag`/`__wa`), `.dt-nav` (+ `__count`/`__cta`/`__pill`), `.dt-acc` (+ `--comm`/`__chev`), `.dt-main`, `.dt-content`, `.dt-topbar` (+ `__h`/`__sub`/`__tools`/`__contrib`/`__login`), `.dt-section` (+ `__head`), `.dt-filters` (+ `__results`/`__search`), `.dt-hub-hero` (+ `__ctas`/`__h`/`__lede`), `.dt-modgrid`, `.dt-mkt-grid`, `.dt-mkt-card` (+ `__art`/`__body`/`__big`/`__cur`/`__delta`/`__meta`/`__price`/`__range`/`__bar`/`__bar-fill`), `.dt-rail` (+ `__h`/`__more`/`__stats`/`__wa`), `.dt-path-tabs`, `.dt-path-tab`, `.dt-btn` (+ `--ghost`/`--primary`).

### 5.7 `desktop-extras.css`

**Owns:** desktop crop detail, market detail, calculator, search, community, state cards.
**Declares roots:** `.dt-crop` (+ `__art`/`__head`/`__main`/`__quickfacts`/`__sci`/`__side`), `.dt-vars-grid`, `.dt-var` (+ `__head`/`__rows`), `.dt-timeline` (+ `__bar`/`__ruler`/`__seg`/`--grow`/`--harv`/`--prep`), `.dt-mkdetail` (+ `__art`/`__big`/`__bignumber`/`__chart`/`__chartfoot`/`__crosslink`/`__cur`/`__delta`/`__head`/`__hero`/`__lbl`/`__stats`), `.dt-stat` (+ `__big`/`__lbl`/`__sub`), `.dt-statgrid`, `.dt-tier-grid`, `.dt-tier-card` (+ `--soil`/`--sun`/`--tomato`/`__count`/`__mod`/`__mods`/`__num`), `.dt-tiers-intro`, `.dt-calc` (+ `__form`/`__h`/`__feedback`/`__resultcard`/`--big`/`__resultbig`/`__resultlbl`/`__results`/`__resultsub`/`__sensitivity`), `.dt-calc-field`/`-help`/`-readonly`/`--soft`/`-row`/`-unit`, `.dt-search` (+ `__bar`/`__chips`/`__group`/`__icon`/`__meta`/`__more`/`__name`/`__row`), `.dt-skeleton`, `.dt-states-grid`, `.dt-statecard` (+ `__body`/`__head`).

---

## 6. Crop icon sprite

Source: `design/illustrations.jsx`, `MODULES_REGISTRY.yaml` (icon field), `IMPLEMENTATION_PLAN.md §8.2`.

### 6.1 How `CROP_ICON` produces icons

`illustrations.jsx` defines 8 named React components (each a self-contained `<svg viewBox="0 0 60 60">`):

```js
const CROP_ICON = {
  tomato: Tomato, lettuce: Lettuce, cucumber: Cucumber, carrot: Carrot,
  pepper: Pepper, onion: Onion, basil: Basil, strawberry: Strawberry,
};
```

Each component uses **shared `<defs>` gradients** declared once via `<WatercolorDefs />` at app
root: `#wc-tomato`, `#wc-leaf`, `#wc-leaf-soft`, `#wc-carrot`, `#wc-pepper`, `#wc-onion`,
`#wc-sun`, `#wc-soil`, plus `#wc-bleed` (white-to-black bleed for highlight) and an `#wc-blur`
filter used **only on hero washes** (not on icons — performance).

### 6.2 Extraction to `icons.svg`

For the WP/PHP build, extract these into a single static sprite file:

```html
<!-- /static/icons.svg (or /wp-content/themes/.../icons.svg) -->
<svg xmlns="http://www.w3.org/2000/svg" style="display:none">
  <defs>
    <radialGradient id="wc-tomato" cx="40%" cy="35%" r="65%">…</radialGradient>
    <radialGradient id="wc-leaf"   cx="40%" cy="35%" r="65%">…</radialGradient>
    <radialGradient id="wc-leaf-soft" …/>
    <radialGradient id="wc-carrot" …/>
    <radialGradient id="wc-pepper" …/>
    <radialGradient id="wc-onion"  …/>
    <radialGradient id="wc-sun"    …/>
    <radialGradient id="wc-soil"   …/>
    <radialGradient id="wc-bleed"  …/>
    <filter id="wc-blur"><feGaussianBlur stdDeviation="1.2"/></filter>
  </defs>
  <symbol id="icon-tomato"     viewBox="0 0 60 60">…paths from Tomato()…</symbol>
  <symbol id="icon-lettuce"    viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-cucumber"   viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-carrot"     viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-pepper"     viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-onion"      viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-basil"      viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-strawberry" viewBox="0 0 60 60">…</symbol>
</svg>
```

Usage in templates:

```html
<svg width="48" height="48" aria-hidden="true">
  <use href="/static/icons.svg#icon-{kind}"/>
</svg>
```

The 8 source paths are in `design/illustrations.jsx` lines ~80–225 — copy them verbatim.

### 6.3 Slug → icon mapping (from MODULES_REGISTRY.yaml)

The registry maps **modules** to icons; **crops** map via slug → kind. Module mapping:

| Module slug | Icon kind |
|---|---|
| crop-book | lettuce |
| market | tomato |
| calc | carrot |
| planner | basil |
| clients | cucumber |
| inventory | strawberry |
| tend-bridge | pepper |
| field-log | onion |

For per-crop mapping in the crop book, `IMPLEMENTATION_PLAN.md §2.2` references
`helpers.vegetable_icon_id(crop_slug)` — but **the actual slug-to-icon table is NOT defined
in the LOD300 package**. Only 8 icons exist; the design implies a fallback to `lettuce` (per
`illustrations.jsx::CropIcon` default) for crops without a dedicated symbol.

> **AMBIGUITY** — see §8.

---

## 7. Variety-row expanded contract (CB5 / `/crop-book/{slug}/variety/{vslug}`)

Source: `COMPONENTS.md §7`, `desktop-extras.jsx::VarietyCardDesktop` (lines 113–131), mandate §3 (row 11), `IMPLEMENTATION_PLAN.md §6` (book_variety).

### 7.1 Collapsed (per-variety inside CB5 list)

```html
<a class="cb-var" href="/crop-book/{slug}/variety/{vslug}/">
  <div class="cb-var__head">
    <span class="cb-var__star">★</span>           {# if is_default #}
    <h4>{name}</h4>
    <span class="pill pill--code">F1 · מורכב</span>  {# if hybrid #}
    <span class="pill pill--muted">מורשת</span>      {# if not hybrid #}
  </div>
  <div class="cb-var__grid">
    <span><small>DTM</small>{dtm}</span>
    <span><small>יבול</small>{yield} ק״ג/מ״ר</span>
    <span><small>צבע</small>{color}</span>
    <span><small>צורה</small>{shape}</span>
    <span><small>טעם</small>{'★'.repeat(taste)}</span>
    <span><small>עמידות</small>{resistance}</span>
  </div>
</a>
```

### 7.2 Expanded variant — `.crop-vars__row--expanded` (mandate-named) / `.variety-fields`

For the dedicated variety route, the row expands to a full field grid using `<dl><dt><dd>`.
Per mandate §3 row 11: `crop-vars__row--expanded` modifier + `variety-fields` container with
`<dl><dt><dd>` triplets.

**Standard `<dt>` labels (Hebrew) — from `Desktop_CropDetail.dt-crop__quickfacts`** (`desktop-extras.jsx`):

| `<dt>` label | Maps to payload_json key | Example `<dd>` |
|---|---|---|
| משפחה | `family` (Hebrew family name) | סולנציאות |
| DTM | `dtm` or `dtm_range` | 60–78 ימים |
| יבול | `yield` or `yield_range` | 5.5–11.4 ק״ג/מ״ר |
| עונה | `season` | אביב · קיץ |
| מרווח | `spacing` | 50×50 ס״מ |
| חממה | `greenhouse` | מומלץ |
| טעם | `taste` (1–5 stars) | ★★★★ |
| צבע | `color` | אדום |
| צורה | `shape` | אשכולי |
| עמידות | `resistance` (disease codes) | TYLCV |

(Convention: `<dt>` is the short Hebrew label; `<dd>` contains the value + unit. Use
`font-variant-numeric: tabular-nums` for all numeric `<dd>`.)

### 7.3 Unknown-field fallback hook (mandate AC-DB-1)

The mandate's AC-DB-1 requires: *"Templates render correctly when `payload_json` contains 1+
fields NOT in the template's known-label dictionary. Page renders 200, the unknown field
appears in a 'more info' fallback section (not a PHP warning, not silent drop)."*

**LOD300 does NOT specify the fallback DOM.** Design implies but does not pin:
- A trailing block (e.g. `<section class="variety-fields__extras">` or
  `<dl class="variety-fields variety-fields--unknown">`) listing each unknown key/value pair
  as raw `<dt>{snake_case_key}</dt><dd>{value}</dd>` (untranslated).
- Suggested label format: `<dt class="variety-fields__unknown-key">{key}</dt>`.

The build must invent this hook — the canon design has no source mockup for it.

> **AMBIGUITY** — see §8.

---

## 8. Open ambiguities (call-outs for team_100 BUILD)

These are gaps in LOD300 that the build must resolve. Don't guess silently — decide and document.

### 8.1 BEM-stem drift: `module-card` (mandate) vs `mod-card` (design CSS)

- Mandate §3 requires `module-card`, `module-card__h`, `module-card__sub`, `module-card__stat`, `module-card__icon`.
- Design `hub.css` declares `.mod-card`, `.mod-card__head`/`__name`/`__sub`/`__stat`/`__icon`/`__body`/`__art`.
- **Decision needed:** emit `module-card` per mandate (rewrite CSS), **OR** dual-class
  (`class="mod-card module-card"`) for back-compat with design CSS while satisfying ACs.

### 8.2 BEM-stem drift: `crop-detail__*` / `crop-vars__*` (mandate) vs `cb-crop-hero` / `cb-var` (design)

- Mandate §3 row 10 requires `crop-detail__head`, `crop-detail__h1`, `crop-detail__sci`, `crop-vars__list`, `crop-vars__row`.
- Design uses `.cb-crop-hero`, `.cb-crop-hero__h`, `.cb-crop-hero__breadcrumb`, `.cb-var`.
- Same decision: rename in CSS, or dual-class.

### 8.3 Token namespace: `--gj-*` (DESIGN_TOKENS.md) vs `--w-*` + `--paper`/`--ink` (system.css v3.3)

- Design CSS files reference `--gj-*` throughout (`gj.css`, `community.css`, etc.)
- `design/system.css` defines `--w-*`, `--paper`, `--paper-2`, `--ink`, `--ink-soft`.
- DESIGN_TOKENS.md is the contract → declare `--gj-*` in `tokens.css`. Keep `--w-*` aliases for
  back-compat with anything that pulls in system.css.

### 8.4 Crop-slug → SVG-icon mapping table missing

- Only 8 icons exist (`tomato`, `lettuce`, `cucumber`, `carrot`, `pepper`, `onion`, `basil`, `strawberry`).
- DB has 66+ crops. LOD300 has **no explicit table** for which icon each crop gets.
- Default in `illustrations.jsx::CropIcon` is `Lettuce` for any unknown kind.
- **Decision needed:** lock a mapping table (e.g. tomato/cherry-tomato → tomato; chard/spinach/kale → lettuce; etc.) or rely on a `crop.icon_slug` DB field (does it exist?).

### 8.5 Unknown-field fallback DOM (mandate AC-DB-1)

- Mandate requires graceful render of unknown `payload_json` keys.
- LOD300 has **no mockup** for this.
- **Decision needed:** invent a fallback container — recommended:
  `<section class="variety-fields__extras"><dl>...</dl></section>` rendered after the known fields.

### 8.6 `gj-row__big` (mandate) vs `cb-qcard` (design) for question cards

- Mandate §3 row 6 (`/crop-book/questions`) requires `gj-row__big`.
- Design uses `.cb-qcard` (with `__num`, `__q`, `__sub`, `__count`).
- Same dual-class question.

### 8.7 `module-card` in book entry vs `cb-path` in design

- Mandate §3 row 5 (`/crop-book/`) says "4 entry-cards with `module-card` pattern".
- Design `crop-book-deep.css` uses `.cb-path` for the 4 entry cards.
- Likely dual-class is the right call.

### 8.8 Mark SVG content not in package

- `shell/_mark_svg.html` is referenced but the actual SFA logomark SVG source is not in
  the design folder. Build must source it from existing `_aos/` brand assets or the
  current production site, or create a new minimal mark.

### 8.9 Community page `<form>` vs design's `.contrib-strip`

- Design `community.jsx` likely includes a contribute form on the community page (the
  `.contrib-strip` macro pattern).
- Mandate §3 row 14 explicitly says **NO form** on `/community` per L-GATE_S binding —
  use `.contact-card` + WhatsApp link only.
- **Binding wins:** community page = contact-card only. `.contrib-strip` lives on market/crop pages.

### 8.10 Stack discrepancy: Flask Blueprint (LOD300) vs PHP/WordPress (re-build mandate)

- LOD300 §2 specifies a Flask Blueprint at `sfa.nimrod.bio` (`organic_market_agent/sfa_app/`).
- Re-build mandate operates on PHP templates (`_layout.php`, `shell/mobile.php`, etc.) and
  deploys via lftp/FTPS.
- The **design contract is stack-neutral** (BEM/DOM/tokens). Build follows PHP per mandate;
  use this digest as the BEM source-of-truth and IGNORE the Jinja2 / Flask wording in LOD300.

### 8.11 Sidebar stats numbers (corrections / suggestions / members)

- Desktop sidebar `.dt-side__stats` shows `{stats.corrections}`, `{stats.suggestions}`, `{stats.members}`.
- LOD300 does not specify the data source. Build can hardcode placeholders (e.g. `247 / 89 / 1200`)
  per the design mockup, or wire to DB if `community_contributions` is queryable.

### 8.12 Module thumb images (`thumb_url`) — placeholders vs real images

- `module_card` expects `m.thumb_url`; falls back to `.mod-card__placeholder--{color}` div.
- LOD300 has AI-image prompts in `MODULES_REGISTRY.yaml::ai_prompts` but no rendered images shipped.
- Build can ship with placeholders only; AI-image render is a separate phase.

---

## 9. Quick lookup tables

### 9.1 Module registry (8 modules, from MODULES_REGISTRY.yaml)

| id | name_he | tier | icon | color | route |
|---|---|---|---|---|---|
| crop-book | ספר גידולים | open | lettuce | leaf | /book/ |
| market | מחירון | open | tomato | tomato | /market/ |
| calc | מחשבון לחקלאי | beta | carrot | sun | /calc/ |
| planner | תכנון עונה | coming | basil | leaf | /planner/ |
| clients | ניהול לקוחות | paid | cucumber | soil | /clients/ |
| inventory | מעקב יבול ומלאי | paid | strawberry | tomato | /inventory/ |
| tend-bridge | חיבור Tend | custom | pepper | soil | /integrations/tend/ |
| field-log | יומן שדה | custom | onion | leaf | /field-log/ |

### 9.2 Tier colors (locked)

| tier | label_he | glyph | color | desc summary |
|---|---|---|---|---|
| open | כלים לקהילה | ● | leaf | public service, no signup |
| beta | בטא · ניסיוני | β | sun | active dev, feedback welcome |
| coming | בקרוב | ⏳ | paper | working on it |
| paid | כלים מתקדמים | ★ | soil | paid track |
| custom | בדיוק לחווה שלך | ✎ | tomato | bespoke build |

### 9.3 Pill tones (`.pill.pill--{tone}`)

`soil`, `know` (→ tomato), `code` (→ sun), `muted`, `warn`, `spark`.

### 9.4 Contact (from `MODULES_REGISTRY.yaml::contact`)

- WhatsApp: `+972547776770` / `054-7776770` — link: `https://wa.me/972547776770`.
- Email: not set in design.

### 9.5 Mandatory cross-references (mandate §3 + COMPONENTS.md)

| Route | COMPONENTS.md anchor | Mandate row |
|---|---|---|
| `/` | §3 ModuleThumb, §2 Tier | row 1 |
| `/about` | §2 Tier (size=lg) | row 2 |
| `/search` | §17 Tabs | row 3 |
| `/calc` | §11 Calculator | row 4 |
| `/crop-book/` | §3 (variant for 4 paths) | row 5 |
| `/crop-book/questions` | §1.1 shell + custom cards | row 6 |
| `/crop-book/family` | §16 Pills + custom | row 7 |
| `/crop-book/table` | §17 Tabs + table | row 8 |
| `/crop-book/search` | §16 Pills + form | row 9 |
| `/crop-book/{slug}` | §4 CrossLink, §7 Variety, §12 Timeline, §8 ContribStrip | row 10 |
| `/crop-book/{slug}/variety/{vslug}` | §7 Variety expanded | row 11 |
| `/market/` | §10 Disclaimer, §5 PriceCard, §8 ContribStrip | row 12 |
| `/market/{slug}` | §10 Disclaimer (full), §4 CrossLink, §12 Timeline, §8 ContribStrip | row 13 |
| `/community` | §9 FeedItem, contact-card only (no form) | row 14 |

---

*End of digest — RESEARCH_team35_design_digest_2026-05-27_v1.0.0*
