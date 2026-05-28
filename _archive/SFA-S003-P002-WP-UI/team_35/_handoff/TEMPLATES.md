# Page Templates — Jinja2 contract & routing

> This document defines every page in the SFA standalone Flask application.

---

## 1. Route map

| Route | Page | Mobile artboard | Desktop artboard | Blueprint |
|-------|------|-----------------|------------------|-----------|
| `/`                  | Hub home          | H1            | D1  | hub.home  |
| `/about/`            | Tiers explainer   | H2            | D2  | hub.tiers |
| `/book/`             | Book entry        | CB0           | (n/a) | book.entry |
| `/book/questions/`   | Questions view    | CB1           | (n/a) | book.questions |
| `/book/family/`      | Family tree       | CB2           | (n/a) | book.family |
| `/book/table/`       | Pro table         | CB3           | D3  | book.table |
| `/book/search/`      | Advanced search   | CB4           | (uses topbar) | book.adv_search |
| `/book/<slug>/`      | Crop detail       | CB5           | D4  | book.crop |
| `/book/<slug>/variety/<vslug>/` | Variety detail | (extends CB5) | (extends D4) | book.variety |
| `/market/`           | Market list       | MK1           | D5  | market.list |
| `/market/<slug>/`    | Market detail     | MK2           | D6  | market.product |
| `/calc/`             | Calculator (β)    | H3            | D7  | calc.home |
| `/search/?q=…`       | Global search     | (topbar entry) | D8 | hub.search |
| `/community/`        | Community page    | H4            | D9  | community.page |

### REST endpoints (JSON, no template)

| Method | Path | Returns |
|--------|------|---------|
| GET    | `/api/v1/modules`                        | Module registry |
| GET    | `/api/v1/search?q=…`                     | Cross-module search results |
| GET    | `/api/v1/market/<slug>/history?days=28`  | Trend chart data |
| GET    | `/api/v1/community/feed?limit=10`        | Recent contributions |
| POST   | `/api/v1/contribute`                     | Submit a contribution |

---

## 2. Template architecture

```
sfa_app/templates/
├── base.html                  Full HTML doc. Includes both shells.
├── shell/
│   ├── mobile.html            .gj-shell — visible <900px
│   ├── desktop.html           .dt-shell — visible ≥900px
│   └── _mark_svg.html         SFA logomark
├── macros/                    Reusable Jinja2 macros (see COMPONENTS.md)
│   ├── tier_badge.html
│   ├── module_card.html
│   ├── price_card.html
│   ├── crop_card.html
│   ├── variety_row.html
│   ├── contrib_strip.html
│   ├── crosslink.html
│   ├── market_disclaimer.html
│   ├── feed_item.html
│   ├── timeline_bar.html
│   └── _icon_<name>.html      8 vegetable icons (alt: SVG sprite use)
└── pages/                     One per route
    ├── hub_home.html
    ├── hub_tiers.html
    ├── hub_calc.html
    ├── book_entry.html
    ├── book_questions.html
    ├── book_family.html
    ├── book_table.html
    ├── book_search.html
    ├── book_crop.html
    ├── book_variety.html
    ├── market_list.html
    ├── market_product.html
    ├── community.html
    └── search_results.html
```

---

## 3. `base.html` contract

```jinja
<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ page_title|default('SFA') }}{% endblock %}</title>
  <meta name="description" content="{{ page_description|default('כלים גדולים לחוות קטנות') }}">

  {# OG tags #}
  <meta property="og:title" content="{{ page_title }}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{{ og_image_url|default(url_for('static', filename='img/og-default.webp', _external=True)) }}">
  <link rel="canonical" href="https://sfa.nimrod.bio{{ request.path }}">

  <link rel="stylesheet" href="{{ url_for('static', filename='tokens.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='gj.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='hub.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='community.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='crop-book-deep.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='desktop.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='desktop-extras.css') }}">
  <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;600;700;800&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

  <style>
    .sfa-mobile-only  { display: block; }
    .sfa-desktop-only { display: none; }
    @media (min-width: 900px) {
      .sfa-mobile-only  { display: none; }
      .sfa-desktop-only { display: block; }
    }
  </style>
</head>
<body class="sfa-app">
  <div class="sfa-mobile-only">{% include 'shell/mobile.html' %}</div>
  <div class="sfa-desktop-only">{% include 'shell/desktop.html' %}</div>
  <script src="{{ url_for('static', filename='sfa.js') }}" defer></script>
</body>
</html>
```

---

## 4. `shell/mobile.html` contract

