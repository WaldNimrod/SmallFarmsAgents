# LOD400 — SFA-S003-P001-WP003 — ספר גידולים: UI Views (view-only)

**Date:** 2026-05-07
**Author:** team_100 (Claude Sonnet 4.6)
**WP:** SFA-S003-P001-WP003 — ממשק ספר גידולים (view-only)
**Type:** LOD400_SPEC
**Status:** L-GATE_S ROUND_2 — all Round 1 findings resolved in v2.0.0; awaiting re-submission to team_190
**L-GATE_S Round 1 verdict:** PASS_WITH_FINDINGS (team_190, 2026-05-07); F3 tab visibility + F4 market-price + F5 ENTITY_REGISTRY resolved. Verdict: `_COMMUNICATION/team_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md`
**Builder:** sfa_build (Sonnet, Team 10)
**Validator:** team_190 (external — L-GATE_SPEC + L-GATE_VALIDATE)
**Depends on:** SFA-S003-P001-WP002 (DB tables + seed data must exist)

**Reference documents (read before writing a single line of code):**
1. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003/LOD300_UI_MOCKUP_2026-05-07_v1.0.0.md` — screen wireframes
2. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` — schema SSoT
3. This LOD400 spec

---

## 1. Goal

Add a **read-only Crop Book** (`/crop-book/`) section to the existing `organic_market_agent` admin panel. This is a new Flask Blueprint with 3 routes, 3 Jinja2 templates, and supporting static assets. Zero edit/create/delete functionality in S003 — view only.

The UI matches the LOD300 wireframes and HTML prototype exactly. RTL layout. Hebrew language throughout.

---

## 2. Architecture

### 2.1 Integration point

The existing admin panel is a Flask app registered in `organic_market_agent/admin/`. The crop book is a new Blueprint registered at prefix `/crop-book/`.

**Registration:** add to `organic_market_agent/admin/__init__.py` (or wherever blueprints are registered):
```python
from organic_market_agent.crop_book.views import crop_book_bp
app.register_blueprint(crop_book_bp, url_prefix="/crop-book")
```

### 2.2 Blueprint module structure

```
organic_market_agent/
└── crop_book/
    ├── views.py           ← Blueprint definition + all 3 route handlers
    └── templates/
        └── crop_book/
            ├── index.html       ← main table / search
            ├── crop.html        ← crop detail (8 tabs)
            └── _macros.html     ← shared macros (season icons, source fan, entity tags)
```

Static files (CSS + JS unique to crop book) go in:
```
organic_market_agent/admin/static/crop_book/
    ├── crop_book.css
    └── crop_book.js
```

### 2.3 Routes

| Route | Handler | Template | Description |
|-------|---------|----------|-------------|
| `GET /crop-book/` | `index()` | `crop_book/index.html` | Main table with category tabs + advanced search |
| `GET /crop-book/<int:crop_id>/` | `crop_detail()` | `crop_book/crop.html` | Full crop page with 8 tabs |
| `GET /crop-book/api/crops` | `api_crops()` | (JSON) | AJAX endpoint for search/filter; returns JSON list |

### 2.4 Data access layer

All DB access is read-only. Use SQLAlchemy sessions from existing `get_db_session()` helper (or equivalent pattern used in current admin routes).

**`index()` query:**
```python
crops = (
    session.query(Crop)
    .options(joinedload(Crop.family))
    .options(joinedload(Crop.default_variety))
    .filter(optional category filter)
    .filter(optional search filter — name_he ILIKE or name_en ILIKE)
    .order_by(Crop.name_he)
    .all()
)
```

**`crop_detail()` query:**
```python
crop = (
    session.query(Crop)
    .options(
        joinedload(Crop.family),
        joinedload(Crop.varieties).joinedload(CropVariety.source_values),
        joinedload(Crop.conversion_group).joinedload(CropConversionGroup.unit_conversions),
    )
    .filter(Crop.id == crop_id)
    .one_or_none()
)
```
Return 404 if not found.

**`api_crops()` — search JSON endpoint:**
Accepts query params: `?q=text&category=ירקות&season=summer&dtm_max=50`

