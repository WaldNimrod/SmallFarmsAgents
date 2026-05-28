# Implementation Plan — SFA Standalone Flask App

> **Target executor:** Claude Code (builder agent) or human dev.
> **Inputs:** this folder + LOD400 spec (to be authored by team_110).
> **Output:** standalone Flask app at `sfa.nimrod.bio`, port 5002.
> **Estimated effort:** 16–20h for WP-B1 (shell + hub + book + market). Calculator + community admin UI are separate work packages (B2, B3).

---

## Phase 0 — Pre-build: confirm 9 open questions

From `HANDOFF_LOD300.md §6`. **Block the build until team_00 advisory closes Q1, Q5, Q7, Q9** (strategic). Q2–Q4, Q6, Q8 — engineering judgment OK.

---

## Phase 1 — Flask app skeleton (2h)

### 1.1 Create the package

```
organic_market_agent/sfa_app/
├── __init__.py
├── routes/
├── templates/
├── static/
├── modules.py
├── helpers.py
└── contribute.py
```

### 1.2 App factory

```python
# organic_market_agent/sfa_app/__init__.py
from flask import Flask
from organic_market_agent.db.session import session_scope

def create_sfa_app() -> Flask:
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
        static_url_path='/static',
    )
    app.config['JSON_AS_ASCII'] = False   # Hebrew in JSON responses

    # No login_manager. No auth. Public.
    # Use a separate read-only DB user (sfa_public).

    from .routes import hub, book, market, calc, community
    app.register_blueprint(hub.bp)
    app.register_blueprint(book.bp, url_prefix='/book')
    app.register_blueprint(market.bp, url_prefix='/market')
    app.register_blueprint(calc.bp, url_prefix='/calc')
    app.register_blueprint(community.bp)  # /community/ + /api/v1/*

    @app.context_processor
    def inject_globals():
        from . import modules, helpers
        return {
            'sfa_modules': modules.SFA_MODULES,
            'sfa_tiers': modules.TIERS,
            'sfa_current_route': None,  # routes override per-request
            'freshness': helpers.get_freshness(),
        }

    return app
```

### 1.3 Gunicorn entrypoint

```python
# organic_market_agent/sfa_app/wsgi.py
from organic_market_agent.sfa_app import create_sfa_app
app = create_sfa_app()
```

### 1.4 Systemd service unit