```jinja
<div class="gj-shell">
  <header class="gj-header gj-header--plain">
    <div class="gj-header__row">
      {% if back_url %}
        <a class="gj-iconbtn" href="{{ back_url }}" aria-label="חזרה">←</a>
      {% endif %}
      <span class="gj-mark">{% include 'shell/_mark_svg.html' %}</span>
      <div class="gj-header__title">
        <div class="gj-title">{{ page_title|default('SFA') }}</div>
        <div class="gj-sub">{{ page_sub|default('') }}</div>
      </div>
      <a href="{{ url_for('hub.search') }}" class="gj-iconbtn" aria-label="חיפוש">⌕</a>
    </div>

    {% if show_module_tabs %}
      <nav class="gj-tabs">
        <a href="{{ url_for('market.list') }}"
           class="gj-tab {% if active=='market' %}is-active{% endif %}">מחירון</a>
        <a href="{{ url_for('book.entry') }}"
           class="gj-tab {% if active=='book' %}is-active{% endif %}">ספר גידולים</a>
      </nav>
    {% endif %}
  </header>

  <main class="gj-body">
    {% block body %}{% endblock %}
  </main>

  <footer class="gj-foot">
    <span class="gj-foot__dot" style="background: var(--status-{{ freshness.state }});"></span>
    <span>{{ freshness.label_he }}</span>
    {% if freshness.sources %}
      <span style="opacity:.4">·</span>
      <span>{{ freshness.sources }}</span>
    {% endif %}
    <span style="margin-inline-start:auto; opacity:.6">SFA</span>
  </footer>
</div>
```

---

## 5. `shell/desktop.html` contract

```jinja
<div class="dt-shell">
  <aside class="dt-side">
    <div class="dt-side__brand">
      {% include 'shell/_mark_svg.html' %}
      <div>
        <div class="dt-side__name">SFA</div>
        <div class="dt-side__tag">חקלאות קטנה</div>
      </div>
    </div>

    <form action="{{ url_for('hub.search') }}" method="get">
      <input class="dt-side__search" type="search" name="q" placeholder="חיפוש בכל המערכת…">
    </form>

    <nav class="dt-nav" data-stateful-accordion>
      {# Tier 1 — open #}
      <details class="dt-acc" data-tier="open" open>
        <summary>
          {{ tier_badge('open') }}
          <span class="dt-acc__chev">▾</span>
        </summary>
        <a href="{{ url_for('hub.home') }}" class="{% if active=='hub' %}is-active{% endif %}">דף הבית</a>
        {% for m in sfa_modules if m.tier == 'open' %}
          <a href="{{ m.route }}" class="{% if active==m.id %}is-active{% endif %}">
            {{ m.name_he }}
            {% if m.stat_count %}<span class="dt-nav__count">{{ m.stat_count }}</span>{% endif %}
          </a>
        {% endfor %}
        {% for m in sfa_modules if m.tier == 'beta' %}
          <a href="{{ m.route }}">{{ m.name_he }} <span class="pill pill--code dt-nav__pill">β</span></a>
        {% endfor %}
      </details>

      {# Tier 3 — paid #}
      <details class="dt-acc" data-tier="paid">
        <summary>
          {{ tier_badge('paid') }}
          <span class="dt-acc__chev">▾</span>
        </summary>
        {% for m in sfa_modules if m.tier == 'paid' %}
          <a href="{{ m.route }}">{{ m.name_he }} <span class="pill pill--soil dt-nav__pill">₪</span></a>
        {% endfor %}
        {% for m in sfa_modules if m.tier == 'coming' %}
          <a href="{{ m.route }}">{{ m.name_he }} <span class="pill pill--muted dt-nav__pill">בקרוב</span></a>
        {% endfor %}
      </details>

      {# Tier 2 — custom #}
      <details class="dt-acc" data-tier="custom">
        <summary>
          {{ tier_badge('custom') }}
          <span class="dt-acc__chev">▾</span>
        </summary>
        {% for m in sfa_modules if m.tier == 'custom' %}
          <a href="{{ m.route }}">{{ m.name_he }}</a>
        {% endfor %}
        <a class="dt-nav__cta" href="https://wa.me/972547776770" target="_blank">+ הציעו כלי חדש</a>
      </details>

      {# Community #}
      <details class="dt-acc dt-acc--comm" open>
        <summary>
          {{ tier_badge('beta', sun_glyph='✺', override_label='קהילה') }}
          <span class="dt-acc__chev">▾</span>
        </summary>
        <div class="dt-side__stats">
          <div><strong>{{ stats.corrections }}</strong><span>תיקונים</span></div>
          <div><strong>{{ stats.suggestions }}</strong><span>הצעות</span></div>
          <div><strong>{{ stats.members }}</strong><span>חברים</span></div>
        </div>
        <div class="dt-side__contrib">
          <a href="#contribute" class="dt-side__crow">✎ תרמו ידע</a>
          <a href="#contribute" class="dt-side__crow">◐ דווחו על שגיאה</a>
          <a href="#contribute" class="dt-side__crow">💡 הציעו פיצ׳ר</a>
          <a href="#contribute" class="dt-side__crow">✦ הציעו מודול</a>
        </div>
        <div class="dt-side__feedh">פעילות אחרונה</div>
        {% for item in recent_feed[:3] %}
          {{ feed_item(item) }}
        {% endfor %}
        <a href="{{ url_for('community.page') }}" class="dt-side__more">כל ההצעות →</a>
        <a href="https://wa.me/972547776770" class="dt-side__wa" target="_blank">💬 WhatsApp · ‎צ׳אט פתוח</a>
      </details>
    </nav>

    <footer class="dt-side__foot">
      <div class="hub-foot__motto">קטן זה יפה</div>
      <div style="font-size:10px; color:var(--gj-ink-soft); font-family:'JetBrains Mono',monospace;">SFA · nimrod.bio</div>
    </footer>
  </aside>

  <main class="dt-main">
    <header class="dt-topbar">
      <div>
        <h1 class="dt-topbar__h">{{ page_title|default('SFA') }}</h1>
        {% if page_sub %}<p class="dt-topbar__sub">{{ page_sub }}</p>{% endif %}
      </div>
      <div class="dt-topbar__tools">
        <a href="#contribute" class="dt-topbar__contrib">+ תרמו ידע</a>
        <a href="#login" class="dt-topbar__login">היכנס / הירשם</a>
      </div>
    </header>
    <div class="dt-content">
      {% block body %}{% endblock %}
    </div>
  </main>
</div>
```