Returns:
```json
[
  {
    "id": 1,
    "name_he": "ארוגולה",
    "name_en": "Arugula",
    "family_scientific": "Brassicaceae",
    "category": "vegetables",
    "harvest_unit_default": "case",
    "variety_count": 4,
    "seasons": ["spring", "fall", "winter"],
    "dtm_min": 21
  }
]
```

---

## 3. UI Specification

### 3.1 Main page (`/crop-book/`)

**Layout:** RTL, Hebrew. Category tabs + search bar + advanced search panel.

**Category tabs:** כל הגידולים / ירקות / עשבי תיבול / פירות / קטניות / עצי פרי / דגנים / גידולי כיסוי

**Crop grid cards** (per card):
- שם_עברי (large), שם_אנגלי (small), שם_מדעי (italic)
- משפחה בוטנית
- [קטגוריה badge]
- יחידת קציר ברירת מחדל
- מספר זנים
- Season emoji icons: ☀️ (קיץ) 🌸 (אביב) 🌧 (חורף) 💨 (סתיו)
  — active seasons at 100% opacity, inactive at 25% opacity
  — season data: derived from `planting_season` text of default variety
- לחיצה → `/crop-book/{id}/`

**Advanced search panel** (collapsible, hidden by default):
- `DTM מקסימלי` — number input (filter: `days_to_maturity ≤ value` on default variety)
- `עונות` — 4 checkboxes: ☀️ קיץ / 🌸 אביב / 🌧 חורף / 💨 סתיו

**Search bar:** free text, filters on `name_he` + `name_en` + `scientific_name` (ILIKE).

### 3.2 Crop detail page (`/crop-book/<id>/`)

**Header:**
- Breadcrumb: ← ספר גידולים / [קטגוריה] / [שם_עברי]
- Crop title: שם_עברי + שם_אנגלי + שם_מדעי (italic)
- Metadata row: משפחה · מחזור גידול · יחידת קציר ברירת מחדל

**8 tabs** — all 8 tabs render on every crop page. Tabs with no data show `—` placeholders; none are hidden. Exception: tab 5 (ציוד) may be hidden/greyed when ALL seeder fields are NULL across ALL varieties of this crop.

| # | Tab label | Content |
|---|----------|---------|
| 1 | זנים | Variety cards — see §3.3 |
| 2 | תיאור | JMF description text with entity tags — see §3.4 |
| 3 | כלכלה | Two-price cards + yield table — see §3.5 |
| 4 | טיפולים | Care schedule matrix — see §3.6 |
| 5 | ציוד | Seeder settings — see §3.7 |
| 6 | מקורות | Side-by-side source comparison — see §3.8 |
| 7 | ציר זמן | Visual timeline — see §3.9 |
| 8 | נתוני שדה | DTM multi-season + unit conversions |

### 3.3 Tab: זנים

List of variety cards, default variety first (★ marker).

Per card:
- שם_זן_עברי + שם_זן_אנגלי
- [★ ברירת מחדל] badge if `is_default=True`
- [🔗 מורכב] badge with rootstock name if `is_grafted=True`
- שיטת שתילה · שלב קציר · חלון קציר · ריווח בשורה × שורות
- תשואה · מחיר מתועד · הכנסה/מ'

### 3.4 Tab: תיאור

JMF description text. Inline entity tags:

```html
<span class="etag et-pest"
      data-etype="pest"
      data-eid="diamondback-moth"
      data-future-url="/entities/pests/diamondback-moth">עש יהלום</span>
```