```
# /etc/systemd/system/sfa-public.service
[Unit]
Description=SFA Public Web App
After=network.target

[Service]
Type=simple
User=sfa
WorkingDirectory=/opt/smallfarmsagents
Environment="DATABASE_URL=postgresql://sfa_public:***@localhost/oma"
ExecStart=/opt/smallfarmsagents/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5002 organic_market_agent.sfa_app.wsgi:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 1.5 nginx vhost

```
server {
    server_name sfa.nimrod.bio;
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/sfa.nimrod.bio/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sfa.nimrod.bio/privkey.pem;

    location /static/ {
        alias /opt/smallfarmsagents/organic_market_agent/sfa_app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

## Phase 2 — Module registry (1h)

### 2.1 Port `MODULES_REGISTRY.yaml` → `sfa_app/modules.py`

```python
SFA_MODULES = [
    {
        'id': 'crop-book',
        'name_he': 'ספר גידולים',
        'sub': 'אינדקס פתוח של גידולים, זנים, מחזורי גידול',
        'tier': 'open',
        'icon': 'lettuce',
        'thumb_prompt': 'module_thumb_book',
        'stat': '66 גידולים · 242 זנים',
        'stat_count': 66,
        'color': 'leaf',
        'route': '/book/',
        'status': 'live',
    },
    # ... 7 more modules — match yaml exactly ...
]

TIERS = {
    'open': {'label_he': 'כלים לקהילה', 'short_he': 'פתוח', 'color': 'leaf', 'description_he': '...'},
    'beta': {'label_he': 'בטא · ניסיוני', 'color': 'sun', 'description_he': '...'},
    'coming': {'label_he': 'בקרוב', 'color': 'paper', 'description_he': '...'},
    'paid': {'label_he': 'כלים מתקדמים', 'color': 'soil', 'description_he': '...'},
    'custom': {'label_he': 'בדיוק לחווה שלך', 'color': 'tomato', 'description_he': '...'},
}

def modules_by_tier(tier):
    return [m for m in SFA_MODULES if m['tier'] == tier]
```

### 2.2 Helpers

```python
# sfa_app/helpers.py
def get_freshness():
    """Returns {'state': 'fresh'|'aging'|'stale'|'error', 'label_he': '...'}"""
    # Reads from publisher artifact_version timestamp or DB query
    ...

def get_breadcrumbs(route):
    ...

def vegetable_icon_id(crop_slug):
    """Maps crop slug → SVG sprite id (tomato|lettuce|...)."""
    ...
```

---

## Phase 3 — Base template + shells (3h)

### 3.1 `templates/base.html`

```jinja
<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}SFA — כלים גדולים לחוות קטנות{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='tokens.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='gj.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='hub.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='community.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='crop-book-deep.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='desktop.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='desktop-extras.css') }}">
  <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;600;700;800&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  {% block head_extra %}{% endblock %}
</head>
<body class="sfa-app">
  <div class="sfa-mobile-only">
    {% include 'shell/mobile.html' %}
  </div>
  <div class="sfa-desktop-only">
    {% include 'shell/desktop.html' %}
  </div>
  <script src="{{ url_for('static', filename='sfa.js') }}" defer></script>
</body>
</html>
```

CSS:
```css
.sfa-mobile-only  { display: block; }
.sfa-desktop-only { display: none; }
@media (min-width: 900px) {
  .sfa-mobile-only  { display: none; }
  .sfa-desktop-only { display: block; }
}
```

### 3.2 `templates/shell/mobile.html`

```jinja
<div class="gj-shell">
  <header class="gj-header gj-header--plain">
    <div class="gj-header__row">
      {% if back_url %}<a class="gj-iconbtn" href="{{ back_url }}">←</a>{% endif %}
      <span class="gj-mark">{% include 'macros/_mark_svg.html' %}</span>
      <div class="gj-header__title">
        <div class="gj-title">{{ page_title|default('SFA') }}</div>
        <div class="gj-sub">{{ page_sub|default('') }}</div>
      </div>
      <a href="{{ url_for('hub.search') }}" class="gj-iconbtn" aria-label="חיפוש">⌕</a>
    </div>
    {% if show_module_tabs %}
      <nav class="gj-tabs">
        <a href="{{ url_for('market.list') }}" class="gj-tab {% if active=='market' %}is-active{% endif %}">מחירון</a>
        <a href="{{ url_for('book.entry') }}" class="gj-tab {% if active=='book' %}is-active{% endif %}">ספר גידולים</a>
      </nav>
    {% endif %}
  </header>

  <main class="gj-body">{% block body %}{% endblock %}</main>

  <footer class="gj-foot">
    <span class="gj-foot__dot" style="background: var(--status-{{ freshness.state }});"></span>
    <span>{{ freshness.label_he }}</span>
  </footer>
</div>
```

### 3.3 `templates/shell/desktop.html`

Port `DesktopShell` from `design/desktop.jsx` directly. The sidebar accordion uses `<details>` elements; persist open/closed via `localStorage` (handled in `sfa.js`).

---

## Phase 4 — Macros (2h)

Port the JSX components in `design/` to Jinja2 macros in `templates/macros/`:

```jinja
{# templates/macros/module_card.html #}
{% macro module_card(m) %}
  <a class="mod-card mod-card--{{ m.color }} mod-card--{{ m.tier }}"
     href="{{ m.route }}" data-tier="{{ m.tier }}">
    <div class="mod-card__art">
      {% if m.thumb_url %}
        <img src="{{ m.thumb_url }}" loading="lazy" alt="">
      {% else %}
        <div class="mod-card__placeholder mod-card__placeholder--{{ m.color }}"></div>
      {% endif %}
      <div class="mod-card__icon">{% include 'macros/_icon_' + m.icon + '.html' %}</div>
    </div>
    <div class="mod-card__body">
      <div class="mod-card__head">
        <h3 class="mod-card__name">{{ m.name_he }}</h3>
        {{ tier_badge(m.tier) }}
      </div>
      <p class="mod-card__sub">{{ m.sub }}</p>
      <p class="mod-card__stat">{{ m.stat }}</p>
    </div>
  </a>
{% endmacro %}
```

Macros needed (mirror `design/` JSX components):

| Macro | From | Notes |
|-------|------|-------|
| `tier_badge(tier, size='sm')` | `hub.jsx` | reads `TIERS[tier]` |
| `module_card(m)` | `hub.jsx::ModuleThumb` | |
| `price_card(p)` | `garden-journal.jsx::GJ_Row` | distribution bar inline |
| `crop_card(c)` | `garden-journal.jsx::CropRowB` | |
| `variety_row(v)` | `crop-book-deep.jsx::VarietyRow` | star + F1 pill + 6-field grid |
| `crosslink(direction, big, sub, href)` | `primitives.jsx::CrossLink` | book↔market |
| `market_disclaimer(full=false)` | `desktop.jsx::MarketDisclaimer*` | mandatory at market top |
| `contrib_strip(context, placeholder)` | `community.jsx::ContributeStrip` | with form action |
| `feed_item(item)` | `community.jsx::FeedItem` | 3 kinds: suggest/correction/data |
| `timeline_bar(prep, grow, harv)` | `garden-journal.jsx` | 3-segment |

Each is ~10–30 lines of Jinja2.

---

## Phase 5 — Routes (4–5h)

### 5.1 Hub routes (`sfa_app/routes/hub.py`)

```python
from flask import Blueprint, render_template, request, g
bp = Blueprint('hub', __name__)

@bp.route('/')
def home():
    return render_template('pages/hub_home.html',
        page_title='SFA',
        page_sub='כלים גדולים לחוות קטנות',
        show_module_tabs=False,
        active='hub',
    )

@bp.route('/about/')
def tiers():
    ...

@bp.route('/search/')
def search():
    q = request.args.get('q', '').strip()
    # cross-module search: crops, market products, community
    results = {'crops': [], 'products': [], 'community': []}
    if q:
        results = perform_global_search(q)
    return render_template('pages/search_results.html', q=q, results=results, ...)
```

### 5.2 Book routes (`sfa_app/routes/book.py`)

```python
@bp.route('/')
def entry():
    """CB0 · 4 entry paths."""
    return render_template('pages/book_entry.html', active='book', ...)

@bp.route('/questions/')
def questions():
    """CB1 · 8 question cards."""
    return render_template('pages/book_questions.html', active='book',
        questions=CB_QUESTIONS, ...)

@bp.route('/family/')
def family():
    """CB2 · 8 botanical families."""
    return render_template('pages/book_family.html', active='book',
        families=load_families(), ...)

@bp.route('/table/')
def table():
    """CB3 · pro table with sort/filter."""
    from organic_market_agent.crop_book.models import Crop
    rows = Crop.query.options(...).all()
    return render_template('pages/book_table.html', active='book',
        rows=rows, ...)

@bp.route('/search/')
def adv_search():
    """CB4 · advanced filter form."""
    ...

@bp.route('/<slug>/')
def crop(slug):
    """CB5 · crop detail with varieties hierarchy."""
    from organic_market_agent.crop_book.models import Crop, CropVariety
    crop = Crop.query.filter_by(slug=slug).first_or_404()
    varieties = (CropVariety.query
                 .filter_by(crop_id=crop.id)
                 .order_by(CropVariety.is_default.desc(), CropVariety.dtm)
                 .all())
    return render_template('pages/book_crop.html', active='book',
        crop=crop, varieties=varieties,
        market_link=lookup_market_price(crop.pricebook_product_id),
        ...)

@bp.route('/<slug>/variety/<vslug>/')
def variety(slug, vslug):
    """Single variety deep page."""
    ...
```

### 5.3 Market routes (`sfa_app/routes/market.py`)

```python
@bp.route('/')
def list():
    """MK1 · list with disclaimer."""
    products = load_market_with_7day_avg()
    return render_template('pages/market_list.html', active='market',
        products=products, ...)

@bp.route('/<slug>/')
def product(slug):
    """MK2 · product detail."""
    ...
```

### 5.4 Calculator (B3 — defer)

```python
@bp.route('/')
def calc():
    return render_template('pages/hub_calc.html', ...)
```

### 5.5 Community routes (`sfa_app/routes/community.py`)

```python
@bp.route('/community/')
def page():
    return render_template('pages/community.html', ...)

@bp.route('/api/v1/contribute', methods=['POST'])
def api_contribute():
    from . import contribute
    return contribute.handle(request)

@bp.route('/api/v1/community/feed')
def api_feed():
    limit = min(int(request.args.get('limit', 10)), 50)
    ...
```

---

## Phase 6 — Pages (3h)

For each `pages/*.html` template, port the matching JSX:

| Page | JSX source |
|------|-----------|
| `hub_home.html` | `hub.jsx::HubHome` |
| `hub_tiers.html` | `hub.jsx::HubTiers` |
| `hub_calc.html` | `hub.jsx::HubCalculator` + `desktop-extras.jsx::Desktop_Calculator` |
| `book_entry.html` | `crop-book-deep.jsx::CB_Entry` |
| `book_questions.html` | `crop-book-deep.jsx::CB_QuestionView` |
| `book_family.html` | `crop-book-deep.jsx::CB_FamilyTree` |
| `book_table.html` | `crop-book-deep.jsx::CB_ProTable` + `desktop.jsx::Desktop_CropBookProTable` |
| `book_search.html` | `crop-book-deep.jsx::CB_Search` |
| `book_crop.html` | `crop-book-deep.jsx::CB_CropFull` + `desktop-extras.jsx::Desktop_CropDetail` |
| `market_list.html` | `garden-journal.jsx::GJ_MarketList` + `desktop.jsx::Desktop_Market` |
| `market_product.html` | `garden-journal.jsx::GJ_MarketDetail` + `desktop-extras.jsx::Desktop_MarketDetail` |
| `community.html` | `desktop-extras.jsx::Desktop_Community` |
| `search_results.html` | `desktop-extras.jsx::Desktop_Search` |

Each template:
1. Extends `base.html`
2. Defines `{% block body %}` with the content area markup
3. Calls macros from `templates/macros/`
4. Each page sets `page_title`, `page_sub`, `active`, `show_module_tabs`, `back_url`, `freshness` via render-context

---

## Phase 7 — Contribute endpoint + DB migration (2h)

### 7.1 New table

```python
# alembic migration: 042_community_contributions.py
def upgrade():
    op.create_table('community_contributions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('context', sa.String(120), nullable=False),    # e.g. 'market.tomato'
        sa.Column('kind', sa.String(40), nullable=False),         # suggest|correction|data|note
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('name', sa.String(120)),                        # optional, free text
        sa.Column('email', sa.String(200)),
        sa.Column('phone', sa.String(40)),
        sa.Column('ip_hash', sa.String(64), nullable=False),
        sa.Column('user_agent', sa.String(400)),
        sa.Column('status', sa.String(20), server_default='pending'),  # pending|approved|rejected
        sa.Column('reviewed_by', sa.String(120)),
        sa.Column('reviewed_at', sa.DateTime),
    )
    op.create_index('ix_community_contributions_status', 'community_contributions', ['status'])
```

### 7.2 Handler

```python
# sfa_app/contribute.py
import hashlib
from datetime import timedelta
from flask import current_app, jsonify, request
from organic_market_agent.db.session import session_scope
from organic_market_agent.models.community import CommunityContribution  # new model

RATE_LIMIT = 5     # per hour per IP
WINDOW_SEC = 3600

def handle(req):
    ip = req.remote_addr or '0.0.0.0'
    ip_hash = hashlib.sha256((ip + current_app.config['SECRET_SALT']).encode()).hexdigest()[:32]

    # rate limit via DB count
    with session_scope() as s:
        recent = s.query(CommunityContribution).filter(
            CommunityContribution.ip_hash == ip_hash,
            CommunityContribution.created_at > datetime.utcnow() - timedelta(seconds=WINDOW_SEC)
        ).count()
        if recent >= RATE_LIMIT:
            return jsonify(error='rate_limited', message='יותר מדי שליחות. נסו עוד שעה.'), 429

        # honeypot
        if req.form.get('website'):
            return jsonify(id='discarded', queued=True), 200

        contrib = CommunityContribution(
            context=req.form.get('context', '')[:120],
            kind=req.form.get('kind', 'note')[:40],
            text=req.form.get('text', '')[:4000],
            name=req.form.get('name', '')[:120] or None,
            email=req.form.get('email', '')[:200] or None,
            phone=req.form.get('phone', '')[:40] or None,
            ip_hash=ip_hash,
            user_agent=req.headers.get('User-Agent', '')[:400],
            status='pending',
        )
        s.add(contrib)
        s.flush()
        contrib_id = contrib.id

    # email team_00 outside the DB tx
    send_review_email(contrib_id, contrib)

    return jsonify(id=contrib_id, queued=True)
```

### 7.3 Admin review UI — defer to WP-B2

For v1, contributions land in DB + email. v2 adds a CRUD review screen in the existing `admin/` Flask app.

---

## Phase 8 — Static assets (1h)

### 8.1 Copy CSS verbatim

```bash
cp design/system.css       sfa_app/static/tokens.css
cp design/gj.css           sfa_app/static/gj.css
cp design/hub.css          sfa_app/static/hub.css
cp design/community.css    sfa_app/static/community.css
cp design/crop-book-deep.css   sfa_app/static/crop-book-deep.css
cp design/desktop.css      sfa_app/static/desktop.css
cp design/desktop-extras.css   sfa_app/static/desktop-extras.css
```

### 8.2 SVG sprite

Extract the 8 vegetable icon SVGs from `design/illustrations.jsx`, combine into a single `static/icons.svg` sprite:

```html
<svg xmlns="http://www.w3.org/2000/svg" style="display:none">
  <defs>
    <radialGradient id="wc-tomato" ...>...</radialGradient>
    ...
  </defs>
  <symbol id="icon-tomato" viewBox="0 0 60 60">…</symbol>
  <symbol id="icon-lettuce" viewBox="0 0 60 60">…</symbol>
  ...
</svg>
```

Used in templates as:
```html
<svg width="48" height="48"><use href="/static/icons.svg#icon-tomato"/></svg>
```

### 8.3 `sfa.js` — minimal vanilla JS

- Accordion state persistence (localStorage)
- ContributeStrip submit (fetch POST)
- Pro table sort (simple onclick handlers)
- Calculator live recompute (no framework)

~150 lines total.

---

## Phase 9 — AI background images (2h, parallelizable)

Generate from prompts in `MODULES_REGISTRY.yaml::ai_prompts` (Midjourney / SDXL), save as `sfa_app/static/img/<key>.webp`. Templates fall back to a tinted placeholder div if the file is missing.

---

## Phase 10 — Tests & deploy (2h)

### 10.1 Tests

- `tests/sfa_app/test_routes.py` — each route returns 200, correct shell renders
- `tests/sfa_app/test_filter_parity.py` — book table sort/filter matches `crop_book.views:api_crops` SSoT
- `tests/sfa_app/test_contribute.py` — POST endpoint behavior (success, rate limit, honeypot)

### 10.2 Deploy

1. Add nginx vhost config + Let's Encrypt cert
2. Install + enable `sfa-public.service`
3. Migrate DB (`alembic upgrade head` for the new contributions table)
4. Smoke-test `https://sfa.nimrod.bio/` end-to-end

---

## Effort summary

| Phase | Hours | Can defer? |
|-------|-------|-----------|
| 0. Open Qs resolution | (blocking) | no |
| 1. Flask skeleton | 2 | no |
| 2. Module registry | 1 | no |
| 3. Base + shells | 3 | no |
| 4. Macros | 2 | no |
| 5. Routes | 4–5 | no |
| 6. Pages | 3 | partially (calc → B3) |
| 7. Contribute endpoint + migration | 2 | no |
| 8. Static assets | 1 | no |
| 9. AI images | 2 | yes — parallel |
| 10. Tests + deploy | 2 | no |
| **Total WP-B1** | **~20h** | |

---

## Acceptance — Done = builder hands back

Working `https://sfa.nimrod.bio/` with:

- [ ] Standalone Flask app, no WP code referenced
- [ ] Mobile shell (<900px) + desktop shell (≥900px), single HTML
- [ ] Hub home renders 8 modules from `modules.py`, grouped into 3 tiers
- [ ] Book: 4 entry paths + crop+varieties hierarchy (CB5)
- [ ] Market: list + detail + mandatory disclaimer everywhere
- [ ] Community page + ContributeStrip in every relevant page
- [ ] `POST /api/v1/contribute` works, persists, emails team_00
- [ ] No regression on existing admin (5001) or existing nimrod.bio WP-embed
- [ ] Tests pass; LCP < 2.5s; no JS errors

Hand off to team_100 for L-GATE_M review.