---

## 6. Page render-context variables

Every page sets (via `render_template` kwargs or `g`):

| Variable | Type | Purpose |
|----------|------|---------|
| `page_title` | str | shown in header + `<title>` |
| `page_sub` | str | small subtitle under page_title |
| `page_description` | str | for `<meta description>` |
| `active` | str | `'hub' \| 'book' \| 'market' \| 'calc' \| 'community' \| 'about'` — drives nav highlight |
| `show_module_tabs` | bool | true on `/`, false on detail pages |
| `back_url` | str \| None | shows ← icon when set |
| `og_image_url` | str \| None | per-page OG image override |
| `freshness` | dict | `{state, label_he, sources}` — drives footer dot color |
| `stats` | dict | `{corrections, suggestions, members}` — community stats |
| `recent_feed` | list | most-recent community contributions |

Provided via Flask `@app.context_processor` for the constants (`sfa_modules`, `sfa_tiers`) and per-route for the dynamic ones.

---

## 7. Per-page block structure

Every `pages/*.html`:

```jinja
{% extends 'base.html' %}
{% from 'macros/tier_badge.html'        import tier_badge %}
{% from 'macros/module_card.html'       import module_card %}
{% from 'macros/contrib_strip.html'     import contrib_strip %}
{% from 'macros/market_disclaimer.html' import market_disclaimer %}
{# ... etc ... #}

{% block title %}{{ page_title }} — SFA{% endblock %}

{% block body %}
  {# Page-specific content — uses macros for repeated UI #}
  ...
{% endblock %}
```

The `{% block body %}` is rendered **inside both** the mobile and desktop shells (since `base.html` includes both via media-query toggle). Layout differences between mobile/desktop are pure CSS — no `{% if mobile %}` conditionals in the template.

---

## 8. Special behaviors

### 8.1 Accordion state persistence (desktop sidebar)

`sfa.js` reads `localStorage.sfaSidebarState`, applies `open` attribute to each `<details data-tier="…">` before paint. Writes back on `toggle` event.

### 8.2 Contribute strip submit

`<form>` POSTs to `/api/v1/contribute`. `sfa.js` upgrades it to an `async fetch` with inline success/error feedback (no full-page reload). Honeypot field `<input name="website" hidden>` to filter bots.

### 8.3 Pro table sort

`<button data-sort="dtm">` on each column header. `sfa.js` re-orders the `<tr>` rows client-side (no server roundtrip).

### 8.4 Calculator (β)

All inputs trigger live recompute via `sfa.js`. The yield + price defaults are pulled from `data-default` attributes server-rendered by Flask (no API call for defaults).

### 8.5 Cross-link "↗ ספר" / "↗ מחירון"

Server-rendered `<a href>` to the matching crop/product page, based on `pricebook_product_id ↔ crop_id` join already in the DB.

---

## 9. Accessibility

- `<html lang="he" dir="rtl">` required
- All icons have `aria-label` or `aria-hidden="true"`
- Form fields have `<legend>` or `<label>`
- All interactive elements get `:focus-visible` styles
- Color contrast verified WCAG AA on `--gj-paper` background
- Hebrew fonts use `font-variant-numeric: tabular-nums` for prices/DTM