Entity type CSS classes and colors per the HTML prototype:
- `.et-pest` — red (#b71c1c / #fdecea)
- `.et-disease` — orange (#bf360c / #fff3e0)
- `.et-equip` — blue (#0d47a1 / #e3f2fd)
- `.et-input` — green (#1b5e20 / #e8f5e9)
- `.et-technique` — purple (#4a148c / #f3e5f5)
- `.et-crop` — teal (#004d40 / #e0f2f1)

Hover tooltip: JS shows entity name (he) + entity type label. `ENTITY_REGISTRY` JS object provides the lookup (same as prototype).

Entity summary panel below description text: lists all detected entities grouped by type.

### 3.5 Tab: כלכלה

Two-price card layout (grid 1fr 1fr):

**Card 1 — מחיר מתועד** (green top border `#2d5a27`):
- Value: `documented_price` ₪ / `documented_price_unit`
- Source: `documented_price_source`
- Expandable yearly breakdown from `crop_variety_source_values` WHERE `field_name='documented_price'`

**Card 2 — מחיר שוק** (blue top border `#1565c0`):
- Show only if `pricebook_product_id IS NOT NULL`
- Otherwise: "לא מקושר למחירון" (grey card)
- When linked: display placeholder text: "מחיר שוק: [pricebook_product_id] — יוצג עם הפעלת מחירון"
- No live price read or delta % in S003 — deferred to מחירון integration phase (per §6)

Yield table below cards:
| שדה | ערך | מקור |
|-----|-----|------|
| תשואה ממוצעת | X ק"ג/מ' ערוגה | source |
| הכנסה ממוצעת | ₪X/מ' ערוגה | computed |
| יחידת קציר | X | |
| משקל יחידה | Xg (from conversion_group) | |

### 3.6 Tab: טיפולים

Phase × treatment matrix table. Phase rows = גידול שלבים (הכנה / נביטה / גידול / קציר).
Treatment columns = ריסוס / שקייה / דישון / עידור / קציר.

Data source: `notes` field and free-text from JMF descriptions (parse if structured; otherwise show empty matrix with note "נתונים בהכנה"). Do NOT block the tab on missing data — show the table structure with `—` values.

### 3.7 Tab: ציוד

Displayed only if `seeder IS NOT NULL` on at least one variety.

Content:
```
מזרע: {seeder}
הגדר קדמי: {seeder_front_gear}
הגדר אחורי: {seeder_rear_gear}
לוח גלגל: {seeder_roller_plate}
מקור: JMF MasterClass
```

### 3.8 Tab: מקורות

Side-by-side source comparison table. Columns = sources found for this crop (JMF, Tend_2022, Tend_2021, team_00...). Rows = fields.

Data from: `crop_variety_source_values` for default variety.

Toggle: "מאוחד" (default, shows `crop_varieties` fields) / "לפי מקור" (shows per-source raw values from `crop_variety_source_values`).

### 3.9 Tab: ציר זמן

Visual phase bar + event dot timeline over a week ruler.

Rendering:
- Ruler: 1 to N weeks (N = `harvest_window_max_days / 7`, rounded up)
- Phase bars: CSS absolute positioning, width = % of total weeks
  - הכנה (grey `#78909c`) — weeks 1 to GH_total/7 (if greenhouse)
  - נביטה (purple `#7e57c2`) — first 1–2 weeks
  - גידול (green `#43a047`) — mid phase
  - קציר / חלון קציר (orange `#fb8c00`) — last phase, width = harvest_window
- Event dots: positioned at key week intersections
- Phase labels inside bars (truncate with ellipsis if bar too narrow)

Fall back to "אין נתוני ציר זמן" text if DTM + harvest_window both NULL.

---

## 4. Acceptance Criteria

### AC-01 — Blueprint registered, routes return 200

- `GET /crop-book/` returns HTTP 200 and renders `crop_book/index.html`.
- `GET /crop-book/1/` for a seeded crop returns HTTP 200 and renders `crop_book/crop.html`.
- `GET /crop-book/99999/` returns HTTP 404.
- `GET /crop-book/api/crops` returns JSON array.

### AC-02 — Main page: all category tabs functional

- Each category tab (`ירקות`, `עשבי תיבול`, etc.) filters the crop grid correctly.
- "כל הגידולים" shows all crops.
- Empty state ("לא נמצאו גידולים") shown when filter yields 0 results.

### AC-03 — Main page: search works

- Free-text search via API endpoint filters by `name_he`, `name_en`, `scientific_name`.
- Results update without full page reload (JS fetch to `/crop-book/api/crops?q=...`).
- Advanced search panel: DTM max filter reduces results to crops whose default variety `days_to_maturity ≤ value`.
- Season checkboxes filter by `planting_season` text match (substring match on season name in Hebrew or English).

### AC-04 — Crop detail: all 8 tabs render

- Tabs present on page. Clicking each tab shows correct content pane.
- Tabs with no data (e.g. טיפולים with all `—` values) shown with an "אין נתונים" placeholder, NOT hidden.
- Tab 5 (ציוד) hidden/greyed when all seeder fields are NULL for all varieties.

### AC-05 — Variety cards correct

- ★ marker on default variety.
- 🔗 badge + rootstock name shown for grafted varieties (Lobelo/Beaufort for tomato).
- Price shows `documented_price` + unit.
- Yield shows `avg_yield_per_bed_m` + unit.

### AC-06 — Two-price cards correct (Tab: כלכלה)

- מחיר מתועד card shows value + source + expandable yearly breakdown for crops with multi-year Tend data.
- When `pricebook_product_id IS NULL`: מחיר שוק card shows "לא מקושר למחירון".
- Layout: two cards side-by-side on desktop (grid 1fr 1fr); stack vertically on mobile (< 768px).

### AC-07 — Entity tags functional

- Tags rendered as styled `<span>` elements with correct CSS class per entity type.
- Hovering a tag shows tooltip with entity name_he + type.
- `data-etype` and `data-eid` attributes present on all tag elements.
- Clicking a tag does NOT navigate (future_url not active yet — no href on the span; tooltip only).

### AC-08 — Timeline tab functional

- For ארוגולה (DTM=21, harvest_window=80): ruler of 12 weeks, phase bars proportional.
- For עגבנייה (harvest_window=100): ruler of ~18 weeks.
- Falls back gracefully for crops with no DTM data.

### AC-09 — RTL layout

- Page `<html dir="rtl">` or equivalent.
- All labels, tabs, cards are right-to-left.
- Breadcrumb uses RTL order.
- Source comparison table reads right-to-left.

### AC-10 — No edit/delete

- Zero form inputs anywhere in crop book views (except the search bar and filter controls).
- No POST routes in the crop book Blueprint.
- No admin CRUD links within crop book pages.

### AC-11 — Tests green

- `tests/crop_book/test_views.py` — Flask test client; all route ACs above; mock DB session.
- All existing tests pass.
- `validate_aos.sh .` returns 0 FAIL.

---

## 5. File-level deliverables

### CREATE
```
organic_market_agent/crop_book/views.py
organic_market_agent/crop_book/templates/crop_book/index.html
organic_market_agent/crop_book/templates/crop_book/crop.html
organic_market_agent/crop_book/templates/crop_book/_macros.html
organic_market_agent/admin/static/crop_book/crop_book.css
organic_market_agent/admin/static/crop_book/crop_book.js

tests/crop_book/test_views.py
```

### UPDATE
- `organic_market_agent/admin/__init__.py` (or equivalent) — register `crop_book_bp`
- `CHANGELOG.md` — add UI entry under `[Unreleased]`
- `_COMMUNICATION/team_10/SFA-S003-P001-WP003/BUILD_REPORT_v1.0.0.md` — builder creates after L-GATE_B

---

## 6. Build notes

- If the admin panel uses Jinja2 + Flask, follow existing template inheritance from `admin/templates/base.html` (or equivalent). Crop book templates extend the same base.
- RTL: the base template likely already sets `dir="rtl"`. If not, add it only to crop book templates.
- Season detection from `planting_season` text: map tokens `קיץ`/`summer` → `☀️`, `אביב`/`spring` → `🌸`, `חורף`/`winter` → `🌧`, `סתיו`/`fall`/`autumn` → `💨`. Implement in `_macros.html`.
- **`ENTITY_REGISTRY`:** Repo-owned static asset at `organic_market_agent/admin/static/crop_book/entity_registry.js`. The template loads it via Flask `url_for('static', filename='crop_book/entity_registry.js')` — no `/tmp` or other ephemeral path dependency. Initial content: entity definitions extracted from the HTML prototype during initial build. Expand with entities found during WP002 seed. Document the version in LOD500.
- **Market price (§6 authoritative):** Do NOT implement live pricebook reads in S003. When `pricebook_product_id IS NOT NULL`, render: "מחיר שוק: [מחירון_מוצר_id] — יוצג עם הפעלת מחירון". When NULL: "לא מקושר למחירון". No delta % calculation in S003 — deferred to מחירון integration phase.

---

*LOD400 v2.0.0 — revised 2026-05-07 by team_100. Changes: F3 tab visibility unified — 8 tabs always render (§3.2); F4 delta% removed from §3.5; F5 ENTITY_REGISTRY repo path canonical (§6); /tmp reference removed from ref docs. Status: ROUND_2 pending team_190 re-submission.*
